"""
study_opening_hour_fade_excursion_exits.py
============================================

H82 / exp-111 -- frozen spec: research/studies/opening-hour-reference-level-fade-h82-spec.md.
Re-shaped monetization of the same behavior as H81 (exp-110), using
FIXED POINT stop/target distances derived from the Discovery-slice
median 15-min MAE/MFE (frozen before this hypothesis's own result was
seen), instead of H81's generic buffer-stop/1.35R-target convention.

REUSED, UNMODIFIED: backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS,
build_daily_bars (study_bar_behavior_batch1.py).

HOW TO RUN:
    python3 src/study_opening_hour_fade_excursion_exits.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from study_bar_behavior_batch1 import build_daily_bars
from study_pre_move_behavior_batch1 import analyze_r_multiples, MIN_PROSPECTIVE_N

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-observatory-hyp-001-h82"

# Frozen, derived from the Discovery sample BEFORE this hypothesis's own result -- see spec.
SHORT_STOP_PTS = 9.12
SHORT_TARGET_PTS = 10.00
LONG_STOP_PTS = 8.75
LONG_TARGET_PTS = 8.50


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
    print("H82/EXP-111: OPENING-HOUR REFERENCE-LEVEL FADE, EXCURSION-DERIVED EXITS")
    print("=" * 78)
    print("\nFrozen spec: research/studies/opening-hour-reference-level-fade-h82-spec.md\n")

    df, is_synthetic = load_price_data(context="study_opening_hour_fade_excursion_exits.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    tz = discovery.index.tz
    idx = discovery.index
    daily_bars = build_daily_bars(discovery)
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days: {len(days_sorted)}")

    short_r, long_r = [], []

    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index:
            continue
        prior_high = float(daily_bars.loc[prior_day, "High"])

        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if len(rth) < 30:
            continue

        overnight_start = pd.Timestamp(prior_day, tz=tz).replace(hour=16, minute=0)
        open_time = pd.Timestamp(day, tz=tz).replace(hour=9, minute=30)
        lo = idx.searchsorted(overnight_start, side="left")
        hi = idx.searchsorted(open_time, side="left")
        overnight = discovery.iloc[lo:hi]
        if overnight.empty:
            continue
        overnight_high = float(overnight["High"].max())
        overnight_low = float(overnight["Low"].min())

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
        short_fired = long_fired = False

        for i in range(5, n):
            if times[i] >= window_end:
                break
            if short_fired and long_fired:
                break

            if not short_fired:
                upper_touch = (
                    (high[i] >= prior_high >= low[i]) or
                    (high[i] >= overnight_high >= low[i]) or
                    (not np.isnan(vwap[i]) and high[i] >= vwap[i] >= low[i])
                )
                if upper_touch:
                    entry = float(close[i])
                    sig = {"signal_time": times[i], "direction": "short", "entry": entry,
                           "stop": entry + SHORT_STOP_PTS, "target": entry - SHORT_TARGET_PTS}
                    r = simulate_signal(rth, sig)
                    if r is not None:
                        short_r.append(r)
                    short_fired = True

            if not long_fired:
                if high[i] >= overnight_low >= low[i]:
                    entry = float(close[i])
                    sig = {"signal_time": times[i], "direction": "long", "entry": entry,
                           "stop": entry - LONG_STOP_PTS, "target": entry + LONG_TARGET_PTS}
                    r = simulate_signal(rth, sig)
                    if r is not None:
                        long_r.append(r)
                    long_fired = True

    print(f"\nShort signals: {len(short_r)}")
    print(f"Long signals: {len(long_r)}")

    combined_r = short_r + long_r
    results = {
        "h82_short_upper_level_fade": analyze_r_multiples(short_r),
        "h82_long_overnight_low_fade": analyze_r_multiples(long_r),
        "h82_combined": analyze_r_multiples(combined_r),
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
    out_path = DATA_DIR / "study_opening_hour_fade_excursion_exits_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
