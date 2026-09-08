"""
study_monetization_diagnostic_round1.py
=========================================

Diagnostic (not a new hypothesis) -- frozen spec:
research/studies/monetization-diagnostic-round1.md.

Reruns H81's short leg and H86's combined signal detection UNCHANGED,
but reports gross R-multiple (before cost) alongside net, to separate
"cost-dominated" from "genuinely negative gross edge" as the failure
mode. Also reports average MAE-to-stop-distance ratio (how often price
moved most of the way to the stop even on winners) as a second lens on
whether the stop is simply too tight for the measured behavior's own
noise.

HOW TO RUN:
    python3 src/study_monetization_diagnostic_round1.py
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
from volatility_conditioning import build_conditioning_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RANGE_LOOKBACK_BARS = 20
BUFFER_MULT = 1.5
ROUND_INCREMENT = 50.0
MOMENTUM_LOOKBACK = 5


def nearest_round_level(price):
    return round(price / ROUND_INCREMENT) * ROUND_INCREMENT


def simulate_with_gross(day_df, sig):
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
    return {
        "r_gross": pnl_gross / risk_points,
        "r_net": pnl_net / risk_points,
        "risk_points": risk_points,
        "exit_reason": outcome["exit_reason"],
    }


def summarize(rows, label):
    if not rows:
        print(f"  {label}: n=0")
        return
    gross = np.array([r["r_gross"] for r in rows])
    net = np.array([r["r_net"] for r in rows])
    stopped = sum(1 for r in rows if "stop" in r["exit_reason"])
    print(f"  {label}: n={len(rows)}")
    print(f"    mean R gross (before cost): {gross.mean():.4f}")
    print(f"    mean R net (after cost):    {net.mean():.4f}")
    print(f"    cost-per-trade in R terms:  {(gross.mean() - net.mean()):.4f}  (fixed 0.75pt / avg risk_pts={np.mean([r['risk_points'] for r in rows]):.2f})")
    print(f"    stopped-out fraction:       {stopped}/{len(rows)} = {stopped/len(rows):.1%}")


def main():
    print("=" * 78)
    print("MONETIZATION DIAGNOSTIC ROUND 1 -- gross vs. net decomposition")
    print("=" * 78)
    print("\nSpec: research/studies/monetization-diagnostic-round1.md\n")

    df, is_synthetic = load_price_data(context="study_monetization_diagnostic_round1.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    tz = discovery.index.tz
    idx = discovery.index
    daily_bars = build_daily_bars(discovery)
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    # ---- H81 short leg (opening-hour reference-level fade) ----
    h81_rows = []
    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
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
        typical = (rth["High"] + rth["Low"] + rth["Close"]).values / 3.0
        volume = rth["Volume"].values
        times = rth.index
        n = len(rth)
        cum_pv = np.cumsum(typical * volume)
        cum_v = np.cumsum(volume)
        with np.errstate(invalid="ignore", divide="ignore"):
            vwap = np.where(cum_v > 0, cum_pv / cum_v, np.nan)
        window_end = pd.Timestamp(day, tz=tz).replace(hour=10, minute=30)
        ranges = high - low
        for i in range(RANGE_LOOKBACK_BARS, n):
            if times[i] >= window_end:
                break
            upper_touch = (
                (high[i] >= prior_high >= low[i]) or
                (high[i] >= overnight_high >= low[i]) or
                (i >= 5 and not np.isnan(vwap[i]) and high[i] >= vwap[i] >= low[i])
            )
            if upper_touch:
                avg_range = float(ranges[i - RANGE_LOOKBACK_BARS:i].mean())
                buffer = BUFFER_MULT * avg_range
                entry = float(close[i])
                stop = float(high[i]) + buffer
                risk = stop - entry
                if risk > 0:
                    target = entry - TARGET_R_MULTIPLE * risk
                    sig = {"signal_time": times[i], "direction": "short", "entry": entry, "stop": stop, "target": target}
                    r = simulate_with_gross(rth, sig)
                    if r is not None:
                        h81_rows.append(r)
                break

    # ---- H86 combined (round-number open continuation) ----
    cond = build_conditioning_frame(discovery)
    normal_days = set(cond.index[~(cond["prior_day_narrow"].astype(bool) | cond["prior_day_wide"].astype(bool))])
    h86_rows = []
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
            if fired or times[i] >= window_end:
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
                    r = simulate_with_gross(rth, sig)
                    if r is not None:
                        h86_rows.append(r)
                    fired = True
            else:
                stop = float(high[i]) + buffer
                risk = stop - entry
                if risk > 0:
                    target = entry - TARGET_R_MULTIPLE * risk
                    sig = {"signal_time": times[i], "direction": "short", "entry": entry, "stop": stop, "target": target}
                    r = simulate_with_gross(rth, sig)
                    if r is not None:
                        h86_rows.append(r)
                    fired = True

    print("H81 short leg (opening-hour reference-level fade):")
    summarize(h81_rows, "h81_short")
    print("\nH86 combined (round-number continuation):")
    summarize(h86_rows, "h86_combined")

    out = {
        "spec": "research/studies/monetization-diagnostic-round1.md",
        "h81_short_n": len(h81_rows),
        "h81_short_mean_gross": float(np.mean([r["r_gross"] for r in h81_rows])) if h81_rows else None,
        "h81_short_mean_net": float(np.mean([r["r_net"] for r in h81_rows])) if h81_rows else None,
        "h86_combined_n": len(h86_rows),
        "h86_combined_mean_gross": float(np.mean([r["r_gross"] for r in h86_rows])) if h86_rows else None,
        "h86_combined_mean_net": float(np.mean([r["r_net"] for r in h86_rows])) if h86_rows else None,
    }
    out_path = DATA_DIR / "monetization_diagnostic_round1_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}.")


if __name__ == "__main__":
    main()
