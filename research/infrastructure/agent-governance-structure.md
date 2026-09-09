# Agent Governance Structure v2 -- Research Director, mandatory Integrity Gate, Portfolio scope

Frozen 2026-09-09 (third structural pass, following H118's Discovery+
Validation+Holdout result). Supersedes the prior version of this
document (2026-09-09, second pass). Source: Jason's review against
Tony_Project_Handoff.docx and the project's Master Methodology, plus
his explicit instruction that this project should now run on the
agent team's own judgment, with him providing direction rather than
being asked for routine input.

## What changed and why (this pass)

The prior version added the Research Director and Candidate Triage but
still treated Research Integrity as an informal, background presence
rather than a mandatory, independent gate. H118 exposed the gap
directly: it reached Holdout Generation 2 -- consuming a scarce,
irreplaceable slot -- on the strength of checks I (Claude) performed
myself (rediscovery/correlation check, regime splits). That is useful
work, but it is not the same as an independent adversarial review whose
job is to try to prove the candidate wrong. Per the methodology,
Research Integrity is not optional or occasional -- it governs
chronological separation, frozen specs, no post-result changes,
complete logging, multiple-testing awareness, realistic costs, and
out-of-sample validation THROUGHOUT the process, not as a stage that
can be skipped when things look promising.

Three changes this pass:
  1. Research Director confirmed as a permanent, standing authority
     (not new -- reaffirmed, now explicitly named a 7th agent for
     clarity rather than "not an execution step," since Jason's
     framing makes it a role, not merely a veto).
  2. Research Integrity becomes a MANDATORY, independent gate with
     veto authority, sitting both continuously across the pipeline
     AND as a required, explicit stop immediately before any candidate
     enters formal Discovery->Validation->Holdout confirmation. A
     candidate does not proceed past this gate on the strength of
     self-performed checks alone.
  3. Portfolio Agent's activation criterion and first task are both
     narrowed: it activates only once a candidate has genuinely
     cleared the full documented promotion bar (all three: 90% CI
     entirely above zero, >=0.05R economically meaningful, confirmed
     by the prescribed prospective test on untouched data), and its
     first job is never "combine these for more return" -- it is
     "does this provide incremental information beyond what we
     already have, or is it the same latent state restated."

## Pipeline (v2)

    Jason (direction, not routine sign-off -- see Standing Rule below)
      |
      v
    RESEARCH DIRECTOR  (research strategy & capital allocation -- what's worth pursuing)
      |
      v
    DISCOVERY AGENT  (maps candidate behaviors, reports novelty + search exposure)
      |
      v
    CANDIDATE TRIAGE  (Research Director function: A-F classification)
      |
      v
    MECHANISM AGENT  (testable mechanism predictions, not post-hoc stories)
      |
      v
    STATISTICAL AGENT  (stability, regime dependence, magnitude, selection sensitivity)
      |
      v
    RESEARCH DIRECTOR RE-EVALUATION  (is the evidence strong enough to spend more research capital?)
      |
      v
    MONETIZATION AGENT  (natural realization path; "no credible path" is a valid conclusion)
      |
      v
    *** MANDATORY INTEGRITY GATE ***  (independent adversarial review -- see below; VETO authority)
      |
      v
    DISCOVERY -> VALIDATION -> HOLDOUT  (existing pipeline, unchanged, this is where H118 currently sits)
      |
      v
    PORTFOLIO AGENT  (only once a candidate clears the full promotion bar: incremental-information test)

Research Integrity also operates CONTINUOUSLY across every stage above
(freeze rules, contamination, multiple-testing tracking, 2-attempt
limit, no resurrection) -- the Integrity Gate is a required, explicit
checkpoint IN ADDITION to that continuous role, not a replacement for
it. LEARN remains institutional memory consulted throughout, by every
agent and the Research Director.

## Research Director (7th agent, standing authority)

Question, always: "Are we researching the right thing?" Reviews what's
tested/failed/succeeded/genuinely-unexplored, novelty, accumulated
multiple-testing exposure, diminishing returns within a research
family, and whether the current methodology itself is still producing
useful discoveries (per the methodology's own principle: when it stops
working, change the methodology, don't keep generating strategies).
Authority: CONTINUE / MODIFY / PIVOT / ABANDON on any thread or family,
at any point. Performs Candidate Triage (A-F, unchanged from v1 -- see
prior spec in git history) and the Research Director Re-Evaluation step
newly added to the pipeline above: after Statistical, before
Monetization, an explicit second look at whether the evidence justifies
spending a Monetization + Integrity + confirmation-pipeline cycle on
this specific candidate, given everything already known.

## Discovery / Mechanism / Statistical / Monetization Agents

Unchanged from the v1 spec (git history: research/infrastructure/
agent-governance-structure.md as of 2026-09-09, first revision) --
Discovery reports novelty + search exposure + known-relationship
overlap; Mechanism requires testable predictions, not narratives;
Statistical requires the 4 questions (stability, regime dependence,
magnitude, selection sensitivity) plus mandatory disclosure of
same-data selection; Monetization stays last before Integrity,
determines natural realization path, "no credible path" is a valid,
successful conclusion.

## Research Integrity -- MANDATORY GATE, independent, with VETO authority

This is the structural correction. Research Integrity is not
background process and not optional. It has two roles:
  1. CONTINUOUS, across every stage (freeze rules, contamination
     prevention, multiple-testing tracking, 2-attempt limit, no
     hypothesis resurrection) -- unchanged from before.
  2. A MANDATORY, EXPLICIT GATE immediately before any candidate is
     allowed to enter formal Discovery->Validation->Holdout
     confirmation, or to accumulate further evidence once results
     exist. A candidate does not pass this gate on the strength of
     self-performed checks by whoever built the monetization spec --
     it requires an independent adversarial pass.

The Integrity Gate's standing brief, for every candidate: "Assume this
candidate is wrong. Find every reason we could be fooling ourselves."
Specifically examines:
  - data leakage
  - Discovery/Validation contamination
  - whether the candidate was selected after seeing the relevant result
  - multiple-testing exposure (naive and effective-independent-series)
  - whether related hypotheses were previously tested
  - whether the candidate is genuinely distinct from previous findings
  - whether the direction was determined beforehand (pre-registered)
    or fit to the result
  - whether any parameter or definition changed after seeing results
  - whether current evidence has been used to influence subsequent
    testing (leakage across candidates, not just within one)
  - whether the candidate is effectively a resurrection/reformulation
    of a closed hypothesis
  - whether its claimed statistical strength accounts for the full
    research history (how many other cells/candidates were scanned to
    produce it)

Research Integrity has VETO authority -- independent of the Research
Director, and the Director cannot override it. A candidate the
Integrity Gate does not clear does not proceed, regardless of how
promising the Director or the numbers look.

## Portfolio Agent -- activation criterion and first task, both narrowed

Activates ONLY once a candidate has genuinely cleared the full
documented promotion bar: (1) 90% bootstrap CI entirely above zero,
(2) >=0.05R economically meaningful, (3) confirmed by the prescribed
prospective test on untouched data (Validation, and per this project's
practice, Holdout). "Survived Discovery" or "survived Validation" alone
is NOT the activation trigger -- only the full bar.

When it does activate, its FIRST job is never optimization or "can we
make more money combining these." Its first job is: "Does this
candidate provide incremental information beyond what we already
validated, or is there evidence it's the same latent market state
restated in different variables?" The three pre-existing validated
findings (range-contraction, overnight coil, midday-afternoon range
persistence) are all volatility/range-persistence facts -- if a new
candidate is also volatility-related, Portfolio's job is to be
PARTICULARLY skeptical of double-counting before any diversification
claim is entertained, not to assume independence.

## LEARN

Unchanged (4 buckets: KNOWN TRUE, KNOWN FAILED, KNOWN FAILURE MODES,
KNOWN UNEXPLORED) -- see prior spec in git history for the full current
contents. Consulted by every agent and the Research Director throughout.

## Reporting format

Unchanged: Finding / Confidence / Novelty / Research Value /
Recommendation (CONTINUE/MODIFY/PIVOT/ABANDON), on every agent report.

## Standing rule change (2026-09-09): team runs on its own judgment

Jason's explicit instruction: this structure is now meant to reduce how
often he is asked for input, not increase it -- the team should follow
its own direction using this governance structure, not default to
asking him. This does not relax any existing standing rule (the 90%-
promotion-bar-clearance and $5+-purchase exceptions to "don't loop me
in" are unchanged and still the only mandatory stop points) -- it
means the Research Director + Integrity Gate structure itself is now
the mechanism for deciding what to research next and whether to trust
a result, in place of asking Jason for that judgment. He directs the
project's overall course; the agent team executes and self-governs the
day-to-day research decisions within it.

## H118's status under this structure

H118 (vwap_dist_vs_atr LOW tercile, 10d drift) reached Holdout
Generation 2 and passed (Discovery/Validation/Holdout all CI-above-
zero) WITHOUT having gone through the mandatory Integrity Gate defined
above -- it was screened by checks I performed myself, not an
independent adversarial pass. Per this corrected structure, its status
is downgraded from "Holdout Passed" (treated as settled) to:

    PROMISING / UNDER INDEPENDENT INTEGRITY REVIEW

pending a full adversarial Integrity Gate pass against the standing
brief above. This does not undo the Holdout result or free up the
consumed slot -- it means the result is not yet trusted as fully
compliant evidence until Integrity has tried to break it. The Integrity
Gate pass follows immediately in the ledger/BACKLOG record.

## Status

Frozen governance spec, third pass. No code changes required by this
document itself. Immediate next application: run the mandatory
Integrity Gate pass on H118 using the standing brief above, and record
the verdict (PASS / VETO / CONDITIONAL) before H118 accumulates any
further evidence (Forward Validation or otherwise).
