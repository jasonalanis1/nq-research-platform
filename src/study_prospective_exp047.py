"""
study_prospective_exp047.py
=============================

Implements the frozen spec in
`research/studies/prospective-validation-exp047-scoping.md` (v2,
Advisor-cleared 2026-09-06, Jason-authorized "let's run it") -- exp-050.

This is NOT a one-time backtest. exp-047 (the raw weekly momentum
signal: sign of trailing 52-week cumulative log return) never cleared
the Discovery-slice promotion bar -- it was a genuine near-miss,
REJECTED. Two follow-on risk-management overlays (exp-048, exp-049)
were also killed and the whole signal family is shelved. Per the
Advisor's own recommendation, the only defensible way to find out if
this near-miss is real is to track it forward on data that did not
exist yet at freeze time, rather than re-mining any data already on
disk (which would waste this project's budgeted Validation/Holdout
reserves on a hypothesis that never earned access to them).

FREEZE ANCHOR: the exact timestamp of the last bar on disk at sign-off,
2026-08-19 19:59:00 America/New_York -- NOT a calendar date, per the
Advisor's v1 review (a calendar date does not guarantee no data existed
yet; an exact on-disk timestamp does). Only weeks entirely after this
instant are eligible to be logged. This script hard-skips (does not log)
any week that is not yet entirely past the freeze anchor, and asserts
(raises) as a safety net if that skip logic is ever bypassed by a bug.

Reuses, UNMODIFIED: resample_to_weekly_closes(), compute_weekly_log_returns(),
compute_weekly_momentum_signal() (from study_nq_weekly_trend_following.py,
exp-047's own script) and compute_positions(), FLIP_COST_POINTS (from
study_nq_trend_following.py -- see the exact import list below) --
and analyze_primary()'s
bootstrap_mean_ci() (from study_nq_trend_following.py), same seed, same
n_bootstrap, same nonparametric resample convention. This is the RAW
exp-047 signal exactly as originally tested -- no ATR overlay, no
stop-loss, no take-profit, no trailing exit (both overlay variants
already failed independently and are shelved).

IMPORTANT: this script deliberately calls load_price_data(apply_holdout=False).
This is NOT a reopening of the legacy holdout boundary for ordinary
testing -- every week this script is capable of logging is already past
2026-08-19, later than even the legacy holdout start date
(2026-04-07), so nothing this script touches can leak into or affect
Discovery/Validation/Holdout Gen 2. It is the one script in this
project intentionally exempted from the apply_holdout_boundary() call,
precisely because its entire purpose is to look at data newer than that
boundary.

PRE-COMMITTED INTERIM-LOOK DISCIPLINE (frozen spec Section 6): the only
permitted interim action, before the first checkpoint, is an early KILL
if the cumulative (from the freeze anchor) 90% bootstrap CI is entirely
below zero for 26 consecutive logged weeks -- a threshold chosen (per a
20,000-path Monte Carlo simulation, documented in the frozen spec) to
give a ~5% false-kill rate under a null signal despite continuous
weekly monitoring. There is no equivalent early-PASS rule.

PRE-REGISTERED CHECKPOINTS (frozen spec Section 7): 104 / 156 / 208
weeks from the freeze anchor, with a hard 260-week (~5yr) maximum
tracking horizon after which this mechanism formally closes regardless
of outcome.

GOVERNANCE NOTE: no other script in this project should independently
compute or publish exp-047's performance over the prospective window --
that would be a backdoor look that could bias checkpoint discretion
even if this script's own discipline is followed perfectly.

HOW TO RUN (safe to re-run any time; idempotent -- only appends rows
for newly-closed weeks not already in the log):
    python3 src/study_prospective_exp047.py

Each run should be followed by a single git commit of the updated log
file (never squashed/amended) -- this project's existing tamper-
evidence convention for append-only ledger files, extended here.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from study_volatility_regime import compute_daily_ref_closes  # reused unmodified
from study_nq_weekly_trend_following import (  # reused unmodified
    resample_to_weekly_closes,
    compute_weekly_log_returns,
    compute_weekly_momentum_signal,
)
from study_nq_trend_following import (  # reused unmodified
    FLIP_COST_POINTS,
    compute_positions,
    analyze_primary,
    bootstrap_mean_ci,
    robustness_drop_largest_pnl_day,
    robustness_split_half,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = PROJECT_ROOT / "research" / "ledger" / "prospective_exp047_log.jsonl"

# Frozen spec Section 3 -- exact last on-disk bar timestamp at v2 sign-off (2026-09-06).
# NOT a calendar date. Only weeks entirely after this instant are eligible to log.
FREEZE_ANCHOR = pd.Timestamp("2026-08-19 19:59:00", tz="America/New_York")
FREEZE_ANCHOR_DATE = FREEZE_ANCHOR.date()

# Frozen spec Section 6 -- early-kill rule (one-sided, no early-pass equivalent).
EARLY_KILL_CONSECUTIVE_WEEKS = 26

# Frozen spec Section 7 -- pre-registered checkpoint schedule + hard max horizon.
CHECKPOINT_WEEKS = [104, 156, 208]
MAX_HORIZON_WEEKS = 260


def load_existing_log() -> list:
    """Reads whatever has already been logged (idempotency support)."""
    if not LOG_PATH.exists():
        return []
    rows = []
    with open(LOG_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_new_rows(new_rows: list):
    """Append-only -- never rewrites existing rows. Each call should be
    followed by its own git commit (tamper-evidence, frozen spec
    Section 5)."""
    if not new_rows:
        return
    with open(LOG_PATH, "a") as f:
        for row in new_rows:
            f.write(json.dumps(row) + "\n")


def compute_prospective_rows(positions: dict, weekly_closes: dict, day_to_week: dict,
                              already_logged_weeks: set) -> list:
    """Mirrors exp-047's compute_weekly_pnl() row shape exactly, but
    only for weeks (a) classifiable (52+ prior weekly returns -- via
    `positions`, inherited from compute_positions(mom_by_week)), (b)
    entirely after the freeze anchor, and (c) not already logged."""
    weeks = sorted(w for w in positions.keys() if weekly_closes.get(w) is not None)
    new_rows = []
    for i in range(1, len(weeks)):
        prev_w, w = weeks[i - 1], weeks[i]
        week_key = f"{w[0]}-W{w[1]:02d}"

        days_in_this_week = day_to_week.get(w, [])
        if not days_in_this_week or min(days_in_this_week) <= FREEZE_ANCHOR_DATE:
            continue  # not yet prospective -- expected/normal, not an error, silently skip

        # Safety-net assertion: given the skip above, this should never fire.
        assert min(days_in_this_week) > FREEZE_ANCHOR_DATE, (
            f"FREEZE ANCHOR VIOLATION: week {week_key} includes a day at or before "
            f"{FREEZE_ANCHOR_DATE} -- refusing to log (frozen spec Section 3)."
        )

        if week_key in already_logged_weeks:
            continue  # idempotency -- never re-log or overwrite an existing row

        prev_close = weekly_closes[prev_w]
        this_close = weekly_closes[w]
        position = positions[w]
        prev_position = positions[prev_w]
        price_change = this_close - prev_close
        pnl = position * price_change
        flipped = position != prev_position
        cost = FLIP_COST_POINTS if flipped else 0.0
        new_rows.append({
            "date": week_key,
            "position": position,
            "flipped": bool(flipped),
            "price_change": price_change,
            "pnl": pnl,
            "cost": cost,
            "net_pnl": pnl - cost,
        })
    return new_rows


def check_early_kill(pnl_df: pd.DataFrame) -> dict:
    """Frozen spec Section 6: cumulative-from-freeze 90% bootstrap CI,
    entirely below zero (BOTH bounds negative), for
    EARLY_KILL_CONSECUTIVE_WEEKS consecutive logged weeks."""
    n = len(pnl_df)
    consecutive_below_zero = 0
    max_consecutive = 0
    triggered_at_week = None
    for i in range(2, n + 1):  # need >=2 points for a bootstrap CI
        sub = pnl_df.iloc[:i]
        ci_low, ci_high = bootstrap_mean_ci(sub["net_pnl"].to_numpy())
        entirely_below_zero = (ci_low < 0) and (ci_high < 0)
        if entirely_below_zero:
            consecutive_below_zero += 1
            max_consecutive = max(max_consecutive, consecutive_below_zero)
            if consecutive_below_zero >= EARLY_KILL_CONSECUTIVE_WEEKS and triggered_at_week is None:
                triggered_at_week = i
        else:
            consecutive_below_zero = 0
    return {
        "n_weeks_logged": n,
        "max_consecutive_ci_below_zero": max_consecutive,
        "early_kill_triggered": triggered_at_week is not None,
        "early_kill_triggered_at_week": triggered_at_week,
    }


def main():
    full_df, is_synthetic = load_price_data(
        context="study_prospective_exp047.py", apply_holdout=False
    )
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    # Deliberately NOT get_discovery_data() / apply_holdout_boundary(): every week this
    # script can possibly log is already past the freeze anchor (2026-08-19), later than
    # even the legacy holdout start (2026-04-07) -- see module docstring.
    day_groups = {day: sub for day, sub in full_df.groupby(full_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)

    weekly_closes = resample_to_weekly_closes(ref_closes)
    weekly_returns = compute_weekly_log_returns(weekly_closes)
    all_weeks = sorted(weekly_closes.keys())
    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)
    positions = compute_positions(mom_by_week)  # reused unmodified

    day_to_week = {}
    for day in sorted(ref_closes.keys()):
        iso_year, iso_week, _ = day.isocalendar()
        day_to_week.setdefault((iso_year, iso_week), []).append(day)

    existing_rows = load_existing_log()
    already_logged_weeks = {r["date"] for r in existing_rows}

    new_rows = compute_prospective_rows(positions, weekly_closes, day_to_week, already_logged_weeks)
    append_new_rows(new_rows)

    all_rows = existing_rows + new_rows
    pnl_df = pd.DataFrame(all_rows) if all_rows else pd.DataFrame(
        columns=["date", "position", "flipped", "price_change", "pnl", "cost", "net_pnl"]
    )

    print("=" * 78)
    print("PROSPECTIVE VALIDATION OF exp-047 (raw weekly momentum signal) -- exp-050")
    print(f"Freeze anchor: {FREEZE_ANCHOR} (only weeks entirely after this are eligible)")
    print("=" * 78)
    print(f"\nNewly logged this run: {len(new_rows)} week(s)")
    print(f"Total prospective weeks logged so far: {len(pnl_df)}")

    if len(pnl_df) == 0:
        print("\nNo prospective weeks exist yet -- nothing past the freeze anchor is on "
              "disk. This is expected until new data is fetched forward. Re-run this "
              "script after data_fetch_databento.py has pulled bars past "
              f"{FREEZE_ANCHOR_DATE}.")
        return

    primary = analyze_primary(pnl_df)  # reused unmodified
    print("\n--- Cumulative primary stats (all logged prospective weeks) ---")
    for k, v in primary.items():
        print(f"  {k}: {v}")

    early_kill = check_early_kill(pnl_df)
    print("\n--- Early-kill check (frozen spec Section 6) ---")
    for k, v in early_kill.items():
        print(f"  {k}: {v}")
    if early_kill["early_kill_triggered"]:
        print(f"\n  *** EARLY KILL TRIGGERED at week {early_kill['early_kill_triggered_at_week']} -- "
              f"cumulative 90% CI has been entirely below zero for "
              f"{EARLY_KILL_CONSECUTIVE_WEEKS}+ consecutive weeks. Per the frozen spec, "
              f"this is a sustained, decisive negative result -- treat as an honest kill, "
              f"do not wait for the next scheduled checkpoint. ***")

    n = len(pnl_df)
    next_checkpoint = next((c for c in CHECKPOINT_WEEKS if n < c), None)
    reached_checkpoint = max([c for c in CHECKPOINT_WEEKS if n >= c], default=None)
    print(f"\n--- Checkpoint status ---")
    print(f"  Weeks logged: {n} / hard maximum horizon {MAX_HORIZON_WEEKS}")
    if reached_checkpoint and n < MAX_HORIZON_WEEKS:
        print(f"  Reached checkpoint: {reached_checkpoint} weeks -- re-run the exp-047 "
              f"promotion bar now (statistically_credible AND economically_meaningful above).")
    if next_checkpoint:
        print(f"  Next pre-registered checkpoint: {next_checkpoint} weeks "
              f"({next_checkpoint - n} more week(s) to go)")
    if n >= MAX_HORIZON_WEEKS:
        print(f"  *** HARD MAXIMUM HORIZON REACHED ({MAX_HORIZON_WEEKS} weeks) -- this "
              f"mechanism formally closes now regardless of outcome, per the frozen spec. ***")

    if n >= 2:
        print("\n--- Robustness (a): drop single largest-magnitude weekly net P&L week ---")
        drop_result = robustness_drop_largest_pnl_day(pnl_df)
        for k, v in drop_result.items():
            print(f"  {k}: {v}")

        print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
        split_result = robustness_split_half(pnl_df)
        print("  First half:", split_result["first_half"])
        print("  Second half:", split_result["second_half"])

    out = {
        "n_weeks_logged": n,
        "primary": primary,
        "early_kill_check": early_kill,
        "next_checkpoint_weeks": next_checkpoint,
        "reached_checkpoint_weeks": reached_checkpoint,
        "max_horizon_weeks": MAX_HORIZON_WEEKS,
        "freeze_anchor": str(FREEZE_ANCHOR),
    }
    status_path = PROJECT_ROOT / "data" / "study_prospective_exp047_status.json"
    with open(status_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved current status snapshot to {status_path}.")
    print(f"Prospective log (append-only, git-commit each run): {LOG_PATH}")


if __name__ == "__main__":
    main()
