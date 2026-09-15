"""
market_behavior_discovery_scan_039.py
========================================

Scan 039. DIRECTIONAL LANE TRIAL 3 (research/ledger/directional_lane.json,
memo research/infrastructure/refocus-2026-09-15.md s.4). Draws Entry 63
(map anchor M33) from research/idea_inventory.md: the weekend/Monday
effect on NQ RTH return direction. Mechanism doc written BEFORE this
scan: research/mechanisms/weekend-effect-nq-m33.md, Section 9 ("Frozen
scope for the scan"). Sourced from the literature channel (French 1980
JFE, "Stock Returns and the Weekend Effect"; Rogalski 1984 JF; Kamara
1997 JFQA) -- a non-state, calendar-anchored idea, eligible for the
directional lane under the memo's sourcing rule (mechanism/calendar/
structure only, never the Idea Factory state library).

Frozen scope (mechanism doc Section 9), Discovery slice ONLY
(2015-01-01 -> 2021-10-03, src/data_split.py), NQ daily RTH aggregation:
  daily RTH return = close(last RTH bar) - open(first RTH bar), same-day,
                      no overnight leg.
  overnight/gap return = open(first RTH bar, day t) - close(last RTH bar,
                      day t-1), the existing project-wide overnight
                      convention.
  Monday = day_of_week == 0 (market_state_primitives.py convention),
      restricted to sessions that are the first usable RTH session of
      their calendar week (excludes weeks where Monday itself is an
      NYSE holiday and Tuesday effectively opens the week -- the
      standard weekend-effect convention, matching Rogalski 1984's own
      "first trading day of the week" definition rather than a strict
      calendar-Monday one).
  NULL 1 (daily) = NQ's own unconditional daily RTH return, all Discovery
      sessions.
  NULL 1 (overnight) = NQ's own unconditional overnight/gap return, all
      Discovery sessions.
THREE pre-registered cells (mechanism doc Section 9):
  1. Monday (first-trading-day-of-week) same-day RTH return net of
     NULL 1 (daily), block-bootstrap CI                       <== GATING (P1)
  2. Friday-close-to-Monday-open gap return net of NULL 1 (overnight),
     reported (P2, Rogalski 1984 specificity check)
  3. First-half vs second-half Discovery-slice split of the Monday
     effect, both net of NULL 1 (daily), reported descriptive (P3,
     Kamara 1997 decay check)
Plus reference/count cells (NULL 1 means, Monday-session count).
Statistical convention: block bootstrap, block=5 (standard weekly-cycle
block, matching this project's day-of-week-adjacent convention, e.g.
Entry 4's own weekly framing), N_BOOT=3000, SEED=20260916, 90% CI,
"credible" = CI entirely on one side of zero.

This is the entry's ONE pre-registered Discovery-stage shot. One shot,
no new cells, no retuning after seeing results.

HOW TO RUN:
    TONY_PRODUCTION=1 python3 src/market_behavior_discovery_scan_039.py
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
BLOCK = 5
N_BOOT = 3000
SEED = 20260916
SCAN_KEY = "scan_039_2026-09-16"
THIN_SAMPLE_FLOOR = 40  # ordinary project floor -- this fires weekly, not expected to bind


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
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 039 (DIRECTIONAL LANE TRIAL 3")
    print("Entry 63 / map M33: weekend/Monday effect on NQ RTH return direction)")
    print("=" * 78)

    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_039.py", symbol="NQ")
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
        rows.append({"date": pd.Timestamp(day), "rth_open": o, "rth_close": c, "rth_return": c - o})
    d = pd.DataFrame(rows).set_index("date").sort_index()
    session_dates = list(d.index)
    print(f"Discovery RTH sessions usable: {len(d)}")

    # Overnight/gap return: today's RTH open - prior usable session's RTH close.
    d["overnight_return"] = d["rth_open"] - d["rth_close"].shift(1)

    # "First trading day of the week": a session whose calendar week (ISO
    # year, ISO week) differs from the immediately preceding usable
    # session's calendar week -- the Rogalski (1984) convention, robust to
    # Monday NYSE holidays (Tuesday becomes the week's first session).
    iso = d.index.isocalendar()
    week_key = list(zip(iso["year"], iso["week"]))
    is_week_start = [True] + [week_key[i] != week_key[i - 1] for i in range(1, len(week_key))]
    d["is_week_start"] = is_week_start
    d["dow"] = d.index.dayofweek  # 0 = Monday

    monday_mask = d["is_week_start"] & (d["dow"] == 0)
    n_monday_not_dow0 = int((d["is_week_start"] & (d["dow"] != 0)).sum())
    print(f"Week-start sessions where dow==Monday: {int(monday_mask.sum())}; "
          f"week-start sessions on a non-Monday weekday (post-Monday-holiday): {n_monday_not_dow0}")

    monday_rth = d.loc[monday_mask, "rth_return"].to_numpy()
    monday_overnight = d.loc[monday_mask, "overnight_return"].dropna().to_numpy()
    all_rth = d["rth_return"].to_numpy()
    all_overnight = d["overnight_return"].dropna().to_numpy()

    c1 = cell_vs_null1(monday_rth, all_rth)
    c1["cell"] = "1_monday_rth_return_vs_null1_daily_GATING"
    c2 = cell_vs_null1(monday_overnight, all_overnight)
    c2["cell"] = "2_friday_close_to_monday_open_gap_vs_null1_overnight_specificity"

    midpoint = session_dates[len(session_dates) // 2]
    first_half_mask = monday_mask & (d.index <= midpoint)
    second_half_mask = monday_mask & (d.index > midpoint)
    first_half_all_mask = d.index <= midpoint
    second_half_all_mask = d.index > midpoint
    c3a = cell_vs_null1(d.loc[first_half_mask, "rth_return"].to_numpy(),
                          d.loc[first_half_all_mask, "rth_return"].to_numpy())
    c3a["cell"] = "3a_first_half_discovery_monday_vs_null1_descriptive"
    c3b = cell_vs_null1(d.loc[second_half_mask, "rth_return"].to_numpy(),
                          d.loc[second_half_all_mask, "rth_return"].to_numpy())
    c3b["cell"] = "3b_second_half_discovery_monday_vs_null1_descriptive"

    c4 = {"cell": "4_null1_reference_unconditional_daily_rth_return",
          "n": int(len(all_rth)), "mean": float(np.nanmean(all_rth))}
    thin = len(monday_rth) < THIN_SAMPLE_FLOOR
    c5 = {"cell": "5_thin_sample_disclosure", "n_monday_sessions": int(len(monday_rth)),
          "floor": THIN_SAMPLE_FLOOR, "thin_sample": bool(thin),
          "note": ("THIN SAMPLE: Monday-session count is below the ordinary n=40 project floor -- unexpected for a "
                    "weekly-firing entry, disclosed per convention." if thin else
                    "Monday-session count clears the ordinary n=40 floor by a wide margin (weekly-firing entry).")}

    p1_pass = bool(c1["credible"] and c1["ci_90"][1] < 0)  # predicted direction: NEGATIVE
    if thin:
        verdict = "THIN_SAMPLE_DISCLOSED"
    elif not p1_pass:
        verdict = "P1_FAIL"
    else:
        verdict = "P1_PASS"
    notes = {
        "THIN_SAMPLE_DISCLOSED": "Monday-session count below the pre-registered floor; disclosed, not a pass or fail on its own.",
        "P1_FAIL": "Monday RTH return CI vs NQ's own unconditional daily RTH return includes zero or is credibly positive (wrong-signed vs the predicted NEGATIVE direction): the documented weekend/Monday effect does not transfer to NQ futures at this data ceiling. Closes per falsifier (a).",
        "P1_PASS": "Monday RTH return is credibly NEGATIVE vs NQ's own unconditional daily RTH return, as predicted. Advance to Statistical per pipeline order.",
    }[verdict]

    print("\n--- CELLS -------------------------------------------------------")
    for c in (c1, c2, c3a, c3b):
        print(f"{c['cell']}")
        print(f"    signal_mean {c['signal_mean']:+.4f}  null1_mean {c['null1_mean']:+.4f}  (n={c['n']})")
        print(f"    diff {c['diff']:+.4f}  ci_90 ({c['ci_90'][0]:+.4f},{c['ci_90'][1]:+.4f})  -> {c['direction']}")
    print(f"{c4['cell']}: mean {c4['mean']:+.4f} (n={c4['n']})")
    print(f"{c5['cell']}: n_monday={c5['n_monday_sessions']} floor={c5['floor']} thin={c5['thin_sample']}")
    print(f"\nVERDICT: {verdict}\n  {notes}")

    result = {"scan": SCAN_KEY, "entry": 63, "map_anchor": "M33",
              "mechanism_doc": "research/mechanisms/weekend-effect-nq-m33.md",
              "slice": "discovery", "block": BLOCK, "n_boot": N_BOOT, "seed": SEED,
              "cells": [c1, c2, c3a, c3b, c4, c5],
              "p1_gating_passes": p1_pass,
              "verdict": verdict, "note": notes,
              "rule": "One shot, frozen scope (mechanism doc Section 9). Three gating/reported cells "
                     "plus reference and thin-sample disclosure. No new cells and no retuning after "
                     "seeing results."}
    out = DATA_DIR / f"{SCAN_KEY}_results.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
