"""
study_trailing_stop_overlay.py
===============================

Implements the frozen spec in
`research/studies/trailing-stop-overlay-scoping.md` (v1, Advisor-cleared
2026-09-06 conditional on the explicit per-bar algorithm below existing
before any code was written; Jason authorized building this by
delegating the design to the Advisor's review, following exp-048's kill)
-- exp-049. Third test in the exp-047 signal family (exp-047: near-miss;
exp-048: hard-cap overlay, kill). Per the frozen spec's pre-commitment:
if this also fails to clear the bar comfortably, this signal family is
shelved -- not followed by a further variant.

Reuses, UNMODIFIED, wherever possible: exp-047's weekly signal/positions
machinery, exp-048's 20-day-ATR risk-unit calculation and daily OHLC/
True-Range helpers, and study_nq_trend_following's FLIP_COST_POINTS/
analyze_primary()/robustness functions.

New code (per the frozen spec): the per-bar trailing-stop algorithm,
which activates a ratcheting trail (distance = the same 1R already
defined, not a new parameter) once a position's favorable excursion
reaches +2R, per the exact causal, no-lookahead ordering pinned in the
frozen spec Section 3: each bar's exit check uses the stop level as it
stood at the END of the PREVIOUS bar, then peak/trail are updated using
the CURRENT bar -- so a bar can never be stopped out by a trail level it
itself just set.

HOW TO RUN:
    python3 src/study_trailing_stop_overlay.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes
from study_nq_weekly_trend_following import (  # reused unmodified
    resample_to_weekly_closes,
    compute_weekly_log_returns,
    compute_weekly_momentum_signal,
)
from study_nq_trend_following import (  # reused unmodified
    FLIP_COST_POINTS,
    compute_positions,
    analyze_primary,
    robustness_drop_largest_pnl_day,
    robustness_split_half,
)
from study_asymmetric_stop_target_overlay import (  # reused unmodified
    compute_daily_ohlc,
    compute_true_range_series,
    make_atr_lookup,
    ATR_WINDOW_DAYS,
    STOP_R,
    TARGET_R,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

TRAIL_R = STOP_R  # frozen spec: trail distance = the same 1R already defined, not a new parameter


def resolve_week_exit_trailing(position: int, entry_price: float, r: float,
                                week_days: list, day_groups: dict):
    """Walks this week's 1-minute bars in chronological order per the
    frozen spec's exact per-bar algorithm. Returns (outcome, exit_delta)
    where outcome is 'stopped_or_trailed' or 'neither'. For 'neither',
    the caller uses the normal weekly rebalance price change (matching
    exp-047/048's convention).

    No-lookahead ordering: current_stop as checked against THIS bar was
    set at the end of the PREVIOUS bar (or is the initial -1R stop on
    the first bar) -- peak/trail are only updated AFTER the exit check,
    using this bar's own high/low, so a bar can never trigger a trail
    level it itself just created.
    """
    target_level_activation = entry_price + TARGET_R * r if position > 0 else entry_price - TARGET_R * r
    if position > 0:
        current_stop = entry_price - STOP_R * r
        peak = entry_price
    else:
        current_stop = entry_price + STOP_R * r
        peak = entry_price  # "peak" here means the running best (lowest) price for a short

    trail_active = False

    for day in week_days:
        sub = day_groups.get(day)
        if sub is None or len(sub) == 0:
            continue
        for _, bar in sub.sort_index().iterrows():
            hi, lo = bar["High"], bar["Low"]

            # Step 1/2: exit check using the level set at the end of the previous bar
            if position > 0:
                if lo <= current_stop:
                    return "stopped_or_trailed", current_stop - entry_price
            else:
                if hi >= current_stop:
                    return "stopped_or_trailed", current_stop - entry_price

            # Step 3: update peak/trough using THIS bar's high/low
            if position > 0:
                peak = max(peak, hi)
            else:
                peak = min(peak, lo)

            # Step 4: activate trail if favorable excursion reaches +2R
            if not trail_active:
                if position > 0 and peak >= target_level_activation:
                    trail_active = True
                elif position < 0 and peak <= target_level_activation:
                    trail_active = True

            # Step 5: ratchet the stop (only tighter), used starting next bar
            if trail_active:
                if position > 0:
                    current_stop = max(current_stop, peak - TRAIL_R * r)
                else:
                    current_stop = min(current_stop, peak + TRAIL_R * r)

    return "neither", None


def compute_trailing_pnl(positions: dict, weekly_closes: dict, day_to_week: dict,
                          day_groups: dict, atr_as_of) -> pd.DataFrame:
    """Same row/column convention as exp-047/048's P&L tables, so the
    reused analyze_primary()/robustness functions work unmodified."""
    weeks = sorted(w for w in positions.keys() if weekly_closes.get(w) is not None)
    rows = []
    outcome_counts = {"stopped_or_trailed": 0, "neither": 0, "no_atr_available": 0}
    for i in range(1, len(weeks)):
        prev_w, w = weeks[i - 1], weeks[i]
        prev_close = weekly_closes[prev_w]
        this_close = weekly_closes[w]
        position = positions[w]
        prev_position = positions[prev_w]

        week_days = sorted(day_to_week.get(w, []))
        entry_price = prev_close

        r = atr_as_of(week_days[0]) if week_days else None
        if r is None or r <= 0 or not week_days:
            outcome_counts["no_atr_available"] += 1
            price_change = this_close - prev_close
        else:
            outcome, delta = resolve_week_exit_trailing(position, entry_price, r, week_days, day_groups)
            outcome_counts[outcome] += 1
            price_change = delta if delta is not None else (this_close - prev_close)

        pnl = position * price_change
        flipped = position != prev_position
        cost = FLIP_COST_POINTS if flipped else 0.0
        rows.append({
            "date": f"{w[0]}-W{w[1]:02d}",
            "position": position,
            "flipped": bool(flipped),
            "price_change": price_change,
            "pnl": pnl,
            "cost": cost,
            "net_pnl": pnl - cost,
        })
    return pd.DataFrame(rows), outcome_counts


def main():
    full_df, is_synthetic = load_price_data(context="study_trailing_stop_overlay.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)

    daily_ohlc = compute_daily_ohlc(day_groups, ref_closes)  # reused unmodified
    days_sorted = sorted(daily_ohlc.keys())
    tr_by_day = compute_true_range_series(daily_ohlc, days_sorted)  # reused unmodified
    atr_as_of = make_atr_lookup(tr_by_day, days_sorted)  # reused unmodified

    weekly_closes = resample_to_weekly_closes(ref_closes)
    weekly_returns = compute_weekly_log_returns(weekly_closes)
    all_weeks = sorted(weekly_closes.keys())
    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)
    positions = compute_positions(mom_by_week)  # reused unmodified

    day_to_week = {}
    for day in days_sorted:
        iso_year, iso_week, _ = day.isocalendar()
        day_to_week.setdefault((iso_year, iso_week), []).append(day)

    pnl_df, outcome_counts = compute_trailing_pnl(positions, weekly_closes, day_to_week, day_groups, atr_as_of)

    out_path = DATA_DIR / "study_trailing_stop_overlay_discovery.csv"
    pnl_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("TRAILING-STOP OVERLAY STUDY (exp-049) -- Discovery slice")
    print("Design: -1R initial stop, trail activates at +2R, trails by 1R behind peak")
    print("=" * 78)
    print(f"\nWeeks with a computed overlay P&L: {len(pnl_df)}")
    print(f"Exit-path breakdown: {outcome_counts}")

    primary = analyze_primary(pnl_df)  # reused unmodified
    print("\n--- PRIMARY: mean weekly net P&L (trailing-overlay-adjusted) ---")
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['statistically_credible']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= 2x own realized cost drag): "
          f"{primary['economically_meaningful']}")
    print(f"\n  MANDATORY DISCLOSURE -- position flips: {primary['n_flips']} "
          f"across {primary['n']} classifiable weeks")

    print("\n--- Robustness (a): drop single largest-magnitude weekly net P&L week ---")
    drop_result = robustness_drop_largest_pnl_day(pnl_df)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(pnl_df)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n" + "=" * 78)
    ci_low, ci_high = primary.get("ci_90", (float("nan"), float("nan")))
    comfortable_margin = None
    if ci_low is not None and primary.get("mean_net_pnl") not in (None, 0):
        comfortable_margin = (ci_low > 0) and ((ci_low / primary["mean_net_pnl"]) > 0.15)
    # Frozen spec: also compare against exp-047's own raw-signal mean (+19.38 pts/wk) --
    # a mean materially below that is not treated as a real improvement even if it
    # technically clears the bar.
    RAW_SIGNAL_MEAN = 19.37876254180602
    not_materially_below_raw = primary.get("mean_net_pnl") is not None and primary["mean_net_pnl"] >= 0.85 * RAW_SIGNAL_MEAN

    if primary["statistically_credible"] and primary["economically_meaningful"] and comfortable_margin and not_materially_below_raw:
        verdict = "PROMOTE-ELIGIBLE, COMFORTABLE PASS -- clears both gates well clear of zero, and does not sacrifice exp-047's raw-signal mean"
    elif primary["statistically_credible"] and primary["economically_meaningful"]:
        verdict = ("PROMOTE-ELIGIBLE, BUT FLAGGED -- clears both gates but either narrowly or with a mean "
                   "materially below exp-047's raw-signal mean; per the frozen spec's stricter follow-on "
                   "reading, NOT treated as a clear promotion without explicit Jason+Advisor discussion")
    else:
        verdict = ("kill -- does not clear the adapted statistical/economic gate. Per the frozen spec's "
                   "pre-commitment, the exp-047 signal family is shelved after this result.")
    print(f"Verdict: {verdict}")

    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "exit_path_breakdown": outcome_counts,
        "verdict": verdict,
        "design": {"stop_R": STOP_R, "trail_R": TRAIL_R, "activation_R": TARGET_R,
                   "atr_window_days": ATR_WINDOW_DAYS, "exit_type": "trailing"},
    }
    json_path = DATA_DIR / "study_trailing_stop_overlay_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
