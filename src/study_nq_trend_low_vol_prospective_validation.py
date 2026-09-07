"""
study_nq_trend_low_vol_prospective_validation.py
====================================================

exp-054 -- the fresh, pre-registered prospective test that exp-053
(hyp-000023, exploratory) said was the only legitimate next step, and
that exp-047's (hyp-000017) own logged notes required before trusting
anything about this signal family beyond its original Discovery-slice
near-miss.

FROZEN HYPOTHESIS (written before this script is run, before any
Validation-slice number is looked at):

    NQ's 52-week weekly trend-momentum signal (exp-047's signal,
    UNCHANGED) clears this project's promotion bar (90% CI entirely
    above zero AND economically meaningful) when restricted to weeks
    classified as LOW volatility regime (bottom tercile, via the
    same causal, point-in-time classify_regimes() already used in
    exp-053, UNCHANGED), evaluated ONLY on the VALIDATION slice
    (2021-10-04 -> 2024-01-03) -- data this specific signal family
    (raw momentum, and the low-vol-regime variant of it) has never
    been tested on before, in exp-047 or exp-053.

This is now ONE pre-registered test, not a 3-way split -- the low-vol
condition was chosen in advance (it's the one that cleared the bar in
exp-053's exploratory pass), so this script does NOT also report
mid/high regime Validation results as competing candidates. It reports
the unfiltered full-Validation-sample result only as background
context (what exp-047's original signal does on fresh data, with no
regime filter), never as an alternative hypothesis being chosen
between after the fact.

CONTINUITY, NOT A COLD RESTART (important for correctness): the
volatility regime classifier and the 52-week momentum signal both need
trailing history to warm up. This script computes both continuously
across Discovery + Validation combined (never touching HOLDOUT_GEN2),
exactly as a live system would -- it does not reset either calculation
at the Discovery/Validation boundary. Only the FINAL evaluation rows
are restricted to weeks whose first trading day falls after
DISCOVERY_END_DATE, i.e. genuinely new weeks this signal/filter
combination has never been scored on before.

REUSED, UNMODIFIED (this is still the same signal, same filter, same
math as exp-047 and exp-053 -- only the data window changes):
  - compute_daily_ref_closes, compute_daily_log_returns,
    compute_trailing_volatility, classify_regimes
    (study_volatility_regime.py)
  - resample_to_weekly_closes, compute_weekly_log_returns,
    compute_weekly_momentum_signal, compute_weekly_pnl
    (study_nq_weekly_trend_following.py)
  - compute_positions, analyze_primary (study_nq_trend_following.py)
  - build_week_to_regime (study_nq_trend_volatility_regime_split.py,
    exp-053) -- takes day_groups/ref_closes as arguments, so it works
    unmodified over this wider Discovery+Validation date range too.

NEW CODE: only the Validation-week filter (first trading day after
DISCOVERY_END_DATE) and the pass/fail write-up below.

PROMOTION CONSEQUENCE, decided in advance: if this clears the bar, the
result is logged as VALIDATION CANDIDATE (one clean out-of-sample
pass, still not enough for live authorization -- would need a HOLDOUT
GEN2 pass next, per the project's four-stage post-Discovery ladder). If
it does not clear the bar, this is a REJECTED result and the low-vol
lead from exp-053 is closed out as noise, not retested with a
different threshold or window.

HOW TO RUN:
    python3 src/study_nq_trend_low_vol_prospective_validation.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import DISCOVERY_END_DATE, VALIDATION_END_DATE
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
from study_nq_trend_volatility_regime_split import build_week_to_regime  # reused unmodified, exp-053

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
    print("EXP-054: NQ TREND MOMENTUM, LOW-VOL REGIME -- PROSPECTIVE VALIDATION TEST")
    print("=" * 78)
    print("\nPre-registered single hypothesis (see this file's docstring), tested on the")
    print("Validation slice only -- data this signal/filter combination has never seen.\n")

    full_df, is_synthetic = load_price_data(context="study_nq_trend_low_vol_prospective_validation.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    # Discovery + Validation combined, continuous (never touches HOLDOUT_GEN2) --
    # needed so the volatility classifier and the 52-week momentum signal have
    # real trailing history at the start of Validation, not a cold restart.
    research_df = full_df[full_df.index <= VALIDATION_END_DATE]
    print(f"Discovery+Validation combined (for signal/regime warm-up continuity): "
          f"{len(research_df.index.normalize().unique())} trading day(s) through {VALIDATION_END_DATE.date()}.")

    day_groups = {day: sub for day, sub in research_df.groupby(research_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)  # reused unmodified

    weekly_closes = resample_to_weekly_closes(ref_closes)  # reused unmodified
    weekly_returns = compute_weekly_log_returns(weekly_closes)  # reused unmodified
    all_weeks = sorted(weekly_closes.keys())
    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)  # reused unmodified
    positions = compute_positions(mom_by_week)  # reused unmodified
    pnl_df = compute_weekly_pnl(positions, weekly_closes)  # reused unmodified

    week_to_regime = build_week_to_regime(day_groups, ref_closes)  # reused unmodified, exp-053

    # NEW: which weeks are genuinely new -- first trading day strictly after
    # DISCOVERY_END_DATE, i.e. never scored by exp-047 or exp-053.
    day_to_week = {}
    for day in sorted(day_groups.keys()):
        iso_year, iso_week, _ = day.isocalendar()
        day_to_week.setdefault((iso_year, iso_week), []).append(day)
    discovery_end_date = DISCOVERY_END_DATE.date()
    validation_weeks = {
        wk for wk, days in day_to_week.items() if sorted(days)[0] > discovery_end_date
    }

    def regime_of_row(date_str: str):
        year_s, week_s = date_str.split("-W")
        return week_to_regime.get((int(year_s), int(week_s)))

    def is_validation_row(date_str: str) -> bool:
        year_s, week_s = date_str.split("-W")
        return (int(year_s), int(week_s)) in validation_weeks

    pnl_df["regime"] = pnl_df["date"].apply(regime_of_row)
    pnl_df["is_validation"] = pnl_df["date"].apply(is_validation_row)

    validation_df = pnl_df[pnl_df["is_validation"]].reset_index(drop=True)
    print(f"\nTotal Validation-slice weeks with a computed weekly P&L: {len(validation_df)}")

    print(f"\n{'=' * 78}")
    print("BACKGROUND (not the test): exp-047's original signal, unfiltered, on Validation")
    print(f"{'=' * 78}")
    background = analyze_split(validation_df, "Validation slice, ALL regimes (context only)")

    print(f"\n{'=' * 78}")
    print("PRIMARY TEST (pre-registered): low-vol-regime weeks only, Validation slice")
    print(f"{'=' * 78}")
    low_vol_validation = validation_df[validation_df["regime"] == "low"].reset_index(drop=True)
    primary = analyze_split(low_vol_validation, f"Validation slice, LOW-vol regime only (n={len(low_vol_validation)})")

    passed = (
        isinstance(primary, dict)
        and not primary.get("skipped")
        and primary.get("statistically_credible")
        and primary.get("economically_meaningful")
    )

    print(f"\n{'=' * 78}")
    if passed:
        verdict = ("PASS. The low-vol-regime trend signal clears the promotion bar on the "
                    "Validation slice -- genuinely new data, pre-registered hypothesis, one "
                    "single test. Logged as VALIDATION CANDIDATE. Still NOT authorized for "
                    "live trading -- next step per the project's ladder would be a "
                    "HOLDOUT GEN2 test, budgeted and requested separately, not run casually.")
    else:
        verdict = ("FAIL. The low-vol-regime signal does not clear the bar on fresh "
                    "Validation-slice data. exp-053's exploratory finding does not replicate "
                    "out of sample -- treated as noise from re-mining Discovery data, not a "
                    "real effect. This line of inquiry is closed: no retuning of the "
                    "volatility threshold or lookback window on this result.")
    print(f"Verdict: {verdict}")

    out = {
        "background_all_regimes_validation": background,
        "primary_low_vol_validation": primary,
        "passed": passed,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_nq_trend_low_vol_prospective_validation_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
