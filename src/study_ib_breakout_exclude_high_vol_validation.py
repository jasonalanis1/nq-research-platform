"""
study_ib_breakout_exclude_high_vol_validation.py
====================================================

exp-058 -- the pre-registered prospective test that exp-057
(hyp-000027, the intraday collective-evidence pilot) said was the
required next step before its one candidate finding could be trusted.

FROZEN HYPOTHESIS (written before this script is run, before any
Validation-slice number is looked at):

    The Initial Balance Breakout signal (exp-028's signal, UNCHANGED)
    clears this project's promotion bar when days classified "high"
    volatility regime (the SAME causal_expanding_tercile-based
    classify_regimes() method already used in exp-053/055/057,
    UNCHANGED) are EXCLUDED, evaluated ONLY on the Validation slice
    (2021-10-04 -> 2024-01-03) -- data this specific signal/filter
    combination has never been tested on before.

WHY THIS LENS, MECHANICALLY CHOSEN (not cherry-picked by eye): of
exp-057's 4 lenses, Initial Balance Breakout had the lowest per-lens
beat-rate in the "volatility_regime = high" bucket (0.4032, furthest
below 0.5 of all 4), so it is the lens exp-057's own data says is most
affected by high-volatility days -- the natural one to carry into a
single concrete test.

CONTINUITY, NOT A COLD RESTART (same discipline as exp-054/056): the
volatility classifier needs trailing history. It is computed
continuously across Discovery + Validation combined (never touching
HOLDOUT_GEN2), exactly as a live system would. Only the FINAL
evaluation rows are restricted to trades whose entry day falls after
DISCOVERY_END_DATE.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes, compute_daily_log_returns,
    compute_trailing_volatility, classify_regimes
    (study_volatility_regime.py)
  - detect_ib_breakout_for_day (detect_ib_breakout.py)
  - simulate_trade, ROUND_TRIP_COST_POINTS (backtest.py)

NEW CODE: only the Validation-slice filter and a small bootstrap
helper for R-multiple per-trade data (this project's existing
analyze_primary() is shaped for weekly points-based P&L, not per-trade
R-multiples, so a matching one is written here instead of forcing an
incompatible shape).

PROMOTION CONSEQUENCE, decided in advance: same as exp-054/056 -- a
clean pass here is logged as VALIDATION CANDIDATE (still not
live-authorized, would need a HOLDOUT GEN2 pass next). A fail closes
this specific filtered-signal line; no retuning of the volatility
threshold on this result.

STATISTICAL BAR (stated before any result is looked at): statistically
credible = 90% bootstrap CI on mean net R-multiple entirely above
zero. Economically meaningful = mean net R-multiple > 0 (costs are
already netted into each trade's R-multiple, so no separate threshold
is layered on top).

HOW TO RUN:
    python3 src/study_ib_breakout_exclude_high_vol_validation.py
"""

import json
import random
from pathlib import Path

from data_loader import load_price_data
from data_split import DISCOVERY_END_DATE, VALIDATION_END_DATE
from study_volatility_regime import (  # reused unmodified
    compute_daily_ref_closes,
    compute_daily_log_returns,
    compute_trailing_volatility,
    classify_regimes,
)
from study_intraday_collective_evidence_pilot import build_ib_breakout_lens  # reused unmodified, exp-057

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 5000


def bootstrap_ci_on_trades(r_multiples: list, n_boot=N_BOOTSTRAP, seed=13) -> tuple:
    if len(r_multiples) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(r_multiples)
    means = []
    for _ in range(n_boot):
        sample = [r_multiples[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo_idx = int(0.05 * n_boot)
    hi_idx = int(0.95 * n_boot) - 1
    return (means[lo_idx], means[hi_idx])


def analyze_split(r_multiples: list, label: str) -> dict:
    print(f"\n{'-' * 78}")
    print(label)
    print(f"{'-' * 78}")
    n = len(r_multiples)
    if n < 10:
        print(f"  n={n} -- too few trades to analyze meaningfully.")
        return {"n": n, "skipped": True}
    mean_r = sum(r_multiples) / n
    ci_low, ci_high = bootstrap_ci_on_trades(r_multiples)
    statistically_credible = ci_low > 0
    economically_meaningful = mean_r > 0
    print(f"  n: {n}")
    print(f"  mean_r_multiple_net: {mean_r:.4f}")
    print(f"  ci_90: ({ci_low:.4f}, {ci_high:.4f})")
    print(f"  Statistically credible: {statistically_credible}   "
          f"Economically meaningful: {economically_meaningful}")
    return {
        "n": n,
        "mean_r_multiple_net": mean_r,
        "ci_90": (ci_low, ci_high),
        "statistically_credible": statistically_credible,
        "economically_meaningful": economically_meaningful,
    }


def main():
    print("=" * 78)
    print("EXP-058: IB BREAKOUT, EXCLUDING HIGH-VOLATILITY DAYS -- PROSPECTIVE VALIDATION")
    print("=" * 78)
    print("\nPre-registered single hypothesis (see this file's docstring), tested on the")
    print("Validation slice only -- data this signal/filter combination has never seen.\n")

    full_df, is_synthetic = load_price_data(context="study_ib_breakout_exclude_high_vol_validation.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    research_df = full_df[full_df.index <= VALIDATION_END_DATE]
    print(f"Discovery+Validation combined (for signal/filter warm-up continuity): "
          f"{len(research_df.index.normalize().unique())} trading day(s) through {VALIDATION_END_DATE.date()}.")

    day_groups = {day: sub for day, sub in research_df.groupby(research_df.index.date)}

    ref_closes = compute_daily_ref_closes(day_groups)  # reused unmodified
    daily_returns = compute_daily_log_returns(ref_closes)  # reused unmodified
    all_days = sorted(day_groups.keys())
    vol_by_day = compute_trailing_volatility(daily_returns, all_days)  # reused unmodified
    volatility_regime = classify_regimes(vol_by_day)  # reused unmodified

    ib_df = build_ib_breakout_lens(day_groups)  # reused unmodified, exp-057
    print(f"\nTotal IB Breakout trades, Discovery+Validation combined: {len(ib_df)}")

    discovery_end_date = DISCOVERY_END_DATE.date()
    ib_df["is_validation"] = ib_df["date"].apply(lambda d: d > discovery_end_date)
    validation_df = ib_df[ib_df["is_validation"]].reset_index(drop=True)
    print(f"Total Validation-slice IB Breakout trades: {len(validation_df)}")

    validation_df["vol_regime"] = validation_df["date"].apply(lambda d: volatility_regime.get(d))

    print(f"\n{'=' * 78}")
    print("BACKGROUND (not the test): IB Breakout, unfiltered, on Validation")
    print(f"{'=' * 78}")
    background = analyze_split(validation_df["r_multiple_net"].tolist(),
                               "Validation slice, ALL trades (context only)")

    print(f"\n{'=' * 78}")
    print("PRIMARY TEST (pre-registered): EXCLUDING high-volatility-regime days")
    print(f"{'=' * 78}")
    filtered_df = validation_df[validation_df["vol_regime"] != "high"]
    primary = analyze_split(filtered_df["r_multiple_net"].tolist(),
                             f"Validation slice, high-vol days excluded (n={len(filtered_df)})")

    passed = (
        isinstance(primary, dict)
        and not primary.get("skipped")
        and primary.get("statistically_credible")
        and primary.get("economically_meaningful")
    )

    print(f"\n{'=' * 78}")
    if passed:
        verdict = ("PASS. Excluding high-volatility days clears the promotion bar on the "
                   "Validation slice -- genuinely new data, pre-registered hypothesis, one "
                   "single test. Logged as VALIDATION CANDIDATE. Still NOT authorized for "
                   "live trading -- next step per the project's ladder would be a "
                   "HOLDOUT GEN2 test, budgeted and requested separately, not run casually.")
    else:
        verdict = ("FAIL. Excluding high-volatility days does not clear the bar on fresh "
                   "Validation-slice data. exp-057's exploratory finding does not replicate "
                   "out of sample -- treated as noise, not a real effect. This line of "
                   "inquiry is closed: no retuning of the volatility threshold on this result.")
    print(f"Verdict: {verdict}")

    out = {
        "background_all_trades_validation": background,
        "primary_exclude_high_vol_validation": primary,
        "passed": passed,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_ib_breakout_exclude_high_vol_validation_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
