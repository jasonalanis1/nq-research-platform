"""
study_overnight_high_wide_open_fade.py
========================================

H85 / exp-114 -- frozen spec: research/studies/overnight-high-wide-open-fade-h85-spec.md.
Parent finding: OBS-FINDING-004 (overnight-high touch, wide regime, open bucket).
Final candidate of Observatory pilot round 1.

REUSED, UNMODIFIED: TARGET_R_MULTIPLE (detect_level_sweep.py),
backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS,
volatility_conditioning.build_conditioning_frame.

HOW TO RUN:
    python3 src/study_overnight_high_wide_open_fade.py
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
SEARCH_BATCH_ID = "batch-2026-09-08-observatory-hyp-004-h85"
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
    print("H85/EXP-114: OVERNIGHT-HIGH WIDE-REGIME OPEN FADE (Observatory candidate #4)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/overnight-high-wide-open-fade-h85-spec.md\n")

    df, is_synthetic = load_price_data(context="study_overnight_high_wide_open_fade.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    tz = discovery.index.tz
    idx = discovery.index
    cond = build_conditioning_frame(discovery)
    wide_days = set(cond.index[cond["prior_day_wide"].astype(bool)])
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days: {len(days_sorted)}, wide-regime days: {len(wide_days)}")

    short_r = []

    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
            continue
        if day not in wide_days:
            continue
        prior_day = days_sorted[day_num - 1]

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
        window_end = pd.Timestamp(day, tz=tz).replace(hour=10, minute=30)

        for i in range(RANGE_LOOKBACK_BARS, n):
            if times[i] >= window_end:
                break
            if high[i] >= overnight_high >= low[i]:
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
                break

    print(f"\nShort (overnight-high wide-open fade) signals: {len(short_r)}")

    results = {"h85_overnight_high_wide_open_fade": analyze_r_multiples(short_r)}

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
    out_path = DATA_DIR / "study_overnight_high_wide_open_fade_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
