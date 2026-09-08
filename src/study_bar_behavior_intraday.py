"""
study_bar_behavior_intraday.py
=================================

exp-094 through exp-099 -- frozen spec: research/studies/bar-behavior-intraday-batch-spec.md.
Re-runs all 6 daily-bar directional mechanisms from batches 1+2
(rejection wick x2, failed breakout, engulfing x2, three-bar sequence)
at 60-minute RTH bar resolution instead of daily -- testing whether the
DAILY timeframe itself, not the pattern ideas, was why nothing survived.

STEP 1 ONLY. Search batch ID: batch-2026-09-08-bar-behavior-intraday.

HOW TO RUN:
    python3 src/study_bar_behavior_intraday.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

WICK_TO_BODY_RATIO = 2.0
LARGE_RANGE_MULTIPLE = 1.5
RANGE_LOOKBACK_BARS = 20
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
SEARCH_BATCH_ID = "batch-2026-09-08-bar-behavior-intraday"
MIN_PROSPECTIVE_N = 40


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


def build_60min_bars(df: pd.DataFrame) -> pd.DataFrame:
    """60-minute RTH bars (09:30-16:00 ET), one row per bar, sequential
    within each day (no cross-day bars). Last bar of the day is a
    partial 30-min bar (15:30-16:00) kept as its own row."""
    session = df.between_time("09:30", "16:00").copy()
    rows = []
    for day, day_df in session.groupby(session.index.date):
        tz = day_df.index.tz
        bar_start = pd.Timestamp(day, tz=tz).replace(hour=9, minute=30)
        day_end = pd.Timestamp(day, tz=tz).replace(hour=16, minute=0)
        while bar_start < day_end:
            bar_end = min(bar_start + pd.Timedelta(minutes=60), day_end)
            bar = day_df[(day_df.index >= bar_start) & (day_df.index < bar_end)]
            if not bar.empty:
                rows.append({
                    "bar_start": bar_start, "date": day,
                    "Open": float(bar["Open"].iloc[0]), "High": float(bar["High"].max()),
                    "Low": float(bar["Low"].min()), "Close": float(bar["Close"].iloc[-1]),
                })
            bar_start = bar_end
    out = pd.DataFrame(rows).set_index("bar_start").sort_index()
    out["range"] = out["High"] - out["Low"]
    out["body"] = (out["Close"] - out["Open"]).abs()
    out["upper_wick"] = out["High"] - out[["Open", "Close"]].max(axis=1)
    out["lower_wick"] = out[["Open", "Close"]].min(axis=1) - out["Low"]
    out["log_return"] = np.log(out["Close"] / out["Close"].shift(1))
    out["trailing_avg_range"] = out["range"].rolling(RANGE_LOOKBACK_BARS, min_periods=RANGE_LOOKBACK_BARS).mean().shift(1)
    return out


def analyze_condition(condition_returns, direction):
    n = len(condition_returns)
    if n < 2:
        return {"n": n, "statistically_credible": False}
    arr = np.array(condition_returns, dtype=float)
    signed = arr * direction
    ci_low, ci_high = bootstrap_mean_ci(signed)
    credible = ci_low > 0
    return {
        "n": n, "mean_signed_to_prediction": float(signed.mean()),
        "ci_90_signed_to_prediction": (ci_low, ci_high), "statistically_credible": bool(credible),
    }


def main():
    print("=" * 78)
    print("EXP-094 to 099: BAR-LEVEL BEHAVIOR, INTRADAY (60-MIN) RESOLUTION")
    print("=" * 78)
    print("\nFrozen spec: research/studies/bar-behavior-intraday-batch-spec.md\n")

    df, is_synthetic = load_price_data(context="study_bar_behavior_intraday.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    bars = build_60min_bars(discovery)
    print(f"60-min bars built: {len(bars)}")

    bars_sorted = bars.index.tolist()

    rejection_bear, rejection_bull, failed_bo = [], [], []
    bull_engulf, bear_engulf, three_bar = [], [], []

    for i in range(2, len(bars_sorted) - 1):
        t = bars_sorted[i]
        t1 = bars_sorted[i - 1]
        t2 = bars_sorted[i - 2]
        nxt = bars_sorted[i + 1]
        row, prior, prior2 = bars.loc[t], bars.loc[t1], bars.loc[t2]
        next_ret = bars.loc[nxt, "log_return"]
        if pd.isna(next_ret) or row["body"] == 0:
            continue

        # exp-094/095: rejection wick vs prior BAR's high/low
        if row["upper_wick"] >= WICK_TO_BODY_RATIO * row["body"] and row["High"] >= prior["High"]:
            rejection_bear.append(next_ret)
        if row["lower_wick"] >= WICK_TO_BODY_RATIO * row["body"] and row["Low"] <= prior["Low"]:
            rejection_bull.append(next_ret)

        # exp-097/098: engulfing (t engulfs t-1's body, opposite colors)
        t_up, t_down = row["Close"] > row["Open"], row["Close"] < row["Open"]
        t1_up, t1_down = prior["Close"] > prior["Open"], prior["Close"] < prior["Open"]
        t_hi, t_lo = max(row["Open"], row["Close"]), min(row["Open"], row["Close"])
        t1_hi, t1_lo = max(prior["Open"], prior["Close"]), min(prior["Open"], prior["Close"])
        engulfs = (t_hi >= t1_hi) and (t_lo <= t1_lo) and (t_hi > t_lo)
        if engulfs and t1_down and t_up:
            bull_engulf.append(next_ret)
        if engulfs and t1_up and t_down:
            bear_engulf.append(next_ret)

        # exp-099: three consecutive same-direction bars
        t2_up, t2_down = prior2["Close"] > prior2["Open"], prior2["Close"] < prior2["Open"]
        if t2_up and t1_up and t_up:
            three_bar.append(next_ret * 1)
        elif t2_down and t1_down and t_down:
            three_bar.append(next_ret * -1)

        # exp-096: failed breakout -- large-range bar T, opposite bar T+1... needs T+2, handled separately below

    # exp-096 needs t, t+1, t+2 -- separate pass
    for i in range(len(bars_sorted) - 2):
        t, t1, t2 = bars_sorted[i], bars_sorted[i + 1], bars_sorted[i + 2]
        row_t, row_t1 = bars.loc[t], bars.loc[t1]
        avg_range = row_t["trailing_avg_range"]
        if pd.isna(avg_range) or avg_range <= 0 or row_t["range"] < LARGE_RANGE_MULTIPLE * avg_range:
            continue
        t_dir = 1 if row_t["Close"] > row_t["Open"] else (-1 if row_t["Close"] < row_t["Open"] else 0)
        t1_dir = 1 if row_t1["Close"] > row_t1["Open"] else (-1 if row_t1["Close"] < row_t1["Open"] else 0)
        if t_dir == 0 or t1_dir == 0 or t1_dir == t_dir:
            continue
        t2_ret = bars.loc[t2, "log_return"]
        if pd.isna(t2_ret):
            continue
        failed_bo.append(t2_ret * t1_dir)

    results = {
        "exp094_bearish_rejection": analyze_condition(rejection_bear, direction=-1),
        "exp095_bullish_rejection": analyze_condition(rejection_bull, direction=1),
        "exp096_failed_breakout": analyze_condition(failed_bo, direction=1),
        "exp097_bullish_engulfing": analyze_condition(bull_engulf, direction=1),
        "exp098_bearish_engulfing": analyze_condition(bear_engulf, direction=-1),
        "exp099_three_bar_sequence": analyze_condition(three_bar, direction=1),
    }

    verdicts = {}
    for key, r in results.items():
        n = r.get("n", 0)
        if n == 0:
            verdicts[key] = "NO_DATA"
        elif r["statistically_credible"]:
            verdicts[key] = "STEP_1_PASS" if n >= MIN_PROSPECTIVE_N else "STEP_1_PASS_TOO_THIN_FOR_PROSPECTIVE"
        else:
            verdicts[key] = "STEP_1_FAIL"

    print()
    for key, r in results.items():
        print(f"{key}: {r}")
    print()
    for key, v in verdicts.items():
        print(f"  {key}: {v}")

    out = {"search_batch_id": SEARCH_BATCH_ID, "results": results, "verdicts": verdicts}
    out_path = DATA_DIR / "study_bar_behavior_intraday_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
