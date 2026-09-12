# BLIND INTEGRITY GATE PACKET

You are the Integrity Gate, in a fresh context. Standing brief: assume this
candidate is wrong; find every reason the PROCEDURE could be fooling us.
Every result figure below is masked on purpose. Rule PASS / VETO / CONDITIONAL
on procedure only: leakage, contamination, post-hoc selection, frozen-before-
test, resurrection, multiplicity accounting, direction pre-registered, cost model
measured not assumed, review point sized (power) before freezing.
Output: Finding / Confidence / Novelty / Research Value / Recommendation.

## Family: vxn_high_next_day_range_h142

## Frozen spec (masked)

# FROZEN Validation spec — hyp-000142 (vxn_level_vs_trailing HIGH -> next-session RTH range)

Frozen: September 11th, 9:52 pm CT (2026-09-12 02:52 UTC), BEFORE any Validation-slice outcome is examined. Extra cycle at Jason's direction; Validation attempts are automated under the OPEN-tier rule ("let it run validation on its own, only holdout needs me").

## What is being tested
State: `vxn_level_vs_trailing` (market_state_primitives_v2.extend_state_frame, unchanged) on row t = VXN close of day t-1 / trailing-20-day mean (through t-2) - 1. Known before day t's RTH opens.
Outcome: day t's RTH range / trailing-20-trading-day average RTH range (build_rth_range_frame, shifted, no lookahead).
Bucket edges: FROZEN from Discovery (Scan 014): LOW <= [masked], HIGH > [masked]. Never refit.

## Pre-registered pass criteria (single shot, Validation slice 2021-10-04 .. 2024-01-03)
Gating cell: HIGH tercile (frozen edge). PASS if the 90% bootstrap CI of the mean range ratio has lower bound > 1.0 AND mean - 1.0 >= [masked] (economic floor). Project-wide multiplicity: also report the Sidak-adjusted CI at the Validation-stage trial count (project_wide_multiplicity.evaluate, stage="validation"); per the project convention the adjusted CI is the BINDING criterion.
Reported, not gating: LOW cell (predicted < 1.0); MID; the P4 split (prior-day range_vs_atr median within HIGH).
FAIL closes hyp-000142 and CLOSES vxn_level_vs_trailing for good (attempt 2 of 2). No second Validation attempt, no re-cut, no horizon change.

## What is NOT allowed after this point
Changing edges, the lookback (20d), the outcome normalisation, the slice boundary, or adding cells. Any discrepancy between this spec and the Validation script is a finding, not a reason to edit the spec.

## Script
src/study_vxn_high_next_day_range_h142_validation.py (to be written verbatim from this spec; the blind Integrity Gate reviews spec + script + mechanism doc BEFORE the script is run).


## Mechanism doc (masked)

# Mechanism — VXN elevated vs. its own norm -> next-day realized RTH range (Entry 8, map anchor M7, range footprint)

Written: September 11th, 9:44 pm CT (2026-09-12 02:44 UTC), extra cycle at Jason's direction  ·  PRE-REGISTERED
Results seen before writing: NO. Attempt 1 on vxn_level_vs_trailing (Scan 002) tested signed RETURNS and closed; this is attempt 2 of 2 and the LAST on this state variable, on a different outcome (magnitude). Transcribed from Entry 8's generation meeting (September 11th, 3:02 pm CT), which wrote the predictions before any number was looked at. Under AMENDMENT v2.5 this doc precedes the scan; after the scan it may only ADD predictions.

## 1. The claim
Options prices embed expected variance. When the market is paying up for NQ variance relative to its own recent norm (VXN close above its trailing-20-day average), the following RTH session's realized range runs above its own recent norm: implied information leads realized. The M7 anchor: vol-targeting and risk-parity books de-lever as VXN rises, and their selling is itself range-generating the next session -- so the footprint is range, not direction (the directional use is closed: hyp-000029/030).

## 2. Who is on the other side
Anyone sizing next-day stops/targets off the trailing realized range alone, ignoring what the options market already paid for. Diffuse, as with every range finding; the operational use is conditioning, not a directional trade.

## 3. Testable predictions
P1 (gating, single cell). HIGH vxn_level_vs_trailing tercile on day t -> day t+1 RTH range / trailing-20d average credibly > 1.0 (90% CI lower bound > 1.0). Falsifying alternative on the identical cell: if elevated VXN is variance-risk-premium noise or LAGS realized vol, the ratio is indistinguishable from 1.0.
P2 (reported). LOW tercile -> ratio credibly < 1.0 (compression).
P3 (separability, gating for ADVANCEMENT not for the Discovery result): the HIGH-VXN effect residualised on overnight_range_vs_atr tercile retains >= 50% of its raw magnitude and stays credible; < 50% = the overnight-coil finding restated through the options market -> CLOSED as redundant at Triage.
P4 (reported, non-restating counterparty check). Effect STRONGER when day t's own realized range was NOT already elevated (VXN high, yesterday quiet = implied leading realized) than when day t was already wild (VXN merely reflecting realized).

## 4. What would falsify this
P1 null (HIGH cell CI includes 1.0); or P3 < 50% retained; or P4 reversed (effect only when yesterday was already wild -- then VXN is a mirror of realized, not a lead).

## 5. Prediction status (updated September 11th, 9:47 pm CT, Scan 014 -- claim above unchanged)
P1 — CONFIRMED. HIGH tercile [masked], next-session range ratio [masked], ci_90 [masked], credibly elevated.
P2 — CONFIRMED. LOW tercile [masked], ratio [masked], [masked] null (clean monotone gradient).
P3 — PASSED the pre-registered >= 50% bar: residualised on overnight_range_vs_atr tercile, 66% of the HIGH-LOW spread retained and the residual HIGH cell stays credibly elevated. corr(vxn_level_vs_trailing, overnight_range_vs_atr) = [masked] -- the overlap with the coil is real, not identity. Advances to Triage rather than closing as redundant.
P4 — RAN OPPOSITE ITS PREDICTION (reported, not gating). Effect is STRONGER when the prior day was already wild ([masked]) than when it was quiet ([masked]); both credibly elevated. Reading: VXN partly mirrors yesterday's realized range (the falsifying alternative has a real component) AND still carries next-session range information when yesterday was quiet (the claim's component). Not smoothed over; a Statistical-stage pass must separate the two (e.g. residualise on range_vs_atr as well as overnight range).

## 6. Verdict
CREDIBLE SURVIVOR at Discovery. Logged hyp-000142 (PROMISING), SCAN_REGISTRY scan_014_2026-09-12 promoted_hypothesis_ids updated. Routed to Director (Triage). Not a directional edge -- a next-session RANGE conditioning fact, the same class as the three validated findings; if it survives Statistical -> Director -> blind Gate -> Validation it joins volatility_conditioning.py, it does not become a strategy. LAST attempt on vxn_level_vs_trailing regardless of what follows. State variable: vxn_level_vs_trailing (market_state_primitives_v2.extend_state_frame, unchanged: VXN close / trailing-20d mean, shifted -- the value on day t uses VXN through day t-1's close as the module defines it; the scan documents the exact alignment it uses). Outcome: day t+1 RTH range / trailing-20d average RTH range (build_rth_range_frame convention). Cells: HIGH gating, LOW reported = 2 cells registered. LAST attempt on this variable.


## Test / scan code (as-is; contains no results)

```python
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

```

## Ledger history for this family (results masked)

```json
[]
```