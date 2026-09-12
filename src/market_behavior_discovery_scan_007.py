"""
market_behavior_discovery_scan_007.py
========================================

Scan 007 of the Market Behavior Discovery Engine. Draws Entry 2 from
research/idea_inventory.md (days_to_monthly_opex, pre/post-expiry
volatility compression) -- SECOND (and per that entry's own Integrity
Gate ruling, LAST) attempt on days_to_monthly_opex as a state variable
(Scan 004 = attempt 1, return-direction test, closed 0/36). This scan
tests a mechanistically distinct claim: does dealer gamma-hedging flow
around monthly options expiry COMPRESS realized volatility (RTH range)
into expiry and RELEASE it after -- tested on RANGE, not signed return.

Frozen scope, from idea_inventory.md Entry 2 (do not re-derive, no
retuning):
  - state variable: days_to_monthly_opex (market_state_primitives_v4.py,
    reused as-is)
  - outcome: same-day RTH range vs trailing-20d average RTH range
    (existing convention, reused from overnight-coil / study_intraday_
    behavior_batch3.py's analyze_overnight_coil / build_overnight_and_
    rth_frame)
  - two pre-registered cells: (1) day immediately BEFORE monthly opex,
    (2) day immediately AFTER monthly opex
  - split built in from the start, not bolted on after a result is
    seen: the 8 non-quarterly-witching months (Jan/Feb/Apr/May/Jul/Aug/
    Oct/Nov) are the PRIMARY pre-registered test; the 4 quarterly-
    witching months (Mar/Jun/Sep/Dec) are reported SEPARATELY, per
    LEARN's flagged data-integrity finding (continuous NQ 1-min series
    has zero usable RTH bars on quarterly witching Fridays themselves)
    and per Entry 2's own falsifiable prediction #3 (witching-month
    effect should be WEAKER/ABSENT if the pinning story is right, since
    quarterly witching is a different, typically HIGHER-activity flow
    regime, not lower).

Predictions (written before any number is looked at, per Entry 2):
  P1: day-before-opex (non-witching) RTH-range ratio < 1 (compression),
      credible vs 1.0 (90% CI upper bound < 1.0).
  P2: day-after-opex (non-witching) RTH-range ratio > 1 (release),
      credible vs 1.0 (90% CI lower bound > 1.0).
  P3 (falsifying alternative): the witching-month cells should NOT show
      the same compression/release pattern more strongly -- if witching
      does show an equal-or-stronger effect in the SAME direction, that
      undercuts the gamma-hedging-specific mechanism story (quarterly
      witching bundles far more open interest, so a pure options-driven
      pinning story should look at least as strong there, but the
      COMPRESSION mechanism specifically predicts monthly-only opex
      behaves differently because monthly opex has less notional pinning
      pressure per common intuition, OR the RTH-data gap on quarterly
      Fridays themselves could produce spurious results either way --
      reported, not pooled, exactly per the entry's own scoping note).

This is the entry's ONE pre-registered Discovery-stage shot. No new
cells, no peeking then adjusting, no retuning. A null on P1/P2 CLOSES
this entry per its own Integrity Gate resurrection terms (2-attempt
limit already exhausted regardless of outcome).

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_007.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives_v4 import _third_friday, _rth_daily_ohlc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
LOOKBACK_DAYS = 20
QUARTERLY_WITCHING_MONTHS = {3, 6, 9, 12}


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


def build_rth_range_frame(raw_df: pd.DataFrame) -> pd.DataFrame:
    """One row per trading day with actual RTH data: rth_range and its
    trailing 20-trading-day average (shifted -- no lookahead), same
    convention as study_intraday_behavior_batch3.build_overnight_and_rth_frame."""
    rth = _rth_daily_ohlc(raw_df)
    rth["rth_range"] = rth["rth_high"] - rth["rth_low"]
    rth["trailing_avg_rth_range"] = rth["rth_range"].rolling(
        LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    return rth


def opex_dates_spanning(trading_days) -> list:
    """All monthly opex (3rd-Friday) calendar dates for every year/month
    spanned by trading_days, whether or not that exact date itself has a
    trading-day row (quarterly-witching Fridays often do not, per LEARN's
    data-integrity finding -- day-before/day-after are found by calendar
    date, not by requiring the opex row itself to exist)."""
    months = sorted({(d.year, d.month) for d in trading_days})
    return [_third_friday(y, m) for (y, m) in months]


def label_event_days(rth: pd.DataFrame) -> pd.DataFrame:
    """Adds `event` (before_opex / after_opex / None) and `witching`
    (bool) columns to a copy of `rth`, keyed by calendar date, found via
    the actual opex 3rd-Friday date per month regardless of whether that
    date itself is present in the data."""
    trading_days = sorted(rth.index)
    out = rth.copy()
    out["event"] = None
    out["witching"] = False
    for opex_date in opex_dates_spanning(trading_days):
        witching = opex_date.month in QUARTERLY_WITCHING_MONTHS
        before = [d for d in trading_days if d < opex_date]
        after = [d for d in trading_days if d > opex_date]
        if before:
            d = max(before)
            # guard against a day already claimed by a different opex's
            # "after" leg (only possible with an absurdly short month gap,
            # not a real risk here, but explicit rather than silent)
            out.loc[d, "event"] = "before_opex"
            out.loc[d, "witching"] = witching
        if after:
            d = min(after)
            out.loc[d, "event"] = "after_opex"
            out.loc[d, "witching"] = witching
    return out


def summarize(ratios: list, direction: str) -> dict:
    n = len(ratios)
    if n < 2:
        return {"n": n, "mean_ratio": float("nan"), "ci_90": [float("nan"), float("nan")],
                "credible_vs_one": False, "direction_confirmed": False}
    mean_r = float(np.mean(ratios))
    ci = bootstrap_mean_ci(ratios)
    credible = ci[0] > 1.0 or ci[1] < 1.0
    if direction == "compress":
        confirmed = credible and ci[1] < 1.0
    else:
        confirmed = credible and ci[0] > 1.0
    return {"n": n, "mean_ratio": mean_r, "ci_90": list(ci),
            "credible_vs_one": bool(credible), "direction_confirmed": bool(confirmed)}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 007 (days_to_monthly_opex, RTH-range compression/release)")
    print("=" * 78)
    print("\nInput: research/idea_inventory.md Entry 2\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_007.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    rth = build_rth_range_frame(discovery)
    print(f"Discovery RTH-days available: {len(rth)}")

    labeled = label_event_days(rth)
    labeled = labeled.dropna(subset=["trailing_avg_rth_range"]).copy()
    labeled["ratio"] = labeled["rth_range"] / labeled["trailing_avg_rth_range"]

    results = {}
    for event, direction in [("before_opex", "compress"), ("after_opex", "release")]:
        for witching_flag, tag in [(False, "non_witching"), (True, "witching")]:
            sub = labeled[(labeled["event"] == event) & (labeled["witching"] == witching_flag)]
            ratios = sub["ratio"].dropna().tolist()
            summ = summarize(ratios, direction)
            key = f"{event}_{tag}"
            results[key] = summ
            print(f"  {key}: n={summ['n']} mean_ratio={summ['mean_ratio']:.4f} "
                  f"ci_90=({summ['ci_90'][0]:.4f},{summ['ci_90'][1]:.4f}) "
                  f"credible_vs_1={summ['credible_vs_one']} direction_confirmed={summ['direction_confirmed']}")

    n_opex_events = len({d for d in opex_dates_spanning(sorted(rth.index))})
    out_path = DATA_DIR / "market_behavior_discovery_scan_007_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "state_var": "days_to_monthly_opex",
            "outcome": "rth_range_vs_trailing_20d_avg_ratio",
            "n_opex_events_spanning_data": n_opex_events,
            "cells": results,
        }, f, indent=2)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
