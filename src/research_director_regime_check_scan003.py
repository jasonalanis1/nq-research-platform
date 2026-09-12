"""
research_director_regime_check_scan003.py
============================================

Research Director's Statistical-stage robustness pass on Scan 003's one
split-sample survivor (zn_level_vs_trailing / low tercile / 10-day
horizon -- see discovery_scan_003_split_sample_robustness.py and
docs/BACKLOG.md's "Discovery Engine Scan 003" entry). EXPLORATORY --
not confirmation. Same method as research_director_regime_check.py
(Scan 001's version): splits Discovery by VOLATILITY REGIME (trailing
20-day ATR(14) above/below its own full-sample median) rather than
chronologically, to check whether the effect is a standalone state
effect or mostly driven by one volatility regime -- a different cut
than the chronological split already run, targeting a different
contamination question.

Bucket edges (state tercile) and the regime threshold are both frozen
on the FULL Discovery sample, not refit per regime slice, for the same
reason the chronological split-sample check froze them.

HOW TO RUN:
    PYTHONPATH=src python3 src/research_director_regime_check_scan003.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_state_primitives_v3 import extend_state_frame_v3

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_NORMALIZED_FLOOR = 0.05
BUCKET_LABELS = ["low", "mid", "high"]

CANDIDATE = {"state_var": "zn_level_vs_trailing", "bucket": "low", "horizon_days": 10}


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
    print("RESEARCH DIRECTOR -- REGIME-SPLIT CHECK on Scan 003 survivor (exploratory)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="research_director_regime_check_scan003.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame_v3(extend_state_frame(build_state_frame(discovery), discovery))
    states_reset = states.reset_index()

    atr_median = float(states_reset["atr14"].dropna().median())
    print(f"\nDiscovery days: {len(states_reset)}   full-sample median ATR(14) (regime threshold): {atr_median:.2f} pts")

    low_vol_mask = states_reset["atr14"] <= atr_median
    high_vol_mask = states_reset["atr14"] > atr_median
    low_vol = states_reset[low_vol_mask].reset_index(drop=True)
    high_vol = states_reset[high_vol_mask].reset_index(drop=True)
    print(f"Low-vol-regime days: {len(low_vol)}   High-vol-regime days: {len(high_vol)}\n")

    var, bucket, horizon = CANDIDATE["state_var"], CANDIDATE["bucket"], CANDIDATE["horizon_days"]
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
        sign_of(low_result) != 0 and sign_of(low_result) == sign_of(high_result)
    )
    one_regime_only = bool(
        (low_result["credible_vs_zero"] and low_result["clears_cost_floor"])
        != (high_result["credible_vs_zero"] and high_result["clears_cost_floor"])
    )

    print(f"{var}/{bucket}/h={horizon}d:")
    print(f"  low-vol regime : n={low_result['n']:4d}  effect_vs_baseline={low_result['effect_vs_baseline_pts']:+7.2f}pts  "
          f"atr_norm={low_result['atr_normalized_effect']:.4f}  credible={low_result['credible_vs_zero']}  cost_ok={low_result['clears_cost_floor']}")
    print(f"  high-vol regime: n={high_result['n']:4d}  effect_vs_baseline={high_result['effect_vs_baseline_pts']:+7.2f}pts  "
          f"atr_norm={high_result['atr_normalized_effect']:.4f}  credible={high_result['credible_vs_zero']}  cost_ok={high_result['clears_cost_floor']}")
    print(f"  direction_consistent_across_regimes={direction_consistent}  regime_dependent_only_one_side={one_regime_only}")

    out = {
        "check": "research_director_regime_check_scan003.py",
        "status": "EXPLORATORY -- second independent robustness cut (volatility regime, not chronological). Not logged to the ledger.",
        "candidate": CANDIDATE,
        "atr_median_threshold": atr_median,
        "low_vol_regime": low_result,
        "high_vol_regime": high_result,
        "direction_consistent_across_regimes": direction_consistent,
        "regime_dependent_only_one_side": one_regime_only,
    }
    out_path = DATA_DIR / "research_director_regime_check_scan003_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nFull results written to {out_path}")


if __name__ == "__main__":
    main()
