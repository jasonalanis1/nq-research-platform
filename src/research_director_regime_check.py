"""
research_director_regime_check.py
====================================

Research Director's Candidate Triage pass on Scan 001's 3 split-sample
survivors (research/infrastructure/agent-governance-structure.md).
EXPLORATORY -- not confirmation. Splits Discovery by VOLATILITY REGIME
(trailing 20-day ATR(14) above/below its own full-sample median, a
different cut than the chronological first-half/second-half split
already run) to check whether each survivor's effect is a standalone
state effect or mostly driven by one volatility regime -- directly
targets the regime-contamination question raised against
overnight_range_vs_atr/mid/10d (same predictor as the validated
overnight-coil RANGE finding) and gives location_in_range a second,
independent robustness cut beyond the chronological split.

Bucket edges (state tercile) and the regime threshold are both frozen
on the FULL Discovery sample, not refit per regime slice, for the same
reason the chronological split-sample check froze them: refitting on a
sub-slice would let the slice curve-fit its own boundaries.

HOW TO RUN:
    python3 src/research_director_regime_check.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_NORMALIZED_FLOOR = 0.05
BUCKET_LABELS = ["low", "mid", "high"]

SURVIVORS = [
    {"state_var": "location_in_range", "bucket": "high", "horizon_days": 10, "triage": "A"},
    {"state_var": "overnight_range_vs_atr", "bucket": "mid", "horizon_days": 10, "triage": "B/C"},
    {"state_var": "location_in_range", "bucket": "low", "horizon_days": 10, "triage": "A"},
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


def score_slice(slice_states, slice_close, var, bucket, horizon, bin_edges, labels):
    bucket_labels = pd.cut(slice_states[var], bins=bin_edges, labels=labels, duplicates="drop")
    slice_atr = float(slice_states["atr14"].dropna().mean())
    fwd_bucket, fwd_baseline = [], []
    for i in range(len(slice_states)):
        r = forward_return(slice_close, i, horizon)
        if r is None:
            continue
        fwd_baseline.append(r)
        b = bucket_labels.iloc[i]
        if pd.notna(b) and str(b) == bucket:
            fwd_bucket.append(r)
    n = len(fwd_bucket)
    baseline_mean = float(np.mean(fwd_baseline)) if fwd_baseline else float("nan")
    if n < 15:
        return {"n": n, "insufficient": True}
    mean_r = float(np.mean(fwd_bucket))
    ci = bootstrap_mean_ci(fwd_bucket)
    effect = mean_r - baseline_mean
    atr_norm = abs(effect) / slice_atr if slice_atr > 0 else float("nan")
    return {
        "n": n, "insufficient": False, "mean_fwd_return_pts": mean_r,
        "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": effect,
        "atr_normalized_effect": atr_norm, "ci_90": list(ci),
        "credible_vs_zero": bool(ci[0] > 0 or ci[1] < 0),
        "clears_cost_floor": bool(atr_norm >= ATR_NORMALIZED_FLOOR),
    }


def main():
    print("=" * 78)
    print("RESEARCH DIRECTOR -- REGIME-SPLIT CHECK on Scan 001 survivors (exploratory)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="research_director_regime_check.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = build_state_frame(discovery)
    states_reset = states.reset_index()
    close = states_reset["Close"]

    atr_median = float(states_reset["atr14"].dropna().median())
    print(f"\nDiscovery days: {len(states_reset)}   full-sample median ATR(14) (regime threshold): {atr_median:.2f} pts")

    low_vol_mask = states_reset["atr14"] <= atr_median
    high_vol_mask = states_reset["atr14"] > atr_median
    low_vol = states_reset[low_vol_mask].reset_index(drop=True)
    high_vol = states_reset[high_vol_mask].reset_index(drop=True)
    print(f"Low-vol-regime days: {len(low_vol)}   High-vol-regime days: {len(high_vol)}\n")

    results = []
    for cand in SURVIVORS:
        var, bucket, horizon = cand["state_var"], cand["bucket"], cand["horizon_days"]
        full_series = states_reset[var]
        valid = full_series.notna()
        edges = np.unique(np.nanpercentile(full_series[valid], [100 / 3, 200 / 3]))
        bin_edges = [-np.inf] + list(edges) + [np.inf]
        labels = BUCKET_LABELS[: len(bin_edges) - 1]

        low_result = score_slice(low_vol, low_vol["Close"], var, bucket, horizon, bin_edges, labels)
        high_result = score_slice(high_vol, high_vol["Close"], var, bucket, horizon, bin_edges, labels)

        def sign_of(r):
            if r.get("insufficient"):
                return 0
            v = r["effect_vs_baseline_pts"]
            return 0 if np.isnan(v) else np.sign(v)

        direction_consistent = bool(
            not low_result.get("insufficient") and not high_result.get("insufficient")
            and sign_of(low_result) != 0 and sign_of(low_result) == sign_of(high_result)
        )
        one_regime_only = bool(
            not low_result.get("insufficient") and not high_result.get("insufficient")
            and (low_result["credible_vs_zero"] and low_result["clears_cost_floor"])
            != (high_result["credible_vs_zero"] and high_result["clears_cost_floor"])
        )

        row = {
            "state_var": var, "bucket": bucket, "horizon_days": horizon,
            "prior_triage": cand["triage"],
            "low_vol_regime": low_result, "high_vol_regime": high_result,
            "direction_consistent_across_regimes": direction_consistent,
            "regime_dependent_only_one_side": one_regime_only,
        }
        results.append(row)

        print(f"{var} / {bucket} / h={horizon}d  (prior triage: {cand['triage']})")
        for label, r in [("low-vol regime", low_result), ("high-vol regime", high_result)]:
            if r.get("insufficient"):
                print(f"  {label}: n={r['n']} -- insufficient")
                continue
            print(f"  {label}: n={r['n']:4d}  mean={r['mean_fwd_return_pts']:+7.2f}pts  "
                  f"vs_baseline={r['effect_vs_baseline_pts']:+7.2f}pts  atr_norm={r['atr_normalized_effect']:.4f}  "
                  f"credible={r['credible_vs_zero']}  cost_floor={r['clears_cost_floor']}")
        print(f"  direction_consistent_across_regimes={direction_consistent}  "
              f"regime_dependent_only_one_side={one_regime_only}\n")

    out = {
        "analysis": "Research Director regime-split check on Scan 001 split-sample survivors (EXPLORATORY)",
        "spec": "research/infrastructure/agent-governance-structure.md",
        "regime_threshold_full_sample_median_atr14": atr_median,
        "results": results,
        "note": (
            "Regime split (low/high trailing ATR14 vs. full-sample median) is a second, "
            "independent robustness cut beyond the chronological split-sample check, aimed "
            "specifically at the regime-contamination question for overnight_range_vs_atr/mid "
            "(same predictor as the validated overnight-coil RANGE finding) and as a second "
            "check on location_in_range. Still exploratory -- no candidate is promoted or "
            "frozen by this analysis alone."
        ),
    }
    out_path = DATA_DIR / "research_director_regime_check_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Saved full results to {out_path}.")


if __name__ == "__main__":
    main()
