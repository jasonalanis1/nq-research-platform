# S007 — screen and salvage, 2026-09-16 (9:00 am CT cycle)

Strategy: **Opening-range break continuation, opening-range-scaled stop.**
Spec `research/infrastructure/strategy-specs/S007-opening-range-break-continuation.md`
(sha256 `eb45ffd8...`), module `src/strategy_s007_opening_range_break_continuation.py`
(sha256 `de154a41...`), frozen before any data was touched.

The **first candidate sourced under Jason's Amendment 1** preference for intraday
strategies that trade most days.

## Screen (Discovery slice only, 2,101 sessions)

| | |
|---|---|
| trades | **1,525** (0.7258 per session — fires on 72.6% of sessions) |
| net after ASSUMED costs, 1 micro | **-$8,623.67** (5 micros -$43,118.35; 10 micros -$86,236.70) |
| gross | **+$526.33**, minus **$9,150.00** of assumed costs |
| win rate | 39.6% |
| avg R net | **-0.2459** |
| SLOW projection (Amendment 1) | 0.7258 × 126 = **91.5 trades in six months** → **NOT SLOW** |

Detail: `data/screen_S007.json`. Net ≤ 0 → Salvage, not paper.

**The sourcing preference worked; the strategy did not.** This is the first
candidate in the book whose trade rate clears the 40-trade clock with room to
spare. It is also the clearest cost result the project has: the gross edge is
**+$0.35 per trade** and the assumed round trip is **$6.00** — seventeen times
the edge. A strategy that fires every day must clear ~0.10R of cost every day.

## Salvage (directive s.7, menu only, one salvage — spent)

`src/salvage_check.py`, detail `data/salvage_S007_2026-09-16.json`.

| condition | result |
|---|---|
| 1. VXN vs trailing | HIGH n=643 -$3,198.41 (-0.174R); LOW n=882 -$5,425.26 (-0.299R) — both lose |
| 2. trend vs range, **day's own** range | TREND n=658 **+$6,469.93 (+0.178R, 54.9%)**; RANGE n=851 -$14,867.11 (-0.568R) |
| 2. trend vs range, **prior-day** range (the knowable half) | PRIOR_EXPANDED n=634 -$5,043.69 (-0.266R); PRIOR_CONTRACTED n=874 -$3,345.74 (-0.221R) — **both lose** |
| 3. time of day | AFTERNOON n=55 +$52.28 but **-0.072R**; MIDDAY n=1,470 -$8,675.95 (-0.253R) |
| 4. scheduled news | NEWS n=177 -$656.55; QUIET n=1,348 -$7,967.12 — both lose |
| spec-named: direction | long n=824 -$3,286.65; short n=701 -$5,337.02 — both lose |

**Verdict: no condition taken. S007 stays KILLED and nothing is spawned.**

Two refusals, both on precedent rather than taste:

1. **The TREND side is ex-post.** The day's own RTH range is not known at the
   10:00–13:00 ET entry, so it cannot filter anything. This is the identical
   ruling S001's salvage made on this same menu condition
   (`research/ledger/strategies.jsonl`, S001 SALVAGE row: "Menu 2 TREND: ex-post
   label, cannot filter"). Read plainly, the +0.178R on TREND days is close to a
   tautology: breakouts continue on days that expanded. To avoid spawning on a
   tautology the **knowable** half of the same menu condition was split instead —
   prior-day range against its own trailing-20 average, known before the open —
   and **both sides lose**. That is direct evidence that the expansion this trade
   needs is not forecastable from the prior session.
2. **The AFTERNOON side is dollars-positive on a negative R** (+$52.28 across 55
   trades at -0.072R). S001's salvage refused exactly this shape (its pre-09:30
   side, +$24 at -0.300R). A handful of dollars on a losing per-trade expectation
   is noise, not a condition.

The spec's own named failure conditions — narrow opening ranges relative to ATR,
gap-open sessions — are subsumed by menu conditions 1 and 2 (both of which lose
on every knowable side) and were not separately spawned. One salvage, spent.

## What is kept

The mechanism paragraph is not refuted by this; what is refuted is that the
mechanism is worth **$6.00 a day**. The liquidity-provider inventory unwind may
well be real and simply smaller than the cost of collecting it at this frequency
with a 0.5×width stop. Anything that revisits it has to start from a bigger
per-trade edge, not a better filter — no knowable filter in the menu found one.
