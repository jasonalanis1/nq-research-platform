"""
study_multiday_pullback_continuation_v2.py
============================================

exp-109 -- frozen spec: research/studies/multiday-pullback-continuation-v2-spec.md.
Frequency-increased follow-up to exp-108 (hyp-000079, CREDIBLE but n=15,
too thin to trust). Allows repeat signals per trend segment (with a
cooldown) and shortens the trend/pullback windows (30/10 instead of
50/20). Stop/target/timeout unchanged from exp-108.

REUSED, UNMODIFIED: build_daily_bars (study_bar_behavior_batch1.py),
TARGET_R_MULTIPLE (detect_level_sweep.py), ROUND_TRIP_COST_POINTS
(backtest.py), compute_atr, analyze_r_multiples,
(study_multiday_pullback_continuation.py / study_pre_move_behavior_batch1.py).

HOW TO RUN:
    python3 src/study_multiday_pullback_continuation_v2.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_level_sweep import TARGET_R_MULTIPLE
from backtest import ROUND_TRIP_COST_POINTS
from study_bar_behavior_batch1 import build_daily_bars
from study_pre_move_behavior_batch1 import analyze_r_multiples, bootstrap_mean_ci
from study_multiday_pullback_continuation import compute_atr

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-multiday-pullback-v2"

TREND_MA = 30
PULLBACK_MA = 10
ATR_WINDOW = 14
MAX_HOLD_DAYS = 20
MIN_BARS_BETWEEN_SIGNALS = 5


def block_bootstrap_ci(segment_r_lists, n_bootstrap=3000, seed=7):
    """Resample whole trend segments (each a list of that segment's trade
    R-multiples) with replacement, rather than individual trades, to
    check whether within-segment correlation changes the conclusion."""
    rng = np.random.default_rng(seed)
    n_segments = len(segment_r_lists)
    if n_segments < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    idx_pool = np.arange(n_segments)
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=n_segments, replace=True)
        pooled = [r for si in idx for r in segment_r_lists[si]]
        means[i] = np.mean(pooled) if pooled else np.nan
    means = means[~np.isnan(means)]
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def main():
    print("=" * 78)
    print("EXP-109: MULTI-DAY PULLBACK CONTINUATION, FREQUENCY-INCREASED (v2)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/multiday-pullback-continuation-v2-spec.md\n")

    df, is_synthetic = load_price_data(context="study_multiday_pullback_continuation_v2.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    daily = build_daily_bars(discovery)
    daily["sma_trend"] = daily["Close"].rolling(TREND_MA, min_periods=TREND_MA).mean()
    daily["sma_pullback"] = daily["Close"].rolling(PULLBACK_MA, min_periods=PULLBACK_MA).mean()
    daily["atr14"] = compute_atr(daily)
    print(f"Discovery daily bars: {len(daily)}")

    days = daily.index.tolist()
    n_days = len(days)

    trend = [None] * n_days
    for i in range(10, n_days):
        row = daily.iloc[i]
        row10 = daily.iloc[i - 10]
        if pd.isna(row["sma_trend"]) or pd.isna(row10["sma_trend"]):
            continue
        if row["Close"] > row["sma_trend"] and row["sma_trend"] > row10["sma_trend"]:
            trend[i] = "up"
        elif row["Close"] < row["sma_trend"] and row["sma_trend"] < row10["sma_trend"]:
            trend[i] = "down"

    segment_r = []  # list of lists, one per trend segment
    cur_segment_r = []
    cur_segment_trend = None
    last_signal_idx = -999

    i = TREND_MA
    while i < n_days - 1:
        cur_trend = trend[i]
        row = daily.iloc[i]
        prev = daily.iloc[i - 1]

        if cur_trend != cur_segment_trend:
            if cur_segment_r:
                segment_r.append(cur_segment_r)
            cur_segment_r = []
            cur_segment_trend = cur_trend
            last_signal_idx = -999

        if cur_trend is None or pd.isna(row["sma_pullback"]) or pd.isna(prev["sma_pullback"]) or pd.isna(row["atr14"]) or row["atr14"] <= 0:
            i += 1
            continue

        if i - last_signal_idx < MIN_BARS_BETWEEN_SIGNALS:
            i += 1
            continue

        signal_fired = False
        direction = None
        if cur_trend == "up" and prev["Close"] < prev["sma_pullback"] and row["Close"] > row["sma_pullback"]:
            direction = "long"
            signal_fired = True
        elif cur_trend == "down" and prev["Close"] > prev["sma_pullback"] and row["Close"] < row["sma_pullback"]:
            direction = "short"
            signal_fired = True

        if not signal_fired:
            i += 1
            continue

        entry_idx = i + 1
        if entry_idx >= n_days:
            break
        entry_price = float(daily.iloc[entry_idx]["Open"])
        risk = 1.5 * float(row["atr14"])
        if risk <= 0:
            i += 1
            continue

        if direction == "long":
            stop = entry_price - risk
            target = entry_price + TARGET_R_MULTIPLE * risk
        else:
            stop = entry_price + risk
            target = entry_price - TARGET_R_MULTIPLE * risk

        exit_price = None
        for j in range(entry_idx, min(entry_idx + MAX_HOLD_DAYS, n_days)):
            bar = daily.iloc[j]
            if direction == "long":
                stop_hit = bar["Low"] <= stop
                target_hit = bar["High"] >= target
            else:
                stop_hit = bar["High"] >= stop
                target_hit = bar["Low"] <= target
            if stop_hit:
                exit_price = stop
                break
            if target_hit:
                exit_price = target
                break
        if exit_price is None:
            timeout_idx = min(entry_idx + MAX_HOLD_DAYS - 1, n_days - 1)
            exit_price = float(daily.iloc[timeout_idx]["Close"])

        pnl_gross = (exit_price - entry_price) if direction == "long" else (entry_price - exit_price)
        pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS
        r_multiple = pnl_net / risk

        cur_segment_r.append(r_multiple)
        last_signal_idx = i
        i = entry_idx

    if cur_segment_r:
        segment_r.append(cur_segment_r)

    all_r = [r for seg in segment_r for r in seg]
    print(f"\nexp-109 signals: {len(all_r)} across {len(segment_r)} trend segments")

    result = analyze_r_multiples(all_r)
    print(f"exp109_multiday_pullback_v2 (standard bootstrap): {result}")

    block_ci = block_bootstrap_ci(segment_r)
    block_credible = block_ci[0] > 0
    print(f"exp109 block-bootstrap-by-segment ci_90: {block_ci}, credible={block_credible}")

    n = result.get("n", 0)
    if n == 0:
        verdict = "NO_DATA"
    elif result["statistically_credible"] and result["economically_meaningful"] and block_credible:
        verdict = "STEP_1+2_PASS_BOTH_BOOTSTRAPS" if n >= 40 else "PASS_TOO_THIN_FOR_PROSPECTIVE"
    elif result["statistically_credible"] and result["economically_meaningful"] and not block_credible:
        verdict = "STANDARD_PASS_BUT_BLOCK_BOOTSTRAP_DISAGREES -- DISQUALIFIED"
    else:
        verdict = "STEP_1+2_FAIL"
    print(f"  exp109_multiday_pullback_v2: {verdict}")

    out = {
        "search_batch_id": SEARCH_BATCH_ID, "n_signals": len(all_r), "n_segments": len(segment_r),
        "result": result, "block_bootstrap_ci_90": block_ci, "block_bootstrap_credible": block_credible,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_multiday_pullback_continuation_v2_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
