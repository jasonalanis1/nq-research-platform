"""
study_collective_evidence_v2_direction.py
==========================================

exp-124 -- frozen spec:
research/studies/collective-evidence-v2-direction-followup-spec.md.
Direction-conditioned follow-up to OBS-FINDING-010: does the
corroboration effect hold up when restricted to days where all fired
conditions imply the SAME trade direction?

HOW TO RUN:
    python3 src/study_collective_evidence_v2_direction.py
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


def bootstrap_mean_ci(vals, n_bootstrap=N_BOOTSTRAP, seed=7):
    rng = np.random.default_rng(seed)
    arr = np.asarray(vals, dtype=float)
    if len(arr) < 2:
        return float("nan"), float("nan")
    means = rng.choice(arr, size=(n_bootstrap, len(arr)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def main():
    print("=" * 78)
    print("COLLECTIVE EVIDENCE v2 DIRECTION FOLLOW-UP")
    print("=" * 78)
    print("\nFrozen spec: research/studies/collective-evidence-v2-direction-followup-spec.md\n")

    df, is_synthetic = load_price_data(context="study_collective_evidence_v2_direction.py")
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

        gap = open_price - prior_close
        cond_gap = abs(gap) >= GAP_THRESH_MULT * prior_range
        gap_dir = "long" if gap < 0 else "short"

        is_wide = bool(conditioning.loc[day, "prior_day_wide"]) if day in conditioning.index else False
        cond_overnight = is_wide and (gap < 0)
        overnight_dir = "long"

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
        level_dir = "short"

        fired_dirs = []
        if cond_gap:
            fired_dirs.append(gap_dir)
        if cond_overnight:
            fired_dirs.append(overnight_dir)
        if cond_level:
            fired_dirs.append(level_dir)

        n_conditions = len(fired_dirs)
        if n_conditions < 2:
            continue

        same_direction = len(set(fired_dirs)) == 1
        implied_dir = fired_dirs[0] if same_direction else None

        close_vals = rth["Close"].values
        if HORIZON_MIN >= len(close_vals):
            continue
        fwd_return = float(close_vals[HORIZON_MIN] - close_vals[0])
        signed_return = fwd_return if implied_dir == "long" else (-fwd_return if implied_dir == "short" else None)

        rows.append({"date": day, "n_conditions": n_conditions, "same_direction": same_direction,
                      "implied_dir": implied_dir, "fwd_return_10min": fwd_return, "signed_return": signed_return})

    trades = pd.DataFrame(rows)
    print(f"\nTotal 2+ condition days: {len(trades)}")
    print(f"Same-direction: {trades['same_direction'].sum()}, Mixed: {(~trades['same_direction']).sum()}")

    same = trades.loc[trades["same_direction"], "signed_return"].dropna().tolist()
    mixed = trades.loc[~trades["same_direction"], "fwd_return_10min"].dropna().tolist()

    result = {}
    if len(same) >= 10:
        ci_vs_zero = bootstrap_mean_ci(same)
        credible_vs_zero = ci_vs_zero[0] > 0 or ci_vs_zero[1] < 0
        result["same_direction_vs_zero"] = {
            "n": len(same), "mean_signed_return": float(np.mean(same)),
            "ci_90": ci_vs_zero, "credible": credible_vs_zero,
        }
        print(f"\nSame-direction signed return vs zero: {result['same_direction_vs_zero']}")

    if len(same) >= 10 and len(mixed) >= 10:
        ci_diff = bootstrap_diff_ci(same, mixed)
        credible_diff = ci_diff[0] > 0 or ci_diff[1] < 0
        result["same_direction_vs_mixed"] = {
            "n_same": len(same), "n_mixed": len(mixed),
            "mean_same": float(np.mean(same)), "mean_mixed_raw": float(np.mean(mixed)),
            "ci_90_diff": ci_diff, "credible": credible_diff,
        }
        print(f"Same-direction (signed) vs mixed (raw): {result['same_direction_vs_mixed']}")

    out = {"search_batch_id": "batch-2026-09-09-collective-evidence-v2-direction", "result": result}
    out_path = DATA_DIR / "study_collective_evidence_v2_direction_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
