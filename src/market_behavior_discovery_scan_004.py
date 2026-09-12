"""
market_behavior_discovery_scan_004.py
========================================

Scan 004 of the Market Behavior Discovery Engine (frozen design spec:
research/infrastructure/market-behavior-discovery-engine-design.md;
frozen scan-specific spec: research/studies/scan-004-scoping-2026-09-10.md
-- every constant, descriptor definition, and horizon below matches that
document exactly, fixed BEFORE this script was run and BEFORE any
Discovery-slice result was looked at, same discipline as Scan 001-003).

Follows Scan 003 (0/1 surviving candidates -- the sole candidate,
zn_level_vs_trailing/low/h10d, failed an independent volatility-regime
split and was abandoned, no hypothesis_id spent; Scan 003 is fully
closed). Per research/NEXT_UP.md queue and the Standing Research Priority
(2026-09-10, favor fast-resolving candidates), Scan 004 retargets to
SHORT horizons (intraday, overnight, 1d, 2d) instead of the [1,3,5,10]-day
set every prior scan used, and scans three new state descriptors, one per
new event family identified in
research/studies/project-audit-and-new-starting-point-2026-09-09.md
("thread 2"): days_to_monthly_opex (options-expiration), 
prior_close_location_in_range (session-transition), and
dist_to_multiday_reference_level_vs_atr (multi-day reference-level
touches) -- see market_state_primitives_v4.py and the frozen scoping doc
for the full definitions and the explicit non-resurrection reasoning
against exp-035, hyp-000110, and the opening-hour/mid-morning reference-
level-fade studies.

Same exploratory/uncorrected Discovery methodology as every prior scan --
nothing here is logged to the ledger, nothing is treated as validated,
only a ranked candidate that clears the SAME multi-stage screen (split-
sample, regime-split, mechanism, then a frozen monetization spec) gets
taken further.

TWO GATES for `ranked` (both required, per the frozen scoping doc's cost
caveat for short horizons): the existing ATR-normalized floor (unchanged,
0.05 of avg daily ATR14, same absolute-points threshold regardless of
horizon -- deliberately NOT relaxed for shorter horizons) AND a NEW
additive absolute-cost floor (effect_vs_baseline_pts >= 3x
ROUND_TRIP_COST_POINTS) -- added because short-horizon costs bite harder
in absolute terms than the ATR check alone might catch.

Non-trading, Discovery data only, per protocol.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_004.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS
from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_state_primitives_v3 import extend_state_frame_v3
from market_state_primitives_v4 import extend_state_frame_v4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_RANKED = 40
ATR_NORMALIZED_FLOOR = 0.05
ABSOLUTE_COST_MULTIPLE = 3.0
HORIZONS = ["intraday", "overnight", "1d", "2d"]

STATE_VARS = [
    "days_to_monthly_opex",
    "prior_close_location_in_range",
    "dist_to_multiday_reference_level_vs_atr",
]
N_BUCKETS = {v: 3 for v in STATE_VARS}
TERCILE_LABELS = ["low", "mid", "high"]


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


def forward_return(close_series, rth_open_series, i, horizon):
    """`close_series`/`rth_open_series` are positionally-indexed (reset_index)
    Series aligned to the same state frame. See
    research/studies/scan-004-scoping-2026-09-10.md "Anchor convention"
    for the exact definitions -- all four are forward-only relative to
    day i's RTH open (the point at which every state descriptor here is
    known), so none of them look ahead of what the state variable itself
    already assumes is knowable."""
    n = len(close_series)
    if horizon == "intraday":
        o, c = rth_open_series.iloc[i], close_series.iloc[i]
        if pd.isna(o) or pd.isna(c):
            return None
        return float(c - o)
    if horizon == "overnight":
        if i + 1 >= n:
            return None
        c0, o1 = close_series.iloc[i], rth_open_series.iloc[i + 1]
        if pd.isna(c0) or pd.isna(o1):
            return None
        return float(o1 - c0)
    if horizon in ("1d", "2d"):
        h = 1 if horizon == "1d" else 2
        if i + h >= n:
            return None
        c0, c1 = close_series.iloc[i], close_series.iloc[i + h]
        if pd.isna(c0) or pd.isna(c1) or c0 <= 0:
            return None
        return float(c1 - c0)
    raise ValueError(f"unknown horizon {horizon!r}")


def bucket_series(series, n_buckets):
    valid = series.notna()
    pct = [100 / n_buckets * k for k in range(1, n_buckets)]
    edges = np.unique(np.nanpercentile(series[valid], pct))
    if len(edges) < 1:
        return None, None
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = TERCILE_LABELS[: len(bin_edges) - 1]
    return pd.cut(series, bins=bin_edges, labels=labels, duplicates="drop"), labels


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 004 (short-horizon: opex, session-transition, multi-day ref-levels)")
    print("=" * 78)
    print("\nFrozen specs: research/infrastructure/market-behavior-discovery-engine-design.md")
    print("              research/studies/scan-004-scoping-2026-09-10.md\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_004.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states_v1 = build_state_frame(discovery)
    states_v2 = extend_state_frame(states_v1, discovery)
    states_v3 = extend_state_frame_v3(states_v2)
    states = extend_state_frame_v4(states_v3, discovery)
    avg_atr = float(states["atr14"].dropna().mean())
    absolute_cost_floor_pts = ABSOLUTE_COST_MULTIPLE * ROUND_TRIP_COST_POINTS
    print(f"Discovery days available: {len(states)}   avg ATR(14): {avg_atr:.2f} pts")
    print(f"Round-trip cost: {ROUND_TRIP_COST_POINTS:.3f} pts -> absolute cost floor: {absolute_cost_floor_pts:.3f} pts "
          f"(={ABSOLUTE_COST_MULTIPLE:.1f}x)")
    for var in STATE_VARS:
        print(f"  {var}: {int(states[var].notna().sum())} non-null of {len(states)}")

    close = states["Close"].reset_index(drop=True)
    rth_open = states["rth_open"].reset_index(drop=True)
    states_reset = states.reset_index()

    candidates = []
    for var in STATE_VARS:
        series = states_reset[var]
        n_buckets = N_BUCKETS[var]
        valid_mask = series.notna()
        if valid_mask.sum() < MIN_N_FOR_RANKED * n_buckets:
            print(f"  {var}: insufficient non-null observations, skipped.")
            continue

        bucket_labels, labels = bucket_series(series, n_buckets)
        if bucket_labels is None:
            print(f"  {var}: degenerate edges, skipped.")
            continue

        for horizon in HORIZONS:
            fwd_rets = {b: [] for b in labels}
            baseline_rets = []
            for i in range(len(states_reset)):
                b = bucket_labels.iloc[i]
                r = forward_return(close, rth_open, i, horizon)
                if r is None:
                    continue
                baseline_rets.append(r)
                if pd.notna(b):
                    fwd_rets[str(b)].append(r)

            baseline_mean = float(np.mean(baseline_rets)) if baseline_rets else float("nan")

            for label in labels:
                rets = fwd_rets[label]
                n = len(rets)
                if n < MIN_N_FOR_RANKED:
                    continue
                mean_r = float(np.mean(rets))
                ci = bootstrap_mean_ci(rets)
                credible_vs_zero = ci[0] > 0 or ci[1] < 0
                effect_vs_baseline = mean_r - baseline_mean
                atr_norm = abs(effect_vs_baseline) / avg_atr if avg_atr > 0 else float("nan")
                clears_atr_floor = atr_norm >= ATR_NORMALIZED_FLOOR
                clears_absolute_floor = abs(effect_vs_baseline) >= absolute_cost_floor_pts
                cost_ok = clears_atr_floor and clears_absolute_floor

                candidates.append({
                    "state_var": var, "bucket": label, "horizon": horizon, "n": n,
                    "mean_fwd_return_pts": mean_r, "ci_90": list(ci),
                    "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": effect_vs_baseline,
                    "atr_normalized_effect": atr_norm, "credible_vs_zero": credible_vs_zero,
                    "clears_atr_floor": clears_atr_floor, "clears_absolute_cost_floor": clears_absolute_floor,
                    "clears_cost_floor": cost_ok,
                    "unusual": bool(credible_vs_zero), "economically_meaningful": bool(cost_ok),
                    "robust": None, "mechanistically_plausible": None,
                })

    ranked = sorted(
        [c for c in candidates if c["credible_vs_zero"] and c["clears_cost_floor"]],
        key=lambda c: c["atr_normalized_effect"], reverse=True,
    )

    n_series_scanned = len(STATE_VARS)
    naive_expected_false_positives = 0.10 * len(candidates)
    effective_expected_false_positives = 0.10 * n_series_scanned

    print(f"\nTotal (state x bucket x horizon) cells scanned: {len(candidates)}")
    print(f"Cells credible AND clearing BOTH cost floors: {len(ranked)}")
    print(f"Multiple-testing: naive expected false positives (alpha=0.10 x {len(candidates)} cells) = "
          f"{naive_expected_false_positives:.1f}; effective (alpha=0.10 x {n_series_scanned} independent series) = "
          f"{effective_expected_false_positives:.1f}\n")

    for c in ranked[:15]:
        print(f"  {c['state_var']:40s} {c['bucket']:5s} h={c['horizon']:9s}  n={c['n']:4d}  "
              f"mean={c['mean_fwd_return_pts']:+7.2f}pts  vs_baseline={c['effect_vs_baseline_pts']:+7.2f}pts  "
              f"atr_norm={c['atr_normalized_effect']:.4f}  ci_90={c['ci_90']}")

    out = {
        "scan": "market_behavior_discovery_scan_004.py -- Scan 004",
        "spec": "research/studies/scan-004-scoping-2026-09-10.md",
        "status": "EXPLORATORY -- NOT a finding, NOT a hypothesis, NOT logged to the ledger",
        "n_days": len(states),
        "avg_atr14": avg_atr,
        "round_trip_cost_points": ROUND_TRIP_COST_POINTS,
        "absolute_cost_floor_points": absolute_cost_floor_pts,
        "state_vars_scanned": STATE_VARS,
        "horizons_scanned": HORIZONS,
        "total_cells": len(candidates),
        "cells_passing_unusual_and_cost_gate": len(ranked),
        "multiple_testing": {
            "naive_expected_false_positives": naive_expected_false_positives,
            "n_independent_series_approx": n_series_scanned,
            "effective_expected_false_positives": effective_expected_false_positives,
        },
        "top_candidates": ranked[:25],
        "all_cells": candidates,
        "note": (
            "Scan 004: days_to_monthly_opex, prior_close_location_in_range, "
            "dist_to_multiday_reference_level_vs_atr, scanned across short "
            "horizons (intraday/overnight/1d/2d) per the Standing Research "
            "Priority (2026-09-10). Same exploratory methodology and "
            "multiple-testing control as Scan 001-003, PLUS a new additive "
            "absolute-cost gate (3x round-trip cost) alongside the unchanged "
            "ATR floor. 'robust' and 'mechanistically_plausible' are NOT "
            "auto-scored -- a candidate needs a separate split-sample + "
            "regime + mechanism pass before any frozen monetization spec."
        ),
    }
    out_path = DATA_DIR / "market_behavior_discovery_scan_004_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nFull results written to {out_path}")


if __name__ == "__main__":
    main()
