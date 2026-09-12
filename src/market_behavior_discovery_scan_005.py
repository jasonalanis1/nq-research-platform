"""
market_behavior_discovery_scan_005.py
========================================

Scan 005 of the Market Behavior Discovery Engine. Frozen scoping:
research/studies/scan-005-scoping-2026-09-10.md. Direction B
(cross-instrument DIVERGENCE / relative-value state) -- genuinely new
mechanism family, never scanned before (LEARN + Integrity Gate
resurrection ruling: PASS, unconditional, both variables, per the
scoping doc). Short horizons only, per the Standing Research Priority.

Two state variables, both a residual between NQ's realized daily return
and what a trailing rolling beta to another instrument's return would
predict, z-scored against the residual's own trailing std:
  D1: nq_zn_divergence   -- NQ vs. ZN  (10Y Treasury futures)
  D2: nq_vxn_divergence  -- NQ vs. VXN (NASDAQ-100 implied vol)
Both carry a PRE-REGISTERED monotonic-reversion shape prediction (LOW
bucket -> positive forward drift, HIGH bucket -> negative forward
drift) -- stated in the scoping doc BEFORE this script was run.

Same exploratory/uncorrected methodology as Scans 001-004: nothing here
is logged to the ledger, nothing is treated as validated -- only a
candidate that clears the same multi-stage screen (split-sample,
regime-split, mechanism, frozen monetization spec) gets taken further.
Discovery data only, per protocol.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_005.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame, VXN_PATH
from study_volatility_regime import compute_daily_ref_closes

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_RANKED = 40
ATR_NORMALIZED_FLOOR = 0.05
HORIZONS = [1, 2, 3, 5]  # short end only, per Standing Research Priority
BETA_LOOKBACK_DAYS = 20
STATE_VARS = ["nq_zn_divergence", "nq_vxn_divergence"]
TERCILE_LABELS = ["low", "mid", "high"]


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


def _load_zn_daily_close() -> pd.Series:
    zn_df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_005.py (ZN)",
                                           apply_holdout=False, symbol="ZN")
    if is_synthetic:
        raise RuntimeError("Only synthetic ZN data available -- nq_zn_divergence cannot be built.")
    day_groups = {day: sub for day, sub in zn_df.groupby(zn_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)
    return pd.Series(ref_closes).sort_index()


def _load_vxn_daily_close() -> pd.Series:
    vxn = pd.read_csv(VXN_PATH, parse_dates=["observation_date"])
    vxn = vxn.dropna(subset=["VXNCLS"])
    vxn = vxn.set_index(vxn["observation_date"].dt.date)["VXNCLS"].astype(float)
    return vxn.sort_index()


def build_divergence_state(nq_close: pd.Series, other_close: pd.Series) -> pd.Series:
    """residual[i-1] = nq_ret[i-1] - beta_20(lagged) * other_ret[i-1],
    z-scored by its own trailing std, assigned to state day i (i.e. this
    IS the prior-day-shift -- caller must not shift again). beta_20 is
    computed on data ending at i-2 (doubly lagged: the beta itself never
    sees the return it is about to be applied to, or anything later)."""
    other_reindexed = other_close.reindex(nq_close.index, method="ffill")
    nq_ret = nq_close.pct_change()
    other_ret = other_reindexed.pct_change()

    # beta_20 at position i-1 uses returns [i-1-20 .. i-2] -- shift(1)
    # on the rolling covariance/variance so the window ending at i-2 is
    # what's used to predict return i-1, never return i-1 itself.
    cov = nq_ret.rolling(BETA_LOOKBACK_DAYS).cov(other_ret).shift(1)
    var = other_ret.rolling(BETA_LOOKBACK_DAYS).var().shift(1)
    beta = cov / var

    predicted = beta * other_ret
    residual = nq_ret - predicted
    resid_std = residual.rolling(BETA_LOOKBACK_DAYS).std().shift(1)
    z = residual / resid_std

    # This whole series is "known as of day i's close" (uses nq_ret[i]).
    # Shift once more so state[i] (knowable at day i's OPEN) uses only
    # information through day i-1 -- same no-lookahead convention as
    # every other prior-day-fact descriptor in this project.
    return z.shift(1)


def forward_return(close_series, i, horizon):
    if i + horizon >= len(close_series):
        return None
    c0, c1 = close_series.iloc[i], close_series.iloc[i + horizon]
    if c0 <= 0:
        return None
    return float(c1 - c0)


def bucket_series(series, n_buckets=3):
    valid = series.notna()
    pct = [100 / n_buckets * k for k in range(1, n_buckets)]
    edges = np.unique(np.nanpercentile(series[valid], pct))
    if len(edges) < 1:
        return None, None
    bin_edges = [-np.inf] + list(edges) + [np.inf]
    labels = TERCILE_LABELS[: len(bin_edges) - 1]
    return pd.cut(series, bins=bin_edges, labels=labels, duplicates="drop"), labels


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 005 (cross-instrument divergence)")
    print("=" * 78)
    print("\nFrozen scoping: research/studies/scan-005-scoping-2026-09-10.md\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_005.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(discovery), discovery)
    avg_atr = float(states["atr14"].dropna().mean())

    nq_close = states["Close"]
    zn_close = _load_zn_daily_close()
    vxn_close = _load_vxn_daily_close()

    states["nq_zn_divergence"] = build_divergence_state(nq_close, zn_close)
    states["nq_vxn_divergence"] = build_divergence_state(nq_close, vxn_close)

    for var in STATE_VARS:
        print(f"  {var}: {int(states[var].notna().sum())} non-null of {len(states)}")

    close = states["Close"].reset_index(drop=True)
    states_reset = states.reset_index()

    candidates = []
    for var in STATE_VARS:
        series = states_reset[var]
        valid_mask = series.notna()
        if valid_mask.sum() < MIN_N_FOR_RANKED * 3:
            print(f"  {var}: insufficient non-null observations, skipped.")
            continue
        bucket_labels, labels = bucket_series(series, 3)
        if bucket_labels is None:
            continue

        for horizon in HORIZONS:
            fwd_rets = {b: [] for b in labels}
            baseline_rets = []
            for i in range(len(states_reset)):
                b = bucket_labels.iloc[i]
                r = forward_return(close, i, horizon)
                if r is None:
                    continue
                baseline_rets.append(r)
                if pd.notna(b):
                    fwd_rets[str(b)].append(r)
            baseline_mean = float(np.mean(baseline_rets)) if baseline_rets else float("nan")

            bucket_means = {}
            for label in labels:
                rets = fwd_rets[label]
                n = len(rets)
                if n < MIN_N_FOR_RANKED:
                    continue
                mean_r = float(np.mean(rets))
                ci = bootstrap_mean_ci(rets)
                credible_vs_zero = ci[0] > 0 or ci[1] < 0
                effect_vs_baseline = mean_r - baseline_mean
                atr_norm = abs(effect_vs_baseline) / avg_atr if avg_atr > 0 else float("nan")
                cost_ok = atr_norm >= ATR_NORMALIZED_FLOOR
                bucket_means[label] = effect_vs_baseline
                candidates.append({
                    "state_var": var, "bucket": label, "horizon_days": horizon, "n": n,
                    "mean_fwd_return_pts": mean_r, "ci_90": list(ci),
                    "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": effect_vs_baseline,
                    "atr_normalized_effect": atr_norm, "credible_vs_zero": credible_vs_zero,
                    "clears_cost_floor": cost_ok,
                    "unusual": bool(credible_vs_zero), "economically_meaningful": bool(cost_ok),
                })
            # Pre-registered shape check: LOW positive, HIGH negative (reversion).
            if "low" in bucket_means and "high" in bucket_means:
                matches_reversion_shape = bucket_means["low"] > 0 and bucket_means["high"] < 0
                for c in candidates:
                    if c["state_var"] == var and c["horizon_days"] == horizon:
                        c["matches_prereg_reversion_shape"] = matches_reversion_shape

    ranked = sorted(
        [c for c in candidates if c["credible_vs_zero"] and c["clears_cost_floor"]],
        key=lambda c: c["atr_normalized_effect"], reverse=True,
    )

    print(f"\nTotal (state x bucket x horizon) cells scanned: {len(candidates)}")
    print(f"Cells credible AND clearing cost floor: {len(ranked)}")
    for c in ranked:
        shape = c.get("matches_prereg_reversion_shape")
        print(f"  {c['state_var']:22s} {c['bucket']:5s} h={c['horizon_days']:2d}d  n={c['n']:4d}  "
              f"mean={c['mean_fwd_return_pts']:+7.2f}pts  vs_baseline={c['effect_vs_baseline_pts']:+7.2f}pts  "
              f"atr_norm={c['atr_normalized_effect']:.4f}  prereg_shape_match={shape}  ci_90={c['ci_90']}")

    out = {
        "scan": "market_behavior_discovery_scan_005.py -- Scan 005",
        "spec": "research/studies/scan-005-scoping-2026-09-10.md",
        "status": "EXPLORATORY -- NOT a finding, NOT a hypothesis, NOT logged to the ledger",
        "n_days": len(states),
        "avg_atr14": avg_atr,
        "state_vars_scanned": STATE_VARS,
        "horizons_scanned": HORIZONS,
        "total_cells": len(candidates),
        "cells_passing_unusual_and_cost_gate": len(ranked),
        "all_candidates": candidates,
        "ranked": ranked,
    }
    out_path = DATA_DIR / "market_behavior_discovery_scan_005_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
