"""
market_behavior_discovery_scan_006.py
========================================

Scan 006 of the Market Behavior Discovery Engine. Draws the top entry
from research/idea_inventory.md (Entry 1, added 2026-09-10, previously
unscanned -- see that file for the full LEARN/Integrity Gate reasoning):
does overnight_range_vs_atr predict the FIRST HOUR of RTH's own
reaction (09:30-10:30 ET), as opposed to H116's already-closed 10-day
close-to-close drift test on the same descriptor (MID tercile).

SECOND (and per the Integrity Gate ruling in idea_inventory.md, LAST)
attempt on overnight_range_vs_atr as a state variable. Genuinely
different forward-return construction (intraday minute-level reaction,
not daily close-to-close), pre-registered before any result is looked
at.

No ex-ante direction: Entry 1's own mechanism claim explicitly allows
EITHER continuation OR reversion (information processed by the deepest
RTH liquidity pool could confirm or fade the overnight move) -- so this
is screened the same two-sided way as every other exploratory Discovery
cell in this project (credible-vs-zero via 90% bootstrap CI not
spanning zero, direction unconstrained), NOT a single pre-registered-
direction shot like the FOMC/NFP macro-announcement tests.

Bucket edges: reuses the SAME overnight_range_vs_atr tercile
construction (percentile-based, computed fresh off the full Discovery
sample, same bucket_series methodology as every prior scan -- "frozen"
means same methodology, not a stored number, consistent with how every
other scan in this project re-derives its own tercile edges each run).

Non-trading, Discovery data only, per protocol. Nothing here is logged
to the ledger unless a cell clears both the ATR-normalized floor and
the additive absolute-cost floor (short-horizon convention, unchanged
from Scan 004/005) and then survives split-sample robustness.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_006.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS
from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_RANKED = 40
ATR_NORMALIZED_FLOOR = 0.05
ABSOLUTE_COST_MULTIPLE = 3.0
STATE_VAR = "overnight_range_vs_atr"
TERCILE_LABELS = ["low", "mid", "high"]
FIRST_HOUR_MINUTES = 60  # 09:30-10:30 ET, matches Entry 1's frozen horizon


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        s = rng.choice(v, size=len(v), replace=True)
        means[i] = s.mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def bucket_series(series, n_buckets=3):
    valid = series.notna()
    pct = [100 / n_buckets * k for k in range(1, n_buckets)]
    edges = np.unique(np.nanpercentile(series[valid], pct))
    if len(edges) < 1:
        return None, None
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = TERCILE_LABELS[: len(bin_edges) - 1]
    return pd.cut(series, bins=bin_edges, labels=labels, duplicates="drop"), labels


def first_hour_return_by_day(raw_df: pd.DataFrame) -> dict:
    """RTH open (first 09:30 bar's Open) to the close of the 60th 1-min
    bar of RTH (~10:29 bar, approximating the 10:30 ET mark) -- same
    fixed-bar-count slicing convention as _opening_range_by_day in
    market_state_primitives.py (iloc[:minutes] on a 1-min series), just
    applied to Open/Close instead of High/Low, and computed directly off
    the raw frame (not build_daily_bars) so this genuinely reflects RTH-
    only price action, matching market_state_primitives_v4._rth_daily_ohlc's
    reasoning for why RTH-only OHLC differs from build_daily_bars' output."""
    out = {}
    for day, day_df in raw_df.groupby(raw_df.index.date):
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty:
            continue
        window = rth.iloc[:FIRST_HOUR_MINUTES]
        if len(window) < FIRST_HOUR_MINUTES:
            continue  # partial/holiday-shortened session -- excluded, not padded, no lookahead substitute
        o = float(window.iloc[0]["Open"])
        c = float(window.iloc[-1]["Close"])
        out[day] = c - o
    return out


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 006 (overnight_range_vs_atr, first-RTH-hour reaction)")
    print("=" * 78)
    print("\nInput: research/idea_inventory.md Entry 1 (drawn 2026-09-10 20:15 UTC session)\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_006.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = build_state_frame(discovery)
    avg_atr = float(states["atr14"].dropna().mean())
    absolute_cost_floor_pts = ABSOLUTE_COST_MULTIPLE * ROUND_TRIP_COST_POINTS
    print(f"Discovery days available: {len(states)}   avg ATR(14): {avg_atr:.2f} pts")
    print(f"Round-trip cost: {ROUND_TRIP_COST_POINTS:.3f} pts -> absolute cost floor: {absolute_cost_floor_pts:.3f} pts "
          f"(={ABSOLUTE_COST_MULTIPLE:.1f}x)")
    print(f"{STATE_VAR}: {int(states[STATE_VAR].notna().sum())} non-null of {len(states)}")

    first_hour = first_hour_return_by_day(discovery)
    print(f"first_hour_return computed for {len(first_hour)} days (excludes partial/holiday-shortened RTH sessions)")

    fh_series = pd.Series({pd.Timestamp(d): v for d, v in first_hour.items()})
    fh_series.index = fh_series.index.date
    states = states.copy()
    states["first_hour_return"] = pd.Series(first_hour).reindex(states.index)

    series = states[STATE_VAR]
    valid_mask = series.notna() & states["first_hour_return"].notna()
    if valid_mask.sum() < MIN_N_FOR_RANKED * 3:
        print("insufficient non-null observations, ABORT")
        return

    bucket_labels, labels = bucket_series(series, 3)
    states_reset = states.reset_index()
    bucket_labels = bucket_labels.reset_index(drop=True)

    candidates = []
    fwd_rets = {b: [] for b in labels}
    baseline_rets = []
    for i in range(len(states_reset)):
        r = states_reset.loc[i, "first_hour_return"]
        if pd.isna(r):
            continue
        baseline_rets.append(float(r))
        b = bucket_labels.iloc[i]
        if pd.notna(b):
            fwd_rets[str(b)].append(float(r))

    baseline_mean = float(np.mean(baseline_rets)) if baseline_rets else float("nan")
    print(f"\nbaseline (all days) n={len(baseline_rets)} mean_first_hour_return={baseline_mean:.4f} pts\n")

    for label in labels:
        rets = fwd_rets[label]
        n = len(rets)
        if n < MIN_N_FOR_RANKED:
            print(f"  {label}: n={n} < {MIN_N_FOR_RANKED}, skipped")
            continue
        mean_r = float(np.mean(rets))
        ci = bootstrap_mean_ci(rets)
        credible_vs_zero = ci[0] > 0 or ci[1] < 0
        effect_vs_baseline = mean_r - baseline_mean
        atr_norm = abs(effect_vs_baseline) / avg_atr if avg_atr > 0 else float("nan")
        clears_atr_floor = atr_norm >= ATR_NORMALIZED_FLOOR
        clears_absolute_floor = abs(effect_vs_baseline) >= absolute_cost_floor_pts
        cost_ok = clears_atr_floor and clears_absolute_floor

        row = {
            "state_var": STATE_VAR, "bucket": label, "horizon": "first_rth_hour", "n": n,
            "mean_fwd_return_pts": mean_r, "ci_90": list(ci),
            "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": effect_vs_baseline,
            "atr_normalized_effect": atr_norm, "credible_vs_zero": credible_vs_zero,
            "clears_atr_floor": clears_atr_floor, "clears_absolute_cost_floor": clears_absolute_floor,
            "clears_cost_floor": cost_ok,
            "ranked": bool(credible_vs_zero and cost_ok),
        }
        candidates.append(row)
        print(f"  {label}: n={n} mean={mean_r:+.4f} ci_90=({ci[0]:+.4f},{ci[1]:+.4f}) "
              f"effect_vs_baseline={effect_vs_baseline:+.4f} atr_norm={atr_norm:.4f} "
              f"credible={credible_vs_zero} cost_ok={cost_ok} RANKED={row['ranked']}")

    ranked = [c for c in candidates if c["ranked"]]
    print(f"\n{len(ranked)}/{len(candidates)} cells RANKED (credible + clears both cost floors)")

    out_path = DATA_DIR / "market_behavior_discovery_scan_006_results.json"
    with open(out_path, "w") as f:
        json.dump({"state_var": STATE_VAR, "horizon": "first_rth_hour", "cells": candidates,
                    "avg_atr": avg_atr, "absolute_cost_floor_pts": absolute_cost_floor_pts}, f, indent=2)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
