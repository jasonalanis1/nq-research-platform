"""
study_vwap_dist_low_10d_drift_h118_holdout.py
=================================================

H118 -- HOLDOUT GENERATION 2 EVALUATION. Jason's explicit, in-the-
moment sign-off given 2026-09-09 in response to a full-promotion-bar
report (research-integrity protocol requires this for every individual
holdout use -- this consumes ONE of 5 total Holdout Generation 2 slots,
win or lose, per docs/RESEARCH_INTEGRITY_PROTOCOL.md).

Exactly the H118 definition, completely unmodified from the Discovery
and Validation passes: long entry at RTH reference close on a day whose
vwap_dist_vs_atr falls in the LOW tercile (bucket edges frozen on the
full Discovery sample, same edges reused here, never refit), exit at
RTH reference close 10 trading days later, no stop/target, one
round-trip cost, R-multiple against entry-day ATR(14).

HOW TO RUN:
    python3 src/study_vwap_dist_low_10d_drift_h118_holdout.py
"""

import json
from pathlib import Path

import numpy as np

from data_loader import load_price_data
from data_split import get_discovery_data, get_holdout_gen2_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from research_ledger import log_hypothesis
from study_vwap_dist_low_10d_drift_h118 import (
    VAR, BUCKET, HORIZON_DAYS, MIN_PROSPECTIVE_N,
    bootstrap_mean_ci, analyze_r_multiples, compute_bin_edges, run_backtest,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main():
    print("=" * 78)
    print("H118 HOLDOUT GENERATION 2 EVALUATION -- vwap_dist_vs_atr LOW, 10d drift")
    print("=" * 78)
    print("\n*** THIS CONSUMES 1 OF 5 HOLDOUT GENERATION 2 SLOTS, WIN OR LOSE ***")
    print("Jason's explicit sign-off: given 2026-09-09 in response to the H118 full-bar-clearance report.\n")

    df, is_synthetic = load_price_data(context="study_vwap_dist_low_10d_drift_h118_holdout.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    # Bucket edges frozen on the FULL DISCOVERY sample -- identical to the Discovery and Validation passes.
    discovery = get_discovery_data(df)
    disc_states = extend_state_frame(build_state_frame(discovery), discovery).reset_index()
    bin_edges, labels = compute_bin_edges(disc_states)
    if BUCKET not in labels:
        print(f"ABORT: bucket {BUCKET!r} not present in frozen edges {bin_edges}.")
        return

    holdout = get_holdout_gen2_data(df)
    hold_states = extend_state_frame(build_state_frame(holdout), holdout).reset_index()

    n, net_points, r_multiples = run_backtest(hold_states, bin_edges, labels)
    print(f"Holdout days: {len(hold_states)}   (bucket edges frozen from Discovery: {bin_edges})")
    print(f"Signals (low-tercile vwap_dist_vs_atr days, valid {HORIZON_DAYS}-day exit): {n}")

    points_result = {
        "n": len(net_points),
        "mean_net_points": float(np.mean(net_points)) if net_points else None,
        "ci_90_points": list(bootstrap_mean_ci(net_points)) if len(net_points) >= 2 else None,
    }
    r_result = analyze_r_multiples(r_multiples)
    n_r = r_result.get("n", 0)

    if n_r == 0:
        verdict = "NO_DATA"
    elif r_result["statistically_credible"] and r_result["economically_meaningful"]:
        verdict = "HOLDOUT_PASS" if n_r >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN"
    else:
        verdict = "HOLDOUT_FAIL"

    discovery_result = {"n": 554, "mean_r_multiple_net": 0.6166127225439121, "ci_90": [0.4533269265357841, 0.7849286122846664]}
    validation_result = {"n": 213, "mean_r_multiple_net": 0.2839896940801262, "ci_90": [0.047924667873678724, 0.5192995801763663]}

    print(f"\nPoints result: {points_result}")
    print(f"R-multiple result: {r_result}")
    print(f"Verdict: {verdict}")

    out = {
        "spec": "research/studies/vwap-dist-low-10d-drift-h118-spec.md",
        "phase": "HOLDOUT_GENERATION_2",
        "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON_DAYS,
        "bin_edges_frozen_from_discovery": [float(x) if np.isfinite(x) else None for x in bin_edges],
        "discovery_slice_result_reference": discovery_result,
        "validation_slice_result_reference": validation_result,
        "points_result": points_result,
        "r_multiple_result": r_result,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_vwap_dist_low_10d_drift_h118_holdout_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

    status = "HOLDOUT PASSED" if verdict == "HOLDOUT_PASS" else "REJECTED"
    notes = (
        f"H118 HOLDOUT GENERATION 2 evaluation (slot 1 of 5 consumed), Jason's explicit sign-off "
        f"given 2026-09-09. Discovery n=554 mean_r=0.617 ci_90=[0.453,0.785]; Validation n=213 "
        f"mean_r=0.284 ci_90=[0.048,0.519]; Holdout n={n_r}, mean_r={r_result.get('mean_r_multiple_net')}, "
        f"ci_90={r_result.get('ci_90')}. Verdict: {verdict}. Bucket edges frozen from Discovery throughout, "
        f"never refit. Full: data/study_vwap_dist_low_10d_drift_h118_holdout_results.json."
    )
    log_hypothesis(
        strategy_name="vwap_dist_low_10d_drift_h118_holdout",
        strategy_origin="derivative",
        parameters={
            "n": n_r,
            "mean_r_multiple_net": r_result.get("mean_r_multiple_net"),
            "ci_90": r_result.get("ci_90"),
            "statistically_credible": r_result.get("statistically_credible"),
            "economically_meaningful": r_result.get("economically_meaningful"),
        },
        data_slice_used="holdout_gen2",
        trade_count=n_r,
        strategy_status=status,
        notes=notes,
    )
    print("\nLogged to research/ledger/hypotheses.jsonl.")


if __name__ == "__main__":
    main()
