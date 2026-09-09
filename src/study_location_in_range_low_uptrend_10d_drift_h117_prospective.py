"""
study_location_in_range_low_uptrend_10d_drift_h117_prospective.py
=====================================================================

H117 -- frozen spec:
research/studies/location-in-range-low-uptrend-10d-drift-h117-prospective-spec.md.
Single pre-registered Validation-slice prospective test of H117.
Bucket edges and trend threshold frozen from Discovery -- nothing
refit here.

HOW TO RUN:
    python3 src/study_location_in_range_low_uptrend_10d_drift_h117_prospective.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data, get_validation_data
from backtest import ROUND_TRIP_COST_POINTS
from market_state_primitives import build_state_frame
from research_ledger import log_hypothesis
from study_location_in_range_low_uptrend_10d_drift_h117 import (
    VAR, BUCKET, BUCKET_LABELS, HORIZON_DAYS, TREND_LOOKBACK_DAYS,
    MIN_PROSPECTIVE_N, bootstrap_mean_ci, analyze_r_multiples,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main():
    print("=" * 78)
    print("H117 PROSPECTIVE: LOCATION-IN-RANGE-LOW, UPTREND-CONDITIONED, VALIDATION SLICE")
    print("=" * 78)
    print("\nFrozen spec: research/studies/location-in-range-low-uptrend-10d-drift-h117-prospective-spec.md\n")

    df, is_synthetic = load_price_data(context="study_location_in_range_low_uptrend_10d_drift_h117_prospective.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    # Bucket edges frozen on the FULL DISCOVERY sample -- identical to the Discovery-slice script.
    discovery = get_discovery_data(df)
    disc_states = build_state_frame(discovery).reset_index()
    disc_series = disc_states[VAR]
    disc_valid = disc_series.notna()
    edges = np.unique(np.nanpercentile(disc_series[disc_valid], [100 / 3, 200 / 3]))
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = BUCKET_LABELS[: len(bin_edges) - 1]
    if BUCKET not in labels:
        print(f"ABORT: bucket {BUCKET!r} not present in frozen edges {bin_edges}.")
        return

    validation = get_validation_data(df)
    val_states = build_state_frame(validation).reset_index()
    close = val_states["Close"]
    atr = val_states["atr14"]
    trailing_trend = close.pct_change(TREND_LOOKBACK_DAYS).shift(1)
    uptrend_mask = trailing_trend > 0

    bucket_labels = pd.cut(val_states[VAR], bins=bin_edges, labels=labels, duplicates="drop")

    net_points = []
    r_multiples = []
    n_signals = 0
    for i in range(len(val_states)):
        b = bucket_labels.iloc[i]
        if not (pd.notna(b) and str(b) == BUCKET):
            continue
        trend_val = uptrend_mask.iloc[i]
        if pd.isna(trend_val) or not bool(trend_val):
            continue
        j = i + HORIZON_DAYS
        if j >= len(val_states):
            continue
        entry_close = close.iloc[i]
        exit_close = close.iloc[j]
        entry_atr = atr.iloc[i]
        if entry_close <= 0 or pd.isna(entry_atr) or entry_atr <= 0:
            continue
        n_signals += 1
        gross = float(exit_close - entry_close)  # long
        net = gross - ROUND_TRIP_COST_POINTS
        net_points.append(net)
        r_multiples.append(net / float(entry_atr))

    print(f"Validation days: {len(val_states)}   (bucket edges frozen from Discovery: {bin_edges})")
    print(f"Signals (low-tercile location_in_range AND uptrend-regime days, valid {HORIZON_DAYS}-day exit): {n_signals}")
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
        verdict = "PROSPECTIVE_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN"
    else:
        verdict = "PROSPECTIVE_FAIL"

    discovery_result = {
        "n": 342, "mean_r_multiple_net": 0.45061770374107385,
        "ci_90": [0.22327746512733654, 0.679320553616318],
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
        "spec": "research/studies/location-in-range-low-uptrend-10d-drift-h117-prospective-spec.md",
        "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON_DAYS,
        "trend_lookback_days": TREND_LOOKBACK_DAYS,
        "bin_edges_frozen_from_discovery": [float(x) if np.isfinite(x) else None for x in bin_edges],
        "discovery_slice_result_reference": discovery_result,
        "points_result": points_result,
        "r_multiple_result": r_result,
        "verdict": verdict,
        "full_promotion_bar_cleared": full_promotion_bar_cleared,
    }
    out_path = DATA_DIR / "study_location_in_range_low_uptrend_10d_drift_h117_prospective_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

    status = "VALIDATED" if full_promotion_bar_cleared else "REJECTED"
    notes = (
        f"H117 prospective, frozen spec "
        f"research/studies/location-in-range-low-uptrend-10d-drift-h117-prospective-spec.md. "
        f"Single pre-registered Validation-slice test of the Discovery-slice pass (Discovery "
        f"n=342 mean_r=0.451 ci_90=[0.223,0.679]). Bucket edges and trend threshold frozen from "
        f"Discovery, unmodified. Validation n={n}, mean_r={r_result.get('mean_r_multiple_net')}, "
        f"ci_90={r_result.get('ci_90')}. Verdict: {verdict}. Full promotion bar cleared: "
        f"{full_promotion_bar_cleared}. Full: "
        f"data/study_location_in_range_low_uptrend_10d_drift_h117_prospective_results.json."
    )
    log_hypothesis(
        strategy_name="location_in_range_low_uptrend_10d_drift_h117_prospective",
        strategy_origin="derivative",
        parameters={
            "n": n,
            "mean_r_multiple_net": r_result.get("mean_r_multiple_net"),
            "ci_90": r_result.get("ci_90"),
            "statistically_credible": r_result.get("statistically_credible"),
            "economically_meaningful": r_result.get("economically_meaningful"),
            "full_promotion_bar_cleared": full_promotion_bar_cleared,
        },
        data_slice_used="validation",
        trade_count=n,
        strategy_status=status,
        notes=notes,
    )
    print("\nLogged to research/ledger/hypotheses.jsonl.")


if __name__ == "__main__":
    main()
