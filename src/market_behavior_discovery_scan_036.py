"""
market_behavior_discovery_scan_036.py
========================================

Scan 036. Draws Entry 34 (map anchor M30): opening-range width -> midday range
and excursion, NQ. Mechanism doc written BEFORE this scan:
research/mechanisms/opening-range-width-midday-excursion-nq-m30.md

WHY THIS ENTRY AND NOT THE OLDEST DRAWABLE (Entry 32/M28): SHELF RULE v2's draw
order is the ranking rule (information gain x edge potential), not age. Stack A
(hyp-000161, a POWERED NULL) established that the Risk/State Engine is a
SIZING and PERMISSION layer, not an entry filter -- so what B2 needs is better
SIZING material. M30 is the only drawable entry that produces exactly that: a
state known at 10:00 ET (an INTRADAY update, between B2's pre-open number and
its 14:00 afternoon update) conditioning a SIZE outcome. Its own doc section 6
says it plainly: "the first queue family that plugs directly into the bot."
Entry 32 (M28, pre-holiday effect) is a calendar effect with no such path.

Frozen scope (doc section 9), Discovery only (2015-01 -> 2021-10-03), daily
aggregation, scan_027/030 pattern. SIX pre-registered cells, 1 gating:
  1. HIGH-LOW midday range-ratio difference, block CI          <== GATING (P1)
  2. HIGH-LOW midday MFE difference, ATR14 units                   (P2, reported)
  3. HIGH-LOW midday MAE difference, ATR14 units                   (P2, reported)
  4. P1 residualized on the prior-day range tercile (F-048):
     stratified HIGH-LOW difference, and the share of cell 1 retained (P3)
  5. unconditional midday range-ratio reference                    (NULL ref)
  6. alignment / coverage disclosure                               (n, skips)

DEFINITIONS, fixed here before any result is seen:
  opening_range_vs_atr  taken from market_state_primitives' frozen state frame
                        (the doc names that variable; re-deriving it here would
                        be a spec deviation). Terciles cut on the Discovery
                        slice, HIGH = top third, LOW = bottom third.
  midday                11:30-13:30 ET, inclusive="left".
  midday range ratio    midday range / trailing-20d mean midday range, the
                        trailing mean SHIFTED BY 1 session (no lookahead).
  midday MFE / MAE      (high - midday open) and (midday open - low), each in
                        ATR14 units -- the same normalisation the Idea Factory
                        footprint that sourced this claim used.
  F-048 stratum         prior-day range tercile (`range_vs_atr`), the validated
                        prior-day-range fact P3 has to survive.

Block bootstrap (block=10) is the CI of record. One shot. No new cells, no
retuning after seeing results.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_036.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
from market_state_primitives import build_state_frame  # noqa: E402
from market_state_primitives_v2 import extend_state_frame  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BLOCK = 10
N_BOOT = 3000
SEED = 20260913
RANGE_LOOKBACK = 20
SCAN_KEY = "scan_036_2026-09-14"


def _block_boot_means(x: np.ndarray, rng) -> np.ndarray:
    """Moving-block bootstrap of the mean; same construction as
    baseline_relative._block_means, kept local so this scan's CI of record
    cannot drift if that helper is ever changed."""
    n = len(x)
    if n <= BLOCK:
        return rng.choice(x, size=(N_BOOT, n), replace=True).mean(axis=1)
    n_blocks = int(np.ceil(n / BLOCK))
    starts = rng.integers(0, n - BLOCK + 1, size=(N_BOOT, n_blocks))
    idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]).reshape(N_BOOT, -1)[:, :n]
    return x[idx].mean(axis=1)


def diff_ci(high: np.ndarray, low: np.ndarray, alpha: float = 0.10):
    """90% block-bootstrap CI on mean(HIGH) - mean(LOW). Both arms are daily,
    sequential, and autocorrelated, so BOTH are block-bootstrapped (unlike
    scan_034's block-vs-iid, where the second arm was a pooled hour sample)."""
    high = high[~np.isnan(high)]
    low = low[~np.isnan(low)]
    if len(high) < BLOCK * 3 or len(low) < BLOCK * 3:
        return float("nan"), [float("nan"), float("nan")]
    rng = np.random.default_rng(SEED)
    d = float(high.mean() - low.mean())
    boots = _block_boot_means(high, rng) - _block_boot_means(low, rng)
    return d, [float(np.percentile(boots, 100 * alpha / 2)),
               float(np.percentile(boots, 100 * (1 - alpha / 2)))]


def _cell(label: str, high: np.ndarray, low: np.ndarray) -> dict:
    d, ci = diff_ci(high, low)
    cred = (not np.isnan(ci[0])) and ((ci[0] > 0) or (ci[1] < 0))
    return {"cell": label, "n_high": int(len(high[~np.isnan(high)])), "n_low": int(len(low[~np.isnan(low)])),
            "high_mean": float(np.nanmean(high)) if len(high) else float("nan"),
            "low_mean": float(np.nanmean(low)) if len(low) else float("nan"),
            "diff": d, "ci_90": ci, "credible": bool(cred),
            "direction": "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 036 (Entry 34 / map M30:")
    print("opening-range width -> midday range and excursion, NQ)")
    print("=" * 78)

    df, synthetic = load_price_data(context="market_behavior_discovery_scan_036.py")
    if synthetic:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(df)

    states = extend_state_frame(build_state_frame(disc), disc)
    idx = pd.to_datetime(pd.Index(states.index))
    for col in ("opening_range_vs_atr", "range_vs_atr", "atr14"):
        if col not in states.columns:
            print(f"ABORT: state frame has no `{col}`."); return
    opening = pd.Series(states["opening_range_vs_atr"].to_numpy(dtype=float), index=idx)
    prior_rng = pd.Series(states["range_vs_atr"].to_numpy(dtype=float), index=idx)
    atr = pd.Series(states["atr14"].to_numpy(dtype=float), index=idx)

    # ---- midday outcomes, one row per session -----------------------------
    rows, skipped = [], 0
    for day, g in disc.groupby(disc.index.date):
        ts = pd.Timestamp(day)
        mid = g.between_time("11:30", "13:30", inclusive="left")
        if len(mid) < 60:
            skipped += 1
            continue
        o = float(mid["Open"].iloc[0])
        hi, lo = float(mid["High"].max()), float(mid["Low"].min())
        rows.append({"date": ts, "midday_range": hi - lo, "mfe": hi - o, "mae": o - lo})
    daily = pd.DataFrame(rows).set_index("date").sort_index()
    daily["trailing_midday"] = daily["midday_range"].rolling(
        RANGE_LOOKBACK, min_periods=RANGE_LOOKBACK).mean().shift(1)
    daily["ratio"] = daily["midday_range"] / daily["trailing_midday"]
    daily["atr14"] = atr.reindex(daily.index)
    daily["mfe_atr"] = daily["mfe"] / daily["atr14"]
    daily["mae_atr"] = daily["mae"] / daily["atr14"]
    daily["opening"] = opening.reindex(daily.index)
    daily["prior_rng"] = prior_rng.reindex(daily.index)

    usable = daily.dropna(subset=["ratio", "opening", "mfe_atr", "mae_atr"])
    lo_edge, hi_edge = np.nanpercentile(usable["opening"], [100 / 3, 200 / 3])
    usable = usable.assign(
        grp=np.where(usable["opening"] <= lo_edge, "LOW",
                     np.where(usable["opening"] >= hi_edge, "HIGH", "MID")))
    H = usable[usable["grp"] == "HIGH"]
    L = usable[usable["grp"] == "LOW"]
    print(f"\nDiscovery sessions with a usable midday window: {len(daily)} (skipped {skipped});")
    print(f"with all state + trailing inputs present: {len(usable)}  -> HIGH {len(H)}, LOW {len(L)}")
    print(f"opening_range_vs_atr tercile edges (Discovery): LOW <= {lo_edge:.4f}, HIGH >= {hi_edge:.4f}")

    # ---- cells 1-3 --------------------------------------------------------
    c1 = _cell("1_midday_range_ratio_HIGH_minus_LOW_GATING", H["ratio"].to_numpy(), L["ratio"].to_numpy())
    c2 = _cell("2_midday_mfe_atr_HIGH_minus_LOW", H["mfe_atr"].to_numpy(), L["mfe_atr"].to_numpy())
    c3 = _cell("3_midday_mae_atr_HIGH_minus_LOW", H["mae_atr"].to_numpy(), L["mae_atr"].to_numpy())

    # ---- cell 4: residualized on the prior-day range tercile (F-048) ------
    pr = usable["prior_rng"].dropna()
    p_lo, p_hi = np.nanpercentile(pr, [100 / 3, 200 / 3])
    strata, weights, parts = [], [], []
    for name, sel in (("prior_LOW", usable["prior_rng"] <= p_lo),
                      ("prior_MID", (usable["prior_rng"] > p_lo) & (usable["prior_rng"] < p_hi)),
                      ("prior_HIGH", usable["prior_rng"] >= p_hi)):
        sub = usable[sel]
        h = sub[sub["grp"] == "HIGH"]["ratio"].to_numpy()
        l = sub[sub["grp"] == "LOW"]["ratio"].to_numpy()
        h, l = h[~np.isnan(h)], l[~np.isnan(l)]
        if len(h) < BLOCK * 3 or len(l) < BLOCK * 3:
            strata.append({"stratum": name, "n_high": int(len(h)), "n_low": int(len(l)),
                           "diff": None, "note": "below the block floor, excluded from the weighted average"})
            continue
        d = float(h.mean() - l.mean())
        w = len(h) + len(l)
        strata.append({"stratum": name, "n_high": int(len(h)), "n_low": int(len(l)), "diff": round(d, 6)})
        weights.append(w); parts.append(d)
    strat_diff = float(np.average(parts, weights=weights)) if parts else float("nan")
    retained = (strat_diff / c1["diff"]) if c1["diff"] not in (0, None) and np.isfinite(c1["diff"]) else float("nan")
    c4 = {"cell": "4_P1_residualized_on_prior_day_range_tercile_F048",
          "strata": strata, "stratified_diff": strat_diff,
          "raw_diff_cell1": c1["diff"], "share_retained": retained,
          "p3_bar": 0.50, "p3_passes": bool(np.isfinite(retained) and retained >= 0.50),
          "note": "P3: >=50% of cell 1's difference must survive stratification on the prior-day "
                  "range tercile, or the claim is a restatement of F-048 and closes as a duplicate."}

    # ---- cells 5-6 --------------------------------------------------------
    c5 = {"cell": "5_unconditional_midday_ratio_reference",
          "n": int(usable["ratio"].notna().sum()),
          "mean": float(usable["ratio"].mean()),
          "note": "the NULL: a ratio of 1.0 means a session's midday range matches its own "
                  "trailing-20d midday average. The claim is about HIGH vs LOW, not vs 1.0."}
    c6 = {"cell": "6_alignment_and_coverage",
          "sessions_in_discovery": int(len(set(disc.index.date))),
          "sessions_with_midday_window": int(len(daily)), "sessions_skipped_short_midday": int(skipped),
          "sessions_usable_after_state_and_trailing": int(len(usable)),
          "n_high": int(len(H)), "n_low": int(len(L)), "n_mid": int((usable["grp"] == "MID").sum()),
          "tercile_edges": {"low_max": float(lo_edge), "high_min": float(hi_edge)},
          "prior_day_tercile_edges": {"low_max": float(p_lo), "high_min": float(p_hi)}}

    p1_pass = bool(c1["credible"] and c1["ci_90"][0] > 0)
    result = {"scan": SCAN_KEY, "entry": 34, "map_anchor": "M30",
              "mechanism_doc": "research/mechanisms/opening-range-width-midday-excursion-nq-m30.md",
              "slice": "discovery", "block": BLOCK, "n_boot": N_BOOT, "seed": SEED,
              "cells": [c1, c2, c3, c4, c5, c6],
              "p1_gating_passes": p1_pass,
              "p3_passes": c4["p3_passes"],
              "verdict": ("P1 PASS + P3 PASS" if p1_pass and c4["p3_passes"] else
                          "P1 PASS, P3 FAIL -> duplicate of F-048" if p1_pass else
                          "P1 FAIL -> closes"),
              "rule": "One shot, frozen scope (doc section 9). Six cells, one gating. No new cells "
                      "and no retuning after seeing results."}

    out = DATA_DIR / f"{SCAN_KEY}_results.json"
    out.write_text(json.dumps(result, indent=2, default=str))

    print("\n--- CELLS -------------------------------------------------------")
    for c in (c1, c2, c3):
        print(f"{c['cell']}")
        print(f"    HIGH {c['high_mean']:+.4f} (n={c['n_high']})  LOW {c['low_mean']:+.4f} (n={c['n_low']})")
        print(f"    diff {c['diff']:+.4f}  ci_90 ({c['ci_90'][0]:+.4f},{c['ci_90'][1]:+.4f})  -> {c['direction']}")
    print(f"{c4['cell']}")
    for s in c4["strata"]:
        print(f"    {s['stratum']:11s} n_high={s['n_high']:4d} n_low={s['n_low']:4d} "
              f"diff={s['diff'] if s['diff'] is not None else 'excluded'}")
    print(f"    stratified diff {strat_diff:+.4f} vs raw {c1['diff']:+.4f} -> "
          f"{retained:.1%} retained (P3 bar 50%) -> {'PASS' if c4['p3_passes'] else 'FAIL'}")
    print(f"{c5['cell']}: mean {c5['mean']:.4f} (n={c5['n']})")
    print(f"\nP1 (GATING): {'PASS' if p1_pass else 'FAIL'}    VERDICT: {result['verdict']}")
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
