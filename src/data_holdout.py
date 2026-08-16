"""
data_holdout.py
=================

WHAT THIS FILE DOES (plain English):
Draws a hard, fixed line in the real price data: everything from
2026-04-07 onward is HOLDOUT data, set aside and untouched by normal
strategy testing. Everything before that is RESEARCH data -- the only
data normal testing is allowed to use.

WHY THIS EXISTS (added 2026-08-16, per docs/RESEARCH_ARCHITECTURE.md's
architecture review, recommendation #1): every strategy test run in this
project so far has used 100% of whatever real data existed at the time.
As more data got pulled, we re-tested the SAME variants on a bigger
window each time -- never checked anything against data that hadn't
already been looked at. That means there has never been a genuine
out-of-sample check, and there currently isn't any unseen data left to
eventually do one with. This file fixes that by carving out ~18% of the
current ~2-year Databento dataset (2024-08-15 through 2026-08-14) as a
holdout: the most recent 112 of 625 trading days, from 2026-04-07 onward.
Research/testing is restricted to the earlier 513 days
(2024-08-15 -> 2026-04-06) by default.

HOW IT WORKS: every script that loads price data for detection or
backtesting calls apply_holdout_boundary(df, context) right after
loading, before doing anything else with it. By default this DROPS any
bars on/after HOLDOUT_START_DATE and prints how many trading days were
excluded, so it's always visible in the console output that a boundary
was applied. To deliberately include holdout data -- which should only
ever happen for the eventual ONE-TIME final validation check described
in docs/RESEARCH_ARCHITECTURE.md, not for routine testing -- set the
environment variable ALLOW_HOLDOUT_DATA=1. Doing so prints a loud,
impossible-to-miss warning every time, so holdout access can never
happen silently or by accident.

IMPORTANT: HOLDOUT_START_DATE is a FIXED calendar date, not a
percentage recomputed from however much data happens to be on disk. If
it were a percentage, pulling more data later would silently shift which
days count as "holdout" -- possibly un-holding-out days that were
already looked at, which would quietly defeat the whole point. If the
holdout boundary ever needs to move, that must be a deliberate decision
(update this constant, document why, note it in
docs/RESEARCH_ARCHITECTURE.md), never an automatic side effect of
pulling fresh data.
"""

import os
import pandas as pd

HOLDOUT_START_DATE = pd.Timestamp("2026-04-07", tz="America/New_York")


def apply_holdout_boundary(df: pd.DataFrame, context: str = "") -> pd.DataFrame:
    """
    Returns df filtered down to RESEARCH data only (everything before
    HOLDOUT_START_DATE), unless ALLOW_HOLDOUT_DATA=1 is set in the
    environment, in which case it returns df unchanged and prints a loud
    warning. `context` is just a short label (e.g. a script name) to make
    the printed message clearer about where this was called from.
    """
    label = f" ({context})" if context else ""
    allow_holdout = os.environ.get("ALLOW_HOLDOUT_DATA", "") == "1"

    if allow_holdout:
        holdout_mask = df.index >= HOLDOUT_START_DATE
        holdout_days = len(set(df.index[holdout_mask].date))
        print(f"*** HOLDOUT DATA INCLUDED{label} *** ALLOW_HOLDOUT_DATA=1 is set -- "
              f"{holdout_days} holdout trading day(s) on/after {HOLDOUT_START_DATE.date()} "
              f"are part of this run. This should only happen for a deliberate, one-time "
              f"final validation check -- see docs/RESEARCH_ARCHITECTURE.md before doing this.")
        return df

    research_df = df[df.index < HOLDOUT_START_DATE]
    total_days = len(set(df.index.date))
    research_days = len(set(research_df.index.date))
    excluded_days = total_days - research_days
    if excluded_days > 0:
        print(f"Holdout boundary applied{label}: using {research_days} research trading day(s), "
              f"excluded {excluded_days} holdout day(s) on/after {HOLDOUT_START_DATE.date()}. "
              f"Set ALLOW_HOLDOUT_DATA=1 to include them (see docs/RESEARCH_ARCHITECTURE.md first).")
    return research_df
