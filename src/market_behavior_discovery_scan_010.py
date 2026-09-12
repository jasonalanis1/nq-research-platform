"""
market_behavior_discovery_scan_010.py
========================================

Scan 010 of the Market Behavior Discovery Engine. Draws Entry 5 from
research/idea_inventory.md (|gap_vs_atr| magnitude, same-day RTH range
vs trailing-20d average) -- FIRST attempt on gap MAGNITUDE as a
volatility (not direction) predictor. The existing signed-gap-fade
lineage (fade_the_gap, gap_down_fade_longonly_h89,
gap_down_fade_multiday_h91, gap_fade_h87, 4 closed hypotheses) tested
the SIGNED value against directional/return outcomes; this is a
distinct variable role (magnitude) and outcome statistic (range), not a
resurrection of that lineage.

Frozen scope, from idea_inventory.md Entry 5 (do not re-derive, no
retuning):
  - state variable: abs(gap_vs_atr) (existing gap_vs_atr descriptor,
    market_state_primitives.py, magnitude only)
  - outcome: same-day RTH range vs trailing-20d average RTH range
    (existing convention, reused from Entry 2/4/6, same as Scan 007/009)
  - THREE pre-registered cells: low/mid/high terciles of abs(gap_vs_atr),
    one outcome each = 3 cells. No horizon sweep (same day only).

Predictions (written before any number is looked at, per Entry 5):
  P1: HIGH abs(gap_vs_atr) tercile -> same-day RTH-range ratio > 1
      (elevation), credible vs 1.0 (90% CI lower bound > 1.0). Overnight
      information not yet repriced gets worked out intraday.
  P2: LOW abs(gap_vs_atr) tercile -> same-day RTH-range ratio < 1
      (compression), credible vs 1.0 (90% CI upper bound < 1.0). An open
      that agrees with the prior close signals no fresh repricing
      pressure, an orderly low-information session.
  P3 (non-restating, reported not gated): if the effect is genuinely
     about UNCERTAINTY rather than mere gap size, it should be WEAKER on
     HIGH abs(gap_vs_atr) days that ALSO show `high` volume_vs_expected
     that same day (a big gap already being met with heavy participation
     has already started resolving the uncertainty by the open, leaving
     less incremental range to unfold during RTH).

This is the entry's ONE pre-registered Discovery-stage shot (3 cells).
No new cells, no peeking then adjusting, no retuning. Per SCAN_REGISTRY's
standing maintenance note, the scan_010_2026-09-11 entry is added to
src/project_wide_multiplicity.py before any CI here is quoted as final.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_010.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_behavior_discovery_scan_007 import build_rth_range_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
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


def summarize(ratios: list) -> dict:
    n = len(ratios)
    if n < 2:
        return {"n": n, "mean_ratio": float("nan"), "ci_90": [float("nan"), float("nan")],
                "credible_vs_one": False, "direction": "insufficient_n"}
    mean_r = float(np.mean(ratios))
    ci = bootstrap_mean_ci(ratios)
    credible = ci[0] > 1.0 or ci[1] < 1.0
    direction = "compressed" if (credible and ci[1] < 1.0) else (
        "elevated" if (credible and ci[0] > 1.0) else "null"
    )
    return {"n": n, "mean_ratio": mean_r, "ci_90": list(ci),
            "credible_vs_one": bool(credible), "direction": direction}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 010 (|gap_vs_atr| magnitude, same-day RTH range vs trailing-20d avg)")
    print("=" * 78)
    print("\nInput: research/idea_inventory.md Entry 5\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_010.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)

    # Same-day RTH range + trailing-20d average (Scan 007's convention, reused as-is)
    rth = build_rth_range_frame(discovery)
    rth = rth.dropna(subset=["trailing_avg_rth_range"]).copy()
    rth["ratio"] = rth["rth_range"] / rth["trailing_avg_rth_range"]

    # gap_vs_atr (v1) + volume_vs_expected (v2), for the tercile split and P3
    states = extend_state_frame(build_state_frame(discovery), discovery)
    states = states[["gap_vs_atr", "volume_vs_expected"]].copy()
    states["abs_gap_vs_atr"] = states["gap_vs_atr"].abs()

    labeled = rth.join(states, how="inner")
    labeled = labeled.dropna(subset=["abs_gap_vs_atr"])
    print(f"Discovery RTH-days available (with trailing avg + gap state): {len(labeled)}")

    # Tercile edges cut fresh on this Discovery sample (not reused from any
    # prior gap scan, since this is a new variable role/outcome)
    valid = labeled["abs_gap_vs_atr"]
    edges = np.nanpercentile(valid, [100 / 3, 200 / 3])
    bin_edges = [-np.inf, edges[0], edges[1], np.inf]
    labeled["bucket"] = pd.cut(labeled["abs_gap_vs_atr"], bins=bin_edges, labels=TERCILE_LABELS)

    results = {}
    for bucket in TERCILE_LABELS:
        sub = labeled[labeled["bucket"] == bucket]
        ratios = sub["ratio"].dropna().tolist()
        summ = summarize(ratios)
        results[bucket] = summ
        print(f"  {bucket}: n={summ['n']} mean_ratio={summ['mean_ratio']:.4f} "
              f"ci_90=({summ['ci_90'][0]:.4f},{summ['ci_90'][1]:.4f}) "
              f"credible_vs_1={summ['credible_vs_one']} direction={summ['direction']}")

    # P3: non-restating, reported not gated -- split the HIGH gap-magnitude
    # cell by its own same-day volume_vs_expected median
    high = labeled[labeled["bucket"] == "high"].dropna(subset=["volume_vs_expected"])
    p3 = {"n_total": int(len(high))}
    if len(high) >= 10:
        med = high["volume_vs_expected"].median()
        low_vol = high[high["volume_vs_expected"] < med]
        high_vol = high[high["volume_vs_expected"] >= med]
        low_summ = summarize(low_vol["ratio"].dropna().tolist())
        high_summ = summarize(high_vol["ratio"].dropna().tolist())
        p3["low_volume_vs_expected"] = low_summ
        p3["high_volume_vs_expected"] = high_summ
        print(f"\n  P3 (reported, not gated, on HIGH-gap days): low_vol n={low_summ['n']} "
              f"mean={low_summ['mean_ratio']:.4f} direction={low_summ['direction']}  |  "
              f"high_vol n={high_summ['n']} mean={high_summ['mean_ratio']:.4f} direction={high_summ['direction']}")
    else:
        print("\n  P3: insufficient HIGH-gap rows with volume_vs_expected for a median split (n < 10) -- not computed.")

    out_path = DATA_DIR / "market_behavior_discovery_scan_010_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "state_var": "abs_gap_vs_atr",
            "outcome": "rth_range_vs_trailing_20d_avg_ratio",
            "cells": results,
            "p3_volume_conditioning_check": p3,
        }, f, indent=2)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
