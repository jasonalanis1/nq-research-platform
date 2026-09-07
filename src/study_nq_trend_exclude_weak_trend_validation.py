"""
study_nq_trend_exclude_weak_trend_validation.py
====================================================

exp-056 -- the pre-registered prospective test that exp-055
(hyp-000025, the collective-evidence pilot) said was the required next
step before its one candidate finding could be trusted.

FROZEN HYPOTHESIS (written before this script is run, before any
Validation-slice number is looked at):

    NQ's 52-week weekly trend-momentum signal (exp-047's signal,
    UNCHANGED) clears this project's promotion bar when weeks where
    price sits close to its own 52-week moving average (the "low"
    distance-from-MA tercile -- a weak-trend reading, using the SAME
    causal_expanding_tercile() method already used in exp-055,
    UNCHANGED) are EXCLUDED, evaluated ONLY on the Validation slice
    (2021-10-04 -> 2024-01-03) -- data this specific signal/filter
    combination has never been tested on before.

This distills exp-055's aggregate, multi-lens "fraction beating
baseline" finding into ONE concrete, tradeable question about the
single underlying signal: does skipping weak-trend weeks actually
improve the raw signal's own result? That is the natural trading
implication of exp-055's finding, and the only version of it precise
enough to pre-register and test on one slice of fresh data.

CONTINUITY, NOT A COLD RESTART (same discipline as exp-054): the
distance-from-MA classifier and the 52-week momentum signal both need
trailing history. Both are computed continuously across Discovery +
Validation combined (never touching HOLDOUT_GEN2), exactly as a live
system would. Only the FINAL evaluation rows are restricted to weeks
whose first trading day falls after DISCOVERY_END_DATE.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes (study_volatility_regime.py)
  - resample_to_weekly_closes, compute_weekly_log_returns,
    compute_weekly_momentum_signal, compute_weekly_pnl
    (study_nq_weekly_trend_following.py)
  - compute_positions, analyze_primary (study_nq_trend_following.py)
  - causal_expanding_tercile (study_collective_evidence_pilot.py,
    exp-055) -- the exact same causal, point-in-time ranking method
    used to find this candidate in the first place.

NEW CODE: only the Validation-week filter and the distance-value
computation loop (identical math to exp-055's, just over a wider
Discovery+Validation date range for continuity).

PROMOTION CONSEQUENCE, decided in advance: same as exp-054 -- a clean
pass here is logged as VALIDATION CANDIDATE (still not live-authorized,
would need a HOLDOUT GEN2 pass next). A fail closes this specific
filtered-signal line; no retuning of the distance threshold or window
on this result.

HOW TO RUN:
    python3 src/study_nq_trend_exclude_weak_trend_validation.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import DISCOVERY_END_DATE, VALIDATION_END_DATE
from study_volatility_regime import compute_daily_ref_closes  # reused unmodified
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
from study_collective_evidence_pilot import causal_expanding_tercile  # reused unmodified, exp-055

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def analyze_split(pnl_df, label: str) -> dict:
    print(f"\n{'-' * 78}")
    print(f"{label}")
    print(f"{'-' * 78}")
    if len(pnl_df) < 10:
        print(f"  n={len(pnl_df)} -- too few weeks to analyze meaningfully.")
        return {"n": len(pnl_df), "skipped": True}
    primary = analyze_primary(pnl_df)  # reused unmodified
    for k, v in primary.items():
        print(f"  {k}: {v}")
    print(f"  Statistically credible: {primary['statistically_credible']}   "
          f"Economically meaningful: {primary['economically_meaningful']}")
    return primary


def main():
    print("=" * 78)
    print("EXP-056: NQ TREND MOMENTUM, EXCLUDING WEAK-TREND WEEKS -- PROSPECTIVE VALIDATION")
    print("=" * 78)
    print("\nPre-registered single hypothesis (see this file's docstring), tested on the")
    print("Validation slice only -- data this signal/filter combination has never seen.\n")

    full_df, is_synthetic = load_price_data(context="study_nq_trend_exclude_weak_trend_validation.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    research_df = full_df[full_df.index <= VALIDATION_END_DATE]
    print(f"Discovery+Validation combined (for signal/filter warm-up continuity): "
          f"{len(research_df.index.normalize().unique())} trading day(s) through {VALIDATION_END_DATE.date()}.")

    day_groups = {day: sub for day, sub in research_df.groupby(research_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)  # reused unmodified

    weekly_closes = resample_to_weekly_closes(ref_closes)  # reused unmodified
    weekly_returns = compute_weekly_log_returns(weekly_closes)  # reused unmodified
    all_weeks = sorted(weekly_closes.keys())
    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)  # reused unmodified
    positions = compute_positions(mom_by_week)  # reused unmodified
    pnl_df = compute_weekly_pnl(positions, weekly_closes)  # reused unmodified

    # NEW (same math as exp-055): distance from the 52-week moving average of
    # weekly closes, as a percentage, causal-expanding-tercile classified.
    dist_values = {}
    for i, w in enumerate(all_weeks):
        if i < 52:
            continue
        window = [weekly_closes[all_weeks[j]] for j in range(i - 52, i)]
        ma = sum(window) / len(window)
        dist_values[w] = 100.0 * (weekly_closes[w] - ma) / ma
    dist_by_week = causal_expanding_tercile(dist_values)  # reused unmodified, exp-055

    # NEW: which weeks are genuinely new -- first trading day strictly after
    # DISCOVERY_END_DATE, i.e. never scored by exp-047 or exp-055.
    day_to_week = {}
    for day in sorted(day_groups.keys()):
        iso_year, iso_week, _ = day.isocalendar()
        day_to_week.setdefault((iso_year, iso_week), []).append(day)
    discovery_end_date = DISCOVERY_END_DATE.date()
    validation_weeks = {
        wk for wk, days in day_to_week.items() if sorted(days)[0] > discovery_end_date
    }

    def dist_of_row(date_str: str):
        year_s, week_s = date_str.split("-W")
        return dist_by_week.get((int(year_s), int(week_s)))

    def is_validation_row(date_str: str) -> bool:
        year_s, week_s = date_str.split("-W")
        return (int(year_s), int(week_s)) in validation_weeks

    pnl_df["distance_tercile"] = pnl_df["date"].apply(dist_of_row)
    pnl_df["is_validation"] = pnl_df["date"].apply(is_validation_row)

    validation_df = pnl_df[pnl_df["is_validation"]].reset_index(drop=True)
    print(f"\nTotal Validation-slice weeks with a computed weekly P&L: {len(validation_df)}")

    print(f"\n{'=' * 78}")
    print("BACKGROUND (not the test): exp-047's original signal, unfiltered, on Validation")
    print(f"{'=' * 78}")
    background = analyze_split(validation_df, "Validation slice, ALL weeks (context only)")

    print(f"\n{'=' * 78}")
    print("PRIMARY TEST (pre-registered): EXCLUDING weak-trend (near-MA / 'low') weeks")
    print(f"{'=' * 78}")
    filtered_df = validation_df[validation_df["distance_tercile"] != "low"].reset_index(drop=True)
    primary = analyze_split(filtered_df, f"Validation slice, weak-trend weeks excluded (n={len(filtered_df)})")

    passed = (
        isinstance(primary, dict)
        and not primary.get("skipped")
        and primary.get("statistically_credible")
        and primary.get("economically_meaningful")
    )

    print(f"\n{'=' * 78}")
    if passed:
        verdict = ("PASS. Excluding weak-trend weeks clears the promotion bar on the "
                    "Validation slice -- genuinely new data, pre-registered hypothesis, one "
                    "single test. Logged as VALIDATION CANDIDATE. Still NOT authorized for "
                    "live trading -- next step per the project's ladder would be a "
                    "HOLDOUT GEN2 test, budgeted and requested separately, not run casually.")
    else:
        verdict = ("FAIL. Excluding weak-trend weeks does not clear the bar on fresh "
                    "Validation-slice data. exp-055's exploratory finding does not replicate "
                    "out of sample -- treated as noise from the correlated-lens pilot, not a "
                    "real effect. This line of inquiry is closed: no retuning of the "
                    "distance threshold or lookback window on this result.")
    print(f"Verdict: {verdict}")

    out = {
        "background_all_weeks_validation": background,
        "primary_exclude_weak_trend_validation": primary,
        "passed": passed,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_nq_trend_exclude_weak_trend_validation_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
