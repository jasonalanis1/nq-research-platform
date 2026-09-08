"""
study_swing_high_wide_open_fade.py
=====================================

H90 / exp-119 -- frozen spec: research/studies/swing-high-wide-open-fade-h90-spec.md.
Parent finding: OBS-FINDING-008 (swing-high touch, wide regime, open
bucket). First candidate selected via the new monetization
pre-screening rule.

REUSED, UNMODIFIED: TARGET_R_MULTIPLE, backtest.simulate_trade,
backtest.ROUND_TRIP_COST_POINTS, build_daily_bars,
volatility_conditioning.build_conditioning_frame,
observatory_v2.find_swing_points (swing-pivot detection, unmodified).

HOW TO RUN:
    python3 src/study_swing_high_wide_open_fade.py
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
from observatory_v2 import find_swing_points

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-observatory-hyp-008-h90"
ATR_WINDOW = 14


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
    print("H90/EXP-119: SWING-HIGH WIDE-REGIME OPEN FADE")
    print("=" * 78)
    print("\nFrozen spec: research/studies/swing-high-wide-open-fade-h90-spec.md\n")

    df, is_synthetic = load_price_data(context="study_swing_high_wide_open_fade.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()
    cond = build_conditioning_frame(discovery)
    wide_days = set(cond.index[cond["prior_day_wide"].astype(bool)])
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days: {len(days_sorted)}, wide-regime days: {len(wide_days)}")

    short_r = []
    for day_num, day in enumerate(days_sorted):
        if day_num == 0 or day not in wide_days:
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
        if len(rth) < 30:
            continue

        high = rth["High"].values
        low = rth["Low"].values
        close = rth["Close"].values
        times = rth.index
        n = len(rth)
        window_end = times[0].replace(hour=10, minute=30)

        swing_high, _ = find_swing_points(high, low)

        for i in range(20, n):
            if times[i] >= window_end:
                break
            if not pd.isna(swing_high[i]) and high[i] >= swing_high[i] >= low[i]:
                entry = float(close[i])
                stop = entry + atr
                target = entry - TARGET_R_MULTIPLE * atr
                sig = {"signal_time": times[i], "direction": "short", "entry": entry, "stop": stop, "target": target}
                r = simulate_signal(rth, sig)
                if r is not None:
                    short_r.append(r)
                break

    print(f"\nShort (swing-high wide-open fade) signals: {len(short_r)}")
    results = {"h90_swing_high_wide_open_fade": analyze_r_multiples(short_r)}
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
    with open(DATA_DIR / "study_swing_high_wide_open_fade_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {DATA_DIR / 'study_swing_high_wide_open_fade_results.json'}")


if __name__ == "__main__":
    main()
