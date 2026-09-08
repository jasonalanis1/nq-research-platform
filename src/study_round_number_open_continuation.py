"""
study_round_number_open_continuation.py
=========================================

H86 / exp-115 -- frozen spec: research/studies/round-number-open-continuation-h86-spec.md.
Parent finding: OBS-FINDING-005 (round-number touch, normal regime,
open bucket -- continuation, not fade). First continuation-style
candidate tried in this project.

REUSED, UNMODIFIED: TARGET_R_MULTIPLE (detect_level_sweep.py),
backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS,
volatility_conditioning.build_conditioning_frame.

HOW TO RUN:
    python3 src/study_round_number_open_continuation.py
"""

import json
from pathlib import Path

import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_level_sweep import TARGET_R_MULTIPLE
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from study_pre_move_behavior_batch1 import analyze_r_multiples, MIN_PROSPECTIVE_N
from volatility_conditioning import build_conditioning_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-observatory-hyp-005-h86"
RANGE_LOOKBACK_BARS = 20
BUFFER_MULT = 1.5
ROUND_INCREMENT = 50.0
MOMENTUM_LOOKBACK = 5


def nearest_round_level(price):
    return round(price / ROUND_INCREMENT) * ROUND_INCREMENT


def simulate_signal(day_df, sig):
    sig_series = pd.Series(sig)
    outcome = simulate_trade(day_df, sig_series, "signal_time")
    risk_points = abs(sig["entry"] - sig["stop"])
    if risk_points <= 0:
        return None
    if sig["direction"] == "long":
        pnl_gross = outcome["exit_price"] - sig["entry"]
    else:
        pnl_gross = sig["entry"] - outcome["exit_price"]
    is_resolved = not outcome["exit_reason"].startswith("unresolved")
    pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
    return pnl_net / risk_points


def main():
    print("=" * 78)
    print("H86/EXP-115: ROUND-NUMBER OPEN CONTINUATION (Observatory candidate #5)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/round-number-open-continuation-h86-spec.md\n")

    df, is_synthetic = load_price_data(context="study_round_number_open_continuation.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    cond = build_conditioning_frame(discovery)
    normal_days = set(cond.index[~(cond["prior_day_narrow"].astype(bool) | cond["prior_day_wide"].astype(bool))])
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days: {len(days_sorted)}, normal-regime days: {len(normal_days)}")

    long_r, short_r = [], []

    for day in days_sorted:
        if day not in normal_days:
            continue
        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if len(rth) < RANGE_LOOKBACK_BARS + MOMENTUM_LOOKBACK + 5:
            continue

        high = rth["High"].values
        low = rth["Low"].values
        close = rth["Close"].values
        times = rth.index
        n = len(rth)
        ranges = high - low
        window_end = times[0].replace(hour=10, minute=30)

        start_i = max(RANGE_LOOKBACK_BARS, MOMENTUM_LOOKBACK)
        fired = False
        for i in range(start_i, n):
            if fired:
                break
            if times[i] >= window_end:
                break
            rlevel = nearest_round_level(close[i])
            if not (high[i] >= rlevel >= low[i]):
                continue

            momentum = close[i] - close[i - MOMENTUM_LOOKBACK]
            if momentum == 0:
                continue
            avg_range = float(ranges[i - RANGE_LOOKBACK_BARS:i].mean())
            buffer = BUFFER_MULT * avg_range
            entry = float(close[i])

            if momentum > 0:
                stop = float(low[i]) - buffer
                risk = entry - stop
                if risk > 0:
                    target = entry + TARGET_R_MULTIPLE * risk
                    sig = {"signal_time": times[i], "direction": "long", "entry": entry, "stop": stop, "target": target}
                    r = simulate_signal(rth, sig)
                    if r is not None:
                        long_r.append(r)
                    fired = True
            else:
                stop = float(high[i]) + buffer
                risk = stop - entry
                if risk > 0:
                    target = entry - TARGET_R_MULTIPLE * risk
                    sig = {"signal_time": times[i], "direction": "short", "entry": entry, "stop": stop, "target": target}
                    r = simulate_signal(rth, sig)
                    if r is not None:
                        short_r.append(r)
                    fired = True

    print(f"\nLong (up-momentum through round level) signals: {len(long_r)}")
    print(f"Short (down-momentum through round level) signals: {len(short_r)}")

    combined_r = long_r + short_r
    results = {
        "h86_long_momentum_continuation": analyze_r_multiples(long_r),
        "h86_short_momentum_continuation": analyze_r_multiples(short_r),
        "h86_combined": analyze_r_multiples(combined_r),
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
    out_path = DATA_DIR / "study_round_number_open_continuation_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
