"""
market_behavior_discovery_scan_020.py
========================================

Scan 020. Draws Entry 19 (map anchor M15) from research/idea_inventory.md:
overnight vs intraday return split, NQ. Mechanism doc written BEFORE this
scan: research/mechanisms/overnight-vs-intraday-return-split-m15.md.

Frozen scope (mechanism doc Section 7), Discovery only:
  session day = RTH 09:30-16:00 ET block;
  R_night = open(first 09:30 bar) - close(last 16:00 bar of the PRIOR
            session), / ATR14 (trailing mean RTH range through t-1);
  R_day   = close(16:00 bar) - open(09:30 bar), / ATR14.
  Sessions lacking a 09:30 or 16:00 bar are dropped and counted.
SEVEN pre-registered cells (scan_020_2026-09-12 in SCAN_REGISTRY):
  1. mean(R_night), block-bootstrap CI (reported)
  2. mean(R_day), block-bootstrap CI (reported)
  3. mean(R_night - R_day), block-bootstrap CI          <== GATING (P1)
  4. cell 3 on Discovery first half   (P2 decay, reported)
  5. cell 3 on Discovery second half  (P2 decay, reported)
  6. share of mean(R_night) in the 09:29->09:30 open print (P3, KILL RULE:
     terminate if > 50%)
  7. lag-1 autocorrelation of R_night with CI (P4 diagnostic, reported)
NULL 1 is built into cell 3 (night vs day legs of ONE drift). Block
bootstrap (block=10 sessions) is the CI of record for every cell.
Monetization pre-check reported: night premium in points vs 2x round-trip
cost (cost assumption disclosed, not asserted).

This is the entry's ONE pre-registered Discovery-stage shot. No new cells,
no peeking then adjusting, no retuning.

RUN RECORD (honesty): run 1 (September 12th, ~4:55 pm CT) had an
implementation defect -- calendar days with only Globex bars (Sunday
evenings) reset the prior-close chain, which silently dropped every
MONDAY's night leg (the weekend leg, the largest one) and left 1,252 of
~1,630 sessions. Caught by the drop-count diagnostic in the test cycle.
Run 1's output is preserved as
data/market_behavior_discovery_scan_020_results_RUN1_BUGGED.json and is
NOT the result of record. The fix changes which sessions are INCLUDED to
match the frozen spec; it does not change any cell, threshold, window or
statistic. Run 2 is the scan of record.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_020.py
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
from baseline_relative import _block_means  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ATR_WINDOW = 14
BLOCK = 10
N_BOOT = 3000
SEED = 20260912
ROUND_TRIP_COST_POINTS = 1.0   # assumption: ~2 ticks spread + commission on NQ; disclosed, not asserted


def block_ci(v, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < BLOCK * 3:
        return [float("nan"), float("nan")]
    rng = np.random.default_rng(SEED)
    means = _block_means(v, BLOCK, N_BOOT, rng)
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


def cell(v):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    ci = block_ci(v)
    credible = (ci[0] > 0) or (ci[1] < 0)
    return {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": ci,
            "credible_vs_zero": bool(credible),
            "direction": "positive" if credible and ci[0] > 0 else ("negative" if credible else "null")}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 020 (Entry 19 / M15: overnight vs intraday return split)")
    print("=" * 78)
    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_020.py", symbol="NQ")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(nq_all)

    rows = []
    dropped = 0
    prior_close = None
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        first = g.between_time("09:30", "09:30")
        last = g.between_time("15:59", "15:59")
        pre = g.between_time("09:29", "09:29")
        if rth.empty:
            # calendar day with Globex bars only (Sunday evening, holiday):
            # not a session. The night leg simply spans it (close-to-open
            # across the weekend/holiday, per the published definition).
            continue
        if first.empty or last.empty or len(rth) < 200:
            dropped += 1
            # a REAL session that is unusable (half day, roll-Friday gap)
            # breaks the chain: the next night leg has no clean prior close.
            prior_close = None
            continue
        o = float(first["Open"].iloc[0]); c = float(last["Close"].iloc[-1])
        pre_close = float(pre["Close"].iloc[-1]) if not pre.empty else np.nan
        rows.append({"date": pd.Timestamp(day), "open": o, "close": c, "prior_close": prior_close,
                     "pre_open_close": pre_close, "rth_range": float(rth["High"].max() - rth["Low"].min())})
        prior_close = c
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["atr14"] = d["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    d = d.dropna(subset=["prior_close", "atr14"])
    d["r_night"] = (d["open"] - d["prior_close"]) / d["atr14"]
    d["r_day"] = (d["close"] - d["open"]) / d["atr14"]
    d["r_night_pts"] = d["open"] - d["prior_close"]
    d["r_globex"] = (d["pre_open_close"] - d["prior_close"]) / d["atr14"]      # 16:00 -> 09:29
    d["r_print"] = (d["open"] - d["pre_open_close"]) / d["atr14"]              # 09:29 close -> 09:30 open
    d["diff"] = d["r_night"] - d["r_day"]
    print(f"Sessions usable: {len(d)}; sessions dropped (missing 09:30/16:00 bar or partial RTH): {dropped}")

    half = len(d) // 2
    cells = {
        "1_night_mean": cell(d["r_night"]),
        "2_day_mean": cell(d["r_day"]),
        "3_night_minus_day_GATING": cell(d["diff"]),
        "4_diff_first_half": cell(d["diff"].iloc[:half]),
        "5_diff_second_half": cell(d["diff"].iloc[half:]),
    }
    # cell 6: open-print share of the night leg
    globex = cell(d["r_globex"].dropna()); prnt = cell(d["r_print"].dropna())
    night_mean = cells["1_night_mean"]["mean"]
    print_share = (prnt["mean"] / night_mean) if night_mean not in (0, float("nan")) and not np.isnan(night_mean) else float("nan")
    cells["6_open_print_share_KILL"] = {"globex_16_to_0929": globex, "print_0929_to_0930": prnt,
                                         "print_share_of_night_mean": float(print_share),
                                         "kill": bool(abs(print_share) > 0.5) if not np.isnan(print_share) else False}
    # cell 7: lag-1 autocorrelation of r_night with block CI (via products)
    x = d["r_night"].values
    xc = x - x.mean()
    prod = xc[1:] * xc[:-1] / xc.var()
    ac = cell(prod)
    cells["7_night_lag1_autocorr"] = ac

    total = cells["1_night_mean"]["mean"] + cells["2_day_mean"]["mean"]
    night_share = cells["1_night_mean"]["mean"] / total if total else float("nan")
    night_pts = float(d["r_night_pts"].mean())

    print("\nCells (ATR units, block bootstrap 90% CI, block=10):")
    for k in ["1_night_mean", "2_day_mean", "3_night_minus_day_GATING", "4_diff_first_half", "5_diff_second_half", "7_night_lag1_autocorr"]:
        s = cells[k]
        print(f"  {k:<26} n={s['n']:>4} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
    k6 = cells["6_open_print_share_KILL"]
    print(f"  6_open_print_share         globex={k6['globex_16_to_0929']['mean']:+.4f} print={k6['print_0929_to_0930']['mean']:+.4f} "
          f"share={k6['print_share_of_night_mean']:+.3f} KILL={k6['kill']}")
    print(f"\nNight share of total drift: {night_share:.2f}   night premium in points/session: {night_pts:+.2f} "
          f"(2x round-trip cost assumption = {2*ROUND_TRIP_COST_POINTS:.1f} pts)")

    g = cells["3_night_minus_day_GATING"]
    if k6["kill"]:
        verdict, note = "KILLED", "Night premium concentrated in the 09:29->09:30 open print (>50%). Family terminates per kill rule (c)."
    elif g["direction"] == "positive":
        decayed = cells["5_diff_second_half"]["direction"] != "positive" and cells["4_diff_first_half"]["direction"] == "positive"
        if decayed:
            verdict, note = "P1_PASS_DECAYED", "Gating cell credible on full Discovery but second half is flat while first half is not -> recorded DECAYED per falsifier (b). Closes."
        else:
            verdict, note = "P1_PASS", "Night leg credibly exceeds day leg; not decayed across halves; not killed. Advance to Statistical per pipeline order."
    else:
        verdict, note = "P1_FAIL", "Night-minus-day CI includes zero: no night/day split in NQ at this ceiling. Entry closes on falsifier (a)."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_sessions": int(len(d)), "dropped_sessions": int(dropped), "cells": cells,
           "night_share_of_total_drift": float(night_share), "night_premium_points_per_session": night_pts,
           "cost_assumption_round_trip_points": ROUND_TRIP_COST_POINTS, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_020_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_020_results.json'}")


if __name__ == "__main__":
    main()
