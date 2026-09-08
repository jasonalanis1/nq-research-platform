"""
study_gap_fade.py
===================

H87 / exp-116 -- frozen spec: research/studies/gap-fade-h87-spec.md.
Parent finding: OBS-FINDING-006 (overnight gap fade). First hypothesis
in this project deliberately designed around the monetization
diagnostic's cost-ratio lesson: uses an ATR-scaled (wide) stop instead
of the 1-minute-bar buffer convention used in H81-H86.

REUSED, UNMODIFIED: TARGET_R_MULTIPLE (detect_level_sweep.py),
backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS,
build_daily_bars (study_bar_behavior_batch1.py).

HOW TO RUN:
    python3 src/study_gap_fade.py
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-observatory-hyp-006-h87"
GAP_THRESH_MULT = 0.5
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
    print("H87/EXP-116: OVERNIGHT GAP FADE (ATR-scaled stop)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/gap-fade-h87-spec.md\n")

    df, is_synthetic = load_price_data(context="study_gap_fade.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery)
    daily_bars = daily_bars.copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()

    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days: {len(days_sorted)}")

    long_r, short_r = [], []

    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index or day not in daily_bars.index:
            continue
        prior_close = float(daily_bars.loc[prior_day, "Close"])
        prior_range = float(daily_bars.loc[prior_day, "range"])
        atr = daily_bars.loc[prior_day, "atr14"]
        if pd.isna(atr) or atr <= 0 or prior_range <= 0:
            continue
        atr = float(atr)

        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty:
            continue
        open_price = float(rth["Close"].iloc[0])
        gap = open_price - prior_close
        if abs(gap) < GAP_THRESH_MULT * prior_range:
            continue

        signal_time = rth.index[0]
        entry = open_price
        if gap < 0:
            direction = "long"
            stop = entry - atr
            target = entry + TARGET_R_MULTIPLE * atr
        else:
            direction = "short"
            stop = entry + atr
            target = entry - TARGET_R_MULTIPLE * atr

        sig = {"signal_time": signal_time, "direction": direction, "entry": entry, "stop": stop, "target": target}
        r = simulate_signal(rth, sig)
        if r is not None:
            if direction == "long":
                long_r.append(r)
            else:
                short_r.append(r)

    print(f"\nLong (gap-down fade) signals: {len(long_r)}")
    print(f"Short (gap-up fade) signals: {len(short_r)}")

    combined_r = long_r + short_r
    results = {
        "h87_long_gap_down_fade": analyze_r_multiples(long_r),
        "h87_short_gap_up_fade": analyze_r_multiples(short_r),
        "h87_combined": analyze_r_multiples(combined_r),
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
    out_path = DATA_DIR / "study_gap_fade_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
