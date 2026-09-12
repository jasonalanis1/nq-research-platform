"""
market_behavior_discovery_scan_003.py
========================================

Scan 003 of the Market Behavior Discovery Engine (frozen spec:
research/infrastructure/market-behavior-discovery-engine-design.md).
Follows Scan 001 (0/2 candidates survived Validation: H116, H117) and
Scan 002 (1/1 candidate survived through Holdout: H118). Per
research/NEXT_UP.md queue item 2 and
research/studies/project-audit-and-new-starting-point-2026-09-09.md's
"thread 2" recommendation, scans the two remaining untested state
variables identified 2026-09-09: opening_range_vs_atr (implemented in
market_state_primitives.py v1 since Scan 001 but never included in
either prior scan's STATE_VARS list) and zn_level_vs_trailing (new,
market_state_primitives_v3.py -- ZN 10-Year Treasury futures prior-day
level vs. its own trailing average, the bond/rate-regime analogue of
Scan 002's vxn_level_vs_trailing).

Same exploratory/uncorrected methodology, same frozen constants
(N_BOOTSTRAP, RANDOM_SEED, HORIZONS, MIN_N_FOR_RANKED,
ATR_NORMALIZED_FLOOR, tercile bucketing) as Scan 001 and Scan 002,
fixed here BEFORE this script is run and BEFORE any Discovery-slice
result is looked at -- no new thresholds introduced, nothing tuned
after the fact. Nothing here is logged to the ledger, nothing is
treated as validated -- only a ranked candidate that clears the SAME
multi-stage screen Scan 001/002's candidates went through
(split-sample, regime-split, mechanism, and only then a frozen
monetization spec) gets taken further.

Non-trading, Discovery data only, per protocol.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_003.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_state_primitives_v3 import extend_state_frame_v3

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_RANKED = 40
ATR_NORMALIZED_FLOOR = 0.05
HORIZONS = [1, 3, 5, 10]

STATE_VARS = [
    "opening_range_vs_atr",
    "zn_level_vs_trailing",
]
N_BUCKETS = {"opening_range_vs_atr": 3, "zn_level_vs_trailing": 3}
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


def forward_return(close_series, i, horizon):
    if i + horizon >= len(close_series):
        return None
    c0, c1 = close_series.iloc[i], close_series.iloc[i + horizon]
    if c0 <= 0:
        return None
    return float(c1 - c0)


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
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 003 (opening range + ZN regime)")
    print("=" * 78)
    print("\nFrozen spec: research/infrastructure/market-behavior-discovery-engine-design.md\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_003.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states_v1 = build_state_frame(discovery)
    states_v2 = extend_state_frame(states_v1, discovery)
    states = extend_state_frame_v3(states_v2)
    avg_atr = float(states["atr14"].dropna().mean())
    print(f"Discovery days available: {len(states)}   avg ATR(14): {avg_atr:.2f} pts")
    for var in STATE_VARS:
        print(f"  {var}: {int(states[var].notna().sum())} non-null of {len(states)}")

    close = states["Close"].reset_index(drop=True)
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
                r = forward_return(close, i, horizon)
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
                cost_ok = atr_norm >= ATR_NORMALIZED_FLOOR

                candidates.append({
                    "state_var": var, "bucket": label, "horizon_days": horizon, "n": n,
                    "mean_fwd_return_pts": mean_r, "ci_90": list(ci),
                    "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": effect_vs_baseline,
                    "atr_normalized_effect": atr_norm, "credible_vs_zero": credible_vs_zero,
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
    print(f"Cells credible AND clearing cost floor: {len(ranked)}")
    print(f"Multiple-testing: naive expected false positives (alpha=0.10 x {len(candidates)} cells) = "
          f"{naive_expected_false_positives:.1f}; effective (alpha=0.10 x {n_series_scanned} independent series) = "
          f"{effective_expected_false_positives:.1f}\n")

    for c in ranked[:15]:
        print(f"  {c['state_var']:24s} {c['bucket']:5s} h={c['horizon_days']:2d}d  n={c['n']:4d}  "
              f"mean={c['mean_fwd_return_pts']:+7.2f}pts  vs_baseline={c['effect_vs_baseline_pts']:+7.2f}pts  "
              f"atr_norm={c['atr_normalized_effect']:.4f}  ci_90={c['ci_90']}")

    out = {
        "scan": "market_behavior_discovery_scan_003.py -- Scan 003",
        "spec": "research/infrastructure/market-behavior-discovery-engine-design.md",
        "status": "EXPLORATORY -- NOT a finding, NOT a hypothesis, NOT logged to the ledger",
        "n_days": len(states),
        "avg_atr14": avg_atr,
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
            "Scan 003: opening_range_vs_atr (implemented since Scan 001, never scanned) and "
            "zn_level_vs_trailing (new, market_state_primitives_v3.py). Same exploratory "
            "methodology and multiple-testing control as Scan 001/002 -- 'robust' and "
            "'mechanistically_plausible' are NOT auto-scored, a candidate needs a separate "
            "split-sample + regime + mechanism pass before any frozen monetization spec."
        ),
    }
    out_path = DATA_DIR / "market_behavior_discovery_scan_003_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nFull results written to {out_path}")


if __name__ == "__main__":
    main()
