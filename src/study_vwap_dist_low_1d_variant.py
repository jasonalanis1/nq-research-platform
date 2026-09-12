"""
study_vwap_dist_low_1d_variant.py
===================================

vwap_dist_vs_atr LOW-tercile, 1-DAY VARIANT of H118 (attempt 2 of 2 on
this candidate under the 2-attempt limit). Frozen spec:
research/studies/vwap-dist-low-1d-variant-spec.md. Integrity Gate
pre-clearance: research/studies/vwap-dist-low-1d-variant-integrity-
preclearance-2026-09-10.md (PASS, unconditional).

NOT H118. Never logs as an h118 row, never edits H118's ledger rows.
STRICT SEPARATION per NEXT_UP.md: does not inform and is not informed
by H118's forward test.

HOW TO RUN:
    python3 src/study_vwap_dist_low_1d_variant.py [--slice discovery|validation]

Default slice is "discovery" (slice 1c -- confirmation of an
already-scanned Scan 002 cell). Pass --slice validation only after
Mechanism + Statistical + Director Re-Evaluation + Integrity Gate
checkpoint have cleared the Discovery-slice result (slice 1d -- single
shot, budgeted Validation data).
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data, get_validation_data
from backtest import ROUND_TRIP_COST_POINTS
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from research_ledger import log_hypothesis

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
HORIZON_DAYS = 1
VAR, BUCKET = "vwap_dist_vs_atr", "low"
BUCKET_LABELS = ["low", "mid", "high"]
MIN_ECONOMIC_R = 0.05
MIN_PROSPECTIVE_N = 30
PARENT_HYPOTHESIS_ID = "hyp-000121"  # H118's own Discovery row


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    if n < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    idx_pool = np.arange(n)
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=n, replace=True)
        means[i] = arr[idx].mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def analyze_r_multiples(r_multiples):
    n = len(r_multiples)
    if n < 2:
        return {"n": n, "statistically_credible": False, "economically_meaningful": False}
    arr = np.array(r_multiples, dtype=float)
    ci_low, ci_high = bootstrap_mean_ci(arr)
    credible = ci_low > 0
    mean_r = float(arr.mean())
    econ = mean_r >= MIN_ECONOMIC_R
    return {
        "n": n, "mean_r_multiple_net": mean_r, "ci_90": (ci_low, ci_high),
        "statistically_credible": bool(credible), "economically_meaningful": bool(econ),
    }


def frozen_h118_bin_edges():
    # FROZEN from H118's own Discovery sample -- never refit here, at
    # any horizon. research/studies/vwap-dist-low-10d-drift-h118-spec.md
    return [-np.inf, -0.0460, 0.1471, np.inf], BUCKET_LABELS


def run_backtest(states_reset, bin_edges, labels):
    close = states_reset["Close"]
    atr = states_reset["atr14"]
    bucket_labels = pd.cut(states_reset[VAR], bins=bin_edges, labels=labels, duplicates="drop")

    net_points, r_multiples = [], []
    n_signals = 0
    for i in range(len(states_reset)):
        b = bucket_labels.iloc[i]
        if not (pd.notna(b) and str(b) == BUCKET):
            continue
        j = i + HORIZON_DAYS
        if j >= len(states_reset):
            continue
        entry_close = close.iloc[i]
        exit_close = close.iloc[j]
        entry_atr = atr.iloc[i]
        if entry_close <= 0 or pd.isna(entry_atr) or entry_atr <= 0:
            continue
        n_signals += 1
        gross = float(exit_close - entry_close)
        net = gross - ROUND_TRIP_COST_POINTS
        net_points.append(net)
        r_multiples.append(net / float(entry_atr))
    return n_signals, net_points, r_multiples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slice", choices=["discovery", "validation"], default="discovery")
    args = parser.parse_args()

    print("=" * 78)
    print(f"vwap_dist_vs_atr LOW, 1-DAY VARIANT of H118 -- {args.slice.upper()} SLICE")
    print("=" * 78)
    print("\nFrozen spec: research/studies/vwap-dist-low-1d-variant-spec.md")
    print("Attempt 2 of 2 on vwap_dist_vs_atr/LOW (2-attempt limit). NOT H118.\n")

    df, is_synthetic = load_price_data(context="study_vwap_dist_low_1d_variant.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    data_slice_fn = get_discovery_data if args.slice == "discovery" else get_validation_data
    sliced = data_slice_fn(df)
    states = extend_state_frame(build_state_frame(sliced), sliced)
    states_reset = states.reset_index()

    bin_edges, labels = frozen_h118_bin_edges()

    n_signals, net_points, r_multiples = run_backtest(states_reset, bin_edges, labels)
    print(f"Signals (low-tercile vwap_dist_vs_atr days, valid {HORIZON_DAYS}-day exit): {n_signals}")
    print(f"Resolved trades: {len(net_points)}")

    points_result = {
        "n": len(net_points),
        "mean_net_points": float(np.mean(net_points)) if net_points else None,
        "ci_90_points": list(bootstrap_mean_ci(net_points)) if len(net_points) >= 2 else None,
    }
    r_result = analyze_r_multiples(r_multiples)
    n = r_result.get("n", 0)

    if n == 0:
        verdict = "NO_DATA"
    elif r_result["statistically_credible"] and r_result["economically_meaningful"]:
        verdict = f"{args.slice.upper()}_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN"
    else:
        verdict = f"{args.slice.upper()}_FAIL"

    print(f"\nPoints result: {points_result}")
    print(f"R-multiple result: {r_result}")
    print(f"Verdict: {verdict}")

    out = {
        "spec": "research/studies/vwap-dist-low-1d-variant-spec.md",
        "slice": args.slice,
        "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON_DAYS,
        "bin_edges": [float(x) if np.isfinite(x) else None for x in bin_edges],
        "points_result": points_result,
        "r_multiple_result": r_result,
        "verdict": verdict,
    }
    out_path = DATA_DIR / f"study_vwap_dist_low_1d_variant_{args.slice}_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

    status = "PROMISING" if "PASS" in verdict else "REJECTED"
    if args.slice == "validation" and "PASS" in verdict:
        status = "VALIDATION CANDIDATE"
    notes = (
        f"vwap_dist_vs_atr LOW, 1-day variant of H118 (attempt 2 of 2, 2-attempt limit, "
        f"vwap_dist_vs_atr/LOW now exhausted). Frozen spec: "
        f"research/studies/vwap-dist-low-1d-variant-spec.md. Integrity Gate pre-clearance PASS: "
        f"research/studies/vwap-dist-low-1d-variant-integrity-preclearance-2026-09-10.md. "
        f"NOT an H118 row, no H118 edit. {args.slice}-slice. n={n}, "
        f"mean_r={r_result.get('mean_r_multiple_net')}, ci_90={r_result.get('ci_90')}. "
        f"Verdict: {verdict}. Full: data/study_vwap_dist_low_1d_variant_{args.slice}_results.json."
    )
    log_hypothesis(
        strategy_name="vwap_dist_low_1d_variant",
        strategy_origin="derivative",
        parameters={
            "n": n,
            "mean_r_multiple_net": r_result.get("mean_r_multiple_net"),
            "ci_90": r_result.get("ci_90"),
            "statistically_credible": r_result.get("statistically_credible"),
            "economically_meaningful": r_result.get("economically_meaningful"),
            "horizon_days": HORIZON_DAYS,
        },
        data_slice_used=args.slice,
        trade_count=n,
        strategy_status=status,
        parent_hypothesis_id=PARENT_HYPOTHESIS_ID,
        notes=notes,
    )
    print("\nLogged to research/ledger/hypotheses.jsonl.")


if __name__ == "__main__":
    main()
