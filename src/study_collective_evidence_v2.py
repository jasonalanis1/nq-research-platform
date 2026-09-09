"""
study_collective_evidence_v2.py
================================

exp-123 -- frozen spec: research/studies/collective-evidence-v2-scoping.md.
Corroboration test across 3 genuinely independent Observatory-
discovered mechanisms (gap-magnitude, overnight-direction+regime,
reference-level touch), fixing pilot v1's disclosed correlated-variant
limitation. Measurement-layer only, no trade design.

HOW TO RUN:
    python3 src/study_collective_evidence_v2.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_bar_behavior_batch1 import build_daily_bars
from volatility_conditioning import build_conditioning_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
GAP_THRESH_MULT = 0.5
N_BOOTSTRAP = 3000
HORIZON_MIN = 10


def bootstrap_diff_ci(a, b, n_bootstrap=N_BOOTSTRAP, seed=7):
    rng = np.random.default_rng(seed)
    a_arr, b_arr = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if len(a_arr) < 2 or len(b_arr) < 2:
        return float("nan"), float("nan")
    diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        as_ = rng.choice(a_arr, size=len(a_arr), replace=True)
        bs_ = rng.choice(b_arr, size=len(b_arr), replace=True)
        diffs[i] = as_.mean() - bs_.mean()
    return float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))


def main():
    print("=" * 78)
    print("COLLECTIVE EVIDENCE PILOT v2: 3 independent mechanisms, corroboration test")
    print("=" * 78)
    print("\nFrozen spec: research/studies/collective-evidence-v2-scoping.md\n")

    df, is_synthetic = load_price_data(context="study_collective_evidence_v2.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    conditioning = build_conditioning_frame(discovery)
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    rows = []
    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index or day not in daily_bars.index:
            continue
        prior_high = float(daily_bars.loc[prior_day, "High"])
        prior_close = float(daily_bars.loc[prior_day, "Close"])
        prior_range = float(daily_bars.loc[prior_day, "range"])
        if prior_range <= 0:
            continue

        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if len(rth) < HORIZON_MIN + 5:
            continue
        open_price = float(rth["Close"].iloc[0])
        open_time = rth.index[0]
        tz = idx.tz

        # condition 1: gap magnitude (either direction) -- fires if |gap| >= 0.5x prior range
        gap = open_price - prior_close
        cond_gap = abs(gap) >= GAP_THRESH_MULT * prior_range

        # condition 2: overnight-direction + wide regime (only defined for down+wide, per
        # OBS-FINDING-009's own scope -- fires only in that specific sub-case, unchanged)
        is_wide = bool(conditioning.loc[day, "prior_day_wide"]) if day in conditioning.index else False
        cond_overnight = is_wide and (gap < 0)

        # condition 3: opening-hour touch of prior-day-high, overnight-high, or VWAP (first 60min)
        overnight_start = pd.Timestamp(prior_day, tz=tz).replace(hour=16, minute=0)
        lo = idx.searchsorted(overnight_start, side="left")
        hi = idx.searchsorted(open_time, side="left")
        overnight = discovery.iloc[lo:hi]
        overnight_high = float(overnight["High"].max()) if not overnight.empty else float("nan")

        open_hour = rth.between_time("09:30", "10:30")
        high_vals = open_hour["High"].values
        low_vals = open_hour["Low"].values
        typical = (open_hour["High"] + open_hour["Low"] + open_hour["Close"]).values / 3.0
        vol = open_hour["Volume"].values
        cum_pv = np.cumsum(typical * vol)
        cum_v = np.cumsum(vol)
        with np.errstate(invalid="ignore", divide="ignore"):
            vwap = np.where(cum_v > 0, cum_pv / cum_v, np.nan)
        touched_level = False
        for i in range(len(open_hour)):
            if high_vals[i] >= prior_high >= low_vals[i]:
                touched_level = True
                break
            if not np.isnan(overnight_high) and high_vals[i] >= overnight_high >= low_vals[i]:
                touched_level = True
                break
            if i >= 5 and not np.isnan(vwap[i]) and high_vals[i] >= vwap[i] >= low_vals[i]:
                touched_level = True
                break
        cond_level = touched_level

        n_conditions = int(cond_gap) + int(cond_overnight) + int(cond_level)

        close_vals = rth["Close"].values
        if HORIZON_MIN >= len(close_vals):
            continue
        fwd_return = float(close_vals[HORIZON_MIN] - close_vals[0])

        rows.append({
            "date": day, "n_conditions": n_conditions, "fwd_return_10min": fwd_return,
            "cond_gap": cond_gap, "cond_overnight": cond_overnight, "cond_level": cond_level,
        })

    trades = pd.DataFrame(rows)
    print(f"\nTotal days: {len(trades)}")
    print(trades["n_conditions"].value_counts().sort_index())

    group_2plus = trades.loc[trades["n_conditions"] >= 2, "fwd_return_10min"].tolist()
    group_0_1 = trades.loc[trades["n_conditions"] <= 1, "fwd_return_10min"].tolist()

    print(f"\n2+ conditions: n={len(group_2plus)}, mean={np.mean(group_2plus) if group_2plus else float('nan'):.3f}")
    print(f"0-1 conditions: n={len(group_0_1)}, mean={np.mean(group_0_1) if group_0_1 else float('nan'):.3f}")

    result = {"note": "insufficient data"}
    if len(group_2plus) >= 10 and len(group_0_1) >= 10:
        ci = bootstrap_diff_ci(group_2plus, group_0_1)
        credible = ci[0] > 0 or ci[1] < 0
        result = {
            "n_2plus": len(group_2plus), "n_0_1": len(group_0_1),
            "mean_2plus": float(np.mean(group_2plus)), "mean_0_1": float(np.mean(group_0_1)),
            "diff": float(np.mean(group_2plus) - np.mean(group_0_1)),
            "ci_90": ci, "credible": credible,
        }
        print(f"\nDiff (2+ minus 0-1): {result}")

    out = {"search_batch_id": "batch-2026-09-09-collective-evidence-v2", "result": result,
           "n_conditions_breakdown": trades["n_conditions"].value_counts().sort_index().to_dict()}
    out_path = DATA_DIR / "study_collective_evidence_v2_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
