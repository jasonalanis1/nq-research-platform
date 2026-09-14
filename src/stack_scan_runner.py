"""
stack_scan_runner.py -- U27 / S2 of the CONDITIONAL STACK format.

ONE runner for every stack. It takes a FROZEN spec (validated and hashed by
src/stack_spec.py, registered in project_wide_multiplicity.STACK_REGISTRY before
this may run), evaluates the layers in time order, and emits per-occurrence rows.

WHAT IT DOES NOT DO: choose anything. No thresholds are fitted here, no variants
are tried, nothing is re-run with a different edge. The spec decides; the runner
executes and reports.

THE PAIRED TEST, STATED ONCE (this is the construction the blind Gate flagged on
hyp-156 -- paired vs unpooled drift -- so it is pinned here in code):
  cell ALL          every occurrence of the trigger, unconditioned
  cell IN_CONTEXT   occurrences where the context layer is true
  cell OUT_CONTEXT  occurrences where it is false
  GATING CLAIM      mean(IN) - mean(OUT), a difference of two INDEPENDENT,
                    disjoint samples of the same trigger. ALL is reported as a
                    reference only and is never the gating number, because
                    IN is a subset of ALL and the comparison would be
                    mechanically correlated.
  CI                percentile bootstrap on the difference, N_BOOT >= 20000,
                    then a Sidak-adjusted interval at the project's Discovery
                    stage trial count.

Chunking: device_bash has a hard ~3-minute limit and background jobs do not
survive between calls, so --year runs one calendar year and appends its
occurrences to a JSONL file; --report reads the whole file and does the
statistics once. Same pattern as market_behavior_discovery_scan_033.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import stack_spec as ss  # noqa: E402

N_BOOT = 20000
RNG_SEED = 20260913
TIME_EXIT = "15:55"


# --------------------------------------------------------------------------
# Layer evaluators. A spec names them; nothing here is chosen at run time.
# --------------------------------------------------------------------------
def trigger_orb_break_b3(day_df: pd.DataFrame) -> dict | None:
    """The frozen B3 opening-range break (src/base_entry_b3.py). Returns the raw
    signal dict or None. Entry is the NEXT bar's open after the trigger bar."""
    import base_entry_b3 as b3
    return b3.signal_for_day(day_df)


TRIGGERS = {"orb_break_b3": trigger_orb_break_b3}


def context_expected_range_mult(states_needed: pd.Index) -> pd.Series:
    """Per-session combined expected-range multiplier, exactly as the frozen
    Risk/State Engine computes it (base volatility conditioning, VXN added as a
    RESIDUAL, not a product). Returned as a date-indexed float series."""
    import risk_state_engine as rse
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame
    from volatility_conditioning import build_conditioning_frame, get_volatility_conditioning
    from data_loader import load_price_data
    from data_split import get_discovery_data

    df, syn = load_price_data(context="stack_scan_runner context layer")
    if syn:
        raise SystemExit("synthetic -- refusing")
    disc = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(disc), disc)
    cond = build_conditioning_frame(disc)
    p = rse.load_params()
    edge = float(p["vxn_high_tercile_edge"])
    vxn = pd.Series(states["vxn_level_vs_trailing"].to_numpy(dtype=float),
                    index=pd.to_datetime(pd.Index(states.index)))
    out = {}
    for d in cond.index:
        base = get_volatility_conditioning(d, cond)["expected_range_multiplier"]
        v = vxn.get(pd.Timestamp(d), np.nan)
        out[pd.Timestamp(d).date()] = rse._combine(base, bool(np.isfinite(v) and v >= edge))
    return pd.Series(out, dtype=float)


CONTEXTS = {"expected_range_mult": context_expected_range_mult}


# --------------------------------------------------------------------------
# Outcome: R realised by the frozen exit rule. No discretion, no optimisation.
# --------------------------------------------------------------------------
def realised_r(day_df: pd.DataFrame, sig: dict) -> float | None:
    """Walk bars from the entry bar to the time exit. Stop and target are the
    spec's frozen levels. If a single bar spans both, the STOP is taken -- the
    conservative assumption, fixed in advance, never chosen per trade."""
    path = day_df[day_df.index >= sig["entry_time"]]
    path = path.between_time("09:30", TIME_EXIT, inclusive="both")
    if path.empty:
        return None
    entry, stop, target = sig["entry"], sig["stop"], sig["target"]
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    long = sig["direction"] == "long"
    for _, bar in path.iterrows():
        hit_stop = bar["Low"] <= stop if long else bar["High"] >= stop
        hit_target = bar["High"] >= target if long else bar["Low"] <= target
        if hit_stop:
            return -1.0
        if hit_target:
            return round(abs(target - entry) / risk, 4)
    last = float(path["Close"].iloc[-1])
    return round(((last - entry) if long else (entry - last)) / risk, 4)


def occurrences_for_year(spec: dict, years) -> list[dict]:
    """One or more calendar years. Years are batched because the price file is
    loaded once per call and device_bash calls are time-boxed."""
    from data_loader import load_price_data
    from data_split import get_discovery_data
    years = [years] if isinstance(years, int) else list(years)
    df, syn = load_price_data(context=f"stack_scan_runner {spec['stack_id']} {years}")
    if syn:
        raise SystemExit("synthetic -- refusing")
    disc = get_discovery_data(df)
    disc = disc[disc.index.year.isin(years)]
    trig_name = spec["layers"][-1]["variable"]
    trig = TRIGGERS[trig_name]
    rows = []
    for day, g in disc.groupby(disc.index.normalize()):
        sig = trig(g)
        if sig is None:
            continue
        r = realised_r(g, sig)
        if r is None:
            continue
        rows.append({"date": str(pd.Timestamp(day).date()), "direction": sig["direction"],
                     "entry_time": str(sig["entry_time"]), "r": r,
                     "range_width": round(float(sig["range_width"]), 4)})
    return rows


# --------------------------------------------------------------------------
def _boot_diff(a: np.ndarray, b: np.ndarray, n_boot: int = N_BOOT, seed: int = RNG_SEED) -> tuple:
    rng = np.random.default_rng(seed)
    d = np.empty(n_boot)
    for i in range(n_boot):
        d[i] = rng.choice(a, a.size, replace=True).mean() - rng.choice(b, b.size, replace=True).mean()
    return float(np.percentile(d, 5)), float(np.percentile(d, 95)), d


def report(spec: dict, rows: list[dict]) -> dict:
    ctx_layer = spec["layers"][0]
    ctx = CONTEXTS[ctx_layer["variable"]](None)
    edges = ctx_layer["edges"]
    if edges == "top tercile":
        cut = float(np.nanpercentile(ctx.to_numpy(dtype=float), 200 / 3))
        in_ctx = {d for d, v in ctx.items() if np.isfinite(v) and v >= cut}
    else:
        raise SystemExit(f"edge rule '{edges}' not implemented -- the spec is frozen, the runner is not guessing")

    for r in rows:
        r["in_context"] = pd.Timestamp(r["date"]).date() in in_ctx
    a = np.array([r["r"] for r in rows if r["in_context"]], dtype=float)
    b = np.array([r["r"] for r in rows if not r["in_context"]], dtype=float)
    allr = np.array([r["r"] for r in rows], dtype=float)

    floor = int(spec["floor_occurrences"])
    if min(a.size, b.size) < floor:
        return {"verdict": "UNDERPOWERED", "n_in": int(a.size), "n_out": int(b.size),
                "floor": floor, "note": "fewer occurrences than the pre-registered floor in at least one "
                                        "cell. The definition is NOT loosened. This consumes one attempt."}

    lo, hi, d = _boot_diff(a, b)
    import project_wide_multiplicity as pwm
    n_disc = pwm.compute_stage_trial_counts()["discovery"]
    z90, z_adj = 1.6449, pwm.sidak_z(n_disc)
    se = (hi - lo) / (2 * z90)
    mean_d = float(a.mean() - b.mean())
    adj = (round(mean_d - z_adj * se, 4), round(mean_d + z_adj * se, 4))
    return {"verdict": "PASS" if adj[0] > 0 or adj[1] < 0 else "NULL",
            "cells": {"ALL_reference": {"n": int(allr.size), "mean_r": round(float(allr.mean()), 4)},
                      "IN_CONTEXT": {"n": int(a.size), "mean_r": round(float(a.mean()), 4)},
                      "OUT_CONTEXT": {"n": int(b.size), "mean_r": round(float(b.mean()), 4)}},
            "gating_difference_in_minus_out": round(mean_d, 4),
            "ci_90_bootstrap": (round(lo, 4), round(hi, 4)),
            "sidak_adjusted_ci": adj, "n_discovery_trials": int(n_disc),
            "n_boot": N_BOOT, "floor": floor}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--year", help="one year or a comma-separated list")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    ss.validate(spec)
    out = Path(a.out or f"data/stack_{spec['stack_id']}_occurrences.jsonl")
    if a.year:
        yrs = [int(y) for y in str(a.year).split(",")]
        rows = occurrences_for_year(spec, yrs)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("a") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        print(json.dumps({"years": yrs, "occurrences": len(rows), "file": str(out)}))
    if a.report:
        rows = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
        rows = list({(r["date"], r["entry_time"]): r for r in rows}.values())
        print(json.dumps({"spec_hash": ss.spec_hash(spec), "n_rows": len(rows),
                          "result": report(spec, rows)}, indent=2))


if __name__ == "__main__":
    main()
