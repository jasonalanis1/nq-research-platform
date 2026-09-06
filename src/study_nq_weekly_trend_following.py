"""
study_nq_weekly_trend_following.py
=====================================

Implements the frozen spec in
`research/studies/weekly-trend-following-scoping.md` (v1, signed off
by Jason 2026-09-06) -- exp-047. Direct weekly-resolution adaptation
of exp-038 (`src/study_nq_trend_following.py`), per the Path-to-
Profitability Advisor's recommendation during a 2026-09-06 strategic-
direction consultation: stop testing new signals at daily/intraday
resolution (both heavily tested, mostly null) and test the one
timeframe never tried in this project's 46-experiment history --
weekly.

Reuses exp-038's signal logic, cost accounting, evaluation gate, and
robustness checks UNMODIFIED wherever the coarser resolution allows --
imported directly from study_nq_trend_following.py, not reimplemented:
  - compute_positions() -- the +1/-1 sign rule, identical.
  - analyze_primary() -- the adapted Step-2 gate (bootstrap CI +
    cost-drag-relative economic threshold), identical.
  - robustness_drop_largest_pnl_day(), robustness_split_half() --
    identical.
  - bootstrap_mean_ci() -- identical.
  - FLIP_COST_POINTS -- identical (imported via the module).

The only genuinely new code, per the frozen spec:
  1. Resampling the existing daily reference-close series to weekly
     bars (last valid daily reference close within each ISO calendar
     week).
  2. A weekly-lookback momentum signal (52-week trailing cumulative
     log return -- the direct weekly analogue of exp-038's 252-day
     lookback), structurally identical to
     study_nq_trend_following.compute_momentum_signal() with the
     lookback unit changed from days to weeks.
  3. A weekly P&L construction, structurally identical to
     study_nq_trend_following.compute_daily_pnl() with days replaced
     by weeks.

ONE primary test: is the mean weekly net P&L of this signal positive
and statistically credible (90% bootstrap CI entirely above zero) AND
economically meaningful (>= 2x its own realized cost drag, the same
adapted bar exp-038 established and Jason already approved)?

Disclosed in the frozen spec, repeated here: ~350 weekly bars is a
~4x reduction in independent observations versus exp-038's 1,463
daily bars. exp-038's own 90% CI already spanned zero on the larger
sample; an inconclusive, underpowered result should be treated as the
MODAL outcome here, not a surprise.

HOW TO RUN:
    python3 src/study_nq_weekly_trend_following.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes, compute_daily_log_returns  # reused unmodified
from study_nq_trend_following import (  # reused unmodified
    FLIP_COST_POINTS,
    compute_positions,
    analyze_primary,
    robustness_drop_largest_pnl_day,
    robustness_split_half,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

MOMENTUM_LOOKBACK_WEEKS = 52  # frozen spec: direct weekly analogue of exp-038's 252-day (~12mo) lookback


def resample_to_weekly_closes(ref_closes: dict) -> dict:
    """ISO-calendar-week -> the last valid daily reference close within
    that week (Mon-Fri), keyed by (iso_year, iso_week) so year
    boundaries are handled correctly (Python's isocalendar() already
    assigns the correct iso_year to a late-Dec/early-Jan boundary
    week). Returns a dict ordered by the (iso_year, iso_week) key,
    mirroring the daily ref_closes dict's day-keyed convention."""
    by_week = {}
    for day in sorted(ref_closes.keys()):
        if ref_closes[day] is None:
            continue
        iso_year, iso_week, _ = day.isocalendar()
        week_key = (iso_year, iso_week)
        by_week[week_key] = ref_closes[day]  # overwritten by later days in the same week -> last valid close wins
    return by_week


def compute_weekly_log_returns(weekly_closes: dict) -> dict:
    """week_t -> log(close_t / close_{t-1}), for the week immediately
    following each prior week in sorted order. Structurally identical
    to study_volatility_regime.compute_daily_log_returns(), weeks
    instead of days."""
    weeks_sorted = sorted(weekly_closes.keys())
    returns = {}
    for i in range(1, len(weeks_sorted)):
        prev_w, w = weeks_sorted[i - 1], weeks_sorted[i]
        returns[w] = float(np.log(weekly_closes[w] / weekly_closes[prev_w]))
    return returns


def compute_weekly_momentum_signal(returns: dict, all_weeks: list) -> dict:
    """week_t -> mom[week_t] = SUM of the MOMENTUM_LOOKBACK_WEEKS most
    recent weekly log returns strictly before week_t, or absent if
    fewer than that many prior weekly returns are available.
    Structurally identical to
    study_nq_trend_following.compute_momentum_signal(), days -> weeks."""
    return_weeks_sorted = sorted(returns.keys())
    mom = {}
    for week_t in all_weeks:
        prior = [w for w in return_weeks_sorted if w < week_t]
        if len(prior) < MOMENTUM_LOOKBACK_WEEKS:
            continue
        window_weeks = prior[-MOMENTUM_LOOKBACK_WEEKS:]
        mom[week_t] = float(sum(returns[w] for w in window_weeks))
    return mom


def compute_weekly_pnl(positions: dict, weekly_closes: dict) -> pd.DataFrame:
    """One row per classifiable week from the second such week onward:
    this week's P&L uses THIS week's position (already known before
    this week's first session, computed from data through last week's
    close) against this week's actual price change, charging
    FLIP_COST_POINTS when this week's position differs from the prior
    classifiable week's position. Structurally identical to
    study_nq_trend_following.compute_daily_pnl(), days -> weeks."""
    weeks = sorted(w for w in positions.keys() if weekly_closes.get(w) is not None)
    rows = []
    for i in range(1, len(weeks)):
        prev_w, w = weeks[i - 1], weeks[i]
        prev_close = weekly_closes[prev_w]
        this_close = weekly_closes[w]
        position = positions[w]
        prev_position = positions[prev_w]
        price_change = this_close - prev_close
        pnl = position * price_change
        flipped = position != prev_position
        cost = FLIP_COST_POINTS if flipped else 0.0
        rows.append({
            # named 'date' (not 'week') so the reused
            # robustness_drop_largest_pnl_day() from
            # study_nq_trend_following.py -- which looks up the
            # 'date' column -- works unmodified on this weekly frame
            "date": f"{w[0]}-W{w[1]:02d}",
            "position": position,
            "flipped": bool(flipped),
            "price_change": price_change,
            "pnl": pnl,
            "cost": cost,
            "net_pnl": pnl - cost,
        })
    return pd.DataFrame(rows)


def main():
    full_df, is_synthetic = load_price_data(context="study_nq_weekly_trend_following.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)

    weekly_closes = resample_to_weekly_closes(ref_closes)
    weekly_returns = compute_weekly_log_returns(weekly_closes)
    all_weeks = sorted(weekly_closes.keys())

    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)
    positions = compute_positions(mom_by_week)  # reused unmodified from study_nq_trend_following
    pnl_df = compute_weekly_pnl(positions, weekly_closes)

    out_path = DATA_DIR / "study_nq_weekly_trend_following_discovery.csv"
    pnl_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("NQ WEEKLY TIME-SERIES MOMENTUM STUDY (exp-047) -- Discovery slice")
    print("=" * 78)
    print(f"\nTotal weekly bars (resampled from daily): {len(weekly_closes)}")
    print(f"Classifiable weeks ({MOMENTUM_LOOKBACK_WEEKS}+ prior weekly returns): {len(mom_by_week)}")
    print(f"Weeks with a computed weekly P&L: {len(pnl_df)}")

    primary = analyze_primary(pnl_df)  # reused unmodified from study_nq_trend_following
    print("\n--- PRIMARY: mean weekly net P&L ---")
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['statistically_credible']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= 2x own realized cost drag): "
          f"{primary['economically_meaningful']}")
    print(f"\n  MANDATORY DISCLOSURE -- position flips: {primary['n_flips']} "
          f"across {primary['n']} classifiable weeks")

    print("\n--- Robustness (a): drop single largest-magnitude weekly net P&L week ---")
    drop_result = robustness_drop_largest_pnl_day(pnl_df)  # reused unmodified, column names match
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(pnl_df)  # reused unmodified
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n" + "=" * 78)
    n = primary["n"]
    meets_min = n >= 150
    if primary["statistically_credible"] and primary["economically_meaningful"]:
        verdict = "PROMOTE-ELIGIBLE (adapted bar, per exp-038 precedent) -- clears both gates"
    else:
        verdict = "kill -- does not clear the adapted statistical/economic gate"
    print(f"Verdict: {verdict}")
    print(f"(Note: the adapted bar, per exp-038 precedent, does not require the standard "
          f"150-trade minimum for a signal this infrequent by construction; n={n} weekly "
          f"observations, disclosed up front as a small sample.)")

    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "verdict": verdict,
        "total_weekly_bars": len(weekly_closes),
    }
    json_path = DATA_DIR / "study_nq_weekly_trend_following_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
