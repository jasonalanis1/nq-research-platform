"""
study_vwap_dist_low_10d_drift_h118_prospective.py
=====================================================

H118 -- frozen spec:
research/studies/vwap-dist-low-10d-drift-h118-prospective-spec.md.
Single pre-registered Validation-slice prospective test of H118.
Bucket edges frozen from Discovery -- nothing refit here.

HOW TO RUN:
    python3 src/study_vwap_dist_low_10d_drift_h118_prospective.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data, get_validation_data
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
    print("H118 PROSPECTIVE: VWAP-DIST-LOW, 10-DAY DRIFT, VALIDATION SLICE")
    print("=" * 78)
    print("\nFrozen spec: research/studies/vwap-dist-low-10d-drift-h118-prospective-spec.md\n")

    df, is_synthetic = load_price_data(context="study_vwap_dist_low_10d_drift_h118_prospective.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    # Bucket edges frozen on the FULL DISCOVERY sample -- identical to the Discovery-slice script.
    discovery = get_discovery_data(df)
    disc_states = extend_state_frame(build_state_frame(discovery), discovery).reset_index()
    bin_edges, labels = compute_bin_edges(disc_states)
    if BUCKET not in labels:
        print(f"ABORT: bucket {BUCKET!r} not present in frozen edges {bin_edges}.")
        return

    validation = get_validation_data(df)
    val_states = extend_state_frame(build_state_frame(validation), validation).reset_index()

    n, net_points, r_multiples = run_backtest(val_states, bin_edges, labels)
    print(f"Validation days: {len(val_states)}   (bucket edges frozen from Discovery: {bin_edges})")
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
        verdict = "PROSPECTIVE_PASS" if n_r >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN"
    else:
        verdict = "PROSPECTIVE_FAIL"

    discovery_result = {
        "n": 554, "mean_r_multiple_net": 0.6166127225439121,
        "ci_90": [0.4533269265357841, 0.7849286122846664],
    }
    full_promotion_bar_cleared = bool(
        verdict == "PROSPECTIVE_PASS"
        and r_result.get("ci_90") and r_result["ci_90"][0] > 0
        and r_result.get("economically_meaningful")
    )

    print(f"\nPoints result: {points_result}")
    print(f"R-multiple result: {r_result}")
    print(f"Verdict: {verdict}")
    print(f"Full 90% promotion bar cleared (Discovery pass + this prospective pass): {full_promotion_bar_cleared}")

    out = {
        "spec": "research/studies/vwap-dist-low-10d-drift-h118-prospective-spec.md",
        "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON_DAYS,
        "bin_edges_frozen_from_discovery": [float(x) if np.isfinite(x) else None for x in bin_edges],
        "discovery_slice_result_reference": discovery_result,
        "points_result": points_result,
        "r_multiple_result": r_result,
        "verdict": verdict,
        "full_promotion_bar_cleared": full_promotion_bar_cleared,
    }
    out_path = DATA_DIR / "study_vwap_dist_low_10d_drift_h118_prospective_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

    status = "VALIDATION CANDIDATE" if full_promotion_bar_cleared else "REJECTED"
    notes = (
        f"H118 prospective, frozen spec "
        f"research/studies/vwap-dist-low-10d-drift-h118-prospective-spec.md. Single "
        f"pre-registered Validation-slice test (Discovery n=554 mean_r=0.617 "
        f"ci_90=[0.453,0.785]). Bucket edges frozen from Discovery. Validation n={n_r}, "
        f"mean_r={r_result.get('mean_r_multiple_net')}, ci_90={r_result.get('ci_90')}. "
        f"Verdict: {verdict}. Full promotion bar cleared: {full_promotion_bar_cleared}. "
        f"Full: data/study_vwap_dist_low_10d_drift_h118_prospective_results.json."
    )
    log_hypothesis(
        strategy_name="vwap_dist_low_10d_drift_h118_prospective",
        strategy_origin="derivative",
        parameters={
            "n": n_r,
            "mean_r_multiple_net": r_result.get("mean_r_multiple_net"),
            "ci_90": r_result.get("ci_90"),
            "statistically_credible": r_result.get("statistically_credible"),
            "economically_meaningful": r_result.get("economically_meaningful"),
            "full_promotion_bar_cleared": full_promotion_bar_cleared,
        },
        data_slice_used="validation",
        trade_count=n_r,
        strategy_status=status,
        notes=notes,
    )
    print("\nLogged to research/ledger/hypotheses.jsonl.")


if __name__ == "__main__":
    main()
