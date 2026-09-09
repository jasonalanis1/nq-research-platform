"""
study_location_in_range_low_uptrend_10d_drift_h117.py
=========================================================

H117 -- frozen spec:
research/studies/location-in-range-low-uptrend-10d-drift-h117-spec.md.
Second live Scan 001 candidate (distinct from H116, not subject to its
attempt count). Two-variable conditioned spec: location_in_range LOW
tercile AND trailing-60-day trend POSITIVE (uptrend regime) -- the
mechanism-consistent "buy-the-dip in an uptrend" framing found by
src/mechanism_agent_trend_check.py's regime split. Long-only, time-based
exit, no stop/target, same convention as H116.

HOW TO RUN:
    python3 src/study_location_in_range_low_uptrend_10d_drift_h117.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from backtest import ROUND_TRIP_COST_POINTS
from market_state_primitives import build_state_frame
from research_ledger import log_hypothesis

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
HORIZON_DAYS = 10
TREND_LOOKBACK_DAYS = 60
VAR, BUCKET = "location_in_range", "low"
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


def main():
    print("=" * 78)
    print("H117: LOCATION-IN-RANGE-LOW, UPTREND-CONDITIONED, 10-DAY DRIFT")
    print("=" * 78)
    print("\nFrozen spec: research/studies/location-in-range-low-uptrend-10d-drift-h117-spec.md\n")

    df, is_synthetic = load_price_data(context="study_location_in_range_low_uptrend_10d_drift_h117.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = build_state_frame(discovery)
    states_reset = states.reset_index()
    close = states_reset["Close"]
    atr = states_reset["atr14"]

    trailing_trend = close.pct_change(TREND_LOOKBACK_DAYS).shift(1)
    uptrend_mask = trailing_trend > 0

    full_series = states_reset[VAR]
    valid = full_series.notna()
    edges = np.unique(np.nanpercentile(full_series[valid], [100 / 3, 200 / 3]))
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = BUCKET_LABELS[: len(bin_edges) - 1]
    bucket_labels = pd.cut(full_series, bins=bin_edges, labels=labels, duplicates="drop")

    if BUCKET not in labels:
        print(f"ABORT: bucket {BUCKET!r} not present in frozen edges {bin_edges}.")
        return

    net_points = []
    r_multiples = []
    n_signals = 0
    for i in range(len(states_reset)):
        b = bucket_labels.iloc[i]
        if not (pd.notna(b) and str(b) == BUCKET):
            continue
        trend_val = uptrend_mask.iloc[i]
        if pd.isna(trend_val) or not bool(trend_val):
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
        gross = float(exit_close - entry_close)  # long
        net = gross - ROUND_TRIP_COST_POINTS
        net_points.append(net)
        r_multiples.append(net / float(entry_atr))

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
        verdict = "DISCOVERY_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN_FOR_PROSPECTIVE"
    else:
        verdict = "DISCOVERY_FAIL"

    print(f"\nPoints result: {points_result}")
    print(f"R-multiple result: {r_result}")
    print(f"Verdict: {verdict}")
    print(
        "\nNote: Discovery-slice pass only. Per the frozen spec, a DISCOVERY_PASS here does NOT "
        "mean promotion -- it proceeds to a genuine, unmodified Validation-slice prospective test."
    )

    out = {
        "spec": "research/studies/location-in-range-low-uptrend-10d-drift-h117-spec.md",
        "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON_DAYS,
        "trend_lookback_days": TREND_LOOKBACK_DAYS,
        "bin_edges": [float(x) if np.isfinite(x) else None for x in bin_edges],
        "points_result": points_result,
        "r_multiple_result": r_result,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_location_in_range_low_uptrend_10d_drift_h117_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

    status = "PROMISING" if verdict == "DISCOVERY_PASS" else "REJECTED"
    notes = (
        f"H117, frozen spec research/studies/location-in-range-low-uptrend-10d-drift-h117-spec.md. "
        f"Second live Scan 001 candidate (distinct from H116, own 2-attempt count). Two-variable "
        f"conditioned spec: location_in_range LOW tercile AND trailing-60d trend POSITIVE -- the "
        f"buy-the-dip-in-an-uptrend mechanism found by mechanism_agent_trend_check.py's regime "
        f"split (uptrend slice: +74.66pts vs. baseline, credible, cost-floor pass; downtrend slice: "
        f"-73.14pts vs. baseline, wrong direction -- hence the trend condition). Time-based exit, "
        f"long-only, no stop/target. Discovery-slice only. n={n}, "
        f"mean_r={r_result.get('mean_r_multiple_net')}, ci_90={r_result.get('ci_90')}. "
        f"Verdict: {verdict}. Full: data/study_location_in_range_low_uptrend_10d_drift_h117_results.json."
    )
    log_hypothesis(
        strategy_name="location_in_range_low_uptrend_10d_drift_h117",
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
