"""
nasdaq_rebalance_calendar.py
=============================

Sources M9 (Idea Inventory market_structure_map.md) -- the one map entry
that had been PARKED pending a free, on-disk calendar of Nasdaq-100
index-effective dates. Filed 2026-09-12 at Jason's direction ("do what
you gotta do, don't wait for me").

WHAT THIS IS: the quarterly "triple/quadruple witching" Fridays (3rd
Friday of March/June/September/December) -- the dates on which Nasdaq-100
index funds and other passive trackers must trade to match the index's
quarterly share-count rebalance (and, in December, the annual
composition reconstitution) by the closing bell, so the new
weights/composition are live from the following Monday's open.

PROVENANCE: Nasdaq's own 2025 annual-reconstitution press release states
the index "is reconstituted each year in December, timed to coincide
with the quadruple witch expiration Friday of the quarter," with the
2025 changes effective "prior to market open on Monday, December 22,
2025" -- December 22, 2025 is the Monday immediately after the 3rd
Friday of December 2025 (December 19), confirming the rule
mechanically. The same quarterly-Friday-close mechanism (fund
rebalancing into the close to match the new share counts) applies in
March, June, and September, not just December -- this is standard,
widely documented index-fund mechanics, not specific to Nasdaq-100's
annual composition change. Ad hoc SPECIAL rebalances (e.g. the one
effective 2023-07-24) are excluded here -- they are irregular,
announced case-by-case, and not on this mechanical calendar.

Dates computed directly (3rd Friday of Mar/Jun/Sep/Dec each year) rather
than hand-typed, to avoid transcription error -- verified against the
one real anchor available (2025-12-19 Friday -> 2025-12-22 Monday
effective, matching Nasdaq's own press release).

HOW TO USE:
    from nasdaq_rebalance_calendar import QUARTERLY_REBALANCE_FRIDAYS
"""
import calendar
from datetime import date


def _third_friday(year: int, month: int) -> date:
    cal = calendar.Calendar()
    fridays = [d for d in cal.itermonthdates(year, month) if d.month == month and d.weekday() == 4]
    return fridays[2]


QUARTERLY_REBALANCE_FRIDAYS = [
    _third_friday(y, m)
    for y in range(2015, 2027)
    for m in (3, 6, 9, 12)
]

QUARTERLY_REBALANCE_FRIDAY_SET = set(QUARTERLY_REBALANCE_FRIDAYS)

assert len(QUARTERLY_REBALANCE_FRIDAYS) == len(set(QUARTERLY_REBALANCE_FRIDAYS)), "duplicate dates"
assert QUARTERLY_REBALANCE_FRIDAYS == sorted(QUARTERLY_REBALANCE_FRIDAYS), "must be sorted"
