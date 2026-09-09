"""
study_vwap_dist_low_10d_drift_h118.py
========================================

H118 -- frozen spec: research/studies/vwap-dist-low-10d-drift-h118-spec.md.
Live candidate from Scan 002 (src/market_behavior_discovery_scan_002.py),
survived chronological split-sample and both regime cuts
(src/scan_002_regime_split_check.py). Long, time-based 10d exit, no
stop/target, mid... low-tercile vwap_dist_vs_atr.

HOW TO RUN:
    python3 src/study_vwap_dist_low_10d_drift_h118.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from backtest import ROUND_TRIP_COST_POINTS
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from research_ledger import log_hypothesis

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
HORIZON_DAYS = 10
VAR, BUCKET = "vwap_dist_vs_atr", "low"
BUCKET_LABELS = ["low", "mid", "high"]
MIN_ECONOMIC_R = 0.05
MIN_PROSPECTIVE_N = 30


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


def compute_bin_edges(states_reset):
    full_series = states_reset[VAR]
    valid = full_series.notna()
    edges = np.unique(np.nanpercentile(full_series[valid], [100 / 3, 200 / 3]))
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = BUCKET_LABELS[: len(bin_edges) - 1]
    return bin_edges, labels


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
    print("=" * 78)
    print("H118: VWAP-DIST-LOW, 10-DAY DRIFT, LONG, TIME-BASED EXIT")
    print("=" * 78)
    print("\nFrozen spec: research/studies/vwap-dist-low-10d-drift-h118-spec.md\n")

    df, is_synthetic = load_price_data(context="study_vwap_dist_low_10d_drift_h118.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(discovery), discovery)
    states_reset = states.reset_index()

    bin_edges, labels = compute_bin_edges(states_reset)
    if BUCKET not in labels:
        print(f"ABORT: bucket {BUCKET!r} not present in frozen edges {bin_edges}.")
        return

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
        verdict = "DISCOVERY_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN_FOR_PROSPECTIVE"
    else:
        verdict = "DISCOVERY_FAIL"

    print(f"\nPoints result: {points_result}")
    print(f"R-multiple result: {r_result}")
    print(f"Verdict: {verdict}")

    out = {
        "spec": "research/studies/vwap-dist-low-10d-drift-h118-spec.md",
        "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON_DAYS,
        "bin_edges": [float(x) if np.isfinite(x) else None for x in bin_edges],
        "points_result": points_result,
        "r_multiple_result": r_result,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_vwap_dist_low_10d_drift_h118_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

    status = "PROMISING" if verdict == "DISCOVERY_PASS" else "REJECTED"
    notes = (
        f"H118, frozen spec research/studies/vwap-dist-low-10d-drift-h118-spec.md. Live Scan 002 "
        f"candidate, survived chronological split-sample AND both volatility- and trend-regime "
        f"cuts (cleanest regime result of any Discovery Engine candidate so far), rediscovery "
        f"check confirms near-zero correlation with existing predictors (genuinely novel). Long, "
        f"time-based 10d exit, no stop/target. Discovery-slice only. n={n}, "
        f"mean_r={r_result.get('mean_r_multiple_net')}, ci_90={r_result.get('ci_90')}. "
        f"Verdict: {verdict}. Full: data/study_vwap_dist_low_10d_drift_h118_results.json."
    )
    log_hypothesis(
        strategy_name="vwap_dist_low_10d_drift_h118",
        strategy_origin="data_discovered",
        parameters={
            "n": n,
            "mean_r_multiple_net": r_result.get("mean_r_multiple_net"),
            "ci_90": r_result.get("ci_90"),
            "statistically_credible": r_result.get("statistically_credible"),
            "economically_meaningful": r_result.get("economically_meaningful"),
        },
        data_slice_used="discovery",
        trade_count=n,
        strategy_status=status,
        notes=notes,
    )
    print("\nLogged to research/ledger/hypotheses.jsonl.")


if __name__ == "__main__":
    main()
