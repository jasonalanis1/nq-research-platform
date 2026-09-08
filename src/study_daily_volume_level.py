"""
study_daily_volume_level.py
================================

exp-071 -- frozen spec: research/studies/daily-volume-level-spec.md.
Tests whether Day T's total traded volume, relative to its own trailing
20-day average, says anything about Day T+1's return. Distinct from
exp-030 (volume-confirmed IB breakout, an intraday breakout-bar filter
on an already-rejected strategy) -- this is a standalone, whole-day,
daily-resolution test, the same shape as the VXN/ZN/6E/CL Step-1 tests.

STEP 1 ONLY (statistical, no costs). No predicted sign pinned in
advance -- reports whichever direction the data shows, honestly (see
frozen spec's Motivation section for why, informed by the bar-behavior
batch's own lesson).

HOW TO RUN:
    python3 src/study_daily_volume_level.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_overnight_gap import get_reference_close
from study_volatility_regime import compute_daily_log_returns
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VOLUME_LOOKBACK_DAYS = 20  # matches this project's standard vol-lookback convention


def build_daily_volume(df: pd.DataFrame) -> pd.DataFrame:
    """One row per calendar day: Close (4pm ET reference close, reused
    unmodified) and total_volume (sum of 1-min Volume that calendar
    day). Days with no usable reference close are dropped, same
    convention as every other daily-resolution study."""
    tz = df.index.tz
    rows = []
    for day, day_df in df.groupby(df.index.date):
        ref_close = get_reference_close(day_df, day, tz)
        if ref_close is None or ref_close <= 0:
            continue
        rows.append({"date": day, "Close": ref_close, "total_volume": float(day_df["Volume"].sum())})
    out = pd.DataFrame(rows).set_index("date").sort_index()
    out["trailing_avg_volume"] = out["total_volume"].rolling(
        VOLUME_LOOKBACK_DAYS, min_periods=VOLUME_LOOKBACK_DAYS
    ).mean().shift(1)
    out["volume_ratio"] = out["total_volume"] / out["trailing_avg_volume"]
    return out


def main():
    print("=" * 78)
    print("EXP-071: DAILY VOLUME LEVEL AS A NEXT-DAY NQ SIGNAL (Step 1 only)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/daily-volume-level-spec.md\n")

    df, is_synthetic = load_price_data(context="study_daily_volume_level.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    daily = build_daily_volume(discovery)
    log_returns = compute_daily_log_returns({d: row["Close"] for d, row in daily.iterrows()})

    valid = daily.dropna(subset=["volume_ratio"]).copy()
    valid["tercile"] = pd.qcut(valid["volume_ratio"], 3, labels=["low", "mid", "high"])

    days_sorted = sorted(daily.index)
    day_to_idx = {d: i for i, d in enumerate(days_sorted)}

    high_returns = []
    low_returns = []
    mid_returns = []
    for day in valid.index:
        idx = day_to_idx.get(day)
        if idx is None or idx + 1 >= len(days_sorted):
            continue
        next_day = days_sorted[idx + 1]
        next_ret = log_returns.get(next_day)
        if next_ret is None:
            continue
        tercile = valid.loc[day, "tercile"]
        if tercile == "high":
            high_returns.append(next_ret)
        elif tercile == "low":
            low_returns.append(next_ret)
        else:
            mid_returns.append(next_ret)

    print(f"Days in HIGH volume tercile: n={len(high_returns)}")
    print(f"Days in LOW volume tercile:  n={len(low_returns)}")
    print(f"Days in MID volume tercile:  n={len(mid_returns)} (descriptive only)")

    mean_high = sum(high_returns) / len(high_returns) if high_returns else float("nan")
    mean_low = sum(low_returns) / len(low_returns) if low_returns else float("nan")
    mean_mid = sum(mid_returns) / len(mid_returns) if mid_returns else float("nan")
    print(f"\nMean next-day return after HIGH volume: {mean_high:.6f}")
    print(f"Mean next-day return after LOW volume:  {mean_low:.6f}")
    print(f"Mean next-day return after MID volume:  {mean_mid:.6f} (descriptive)")

    ci_low, ci_high = bootstrap_mean_diff_ci(high_returns, low_returns)
    diff = mean_high - mean_low
    statistically_credible = (ci_low > 0) or (ci_high < 0)
    direction = "HIGH volume -> higher next-day return" if (statistically_credible and diff > 0) else (
        "HIGH volume -> lower next-day return" if statistically_credible else "no credible direction"
    )
    print(f"\nDifference (HIGH - LOW): {diff:.6f}")
    print(f"90% bootstrap CI on the difference: ({ci_low:.6f}, {ci_high:.6f})")
    print(f"Statistically credible (CI entirely off zero): {statistically_credible}")
    print(f"Direction: {direction}")

    print(f"\n{'=' * 78}")
    if statistically_credible:
        verdict = (f"STEP 1 PASS ({direction}). Logged as PROMISING (Step 1 only -- no costed "
                   "rule built, no trades). Next step: design one concrete, pre-registered, "
                   "costed trading rule and test it prospectively on the Validation slice.")
    else:
        verdict = ("STEP 1 FAIL. Daily volume level alone does not show a statistically "
                   "credible difference in next-day NQ returns on the Discovery slice. "
                   "Logged as REJECTED. No retuning -- this line is closed.")
    print(f"Verdict: {verdict}")

    out = {
        "n_high": len(high_returns), "n_low": len(low_returns), "n_mid": len(mid_returns),
        "mean_after_high": mean_high, "mean_after_low": mean_low, "mean_after_mid_descriptive": mean_mid,
        "diff": diff, "ci_90": [ci_low, ci_high],
        "statistically_credible": statistically_credible, "direction": direction, "verdict": verdict,
    }
    out_path = DATA_DIR / "study_daily_volume_level_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
