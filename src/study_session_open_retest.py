"""
study_session_open_retest.py
==============================

H88 / exp-117 -- frozen spec: research/studies/session-open-retest-h88-spec.md.
Parent finding: OBS-FINDING-007 (session-open retest, mid-morning,
normal regime). Second test of the ATR-scaled-stop convention adopted
after H87.

REUSED, UNMODIFIED: TARGET_R_MULTIPLE (detect_level_sweep.py),
backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS,
build_daily_bars, volatility_conditioning.build_conditioning_frame.

HOW TO RUN:
    python3 src/study_session_open_retest.py
"""

import json
from pathlib import Path

import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_level_sweep import TARGET_R_MULTIPLE
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from study_bar_behavior_batch1 import build_daily_bars
from study_pre_move_behavior_batch1 import analyze_r_multiples, MIN_PROSPECTIVE_N
from volatility_conditioning import build_conditioning_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-observatory-hyp-007-h88"
RANGE_LOOKBACK_BARS = 20
MOMENTUM_LOOKBACK = 5
OPEN_RETEST_MULT = 1.0
ATR_WINDOW = 14


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
    print("H88/EXP-117: SESSION-OPEN RETEST (Observatory candidate #7, ATR stop)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/session-open-retest-h88-spec.md\n")

    df, is_synthetic = load_price_data(context="study_session_open_retest.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()
    cond = build_conditioning_frame(discovery)
    normal_days = set(cond.index[~(cond["prior_day_narrow"].astype(bool) | cond["prior_day_wide"].astype(bool))])
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days: {len(days_sorted)}, normal-regime days: {len(normal_days)}")

    long_r, short_r = [], []

    for day_num, day in enumerate(days_sorted):
        if day_num == 0 or day not in normal_days:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index:
            continue
        atr = daily_bars.loc[prior_day, "atr14"]
        if pd.isna(atr) or atr <= 0:
            continue
        atr = float(atr)

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
        open_price = float(close[0])

        window_start = times[0].replace(hour=10, minute=30)
        window_end = times[0].replace(hour=12, minute=0)

        start_i = max(RANGE_LOOKBACK_BARS, MOMENTUM_LOOKBACK, 20)
        fired = False
        for i in range(start_i, n):
            if fired:
                break
            if times[i] < window_start:
                continue
            if times[i] >= window_end:
                break
            avg_range = float(ranges[max(0, i - 20):i].mean())
            if avg_range <= 0:
                continue
            if abs(close[i - 1] - open_price) < OPEN_RETEST_MULT * avg_range:
                continue
            if not (high[i] >= open_price >= low[i]):
                continue

            entry = float(close[i])
            direction = "long" if close[i - MOMENTUM_LOOKBACK] > open_price else "short"
            if direction == "long":
                stop = entry - atr
                target = entry + TARGET_R_MULTIPLE * atr
            else:
                stop = entry + atr
                target = entry - TARGET_R_MULTIPLE * atr

            sig = {"signal_time": times[i], "direction": direction, "entry": entry, "stop": stop, "target": target}
            r = simulate_signal(rth, sig)
            if r is not None:
                (long_r if direction == "long" else short_r).append(r)
            fired = True

    print(f"\nLong (open-as-support) signals: {len(long_r)}")
    print(f"Short (open-as-resistance) signals: {len(short_r)}")

    combined_r = long_r + short_r
    results = {
        "h88_long_open_support": analyze_r_multiples(long_r),
        "h88_short_open_resistance": analyze_r_multiples(short_r),
        "h88_combined": analyze_r_multiples(combined_r),
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
    out_path = DATA_DIR / "study_session_open_retest_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
