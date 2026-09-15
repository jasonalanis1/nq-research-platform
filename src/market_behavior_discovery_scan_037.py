"""
market_behavior_discovery_scan_037.py
========================================

Scan 037. DIRECTIONAL LANE TRIAL 1 (research/ledger/directional_lane.json,
memo research/infrastructure/refocus-2026-09-15.md s.4). Draws Entry 32
(map anchor M28) from research/idea_inventory.md:1876: the NYSE pre-holiday
effect, NQ. Mechanism doc written BEFORE this scan (and before the memo):
research/mechanisms/pre-holiday-effect-nq-m28.md, Section 9 ("Frozen scope
for the scan"). Sourced from the literature channel (Lakonishok & Smidt
1988, Ariel 1990) -- a non-state, calendar-anchored idea, eligible for the
directional lane under the memo's sourcing rule (mechanism/calendar/
structure only, never the Idea Factory state library).

Frozen scope (mechanism doc Section 9), Discovery slice ONLY
(2015-01-01 -> 2021-10-03, src/data_split.py), NQ daily RTH aggregation:
  daily RTH return = close(last RTH bar) - open(first RTH bar), same-day,
                      no overnight leg (a DIRECTIONAL same-session claim).
  NULL 1 (baseline_relative.py convention) = NQ's own unconditional daily
      RTH return over the same slice.
  Pre-holiday session  = the last Discovery session with RTH data strictly
      before an NYSE full-closure holiday date.
  Post-holiday session = the first Discovery session with RTH data strictly
      after an NYSE full-closure holiday date.
  NYSE holiday calendar = hardcoded below, the 9 recurring NYSE
      full-closure holidays (New Year's Day, MLK, Presidents, Good Friday,
      Memorial, Independence, Labor, Thanksgiving, Christmas; each on its
      OBSERVED closure date where a weekend shift applies) for calendar
      years 2015-2021. Juneteenth excluded throughout -- it was not an
      NYSE closure until June 2022, after this scan's entire Discovery
      slice; including it would be an anachronism, not a completeness fix.
      No ad hoc special closures (e.g. the December 2018 day of mourning)
      -- those are not part of the recurring calendar the literature
      describes and are out of the mechanism doc's frozen scope.
FOUR pre-registered cells (mechanism doc Section 9):
  1. Pre-holiday session return net of NULL 1, block-bootstrap CI  <== GATING (P1)
  2. Post-holiday session return net of NULL 1, reported (P2, specificity)
  3. Unconditional daily RTH return distribution mean (NULL 1 reference)
  4. Trade-count / thin-sample disclosure (falsifier c: usable count < ~40)
Statistical convention (mechanism doc Section 9, matching the M19/M22/M25
thin-annual-event-count family): block bootstrap, block=5, N_BOOT=3000,
SEED=20260913, 90% CI, "credible" = CI entirely on one side of zero.

This is the entry's ONE pre-registered Discovery-stage shot. One shot, no
new cells, no retuning after seeing results.

HOW TO RUN:
    TONY_PRODUCTION=1 python3 src/market_behavior_discovery_scan_037.py
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
SEED = 20260913
SCAN_KEY = "scan_037_2026-09-15"
THIN_SAMPLE_FLOOR = 40

# ---------------------------------------------------------------------------
# NYSE full-closure holiday calendar, 2015-01-01 -> 2021-10-03 (the Discovery
# slice), OBSERVED closure dates. Juneteenth excluded (not an NYSE holiday
# until 2022, per this file's docstring). Hardcoded once, not re-derived, so
# it cannot silently drift if a future data pull changes the frame.
# ---------------------------------------------------------------------------
NYSE_HOLIDAYS = [
    # 2015
    date(2015, 1, 1),   # New Year's Day
    date(2015, 1, 19),  # MLK Day
    date(2015, 2, 16),  # Presidents Day
    date(2015, 4, 3),   # Good Friday
    date(2015, 5, 25),  # Memorial Day
    date(2015, 7, 3),   # Independence Day (observed, Jul 4 = Sat)
    date(2015, 9, 7),   # Labor Day
    date(2015, 11, 26), # Thanksgiving
    date(2015, 12, 25), # Christmas
    # 2016
    date(2016, 1, 1),   # New Year's Day
    date(2016, 1, 18),  # MLK Day
    date(2016, 2, 15),  # Presidents Day
    date(2016, 3, 25),  # Good Friday
    date(2016, 5, 30),  # Memorial Day
    date(2016, 7, 4),   # Independence Day
    date(2016, 9, 5),   # Labor Day
    date(2016, 11, 24), # Thanksgiving
    date(2016, 12, 26), # Christmas (observed, Dec 25 = Sun)
    # 2017
    date(2017, 1, 2),   # New Year's Day (observed, Jan 1 = Sun)
    date(2017, 1, 16),  # MLK Day
    date(2017, 2, 20),  # Presidents Day
    date(2017, 4, 14),  # Good Friday
    date(2017, 5, 29),  # Memorial Day
    date(2017, 7, 4),   # Independence Day
    date(2017, 9, 4),   # Labor Day
    date(2017, 11, 23), # Thanksgiving
    date(2017, 12, 25), # Christmas
    # 2018
    date(2018, 1, 1),   # New Year's Day
    date(2018, 1, 15),  # MLK Day
    date(2018, 2, 19),  # Presidents Day
    date(2018, 3, 30),  # Good Friday
    date(2018, 5, 28),  # Memorial Day
    date(2018, 7, 4),   # Independence Day
    date(2018, 9, 3),   # Labor Day
    date(2018, 11, 22), # Thanksgiving
    date(2018, 12, 25), # Christmas
    # 2019
    date(2019, 1, 1),   # New Year's Day
    date(2019, 1, 21),  # MLK Day
    date(2019, 2, 18),  # Presidents Day
    date(2019, 4, 19),  # Good Friday
    date(2019, 5, 27),  # Memorial Day
    date(2019, 7, 4),   # Independence Day
    date(2019, 9, 2),   # Labor Day
    date(2019, 11, 28), # Thanksgiving
    date(2019, 12, 25), # Christmas
    # 2020
    date(2020, 1, 1),   # New Year's Day
    date(2020, 1, 20),  # MLK Day
    date(2020, 2, 17),  # Presidents Day
    date(2020, 4, 10),  # Good Friday
    date(2020, 5, 25),  # Memorial Day
    date(2020, 7, 3),   # Independence Day (observed, Jul 4 = Sat)
    date(2020, 9, 7),   # Labor Day
    date(2020, 11, 26), # Thanksgiving
    date(2020, 12, 25), # Christmas
    # 2021 (Discovery ends 2021-10-03 -- Thanksgiving/Christmas fall after
    # the slice boundary and are correctly excluded, not an oversight)
    date(2021, 1, 1),   # New Year's Day
    date(2021, 1, 18),  # MLK Day
    date(2021, 2, 15),  # Presidents Day
    date(2021, 4, 2),   # Good Friday
    date(2021, 5, 31),  # Memorial Day
    date(2021, 7, 5),   # Independence Day (observed, Jul 4 = Sun)
    date(2021, 9, 6),   # Labor Day
]


def block_ci(v, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < BLOCK * 3:
        return [float("nan"), float("nan")]
    from baseline_relative import _block_means
    rng = np.random.default_rng(SEED)
    means = _block_means(v, BLOCK, N_BOOT, rng)
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


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
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 037 (DIRECTIONAL LANE TRIAL 1")
    print("Entry 32 / map M28: NYSE pre-holiday effect, NQ)")
    print("=" * 78)

    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_037.py", symbol="NQ")
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
    session_dates = sorted(d.index.normalize().unique())
    session_date_set = set(pd.Timestamp(x).date() for x in session_dates)
    print(f"Discovery RTH sessions usable: {len(d)}")

    pre_dates, post_dates, holidays_matched = [], [], 0
    for h in NYSE_HOLIDAYS:
        prior = [x for x in session_date_set if x < h]
        after = [x for x in session_date_set if x > h]
        if not prior or not after:
            continue  # holiday outside the Discovery data range on one side
        holidays_matched += 1
        pre_dates.append(max(prior))
        post_dates.append(min(after))
    pre_dates = sorted(set(pre_dates))
    post_dates = sorted(set(post_dates))

    pre_returns = d.loc[[pd.Timestamp(x) for x in pre_dates if pd.Timestamp(x) in d.index], "rth_return"].to_numpy()
    post_returns = d.loc[[pd.Timestamp(x) for x in post_dates if pd.Timestamp(x) in d.index], "rth_return"].to_numpy()
    all_returns = d["rth_return"].to_numpy()

    print(f"NYSE holidays in calendar list: {len(NYSE_HOLIDAYS)}; matched inside Discovery data on both sides: {holidays_matched}")
    print(f"Pre-holiday sessions (unique): {len(pre_dates)}; post-holiday sessions (unique): {len(post_dates)}")

    c1 = cell_vs_null1(pre_returns, all_returns)
    c1["cell"] = "1_pre_holiday_vs_null1_GATING"
    c2 = cell_vs_null1(post_returns, all_returns)
    c2["cell"] = "2_post_holiday_vs_null1_specificity"
    c3 = {"cell": "3_null1_reference_unconditional_daily_rth_return",
          "n": int(len(all_returns)), "mean": float(np.nanmean(all_returns))}
    thin = len(pre_dates) < THIN_SAMPLE_FLOOR
    c4 = {"cell": "4_thin_sample_disclosure", "n_pre_holiday_sessions": int(len(pre_dates)),
          "floor": THIN_SAMPLE_FLOOR, "thin_sample": bool(thin),
          "note": ("THIN SAMPLE: usable pre-holiday count is below the ~40-session floor "
                    "(mechanism doc falsifier c), disclosed per the M19 convention."
                    if thin else "Usable pre-holiday count clears the thin-sample floor.")}

    p1_pass = bool(c1["credible"] and c1["ci_90"][0] > 0)
    p2_also_elevated = bool(c2["credible"] and c2["ci_90"][0] > 0)
    if thin:
        verdict = "THIN_SAMPLE_DISCLOSED"
    elif not p1_pass:
        verdict = "P1_FAIL"
    elif p2_also_elevated:
        verdict = "P1_PASS_NOT_SPECIFIC"
    else:
        verdict = "P1_PASS_SPECIFIC"
    notes = {
        "THIN_SAMPLE_DISCLOSED": "Usable pre-holiday count below the pre-registered thin-sample floor; disclosed, not a pass or fail on its own (falsifier c).",
        "P1_FAIL": "Pre-holiday session return CI vs NQ's own unconditional daily RTH return includes zero (or is credibly negative): the documented equity pre-holiday effect does not transfer to NQ futures at this data ceiling. Closes per falsifier (a).",
        "P1_PASS_NOT_SPECIFIC": "P1 passes but the post-holiday session shows the same elevation (falsifier b): more likely generic holiday-adjacent thin-volume noise than a pre-holiday-specific effect.",
        "P1_PASS_SPECIFIC": "P1 passes and the post-holiday session does NOT show the same elevation: a specific pre-holiday effect, gating prediction holds. Advance to Statistical per pipeline order.",
    }[verdict]

    print("\n--- CELLS -------------------------------------------------------")
    for c in (c1, c2):
        print(f"{c['cell']}")
        print(f"    signal_mean {c['signal_mean']:+.4f}  null1_mean {c['null1_mean']:+.4f}  (n={c['n']})")
        print(f"    diff {c['diff']:+.4f}  ci_90 ({c['ci_90'][0]:+.4f},{c['ci_90'][1]:+.4f})  -> {c['direction']}")
    print(f"{c3['cell']}: mean {c3['mean']:+.4f} (n={c3['n']})")
    print(f"{c4['cell']}: n_pre={c4['n_pre_holiday_sessions']} floor={c4['floor']} thin={c4['thin_sample']}")
    print(f"\nVERDICT: {verdict}\n  {notes}")

    result = {"scan": SCAN_KEY, "entry": 32, "map_anchor": "M28",
              "mechanism_doc": "research/mechanisms/pre-holiday-effect-nq-m28.md",
              "slice": "discovery", "block": BLOCK, "n_boot": N_BOOT, "seed": SEED,
              "cells": [c1, c2, c3, c4],
              "p1_gating_passes": p1_pass,
              "verdict": verdict, "note": notes,
              "rule": "One shot, frozen scope (mechanism doc Section 9). Four cells, one gating. "
                     "No new cells and no retuning after seeing results."}
    out = DATA_DIR / f"{SCAN_KEY}_results.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
