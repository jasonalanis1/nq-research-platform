"""
study_overnight_down_wide_open_fade.py
=======================================

H92 / exp-120 -- frozen spec:
research/studies/overnight-down-wide-open-fade-h92-spec.md.
Parent finding: OBS-FINDING-009 (research/studies/obs-finding-009-overnight-down-wide-open-fade.md).
Long-only fade of an overnight decline following a wide-regime prior
day, ATR(14)-scaled stop (same convention as H87/H89).

HOW TO RUN:
    python3 src/study_overnight_down_wide_open_fade.py
"""
import json
from pathlib import Path

import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_level_sweep import TARGET_R_MULTIPLE
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from study_bar_behavior_batch1 import build_daily_bars
from volatility_conditioning import build_conditioning_frame
from study_pre_move_behavior_batch1 import analyze_r_multiples, MIN_PROSPECTIVE_N

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-09-observatory-h92"
ATR_WINDOW = 14


def simulate_signal(day_df, sig):
    sig_series = pd.Series(sig)
    outcome = simulate_trade(day_df, sig_series, "signal_time")
    risk_points = abs(sig["entry"] - sig["stop"])
    if risk_points <= 0:
        return None
    pnl_gross = outcome["exit_price"] - sig["entry"]
    is_resolved = not outcome["exit_reason"].startswith("unresolved")
    pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
    return pnl_net / risk_points


def main():
    print("=" * 78)
    print("H92/EXP-120: OVERNIGHT-DOWN WIDE-REGIME OPEN FADE, LONG-ONLY")
    print("=" * 78)
    print("\nFrozen spec: research/studies/overnight-down-wide-open-fade-h92-spec.md\n")

    df, is_synthetic = load_price_data(context="study_overnight_down_wide_open_fade.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()
    conditioning = build_conditioning_frame(discovery)
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    long_r = []
    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index or day not in daily_bars.index:
            continue
        if prior_day not in conditioning.index:
            continue
        is_wide = bool(conditioning.loc[prior_day, "prior_day_wide"]) if prior_day in conditioning.index else False
        # conditioning frame's prior_day_wide is itself already shifted (classifies TODAY
        # by YESTERDAY's range); here we need "yesterday was wide", i.e. conditioning row
        # for TODAY (day), not prior_day -- align with OBS-FINDING-009's definition.
        if day not in conditioning.index:
            continue
        is_wide_today_context = bool(conditioning.loc[day, "prior_day_wide"])
        if not is_wide_today_context:
            continue

        prior_close = float(daily_bars.loc[prior_day, "Close"])
        atr = daily_bars.loc[prior_day, "atr14"]
        if pd.isna(atr) or atr <= 0:
            continue
        atr = float(atr)

        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty:
            continue
        open_price = float(rth["Close"].iloc[0])
        overnight_return = open_price - prior_close
        if overnight_return >= 0:
            continue  # only overnight-DOWN

        entry = open_price
        stop = entry - atr
        target = entry + TARGET_R_MULTIPLE * atr
        sig = {"signal_time": rth.index[0], "direction": "long", "entry": entry, "stop": stop, "target": target}
        r = simulate_signal(rth, sig)
        if r is not None:
            long_r.append(r)

    print(f"\nOvernight-down/wide-regime long fade signals: {len(long_r)}")
    results = {"h92_overnight_down_wide_open_fade_longonly": analyze_r_multiples(long_r)}
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
    with open(DATA_DIR / "study_overnight_down_wide_open_fade_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {DATA_DIR / 'study_overnight_down_wide_open_fade_results.json'}")


if __name__ == "__main__":
    main()
