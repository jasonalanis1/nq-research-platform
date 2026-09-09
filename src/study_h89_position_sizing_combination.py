"""
study_h89_position_sizing_combination.py
==========================================

exp-127 -- frozen spec: research/studies/h89-position-sizing-combination-spec.md.
Combines 2 already-validated project components (H89's gap-fade signal,
the position_size_multiplier sizing tool) to see if sizing improves the
risk-adjusted profile of the project's closest-ever near-miss.

HOW TO RUN:
    python3 src/study_h89_position_sizing_combination.py
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
from volatility_conditioning import build_conditioning_frame, get_volatility_conditioning, position_size_multiplier

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
GAP_THRESH_MULT = 0.5
ATR_WINDOW = 14
N_BOOTSTRAP = 3000


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


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=7):
    arr = np.asarray(values, dtype=float)
    if len(arr) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = rng.choice(arr, size=(n_bootstrap, len(arr)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def main():
    print("=" * 78)
    print("H89 + POSITION-SIZING COMBINATION TEST (exp-127)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/h89-position-sizing-combination-spec.md\n")

    df, is_synthetic = load_price_data(context="study_h89_position_sizing_combination.py")
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

    rows = []
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
            continue
        entry = open_price
        stop = entry - atr
        target = entry + TARGET_R_MULTIPLE * atr
        sig = {"signal_time": rth.index[0], "direction": "long", "entry": entry, "stop": stop, "target": target}
        r = simulate_signal(rth, sig)
        if r is None:
            continue

        vc = get_volatility_conditioning(day, conditioning)
        size_mult = position_size_multiplier(vc["expected_range_multiplier"])
        rows.append({"date": day, "r_multiple": r, "size_multiplier": size_mult, "size_weighted_r": r * size_mult})

    trades = pd.DataFrame(rows)
    print(f"\nTotal H89 trades: {len(trades)}")

    unweighted = trades["r_multiple"].to_numpy()
    weighted = trades["size_weighted_r"].to_numpy()

    def summarize(vals, label):
        mean = float(np.mean(vals))
        std = float(np.std(vals, ddof=1))
        sharpe_like = mean / std if std > 0 else float("nan")
        ci = bootstrap_mean_ci(vals)
        credible = ci[0] > 0 or ci[1] < 0
        print(f"{label}: n={len(vals)} mean={mean:.4f} std={std:.4f} sharpe_like={sharpe_like:.4f} ci_90={ci} credible={credible}")
        return {"n": len(vals), "mean": mean, "std": std, "sharpe_like": sharpe_like, "ci_90": ci, "credible": credible}

    result_unweighted = summarize(unweighted, "UNWEIGHTED (original H89)")
    result_weighted = summarize(weighted, "SIZE-WEIGHTED (combined with sizing tool)")

    print(f"\nSize multiplier distribution: min={trades['size_multiplier'].min():.2f} max={trades['size_multiplier'].max():.2f} mean={trades['size_multiplier'].mean():.2f}")
    print(f"Days where sizing fired (multiplier != 1.0): {(trades['size_multiplier'] != 1.0).sum()} / {len(trades)}")

    out = {"search_batch_id": "batch-2026-09-09-h89-sizing-combination",
           "unweighted": result_unweighted, "size_weighted": result_weighted}
    out_path = DATA_DIR / "study_h89_position_sizing_combination_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
