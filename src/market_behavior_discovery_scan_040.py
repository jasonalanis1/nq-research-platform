"""
market_behavior_discovery_scan_040.py
========================================

Scan 040. DIRECTIONAL LANE TRIAL 4 (research/ledger/directional_lane.json,
memo research/infrastructure/refocus-2026-09-15.md s.4). Draws Entry 64
(map anchor M34) from research/idea_inventory.md: the Santa Claus Rally /
turn-of-year effect on NQ RTH return direction. Mechanism doc written
BEFORE this scan: research/mechanisms/santa-claus-rally-nq-m34.md,
Section 9 ("Frozen scope for the scan"). Sourced from the literature
channel (Hirsch 1972 Stock Trader's Almanac; Bhabra, Dhillon and Ramirez
1999 Financial Review) -- a non-state, calendar-anchored idea, eligible
for the directional lane under the memo's sourcing rule.

Frozen scope (mechanism doc Section 9), Discovery slice ONLY
(2015-01-01 -> 2021-10-03, src/data_split.py), NQ daily RTH aggregation:
  daily RTH return = close(last RTH bar) - open(first RTH bar), same-day,
                      no overnight leg (house convention, matches
                      scan_037/038/039 and market_state_primitives.py).
  Santa Claus Rally window = last 5 RTH sessions of the calendar year
      + first 2 RTH sessions of the following January (Hirsch 1972
      definition), cumulative RTH return (sum of daily RTH returns).
  NULL 1 = NQ's own unconditional 7-session rolling RTH return
      (rolling sum of 7 consecutive daily RTH returns), all Discovery
      sessions.
THREE pre-registered cells (mechanism doc Section 9):
  1. Santa Claus Rally window cumulative return net of NULL 1,
     block-bootstrap CI                                     <== GATING (P1)
  2. December-leg-only vs January-leg-only, each net of NULL 1's
     per-session mean scaled to leg length, reported (P2, specificity)
  3. First-half (years 2015-2017) vs second-half (years 2018-2020) of
     the window observations, both net of NULL 1, reported descriptive
     (P3, decay check)
Plus reference/count cells (NULL 1 mean, window-year count).
THIN-SAMPLE OVERRIDE (mechanism doc Section 5c, pre-registered): this
window fires once per year -- only ~6 complete windows exist in the
Discovery slice. n < 40 (the ordinary project floor) OVERRIDES the
ordinary P1_PASS/P1_FAIL verdict; verdict is reported as
THIN_SAMPLE_DISCLOSED regardless of P1's own result, same override
scan_039 used for its (non-binding) thin-sample check.
Statistical convention: block bootstrap, block=7 (window length, "block
= overlap length" rule), N_BOOT=3000, SEED=20260916, 90% CI, "credible"
= CI entirely on one side of zero.

This is the entry's ONE pre-registered Discovery-stage shot. One shot,
no new cells, no retuning after seeing results.

HOW TO RUN:
    TONY_PRODUCTION=1 python3 src/market_behavior_discovery_scan_040.py
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
from baseline_relative import block_bootstrap_diff_ci  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BLOCK = 7
N_BOOT = 3000
SEED = 20260916
SCAN_KEY = "scan_040_2026-09-16"
THIN_SAMPLE_FLOOR = 40  # ordinary project floor -- this fires once a year, EXPECTED to bind
DEC_LEG = 5
JAN_LEG = 2
WINDOW_LEN = DEC_LEG + JAN_LEG  # 7


def cell_vs_null1(signal_vals, all_vals):
    """NULL 1 convention (baseline_relative.py): mean(signal) - mean(all),
    with its own block-bootstrap CI on the difference."""
    s = np.asarray([x for x in signal_vals if not np.isnan(x)], float)
    a = np.asarray([x for x in all_vals if not np.isnan(x)], float)
    if len(s) < 2 or len(a) < 2:
        return {"n": int(len(s)), "signal_mean": float("nan"), "null1_mean": float("nan"),
                "diff": float("nan"), "ci_90": [float("nan"), float("nan")], "credible": False, "direction": "n/a"}
    diff = float(s.mean() - a.mean())
    lo, hi = block_bootstrap_diff_ci(s, a, block=BLOCK, n_bootstrap=N_BOOT, seed=SEED)
    cred = (not np.isnan(lo)) and ((lo > 0) or (hi < 0))
    return {"n": int(len(s)), "signal_mean": float(s.mean()), "null1_mean": float(a.mean()),
            "diff": diff, "ci_90": [lo, hi], "credible": bool(cred),
            "direction": "positive" if cred and lo > 0 else ("negative" if cred else "null")}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 040 (DIRECTIONAL LANE TRIAL 4")
    print("Entry 64 / map M34: Santa Claus Rally / turn-of-year effect on NQ RTH return)")
    print("=" * 78)

    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_040.py", symbol="NQ")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(nq_all)

    rows = []
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty or len(rth) < 200:
            continue
        o = float(rth["Open"].iloc[0])
        c = float(rth["Close"].iloc[-1])
        rows.append({"date": pd.Timestamp(day), "rth_return": c - o})
    d = pd.DataFrame(rows).set_index("date").sort_index()
    print(f"Discovery RTH sessions usable: {len(d)}")

    # NULL 1: NQ's own unconditional rolling 7-session RTH return (non-overlapping
    # blocks, matching the window's own cumulative-return construction).
    daily = d["rth_return"].to_numpy()
    n_full_blocks = len(daily) // WINDOW_LEN
    all_7session = np.array([daily[i * WINDOW_LEN:(i + 1) * WINDOW_LEN].sum()
                              for i in range(n_full_blocks)])

    # Santa Claus Rally windows: last 5 RTH sessions of each calendar year +
    # first 2 RTH sessions of the following January, fully inside the
    # Discovery slice (both legs present).
    years = sorted(set(d.index.year))
    window_rows = []
    for y in years:
        dec_sessions = d.loc[(d.index.year == y) & (d.index.month == 12)]
        jan_sessions = d.loc[(d.index.year == y + 1) & (d.index.month == 1)]
        if len(dec_sessions) < DEC_LEG or len(jan_sessions) < JAN_LEG:
            continue  # incomplete leg (year boundary outside Discovery slice)
        dec_leg = dec_sessions["rth_return"].iloc[-DEC_LEG:]
        jan_leg = jan_sessions["rth_return"].iloc[:JAN_LEG]
        window_rows.append({
            "year": y,
            "dec_leg_sum": float(dec_leg.sum()),
            "jan_leg_sum": float(jan_leg.sum()),
            "window_sum": float(dec_leg.sum() + jan_leg.sum()),
        })
    w = pd.DataFrame(window_rows)
    print(f"Complete Santa Claus Rally windows in Discovery slice: {len(w)} (years: "
          f"{list(w['year']) if len(w) else '[]'})")

    window_sums = w["window_sum"].to_numpy() if len(w) else np.array([])

    c1 = cell_vs_null1(window_sums, all_7session)
    c1["cell"] = "1_santa_claus_window_vs_null1_7session_GATING"

    # P2: December leg vs January leg, each net of NULL 1's per-session mean
    # scaled to that leg's length.
    null1_per_session_mean = float(np.nanmean(daily))
    dec_leg_vals = w["dec_leg_sum"].to_numpy() if len(w) else np.array([])
    jan_leg_vals = w["jan_leg_sum"].to_numpy() if len(w) else np.array([])
    dec_null1_scaled = np.full(len(dec_leg_vals), null1_per_session_mean * DEC_LEG)
    jan_null1_scaled = np.full(len(jan_leg_vals), null1_per_session_mean * JAN_LEG)
    c2a = cell_vs_null1(dec_leg_vals, dec_null1_scaled)
    c2a["cell"] = "2a_december_leg_vs_null1_scaled_specificity"
    c2b = cell_vs_null1(jan_leg_vals, jan_null1_scaled)
    c2b["cell"] = "2b_january_leg_vs_null1_scaled_specificity"

    # P3: first-half vs second-half of window-years, both net of NULL 1
    # (whole-window baseline, same NULL 1 as P1).
    if len(w):
        midpoint_idx = len(w) // 2
        first_half = w.iloc[:midpoint_idx]["window_sum"].to_numpy()
        second_half = w.iloc[midpoint_idx:]["window_sum"].to_numpy()
    else:
        first_half = np.array([])
        second_half = np.array([])
    c3a = cell_vs_null1(first_half, all_7session)
    c3a["cell"] = "3a_first_half_window_years_vs_null1_descriptive"
    c3b = cell_vs_null1(second_half, all_7session)
    c3b["cell"] = "3b_second_half_window_years_vs_null1_descriptive"

    c4 = {"cell": "4_null1_reference_unconditional_7session_rth_return",
          "n": int(len(all_7session)), "mean": float(np.nanmean(all_7session)) if len(all_7session) else float("nan")}

    thin = len(window_sums) < THIN_SAMPLE_FLOOR
    c5 = {"cell": "5_thin_sample_disclosure", "n_window_years": int(len(window_sums)),
          "floor": THIN_SAMPLE_FLOOR, "thin_sample": bool(thin),
          "note": ("THIN SAMPLE (pre-registered, expected): the Santa Claus Rally window fires once a year -- "
                    "the Discovery slice contains too few complete windows to clear the ordinary n=40 floor. "
                    "A null here is far more likely to be UNDERPOWERED than a genuine absence of effect (mechanism "
                    "doc Section 5c). Per the frozen scope, THIS OVERRIDES the ordinary P1 pass/fail verdict below."
                    if thin else
                    "Window-year count clears the ordinary n=40 floor.")}

    p1_pass = bool(c1["credible"] and c1["ci_90"][0] > 0)  # predicted direction: POSITIVE
    if thin:
        verdict = "THIN_SAMPLE_DISCLOSED"
    elif not p1_pass:
        verdict = "P1_FAIL"
    else:
        verdict = "P1_PASS"
    notes = {
        "THIN_SAMPLE_DISCLOSED": "Window-year count is below the pre-registered n=40 floor (expected, disclosed in the mechanism "
                                  "doc before this scan ran) -- reported as a descriptive lead only, not a pass or fail on its own. "
                                  "P1's own credible/not-credible read is still reported below for completeness.",
        "P1_FAIL": "Santa Claus window CI vs NQ's own unconditional 7-session RTH return includes zero or is credibly negative "
                   "(wrong-signed vs the predicted POSITIVE direction): the documented turn-of-year effect does not transfer to "
                   "NQ futures at this data ceiling. Closes per falsifier (a).",
        "P1_PASS": "Santa Claus window return is credibly POSITIVE vs NQ's own unconditional 7-session RTH return, as predicted. "
                   "Advance to Statistical per pipeline order -- BUT read against the thin-sample floor.",
    }[verdict]

    print("\n--- CELLS -------------------------------------------------------")
    for c in (c1, c2a, c2b, c3a, c3b):
        print(f"{c['cell']}")
        if not np.isnan(c["signal_mean"]):
            print(f"    signal_mean {c['signal_mean']:+.4f}  null1_mean {c['null1_mean']:+.4f}  (n={c['n']})")
            print(f"    diff {c['diff']:+.4f}  ci_90 ({c['ci_90'][0]:+.4f},{c['ci_90'][1]:+.4f})  -> {c['direction']}")
        else:
            print("    insufficient data")
    print(f"{c4['cell']}: mean {c4['mean']:+.4f} (n={c4['n']})")
    print(f"{c5['cell']}: n_window_years={c5['n_window_years']} floor={c5['floor']} thin={c5['thin_sample']}")
    print(f"\nVERDICT: {verdict}\n  {notes}")

    result = {"scan": SCAN_KEY, "entry": 64, "map_anchor": "M34",
              "mechanism_doc": "research/mechanisms/santa-claus-rally-nq-m34.md",
              "slice": "discovery", "block": BLOCK, "n_boot": N_BOOT, "seed": SEED,
              "cells": [c1, c2a, c2b, c3a, c3b, c4, c5],
              "p1_gating_passes": p1_pass,
              "verdict": verdict, "note": notes,
              "window_years": w["year"].tolist() if len(w) else [],
              "rule": "One shot, frozen scope (mechanism doc Section 9). Three gating/reported cells "
                     "plus reference and thin-sample disclosure (pre-registered override). No new cells "
                     "and no retuning after seeing results."}
    out = DATA_DIR / f"{SCAN_KEY}_results.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
