"""
study_overnight_range_mid_10d_drift_h116.py
==============================================

H116 -- frozen spec:
research/studies/overnight-range-mid-10d-drift-h116-spec.md.
First monetization attempt for the Discovery Engine's strongest
surviving candidate: overnight_range_vs_atr (mid tercile) -> positive
10-trading-day forward return. Survived four independent exploratory
checks (chronological split-sample, volatility-regime split,
trend-regime split, separability vs. the known overnight-coil range
finding). Natural realization path per the frozen spec: TIME-BASED
EXIT, directional LONG, no stop/target (matches how the effect was
discovered and measured -- avoids the exit-design-mismatch trap from
H114/H115).

Entry: RTH reference close on a day whose overnight_range_vs_atr falls
in the MIDDLE tercile (frozen bucket edges, identical to Scan 001 and
every exploratory pass since -- not refit here).
Exit: RTH reference close 10 trading days later. No stop, no target.
Cost: one round-trip cost, applied once per trade.
Risk unit for R-multiple: entry-day ATR(14) (not a stop distance --
used only for the promotion bar's required units).

Discovery-slice only for this pass. This is hypothesis #1 (attempt 1
of 2) for this candidate behavior, per the project's 2-attempt limit.
A pass here does NOT mean promotion -- it means proceeding to a
genuine Validation-slice prospective test, unmodified.

HOW TO RUN:
    python3 src/study_overnight_range_mid_10d_drift_h116.py
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
VAR, BUCKET = "overnight_range_vs_atr", "mid"
BUCKET_LABELS = ["low", "mid", "high"]
MIN_ECONOMIC_R = 0.05
MIN_PROSPECTIVE_N = 30  # project-standard thin-sample floor, matches H114/H115 usage


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
    print("H116: OVERNIGHT-RANGE-MID 10-DAY DRIFT, LONG, TIME-BASED EXIT")
    print("=" * 78)
    print("\nFrozen spec: research/studies/overnight-range-mid-10d-drift-h116-spec.md\n")

    df, is_synthetic = load_price_data(context="study_overnight_range_mid_10d_drift_h116.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = build_state_frame(discovery)
    states_reset = states.reset_index()
    close = states_reset["Close"]
    atr = states_reset["atr14"]

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

    print(f"Signals (mid-tercile overnight_range_vs_atr days with valid {HORIZON_DAYS}-day exit): {n_signals}")
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
        "\nNote: this is a Discovery-slice pass only. Per the frozen spec and the project's "
        "Research Integrity Protocol, a DISCOVERY_PASS here does NOT mean promotion -- it means "
        "the candidate proceeds to a genuine, unmodified Validation-slice prospective test."
    )

    out = {
        "spec": "research/studies/overnight-range-mid-10d-drift-h116-spec.md",
        "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON_DAYS,
        "bin_edges": [float(x) if np.isfinite(x) else None for x in bin_edges],
        "points_result": points_result,
        "r_multiple_result": r_result,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_overnight_range_mid_10d_drift_h116_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

    status = "PROMISING" if verdict in ("DISCOVERY_PASS",) else "REJECTED"
    notes = (
        f"H116, frozen spec research/studies/overnight-range-mid-10d-drift-h116-spec.md. "
        f"First monetization attempt (1 of 2) for the Discovery Engine's strongest surviving "
        f"candidate (overnight_range_vs_atr mid tercile -> positive 10d forward return), which "
        f"survived chronological split-sample, volatility-regime, trend-regime, and separability "
        f"checks. Time-based exit, long-only, no stop/target -- natural realization path per the "
        f"frozen spec, chosen to avoid the exit-design-mismatch failure mode from H114/H115. "
        f"Discovery-slice only. n={n}, mean_r={r_result.get('mean_r_multiple_net')}, "
        f"ci_90={r_result.get('ci_90')}. Verdict: {verdict}. "
        f"Full: data/study_overnight_range_mid_10d_drift_h116_results.json."
    )
    log_hypothesis(
        strategy_name="overnight_range_mid_10d_drift_h116",
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
