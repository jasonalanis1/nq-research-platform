"""
study_overnight_down_wide_open_fade_h93_prospective.py
========================================================

exp-122 -- frozen spec:
research/studies/overnight-down-wide-open-fade-h93-prospective-spec.md.
Pre-registered prospective test of H93 on the Validation slice.
Signal/stop/target unchanged; regime classifier computed continuously
across Discovery+Validation for warm-up continuity.

HOW TO RUN:
    python3 src/study_overnight_down_wide_open_fade_h93_prospective.py
"""
import json
from pathlib import Path

import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data, get_validation_data, _research_only, DISCOVERY_END_DATE, VALIDATION_END_DATE
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from study_bar_behavior_batch1 import build_daily_bars
from volatility_conditioning import build_conditioning_frame
from study_pre_move_behavior_batch1 import analyze_r_multiples, MIN_PROSPECTIVE_N

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-09-observatory-h93-prospective"
FIXED_STOP_POINTS = 13.125
FIXED_TARGET_POINTS = 19.25


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
    print("H93 PROSPECTIVE VALIDATION (exp-122) -- overnight-down wide-open fade")
    print("=" * 78)
    print("\nFrozen spec: research/studies/overnight-down-wide-open-fade-h93-prospective-spec.md\n")

    df, is_synthetic = load_price_data(context="study_overnight_down_wide_open_fade_h93_prospective.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    # continuous warm-up: Discovery+Validation combined for computing regime/ATR,
    # then only Validation-window days are scored (same convention as hyp-000024/026/028/035)
    research_df = _research_only(df, "study_overnight_down_wide_open_fade_h93_prospective.py")
    combined = research_df[research_df.index <= VALIDATION_END_DATE]
    idx = combined.index
    daily_bars = build_daily_bars(combined).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    conditioning = build_conditioning_frame(combined)
    day_groups = {d: g for d, g in combined.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    validation = get_validation_data(df)
    validation_days = set(validation.index.date)
    print(f"Validation-window days to score: {len(validation_days)}")

    long_r = []
    for day_num, day in enumerate(days_sorted):
        if day not in validation_days:
            continue
        if day_num == 0:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index or day not in daily_bars.index:
            continue
        if day not in conditioning.index:
            continue
        if not bool(conditioning.loc[day, "prior_day_wide"]):
            continue

        prior_close = float(daily_bars.loc[prior_day, "Close"])
        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty:
            continue
        open_price = float(rth["Close"].iloc[0])
        overnight_return = open_price - prior_close
        if overnight_return >= 0:
            continue

        entry = open_price
        stop = entry - FIXED_STOP_POINTS
        target = entry + FIXED_TARGET_POINTS
        sig = {"signal_time": rth.index[0], "direction": "long", "entry": entry, "stop": stop, "target": target}
        r = simulate_signal(rth, sig)
        if r is not None:
            long_r.append(r)

    print(f"\nValidation-slice overnight-down/wide-regime long fade signals: {len(long_r)}")
    results = {"h93_prospective_validation": analyze_r_multiples(long_r)}
    verdicts = {}
    for key, r in results.items():
        n = r.get("n", 0)
        if n == 0:
            verdicts[key] = "NO_DATA"
        elif r["statistically_credible"] and r["economically_meaningful"]:
            verdicts[key] = "PROSPECTIVE_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN"
        else:
            verdicts[key] = "PROSPECTIVE_FAIL"

    print()
    for key, r in results.items():
        print(f"{key}: {r}")
    print()
    for key, v in verdicts.items():
        print(f"  {key}: {v}")

    out = {"search_batch_id": SEARCH_BATCH_ID, "results": results, "verdicts": verdicts}
    with open(DATA_DIR / "study_overnight_down_wide_open_fade_h93_prospective_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {DATA_DIR / 'study_overnight_down_wide_open_fade_h93_prospective_results.json'}")


if __name__ == "__main__":
    main()
