"""
study_asymmetric_stop_target_overlay.py
========================================

Implements the frozen spec in
`research/studies/asymmetric-stop-target-overlay-scoping.md` (v2,
Advisor-reviewed twice -- once on the general design, once on the
hard-cap-vs-trailing exit decision -- and signed off by Jason
2026-09-06) -- exp-048. Directly implements Jason's own risk-
management idea (paraphrased: stop out at a defined loss, hold until
at least doubling winnings) applied concretely to exp-047's weekly
trend-following signal, this project's closest-ever near-miss.

Per the Path-to-Profitability Advisor's explicit recommendation on the
final open design question: the take-profit is a HARD CAP at +2R
(exit immediately when touched), not a trailing exit. A trailing
design was rejected because it would require carrying position state
across exp-047's weekly rebalance boundary (an architecture change,
not a parameter choice) and would calibrate an untested trail
distance against only ~42 weeks that ever reach +2R -- both judged
worse than the hard cap's known, bounded, already-disclosed
tail-capping cost.

INTERPRETATION CAVEAT (Advisor-recommended, recorded before this is
run): if this comes back null, that is evidence against THIS SPECIFIC
capped parameterization (1R stop / hard 2R cap / 20-day ATR) -- not a
general rejection of Jason's "let winners run" intuition. A trailing-
exit design remains a distinct, not-yet-tested hypothesis, not one
this result speaks to either way.

Reuses, UNMODIFIED, wherever possible:
  - study_nq_weekly_trend_following.resample_to_weekly_closes()
  - study_nq_weekly_trend_following.compute_weekly_log_returns()
  - study_nq_weekly_trend_following.compute_weekly_momentum_signal()
  - study_nq_trend_following.compute_positions()
  - study_nq_trend_following.FLIP_COST_POINTS
  - study_nq_trend_following.analyze_primary()
  - study_nq_trend_following.robustness_drop_largest_pnl_day()
  - study_nq_trend_following.robustness_split_half()
  - study_volatility_regime.compute_daily_ref_closes()

New code (per the frozen spec): the 20-day ATR risk-unit calculation,
and the path-dependent stop/target exit-price resolution against real
1-minute intraday data (adapted from the already-run, purely
descriptive pilot tabulation in src/pilot_stop_target_tabulation.py,
extended here to also return the P&L-relevant exit price, not just a
touch/no-touch count).

ONE primary test, same two checks as exp-047, read MORE STRICTLY per
the frozen spec's Section 4 (this is a follow-on test of a near-miss,
not an independent first test -- only a comfortable, not merely
technical, pass on both checks is treated as clearing the bar):
1. 90% bootstrap CI on the resulting weekly net P&L series, entirely
   above zero.
2. Mean weekly net P&L economically meaningful vs. cost drag.

HOW TO RUN:
    python3 src/study_asymmetric_stop_target_overlay.py
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

ATR_WINDOW_DAYS = 20  # frozen spec: matches this signal's own ~52-week (slow) cadence
STOP_R = 1.0
TARGET_R = 2.0  # HARD CAP, per Advisor's explicit recommendation -- not trailing


def compute_daily_ohlc(day_groups: dict, ref_closes: dict) -> dict:
    """One day -> {high, low, close} aggregated from that day's 1-minute
    bars, close taken from the already-computed daily reference close
    (same series exp-047 uses)."""
    daily_ohlc = {}
    for day, sub in day_groups.items():
        if len(sub) == 0:
            continue
        daily_ohlc[day] = {
            "high": float(sub["High"].max()),
            "low": float(sub["Low"].min()),
            "close": ref_closes.get(day),
        }
    return daily_ohlc


def compute_true_range_series(daily_ohlc: dict, days_sorted: list) -> dict:
    """True Range per day (standard 3-way max), skipping days with no
    valid closes on either side."""
    tr_by_day = {}
    for i in range(1, len(days_sorted)):
        d, prev_d = days_sorted[i], days_sorted[i - 1]
        if daily_ohlc[d]["close"] is None or daily_ohlc[prev_d]["close"] is None:
            continue
        h, l, prev_c = daily_ohlc[d]["high"], daily_ohlc[d]["low"], daily_ohlc[prev_d]["close"]
        tr_by_day[d] = max(h - l, abs(h - prev_c), abs(l - prev_c))
    return tr_by_day


def make_atr_lookup(tr_by_day: dict, days_sorted: list):
    """Returns a function: target_day -> trailing ATR_WINDOW_DAYS-day
    mean True Range using only days strictly before target_day (causal,
    no lookahead), or None if insufficient history."""
    def atr_as_of(target_day):
        prior_days = [d for d in days_sorted if d in tr_by_day and d < target_day]
        if len(prior_days) < ATR_WINDOW_DAYS:
            return None
        window = prior_days[-ATR_WINDOW_DAYS:]
        return float(np.mean([tr_by_day[d] for d in window]))
    return atr_as_of


def resolve_week_exit(position: int, entry_price: float, r: float,
                       week_days: list, day_groups: dict):
    """Walks this week's 1-minute bars in chronological order. Returns
    (outcome, exit_price_delta_from_entry) where outcome is one of
    'stop_first', 'target_first', 'neither'. For 'neither', the caller
    uses the normal weekly rebalance price change instead (matching
    exp-047's convention) -- this function returns None for that case's
    delta, since it isn't resolved by the path check.

    Same-bar ambiguity (a single bar's range touches both levels):
    conservatively assumes the stop triggers first, per the frozen
    spec (standard industry convention, not resolved in the strategy's
    favor).
    """
    if position > 0:
        stop_level = entry_price - STOP_R * r
        target_level = entry_price + TARGET_R * r
    else:
        stop_level = entry_price + STOP_R * r
        target_level = entry_price - TARGET_R * r

    for day in week_days:
        sub = day_groups.get(day)
        if sub is None or len(sub) == 0:
            continue
        for _, bar in sub.sort_index().iterrows():
            hi, lo = bar["High"], bar["Low"]
            if position > 0:
                stop_touched = lo <= stop_level
                target_touched = hi >= target_level
            else:
                stop_touched = hi >= stop_level
                target_touched = lo <= target_level
            if stop_touched and target_touched:
                return "stop_first", stop_level - entry_price
            elif stop_touched:
                return "stop_first", stop_level - entry_price
            elif target_touched:
                return "target_first", target_level - entry_price
    return "neither", None


def compute_overlay_pnl(positions: dict, weekly_closes: dict, day_to_week: dict,
                         day_groups: dict, atr_as_of) -> pd.DataFrame:
    """One row per classifiable week from the second such week onward,
    same convention as exp-047's compute_weekly_pnl(). price_change is
    now resolved via the stop/target path check when either level is
    touched during the entry week, or via the normal week-over-week
    reference-close change when neither is touched (identical to
    exp-047 for that subset of weeks). Column names match exp-047's
    compute_weekly_pnl() exactly ("date", "position", "flipped",
    "price_change", "pnl", "cost", "net_pnl") so the reused
    analyze_primary()/robustness functions work unmodified."""
    weeks = sorted(w for w in positions.keys() if weekly_closes.get(w) is not None)
    rows = []
    outcome_counts = {"stop_first": 0, "target_first": 0, "neither": 0, "no_atr_available": 0}
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
            price_change = this_close - prev_close  # falls back to exp-047's own convention
        else:
            outcome, delta = resolve_week_exit(position, entry_price, r, week_days, day_groups)
            outcome_counts[outcome] += 1
            if delta is not None:
                price_change = delta
            else:
                price_change = this_close - prev_close  # neither touched -- exp-047's convention

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
    full_df, is_synthetic = load_price_data(context="study_asymmetric_stop_target_overlay.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)

    daily_ohlc = compute_daily_ohlc(day_groups, ref_closes)
    days_sorted = sorted(daily_ohlc.keys())
    tr_by_day = compute_true_range_series(daily_ohlc, days_sorted)
    atr_as_of = make_atr_lookup(tr_by_day, days_sorted)

    weekly_closes = resample_to_weekly_closes(ref_closes)
    weekly_returns = compute_weekly_log_returns(weekly_closes)
    all_weeks = sorted(weekly_closes.keys())
    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)
    positions = compute_positions(mom_by_week)  # reused unmodified

    day_to_week = {}
    for day in days_sorted:
        iso_year, iso_week, _ = day.isocalendar()
        day_to_week.setdefault((iso_year, iso_week), []).append(day)

    pnl_df, outcome_counts = compute_overlay_pnl(positions, weekly_closes, day_to_week, day_groups, atr_as_of)

    out_path = DATA_DIR / "study_asymmetric_stop_target_overlay_discovery.csv"
    pnl_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("ASYMMETRIC STOP-LOSS/TAKE-PROFIT OVERLAY STUDY (exp-048) -- Discovery slice")
    print("HARD CAP design: -1R stop / +2R target, 20-day ATR risk unit")
    print("=" * 78)
    print(f"\nWeeks with a computed overlay P&L: {len(pnl_df)}")
    print(f"Exit-path breakdown: {outcome_counts}")

    primary = analyze_primary(pnl_df)  # reused unmodified
    print("\n--- PRIMARY: mean weekly net P&L (overlay-adjusted) ---")
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['statistically_credible']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= 2x own realized cost drag): "
          f"{primary['economically_meaningful']}")
    print(f"\n  MANDATORY DISCLOSURE -- position flips: {primary['n_flips']} "
          f"across {primary['n']} classifiable weeks")

    print("\n--- Robustness (a): drop single largest-magnitude weekly net P&L week ---")
    drop_result = robustness_drop_largest_pnl_day(pnl_df)  # reused unmodified
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(pnl_df)  # reused unmodified
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n" + "=" * 78)
    n = primary["n"]
    # Per the frozen spec's Section 4/5: a follow-on test of a near-miss is read MORE
    # STRICTLY -- a narrow/borderline pass is reported as inconclusive, not promoted.
    ci_low, ci_high = primary.get("ci_90", (float("nan"), float("nan")))
    comfortable_margin = None
    if ci_low is not None and primary.get("mean_net_pnl") not in (None, 0):
        comfortable_margin = (ci_low > 0) and ((ci_low / primary["mean_net_pnl"]) > 0.15)

    if primary["statistically_credible"] and primary["economically_meaningful"]:
        verdict = ("PROMOTE-ELIGIBLE, COMFORTABLE PASS -- clears both gates well clear of zero"
                    if comfortable_margin else
                    "PROMOTE-ELIGIBLE, BUT NARROW -- clears both gates only technically; "
                    "flagged for explicit Jason+Advisor discussion before treating as a real signal, "
                    "per the frozen spec's stricter reading of a follow-on test")
    else:
        verdict = ("kill -- does not clear the adapted statistical/economic gate. Per the frozen "
                    "spec's interpretation caveat: this rejects the SPECIFIC 1R-stop/hard-2R-cap/"
                    "20-day-ATR design, not Jason's underlying risk-management intuition in general.")
    print(f"Verdict: {verdict}")

    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "exit_path_breakdown": outcome_counts,
        "verdict": verdict,
        "design": {"stop_R": STOP_R, "target_R": TARGET_R, "atr_window_days": ATR_WINDOW_DAYS, "exit_type": "hard_cap"},
    }
    json_path = DATA_DIR / "study_asymmetric_stop_target_overlay_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
