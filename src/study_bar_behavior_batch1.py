"""
study_bar_behavior_batch1.py
=================================

exp-066/067/068 -- first batch under the 2026-09-08 mission redirection
(market behavior -> condition -> strategy, at the level of individual
daily bars). Frozen spec: research/studies/bar-behavior-batch1-spec.md
-- read that file for the full rationale. This script implements
exactly the 3 pre-registered behaviors there, nothing else.

STEP 1 ONLY (statistical, no costs) -- same gate as exp-059 through
exp-065. All 3 logged under one shared search_batch_id so the ledger
discloses this was a 3-way simultaneous test, not 3 isolated ones (per
the Path-to-Profitability Advisor's multiple-testing guardrail on this
redirection).

REUSED, UNMODIFIED:
  - load_price_data, get_discovery_data (data_loader.py, data_split.py)
  - get_reference_close (study_overnight_gap.py)
  - compute_daily_log_returns (study_volatility_regime.py)
  - bootstrap_mean_ci-style CI (written fresh here, same nonparametric
    resample-and-recompute convention as study_nq_trend_following.py's
    bootstrap_mean_ci -- single-sample mean CI, not the two-sample
    diff-CI used by the up/down-style studies, since each of these 3
    conditions is tested as one signed group against zero, not two
    groups against each other)

HOW TO RUN:
    python3 src/study_bar_behavior_batch1.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_overnight_gap import get_reference_close
from study_volatility_regime import compute_daily_log_returns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

WICK_TO_BODY_RATIO = 2.0        # frozen -- structural, not tuned
LARGE_RANGE_MULTIPLE = 1.5      # frozen -- structural, not tuned
RANGE_LOOKBACK_DAYS = 20        # matches this project's standard vol-lookback convention
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
SEARCH_BATCH_ID = "batch-2026-09-08-bar-behavior-1"


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    if n < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    idx_pool = np.arange(n)
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=n, replace=True)
        means[i] = arr[idx].mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def build_daily_bars(df: pd.DataFrame) -> pd.DataFrame:
    """One row per calendar day: Open (first bar's Open that day), High
    (day's max High), Low (day's min Low), Close (4pm ET reference
    close, reused unmodified from study_overnight_gap.py -- consistent
    with every other daily-resolution study in this project). Days with
    no usable reference close are dropped (same convention as
    compute_daily_ref_closes elsewhere)."""
    tz = df.index.tz
    rows = []
    for day, day_df in df.groupby(df.index.date):
        ref_close = get_reference_close(day_df, day, tz)
        if ref_close is None or ref_close <= 0:
            continue
        rows.append({
            "date": day,
            "Open": float(day_df.iloc[0]["Open"]),
            "High": float(day_df["High"].max()),
            "Low": float(day_df["Low"].min()),
            "Close": ref_close,
        })
    out = pd.DataFrame(rows).set_index("date").sort_index()
    out["range"] = out["High"] - out["Low"]
    out["body"] = (out["Close"] - out["Open"]).abs()
    out["upper_wick"] = out["High"] - out[["Open", "Close"]].max(axis=1)
    out["lower_wick"] = out[["Open", "Close"]].min(axis=1) - out["Low"]
    out["trailing_avg_range"] = out["range"].rolling(RANGE_LOOKBACK_DAYS, min_periods=RANGE_LOOKBACK_DAYS).mean().shift(1)
    return out


def analyze_condition(label, condition_returns, direction):
    """direction: +1 if predicted direction is positive, -1 if negative.
    Returns dict with mean/CI in RAW terms and in SIGNED (predicted-
    direction) terms."""
    n = len(condition_returns)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": (float("nan"), float("nan")),
                "statistically_credible": False}
    arr = np.array(condition_returns, dtype=float)
    mean_raw = float(arr.mean())
    ci_low_raw, ci_high_raw = bootstrap_mean_ci(arr)
    signed = arr * direction
    mean_signed = float(signed.mean())
    ci_low_signed, ci_high_signed = bootstrap_mean_ci(signed)
    credible = ci_low_signed > 0
    return {
        "n": n,
        "mean_raw": mean_raw,
        "ci_90_raw": (ci_low_raw, ci_high_raw),
        "mean_signed_to_prediction": mean_signed,
        "ci_90_signed_to_prediction": (ci_low_signed, ci_high_signed),
        "statistically_credible": bool(credible),
    }


def main():
    print("=" * 78)
    print("EXP-066/067/068: BAR-LEVEL BEHAVIOR BATCH 1 (Step 1 only)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/bar-behavior-batch1-spec.md\n")

    df, is_synthetic = load_price_data(context="study_bar_behavior_batch1.py")
    if is_synthetic:
        print("ABORT: only synthetic data available -- this study requires real data.")
        return

    discovery = get_discovery_data(df)
    daily = build_daily_bars(discovery)
    log_returns = compute_daily_log_returns({d: row["Close"] for d, row in daily.iterrows()})

    days_sorted = sorted(daily.index)
    day_to_idx = {d: i for i, d in enumerate(days_sorted)}

    # exp-066: bearish rejection at resistance (long upper wick at/above prior day's High)
    exp066_returns = []
    # exp-067: bullish rejection at support (long lower wick at/below prior day's Low)
    exp067_returns = []
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
            exp066_returns.append(next_ret)

        if row["lower_wick"] >= WICK_TO_BODY_RATIO * row["body"] and row["Low"] <= daily.loc[prior_day, "Low"]:
            exp067_returns.append(next_ret)

    # exp-068: failed breakout -- large-range day T, opposite-direction day T+1, measure T+2 signed to the T+1 direction
    exp068_returns = []
    exp068_dropped = 0
    for i in range(len(days_sorted) - 2):
        day_t = days_sorted[i]
        day_t1 = days_sorted[i + 1]
        day_t2 = days_sorted[i + 2]
        row_t = daily.loc[day_t]
        row_t1 = daily.loc[day_t1]
        avg_range = row_t["trailing_avg_range"]
        if pd.isna(avg_range) or avg_range <= 0:
            exp068_dropped += 1
            continue
        if row_t["range"] < LARGE_RANGE_MULTIPLE * avg_range:
            continue  # not a large-range day, not an instance of this pattern at all
        t_direction = 1 if row_t["Close"] > row_t["Open"] else (-1 if row_t["Close"] < row_t["Open"] else 0)
        t1_direction = 1 if row_t1["Close"] > row_t1["Open"] else (-1 if row_t1["Close"] < row_t1["Open"] else 0)
        if t_direction == 0 or t1_direction == 0 or t1_direction == t_direction:
            continue  # not a failed-breakout instance (no follow-through failure)
        t2_ret = log_returns.get(day_t2)
        if t2_ret is None:
            exp068_dropped += 1
            continue
        # predicted direction = t1_direction (the reversal implied by the failed follow-through)
        exp068_returns.append(t2_ret * t1_direction)

    results = {}
    results["exp066_bearish_rejection"] = analyze_condition(
        "exp-066 bearish rejection at resistance", exp066_returns, direction=-1)
    results["exp067_bullish_rejection"] = analyze_condition(
        "exp-067 bullish rejection at support", exp067_returns, direction=1)
    # exp-068's returns are already signed to the predicted direction, so direction=+1 here
    results["exp068_failed_breakout"] = analyze_condition(
        "exp-068 failed breakout continuation", exp068_returns, direction=1)
    results["exp068_dropped_instances"] = exp068_dropped

    print(f"\nexp-066 (bearish rejection, n={results['exp066_bearish_rejection']['n']}): "
          f"{results['exp066_bearish_rejection']}")
    print(f"\nexp-067 (bullish rejection, n={results['exp067_bullish_rejection']['n']}): "
          f"{results['exp067_bullish_rejection']}")
    print(f"\nexp-068 (failed breakout, n={results['exp068_failed_breakout']['n']}, "
          f"dropped={exp068_dropped}): {results['exp068_failed_breakout']}")

    verdicts = {}
    for key in ["exp066_bearish_rejection", "exp067_bullish_rejection", "exp068_failed_breakout"]:
        r = results[key]
        if r["n"] < 2:
            verdicts[key] = "INSUFFICIENT_DATA"
        elif r["statistically_credible"]:
            verdicts[key] = "STEP_1_PASS"
        else:
            verdicts[key] = "STEP_1_FAIL"
    results["verdicts"] = verdicts

    print(f"\n{'=' * 78}")
    print(f"Verdicts: {verdicts}")

    out_path = DATA_DIR / "study_bar_behavior_batch1_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")
    print(f"search_batch_id for ledger logging: {SEARCH_BATCH_ID}")


if __name__ == "__main__":
    main()
