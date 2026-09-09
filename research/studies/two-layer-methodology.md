# Two-Layer Research Methodology (Canonical)

Status: FROZEN as of 2026-09-09. This document is the authoritative
statement of the project's research methodology, superseding any looser
prior description (including informal "staff meeting" summaries). It is
written to formally set in stone the correction Jason gave on 2026-09-09
after reviewing an earlier, imprecise restatement of the project's vision.
Amends/consolidates: research/studies/observatory-finding-protocol-addendum.md,
research/studies/observatory-v1-design-spec.md,
research/studies/observatory-v2-design-spec.md,
research/studies/observatory-v3-design-spec.md.

## Why this document exists

An earlier summary of the project's vision used two phrases that are too
strong and were explicitly corrected:

- "after a behavior is confirmed real" -- wrong. The Observatory is
  exploratory only. It cannot confirm, prove, or validate that a behavior
  is real. It can only surface a candidate for further investigation.
- "the measurement side works -- it correctly finds real patterns" --
  wrong. What the project actually has evidence for is a set of
  interesting conditional relationships, not proof of genuine, persistent
  edges. The Observatory's own exploratory nature and multiple-testing
  exposure mean this distinction is not cosmetic.

Both corrections point at the same underlying principle: discovery and
confirmation are different activities, done by different layers of the
process, and the outputs of the first layer are never treated as if they
were outputs of the second.

## The two layers

### Layer 1: Market Behavior Observatory (discovery / characterization only)

Purpose: discover and characterize potentially meaningful behaviors.
Never to prove an edge exists. Never to create or imply a trading
strategy. Never to "confirm" anything.

Inputs: an objectively defined market event or condition.
Output: a measurement of what happens after that event/condition,
relative to an appropriate baseline (a Behavioral Finding, per
observatory-finding-protocol-addendum.md).

What the Observatory is allowed to say about its own output: this cell/
cluster looks real-looking (coherent effect direction across related
cells, plausible mechanism, adequate sample size) or looks like a likely
scan artifact. That is a descriptive judgment about measurement quality,
not a claim of a proven edge.

What the Observatory is never allowed to say: that a behavior is
"confirmed," "validated," "proven," or that it constitutes a trading
edge. Those words are reserved for Layer 2 outcomes only.

### Layer 2: Monetization and Validation (confirmation, separate hypothesis)

Purpose: take an Observatory-identified candidate behavior and ask a
SEPARATE, explicitly documented question -- can this behavior be
monetized by some specific, frozen trading rule?

A monetization hypothesis is:
- Its own hypothesis spec, referencing the parent Behavioral Finding by
  ID, with its own frozen entry/exit/stop/target rules written down
  BEFORE the relevant test is run.
- Run through the existing Discovery -> Validation pipeline (chronological
  splits, statistical evaluation, promotion bar: 90% bootstrap CI
  entirely above zero AND economically meaningful (>= 0.05R), confirmed
  by one pre-registered prospective test on fresh out-of-sample data, no
  retuning after a null result).
- The only place in the whole process where the words "confirmed,"
  "validated," "promoted," or "rejected" are appropriate.

## The critical principle

A behavioral finding can be interesting without being a proven edge.
A failed trading implementation does not necessarily disprove the
underlying behavior -- it disproves that specific, frozen trade design
against that behavior. The behavior itself is only falsified by
re-examining the measurement (a new Observatory scan), never as a side
effect of a failed Layer 2 test.

This is why a Behavioral Finding document is frozen once written and is
never rewritten because a later monetization hypothesis against it
failed (see observatory-finding-protocol-addendum.md).

## The research sequence

MARKET -> OBSERVE -> MEASURE -> CHARACTERIZE -> COMPARE TO BASELINE ->
ASSESS ROBUSTNESS -> IDENTIFY CANDIDATE BEHAVIOR -> FORMULATE SEPARATE
MONETIZATION HYPOTHESIS -> FREEZE -> VALIDATE -> PROMOTE OR REJECT.

The strategy is always downstream of the behavior. The behavior is
never defined by the strategy.

## What changes about how research starts

This is not merely "add an Observatory alongside the old process." It
changes what constitutes the STARTING POINT of research.

- The Observatory (behavior-first: observe a market condition, measure
  what follows, characterize it, only then ask if it's monetizable) is
  now the DEFAULT hypothesis-generation mechanism for new research.
- The old strategy-first pipeline (start from a trading idea/intuition,
  build it, test it) still exists and remains available for formal
  Discovery/Validation testing -- a hypothesis can still enter the
  pipeline that way. But it is no longer the default mechanism for
  generating NEW ideas. New research defaults to behavior-first.

## Open, not-yet-answered question

Does behavior-first (Observatory-sourced) research actually produce
higher-quality candidates or more validated edges than the old
intuition/strategy-sourced process? This has not been demonstrated
either way. It is itself a question the project needs to test over time
(e.g., by comparing the eventual Validation-survival rate of
Observatory-sourced hypotheses against historical strategy-sourced
hypotheses), not an assumption baked into the methodology.

## Required classification step for legacy/pending work

Before resuming ANY previously-unresolved research thread that predates
this document, it must first be classified against this methodology:

- **CONTINUE** -- legitimate unresolved question; completing it could
  materially inform the research under the current methodology as-is.
- **ABANDON** -- legacy strategy-first idea that no longer fits the
  current methodology and does not warrant reframing.
- **MODIFY** -- the underlying research question still has value but
  needs to be reframed as a behavioral investigation (i.e., routed
  through Layer 1 -- given its own Behavioral Finding -- before any
  further monetization work) rather than continued as originally scoped.

The priority of any research action is set by its probability of
producing a genuine edge under this methodology -- never merely by
whether it happens to be unfinished. Classification results and their
reasoning are recorded in docs/BACKLOG.md and/or the ledger at the time
the classification is made.

## Addendum (2026-09-09): Institutional Knowledge as a Third, Persistent Layer

Jason's refinement, formalized here. The research sequence is:

MARKET -> OBSERVE -> MEASURE -> CHARACTERIZE -> HYPOTHESIS -> FREEZE ->
TEST -> VALIDATE -> PROMOTE/REJECT -> **LEARN**

The new step, LEARN, is not another pipeline stage a single hypothesis
passes through -- it's a persistent, accumulating layer that sits
alongside the two-layer structure and feeds every future hypothesis's
design, without ever retroactively reopening a closed one.

**The guardrail, stated precisely:** "build on what we've learned"
means accumulating checkable KNOWLEDGE (failure modes, magnitude
scales, structural constraints), never accumulating MODIFICATIONS to a
specific hypothesis. A rejected hypothesis is never reshaped based on
its own result beyond the existing two-attempt limit (H81->H82,
H87->H89, H92->H93 pattern) -- that boundary is unchanged. What's new
is that its REASON for failure becomes a standing, reusable fact,
separate from the hypothesis itself, checked against before writing
the NEXT, unrelated hypothesis.

**Failure-mode taxonomy accumulated so far** (from ~104 hypotheses):

1. **Cost-dominance** -- a real, credible gross effect is wiped out by
   fixed transaction cost because the realistic risk distance (15-25
   points for most NQ intraday setups) is only a few multiples of
   round-trip cost. Diagnosed 2026-09-08, now enforced mechanically as
   the ATR-normalized cost floor (0.05) at Observatory scan time
   (v4-v6) -- a candidate below this floor is deprioritized before a
   hypothesis spec is ever written, not discovered after a failed test.
2. **Thin-sample overconfidence** -- a technically-credible CI (entirely
   above/below zero) computed on too few observations (n<15-40
   depending on the test) is not trustworthy even when it passes the
   mechanical bar. (hyp-000051 n=9; several Observatory Interesting-
   but-thin candidates in v4/v6.) Enforced via MIN_N_FOR_PROMISING=40
   for "Promising" vs. n>=15 for "Interesting" (not fully trusted).
3. **Correlated-lens double-counting** -- aggregating several variants
   of the SAME underlying signal and treating their agreement as
   corroboration is not independent evidence. (Collective-evidence
   pilot v1, hyp-000025/027, explicitly disclosed and later fixed in
   pilot v2 by using 3 genuinely independent mechanisms.)
4. **Direction ambiguity in aggregate/pooled measurements** -- a real,
   credible POOLED effect (e.g. "2+ independent signals agreeing
   predicts X") can dissolve once restricted to a single, consistent
   trade direction -- the pooled statistic was real but not itself
   actionable. (OBS-FINDING-010 / collective-evidence v2, 2026-09-09.)
5. **Marginal Discovery passes don't replicate** -- a Step-1+2 pass
   whose CI lower bound sits near zero (barely credible) should be
   treated as a weak signal for the prospective test, not a strong one
   -- so far 0-for-several on marginal passes surviving Validation
   (H93's marginal pass failed; COT positioning's stronger Discovery
   result also failed). Not yet formalized as a numeric rule (would
   need more data points to calibrate honestly) -- flagged as an open
   question for the LEARN layer to eventually resolve, not assumed.

**How this is used going forward:** before writing any new Observatory
Behavioral Finding or hypothesis spec, check candidate 1-5 above --
does the candidate's expected magnitude clear the cost floor (1)? Is
its sample size adequate for the confidence level being claimed (2)?
Are its contributing signals genuinely independent, not variants of
one thing (3)? If it's a pooled/aggregate measurement, does the effect
survive being split by actionable direction (4)? If it clears Discovery
only marginally, is that flagged honestly rather than treated as
equivalent to a strong pass (5)? This doesn't add new pipeline steps or
new sign-offs -- it's a checklist drawn from accumulated failures,
applied silently at design time, the same way the ATR cost floor
already is for failure mode 1.

This addendum itself is subject to the same discipline it describes:
it will be extended (new failure modes appended) as the project learns
more, but never rewritten to fit a specific hypothesis's result.

## Retrospective application (2026-09-09): applying LEARN to all 81 past rejections

Classified every currently-REJECTED hypothesis (81 of 104 logged) by
which LEARN failure mode, if any, explains its rejection. Result:

- **~23 (28%)** hit one of the 5 named failure modes above -- a real,
  credible signal was found and then lost to a specific, now-known
  downstream cause (marginal Discovery passes not replicating: 9;
  thin-sample overconfidence: 7; single-event/artifact concentration: 4;
  cost-dominance: 2 explicitly named in their own notes, though the
  2026-09-08 diagnostic showed this mechanism is present much more
  broadly across the Observatory-era hypotheses than just these 2 --
  most just don't name it explicitly in the notes text; correlated-lens
  double-counting: 1).
- **~55-60 (roughly 70%)** are CLEAN NULLS -- no real effect was ever
  detected in the first place (CI spans zero from Step 1, no gross
  edge, wrong-direction point estimate). These are not failures of
  monetization or sample size; the underlying idea itself had nothing
  there.

**This is the single most useful retrospective finding from applying
LEARN to the project's history**, and it reframes the project's own
self-diagnosis: the popular internal narrative (informed heavily by
the 2026-09-08 cost-dominance diagnostic, which was itself based on a
small number of Observatory-era near-misses) was that "the project
finds real effects but can't monetize them." Applied across all 81
rejections, that story explains only about a quarter of them. The
majority of tested ideas -- most bar patterns, most cross-asset
standalone signals, most legacy strategy-first re-mines -- never
showed a real effect at all, at any stage, regardless of cost or
sample size. Cost-dominance and the other 4 failure modes are real and
worth screening for (and are, mechanically, in Observatory v4-v6), but
they describe the minority case: candidates that got somewhere and
then hit a specific wall. Most candidates never got anywhere.

**Practical implication for future candidate sourcing:** this argues
for weighting effort toward whatever process improves the base rate of
finding a real effect in the first place (better event definitions,
genuinely novel data, or the Observatory's own baseline-relative
measurement approach, which empirically has a better clean-null vs.
real-signal ratio than the legacy strategy-first approach it replaced
-- not independently verified with a formal count in this pass, but
consistent with the 2026-09-08 audit's origin-family breakdown) over
further refining the failure-mode screens for candidates that already
clear the "real effect" bar, since that bar is the harder one to clear.
