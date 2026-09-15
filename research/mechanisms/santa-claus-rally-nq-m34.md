# Mechanism — Santa Claus Rally / turn-of-year effect on NQ RTH return, NQ (M34, literature channel, open scope)

Written: 2026-09-16, ~1:00 pm CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO. No scan exists.
Origin: sourcing owed this cycle (shelf at 0/3, directional lane trials
1-3 all closed same-cycle they were sourced) — directional lane trial 4
candidate, sourced per the memo's rule (mechanism/calendar/structure,
never the Idea Factory state library). Sanity-checked against
scan_037/038/039 first (see session report) before sourcing this: sign
conventions, NULL 1 construction, and timezone handling in all three
prior scans were verified correct and consistent with the house
convention (`src/market_state_primitives.py:116`,
`src/data_loader.py:66`) — three wrong-signed nulls in a row is not
itself evidence of a bug, so a fourth trial proceeds.

## 1. The claim
NQ's cumulative RTH return over the "Santa Claus Rally" window — the
last 5 RTH sessions of the calendar year plus the first 2 RTH sessions
of the following January (Yale Hirsch's original 1972 *Stock Trader's
Almanac* definition) — is credibly POSITIVE relative to NQ's own
unconditional 7-session rolling RTH return (NULL 1). Ranked among the
most durable calendar seasonalities in US equities (Hirsch 1972;
Hirsch and Hirsch 2023 *Stock Trader's Almanac*, annually updated
track record now spanning >70 years for S&P/DJIA; academically examined
by Bhabra, Dhillon and Ramirez 1999, *Financial Review*, "A November
Effect? Revisiting the Tax-Loss-Selling Hypothesis," which documents
the window's positive mean return net of standard January-effect and
turn-of-month controls). Never tested against NQ, or any instrument, in
this project.

## 2. Who is on the other side
No single named FORCED counterparty (weaker mechanism story, flagged in
advance, same disclosure precedent already accepted for M28/M32/M33).
Two candidate mechanisms from the literature, both predicting the SAME
direction:
(a) TAX-LOSS-SELLING UNWIND: the heaviest tax-loss-selling pressure on
    losing positions falls in the weeks BEFORE this window (documented
    turn-of-year tax literature, e.g. Reinganum 1983 *Journal of
    Financial Economics*); by the last week of December that selling
    pressure has largely exhausted itself, and light-volume holiday
    trading lets a modest reflexive buying bias (short-covering,
    seasonal retail optimism) show through with less large-seller
    resistance than an ordinary week.
(b) INSTITUTIONAL LIGHT-VOLUME / WINDOW-DRESSING: year-end desk
    staffing thins, algorithmic and index-related flow dominates a
    lower-liquidity tape, and window-dressing purchases of
    recently-strong names by funds finalizing December-31 statements
    add a further small bid (Haugen and Lakonishok 1988, *The
    Incredible January Effect*, ties window-dressing to the adjacent
    January effect).
Included despite the no-named-counterparty caveat given the length and
consistency of the documented track record (Hirsch's own almanac data:
positive in the large majority of years since 1950 across DJIA/S&P).

## 3. Why this is not the overfitting trap
Single, pre-specified calendar-anchor test using the existing NYSE
holiday/session calendar (already on disk, used for M20's release-day
rule and M28's pre-holiday-session identification) — no new data or
descriptor code required. Checked against every existing calendar-anchor
entry in `research/idea_inventory.md` and `research/market_structure_map.md`:
- Not M6/hyp-000108 (turn-of-month inflows, spent) — that entry tests
  the first 3 sessions of ANY calendar month, a monthly-recurring
  (12x/year), payroll/401k-inflow mechanism. This entry fires ONCE a
  year, anchored specifically to the December/January boundary, with a
  tax-loss-unwind/window-dressing mechanism, not a payroll-inflow one.
- Not M24 (month-end payment-cycle reversal, CLOSED) — monthly anchor,
  pension/cash-management forced-selling mechanism, opposite flow
  direction (selling pressure, not a buying bias), and tests the month
  AFTER a weak last week, not the turn-of-year window itself.
- Not M28 (pre-holiday effect, CLOSED trial 1) — M28 tests the SINGLE
  RTH session immediately before ANY NYSE full-closure holiday
  (~10x/year, one-day horizon). This entry is a specific 7-session,
  once-a-year window spanning the December 25th AND January 1st
  holidays together, not a single pre-holiday session; different
  horizon, different mechanism (tax-unwind/window-dressing, not
  reduced pre-closure hedging).
- Not M32 (DST transition, CLOSED trial 2) — unrelated calendar anchor
  and mechanism (circadian/sleep, 2x/year, March/November).
- Not M33 (weekend/Monday effect, CLOSED trial 3) — unrelated calendar
  anchor and mechanism (weekly, bad-news-timing/sentiment).
- Not M22 (ZN month-end duration extension, CLOSED) — different
  instrument (ZN), monthly anchor, index-duration mechanism.
- Not M25 (options-expiration week, CLOSED) — monthly opex anchor,
  dealer delta-hedge mechanism, unrelated.
- Not M5 (month-end NQ-vs-ZN relative performance, spent) — cross-asset
  conditioning variable, different claim shape (relative performance,
  not an unconditional seasonal window).

## 4. Testable predictions
P1 (GATING). The Santa Claus Rally window's cumulative RTH return
   (last 5 December RTH sessions + first 2 January RTH sessions) is
   credibly POSITIVE relative to NQ's own unconditional 7-session
   rolling RTH return (90% block-bootstrap CI entirely positive).
P2 (reported, specificity). December-leg-only (last 5 sessions) vs
   January-leg-only (first 2 sessions) reported separately, each net
   of NULL 1's per-session mean scaled to leg length — probes whether
   any effect concentrates in one leg (Hirsch's own literature
   attributes more of the effect to the December leg).
P3 (reported, descriptive). First-half vs second-half of the Discovery
   slice split at the midpoint YEAR (years 2015-2018 vs 2018-2021),
   both net of NULL 1 — decay check, same style as M33's P3.

## 5. What would falsify this
(a) P1 fails (CI does not clear zero, or clears negative) — closes
    this entry; the documented Santa Claus Rally does not transfer to
    NQ futures RTH sessions at this data ceiling.
(b) P1 passes but is not distinguishable from an ordinary 7-session
    NQ return once thin-sample power is accounted for (see THIN-SAMPLE
    disclosure below).
(c) THIN-SAMPLE disclosure, pre-registered: this window fires ONCE per
    year. Discovery slice (2015-01-01 -> 2021-10-03) covers calendar
    years 2015-2020 inclusive for a complete December-to-January
    window (the 2021 window falls outside the Discovery slice, whose
    last date is 2021-10-03) — approximately **n=6 window
    observations**, well below the ordinary 40-observation project
    floor. This is the thinnest directional-lane entry sourced so far
    (M32's 13 transition-weeks was previously the thinnest). Disclosed
    in advance: a null here is far more likely to be UNDERPOWERED than
    a genuine absence of effect, and a "pass" would need unusually wide
    separation from zero to be treated as more than a coincidence at
    n=6. This caveat is written into the verdict logic itself (see
    Section 9) rather than left to be discovered after the run.

## 6. Information gain and edge potential
Information gain: LOW-to-moderate given the severe thin-sample
disclosure above — this entry is drawn mainly because it is a genuinely
untested, well-documented, non-state calendar idea and the lane
requires sourcing one, not because it is expected to be well-powered.
If it passes despite the thin sample, it is reported as a lead requiring
independent confirmation (e.g. an out-of-project longer equity-index
series), not as an actionable result on n=6. Edge potential if real:
very low usable frequency (1x/year) makes it a poor sizing/timing
overlay candidate regardless of statistical outcome — a Portfolio
question if it ever passed, not pre-decided here.

## 7. Resurrection ruling (LEARN + Integrity)
NOT M6/hyp-000108 (turn-of-month, spent, monthly/12x-year, payroll
mechanism). NOT M24 (month-end payment-cycle reversal, CLOSED, monthly,
opposite-direction selling-pressure mechanism). NOT M28 (pre-holiday,
CLOSED trial 1, single-session/10x-year, reduced-hedging mechanism).
NOT M32 (DST, CLOSED trial 2, unrelated anchor/mechanism). NOT M33
(weekend/Monday, CLOSED trial 3, unrelated anchor/mechanism). NOT M22
(ZN duration, CLOSED, different instrument). NOT M25 (opex week,
CLOSED, unrelated anchor/mechanism). NOT M5 (NQ-vs-ZN relative
performance, spent, cross-asset conditioning, different claim shape).
RULING: NEW. Attempt 1 of 2.

## 8. Instrument-choice gate
1. NQ only — consistent with this project's current instrument focus;
   uses the existing NYSE holiday/session calendar already on disk
   project-wide, no new data or descriptor code needed.
2. Annual anchor (last 5 December RTH sessions + first 2 January RTH
   sessions), no lookahead (the calendar is known trivially in advance).
3. Directional (signed 7-session cumulative RTH return), not magnitude.
   NULL 1 = NQ's own unconditional 7-session rolling RTH return over
   the same Discovery slice.

## 9. Frozen scope (for the scan)
ONE scan, full Discovery range (2015-01-01 -> 2021-10-03,
`src/data_split.py`), NQ daily RTH aggregation (already on disk
project-wide, no new data needed). Three cells:
  1. Santa Claus Rally window (last 5 Dec RTH sessions + first 2 Jan
     RTH sessions) cumulative return net of NULL 1 (NQ's own
     unconditional 7-session rolling RTH return), block-bootstrap CI
     <== GATING (P1)
  2. December-leg-only vs January-leg-only, each net of NULL 1's
     per-session mean scaled to leg length, reported (P2, specificity)
  3. First-half (years 2015-2017) vs second-half (years 2018-2020) of
     the window observations, both net of NULL 1, reported descriptive
     (P3, decay check)
Plus reference/count cells (NULL 1 mean, window-year count) and the
THIN-SAMPLE disclosure from Section 5(c), which OVERRIDES the ordinary
P1_PASS/P1_FAIL verdict when n < 40: verdict is reported as
THIN_SAMPLE_DISCLOSED regardless of P1's own result, consistent with
scan_039's precedent for the thin-sample override.
Statistical convention: block bootstrap, block=7 (window length, same
"block = overlap length" rule used project-wide, e.g. M32's
transition-week block=5 for a 5-session window — this window is 7
sessions), N_BOOT=3000, SEED=20260916, 90% CI, "credible" = CI entirely
on one side of zero.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. Sourced this cycle
(~1:00 pm, September 16th) to restore the shelf floor after M33 closed
last cycle as directional lane trial 3. Budget allows drawing the same
cycle (memo's own source-then-draw precedent, used for trials 1-3
already).
