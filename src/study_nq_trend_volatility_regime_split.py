"""
study_nq_trend_volatility_regime_split.py
=============================================

EXPLORATORY / HYPOTHESIS-GENERATING ONLY -- NOT a proper new test.

exp-047 (`src/study_nq_weekly_trend_following.py`, hyp-000017) tested
NQ's 52-week weekly trend-momentum signal on the Discovery slice and
got a near-miss: mean +19.38 pts/week, 90% CI [-1.165, +40.414] --
touches zero, killed. That hypothesis's own logged notes explicitly
stated: "Only defensible follow-up would be a separately pre-registered
prospective test on new future data, not a re-mine of this Discovery
history -- not currently authorized."

This script deliberately does re-mine that same Discovery history --
Jason asked (2026-09-07) whether a strategy that doesn't win overall
might still win consistently within some sub-condition (e.g. calm vs.
volatile markets), and wanted that checked before committing to a
bigger framework. Per the Path-to-Profitability Advisor's guidance the
same day: this is legitimate ONLY as a cheap, fast, honestly-labeled
exploratory check using ONE condition chosen for a real economic
reason (not scanned for), with the result explicitly downgraded to
"hypothesis-generating" -- never treated as evidence, never promoted,
and any promising split found here would need a fresh prospective test
on data never used for this exploration before being trusted at all.
That is the deliberate, disclosed exception being made to exp-047's
own no-re-mine commitment here -- not a quiet violation of it.

CONDITION CHOSEN (pre-specified before looking at the split results):
market volatility regime, using `classify_regimes()` from
`study_volatility_regime.py` (already built and reviewed in an earlier
study, reused UNMODIFIED here) -- an expanding, point-in-time,
causal, tercile-based classification (never full-sample, no
lookahead). Chosen because it is the standard, literature-grounded
explanation for time-series-momentum strength varying over time (not
picked because it happened to make this split look good -- it was
picked before this script was run at all).

Each week is assigned the volatility regime of ITS OWN FIRST TRADING
DAY (the same causal information already available before that week's
position is taken, per exp-047's own convention -- no new lookahead
introduced by this split).

REUSED, UNMODIFIED (almost nothing here is new code):
  - compute_daily_ref_closes, compute_daily_log_returns,
    compute_trailing_volatility, classify_regimes
    (study_volatility_regime.py)
  - resample_to_weekly_closes, compute_weekly_log_returns,
    compute_weekly_momentum_signal, compute_weekly_pnl
    (study_nq_weekly_trend_following.py)
  - compute_positions, analyze_primary (study_nq_trend_following.py)

NEW CODE: only the day-to-week regime mapping and the split-and-
re-analyze loop below.

HOW TO RUN:
    python3 src/study_nq_trend_volatility_regime_split.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import (  # reused unmodified
    compute_daily_ref_closes,
    compute_daily_log_returns,
    compute_trailing_volatility,
    classify_regimes,
)
from study_nq_weekly_trend_following import (  # reused unmodified
    resample_to_weekly_closes,
    compute_weekly_log_returns,
    compute_weekly_momentum_signal,
    compute_weekly_pnl,
)
from study_nq_trend_following import (  # reused unmodified
    compute_positions,
    analyze_primary,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def build_week_to_regime(day_groups: dict, ref_closes: dict) -> dict:
    """week_key -> the volatility regime ('high'/'mid'/'low') of that
    week's own first trading day, using classify_regimes()'s existing
    causal, point-in-time tercile classification unmodified. A week
    whose first day has no regime yet (very early warm-up) is left
    unmapped and excluded from all three regime splits below (not
    silently assigned to one)."""
    daily_returns = compute_daily_log_returns(ref_closes)
    all_days = sorted(day_groups.keys())
    vol_by_day = compute_trailing_volatility(daily_returns, all_days)
    regimes = classify_regimes(vol_by_day)  # reused unmodified

    day_to_week = {}
    for day in all_days:
        iso_year, iso_week, _ = day.isocalendar()
        day_to_week.setdefault((iso_year, iso_week), []).append(day)

    week_to_regime = {}
    for week_key, days in day_to_week.items():
        first_day = sorted(days)[0]
        if first_day in regimes:
            week_to_regime[week_key] = regimes[first_day]
    return week_to_regime


def analyze_split(pnl_df, label: str) -> dict:
    print(f"\n{'-' * 78}")
    print(f"{label}")
    print(f"{'-' * 78}")
    if len(pnl_df) < 10:
        print(f"  n={len(pnl_df)} -- too few weeks to analyze meaningfully, skipping.")
        return {"n": len(pnl_df), "skipped": True}
    primary = analyze_primary(pnl_df)  # reused unmodified
    for k, v in primary.items():
        print(f"  {k}: {v}")
    print(f"  Statistically credible: {primary['statistically_credible']}   "
          f"Economically meaningful: {primary['economically_meaningful']}")
    return primary


def main():
    print("=" * 78)
    print("EXP-053 (EXPLORATORY): NQ WEEKLY TREND MOMENTUM, SPLIT BY VOLATILITY REGIME")
    print("=" * 78)
    print("\nNOT a proper new test -- re-mines exp-047's own Discovery history, with the")
    print("deliberate disclosed exception explained in this file's docstring. Any result")
    print("here is hypothesis-generating only, never evidence, never promoted as-is.\n")

    full_df, is_synthetic = load_price_data(context="study_nq_trend_volatility_regime_split.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)

    # exp-047's own pipeline, unmodified, for the underlying signal/positions/pnl.
    weekly_closes = resample_to_weekly_closes(ref_closes)
    weekly_returns = compute_weekly_log_returns(weekly_closes)
    all_weeks = sorted(weekly_closes.keys())
    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)
    positions = compute_positions(mom_by_week)  # reused unmodified
    pnl_df = compute_weekly_pnl(positions, weekly_closes)  # reused unmodified

    # NEW: map each week to its own first-trading-day volatility regime.
    week_to_regime = build_week_to_regime(day_groups, ref_closes)

    def regime_of_row(date_str: str):
        # date_str is "YYYY-Www" (exp-047's own weekly-row convention)
        year_s, week_s = date_str.split("-W")
        return week_to_regime.get((int(year_s), int(week_s)))

    pnl_df["regime"] = pnl_df["date"].apply(regime_of_row)

    print(f"\nTotal weeks with a computed weekly P&L (same as exp-047): {len(pnl_df)}")
    print(f"Weeks with a mapped volatility regime: {pnl_df['regime'].notna().sum()} "
          f"(remainder: no regime yet available for that week's first day)")

    results = {}
    for regime in ["low", "mid", "high"]:
        subset = pnl_df[pnl_df["regime"] == regime].reset_index(drop=True)
        results[regime] = analyze_split(
            subset, f"Regime = {regime.upper()} volatility  (n={len(subset)} weeks)"
        )

    print(f"\n{'=' * 78}")
    print("REFERENCE: full-sample exp-047 result (all regimes combined, unfiltered)")
    print(f"{'=' * 78}")
    results["all_combined_reference"] = analyze_split(pnl_df, "All weeks (exp-047's original result)")

    any_regime_clears = any(
        isinstance(r, dict) and r.get("statistically_credible") and r.get("economically_meaningful")
        for k, r in results.items() if k != "all_combined_reference"
    )
    print(f"\n{'=' * 78}")
    if any_regime_clears:
        verdict = ("At least one volatility regime clears the promotion bar on this "
                    "(already-used) Discovery data. EXPLORATORY ONLY -- this is a candidate "
                    "for a fresh, pre-registered prospective test on new data, not a result "
                    "to act on directly. Per the frozen exp-047 pre-commitment, this Discovery "
                    "slice is now used up for this signal family; a future test must use data "
                    "not yet touched by any test of this family.")
    else:
        verdict = ("No volatility regime clears the promotion bar either. The near-miss does "
                    "not appear to be concentrated in calm or volatile markets specifically -- "
                    "on this data, splitting by this one condition does not reveal a hidden "
                    "winner. Consistent with the Advisor's framing: this signal doesn't show "
                    "much raw material to find patterns in, which is itself informative.")
    print(f"Verdict: {verdict}")

    out_path = DATA_DIR / "study_nq_trend_volatility_regime_split_discovery_results.json"
    with open(out_path, "w") as f:
        json.dump({"results": results, "verdict": verdict}, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
