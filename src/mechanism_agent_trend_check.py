"""
mechanism_agent_trend_check.py
=================================

Mechanism Agent pass on the 2 candidates that survived both the
chronological split-sample check and the volatility-regime check
(research/infrastructure/agent-governance-structure.md standard: a
testable mechanism PREDICTION, not a post-hoc story).

CANDIDATE 1: overnight_range_vs_atr / mid / 10d
  Mechanism A (real, distinct): a "normal" (neither extreme-quiet nor
    extreme-wide) overnight session reflects balanced, confident
    overnight positioning that continues into the following sessions --
    a steady-state trending mechanism, independent of the broader
    market trend.
  Mechanism B (artifact/rediscovery): the "mid" bucket just correlates
    with the calm, sustained-uptrend stretches of the Discovery window,
    and the apparent return effect is really the secular uptrend
    showing up more cleanly when volatility is "normal" rather than at
    either extreme.
  DISTINGUISHING PREDICTION: if A is right, the effect should hold in
  BOTH uptrend and downtrend regimes (a steady-state mechanism doesn't
  care which way the steady state is going). If B is right, the effect
  should be concentrated in (or only exist during) uptrend regimes.

CANDIDATE 2: location_in_range / low / 10d
  Mechanism A (real, distinct): "buy-the-dip" value-buying -- price
  near a multi-week low attracts support flow BECAUSE the broader
  structure is an uptrend (dip = opportunity only when the trend
  above it is up).
  Mechanism B (real, distinct, different flavor): pure mean-reversion
  from a stretched short-term extreme, independent of broader trend
  direction (works the same during downtrends -- a low is a low).
  DISTINGUISHING PREDICTION: if A (uptrend-dependent) is right, the
  effect should be present or amplified during uptrend regimes and
  weak/absent/reversed during downtrend regimes. If B (pure mean-
  reversion) is right, the effect should hold in both regimes.

Both predictions are tested the same way: split Discovery by trailing
60-day trend direction (positive vs. negative 60-day return, frozen
threshold at zero -- no fitting), using the SAME frozen bucket edges
from Scan 001 (not refit per regime slice, same reasoning as the prior
two robustness passes). Still EXPLORATORY -- this narrows which
mechanism is more consistent with the data, it does not confirm either
one, and nothing here is promoted or frozen.

HOW TO RUN:
    python3 src/mechanism_agent_trend_check.py
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
TREND_LOOKBACK_DAYS = 60

CANDIDATES = [
    {"state_var": "overnight_range_vs_atr", "bucket": "mid", "horizon_days": 10,
     "mechanism_a": "steady-state (trend-independent)", "mechanism_b": "secular-uptrend artifact (trend-dependent)"},
    {"state_var": "location_in_range", "bucket": "low", "horizon_days": 10,
     "mechanism_a_label": "buy-the-dip (trend-dependent)", "mechanism_b_label": "pure mean-reversion (trend-independent)"},
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
    print("MECHANISM AGENT -- trend-regime distinguishing test (exploratory)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="mechanism_agent_trend_check.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = build_state_frame(discovery)
    states_reset = states.reset_index()
    close = states_reset["Close"]

    trailing_trend = close.pct_change(TREND_LOOKBACK_DAYS).shift(1)
    states_reset["trailing_trend"] = trailing_trend
    uptrend_mask = states_reset["trailing_trend"] > 0
    downtrend_mask = states_reset["trailing_trend"] <= 0
    uptrend = states_reset[uptrend_mask].reset_index(drop=True)
    downtrend = states_reset[downtrend_mask].reset_index(drop=True)
    print(f"\nDiscovery days: {len(states_reset)}  (trend = trailing {TREND_LOOKBACK_DAYS}-day return, sign only)")
    print(f"Uptrend-regime days: {len(uptrend)}   Downtrend-regime days: {len(downtrend)}\n")

    results = []
    for cand in CANDIDATES:
        var, bucket, horizon = cand["state_var"], cand["bucket"], cand["horizon_days"]
        full_series = states_reset[var]
        valid = full_series.notna()
        edges = np.unique(np.nanpercentile(full_series[valid], [100 / 3, 200 / 3]))
        bin_edges = [-np.inf] + list(edges) + [np.inf]
        labels = BUCKET_LABELS[: len(bin_edges) - 1]

        up_result = score_slice(uptrend, uptrend["Close"], var, bucket, horizon, bin_edges, labels)
        down_result = score_slice(downtrend, downtrend["Close"], var, bucket, horizon, bin_edges, labels)

        def sign_of(r):
            if r.get("insufficient"):
                return 0
            v = r["effect_vs_baseline_pts"]
            return 0 if np.isnan(v) else np.sign(v)

        both_present = bool(
            not up_result.get("insufficient") and not down_result.get("insufficient")
            and up_result["credible_vs_zero"] and up_result["clears_cost_floor"]
            and down_result["credible_vs_zero"] and down_result["clears_cost_floor"]
            and sign_of(up_result) == sign_of(down_result) and sign_of(up_result) != 0
        )
        uptrend_only = bool(
            not up_result.get("insufficient")
            and up_result["credible_vs_zero"] and up_result["clears_cost_floor"]
            and (down_result.get("insufficient") or not (down_result["credible_vs_zero"] and down_result["clears_cost_floor"]))
        )

        verdict = "TREND-INDEPENDENT (present in both regimes)" if both_present else (
            "TREND-DEPENDENT (uptrend-only or asymmetric)" if uptrend_only else "INCONCLUSIVE / regime-sensitive")

        row = {
            "state_var": var, "bucket": bucket, "horizon_days": horizon,
            "uptrend_regime": up_result, "downtrend_regime": down_result,
            "verdict": verdict,
        }
        results.append(row)

        print(f"{var} / {bucket} / h={horizon}d")
        for label, r in [("uptrend regime", up_result), ("downtrend regime", down_result)]:
            if r.get("insufficient"):
                print(f"  {label}: n={r['n']} -- insufficient")
                continue
            print(f"  {label}: n={r['n']:4d}  mean={r['mean_fwd_return_pts']:+7.2f}pts  "
                  f"vs_baseline={r['effect_vs_baseline_pts']:+7.2f}pts  atr_norm={r['atr_normalized_effect']:.4f}  "
                  f"credible={r['credible_vs_zero']}  cost_floor={r['clears_cost_floor']}")
        print(f"  VERDICT: {verdict}\n")

    out = {
        "analysis": "Mechanism Agent trend-regime distinguishing test (EXPLORATORY, not confirmation)",
        "spec": "research/infrastructure/agent-governance-structure.md",
        "trend_lookback_days": TREND_LOOKBACK_DAYS,
        "results": results,
        "note": (
            "Trend-independent presence in both up and down trailing-60-day regimes is evidence "
            "against a pure secular-uptrend-bleed-through explanation, and against a pure "
            "buy-the-dip-only-in-an-uptrend mechanism -- it does not by itself confirm any specific "
            "mechanism. Trend-dependent (uptrend-only) presence is evidence FOR a "
            "trend-context-dependent mechanism, and a reason for caution about generalizing the "
            "effect outside periods resembling Discovery's own dominant regime. Nothing here is "
            "promoted, frozen, or traded -- still exploratory, still requires a frozen monetization "
            "spec and genuine Validation-slice test before anything is a finding."
        ),
    }
    out_path = DATA_DIR / "mechanism_agent_trend_check_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Saved full results to {out_path}.")


if __name__ == "__main__":
    main()
