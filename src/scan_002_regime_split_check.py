"""
scan_002_regime_split_check.py
=================================

Second, independent robustness cut (volatility-regime split, not
chronological) on Scan 002's lone split-sample survivor,
vwap_dist_vs_atr/low/10d -- same methodology as Scan 001's
research_director_regime_check.py. Bucket edges frozen on the FULL
Discovery sample, not refit per regime slice.

HOW TO RUN:
    python3 src/scan_002_regime_split_check.py
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

VAR, BUCKET, HORIZON = "vwap_dist_vs_atr", "low", 10
TREND_LOOKBACK_DAYS = 60


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


def score_slice(slice_states, slice_close, bucket_labels_slice, bucket, horizon, avg_atr):
    fwd_bucket, fwd_baseline = [], []
    for i in range(len(slice_states)):
        r = forward_return(slice_close, i, horizon)
        if r is None:
            continue
        fwd_baseline.append(r)
        b = bucket_labels_slice.iloc[i]
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
    print("SCAN 002 -- REGIME-SPLIT + TREND-SPLIT CHECK on vwap_dist_vs_atr/low/10d")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="scan_002_regime_split_check.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(discovery), discovery)
    states_reset = states.reset_index()
    avg_atr = float(states_reset["atr14"].dropna().mean())

    full_series = states_reset[VAR]
    valid = full_series.notna()
    edges = np.unique(np.nanpercentile(full_series[valid], [100 / 3, 200 / 3]))
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = TERCILE_LABELS[: len(bin_edges) - 1]
    full_labels = pd.cut(full_series, bins=bin_edges, labels=labels, duplicates="drop")

    # --- Volatility regime split (trailing ATR14 vs. its own full-sample median) ---
    atr_median = float(states_reset["atr14"].dropna().median())
    low_vol_mask = states_reset["atr14"] <= atr_median
    high_vol_mask = states_reset["atr14"] > atr_median
    low_vol = states_reset[low_vol_mask].reset_index(drop=True)
    high_vol = states_reset[high_vol_mask].reset_index(drop=True)
    low_vol_labels = full_labels[low_vol_mask].reset_index(drop=True)
    high_vol_labels = full_labels[high_vol_mask].reset_index(drop=True)

    r_low_vol = score_slice(low_vol, low_vol["Close"], low_vol_labels, BUCKET, HORIZON, avg_atr)
    r_high_vol = score_slice(high_vol, high_vol["Close"], high_vol_labels, BUCKET, HORIZON, avg_atr)

    # --- Trend regime split (trailing 60d return sign) ---
    trailing_trend = states_reset["Close"].pct_change(TREND_LOOKBACK_DAYS).shift(1)
    uptrend_mask = trailing_trend > 0
    downtrend_mask = trailing_trend <= 0
    uptrend = states_reset[uptrend_mask].reset_index(drop=True)
    downtrend = states_reset[downtrend_mask].reset_index(drop=True)
    uptrend_labels = full_labels[uptrend_mask].reset_index(drop=True)
    downtrend_labels = full_labels[downtrend_mask].reset_index(drop=True)

    r_uptrend = score_slice(uptrend, uptrend["Close"], uptrend_labels, BUCKET, HORIZON, avg_atr)
    r_downtrend = score_slice(downtrend, downtrend["Close"], downtrend_labels, BUCKET, HORIZON, avg_atr)

    def sign_of(r):
        if r.get("insufficient"):
            return 0
        v = r["effect_vs_baseline_pts"]
        return 0 if np.isnan(v) else np.sign(v)

    vol_direction_consistent = bool(
        not r_low_vol.get("insufficient") and not r_high_vol.get("insufficient")
        and sign_of(r_low_vol) != 0 and sign_of(r_low_vol) == sign_of(r_high_vol)
    )
    vol_both_pass = bool(
        vol_direction_consistent
        and r_low_vol["credible_vs_zero"] and r_low_vol["clears_cost_floor"]
        and r_high_vol["credible_vs_zero"] and r_high_vol["clears_cost_floor"]
    )
    trend_direction_consistent = bool(
        not r_uptrend.get("insufficient") and not r_downtrend.get("insufficient")
        and sign_of(r_uptrend) != 0 and sign_of(r_uptrend) == sign_of(r_downtrend)
    )
    trend_both_pass = bool(
        trend_direction_consistent
        and r_uptrend["credible_vs_zero"] and r_uptrend["clears_cost_floor"]
        and r_downtrend["credible_vs_zero"] and r_downtrend["clears_cost_floor"]
    )

    print(f"\nvwap_dist_vs_atr / {BUCKET} / h={HORIZON}d  (bin_edges={bin_edges})")
    print(f"  full-sample median ATR14 (regime threshold): {atr_median:.2f} pts")
    for label, r in [("low-vol regime", r_low_vol), ("high-vol regime", r_high_vol),
                      ("uptrend regime", r_uptrend), ("downtrend regime", r_downtrend)]:
        if r.get("insufficient"):
            print(f"  {label}: n={r['n']} -- insufficient")
            continue
        print(f"  {label}: n={r['n']:4d}  mean={r['mean_fwd_return_pts']:+7.2f}pts  "
              f"vs_baseline={r['effect_vs_baseline_pts']:+7.2f}pts  atr_norm={r['atr_normalized_effect']:.4f}  "
              f"credible={r['credible_vs_zero']}  cost_floor={r['clears_cost_floor']}")
    print(f"\n  vol_direction_consistent={vol_direction_consistent}  vol_both_pass={vol_both_pass}")
    print(f"  trend_direction_consistent={trend_direction_consistent}  trend_both_pass={trend_both_pass}")

    overall_survives = vol_both_pass and trend_both_pass
    print(f"\n  OVERALL: survives BOTH regime cuts = {overall_survives}")

    out = {
        "analysis": "Scan 002 regime-split + trend-split check on vwap_dist_vs_atr/low/10d (EXPLORATORY)",
        "spec": "research/infrastructure/agent-governance-structure.md",
        "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON,
        "bin_edges": [float(x) if np.isfinite(x) else None for x in bin_edges],
        "atr_regime_threshold_median": atr_median,
        "low_vol_regime": r_low_vol, "high_vol_regime": r_high_vol,
        "uptrend_regime": r_uptrend, "downtrend_regime": r_downtrend,
        "vol_direction_consistent": vol_direction_consistent, "vol_both_pass": vol_both_pass,
        "trend_direction_consistent": trend_direction_consistent, "trend_both_pass": trend_both_pass,
        "survives_both_regime_cuts": overall_survives,
        "note": (
            "EXPLORATORY. If this candidate fails either cut, it is dropped/reclassified as a "
            "regime artifact, same discipline as location_in_range/high/10d in Scan 001. If it "
            "survives both, it still needs a testable mechanism prediction (why would closing "
            "well below session VWAP predict a POSITIVE 10-day forward return) before any frozen "
            "monetization spec -- and even then, Scan 001's 0-for-2 Validation track record means "
            "this is not treated as likely to promote."
        ),
    }
    out_path = DATA_DIR / "scan_002_regime_split_check_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
