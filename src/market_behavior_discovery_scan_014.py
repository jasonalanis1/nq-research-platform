"""
market_behavior_discovery_scan_014.py
========================================

Scan 014. Draws Entry 8 (map anchor M7, range footprint): vxn_level_vs_trailing
HIGH tercile -> next-session RTH range vs trailing-20d average. ATTEMPT 2 OF 2
(LAST) on vxn_level_vs_trailing (Scan 002 tested signed returns). Mechanism
doc written BEFORE this scan: research/mechanisms/vxn-implied-leads-realized-
range-m7.md.

ALIGNMENT (documented, no lookahead): market_state_primitives_v2 defines
vxn_level_vs_trailing on row t as VXN close of day t-1 / trailing-20d mean
(through t-2) - 1, i.e. the value is known before day t's RTH opens. So
"VXN close on day t-1 -> the FOLLOWING session's range" is: state at row t,
outcome = row t's own RTH range / trailing-20d average (shifted, no lookahead).
Terciles cut on the Discovery sample.

Cells (2 registered): HIGH (gating, P1: ratio credibly > 1.0), LOW (reported,
P2: credibly < 1.0). Reported: P3 separability vs overnight_range_vs_atr
tercile (residualised, >= 50% retained required to ADVANCE), P4 split of the
HIGH cell by whether day t-1's own realized range was elevated.

ONE pre-registered shot; no retuning. scan_014_2026-09-12 registered in
src/project_wide_multiplicity.py BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_014.py
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
    v = np.asarray(values, dtype=float); v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = rng.choice(v, size=(n_bootstrap, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def summarize(vals) -> dict:
    vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
    n = len(vals)
    if n < 2:
        return {"n": n, "mean_ratio": float("nan"), "ci_90": [float("nan"), float("nan")], "credible_vs_one": False, "direction": "insufficient_n"}
    m = float(np.mean(vals)); ci = bootstrap_mean_ci(vals)
    credible = ci[0] > 1.0 or ci[1] < 1.0
    direction = "elevated" if (credible and ci[0] > 1.0) else ("compressed" if (credible and ci[1] < 1.0) else "null")
    return {"n": n, "mean_ratio": m, "ci_90": list(ci), "credible_vs_one": bool(credible), "direction": direction}


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 014 (Entry 8 / M7: VXN elevated vs norm -> next-session RTH range)"); print("=" * 78)
    df, syn = load_price_data(context="market_behavior_discovery_scan_014.py")
    if syn:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(df)
    rth = build_rth_range_frame(disc).dropna(subset=["trailing_avg_rth_range"]).copy()
    rth["ratio"] = rth["rth_range"] / rth["trailing_avg_rth_range"]
    st = extend_state_frame(build_state_frame(disc), disc)[["vxn_level_vs_trailing", "overnight_range_vs_atr", "range_vs_atr"]]
    f = rth.join(st, how="inner").dropna(subset=["vxn_level_vs_trailing", "ratio"]).copy()
    print(f"Discovery days usable: {len(f)}")
    edges = np.nanpercentile(f["vxn_level_vs_trailing"], [100 / 3, 200 / 3])
    f["bucket"] = pd.cut(f["vxn_level_vs_trailing"], bins=[-np.inf, edges[0], edges[1], np.inf], labels=TERCILE_LABELS)
    print(f"vxn_level_vs_trailing tercile edges: {edges[0]:+.4f}, {edges[1]:+.4f}")
    cells = {}
    for b in TERCILE_LABELS:
        s = summarize(f.loc[f["bucket"] == b, "ratio"].tolist()); cells[b] = s
        print(f"  {b:>4}: n={s['n']} mean_ratio={s['mean_ratio']:.4f} ci_90=({s['ci_90'][0]:.4f},{s['ci_90'][1]:.4f}) {s['direction']}")
    verdict = "P1_PASS" if cells["high"]["direction"] == "elevated" else "P1_FAIL"
    print(f"\nGATING (HIGH cell elevated): {verdict}")

    # P3 separability vs overnight_range_vs_atr tercile (residualised)
    g = f.dropna(subset=["overnight_range_vs_atr"]).copy()
    g["on_t"] = pd.qcut(g["overnight_range_vs_atr"], 3, labels=TERCILE_LABELS)
    raw_spread = float(g.loc[g.bucket == "high", "ratio"].mean() - g.loc[g.bucket == "low", "ratio"].mean())
    g["resid"] = g["ratio"] - g.groupby("on_t", observed=True)["ratio"].transform("mean") + g["ratio"].mean()
    rh = summarize(g.loc[g.bucket == "high", "resid"].tolist()); rl = summarize(g.loc[g.bucket == "low", "resid"].tolist())
    resid_spread = rh["mean_ratio"] - rl["mean_ratio"]
    p3 = {"raw_high_minus_low": raw_spread, "resid_high_minus_low": resid_spread,
          "fraction_retained": (resid_spread / raw_spread) if raw_spread else float("nan"),
          "resid_high_cell": rh, "corr_vxn_vs_overnight_range": float(g["vxn_level_vs_trailing"].corr(g["overnight_range_vs_atr"]))}
    print(f"  P3 separability: raw spread {raw_spread:+.4f}, residualised {resid_spread:+.4f}, retained {p3['fraction_retained']:.2f}, resid HIGH {rh['direction']}; corr(vxn, overnight_range)={p3['corr_vxn_vs_overnight_range']:+.3f}")

    # P4: within HIGH, split by whether the prior day's own realized range (range_vs_atr) was elevated
    h = f[(f.bucket == "high")].dropna(subset=["range_vs_atr"])
    p4 = {}
    if len(h) >= 10:
        med = h["range_vs_atr"].median()
        p4 = {"prior_day_quiet": summarize(h.loc[h["range_vs_atr"] < med, "ratio"].tolist()),
              "prior_day_wild": summarize(h.loc[h["range_vs_atr"] >= med, "ratio"].tolist())}
        print(f"  P4 prior-quiet n={p4['prior_day_quiet']['n']} mean={p4['prior_day_quiet']['mean_ratio']:.4f} {p4['prior_day_quiet']['direction']} | prior-wild n={p4['prior_day_wild']['n']} mean={p4['prior_day_wild']['mean_ratio']:.4f} {p4['prior_day_wild']['direction']}")
    out = {"state_var": "vxn_level_vs_trailing", "tercile_edges": [float(edges[0]), float(edges[1])], "n_days": int(len(f)),
           "cells": cells, "gating_verdict": verdict, "p3_separability_vs_overnight_range": p3, "p4_prior_day_realized_split": p4}
    (DATA_DIR / "market_behavior_discovery_scan_014_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_014_results.json'}")


if __name__ == "__main__":
    main()
