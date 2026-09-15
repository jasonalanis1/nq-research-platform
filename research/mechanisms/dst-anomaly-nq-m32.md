# Mechanism — Daylight-saving-time transition anomaly, NQ (M32, literature channel, open scope)

Written: 2026-09-16, ~9:00 am CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO. No scan exists.
Origin: sourcing owed this cycle (SHELF RULE v2 floor, shelf at 0/3 per
`research/_cycle_preflight.json`) — directional lane trial 2, sourced
per the memo's rule (mechanism/calendar/structure, never the Idea
Factory state library). Entry 32/M28 (pre-holiday) closed last cycle
(trial 1, clean null); hyp-000145/M15 (overnight-vs-intraday) also
spent (Sept 12th, clean null). Both cited candidates from the memo's
own text are now exhausted.

## 1. The claim
NQ's cumulative RTH return over the calendar week (5 sessions) following
a US daylight-saving-time transition (both "spring forward," the second
Sunday of March, and "fall back," the first Sunday of November) is
credibly NEGATIVE relative to NQ's own unconditional 5-session rolling
return (NULL 1). This is the daylight-saving anomaly documented across
world equity indices by Kamstra, Kramer and Levi (2000, *American
Economic Review*, "Losing Sleep at the Market: The Daylight Saving
Anomaly") and revisited in their 2002 reply to Pinegar's critique
(Kamstra, Kramer and Levi 2002, *AER*) — never tested against NQ, or
against any instrument, in this project.

## 2. Who is on the other side
No single named forced participant — flagged explicitly as a WEAKER
mechanism story, the same disclosure this project already accepted for
M28 (pre-holiday effect). The literature's proposed channel is
population-wide and physiological, not institutional: the one-hour
clock shift disrupts sleep cycles for a large, synchronized population
of US-based traders and decision-makers (retail and institutional
alike) in the days around the transition; disrupted sleep is
independently linked in the psychology/finance literature to reduced
risk tolerance and more conservative position-taking (the authors'
cited channel, not re-derived here). This is a genuinely different
channel from M28's (reduced hedging/short-selling flow into a
closure) — a circadian/behavioral mechanism, not a liquidity or
positioning one. Included on the same basis M28 was: the empirical
regularity is well-replicated (multiple countries' equity indices,
Kamstra-Kramer-Levi 2000 Table 2) and testing it against NQ futures
specifically is informative regardless of mechanism precision.

## 3. Why this is not the overfitting trap
Single, pre-specified calendar-anchor test using an external,
non-price-derived calendar (US DST transition dates, computable
directly from the statutory rule — second Sunday of March, first Sunday
of November, unchanged since the Energy Policy Act of 2005 — not
estimated or fit from NQ's own return data). Not a variant of any
closed or spent calendar entry:
- Not M28 (pre-holiday, CLOSED trial 1) — exchange-closure boundary,
  reduced-hedging-flow mechanism; DST is a clock-change with no market
  closure at all, and a circadian/behavioral mechanism, not a
  liquidity one.
- Not M6/hyp-000108 (turn-of-month inflows, spent) — unrelated anchor
  (payroll/401k timing) and unrelated participant.
- Not M24 (month-end payment-cycle reversal, CLOSED) — unrelated
  anchor and mechanism (pension/cash-management forced selling).
- Not M15/hyp-000145 (overnight-vs-intraday split, spent, clean null)
  — an unconditional session-level decomposition with no calendar
  conditioning at all; this entry conditions on a specific two-events-
  a-year calendar anchor.
- Not M5 (month-end/quarter-end NQ-vs-ZN relative performance, spent)
  — different anchor, different signal (cross-asset relative
  performance vs. a pure calendar date).

## 4. Testable predictions
P1 (GATING). The 5-RTH-session cumulative return in the calendar week
   following a US DST transition (both spring and fall) is credibly
   NEGATIVE relative to NQ's own unconditional 5-session rolling
   return (90% block-bootstrap CI entirely negative).
P2 (reported, specificity/fidelity to the literature). The single
   Monday-only return immediately following the transition weekend
   (the literature's original, narrower claim) is reported unpinned —
   does the effect concentrate in the first session, or spread across
   the week?
P3 (reported, descriptive). Spring-transition weeks vs. fall-transition
   weeks reported separately, unpinned — Kamstra-Kramer-Levi found the
   spring effect stronger; this is a specificity cross-check, not a
   second gate.

## 5. What would falsify this
(a) P1 fails (CI does not clear zero, or clears positive) — closes this
    entry; the documented daylight-saving anomaly does not transfer to
    NQ futures at this data ceiling.
(b) P1 passes but the effect is indistinguishable from NQ's ordinary
    week-to-week return noise once thin-sample power is accounted for
    (see (c)) — disclosed, not treated as a pass.
(c) THIN-SAMPLE disclosure: 2 transitions/year over the Discovery slice
    (2015-01-01 -> 2021-10-03, src/data_split.py, ~6.75 years) yields
    roughly 13-14 transition weeks, i.e. roughly 65-70 usable RTH
    sessions at the week-level unit of analysis (5 sessions x ~13-14
    transitions) — the WEEK is the observational unit for the gating
    statistic's variance structure even though the block bootstrap
    resamples returns within it; if the usable transition-week count
    comes in below 12, disclose as thin-sample per the M19/M22
    convention rather than treating a null as fully powered.

## 6. Information gain and edge potential
Information gain: moderate. A well-replicated, multi-country calendar
anomaly with an unambiguous, non-price-derived, publicly known trigger
date, never tested against NQ or any instrument in this project. A pass
would be a genuinely new directional characterization fact on a
2-events-a-year cadence; a null is informative on its own terms (the
effect may not transfer to US index futures, or may have decayed since
the 1967-1998 sample the original paper used).
Edge potential if real: NQ already has an existing base strategy (per
this project's own framing of NQ's advantage over the open-scope
CL/6E/ZN family), so a pass has a nearer path to a sizing/timing overlay
than the open-scope family typically does — same disclosure M28 made.
Given the 2-events-a-year cadence, any real effect would be a niche
seasonal overlay, not a standalone strategy.

## 7. Resurrection ruling (LEARN + Integrity)
- NOT M28 (pre-holiday effect, CLOSED trial 1) — exchange-closure
  calendar anchor and reduced-hedging mechanism vs. this entry's
  clock-change anchor and circadian/behavioral mechanism. Different
  anchor, different channel.
- NOT M6/hyp-000108 (turn-of-month inflows, spent) — different anchor
  and participant.
- NOT M24 (month-end payment-cycle reversal, CLOSED) — different
  anchor and mechanism.
- NOT M15/hyp-000145 (overnight-vs-intraday split, spent, clean null)
  — unconditional decomposition, no calendar conditioning; this entry
  is calendar-conditioned on a 2x/year clock-change date.
- NOT M5 (month-end/quarter-end NQ-vs-ZN, spent) — different anchor,
  different signal construction (cross-asset relative performance vs.
  a single external calendar trigger).
RULING: NEW. Attempt 1 of 2.

## 8. Instrument-choice gate
1. NQ only — consistent with this project's current instrument focus;
   DST transition dates are a fixed, publicly known statutory rule
   (2nd Sunday of March, 1st Sunday of November since 2007), computable
   without any new data file.
2. Weekly anchor (5 RTH sessions following each transition Sunday),
   no lookahead (transition dates are known decades in advance).
3. Directional (signed 5-session cumulative return), not magnitude.
   NULL 1 = NQ's own unconditional 5-session rolling return over the
   same Discovery slice.

## 9. Frozen scope (for the scan)
ONE scan, full Discovery range (2015-01-01 -> 2021-10-03,
src/data_split.py), NQ daily RTH aggregation (already on disk
project-wide, no new data needed). Five cells:
  1. Transition-week (5 RTH sessions starting the first session on or
     after each DST transition Sunday) cumulative return net of NULL 1
     (unconditional 5-session rolling return), block-bootstrap CI  <== GATING (P1)
  2. Transition-Monday-only return net of NQ's own unconditional daily
     RTH return, reported (P2, literature fidelity check)
  3. Spring-transition weeks vs. fall-transition weeks, both reported
     separately net of NULL 1, descriptive (P3)
  4. Unconditional 5-session rolling return distribution mean (NULL 1
     reference)
  5. Transition-week-count / thin-sample disclosure cell (falsifier c)
Statistical convention: block bootstrap, block=5 (thin annual event
count, matching the M19/M22/M25/M28 convention for infrequent
calendar-anchored events), N_BOOT=3000, SEED=20260916, 90% CI,
"credible" = CI entirely on one side of zero.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. Sourced this cycle to
restore the shelf floor per SHELF RULE v2 after Entry 32/M28 closed
last cycle. Filed DRAWABLE; whether it is drawn this same cycle as
directional lane trial 2 is a budget-and-judgment call for the owning
cycle, per the memo's own source-then-draw precedent (Entry 32 itself
was sourced one cycle and drawn the next; hyp-000163's trial 1 draw
happened same-day as the memo but a different cycle).
