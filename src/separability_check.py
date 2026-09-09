"""
separability_check.py
========================

Tests whether overnight_range_vs_atr/mid/10d's RETURN effect is
separable from the already-validated overnight-coil RANGE finding on
the same predictor, or whether it's a statistical byproduct of that
same range/volatility relationship (e.g. skew in the return
distribution induced by the range outcome itself).

METHOD: partial regression. forward_10d_return ~ mid_bucket_dummy +
forward_10d_range, on the full Discovery sample. If the mid_bucket
coefficient stays credibly nonzero (bootstrap CI) after controlling
for the realized forward range over the same window, the return
effect carries information beyond what the range relationship alone
would produce -- i.e. it's separable. If the coefficient collapses
toward zero once forward range is included, the return effect is
largely explained by the range/volatility channel already known.

Still EXPLORATORY. Bucket edges frozen on the full sample (same
convention as every prior pass). Nothing promoted or frozen by this
check alone.

HOW TO RUN:
    python3 src/separability_check.py
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
HORIZON = 10
VAR, BUCKET = "overnight_range_vs_atr", "mid"
BUCKET_LABELS = ["low", "mid", "high"]


def forward_return(close_series, i, horizon):
    if i + horizon >= len(close_series):
        return None
    c0, c1 = close_series.iloc[i], close_series.iloc[i + horizon]
    if c0 <= 0:
        return None
    return float(c1 - c0)


def forward_range(states_reset, i, horizon):
    j = i + horizon
    if j >= len(states_reset):
        return None
    window = states_reset.iloc[i + 1: j + 1]
    if window.empty:
        return None
    return float(window["High"].max() - window["Low"].min())


def bootstrap_coef_ci(X, y, col_idx, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    n = len(y)
    coefs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        Xs, ys = X[idx], y[idx]
        beta, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
        coefs[i] = beta[col_idx]
    return float(np.percentile(coefs, 5)), float(np.percentile(coefs, 95))


def main():
    print("=" * 78)
    print("SEPARABILITY CHECK -- overnight_range_vs_atr/mid/10d return effect vs. forward range")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="separability_check.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = build_state_frame(discovery)
    states_reset = states.reset_index()
    close = states_reset["Close"]

    full_series = states_reset[VAR]
    valid = full_series.notna()
    edges = np.unique(np.nanpercentile(full_series[valid], [100 / 3, 200 / 3]))
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = BUCKET_LABELS[: len(bin_edges) - 1]
    bucket_labels = pd.cut(full_series, bins=bin_edges, labels=labels, duplicates="drop")

    rows = []
    for i in range(len(states_reset)):
        r = forward_return(close, i, HORIZON)
        rg = forward_range(states_reset, i, HORIZON)
        if r is None or rg is None:
            continue
        b = bucket_labels.iloc[i]
        is_mid = 1.0 if (pd.notna(b) and str(b) == BUCKET) else 0.0
        rows.append((r, is_mid, rg))

    data = np.array(rows)
    y = data[:, 0]
    mid_dummy = data[:, 1]
    fwd_range = data[:, 2]
    n = len(y)
    print(f"\nObservations (Discovery days with valid {HORIZON}-day forward window): {n}")
    print(f"Mid-bucket days: {int(mid_dummy.sum())}")

    # Model 1: return ~ mid_dummy (no control) -- reproduces the raw effect
    X1 = np.column_stack([np.ones(n), mid_dummy])
    beta1, *_ = np.linalg.lstsq(X1, y, rcond=None)
    ci1 = bootstrap_coef_ci(X1, y, col_idx=1)
    print(f"\nModel 1 (no control): mid_bucket coefficient = {beta1[1]:+.2f} pts   ci_90={ci1}")

    # Model 2: return ~ mid_dummy + forward_range (controls for the realized
    # range outcome over the same window -- the already-known channel)
    X2 = np.column_stack([np.ones(n), mid_dummy, fwd_range])
    beta2, *_ = np.linalg.lstsq(X2, y, rcond=None)
    ci2 = bootstrap_coef_ci(X2, y, col_idx=1)
    print(f"Model 2 (controlling for forward range): mid_bucket coefficient = {beta2[1]:+.2f} pts   ci_90={ci2}")
    print(f"forward_range coefficient (sanity -- should be near 0 for a symmetric range measure "
          f"unless range itself correlates with direction): {beta2[2]:+.4f}")

    retained_fraction = beta2[1] / beta1[1] if beta1[1] != 0 else float("nan")
    still_credible = bool(ci2[0] > 0 or ci2[1] < 0)
    print(f"\nFraction of raw effect retained after controlling for forward range: {retained_fraction:.2f}")
    print(f"mid_bucket coefficient still credible (CI excludes 0) after control: {still_credible}")

    if still_credible and retained_fraction > 0.5:
        verdict = "SEPARABLE -- return effect survives controlling for forward range, largely independent information"
    elif still_credible and retained_fraction <= 0.5:
        verdict = "PARTIALLY SEPARABLE -- return effect shrinks substantially but stays credible after controlling for range"
    else:
        verdict = "NOT SEPARABLE -- return effect collapses once forward range is controlled for; likely a byproduct of the known range/volatility relationship, not new information"
    print(f"\nVERDICT: {verdict}")

    out = {
        "analysis": "Separability check: overnight_range_vs_atr/mid/10d return effect vs. forward range",
        "spec": "research/infrastructure/agent-governance-structure.md",
        "n": n,
        "mid_bucket_n": int(mid_dummy.sum()),
        "model1_no_control": {"mid_bucket_coef": float(beta1[1]), "ci_90": list(ci1)},
        "model2_controlling_for_forward_range": {
            "mid_bucket_coef": float(beta2[1]), "ci_90": list(ci2),
            "forward_range_coef": float(beta2[2]),
        },
        "retained_fraction": float(retained_fraction),
        "still_credible_after_control": still_credible,
        "verdict": verdict,
        "note": (
            "EXPLORATORY. Linear partial regression, not a causal test -- controls for the "
            "realized forward RANGE over the same 10-day window as a proxy for 'is this just "
            "the known range/volatility channel showing up as an apparent return effect.' A "
            "verdict of SEPARABLE narrows (does not eliminate) the rediscovery concern; nothing "
            "here is promoted, frozen, or traded."
        ),
    }
    out_path = DATA_DIR / "separability_check_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
