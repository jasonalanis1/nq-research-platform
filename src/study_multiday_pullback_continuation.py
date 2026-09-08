"""
study_multiday_pullback_continuation.py
=========================================

exp-108 -- frozen spec: research/studies/multiday-pullback-continuation-spec.md.
A genuinely different structure from every same-day reactive trigger
tested today (exp-100 to 107, all closed, gross edge ~0): a multi-day
SWING setup, held for days with its own stop/target/timeout, not judged
on a single day's return.

REUSED, UNMODIFIED: build_daily_bars (study_bar_behavior_batch1.py),
TARGET_R_MULTIPLE (detect_level_sweep.py), ROUND_TRIP_COST_POINTS
(backtest.py).

HOW TO RUN:
    python3 src/study_multiday_pullback_continuation.py
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
from study_pre_move_behavior_batch1 import analyze_r_multiples

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-multiday-pullback"

TREND_MA = 50
PULLBACK_MA = 20
ATR_WINDOW = 14
MAX_HOLD_DAYS = 20


def compute_atr(daily):
    high, low, close = daily["High"], daily["Low"], daily["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean()


def main():
    print("=" * 78)
    print("EXP-108: MULTI-DAY 20-MA PULLBACK CONTINUATION")
    print("=" * 78)
    print("\nFrozen spec: research/studies/multiday-pullback-continuation-spec.md\n")

    df, is_synthetic = load_price_data(context="study_multiday_pullback_continuation.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    daily = build_daily_bars(discovery)
    daily["sma50"] = daily["Close"].rolling(TREND_MA, min_periods=TREND_MA).mean()
    daily["sma20"] = daily["Close"].rolling(PULLBACK_MA, min_periods=PULLBACK_MA).mean()
    daily["atr14"] = compute_atr(daily)
    print(f"Discovery daily bars: {len(daily)}")

    days = daily.index.tolist()
    n_days = len(days)

    trend = [None] * n_days  # "up", "down", or None
    for i in range(10, n_days):
        row = daily.iloc[i]
        row10 = daily.iloc[i - 10]
        if pd.isna(row["sma50"]) or pd.isna(row10["sma50"]):
            continue
        if row["Close"] > row["sma50"] and row["sma50"] > row10["sma50"]:
            trend[i] = "up"
        elif row["Close"] < row["sma50"] and row["sma50"] < row10["sma50"]:
            trend[i] = "down"

    r_multiples = []
    n_signals = 0
    last_trend_at_signal = None

    i = TREND_MA
    while i < n_days - 1:
        cur_trend = trend[i]
        row = daily.iloc[i]
        prev = daily.iloc[i - 1]

        if cur_trend is None or pd.isna(row["sma20"]) or pd.isna(prev["sma20"]) or pd.isna(row["atr14"]) or row["atr14"] <= 0:
            i += 1
            continue

        # only first re-cross per trend segment
        if cur_trend == last_trend_at_signal:
            i += 1
            continue

        signal_fired = False
        direction = None
        if cur_trend == "up" and prev["Close"] < prev["sma20"] and row["Close"] > row["sma20"]:
            direction = "long"
            signal_fired = True
        elif cur_trend == "down" and prev["Close"] > prev["sma20"] and row["Close"] < row["sma20"]:
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
        exit_bars_held = 0
        for j in range(entry_idx, min(entry_idx + MAX_HOLD_DAYS, n_days)):
            bar = daily.iloc[j]
            exit_bars_held = j - entry_idx + 1
            if direction == "long":
                stop_hit = bar["Low"] <= stop
                target_hit = bar["High"] >= target
            else:
                stop_hit = bar["High"] >= stop
                target_hit = bar["Low"] <= target
            if stop_hit and target_hit:
                exit_price = stop  # stop-priority tie-break, conservative
                break
            if stop_hit:
                exit_price = stop
                break
            if target_hit:
                exit_price = target
                break
        if exit_price is None:
            timeout_idx = min(entry_idx + MAX_HOLD_DAYS - 1, n_days - 1)
            exit_price = float(daily.iloc[timeout_idx]["Close"])

        if direction == "long":
            pnl_gross = exit_price - entry_price
        else:
            pnl_gross = entry_price - exit_price
        pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS
        r_multiple = pnl_net / risk

        r_multiples.append(r_multiple)
        n_signals += 1
        last_trend_at_signal = cur_trend
        i = entry_idx  # avoid re-signaling on the entry day itself

    print(f"\nexp-108 signals: {n_signals}")
    result = analyze_r_multiples(r_multiples)
    print(f"exp108_multiday_pullback_continuation: {result}")

    n = result.get("n", 0)
    if n == 0:
        verdict = "NO_DATA"
    elif result["statistically_credible"] and result["economically_meaningful"]:
        verdict = "STEP_1+2_PASS" if n >= 40 else "PASS_TOO_THIN_FOR_PROSPECTIVE"
    else:
        verdict = "STEP_1+2_FAIL"
    print(f"  exp108_multiday_pullback_continuation: {verdict}")

    out = {"search_batch_id": SEARCH_BATCH_ID, "n_signals": n_signals, "result": result, "verdict": verdict}
    out_path = DATA_DIR / "study_multiday_pullback_continuation_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
