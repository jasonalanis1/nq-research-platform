# Mechanism — Weekend/Monday effect on NQ RTH return direction, NQ (M33, literature channel, open scope)

Written: 2026-09-16, ~11:00 am CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO. No scan exists.
Origin: sourcing owed this cycle (shelf at 0/3 per
`research/_cycle_preflight.json`, and directional lane trials 1 and 2
both closed same-cycle they were sourced, per REFOCUS 9:00 am cycle
NEXT note) — directional lane trial 3 candidate, sourced per the memo's
rule (mechanism/calendar/structure, never the Idea Factory state
library). M28 (pre-holiday) and M32 (DST transition), the two candidates
drawn so far, are both closed; M15/hyp-000145 (overnight-vs-intraday)
and M6/hyp-000108 (turn-of-month), M24 (month-end payment-cycle), M25
(opex-week), M22 (ZN month-end duration) are all already spent or
closed magnitude-adjacent anchors, checked per Entry 32's own disclosure
list.

## 1. The claim
NQ's Monday same-day RTH return (open to close) is credibly NEGATIVE
relative to NQ's own unconditional daily RTH return (NULL 1). This is
the classic "weekend effect" / "Monday effect," one of the most widely
replicated calendar anomalies in the equity-return literature: French
(1980, *Journal of Financial Economics*, "Stock Returns and the Weekend
Effect") first documented mean NYSE/S&P returns from Friday close to
Monday close as reliably negative, later extended and cross-checked by
Gibbons and Hess (1981, *Journal of Business*) and Rogalski (1984,
*Journal of Finance*, who located the negative return specifically in
the non-trading Friday-close-to-Monday-open segment rather than the
Monday RTH session itself — a specificity distinction this entry's P2
cell is built to check). Never tested against NQ, or any instrument, in
this project as a RETURN-DIRECTION claim.

## 2. Who is on the other side
Two candidate mechanisms, both from the literature, making the SAME
directional prediction for different reasons (same two-mechanism
disclosure style already used for Entry 3 and Entry 4 in this
project):
(a) BAD-NEWS-TIMING: firms and issuers disproportionately release bad
    news over the weekend (after Friday's close, when no session can
    react to it) to let it be digested before Monday's open, so Monday's
    session incorporates a disproportionate share of the week's negative
    news flow (Damodaran 1989, *Review of Financial Studies*, documents
    the weekend clustering of bad corporate announcements specifically).
(b) INVESTOR PSYCHOLOGY / SENTIMENT: individual investors, who are more
    active relative to institutions early in the week, tend toward
    pessimism after a weekend (weekend-blues framing used alongside
    French's original paper and revisited in Sias and Starks (1995,
    *Journal of Finance*), who found the effect concentrated in
    individual- rather than institutional-investor-dominated stocks).
No single named FORCED counterparty in the M19-M28 sense (weaker
mechanism story, flagged in advance) — same disclosure precedent
already accepted for M28 (pre-holiday) and M32 (DST transition), both
of which explicitly carried the same caveat. Included anyway given the
depth of replication (French 1980 is among the most-cited calendar
anomaly papers in finance; the effect has since been re-examined and
found to have weakened/decayed in post-1990s US equity data — Kamara
1997, *Journal of Financial and Quantitative Analysis* — which the P3
cell below is built to probe by splitting the Discovery slice in half).

## 3. Why this is not the overfitting trap
Single, pre-specified calendar-anchor test using `day_of_week`, an
existing descriptor (`market_state_primitives.py`) with no new data or
descriptor code required, applied here for the FIRST time to a
RETURN-DIRECTION outcome. Checked against every existing use of
`day_of_week` and every already-spent/closed calendar anchor in
`research/idea_inventory.md` and `research/market_structure_map.md`:
- Not Entry 4 / `day_of_week` (Friday), CLOSED — that entry tested
  Friday's SAME-DAY RTH RANGE vs. its own trailing-20-day average, a
  volatility-magnitude claim with two opposite-signed predictions about
  participation. This entry tests MONDAY'S return SIGN vs. NQ's own
  unconditional daily RTH return — a different weekday (Monday, not
  Friday), a different outcome variable (signed return, not range), and
  a different mechanism family (bad-news-timing / weekend-sentiment
  digestion, not participation-driven volatility). Entry 4's own LEARN
  section explicitly flagged Monday as "the natural counterpart... only
  as a candidate SECOND cell" and never drew it.
- Not hyp-000016 / hyp-000042 — both fed `day_of_week` as one of 8-16
  features into a joint L1-regularized logistic-regression ensemble
  predicting NEXT-DAY return sign; both runs zeroed out every
  coefficient including day_of_week's and never isolated or reported a
  standalone day_of_week effect (confirmed in Entry 4's own LEARN
  section, idea_inventory.md:349-361). This entry isolates Monday alone
  against a single pre-registered cell, the same distinction the
  project already ruled clean for Entry 4.
- Not M28 (pre-holiday, CLOSED trial 1) — exchange-closure calendar
  anchor, reduced-hedging-flow mechanism; fires ~10x/year around NYSE
  holidays. This entry's anchor is the ordinary weekly Monday, fires
  every week, no exchange closure involved, different mechanism
  (bad-news-timing / weekend-sentiment, not reduced pre-closure hedging
  flow).
- Not M32 (DST transition, CLOSED trial 2) — 2x/year clock-change
  anchor, circadian/sleep-disruption mechanism. This entry's anchor is
  every ordinary week, not a 2x/year transition, and the mechanism
  (bad-news timing / weekend sentiment) is unrelated to sleep
  physiology.
- Not M6/hyp-000108 (turn-of-month inflows, spent) — monthly-calendar
  anchor (first sessions of a month), payroll/401k participant. Weekly,
  unrelated anchor and participant.
- Not M24 (month-end payment-cycle reversal, CLOSED) — monthly anchor,
  pension/cash-management forced-selling mechanism. Unrelated.
- Not M25 (options-expiration week, CLOSED) — monthly, options-dealer
  delta-hedge mechanism. Unrelated.
- Not M22 (ZN month-end duration extension, CLOSED) — different
  instrument (ZN), monthly anchor, index-duration mechanism. Unrelated.

## 4. Testable predictions
P1 (GATING). Monday's same-day RTH return (open to close) is credibly
   NEGATIVE relative to NQ's own unconditional daily RTH return (90%
   block-bootstrap CI entirely negative).
P2 (reported, specificity). Rogalski (1984) located the effect in the
   non-trading Friday-close-to-Monday-open segment, not the Monday RTH
   session itself — reported unpinned: the Friday-close-to-Monday-open
   gap return (using the existing overnight/gap convention already on
   disk) vs. NQ's own unconditional overnight gap return. If P1 is null
   but P2 is credibly negative, that is informative fidelity to the
   literature's more precise claim, not a pass on P1.
P3 (reported, descriptive). First half vs. second half of the Discovery
   slice (2015-01-01 -> 2018-05-17 split at the midpoint date, vs.
   2018-05-18 -> 2021-10-03), both net of NULL 1 — probes whether any
   effect has decayed over the sample, per Kamara (1997)'s documented
   weakening of the US weekend effect in post-1990s data. Descriptive
   only, not a second gate.

## 5. What would falsify this
(a) P1 fails (CI does not clear zero, or clears positive) — closes this
    entry; the documented weekend/Monday effect does not transfer to
    NQ futures RTH sessions at this data ceiling.
(b) P1 passes but is not distinguishable from NQ's ordinary
    day-to-day return noise once thin-sample power is accounted for
    (see (c)) — disclosed, not treated as a pass.
(c) THIN-SAMPLE disclosure: this fires every week, so power is NOT a
    concern the way it is for M28/M32/M25 (Discovery slice
    2015-01-01 -> 2021-10-03 yields on the order of 330-340 Monday RTH
    sessions after holiday closures are excluded) — no thin-sample
    floor applies; disclosed here only to confirm the count clears an
    ordinary n=40 floor by a wide margin, consistent with this being
    the best-powered directional-lane entry sourced so far.

## 6. Information gain and edge potential
Information gain: moderate-to-high. This is among the most replicated
calendar anomalies in the finance literature, with a specific,
falsifiable, non-price-derived trigger (the calendar weekday itself),
and it has never been tested on NQ, or on any instrument, in this
project as a RETURN-DIRECTION claim (only as one buried coefficient in
two already-closed joint models). A pass would be the first credible
directional finding of the directional lane; a null is informative in
its own right — a well-documented effect that fails to transfer, or
that decayed out of the US equity-index complex before NQ futures data
begins (consistent with Kamara 1997's own documented post-1990s
weakening).
Edge potential if real: highest-frequency calendar anchor sourced so
far in the directional lane (fires ~52x/year vs. M28's ~10x/year or
M32's 2x/year), which — if P1 is credible — gives the nearest path of
any directional-lane candidate to a usable sizing/timing overlay,
purely on statistical power grounds; that judgment is Portfolio's to
make later, not pre-decided here.

## 7. Resurrection ruling (LEARN + Integrity)
- NOT Entry 4 / day_of_week(Friday) RTH range (CLOSED) — different
  weekday, different outcome variable (range vs. signed return),
  different mechanism family. Entry 4's own text flagged Monday as an
  untested "natural counterpart," never drawn.
- NOT hyp-000016 / hyp-000042 — joint multi-feature next-day-sign
  models that never isolated day_of_week; this entry isolates Monday
  alone on its own cell, the same distinction already ruled clean for
  Entry 4.
- NOT M28 (pre-holiday, CLOSED trial 1) — exchange-closure anchor,
  ~10x/year, reduced-hedging mechanism.
- NOT M32 (DST transition, CLOSED trial 2) — 2x/year clock-change
  anchor, circadian mechanism.
- NOT M6/hyp-000108, M24, M25, M22 (turn-of-month, month-end
  payment-cycle, opex-week, ZN duration — all spent or CLOSED) —
  monthly-calendar anchors, unrelated participants and mechanisms.
RULING: NEW. Attempt 1 of 2.

## 8. Instrument-choice gate
1. NQ only — consistent with this project's current instrument focus;
   `day_of_week` is a fixed calendar descriptor already implemented
   project-wide, no new data or descriptor code needed.
2. Weekly anchor (every Monday RTH session), no lookahead (the calendar
   weekday is known trivially in advance).
3. Directional (signed same-day RTH return), not magnitude. NULL 1 =
   NQ's own unconditional daily RTH return over the same Discovery
   slice.

## 9. Frozen scope (for the scan)
ONE scan, full Discovery range (2015-01-01 -> 2021-10-03,
src/data_split.py), NQ daily RTH aggregation (already on disk
project-wide, no new data needed). Three cells:
  1. Monday same-day RTH return (open to close) net of NULL 1 (NQ's
     own unconditional daily RTH return), block-bootstrap CI  <== GATING (P1)
  2. Friday-close-to-Monday-open gap return net of NQ's own
     unconditional overnight/gap return, reported (P2, Rogalski 1984
     specificity check)
  3. First-half vs. second-half Discovery-slice split of the Monday
     effect (both net of NULL 1), reported descriptive (P3, decay
     check per Kamara 1997)
Statistical convention: block bootstrap, block=5 (standard weekly-cycle
block matching this project's day-of-week-adjacent convention, e.g.
Entry 4's own weekly framing), N_BOOT=3000, SEED=20260916, 90% CI,
"credible" = CI entirely on one side of zero.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. Sourced this cycle
(11:00 am, September 16th) to restore the shelf floor after M32 closed
last cycle as directional lane trial 2. Budget allows drawing the same
cycle (memo's own source-then-draw precedent, used for both trial 1 and
trial 2 already).
