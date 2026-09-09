"""
market_behavior_discovery_scan.py
====================================

First run of the Market Behavior Discovery Engine (frozen spec:
research/infrastructure/market-behavior-discovery-engine-design.md).
Scan 001 -- re-tests the project's EXISTING Discovery data under the
new state-first methodology instead of one hand-picked event at a
time. Per Jason's direction (2026-09-09): "back to square one" on
testing, using the new structure, without erasing anything already
built -- this scan reuses market_state_primitives.py (Layer 0) and the
project's existing bootstrap/ATR-normalized conventions unchanged.

WHAT THIS IS, AND ISN'T: this is Layer 1 (Behavior Discovery) -- an
EXPLORATORY, UNCORRECTED scan across (state variable x bucket x
forward horizon). Its job is to surface and RANK candidates, not to
confirm anything. Per the design spec's multiple-testing control, NO
result from this scan is logged to the hypothesis ledger and NONE is
treated as validated -- only a candidate that clears the ranking gate
(unusual + robust + economically meaningful + mechanistically
plausible) gets written up as its own frozen monetization spec and
enters the UNCHANGED existing Discovery->Validation->Holdout pipeline.
This script's output is a ranked candidate list, not a result.

Non-trading, Discovery data only, per protocol.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_RANKED = 40          # below this, a candidate can only be "noted", never ranked
ATR_NORMALIZED_FLOOR = 0.05     # same cost-dominance floor used project-wide
HORIZONS = [1, 3, 5, 10]        # trading days forward

STATE_VARS = [
    "range_vs_atr",
    "overnight_range_vs_atr",
    "gap_vs_atr",
    "directional_persistence",
    "location_in_range",
]
N_BUCKETS = 3  # low / mid / high terciles
BUCKET_LABELS = ["low", "mid", "high"]


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
    return float(c1 - c0)  # points, consistent with this project's other studies


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 001 (exploratory, state-first)")
    print("=" * 78)
    print("\nFrozen spec: research/infrastructure/market-behavior-discovery-engine-design.md\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = build_state_frame(discovery)
    avg_atr = float(states["atr14"].dropna().mean())
    print(f"Discovery days available: {len(states)}   avg ATR(14): {avg_atr:.2f} pts")

    close = states["Close"].reset_index(drop=True)
    states_reset = states.reset_index()

    candidates = []
    for var in STATE_VARS:
        series = states_reset[var]
        valid_mask = series.notna()
        if valid_mask.sum() < MIN_N_FOR_RANKED * N_BUCKETS:
            print(f"  {var}: insufficient non-null observations, skipped.")
            continue
        try:
            edges = np.nanpercentile(series[valid_mask], [100 / 3, 200 / 3])
        except Exception:
            continue
        edges = np.unique(edges)
        if len(edges) < 2:
            print(f"  {var}: degenerate (too few distinct values for tercile split), skipped.")
            continue
        bin_edges = [-np.inf] + list(edges) + [np.inf]
        labels = BUCKET_LABELS[: len(bin_edges) - 1]

        bucket_labels = pd.cut(series, bins=bin_edges, labels=labels, duplicates="drop")

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
                    "state_var": var,
                    "bucket": label,
                    "horizon_days": horizon,
                    "n": n,
                    "mean_fwd_return_pts": mean_r,
                    "ci_90": list(ci),
                    "baseline_mean_pts": baseline_mean,
                    "effect_vs_baseline_pts": effect_vs_baseline,
                    "atr_normalized_effect": atr_norm,
                    "credible_vs_zero": credible_vs_zero,
                    "clears_cost_floor": cost_ok,
                    "unusual": bool(credible_vs_zero),
                    "economically_meaningful": bool(cost_ok),
                    # "robust" and "mechanistically_plausible" are NOT auto-scored --
                    # robust needs a split-sample check (deferred to a v2 scan pass),
                    # mechanistically_plausible needs a Mechanism Agent pass. Both
                    # left False here so nothing auto-promotes past ranking without
                    # that second, separate pass -- see design spec ranking gate.
                    "robust": None,
                    "mechanistically_plausible": None,
                })

    ranked = sorted(
        [c for c in candidates if c["credible_vs_zero"] and c["clears_cost_floor"]],
        key=lambda c: c["atr_normalized_effect"],
        reverse=True,
    )

    print(f"\nTotal (state x bucket x horizon) cells scanned: {len(candidates)}")
    print(f"Cells credible AND clearing cost floor (candidates, unranked-for-mechanism): {len(ranked)}\n")

    for c in ranked[:15]:
        print(f"  {c['state_var']:28s} {c['bucket']:5s} h={c['horizon_days']:2d}d  n={c['n']:4d}  "
              f"mean={c['mean_fwd_return_pts']:+7.2f}pts  vs_baseline={c['effect_vs_baseline_pts']:+7.2f}pts  "
              f"atr_norm={c['atr_normalized_effect']:.4f}  ci_90={c['ci_90']}")

    out = {
        "scan": "market_behavior_discovery_scan.py -- Scan 001",
        "spec": "research/infrastructure/market-behavior-discovery-engine-design.md",
        "status": "EXPLORATORY -- NOT a finding, NOT a hypothesis, NOT logged to the ledger",
        "n_days": len(states),
        "avg_atr14": avg_atr,
        "state_vars_scanned": STATE_VARS,
        "horizons_scanned": HORIZONS,
        "total_cells": len(candidates),
        "cells_passing_unusual_and_cost_gate": len(ranked),
        "top_candidates": ranked[:25],
        "all_cells": candidates,
        "note": (
            "This scan only scores 'unusual' (credible vs. zero) and 'economically "
            "meaningful' (clears ATR-normalized cost floor) automatically. 'robust' "
            "(split-sample stability) and 'mechanistically_plausible' (a real reason "
            "this would happen, not just an arbitrary grid cell) are NOT auto-scored "
            "-- per the design spec's multiple-testing control, a candidate only "
            "reaches frozen-spec status after BOTH of those get a separate, explicit "
            "pass. Do not treat any row here as validated or tradeable."
        ),
    }
    out_path = DATA_DIR / "market_behavior_discovery_scan_001_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full scan results to {out_path}.")


if __name__ == "__main__":
    main()
