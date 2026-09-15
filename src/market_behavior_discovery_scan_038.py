"""
market_behavior_discovery_scan_038.py
========================================

Scan 038. DIRECTIONAL LANE TRIAL 2 (research/ledger/directional_lane.json,
memo research/infrastructure/refocus-2026-09-15.md s.4). Draws Entry 62
(map anchor M32) from research/idea_inventory.md: the US daylight-saving-
time transition anomaly, NQ. Mechanism doc written BEFORE this scan:
research/mechanisms/dst-anomaly-nq-m32.md, Section 9 ("Frozen scope for
the scan"). Sourced from the literature channel (Kamstra, Kramer and
Levi 2000 AER, "Losing Sleep at the Market") -- a non-state,
calendar-anchored idea, eligible for the directional lane under the
memo's sourcing rule (mechanism/calendar/structure only, never the Idea
Factory state library).

Frozen scope (mechanism doc Section 9), Discovery slice ONLY
(2015-01-01 -> 2021-10-03, src/data_split.py), NQ daily RTH aggregation:
  daily RTH return = close(last RTH bar) - open(first RTH bar), same-day,
                      no overnight leg.
  Transition week = the 5 consecutive usable Discovery RTH session dates
      starting at the first usable session date on or after each US DST
      transition Sunday (2nd Sunday of March, 1st Sunday of November,
      statutory rule unchanged since the Energy Policy Act of 2005).
      DST transition Sundays hardcoded below for 2015-2021 (the
      Discovery slice) -- computable, not estimated or fit.
  NULL 1 = NQ's own unconditional 5-session ROLLING return: the sum of
      daily RTH returns over every consecutive 5-session window in the
      Discovery slice (overlapping windows, standard rolling-sum
      convention), block-bootstrap CI on the difference of means.
FIVE pre-registered cells (mechanism doc Section 9):
  1. Transition-week cumulative return net of NULL 1, block-bootstrap CI <== GATING (P1)
  2. Transition-Monday-only return net of NQ's own unconditional daily
     RTH return, reported (P2, literature fidelity)
  3. Spring-transition weeks vs fall-transition weeks, both net of
     NULL 1, reported descriptive (P3)
  4. Unconditional 5-session rolling return distribution mean (NULL 1
     reference)
  5. Transition-week-count / thin-sample disclosure (falsifier c:
     usable transition-week count < 12)
Statistical convention (mechanism doc Section 9, matching the
M19/M22/M25/M28 thin-annual-event-count family): block bootstrap,
block=5, N_BOOT=3000, SEED=20260916, 90% CI, "credible" = CI entirely
on one side of zero.

This is the entry's ONE pre-registered Discovery-stage shot. One shot,
no new cells, no retuning after seeing results.

HOW TO RUN:
    TONY_PRODUCTION=1 python3 src/market_behavior_discovery_scan_038.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
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
SCAN_KEY = "scan_038_2026-09-16"
THIN_SAMPLE_FLOOR = 12  # transition weeks (mechanism doc Section 9 / falsifier c)

# ---------------------------------------------------------------------------
# US DST transition Sundays, 2015-01-01 -> 2021-10-03 (the Discovery
# slice). Statutory rule since the Energy Policy Act of 2005: spring
# forward the 2nd Sunday of March, fall back the 1st Sunday of November.
# Fall 2021 (Nov 7, 2021) is after the Discovery slice boundary and is
# correctly excluded, not an oversight. Hardcoded once, not re-derived.
# ---------------------------------------------------------------------------
DST_TRANSITIONS = [
    ("spring", date(2015, 3, 8)),
    ("fall",   date(2015, 11, 1)),
    ("spring", date(2016, 3, 13)),
    ("fall",   date(2016, 11, 6)),
    ("spring", date(2017, 3, 12)),
    ("fall",   date(2017, 11, 5)),
    ("spring", date(2018, 3, 11)),
    ("fall",   date(2018, 11, 4)),
    ("spring", date(2019, 3, 10)),
    ("fall",   date(2019, 11, 3)),
    ("spring", date(2020, 3, 8)),
    ("fall",   date(2020, 11, 1)),
    ("spring", date(2021, 3, 14)),
    # fall 2021 (Nov 7, 2021) is outside the Discovery slice (ends 2021-10-03)
]


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
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 038 (DIRECTIONAL LANE TRIAL 2")
    print("Entry 62 / map M32: US daylight-saving-time transition anomaly, NQ)")
    print("=" * 78)

    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_038.py", symbol="NQ")
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
    session_dates = list(d.index)
    print(f"Discovery RTH sessions usable: {len(d)}")

    # NULL 1: unconditional 5-session rolling cumulative return, all overlapping windows
    daily = d["rth_return"].to_numpy()
    roll5_all = np.array([daily[i:i + 5].sum() for i in range(len(daily) - 4)])

    # Transition weeks: first usable session date >= transition Sunday, then
    # the next 5 consecutive usable session dates starting there.
    week_returns, monday_returns, week_kinds, matched = [], [], [], 0
    for kind, sunday in DST_TRANSITIONS:
        after = [i for i, dt in enumerate(session_dates) if dt.date() >= sunday]
        if not after:
            continue
        start_idx = after[0]
        if start_idx + 5 > len(session_dates):
            continue  # not enough sessions left in the slice for a full week
        matched += 1
        week = daily[start_idx:start_idx + 5]
        week_returns.append(float(week.sum()))
        monday_returns.append(float(daily[start_idx]))
        week_kinds.append(kind)

    week_returns = np.array(week_returns)
    monday_returns = np.array(monday_returns)
    week_kinds = np.array(week_kinds)

    print(f"DST transitions in calendar list: {len(DST_TRANSITIONS)}; matched inside Discovery data: {matched}")
    print(f"Transition weeks (unique): {len(week_returns)}")

    c1 = cell_vs_null1(week_returns, roll5_all)
    c1["cell"] = "1_transition_week_vs_null1_GATING"
    c2 = cell_vs_null1(monday_returns, daily)
    c2["cell"] = "2_transition_monday_only_vs_null1_daily_specificity"
    spring_returns = week_returns[week_kinds == "spring"]
    fall_returns = week_returns[week_kinds == "fall"]
    c3_spring = cell_vs_null1(spring_returns, roll5_all)
    c3_spring["cell"] = "3a_spring_transition_weeks_vs_null1_descriptive"
    c3_fall = cell_vs_null1(fall_returns, roll5_all)
    c3_fall["cell"] = "3b_fall_transition_weeks_vs_null1_descriptive"
    c4 = {"cell": "4_null1_reference_unconditional_5session_rolling_return",
          "n": int(len(roll5_all)), "mean": float(np.nanmean(roll5_all))}
    thin = len(week_returns) < THIN_SAMPLE_FLOOR
    c5 = {"cell": "5_thin_sample_disclosure", "n_transition_weeks": int(len(week_returns)),
          "floor": THIN_SAMPLE_FLOOR, "thin_sample": bool(thin),
          "note": ("THIN SAMPLE: usable transition-week count is below the pre-registered "
                    "12-week floor (mechanism doc falsifier c), disclosed per the M19 convention."
                    if thin else "Usable transition-week count clears the thin-sample floor.")}

    p1_pass = bool(c1["credible"] and c1["ci_90"][1] < 0)  # predicted direction: NEGATIVE
    if thin:
        verdict = "THIN_SAMPLE_DISCLOSED"
    elif not p1_pass:
        verdict = "P1_FAIL"
    else:
        verdict = "P1_PASS"
    notes = {
        "THIN_SAMPLE_DISCLOSED": "Usable transition-week count below the pre-registered thin-sample floor; disclosed, not a pass or fail on its own (falsifier c).",
        "P1_FAIL": "Transition-week cumulative return CI vs NQ's own unconditional 5-session rolling return includes zero or is credibly positive (wrong-signed vs the predicted NEGATIVE direction): the documented daylight-saving anomaly does not transfer to NQ futures at this data ceiling. Closes per falsifier (a).",
        "P1_PASS": "Transition-week cumulative return is credibly NEGATIVE vs NQ's own unconditional 5-session rolling return, as predicted. Advance to Statistical per pipeline order.",
    }[verdict]

    print("\n--- CELLS -------------------------------------------------------")
    for c in (c1, c2, c3_spring, c3_fall):
        print(f"{c['cell']}")
        print(f"    signal_mean {c['signal_mean']:+.4f}  null1_mean {c['null1_mean']:+.4f}  (n={c['n']})")
        print(f"    diff {c['diff']:+.4f}  ci_90 ({c['ci_90'][0]:+.4f},{c['ci_90'][1]:+.4f})  -> {c['direction']}")
    print(f"{c4['cell']}: mean {c4['mean']:+.4f} (n={c4['n']})")
    print(f"{c5['cell']}: n_weeks={c5['n_transition_weeks']} floor={c5['floor']} thin={c5['thin_sample']}")
    print(f"\nVERDICT: {verdict}\n  {notes}")

    result = {"scan": SCAN_KEY, "entry": 62, "map_anchor": "M32",
              "mechanism_doc": "research/mechanisms/dst-anomaly-nq-m32.md",
              "slice": "discovery", "block": BLOCK, "n_boot": N_BOOT, "seed": SEED,
              "cells": [c1, c2, c3_spring, c3_fall, c4, c5],
              "p1_gating_passes": p1_pass,
              "verdict": verdict, "note": notes,
              "rule": "One shot, frozen scope (mechanism doc Section 9). Five cells, one gating. "
                     "No new cells and no retuning after seeing results."}
    out = DATA_DIR / f"{SCAN_KEY}_results.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
