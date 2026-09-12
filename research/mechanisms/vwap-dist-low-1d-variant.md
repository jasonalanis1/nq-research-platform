# Mechanism — vwap_dist_vs_atr LOW, 1-day variant (attempt 2/2)

Written: 2026-09-10  ·  PARTIALLY PRE-REGISTERED
Results seen before writing: Discovery-slice YES (n=558, mean R 0.1097,
CI [0.053,0.165], DISCOVERY_PASS; stability check: split-sample first
half not credible on its own, vol-regime and trend-regime both stable
-- see research/studies/vwap-dist-low-1d-variant-spec.md and the
stability-check script output). Validation-slice: NOT YET RUN. The
predictions below about the VALIDATION-SLICE result are written before
that data is touched — that portion is genuinely pre-registered. The
predictions about the DISCOVERY-slice shape are POST-HOC relative to
this specific 1d confirmation run (though the underlying numbers were
already visible in Scan 002 and in H118's own mechanism doc before this
document existed) — carries hypothesis weight only, not evidence
weight, for that portion.

## 1. The claim

Same underlying state as H118 (research/mechanisms/h118-vwap-dist-low.md):
a day closing well below its own session VWAP, scaled by ATR, marks
overshoot-driven selling that the market spends the following session(s)
absorbing. This document's specific claim is narrower: H118's own P2
finding (two-thirds of the 10-day effect lands in day 1, flat through
day 5) implies the absorption is FAST -- if true, the 1-day slice on its
own, tested prospectively, should be a genuine, credible, economically
meaningful edge in its own right, not merely a fragment of a 10-day
number that only looks real in aggregate.

## 2. Who is on the other side

Unchanged from H118: forced or impatient sellers (margin calls,
de-risking, momentum overshoot) paying for immediacy; the mechanism's
honest weakness (no order-flow data to confirm forced selling is
actually present) is identical here and not re-argued.

## 3. Testable predictions

P1. **The 1-day effect should be credible and stable on its own**, not
    merely a component of the 10-day figure that happens to look
    reasonable when summed. Split-sample and regime-split should show
    the same sign and (mostly) credible CIs, matching the discipline
    H118 itself was held to before being taken to a frozen spec.
P2. **The 1-day Validation-slice result should be of comparable
    magnitude to the 1-day Discovery-slice result** (mean R roughly
    0.05-0.15), NOT dramatically smaller. If absorption is fast and
    genuinely mechanistic, one day of data should be less sensitive to
    Discovery-stage selection effects than the 10-day figure was
    (H118's own Validation R dropped from 0.62 Discovery to 0.28
    Validation -- a large shrinkage this project's own multiplicity
    review attributed partly to winner-curse geometry across a 10-day
    aggregation). A 1-day effect that shrinks by a SIMILAR or SMALLER
    proportion on Validation, versus H118's ~55% shrinkage, would
    support the "fast absorption is the real, robust part" reading.
P3. **This candidate's Validation-slice result should NOT be
    informative about H118's forward test, and vice versa** -- STRICT
    SEPARATION is a design constraint here, not itself a prediction,
    but is stated for completeness per NEXT_UP's hard constraint.

## 4. What would falsify this

P1 fails if the 1-day effect is unstable across split-sample or regime
cuts in a way the 10-day H118 figure was not (H118 passed both cuts
cleanly). P2 fails if the Validation-slice R comes back much smaller
than the Discovery-slice R, or not credible at all -- that would say the
1-day cell benefits from the SAME kind of Discovery-stage selection
H118's 10-day figure did, undermining the "day 1 is the well-understood
part" reading from the H118 mechanism doc.

## 5. Prediction status

**P1 — PARTIALLY CONFIRMED, one caution.** Vol-regime split: both
low-vol (n=262, R=0.136, CI [0.025,0.246]) and high-vol (n=296,
R=0.226, CI [0.110,0.364]) credible and positive. Trend-regime split:
both uptrend (n=427, R=0.128, CI [0.058,0.201]) and downtrend (n=118,
R=0.288, CI [0.131,0.466]) credible and positive. Chronological
split-sample: second half credible (n=292, R=0.138, CI [0.068,0.208]),
but FIRST half is NOT independently credible on its own (n=266,
R=0.079, CI [-0.012,0.167] -- positive point estimate, CI touches
zero). This is weaker than H118's own split-sample record (which
passed cleanly on both halves) and is disclosed as a genuine caution,
not smoothed over -- the 1-day cell is thinner-powered per slice than
the 10-day cell was on the same split.
P2 — CONTRADICTED. Validation-slice result (hyp-000137): n=218,
    mean R=0.0473, CI_90 [-0.0330, 0.1270] -- NOT credible (spans zero),
    NOT economically meaningful (below the 0.05R floor). Discovery R
    (0.1097) -> Validation R (0.0473) is a 57% shrinkage -- essentially
    THE SAME magnitude of shrinkage H118's own 10-day Discovery->
    Validation drop showed (0.62 -> 0.28, 55%), not smaller as P2 hoped.
    This is the opposite of what would have supported "day 1 is the
    well-understood, selection-resistant part of H118's edge": the
    1-day cell is EQUALLY vulnerable to whatever Discovery-stage
    selection effect shrinks the 10-day figure, not immune to it
    because it's the fast part. Genuinely pre-registered result -- this
    document existed, with this exact prediction, before the Validation
    data was touched.
P3 — CONFIRMED by construction. No H118 row touched, no H118 data
    referenced in this candidate's own numbers, and this null result
    does not change H118's status, forward test, or review point in
    any way (STRICT SEPARATION maintained both directions).

## 6. Verdict

REFUTED at the load-bearing prediction. P2 -- the one genuinely
pre-registered, forward-looking prediction this document made -- was
contradicted: the 1-day cell shrinks from Discovery to Validation by
essentially the same proportion H118's full 10-day figure did, and
loses statistical credibility entirely (H118's own Validation stayed
barely credible; this one does not). The clean Discovery-slice
regime-splits (P1) were real but insufficient -- exactly the lesson
Scan 001 already taught this project once (surviving several
exploratory robustness cuts on Discovery data is not a substitute for
genuine out-of-sample testing) and this candidate reconfirms it a
second time, independently, at a different horizon.

Practical implication for H118's own mechanism doc (h118-vwap-dist-low.md,
not edited by this document, STRICT SEPARATION): the hope that "the
first day is the mechanistically clean, statistically robust part" is
NOT supported by this independent test. The front-loading in P2 there
(most of the 10-day points arriving in day 1) may be a real feature of
the GROSS return shape without implying the 1-day slice is any more
robust to Discovery-stage selection than the 10-day aggregate is. This
is a LEARN-worthy structural lesson, not a comment on H118's own
already-passed Holdout result.

CLOSES this candidate. vwap_dist_vs_atr/LOW's 2-attempt limit is now
EXHAUSTED (H118 = attempt 1, promoted; this variant = attempt 2,
REJECTED at Validation). No third attempt at any other horizon or
sub-window without a new staff-meeting-level justification. Ledger:
hyp-000136 (Discovery, PROMISING) -> hyp-000137 (Validation, REJECTED,
same candidate lineage via parent_hypothesis_id).
