"""
scan_002_split_sample_robustness.py
======================================

Split-sample robustness screen (EXPLORATORY, not confirmation -- same
standing methodology as Scan 001's screen) on Scan 002's top 4 deduped
candidates (best horizon per state_var/bucket pair): vxn_level_vs_trailing
/low, vwap_dist_vs_atr/low, volume_vs_expected/low,
directional_persistence_quintile/q2. Bucket edges frozen on the FULL
Discovery sample, never refit per half.

HOW TO RUN:
    python3 src/scan_002_split_sample_robustness.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_NORMALIZED_FLOOR = 0.05
TERCILE_LABELS = ["low", "mid", "high"]
QUINTILE_LABELS = ["q1", "q2", "q3", "q4", "q5"]

CANDIDATES = [
    {"state_var": "vxn_level_vs_trailing", "bucket": "low", "horizon_days": 10, "n_buckets": 3},
    {"state_var": "vwap_dist_vs_atr", "bucket": "low", "horizon_days": 10, "n_buckets": 3},
    {"state_var": "volume_vs_expected", "bucket": "low", "horizon_days": 10, "n_buckets": 3},
    {"state_var": "directional_persistence_quintile", "bucket": "q2", "horizon_days": 10, "n_buckets": 5},
]


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        s = rng.choice(v, size=len(v), replace=True)
        means[i] = s.mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def forward_return(close_series, i, horizon):
    if i + horizon >= len(close_series):
        return None
    c0, c1 = close_series.iloc[i], close_series.iloc[i + horizon]
    if c0 <= 0:
        return None
    return float(c1 - c0)


def freeze_bucket_labels(full_series, n_buckets):
    if n_buckets == 5:
        return full_series.map(lambda x: QUINTILE_LABELS[int(x)] if pd.notna(x) else np.nan)
    valid = full_series.notna()
    pct = [100 / n_buckets * k for k in range(1, n_buckets)]
    edges = np.unique(np.nanpercentile(full_series[valid], pct))
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = TERCILE_LABELS[: len(bin_edges) - 1]
    return pd.cut(full_series, bins=bin_edges, labels=labels, duplicates="drop")


def score_half(half_states, half_close, bucket_labels_half, bucket, horizon, avg_atr):
    fwd_bucket, fwd_baseline = [], []
    for i in range(len(half_states)):
        r = forward_return(half_close, i, horizon)
        if r is None:
            continue
        fwd_baseline.append(r)
        b = bucket_labels_half.iloc[i]
        if pd.notna(b) and str(b) == bucket:
            fwd_bucket.append(r)
    n = len(fwd_bucket)
    baseline_mean = float(np.mean(fwd_baseline)) if fwd_baseline else float("nan")
    if n < 15:
        return {"n": n, "insufficient": True}
    mean_r = float(np.mean(fwd_bucket))
    ci = bootstrap_mean_ci(fwd_bucket)
    effect = mean_r - baseline_mean
    atr_norm = abs(effect) / avg_atr if avg_atr > 0 else float("nan")
    return {
        "n": n, "insufficient": False, "mean_fwd_return_pts": mean_r,
        "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": effect,
        "atr_normalized_effect": atr_norm, "ci_90": list(ci),
        "credible_vs_zero": bool(ci[0] > 0 or ci[1] < 0),
        "clears_cost_floor": bool(atr_norm >= ATR_NORMALIZED_FLOOR),
    }


def main():
    print("=" * 78)
    print("SCAN 002 SPLIT-SAMPLE ROBUSTNESS SCREEN (exploratory)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="scan_002_split_sample_robustness.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(discovery), discovery)
    states_reset = states.reset_index()
    avg_atr = float(states_reset["atr14"].dropna().mean())

    mid = len(states_reset) // 2
    first_half = states_reset.iloc[:mid].reset_index(drop=True)
    second_half = states_reset.iloc[mid:].reset_index(drop=True)
    print(f"\nFirst half: {first_half['date'].iloc[0]} -> {first_half['date'].iloc[-1]}  n={len(first_half)}")
    print(f"Second half: {second_half['date'].iloc[0]} -> {second_half['date'].iloc[-1]}  n={len(second_half)}\n")

    results = []
    for cand in CANDIDATES:
        var, bucket, horizon, n_buckets = cand["state_var"], cand["bucket"], cand["horizon_days"], cand["n_buckets"]
        full_labels = freeze_bucket_labels(states_reset[var], n_buckets)
        first_labels = full_labels.iloc[:mid].reset_index(drop=True)
        second_labels = full_labels.iloc[mid:].reset_index(drop=True)

        r1 = score_half(first_half, first_half["Close"], first_labels, bucket, horizon, avg_atr)
        r2 = score_half(second_half, second_half["Close"], second_labels, bucket, horizon, avg_atr)

        def sign_of(r):
            if r.get("insufficient"):
                return 0
            v = r["effect_vs_baseline_pts"]
            return 0 if np.isnan(v) else np.sign(v)

        direction_consistent = bool(
            not r1.get("insufficient") and not r2.get("insufficient")
            and sign_of(r1) != 0 and sign_of(r1) == sign_of(r2)
        )
        survives_both = bool(
            direction_consistent
            and r1["credible_vs_zero"] and r1["clears_cost_floor"]
            and r2["credible_vs_zero"] and r2["clears_cost_floor"]
        )
        mag_ratio = None
        if direction_consistent and r1.get("effect_vs_baseline_pts") not in (None, 0):
            mag_ratio = r2["effect_vs_baseline_pts"] / r1["effect_vs_baseline_pts"]

        row = {
            "state_var": var, "bucket": bucket, "horizon_days": horizon,
            "first_half": r1, "second_half": r2,
            "direction_consistent": direction_consistent,
            "magnitude_ratio_2nd_over_1st": mag_ratio,
            "survives_both_halves": survives_both,
        }
        results.append(row)

        print(f"{var} / {bucket} / h={horizon}d")
        for label, r in [("1st half", r1), ("2nd half", r2)]:
            if r.get("insufficient"):
                print(f"  {label}: n={r['n']} -- insufficient")
                continue
            print(f"  {label}: n={r['n']:4d}  mean={r['mean_fwd_return_pts']:+7.2f}pts  "
                  f"vs_baseline={r['effect_vs_baseline_pts']:+7.2f}pts  atr_norm={r['atr_normalized_effect']:.4f}  "
                  f"credible={r['credible_vs_zero']}  cost_floor={r['clears_cost_floor']}")
        print(f"  direction_consistent={direction_consistent}  survives_both_halves={survives_both}\n")

    n_survivors = sum(1 for r in results if r["survives_both_halves"])
    print(f"Observed: {n_survivors} of {len(CANDIDATES)} candidates survive split-sample.")

    out = {
        "analysis": "Scan 002 split-sample robustness screen (EXPLORATORY)",
        "spec": "research/infrastructure/agent-governance-structure.md",
        "candidates_screened": len(CANDIDATES),
        "survivors": n_survivors,
        "results": results,
        "note": (
            "EXPLORATORY, not confirmation -- candidates were selected on the full sample the "
            "halves come from. Bucket edges/quintile assignment frozen on the full sample, not "
            "refit per half. A survivor still needs a regime-split + mechanism pass before any "
            "frozen monetization spec, same discipline as Scan 001 (whose 2 survivors of this "
            "same screen both then failed Validation)."
        ),
    }
    out_path = DATA_DIR / "scan_002_split_sample_robustness_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
