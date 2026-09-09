"""
market_behavior_discovery_scan_002.py
========================================

Scan 002 of the Market Behavior Discovery Engine (frozen spec:
research/infrastructure/market-behavior-discovery-engine-design.md).
Follows directly from Scan 001's result (0/2 candidates survived
Validation) -- rather than re-spending the remaining attempts on
already-nulled candidates, this scans NEW state variables from the
KNOWN UNEXPLORED LEARN bucket: volume vs. expected, distance from
session VWAP, a VXN-level cross-market descriptor (VXN daily close vs.
its own trailing average -- the only cross-market series on disk; a
true ES/NQ relationship stays deferred, no ES data available), and a
quintile (non-tercile) discretization of directional_persistence.

Same exploratory/uncorrected methodology and multiple-testing control
as Scan 001: nothing here is logged to the ledger, nothing is treated
as validated -- only a ranked candidate that clears the SAME
multi-stage screen Scan 001's candidates went through (split-sample,
regime-split, mechanism, and only then a frozen monetization spec)
gets taken further.

Non-trading, Discovery data only, per protocol.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_002.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_RANKED = 40
ATR_NORMALIZED_FLOOR = 0.05
HORIZONS = [1, 3, 5, 10]

STATE_VARS = [
    "volume_vs_expected",
    "vwap_dist_vs_atr",
    "vxn_level_vs_trailing",
    "directional_persistence_quintile",
]
N_BUCKETS = {  # quintile var gets its own natural 5 buckets, others stay terciles for consistency
    "volume_vs_expected": 3, "vwap_dist_vs_atr": 3,
    "vxn_level_vs_trailing": 3, "directional_persistence_quintile": 5,
}
TERCILE_LABELS = ["low", "mid", "high"]
QUINTILE_LABELS = ["q1", "q2", "q3", "q4", "q5"]


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
    if n_buckets == 5:
        # directional_persistence_quintile is already a 0..4 integer label from
        # extend_state_frame's pd.qcut call -- use it directly, no re-binning.
        return series.map(lambda x: QUINTILE_LABELS[int(x)] if pd.notna(x) else np.nan), QUINTILE_LABELS
    pct = [100 / n_buckets * k for k in range(1, n_buckets)]
    edges = np.unique(np.nanpercentile(series[valid], pct))
    if len(edges) < 1:
        return None, None
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = TERCILE_LABELS[: len(bin_edges) - 1]
    return pd.cut(series, bins=bin_edges, labels=labels, duplicates="drop"), labels


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 002 (new state variables)")
    print("=" * 78)
    print("\nFrozen spec: research/infrastructure/market-behavior-discovery-engine-design.md\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_002.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states_v1 = build_state_frame(discovery)
    states = extend_state_frame(states_v1, discovery)
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

    n_series_scanned = len(STATE_VARS)  # 4 independent variables (one already collapsed to its own natural buckets)
    naive_expected_false_positives = 0.10 * len(candidates)
    effective_expected_false_positives = 0.10 * n_series_scanned

    print(f"\nTotal (state x bucket x horizon) cells scanned: {len(candidates)}")
    print(f"Cells credible AND clearing cost floor: {len(ranked)}")
    print(f"Multiple-testing: naive expected false positives (alpha=0.10 x {len(candidates)} cells) = "
          f"{naive_expected_false_positives:.1f}; effective (alpha=0.10 x {n_series_scanned} independent series) = "
          f"{effective_expected_false_positives:.1f}\n")

    for c in ranked[:15]:
        print(f"  {c['state_var']:34s} {c['bucket']:5s} h={c['horizon_days']:2d}d  n={c['n']:4d}  "
              f"mean={c['mean_fwd_return_pts']:+7.2f}pts  vs_baseline={c['effect_vs_baseline_pts']:+7.2f}pts  "
              f"atr_norm={c['atr_normalized_effect']:.4f}  ci_90={c['ci_90']}")

    out = {
        "scan": "market_behavior_discovery_scan_002.py -- Scan 002",
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
            "Scan 002: new state variables (volume vs. expected, VWAP distance, VXN level vs. "
            "trailing, directional_persistence quintile) not scanned in Scan 001. Same exploratory "
            "methodology and multiple-testing control -- 'robust' and 'mechanistically_plausible' "
            "are NOT auto-scored, a candidate needs a separate split-sample + regime + mechanism "
            "pass before any frozen monetization spec, identical to how Scan 001's H116/H117 were "
            "screened (both of which then failed Validation -- treat any survivor here with the "
            "same skepticism)."
        ),
    }
    out_path = DATA_DIR / "market_behavior_discovery_scan_002_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full scan results to {out_path}.")


if __name__ == "__main__":
    main()
