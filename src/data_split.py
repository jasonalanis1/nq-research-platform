"""
data_split.py
==============

WHAT THIS FILE DOES (plain English):
Carves the RESEARCH portion of the data (everything data_holdout.py
already excludes as legacy holdout, i.e. before 2026-04-07) into three
further pieces: DISCOVERY, VALIDATION, and HOLDOUT_GEN2. This is the
three-way split described in docs/RESEARCH_INTEGRITY_PROTOCOL.md,
built once the expanded historical dataset (2015-01-01 onward) has been
pulled and quality-checked.

WHY THIS EXISTS: the Research Integrity Protocol requires that a future
Strategy R&D Agent only ever sees DISCOVERY data while searching for
hypotheses, and that a promoted candidate gets tested on VALIDATION data
it never saw during discovery, with parameters frozen. HOLDOUT_GEN2 is a
second, separate reserve of genuinely unseen historical data -- distinct
from the existing legacy holdout (data_holdout.py's 2026-04-07+ window,
now called "Holdout Generation 1" in the protocol), which stays
completely untouched by this file. Generation 1 and Generation 2 are two
separate reserves, not one merged pool -- see the protocol doc's
"Renewable holdout generations" section.

HOW THE BOUNDARIES WERE CHOSEN (2026-08-20): the research window
(2015-01-01 -> 2026-04-06, the day before the legacy holdout starts) is
~4,113 calendar days. Split by calendar-day proportion at 60/20/20:

    DISCOVERY:      2015-01-01 -> 2021-10-03  (~60%)
    VALIDATION:      2021-10-04 -> 2024-01-03  (~20%)
    HOLDOUT_GEN2:    2024-01-04 -> 2026-04-06  (~20%)
    (Holdout Generation 1, unchanged: 2026-04-07 -> present, per data_holdout.py)

These are FIXED calendar dates, not percentages recomputed from however
much data happens to be on disk -- same reasoning as
data_holdout.py's HOLDOUT_START_DATE: a percentage-based split would
silently redraw the boundaries every time more data gets pulled,
possibly un-holding-out days that were already looked at. If these
dates ever need to change, that's a deliberate decision requiring a new
entry in docs/RESEARCH_INTEGRITY_PROTOCOL.md, never an automatic side
effect.

STATUS AS OF 2026-08-20: drafted as infrastructure, NOT yet wired into
any script. Per docs/RESEARCH_INTEGRITY_PROTOCOL.md decision #1, no
autonomous Strategy R&D or formal Larry candidate validation begins
until (a) this split exists AND (b) the expanded dataset it's built on
has been fully verified (data pull + reproducibility check in progress
as of this writing). This file being drafted is not the same as that
gate being cleared -- don't use get_discovery_data() for anything until
that verification is confirmed complete.
"""

import pandas as pd
from data_holdout import apply_holdout_boundary, HOLDOUT_START_DATE

DISCOVERY_END_DATE = pd.Timestamp("2021-10-03", tz="America/New_York")
VALIDATION_END_DATE = pd.Timestamp("2024-01-03", tz="America/New_York")
# HOLDOUT_GEN2 runs from the day after VALIDATION_END_DATE through the
# day before HOLDOUT_START_DATE (2026-04-07, imported from data_holdout.py)


def _research_only(df: pd.DataFrame, context: str) -> pd.DataFrame:
    """Applies the existing legacy-holdout boundary first, so Generation 1
    (2026-04-07+) can never leak into any of the three pieces below,
    no matter what date range the caller passes in."""
    return apply_holdout_boundary(df, context=context)


def get_discovery_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    The ONLY slice a Strategy R&D Agent may ever see. Oldest ~60% of the
    research window (2015-01-01 -> 2021-10-03).
    """
    research_df = _research_only(df, "data_split.get_discovery_data")
    out = research_df[research_df.index <= DISCOVERY_END_DATE]
    days = len(set(out.index.date))
    print(f"Discovery slice: {days} trading day(s), {DISCOVERY_END_DATE.date()} or earlier. "
          f"This is the only data an R&D agent may use for hypothesis search.")
    return out


def get_validation_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Middle ~20% of the research window (2021-10-04 -> 2024-01-03). For
    testing a FROZEN candidate that was promoted out of discovery --
    never for searching or tuning.
    """
    research_df = _research_only(df, "data_split.get_validation_data")
    out = research_df[
        (research_df.index > DISCOVERY_END_DATE) &
        (research_df.index <= VALIDATION_END_DATE)
    ]
    days = len(set(out.index.date))
    print(f"Validation slice: {days} trading day(s), {(DISCOVERY_END_DATE + pd.Timedelta(days=1)).date()} "
          f"-> {VALIDATION_END_DATE.date()}. Only for testing frozen candidates, never for tuning.")
    return out


def get_holdout_gen2_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Most recent ~20% of the research window (2024-01-04 -> 2026-04-06) --
    "Holdout Generation 2" per docs/RESEARCH_INTEGRITY_PROTOCOL.md.
    Separate from and in addition to the existing legacy holdout
    (Generation 1, 2026-04-07+, still governed entirely by
    data_holdout.py -- this function never touches that data).

    Like Generation 1, this is a finite, budgeted resource -- see the
    protocol doc's holdout-ledger requirements before calling this for
    any real candidate. This function does not itself enforce the
    5-slot budget or require sign-off; that's a ledger/process
    requirement, not something safe to silently enforce in code without
    a human decision each time.
    """
    research_df = _research_only(df, "data_split.get_holdout_gen2_data")
    out = research_df[research_df.index > VALIDATION_END_DATE]
    days = len(set(out.index.date))
    print(f"*** HOLDOUT GENERATION 2 ACCESSED *** {days} trading day(s), "
          f"{(VALIDATION_END_DATE + pd.Timedelta(days=1)).date()} -> "
          f"{(HOLDOUT_START_DATE - pd.Timedelta(days=1)).date()}. This is a budgeted resource -- "
          f"confirm this use is logged in the holdout ledger per docs/RESEARCH_INTEGRITY_PROTOCOL.md "
          f"before trusting any result from it.")
    return out
