# Mechanism — Monthly options-expiration week delta-hedge unwind (M25)

Written: 2026-09-13, ~9:26 am CT (9:00 am CT scheduled cycle)  ·  Pre-registered  ·  Sourcing entry, literature channel
Results seen before writing: no. No scan exists. Mechanism doc written before any scan, per standing discipline.

## 1. The claim
Stivers and Sun ("Returns and Option Activity over the Option-Expiration
Week for S&P 100 Stocks", SSRN) document that large-cap stocks with
actively traded options show substantially higher average returns during
the calendar week containing the monthly (third-Friday) options
expiration than in other weeks -- an indicative +9.3%/year effect summed
across the 12 expiration weeks, on S&P 100 names.

This is NOT the same claim as the already-declined quarterly witching-day
candidate (7:00 am CT cycle, 2026-09-13): that candidate was a single-DAY
event (the witching Friday's settlement session itself) and was ruled out
on a data-integrity ground -- zero usable NQ RTH bars on witching Fridays
in the Discovery window, a continuous-contract roll-splicing gap. M25
tests the whole calendar WEEK containing the monthly expiration (every
month has one, not just the quarterly "triple/quadruple witching" months),
using ordinary daily RTH closes across five sessions -- none of which
individually depend on the witching Friday's own 1-minute bars being
intact. This sidesteps the data gap that killed the quarterly candidate
entirely, and gives ~12x the event count (monthly, not quarterly).

## 2. Who is on the other side
Option market makers with net long call positions across S&P 100 / S&P 500
names. As the week's options approach expiration, open interest runs off;
makers who were short the underlying to hedge those long-call positions
must buy back that short-stock hedge as the offsetting long-call exposure
unwinds, creating a mechanical buy-pressure drift into the week. Declining
implied volatility into expiration (falling perceived risk) is offered as
a secondary, less mechanical driver.

## 3. The proxy (none needed -- this is a calendar-week partition, not a
state-variable regime): the conditioning variable is simply "is this
calendar week the one containing the month's third Friday," a pre-
determined calendar fact, not an estimated proxy. No lookahead risk.

## 4. Testable predictions
P1 (GATING). NQ's RTH return over the 5-session calendar week containing
   the monthly third-Friday expiration, aggregated across all such weeks
   in Discovery, is credibly POSITIVE relative to NQ's own unconditional
   weekly drift (NULL 1) -- not merely positive in isolation.
P2 (reported). The effect is not simply a duplicate of NQ's own positive
   unconditional intraday drift (Scan 020's finding, M15): the expiration-
   week premium must be LARGER than the average non-expiration week's
   return, tested as a difference.

## 5. What would falsify this
(a) No credible difference between expiration-week and non-expiration-week
    returns (falls inside NULL 1's own noise band).
(b) The effect is concentrated in a single day of the expiration week
    (e.g., only the Monday, or only the Friday) rather than building
    across the week -- would suggest a different, narrower mechanism (or
    the already-declined witching-day artifact) is doing the work, not a
    week-long unwind.
(c) KILL RULE: if the week's whole return is concentrated in the first
    RTH session's first 1-minute bar, this is a print/gap artifact, not a
    hedge-unwind building in over the week.

## 6. Information gain and edge potential
Information gain: moderate-high. This is the SAME delta-hedge-unwind
family as M14 (dealer gamma / hedging demand) but at a different
timescale (calendar-week vs. intraday close) and a different conditioning
variable (calendar date vs. an estimated autocorrelation proxy) -- a
credible pass here, especially after M14's own null this cycle, would be
informative about whether the M13/M14 family's underlying mechanism
(mandatory dealer hedge flow) shows up more reliably at a slower,
calendar-scheduled cadence than at the daily/intraday one.
Edge potential if real: a genuine monthly-scheduled premium (12
events/year) is a modest but real, non-event-risk directional signal --
product track: directional alpha, realization path: hold the calendar
week, time-based exit.

## 7. Resurrection ruling (LEARN + Integrity)
- NOT the quarterly witching-day candidate declined 2026-09-13 (7:00 am CT
  cycle): that was a single-session settlement-day claim, killed on a data
  gap. M25 is a whole-week claim using ordinary sessions, sidesteps that
  gap entirely, and has ~12x the event count.
- NOT M14 (option-dealer gamma regime, CLOSED 2026-09-13, hyp-000155,
  P1_FAIL): M14 tests an intraday-autocorrelation-derived REGIME
  conditioning the last-30-minutes response; M25 tests a calendar-
  scheduled WEEKLY return level with no estimated proxy at all. Different
  variable, different horizon, different test. A credible M25 pass would
  NOT be double-counted as M14 evidence, and vice versa -- overlap is
  real (both cite dealer delta-hedge unwind as the driver) but the tests
  are structurally independent, same discipline as M13/M14's own overlap
  handling.
- NOT M1 (cash-close 15:50-16:00, CLOSED) or M9 (Nasdaq-100 rebalance
  days, CLOSED/parked): different calendar anchor, different mechanism.
RULING: NEW. Attempt 1 of 2. Publication is an SSRN working paper (S&P
100 stocks, not NQ-specific, not dated with certainty from this pass --
flag as a caveat: decay evidence not established, record any null or pass
without over-claiming publication-date-based decay reasoning until the
exact publication year is confirmed).

## 8. Instrument-choice gate
1. Leads: S&P 100 constituent stocks carry the signal (that is what the
   paper tests); NQ (Nasdaq-100) is a related but DIFFERENT underlying
   basket -- large overlap in mega-cap tech names but not identical.
   Stated as a caveat, not fabricated equivalence.
2. Weekly, not millisecond or even intraday: the hedge unwind runs off
   with open interest over the whole week, consistent with a slow,
   scheduled flow, not a race.
3. NQ is the vehicle actually on disk and tradable at the platform's
   current scope; ES would be a closer match to "large-cap options" than
   NQ but M25 is filed as an NQ-first test given what is already on disk
   (ES also available now per this cycle's data-ceiling resolution --
   ES could be a natural cross-check if NQ is not credible, held for a
   possible attempt 2, not run in this pass).
4. Directional NQ (not relative). Survives NULL 1 by construction (tested
   as a difference).
5. NULL 1 applies (NQ's own unconditional weekly drift).

## 9. Frozen scope (for the scan)
ONE scan. Partition all Discovery calendar weeks into EXPIRATION (contains
the month's third Friday) vs NON-EXPIRATION. Outcome = NQ RTH week return
(Monday open through Friday close, or the week's actual first/last RTH
sessions if a holiday shortens it), ATR-normalized by the week's own
range or by a trailing daily ATR14 average -- exact normalization decided
at scan-write time and disclosed, not tuned after seeing results.
Reported: within-week day-by-day cumulative pattern (falsifier b check);
kill check on the week's first session's first 1-minute bar (falsifier c).
Estimated cells: expiration-week cell (GATING vs NULL1), non-expiration-
week cell (comparison), diff cell (P2), ~5 within-week day-of-week
cumulative cells (reported), kill cell = ~8-9 cells total, registered
exactly before the scan is written.
Data: NQ on disk, full Discovery range. No purchase needed.

## 10. Prediction status
P1 -- untested. P2 -- untested. NOT drawn this cycle: budget-use judgment
call, recorded here and in KNOWLEDGE.md -- this cycle already ran two full
multi-instrument scans (Scan 028, 15 cells; Scan 029, 8 cells) plus the
data-ceiling resolution and cost-log bug fix; sourcing this entry restores
the shelf to the floor of 3 as SHELF RULE v2 requires, but the draw itself
is deferred to preserve enough budget for a careful, unhurried close-out
of an already-heavy cycle, rather than rushing a third scan's cell design
in the time remaining. DRAWABLE as of this doc's completion; first in
line next cycle.
