"""
study_momentum_continuation_prospective.py
================================================

exp-069 -- prospective (Validation-slice) test of the momentum-
continuation effect disclosed in exp-066/068's batch (see
research/studies/momentum-continuation-prospective-spec.md for the
full rationale on why this runs on Validation, not Discovery).

STEP 1 ONLY (statistical, no costs). Reuses the exact daily-bar
construction from study_bar_behavior_batch1.py unmodified.

HOW TO RUN:
    python3 src/study_momentum_continuation_prospective.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_validation_data
from study_bar_behavior_batch1 import build_daily_bars, bootstrap_mean_ci, WICK_TO_BODY_RATIO, LARGE_RANGE_MULTIPLE
from study_volatility_regime import compute_daily_log_returns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-momentum-continuation-prospective"


def analyze_condition(condition_returns, direction=1):
    n = len(condition_returns)
    if n < 2:
        return {"n": n, "mean_signed_to_prediction": float("nan"),
                "ci_90_signed_to_prediction": (float("nan"), float("nan")),
                "statistically_credible": False}
    arr = np.array(condition_returns, dtype=float) * direction
    mean_signed = float(arr.mean())
    ci_low, ci_high = bootstrap_mean_ci(arr)
    return {
        "n": n,
        "mean_signed_to_prediction": mean_signed,
        "ci_90_signed_to_prediction": (ci_low, ci_high),
        "statistically_credible": bool(ci_low > 0),
    }


def main():
    print("=" * 78)
    print("EXP-069: MOMENTUM-CONTINUATION PROSPECTIVE TEST (Validation slice, Step 1)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/momentum-continuation-prospective-spec.md\n")

    df, is_synthetic = load_price_data(context="study_momentum_continuation_prospective.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    validation = get_validation_data(df)
    daily = build_daily_bars(validation)
    log_returns = compute_daily_log_returns({d: row["Close"] for d, row in daily.iterrows()})
    days_sorted = sorted(daily.index)

    # (a) rejection wick at resistance -> predicted CONTINUATION (positive next-day return)
    cond_a_returns = []
    for i in range(1, len(days_sorted) - 1):
        day = days_sorted[i]
        prior_day = days_sorted[i - 1]
        next_day = days_sorted[i + 1]
        row = daily.loc[day]
        if row["body"] == 0:
            continue
        next_ret = log_returns.get(next_day)
        if next_ret is None:
            continue
        if row["upper_wick"] >= WICK_TO_BODY_RATIO * row["body"] and row["High"] >= daily.loc[prior_day, "High"]:
            cond_a_returns.append(next_ret)  # predicted positive -> direction=1 applied in analyze_condition

    # (b) failed-breakout day -> predicted return toward ORIGINAL (day T) direction
    cond_b_returns = []
    dropped = 0
    for i in range(len(days_sorted) - 2):
        day_t = days_sorted[i]
        day_t1 = days_sorted[i + 1]
        day_t2 = days_sorted[i + 2]
        row_t = daily.loc[day_t]
        row_t1 = daily.loc[day_t1]
        avg_range = row_t["trailing_avg_range"]
        if pd.isna(avg_range) or avg_range <= 0:
            dropped += 1
            continue
        if row_t["range"] < LARGE_RANGE_MULTIPLE * avg_range:
            continue
        t_direction = 1 if row_t["Close"] > row_t["Open"] else (-1 if row_t["Close"] < row_t["Open"] else 0)
        t1_direction = 1 if row_t1["Close"] > row_t1["Open"] else (-1 if row_t1["Close"] < row_t1["Open"] else 0)
        if t_direction == 0 or t1_direction == 0 or t1_direction == t_direction:
            continue
        t2_ret = log_returns.get(day_t2)
        if t2_ret is None:
            dropped += 1
            continue
        # predicted direction = t_direction (mirrors exp-068's original spec, reversed)
        cond_b_returns.append(t2_ret * t_direction)

    results = {
        "cond_a_rejection_wick_continuation": analyze_condition(cond_a_returns, direction=1),
        "cond_b_failed_breakout_original_direction": analyze_condition(cond_b_returns, direction=1),
        "cond_b_dropped_instances": dropped,
    }

    print(f"\n(a) Rejection wick continuation, n={results['cond_a_rejection_wick_continuation']['n']}: "
          f"{results['cond_a_rejection_wick_continuation']}")
    print(f"\n(b) Failed-breakout original-direction, n={results['cond_b_failed_breakout_original_direction']['n']}, "
          f"dropped={dropped}: {results['cond_b_failed_breakout_original_direction']}")

    verdicts = {}
    for key in ["cond_a_rejection_wick_continuation", "cond_b_failed_breakout_original_direction"]:
        r = results[key]
        if r["n"] < 2:
            verdicts[key] = "INSUFFICIENT_DATA"
        elif r["statistically_credible"]:
            verdicts[key] = "PROSPECTIVE_PASS"
        else:
            verdicts[key] = "PROSPECTIVE_FAIL"
    results["verdicts"] = verdicts

    print(f"\n{'=' * 78}")
    print(f"Verdicts: {verdicts}")

    out_path = DATA_DIR / "study_momentum_continuation_prospective_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")
    print(f"search_batch_id for ledger logging: {SEARCH_BATCH_ID}")


if __name__ == "__main__":
    main()
