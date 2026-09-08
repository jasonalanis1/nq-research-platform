"""
study_h87_stability_check.py
==============================

Diagnostic (not a new hypothesis) -- frozen spec:
research/studies/h87-stability-check-spec.md.

Reruns H87's long leg (gap-down fade, ATR-scaled stop) UNCHANGED, split
by first-half vs. second-half of the Discovery period, to check whether
the near-miss result is stable or concentrated in one sub-period.

HOW TO RUN:
    python3 src/study_h87_stability_check.py
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
GAP_THRESH_MULT = 0.5
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
    df, is_synthetic = load_price_data(context="study_h87_stability_check.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    trades = []
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
        if gap >= 0 or abs(gap) < GAP_THRESH_MULT * prior_range:
            continue  # long leg only: gap DOWN
        entry = open_price
        stop = entry - atr
        target = entry + TARGET_R_MULTIPLE * atr
        sig = {"signal_time": rth.index[0], "direction": "long", "entry": entry, "stop": stop, "target": target}
        r = simulate_signal(rth, sig)
        if r is not None:
            trades.append({"date": day, "r": r})

    trades.sort(key=lambda t: t["date"])
    n = len(trades)
    half = n // 2
    first, second = trades[:half], trades[half:]
    r_first = np.array([t["r"] for t in first])
    r_second = np.array([t["r"] for t in second])

    print(f"H87 long leg (gap-down fade) stability check: n={n} total")
    print(f"  First half:  n={len(first)}, mean_r={r_first.mean():.4f}, dates {first[0]['date']}..{first[-1]['date']}")
    print(f"  Second half: n={len(second)}, mean_r={r_second.mean():.4f}, dates {second[0]['date']}..{second[-1]['date']}")

    out = {
        "spec": "research/studies/h87-stability-check-spec.md",
        "n_total": n,
        "first_half": {"n": len(first), "mean_r": float(r_first.mean())},
        "second_half": {"n": len(second), "mean_r": float(r_second.mean())},
    }
    with open(DATA_DIR / "h87_stability_check_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {DATA_DIR / 'h87_stability_check_results.json'}")


if __name__ == "__main__":
    main()
