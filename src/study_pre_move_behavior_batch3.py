"""
study_pre_move_behavior_batch3.py
=================================

exp-104/105 -- frozen spec: research/studies/pre-move-behavior-batch3-spec.md.
Two more fresh setups: opening signed-volume imbalance (a crude OHLCV
order-flow proxy) and prior-RTH-close rejection (a fixed external
reference level, not a rolling window) -- genuinely different mechanisms
from batch 1/2's volume-vacuum and trend-alignment.

STEP 1 + STEP 2 together. Search batch ID:
batch-2026-09-08-pre-move-behavior-3.

REUSED, UNMODIFIED from study_pre_move_behavior_batch1.py: simulate_signal,
analyze_r_multiples.

HOW TO RUN:
    python3 src/study_pre_move_behavior_batch3.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_level_sweep import TARGET_R_MULTIPLE
from study_pre_move_behavior_batch1 import simulate_signal, analyze_r_multiples, MIN_PROSPECTIVE_N

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-pre-move-behavior-3"

CONFIRM_BARS = 3
RANGE_LOOKBACK_BARS = 20


def detect_volume_imbalance_signal_for_day(day_df):
    """exp-104: opening (09:30-10:00) signed-volume imbalance."""
    tz = day_df.index.tz
    day = day_df.index[0].date()
    open_start = pd.Timestamp(day, tz=tz).replace(hour=9, minute=30)
    open_end = pd.Timestamp(day, tz=tz).replace(hour=10, minute=0)
    opening = day_df[(day_df.index >= open_start) & (day_df.index < open_end)]
    if opening.empty:
        return None

    imbalance = float(np.sign(opening["Close"] - opening["Open"]).mul(opening["Volume"]).sum())
    if imbalance == 0:
        return None

    entry_bars = day_df[day_df.index >= open_end]
    if entry_bars.empty:
        return None
    entry_price = float(entry_bars["Open"].iloc[0])
    w_high, w_low = float(opening["High"].max()), float(opening["Low"].min())

    if imbalance > 0:
        stop = w_low
        risk = entry_price - stop
        if risk <= 0:
            return None
        return {"signal_time": entry_bars.index[0], "direction": "long", "entry": entry_price,
                "stop": stop, "target": entry_price + TARGET_R_MULTIPLE * risk}
    else:
        stop = w_high
        risk = stop - entry_price
        if risk <= 0:
            return None
        return {"signal_time": entry_bars.index[0], "direction": "short", "entry": entry_price,
                "stop": stop, "target": entry_price - TARGET_R_MULTIPLE * risk}


def detect_prior_close_rejection_signal_for_day(day_df, prior_close):
    """exp-105: first touch of prior day's RTH close, 09:30-12:00, rejected
    (price fails to hold beyond it for CONFIRM_BARS) -> fade back toward
    the approach direction."""
    if prior_close is None:
        return None
    tz = day_df.index.tz
    day = day_df.index[0].date()
    watch_end = pd.Timestamp(day, tz=tz).replace(hour=12, minute=0)
    watch = day_df[day_df.index < watch_end]
    if len(watch) < RANGE_LOOKBACK_BARS + CONFIRM_BARS + 2:
        return None

    ranges = (watch["High"] - watch["Low"]).values
    opens, highs, lows, closes = watch["Open"].values, watch["High"].values, watch["Low"].values, watch["Close"].values
    idx = watch.index

    approach_side = None  # "above" or "below" prior_close, based on price before the touch
    for i in range(RANGE_LOOKBACK_BARS, len(watch) - CONFIRM_BARS):
        side_now = "above" if closes[i - 1] > prior_close else ("below" if closes[i - 1] < prior_close else None)
        if side_now is not None:
            approach_side = side_now
        touched = highs[i] >= prior_close >= lows[i]
        if not touched or approach_side is None:
            continue

        confirm = closes[i + 1:i + 1 + CONFIRM_BARS]
        if len(confirm) < CONFIRM_BARS:
            continue
        if approach_side == "above":
            # came from above, touched, rejected = all confirm closes stay above prior_close again
            rejected = all(c > prior_close for c in confirm)
            direction = "long"  # fade back up, continuing the from-above approach direction
        else:
            rejected = all(c < prior_close for c in confirm)
            direction = "short"

        if not rejected:
            continue

        avg_range = float(np.mean(ranges[max(0, i - RANGE_LOOKBACK_BARS):i]))
        buffer = 2 * avg_range
        entry_idx = i + CONFIRM_BARS
        entry_price = float(closes[entry_idx])
        if direction == "long":
            stop = prior_close - buffer
            risk = entry_price - stop
            if risk <= 0:
                continue
            target = entry_price + TARGET_R_MULTIPLE * risk
        else:
            stop = prior_close + buffer
            risk = stop - entry_price
            if risk <= 0:
                continue
            target = entry_price - TARGET_R_MULTIPLE * risk

        return {"signal_time": idx[entry_idx], "direction": direction, "entry": entry_price,
                "stop": stop, "target": target}
    return None


def main():
    print("=" * 78)
    print("EXP-104/105: OPENING VOLUME IMBALANCE / PRIOR-CLOSE REJECTION")
    print("=" * 78)
    print("\nFrozen spec: research/studies/pre-move-behavior-batch3-spec.md\n")

    df, is_synthetic = load_price_data(context="study_pre_move_behavior_batch3.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    session = discovery.between_time("09:30", "16:00")
    day_groups = {d: g for d, g in session.groupby(session.index.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery RTH days: {len(day_groups)}")

    prior_close_map = {}
    prev_close = None
    for day in days_sorted:
        prior_close_map[day] = prev_close
        prev_close = float(day_groups[day]["Close"].iloc[-1])

    imbalance_r = []
    rejection_r = []

    for day in days_sorted:
        day_df = day_groups[day]

        sig1 = detect_volume_imbalance_signal_for_day(day_df)
        if sig1 is not None:
            r = simulate_signal(day_df, sig1)
            if r is not None:
                imbalance_r.append(r)

        sig2 = detect_prior_close_rejection_signal_for_day(day_df, prior_close_map[day])
        if sig2 is not None:
            r = simulate_signal(day_df, sig2)
            if r is not None:
                rejection_r.append(r)

    print(f"\nexp-104 opening volume imbalance: {len(imbalance_r)} signals")
    print(f"exp-105 prior-close rejection: {len(rejection_r)} signals")

    results = {
        "exp104_opening_volume_imbalance": analyze_r_multiples(imbalance_r),
        "exp105_prior_close_rejection": analyze_r_multiples(rejection_r),
    }

    verdicts = {}
    for key, r in results.items():
        n = r.get("n", 0)
        if n == 0:
            verdicts[key] = "NO_DATA"
        elif r["statistically_credible"] and r["economically_meaningful"]:
            verdicts[key] = "STEP_1+2_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN_FOR_PROSPECTIVE"
        else:
            verdicts[key] = "STEP_1+2_FAIL"

    print()
    for key, r in results.items():
        print(f"{key}: {r}")
    print()
    for key, v in verdicts.items():
        print(f"  {key}: {v}")

    out = {"search_batch_id": SEARCH_BATCH_ID, "results": results, "verdicts": verdicts}
    out_path = DATA_DIR / "study_pre_move_behavior_batch3_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
