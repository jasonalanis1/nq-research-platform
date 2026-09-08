# Observatory Protocol Addendum: Behavioral Finding as a Required Intermediate Object

Amends: research/studies/observatory-v1-design-spec.md
Reason: process gap identified by Jason after H81/H82 (2026-09-08) --
the pipeline went straight from "Observatory scan produces a Promising
cell" to "write a monetization hypothesis spec," with the behavioral
characterization folded into the hypothesis spec's own "Origin" section
rather than existing as its own independently-evaluated object. That is
too compressed relative to the two-layer design that was actually
approved: measurement layer, then strategy layer, evaluated separately.

## The fix

A THIRD document type is now required between an Observatory scan and
any hypothesis spec: a **Behavioral Finding**.

1. **Observatory scan** (existing) -- produces a candidate list, ranked
   Promising/Interesting/Weak/No meaningful difference. Not itself
   evaluated further; purely descriptive output of the measurement
   instrument.
2. **Behavioral Finding** (NEW) -- one specific Promising or Interesting
   cell (or a small coherent cluster of cells, as with the opening-hour
   cluster) is written up on its own, with NO trade design attached:
   - Finding ID (`OBS-FINDING-NNN`), the exact event/state/horizon
     definition, effect size and direction, n, 90% CI, cross-period
     (year-thirds) consistency, concentration ratio, and an economic-
     plausibility note (a stated mechanism, or explicitly "no
     mechanism identified").
   - An explicit judgment: does this look like a real, structural
     market behavior, or a scan artifact that happens to clear the
     ranking bar? This judgment is made by looking ONLY at the
     measurement -- no entry, stop, or target exists yet, so there is
     nothing to be anchored by.
   - The finding is frozen once written -- its description does not
     change after a monetization hypothesis is attempted, regardless
     of that hypothesis's result.
3. **Hypothesis spec(s)** (existing, e.g. H81/H82-style) -- one or more
   monetization attempts against a frozen Behavioral Finding, each
   referencing it by Finding ID as `parent_finding_id`. The finding
   itself is never rewritten because a hypothesis against it failed;
   only the finding's own future re-scans (a new Observatory run) could
   update it, and that is a separate, explicit action, not a side
   effect of a failed trade test.

## Why this matters in practice

Without step 2, a failed hypothesis reads as ambiguous: did the
behavior not really exist, or did the trade design fail to capture a
real behavior? Jason's own post-H81 correction ("real and credible" was
too strong given upstream multiple-testing exposure) is exactly the
kind of judgment that belongs in the Behavioral Finding, decided once,
independently of any trade result -- not re-litigated informally after
each hypothesis outcome.

## Retroactive application

`OBS-FINDING-001` (research/studies/obs-finding-001-opening-hour-reference-level-cluster.md)
is written retroactively for the opening-hour cluster that produced
H81/H82, for documentation consistency. It does not change the
already-closed status of that behavior line -- both monetization
attempts still failed and the line stays closed. Every candidate from
here forward (starting with candidate #2 of the 3-5-candidate pilot)
gets its Behavioral Finding written and reviewed BEFORE any hypothesis
spec is drafted.
