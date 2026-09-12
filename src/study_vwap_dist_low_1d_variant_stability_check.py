"""
study_vwap_dist_low_1d_variant_stability_check.py
====================================================

STATISTICAL AGENT input for vwap_dist_vs_atr/LOW, 1-day variant
(research/studies/vwap-dist-low-1d-variant-spec.md). Chronological
split-sample + volatility-regime + trend-regime robustness, mirroring
H118's own checks (src/scan_002_regime_split_check.py) but using the
FROZEN candidate-script R convention (per-trade entry-day ATR14
normalization, no baseline subtraction) for consistency with this
variant's own frozen spec and with H118's canonical ledger number --
NOT the Scan 002 sweep's screening approximation (avg-ATR-normalized
effect-vs-baseline), which this session found is a materially
different metric (see the spec doc's addendum). Discovery-slice only.
Diagnostic -- does not itself log a new ledger row.

HOW TO RUN:
    python3 src/study_vwap_dist_low_1d_variant_stability_check.py
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
HORIZON_DAYS = 1
VAR, BUCKET = "vwap_dist_vs_atr", "low"
BIN_EDGES = [-np.inf, -0.0460, 0.1471, np.inf]  # frozen, H118's own edges
LABELS = ["low", "mid", "high"]
TREND_LOOKBACK_DAYS = 60


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    if len(arr) < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    idx_pool = np.arange(len(arr))
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=len(arr), replace=True)
        means[i] = arr[idx].mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def score_slice(states_slice):
    states_slice = states_slice.reset_index(drop=True)
    close = states_slice["Close"]
    atr = states_slice["atr14"]
    bucket_labels = pd.cut(states_slice[VAR], bins=BIN_EDGES, labels=LABELS, duplicates="drop")
    r_multiples = []
    for i in range(len(states_slice)):
        b = bucket_labels.iloc[i]
        if not (pd.notna(b) and str(b) == BUCKET):
            continue
        j = i + HORIZON_DAYS
        if j >= len(states_slice):
            continue
        entry_close, exit_close, entry_atr = close.iloc[i], close.iloc[j], atr.iloc[i]
        if entry_close <= 0 or pd.isna(entry_atr) or entry_atr <= 0:
            continue
        net = float(exit_close - entry_close) - ROUND_TRIP_COST_POINTS
        r_multiples.append(net / float(entry_atr))
    n = len(r_multiples)
    if n < 15:
        return {"n": n, "insufficient": True}
    arr = np.array(r_multiples)
    ci = bootstrap_mean_ci(arr)
    return {
        "n": n, "insufficient": False, "mean_r": float(arr.mean()), "ci_90": list(ci),
        "credible": bool(ci[0] > 0), "sign": int(np.sign(arr.mean())),
    }


def main():
    print("=" * 78)
    print("STATISTICAL AGENT INPUT -- vwap_dist_vs_atr/LOW 1d variant stability")
    print("=" * 78)
    df, is_synthetic = load_price_data(context="study_vwap_dist_low_1d_variant_stability_check.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(discovery), discovery).reset_index()

    full = score_slice(states)
    print(f"\nFull Discovery slice: {full}")

    mid = len(states) // 2
    first_half = score_slice(states.iloc[:mid])
    second_half = score_slice(states.iloc[mid:])
    print(f"\nChronological split-sample:")
    print(f"  First half:  {first_half}")
    print(f"  Second half: {second_half}")

    atr_median = float(states["atr14"].dropna().median())
    low_vol = score_slice(states[states["atr14"] <= atr_median])
    high_vol = score_slice(states[states["atr14"] > atr_median])
    print(f"\nVolatility regime split (ATR14 vs its own median {atr_median:.2f}):")
    print(f"  Low-vol:  {low_vol}")
    print(f"  High-vol: {high_vol}")

    trailing_trend = states["Close"].pct_change(TREND_LOOKBACK_DAYS).shift(1)
    uptrend = score_slice(states[trailing_trend > 0])
    downtrend = score_slice(states[trailing_trend <= 0])
    print(f"\nTrend regime split (trailing {TREND_LOOKBACK_DAYS}d return sign):")
    print(f"  Uptrend:   {uptrend}")
    print(f"  Downtrend: {downtrend}")

    def ok(r):
        return (not r.get("insufficient")) and r.get("credible") and r.get("sign", 0) > 0

    split_sample_stable = ok(first_half) and ok(second_half)
    vol_regime_stable = ok(low_vol) and ok(high_vol)
    trend_regime_stable = ok(uptrend) and ok(downtrend)

    print(f"\nSplit-sample stable (both halves credible, positive): {split_sample_stable}")
    print(f"Vol-regime stable (both regimes credible, positive):   {vol_regime_stable}")
    print(f"Trend-regime stable (both regimes credible, positive): {trend_regime_stable}")

    out = {
        "full": full, "first_half": first_half, "second_half": second_half,
        "low_vol": low_vol, "high_vol": high_vol, "uptrend": uptrend, "downtrend": downtrend,
        "split_sample_stable": split_sample_stable, "vol_regime_stable": vol_regime_stable,
        "trend_regime_stable": trend_regime_stable,
    }
    out_path = DATA_DIR / "study_vwap_dist_low_1d_variant_stability_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
