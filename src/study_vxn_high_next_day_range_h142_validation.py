"""ONE-SHOT Validation -- hyp-000142. Spec (frozen BEFORE this ran):
research/studies/vxn-high-next-day-range-h142-validation-spec.md.
Edges frozen from Discovery (Scan 014). Validation slice only. Nothing tuned.
HOW TO RUN: PYTHONPATH=src python3 src/study_vxn_high_next_day_range_h142_validation.py
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import load_price_data
from data_split import get_validation_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_behavior_discovery_scan_007 import build_rth_range_frame
import project_wide_multiplicity as pwm

FROZEN_EDGES = (-0.0608, 0.0258)   # from data/market_behavior_discovery_scan_014_results.json, never refit
OUT = Path(__file__).resolve().parent.parent / "data" / "study_vxn_high_next_day_range_h142_validation_results.json"
N_BOOT, SEED = 3000, 7


def ci(v):
    v = np.asarray(v, dtype=float); v = v[~np.isnan(v)]
    if len(v) < 2: return float("nan"), float("nan")
    m = np.random.default_rng(SEED).choice(v, size=(N_BOOT, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(m, 5)), float(np.percentile(m, 95))


def summ(vals):
    vals = list(vals); n = len(vals)
    if n < 2: return {"n": n, "mean": float("nan"), "ci_90": [float("nan")] * 2, "credible": False}
    lo, hi = ci(vals); return {"n": n, "mean": float(np.mean(vals)), "ci_90": [lo, hi], "credible": bool(lo > 1 or hi < 1)}


def main():
    df, syn = load_price_data(context="study_vxn_high_next_day_range_h142_validation.py")
    if syn: raise SystemExit("ABORT synthetic")
    val = get_validation_data(df)
    rth = build_rth_range_frame(val).dropna(subset=["trailing_avg_rth_range"]).copy()
    rth["ratio"] = rth["rth_range"] / rth["trailing_avg_rth_range"]
    st = extend_state_frame(build_state_frame(val), val)[["vxn_level_vs_trailing", "range_vs_atr"]]
    f = rth.join(st, how="inner").dropna(subset=["vxn_level_vs_trailing", "ratio"]).copy()
    f["bucket"] = pd.cut(f["vxn_level_vs_trailing"], bins=[-np.inf, FROZEN_EDGES[0], FROZEN_EDGES[1], np.inf], labels=["low", "mid", "high"])
    cells = {c: summ(f.loc[f.bucket == c, "ratio"]) for c in ["low", "mid", "high"]}
    for c, s in cells.items(): print(f"  {c:>4}: n={s['n']} mean={s['mean']:.4f} ci_90=({s['ci_90'][0]:.4f},{s['ci_90'][1]:.4f}) credible={s['credible']}")
    h = cells["high"]; tc = pwm.compute_stage_trial_counts()
    v = pwm.evaluate(label="hyp-000142_high_validation", stage="validation", n_obs=h["n"], mean=h["mean"], ci_90=tuple(h["ci_90"]), null_value=1.0, stage_trial_counts=tc)
    raw_pass = h["ci_90"][0] > 1.0 and (h["mean"] - 1.0) >= 0.05
    adj_pass = v.adjusted_ci[0] > 1.0 and (h["mean"] - 1.0) >= 0.05
    verdict = "VALIDATION_PASS" if adj_pass else "VALIDATION_FAIL"
    print(f"\nHIGH raw CI {h['ci_90']} raw_pass={raw_pass}; Sidak-adjusted (N_val={tc['validation']}) CI {list(v.adjusted_ci)} adj_pass={adj_pass}\nVERDICT: {verdict}")
    hh = f[f.bucket == "high"].dropna(subset=["range_vs_atr"]); med = hh["range_vs_atr"].median()
    p4 = {"prior_day_quiet": summ(hh.loc[hh.range_vs_atr < med, "ratio"]), "prior_day_wild": summ(hh.loc[hh.range_vs_atr >= med, "ratio"])}
    OUT.write_text(json.dumps({"frozen_edges": FROZEN_EDGES, "n_days": int(len(f)), "cells": cells, "sidak": {"n_validation_trials": tc["validation"], "adjusted_ci": list(v.adjusted_ci)},
                               "raw_pass": raw_pass, "adjusted_pass": adj_pass, "verdict": verdict, "p4_split": p4}, indent=1, default=float))
    print(f"Written {OUT}")


if __name__ == "__main__":
    main()
