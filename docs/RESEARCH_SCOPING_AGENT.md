# Research Scoping Agent

*2026-09-03. A standing, repeatable role for turning a candidate idea into
a proper frozen-specification draft -- proposed at Jason's request, after
he asked whether "an agent that scopes things" could be built to support
the project going forward. Complements
docs/RESEARCH_INTEGRITY_PROTOCOL.md and docs/PATH_TO_PROFITABILITY_ADVISOR.md
rather than replacing either.*

## Why this exists

Every hypothesis this project has ever tested needed a carefully written
frozen specification BEFORE any code was written -- that discipline is
why 22 honest results exist instead of 22 quietly-adjusted ones. Up to
now, writing that first draft has been done freehand, by whoever is in
the working conversation at the time, with no fixed checklist. That
worked, but unevenly: the multi-factor combination scoping draft needed
a second full revision after the Advisor's review caught six real gaps
that a checklist would have caught up front (a missing-data plan, an
undefined evaluation metric, a missing stability check, and so on).

This document names that first-draft-writing step as its own role, with
its own checklist, so the next candidate idea -- whether scoped by Claude
in some future session, or eventually by a more automated process -- starts
from the same standard instead of reinventing it each time.

## What this is NOT

Not the Path-to-Profitability Advisor. The Advisor critiques a proposal
that already exists and gives an independent opinion on direction,
pacing, and practical build concerns. The Scoping Agent writes the
proposal in the first place. They are sequential, not overlapping: scope
first, then get the Advisor's take on the result, per
`PATH_TO_PROFITABILITY_ADVISOR.md`'s existing mandatory-consultation
rule.

Not the future "Strategy R&D Agent" described in
`docs/RESEARCH_INTEGRITY_PROTOCOL.md` (Phase 2: generate/mutate/combine
hypotheses at scale, gated behind infrastructure that is now built but
not yet used for that purpose). This is a narrower, usable-right-now
piece: the specification-writing step such a system would eventually
need, done by hand, one candidate at a time.

Not an authorization mechanism. A completed scoping draft is exactly
that -- a draft. It carries no authority to write implementation code on
its own. `docs/RESEARCH_INTEGRITY_PROTOCOL.md`'s frozen-spec-before-
implementation rule and Jason's explicit sign-off still govern whether
anything in a draft ever gets built.

## The checklist every scoping draft must satisfy

A draft is not complete until it can honestly check every item below --
this is what "line-by-line ready for review" means going forward, so
Jason and the Advisor are reviewing a draft that has already cleared its
own obvious gaps, not doing that work for the first time themselves.

1. **Provenance stated plainly.** Where did this idea come from -- the
   backlog, a past study's disclosed side-observation, outside research?
   Is it genuinely a new mechanism, or a variant of something already
   tested (and if the latter, what specifically makes it different
   enough to be worth a fresh test)?
2. **Reuse over invention.** Every function, statistic, or convention
   that already exists in this codebase and fits is reused unmodified,
   named explicitly. New code is written only for the one genuinely new
   piece the idea requires.
3. **Every free choice pinned down before any result exists.** Exact
   population definitions, thresholds, horizons, cost assumptions -- all
   frozen in the document itself, not left as "to be decided during
   coding."
4. **Known risks and reasons for skepticism disclosed up front, not
   after.** If there is a real, specific reason to expect this might not
   work (a conflicting finding elsewhere in the project, a small sample,
   a structural reason for doubt), it is written into the draft before
   anything is run -- exp-045's pooled-CPI+NFP draft disclosing the
   CPI/NFP sign disagreement in advance is the model to follow.
5. **A stated path from result to verdict.** Exactly how a raw
   statistical result becomes "promote," "kill," or "retest" -- which
   gates apply, at what threshold, and whether the standard 150-trade /
   90%-CI promotion bar applies as-is or needs a disclosed, deliberate
   adaptation (per the precedent set for exp-038's daily-resolution
   bar).
6. **Discovery/Validation/Holdout discipline respected explicitly.**
   States plainly that only Discovery data is used for the search
   itself, and whether/when a Validation-slice check would become
   appropriate if the draft's gates are cleared.
7. **Multiple-testing accounting addressed.** Confirms the candidate
   will get its own experiment number and Research Ledger entry, and --
   if it is itself a search over multiple variants rather than one
   pre-registered test -- how many variants, and how Larry's DSR/PBO
   tooling will be applied to the result.
8. **An explicit "What this is NOT" section.** Scope boundaries stated
   plainly, mirroring every prior frozen spec in this project.
9. **ASCII-only**, matching this project's existing convention for every
   committed document.

## How it runs

A fresh Agent, isolated from whatever working conversation raised the
candidate idea, given: (a) this document, (b) the specific candidate
idea or backlog item to scope, and (c) instructed to read the real
repository directly first -- past experiments, `docs/BACKLOG.md`,
`docs/RESEARCH_INTEGRITY_PROTOCOL.md`, and any directly relevant past
study -- before drafting anything, the same "read the real files, not a
summary" discipline the Advisor already follows. Its output is a
complete draft scoping document satisfying the checklist above, marked
explicitly as a draft, not yet authorized for implementation.

The standing pipeline this creates: **scope** (this role, produces a
checklist-complete draft) -> **review** (the Path-to-Profitability
Advisor, per its own existing mandatory-consultation rule) -> **decide**
(Jason, line-by-line sign-off) -> **build** (only after sign-off, per
`docs/RESEARCH_INTEGRITY_PROTOCOL.md`'s existing frozen-spec discipline).

## How this document changes

Same governance as `docs/PATH_TO_PROFITABILITY_ADVISOR.md`: amended only
through an explicit, deliberate decision, with a stated reason, Jason's
sign-off, and a new dated History entry -- never quietly, and never as a
reaction to a single day's inconvenient result.

## History

- 2026-09-03: Proposed after Jason asked whether an agent could be built
  specifically to scope things out in support of the project, following
  the multi-factor combination model's scoping draft needing a full
  revision pass once the Advisor's review caught gaps a checklist would
  have caught up front. This document formalizes the scoping step as its
  own named, checklist-driven role, sequenced ahead of the existing
  Advisor review rather than replacing it.
