"""
market_behavior_discovery_scan_041.py
========================================

Scan 041. DIRECTIONAL LANE TRIAL 5 (research/ledger/directional_lane.json,
memo research/infrastructure/refocus-2026-09-15.md s.4). Draws Entry 65
(map anchor M35) from research/idea_inventory.md: the semi-monthly effect
on NQ RTH return direction. Mechanism doc written BEFORE this scan:
research/mechanisms/semi-monthly-effect-nq-m35.md, Section 9 ("Frozen
scope for the scan"). Sourced from the literature channel (Ariel 1987
Journal of Financial Economics; Lakonishok and Smidt 1988 Review of
Financial Studies) -- a non-state, calendar-anchored idea, eligible for
the directional lane under the memo's sourcing rule.

Frozen scope (mechanism doc Section 9), Discovery slice ONLY
(2015-01-01 -> 2021-10-03, src/data_split.py), NQ daily RTH aggregation:
  daily RTH return = close(last RTH bar) - open(first RTH bar), same-day,
                      no overnight leg (house convention, matches
                      scan_037/038/039/040 and market_state_primitives.py).
  trading-day-of-month = 1-indexed count of RTH sessions within each
      calendar month, in session order (no lookahead -- known trivially
      from the calendar).
  FIRST HALF = trading-day-of-month 1-9 (Ariel's own window length).
  SECOND HALF = trading-day-of-month 10+.
  NULL 1 = NQ's own unconditional daily RTH return, all Discovery
      sessions (same NULL 1 convention as scan_039/M33).
FOUR pre-registered cells (mechanism doc Section 9):
  1. First-half sessions mean RTH return net of NULL 1, block-bootstrap
     CI                                                      <== GATING (P1)
  2. Second-half sessions mean RTH return net of NULL 1, reported
     (P2, specificity)
  3. First-half years (2015-2018) vs second-half years (2018-2021) of
     the first-half-of-month effect, both net of NULL 1, reported
     descriptive (P3, decay check)
Plus reference/count cells (NULL 1 mean, session counts per group).
Statistical convention: block bootstrap, block=9 (window length, "block
= overlap length" rule), N_BOOT=3000, SEED=20260916, 90% CI, "credible"
= CI entirely on one side of zero.

This is the entry's ONE pre-registered Discovery-stage shot. One shot,
no new cells, no retuning after seeing results.

HOW TO RUN:
    TONY_PRODUCTION=1 python3 src/market_behavior_discovery_scan_041.py
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
BLOCK = 9
N_BOOT = 3000
SEED = 20260916
SCAN_KEY = "scan_041_2026-09-16"
FIRST_HALF_LEN = 9
THIN_SAMPLE_FLOOR = 40


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
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 041 (DIRECTIONAL LANE TRIAL 5")
    print("Entry 65 / map M35: Semi-monthly effect on NQ RTH return direction)")
    print("=" * 78)

    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_041.py", symbol="NQ")
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

    # trading-day-of-month: 1-indexed session count within each calendar month
    d["year_month"] = d.index.to_period("M")
    d["tdom"] = d.groupby("year_month").cumcount() + 1

    all_returns = d["rth_return"].to_numpy()

    first_half_mask = d["tdom"] <= FIRST_HALF_LEN
    second_half_mask = ~first_half_mask
    first_half_vals = d.loc[first_half_mask, "rth_return"].to_numpy()
    second_half_vals = d.loc[second_half_mask, "rth_return"].to_numpy()

    print(f"First-half-of-month sessions (tdom 1-{FIRST_HALF_LEN}): {len(first_half_vals)}")
    print(f"Second-half-of-month sessions (tdom {FIRST_HALF_LEN + 1}+): {len(second_half_vals)}")

    c1 = cell_vs_null1(first_half_vals, all_returns)
    c1["cell"] = "1_first_half_of_month_vs_null1_daily_GATING"

    c2 = cell_vs_null1(second_half_vals, all_returns)
    c2["cell"] = "2_second_half_of_month_vs_null1_daily_specificity"

    # P3: first-half vs second-half of Discovery YEARS, applied to the
    # first-half-of-month effect (decay check), both net of NULL 1.
    years = d.index.year
    year_list = sorted(set(years))
    midpoint = len(year_list) // 2
    early_years = set(year_list[:midpoint])
    late_years = set(year_list[midpoint:])
    early_mask = first_half_mask & d.index.year.isin(early_years)
    late_mask = first_half_mask & d.index.year.isin(late_years)
    early_vals = d.loc[early_mask, "rth_return"].to_numpy()
    late_vals = d.loc[late_mask, "rth_return"].to_numpy()
    c3a = cell_vs_null1(early_vals, all_returns)
    c3a["cell"] = f"3a_first_half_years_{min(early_years)}-{max(early_years)}_first_half_of_month_vs_null1_descriptive"
    c3b = cell_vs_null1(late_vals, all_returns)
    c3b["cell"] = f"3b_second_half_years_{min(late_years)}-{max(late_years)}_first_half_of_month_vs_null1_descriptive"

    c4 = {"cell": "4_null1_reference_unconditional_daily_rth_return",
          "n": int(len(all_returns)), "mean": float(np.nanmean(all_returns)) if len(all_returns) else float("nan")}

    thin = len(first_half_vals) < THIN_SAMPLE_FLOOR
    c5 = {"cell": "5_thin_sample_disclosure", "n_first_half_sessions": int(len(first_half_vals)),
          "floor": THIN_SAMPLE_FLOOR, "thin_sample": bool(thin),
          "note": ("Session count clears the ordinary n=40 floor comfortably -- expected, this fires "
                    "~9x per month across ~81 months of the Discovery slice, the best-powered directional-lane "
                    "entry sourced so far." if not thin else
                    "THIN SAMPLE -- unexpected, investigate before treating any result as final.")}

    p1_pass = bool(c1["credible"] and c1["ci_90"][0] > 0)  # predicted direction: POSITIVE
    if thin:
        verdict = "THIN_SAMPLE_DISCLOSED"
    elif not p1_pass:
        verdict = "P1_FAIL"
    else:
        verdict = "P1_PASS"
    notes = {
        "THIN_SAMPLE_DISCLOSED": "Unexpected thin sample -- reported as a descriptive lead only, not a pass or fail on its own.",
        "P1_FAIL": "First-half-of-month CI vs NQ's own unconditional daily RTH return includes zero or is credibly negative "
                   "(not the predicted POSITIVE direction): the documented semi-monthly effect does not transfer to NQ "
                   "futures at this data ceiling. Closes per falsifier (a).",
        "P1_PASS": "First-half-of-month return is credibly POSITIVE vs NQ's own unconditional daily RTH return, as "
                   "predicted. Read against P2 (second-half specificity) before treating this as clean -- falsifier (b).",
    }[verdict]

    print("\n--- CELLS -------------------------------------------------------")
    for c in (c1, c2, c3a, c3b):
        print(f"{c['cell']}")
        if not np.isnan(c["signal_mean"]):
            print(f"    signal_mean {c['signal_mean']:+.4f}  null1_mean {c['null1_mean']:+.4f}  (n={c['n']})")
            print(f"    diff {c['diff']:+.4f}  ci_90 ({c['ci_90'][0]:+.4f},{c['ci_90'][1]:+.4f})  -> {c['direction']}")
        else:
            print("    insufficient data")
    print(f"{c4['cell']}: mean {c4['mean']:+.4f} (n={c4['n']})")
    print(f"{c5['cell']}: n_first_half_sessions={c5['n_first_half_sessions']} floor={c5['floor']} thin={c5['thin_sample']}")
    print(f"\nVERDICT: {verdict}\n  {notes}")

    result = {"scan": SCAN_KEY, "entry": 65, "map_anchor": "M35",
              "mechanism_doc": "research/mechanisms/semi-monthly-effect-nq-m35.md",
              "slice": "discovery", "block": BLOCK, "n_boot": N_BOOT, "seed": SEED,
              "cells": [c1, c2, c3a, c3b, c4, c5],
              "p1_gating_passes": p1_pass,
              "verdict": verdict, "note": notes,
              "rule": "One shot, frozen scope (mechanism doc Section 9). Four gating/reported cells "
                     "plus reference and thin-sample disclosure. No new cells and no retuning after "
                     "seeing results."}
    out = DATA_DIR / f"{SCAN_KEY}_results.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
