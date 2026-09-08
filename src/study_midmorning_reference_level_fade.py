"""
study_midmorning_reference_level_fade.py
=========================================

H83 / exp-112 -- frozen spec: research/studies/midmorning-reference-level-fade-h83-spec.md.
Parent finding: OBS-FINDING-002 (mid-morning touches of overnight-high /
prior-day-high, "normal" regime). Short-only (no long-side candidate
cleared the Promising bar in this bucket).

REUSED, UNMODIFIED: TARGET_R_MULTIPLE (detect_level_sweep.py),
backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS,
build_daily_bars (study_bar_behavior_batch1.py),
volatility_conditioning.build_conditioning_frame (regime classification).

HOW TO RUN:
    python3 src/study_midmorning_reference_level_fade.py
"""

import json
from pathlib import Path

import numpy as np
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
SEARCH_BATCH_ID = "batch-2026-09-08-observatory-hyp-002-h83"
RANGE_LOOKBACK_BARS = 20
BUFFER_MULT = 1.5


def simulate_signal(day_df, sig):
    sig_series = pd.Series(sig)
    outcome = simulate_trade(day_df, sig_series, "signal_time")
    risk_points = abs(sig["entry"] - sig["stop"])
    if risk_points <= 0:
        return None
    pnl_gross = sig["entry"] - outcome["exit_price"]
    is_resolved = not outcome["exit_reason"].startswith("unresolved")
    pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
    return pnl_net / risk_points


def main():
    print("=" * 78)
    print("H83/EXP-112: MID-MORNING REFERENCE-LEVEL FADE (Observatory candidate #2)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/midmorning-reference-level-fade-h83-spec.md\n")

    df, is_synthetic = load_price_data(context="study_midmorning_reference_level_fade.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    tz = discovery.index.tz
    idx = discovery.index
    daily_bars = build_daily_bars(discovery)
    cond = build_conditioning_frame(discovery)
    normal_days = set(cond.index[cond["regime"] == "normal"]) if "regime" in cond.columns else None
    if normal_days is None:
        print(f"NOTE: conditioning frame columns = {list(cond.columns)}; regime col not found, treating all days as normal.")
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days: {len(days_sorted)}")

    short_r = []

    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
            continue
        if normal_days is not None and day not in normal_days:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index:
            continue
        prior_high = float(daily_bars.loc[prior_day, "High"])

        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if len(rth) < RANGE_LOOKBACK_BARS + 5:
            continue

        overnight_start = pd.Timestamp(prior_day, tz=tz).replace(hour=16, minute=0)
        open_time = pd.Timestamp(day, tz=tz).replace(hour=9, minute=30)
        lo = idx.searchsorted(overnight_start, side="left")
        hi = idx.searchsorted(open_time, side="left")
        overnight = discovery.iloc[lo:hi]
        if overnight.empty:
            continue
        overnight_high = float(overnight["High"].max())

        high = rth["High"].values
        low = rth["Low"].values
        close = rth["Close"].values
        times = rth.index
        n = len(rth)
        ranges = high - low

        window_start = pd.Timestamp(day, tz=tz).replace(hour=10, minute=30)
        window_end = pd.Timestamp(day, tz=tz).replace(hour=12, minute=0)

        for i in range(RANGE_LOOKBACK_BARS, n):
            if times[i] < window_start:
                continue
            if times[i] >= window_end:
                break

            upper_touch = (high[i] >= prior_high >= low[i]) or (high[i] >= overnight_high >= low[i])
            if upper_touch:
                avg_range = float(ranges[i - RANGE_LOOKBACK_BARS:i].mean())
                buffer = BUFFER_MULT * avg_range
                entry = float(close[i])
                stop = float(high[i]) + buffer
                risk = stop - entry
                if risk > 0:
                    target = entry - TARGET_R_MULTIPLE * risk
                    sig = {"signal_time": times[i], "direction": "short", "entry": entry, "stop": stop, "target": target}
                    r = simulate_signal(rth, sig)
                    if r is not None:
                        short_r.append(r)
                break  # first touch only per day

    print(f"\nShort (mid-morning upper-level fade) signals: {len(short_r)}")

    results = {"h83_midmorning_upper_level_fade": analyze_r_multiples(short_r)}

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
    out_path = DATA_DIR / "study_midmorning_reference_level_fade_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
