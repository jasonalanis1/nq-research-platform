"""
market_behavior_discovery_scan_008.py
========================================

Scan 008 of the Market Behavior Discovery Engine. Draws Entry 3 from
research/idea_inventory.md (overnight-vs-RTH return divergence
persistence) -- FIRST ATTEMPT on this state variable and mechanism
family (Integrity Gate ruling: clean, no resurrection risk).

Frozen scope, from idea_inventory.md Entry 3 (do not re-derive, no
retuning):
  - state variable: trailing 20-trading-day cumulative overnight return
    (RTH open - prior RTH close, signed) minus trailing 20-day
    cumulative RTH return (RTH close - RTH open, signed), both ATR(14)
    -normalized per-day before summing, terciled. Known at today's open
    (no lookahead -- the trailing window is shifted to exclude today).
  - outcome: today's OWN overnight-vs-RTH divergence (today's own
    overnight return minus today's own RTH return, ATR-normalized) --
    NOT a restatement of the trailing state itself, a same-day-forward
    fact not knowable until the state was already fixed at the open.
  - one pre-registered horizon: next 1 trading day (today, relative to
    the trailing state fixed at today's open).
  - 3 pre-registered cells: HIGH / MID / LOW tercile of the trailing
    divergence measure.

Predictions (written before any number is looked at, per Entry 3):
  P1 (persistence, primary): HIGH trailing-divergence tercile -> today's
     own divergence is credibly POSITIVE (continuation, not reversion).
     LOW trailing-divergence tercile -> today's own divergence is
     credibly NEGATIVE (continuation in the opposite direction).
     Mechanism: overnight index-futures flow is structurally
     price-insensitive (mandate-driven contribution/rebalancing flow)
     and should persist when elevated, not mean-revert.
  P2 (falsifying alternative): if the pattern is instead pure
     mean-reverting statistical artifact, the HIGH tercile should show a
     credibly NEGATIVE today's-own-divergence (reversion) and the LOW
     tercile a credibly POSITIVE one -- the opposite sign from P1. P1
     and P2 are mutually exclusive single-shot predictions on the same
     two cells, so this scan is informative regardless of which way (if
     either) it resolves.
  P3 (non-restating counterparty check, secondary, reported only within
     whichever of HIGH/LOW is credible under P1): the effect should be
     WEAKER immediately following days classified `low` on the existing
     volume_vs_expected descriptor (mechanical-flow story predicts the
     effect scales with real participation).

This is the entry's ONE pre-registered Discovery-stage shot. No new
cells, no peeking then adjusting, no retuning.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_008.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_state_primitives_v4 import _rth_daily_ohlc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 8
LOOKBACK_DAYS = 20


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


def build_divergence_frame(raw_df: pd.DataFrame, states: pd.DataFrame) -> pd.DataFrame:
    """One row per RTH day: today's own overnight/RTH divergence
    (outcome), and the trailing 20-day cumulative divergence known at
    today's open (state, shifted -- no lookahead)."""
    rth = _rth_daily_ohlc(raw_df)
    rth = rth.reindex(states.index)
    atr14 = states["atr14"]

    prior_close = rth["rth_close"].shift(1)
    overnight_return_atr = (rth["rth_open"] - prior_close) / atr14
    rth_return_atr = (rth["rth_close"] - rth["rth_open"]) / atr14
    daily_divergence = overnight_return_atr - rth_return_atr  # today's own outcome

    trailing_divergence = daily_divergence.rolling(
        LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).sum().shift(1)  # cumulative, known at today's open

    out = pd.DataFrame({
        "daily_divergence": daily_divergence,
        "trailing_divergence": trailing_divergence,
        "volume_vs_expected": states["volume_vs_expected"],
    })
    return out


def summarize(values: list) -> dict:
    n = len(values)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": [float("nan"), float("nan")], "credible": False}
    ci = bootstrap_mean_ci(values)
    credible = ci[0] > 0 or ci[1] < 0
    return {"n": n, "mean": float(np.mean(values)), "ci_90": list(ci), "credible": bool(credible)}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 008 (overnight-vs-RTH return divergence persistence)")
    print("=" * 78)
    print("\nInput: research/idea_inventory.md Entry 3\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_008.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(discovery), discovery)
    frame = build_divergence_frame(discovery, states)
    frame = frame.dropna(subset=["trailing_divergence", "daily_divergence"]).copy()
    print(f"Discovery RTH-days with a valid trailing-divergence state: {len(frame)}")

    frame["tercile"] = pd.qcut(frame["trailing_divergence"], 3, labels=["low", "mid", "high"])

    results = {}
    for tercile in ["low", "mid", "high"]:
        sub = frame[frame["tercile"] == tercile]
        vals = sub["daily_divergence"].dropna().tolist()
        summ = summarize(vals)
        results[tercile] = summ
        print(f"  {tercile}: n={summ['n']} mean={summ['mean']:.4f} "
              f"ci_90=({summ['ci_90'][0]:.4f},{summ['ci_90'][1]:.4f}) credible={summ['credible']}")

    p1_high_confirmed = results["high"]["credible"] and results["high"]["mean"] > 0
    p1_low_confirmed = results["low"]["credible"] and results["low"]["mean"] < 0
    p2_high_confirmed = results["high"]["credible"] and results["high"]["mean"] < 0
    p2_low_confirmed = results["low"]["credible"] and results["low"]["mean"] > 0
    print(f"\nP1 (persistence) HIGH confirmed: {p1_high_confirmed}  LOW confirmed: {p1_low_confirmed}")
    print(f"P2 (reversion, falsifying alt) HIGH confirmed: {p2_high_confirmed}  LOW confirmed: {p2_low_confirmed}")

    # P3 -- non-restating counterparty check, reported only for whichever
    # of HIGH/LOW came back credible under P1 (persistence).
    p3 = {}
    for tercile, confirmed in [("high", p1_high_confirmed), ("low", p1_low_confirmed)]:
        if not confirmed:
            continue
        sub = frame[frame["tercile"] == tercile]
        low_vol = sub[sub["volume_vs_expected"] < sub["volume_vs_expected"].median()]
        vals = low_vol["daily_divergence"].dropna().tolist()
        summ = summarize(vals)
        p3[tercile] = summ
        print(f"  P3 {tercile}/low-volume subset: n={summ['n']} mean={summ['mean']:.4f} "
              f"ci_90=({summ['ci_90'][0]:.4f},{summ['ci_90'][1]:.4f}) credible={summ['credible']}")

    out_path = DATA_DIR / "market_behavior_discovery_scan_008_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "state_var": "trailing_20d_overnight_minus_rth_return_divergence",
            "outcome": "today_own_overnight_minus_rth_divergence_atr",
            "cells": results,
            "p1_persistence_confirmed": {"high": p1_high_confirmed, "low": p1_low_confirmed},
            "p2_reversion_confirmed": {"high": p2_high_confirmed, "low": p2_low_confirmed},
            "p3_volume_conditioned": p3,
        }, f, indent=2)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
