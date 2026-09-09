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
