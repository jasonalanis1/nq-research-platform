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
    produce it) -- ADDED 2026-09-09: this is no longer assessed
    informally per candidate. Run `src/project_wide_multiplicity.py`
    (Sidak family-wise correction, stage-specific project-wide trial
    counts) and cite its adjusted CI for the candidate's Discovery,
    Validation, and Holdout legs. Update SCAN_REGISTRY in that module
    first if a new Discovery Engine scan has run since its last update.
    See research/studies/project-wide-multiplicity-2026-09-09.md for
    the method and the first project-wide application (closes this
    doc's own H118 open item below).

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

## H118's status under this structure (STALE -- see AMENDMENT v2.1 Correction)

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

## Status (v2 -- superseded by AMENDMENT v2.1 below)

Frozen governance spec, third pass. No code changes required by this
document itself. Immediate next application: run the mandatory
Integrity Gate pass on H118 using the standing brief above, and record
the verdict (PASS / VETO / CONDITIONAL) before H118 accumulates any
further evidence (Forward Validation or otherwise).

---

# AMENDMENT v2.1 -- Session Protocol: agent applicability, RETURN, and the STAFF MEETING

Frozen 2026-09-10. Source: Jason's direction that autonomous 4-hour
sessions must reach the same level of agent utilization, collaboration
and learning that the sessions did when he was personally in them --
and his explicit instruction on how to handle a skipped stage: not a
hard block, but "reviewed if it skips by an agent whichever makes most
sense, and that agent can recourse it to the appropriate workflow;
agent can call a staff meeting if necessary within the next step to
determine appropriate direction needed for the hypothesis."

Nothing in v2 is repealed. This amendment says WHEN each agent runs,
WHAT HAPPENS when one is skipped, and HOW disagreement gets resolved.

## The problem this fixes

Measured 2026-09-10 across every automated session on record: the
running chain is Discovery -> Statistical -> dead. Nothing else has
fired. Scan 003 died on a volatility-regime split; Scan 004 died on
split-sample, 0 of 36. Candidate Triage, Mechanism, Director
Re-Evaluation, Monetization and the Integrity Gate have never executed
inside an automated session, and LEARN has never been invoked by name.

Most of that is the filter working -- a candidate killed at Statistical
legitimately never reaches Monetization. But three things are genuine
defects, not consequences of the filter:

  1. Nothing detects a SKIPPED stage. If a session promotes a candidate
     without a Mechanism doc, nothing notices.
  2. The Research Director never actually convenes. It has a mandatory
     Re-Evaluation checkpoint in the v2 pipeline that has never fired,
     and a standing "is the methodology still working" duty that no
     event triggers.
  3. There is no forum for disagreement. When two agents reach opposite
     conclusions, the session picks one silently.

## Rule 1 -- Applicability: an agent runs when its input exists

An agent is not skipped because a session is busy; it is skipped only
because its INPUT CONDITION was not met. Each session must be able to
say, for every agent, either "ran" or "input condition not met."

    AGENT                      INPUT CONDITION (runs when...)
    -------------------------  ------------------------------------------
    LEARN                      ALWAYS, before any scan scope is frozen and
                               before any candidate is re-tested. Checks the
                               4 buckets (KNOWN TRUE / KNOWN FAILED / KNOWN
                               FAILURE MODES / KNOWN UNEXPLORED) for
                               resurrection and for a failure mode this
                               candidate already matches.
    Research Director (entry)  A scan or test is about to be scoped.
                               Sets direction; owns the freeze.
    Discovery                  A frozen scope exists.
    Candidate Triage           A scan produced >=1 cell clearing its gate.
                               Grades A-F. D/F closes without spending a
                               hypothesis ID.
    Mechanism                  A candidate graded C or better exists.
                               Produces research/mechanisms/<name>.md.
                               No mechanism doc, no advance (MECHANISM GATE,
                               binding from 2026-09-10).
    Statistical                A candidate has a mechanism doc. The 4
                               questions plus mandatory same-data selection
                               disclosure.
    Director Re-Evaluation     A candidate survived Statistical. Explicit
                               second look: does this evidence justify
                               spending a Monetization + Integrity +
                               confirmation cycle, given everything known?
    Monetization               Director returned CONTINUE at Re-Evaluation.
                               "No credible path" is a valid success.
    Integrity Gate (checkpoint) A candidate is about to cross Discovery->
                               Validation or Validation->Holdout. VETO
                               authority, not advisory.
    Integrity Gate (audit)     ALWAYS, at the close of every session.
                               See Rule 2.
    Portfolio                  A candidate cleared the FULL promotion bar
                               (90% bootstrap CI above zero AND >=0.05R AND
                               confirmed on untouched data). Currently
                               dormant: 0 validated directional strategies.

Every agent report uses the v2 format, unchanged: Finding / Confidence /
Novelty / Research Value / Recommendation (CONTINUE / MODIFY / PIVOT /
ABANDON).

## Rule 2 -- RETURN: the Integrity Gate audits every session close

The Integrity Gate already operates continuously across every stage
(v2). This amendment gives that continuous role one concrete, mandatory
action: at the CLOSE of every session, before the lock is released, the
Integrity Gate audits each candidate that moved during the session
against Rule 1.

If a required stage was skipped, the Integrity Gate issues a RETURN:

  - The candidate is routed back to the missing stage.
  - The RETURN is written to the top of the NEXT_UP queue, ahead of new
    work, so the next session picks it up first.
  - It is recorded in the session report with the stage, the candidate,
    and what was missing.

A RETURN is a course correction, NOT a block and NOT a kill. The
candidate is not rejected, the work already done is not discarded, and
no hypothesis ID is spent or freed. The pipeline resumes at the stage
that was missed.

Chosen deliberately over a hard gate: a hard block would stall a
candidate until a human intervened, which is exactly the dependency
this project is trying to remove.

## Rule 3 -- STAFF MEETING: convened by the Director, requested by anyone

Any agent MAY REQUEST a staff meeting. Only the Research Director
convenes one. It must be convened -- not deferred past the next step --
when any of the following occurs:

  a. SECOND RETURN on the same candidate. The routing did not take;
     something structural is wrong, not procedural.
  b. CONFLICTING RECOMMENDATIONS. Two agents return different
     dispositions on the same candidate (e.g. Statistical says
     CONTINUE, Mechanism reports its prediction failed).
  c. ZERO-SURVIVOR SCAN, or EVERY 3rd CLOSED SCAN. This is the
     methodology review: is the approach itself still producing
     discoveries? Per the Master Methodology's own principle -- when a
     method stops producing discoveries, change the method rather than
     keep generating candidates. Standing as of 2026-09-10: Scans 001,
     003 and 004 all returned zero survivors; Scan 002 produced the
     only survivor in project history (H118). This condition is
     ALREADY MET and the review is overdue.
  d. ANY AGENT REQUESTS ONE and states why.

A staff meeting produces exactly ONE disposition -- CONTINUE / MODIFY /
PIVOT / ABANDON -- plus the specific change that follows from it. It is
recorded in the session report with each agent's position, not only the
outcome, so a later session can see the disagreement and not relitigate
it blind.

The Integrity Gate's VETO survives inside the staff meeting. A meeting
cannot overrule it by majority; the Director cannot overrule it at all.

## Rule 4 -- The session report

Session-level, one per run, at research/sessions/YYYY-MM-DD-HHMM.md.
Written before the lock is released, even on a short or interrupted run.

    ## Session <timestamp local> -- <duration>

    ### Agents
    <agent> -- RAN: <Finding / Confidence / Novelty / Research Value /
                     Recommendation>
    <agent> -- NOT RUN: <which input condition was not met>
    (every agent in Rule 1 appears in one of these two lists; an agent
     omitted entirely is itself an audit finding)

    ### Returns issued
    <candidate> -> returned to <stage>: <what was missing>
    (or: none)

    ### Staff meeting
    <convened / not convened>. Trigger: <a-d>. Positions: <per agent>.
    Disposition: <CONTINUE / MODIFY / PIVOT / ABANDON>. Change: <what>.

    ### Moved this session
    <what actually changed in the ledger, the queue, or on disk>

    ### Queued next
    <top of NEXT_UP after this run>

This is the artifact that answers "what happened while I wasn't
watching" without reading the ledger. The daily research report reads
from these.

## Rule 5 -- LEARN is consulted by name

LEARN is a standing layer, not a pipeline step, and correctly has no
position in the chain. But "consulted throughout" has in practice meant
"never invoked," with resurrection-checking happening only because
whoever scoped a scan happened to remember (Scan 004 did; nothing
guaranteed it).

From 2026-09-10, LEARN is consulted BY NAME at two points, and its
finding is recorded: before a scan scope is frozen, and before any
candidate is re-tested. It answers two questions: has this been closed
before under another name, and does it match a KNOWN FAILURE MODE.

## Correction to v2: H118's status

The v2 section "H118's status under this structure" is now STALE and is
superseded here. It was written before the Integrity Gate ran and
describes a state that no longer holds.

Actual status as of 2026-09-10:

  - Holdout Generation 2: PASSED (slot 1 of 5 consumed, Jason's
    explicit sign-off 2026-09-09). The slot is spent either way.
  - Mandatory Integrity Gate: RUN 2026-09-09, one-shot, against the
    standing adversarial brief. Verdict CONDITIONAL PASS, recorded at
    research/studies/h118-multiplicity-integrity-review-2026-09-09.md.
    Conditions: re-baseline the working effect to Holdout ~0.40R
    (floor 0.14R), never quote the 0.62R Discovery figure, record the
    corrected Validation interval, and lock the forward review point.
  - Current stage: PROSPECTIVE STATISTICAL FORWARD TEST. Live since
    2026-09-08, one open position, research/forward_validation/
    h118_forward_log.jsonl. Ledger: hyp-000134 FORWARD VALIDATION.
  - Review point, pre-registered and locked: 40 resolved trades AND
    12 months. Never moves, tighter or looser.
  - Portfolio: NOT activated. Forward test precedes Portfolio; the bar
    Portfolio activates on is what the forward test is establishing.

H118 and EXP-047 remain outside automated scope entirely (SCOPE
BOUNDARY, 2026-09-09): automated sessions flag and stop, never act.
That includes RETURNs -- the Integrity Gate audit may FLAG a gap on a
promoted candidate, but may not route, re-run or modify it.

## Status

Frozen amendment. No code changes required. Immediate application: the
Rule 3(c) methodology staff meeting is already triggered and overdue,
and the Mechanism docs for the three candidates now at Validation
(range contraction, overnight coil, midday-afternoon persistence) are
outstanding under the MECHANISM GATE.

---

# AMENDMENT v2.2 -- the empty queue is a Discovery trigger, not a stopping point

Frozen 2026-09-10. Source: Jason, explicitly, after v2.1's first day:
sessions are NOT to stop early or cap their output. "I want them to run
as much as they can... it should work the queue till dry and then yes
open the invitation to staff meeting with discovery."

This repeals two economy measures added earlier the same day: the
80-line session report cap, and the instruction to end a run once the
remaining queue was blocked. Neither survives. A session works the
queue until it is dry, and a dry queue is a trigger, not an ending.

## New staff meeting trigger (e): QUEUE DRY

Added to AMENDMENT v2.1 Rule 3. The Research Director MUST convene a
staff meeting when the queue is empty or everything left in it is
blocked. Unlike the other four triggers, this one is not about
resolving a dispute -- it exists to GENERATE the next work. DISCOVERY
LEADS IT; the Director chairs.

Order of business, fixed, because the order is what keeps it honest:

  1. LEARN reports FIRST, before any idea is floated. It states what
     the KNOWN UNEXPLORED bucket actually still holds -- not what
     sounds new. An idea that has already been closed under another
     name is not a candidate, and LEARN is the only thing standing
     between the project and re-testing its own graveyard.

  2. DISCOVERY proposes directions, drawn from what LEARN just said is
     genuinely untried. It states, per direction: what state variable,
     what mechanism claim it would be testing, and what horizon. The
     STANDING RESEARCH PRIORITY applies -- short-horizon candidates
     resolve faster and are preferred over 10-day drift, all else
     equal.

  3. INTEGRITY GATE rules on resurrection, PER VARIABLE, BEFORE any
     scope is written. Every proposed variable gets an explicit ruling:
     new, or a second attempt on a closed family. A second attempt
     engages the 2-attempt limit and must be logged as such. This
     ruling is not advisory and the Director cannot overrule it.

  4. STATISTICAL states the cost of scanning at all: another scan
     raises the project-wide trial count and tightens the Sidak
     correction for every candidate still in flight. If candidates are
     mid-pipeline, that cost may exceed the value of a new scan --
     say so plainly rather than treating a scan as free.

  5. MECHANISM states whether any proposed direction can carry a
     PRE-registered mechanism prediction. Per v2.1's own finding, this
     project has never once done mechanism work prospectively. A
     direction that can be predicted before it is measured is worth
     more than one that can only be explained afterwards, and should
     be preferred where the choice exists.

  6. DIRECTOR issues ONE disposition and freezes the resulting scope.
     That frozen scope becomes the new queue.

If the meeting concludes that NOTHING is worth scanning -- a legitimate
outcome, and the one the methodology's own "when a method stops
producing discoveries, change the method" principle points at -- then
the disposition is PIVOT or ABANDON on the current method, and the
queue it produces is the work of finding a different approach. It is
never "nothing to do."

## What does NOT change

Report length is bounded by what the work requires, not by a line
count. The Integrity Gate audit still closes every session. RETURNs,
the SCOPE BOUNDARY, the MECHANISM GATE, and the never-bent rules
(review points, Holdout slots, $5+, live capital) are untouched.

---

# AMENDMENT v2.3 -- the Idea Inventory, and the standing guard against manufactured work

Frozen 2026-09-10, from the staff meeting Jason convened on what should
happen when the queue is empty. Disposition MODIFY, unanimous, no veto.

His constraint, in his words: he does not want "a session that just
keeps going and going," and he does not want "manufactured work, fake
work" -- but he also does not want the work minimized. "We need to be
doing genuine testing, genuine work." Those reconcile only if the
supply of ideas is generated in slack time and spent under load, and
if there is an explicit, honest terminal state.

## Why generating at empty is the wrong time

Positions from the meeting, recorded:

  LEARN: the failure is not that the queue empties. It is that "what
  is genuinely unexplored" is recomputed from scratch, from memory, by
  whoever happens to be running, at the exact moment work has run out.
  It should be a maintained artifact, not a recollection.

  DISCOVERY: generation at empty is generation under pressure, the
  worst condition for it. You get what sounds plausible in the moment.
  That is precisely how four already-closed families (VWAP distance,
  volume-vs-expected, VXN level, ZN lead) were queued for Scan 005 as
  "genuinely new" on 2026-09-09.

  INTEGRITY GATE: the hazard in "never stop" is manufactured work. The
  2-attempt limit and the no-resurrection rule exist because a system
  under pressure to produce will re-test its own graveyard. Vetting
  must happen at INSERTION, in slack, not at DRAW, under load.

  STATISTICAL: every scan raises the project-wide trial count and
  tightens the Sidak correction for every candidate still in flight.
  A process built to always have something to scan will scan more.
  HOLD must remain an available answer.

  MECHANISM: the strongest filter on a generated idea is whether it
  can carry a prediction BEFORE it is measured. An entry with no
  mechanism claim is a lottery ticket.

## The Idea Inventory

research/idea_inventory.md -- a ranked list of vetted, unscanned
research directions. Sessions TOP IT UP in slack and DRAW FROM IT
under load. It is the reason the queue should rarely reach empty, and
the reason reaching empty is no longer an improvisation.

ENTRY BAR. Four things, all four, or it does not go in:

  1. STATE VARIABLE -- what is actually measured, in terms that could
     be implemented without further interpretation.
  2. MECHANISM CLAIM -- one line, in market terms: who is on the other
     side of this trade and why do they keep taking it. Not a
     narrative, a claim that could fail.
  3. HORIZON -- and per the STANDING RESEARCH PRIORITY, short
     (intraday / overnight / 1-2 day) is preferred over 10-day drift,
     because holding period governs how fast a result resolves.
  4. INTEGRITY GATE RESURRECTION RULING -- new, or second attempt on a
     closed family. A second attempt engages the 2-attempt limit and
     is logged as such at insertion. The Director cannot overrule it.

An entry lacking any of the four is not "incomplete," it is not an
entry. It does not sit in the file waiting to be finished.

## Cadence -- who does what, and when

  TOP UP: at the close of every session, the Integrity Gate audit
  also counts the inventory. If it holds FEWER THAN 3 entries, the
  NEXT session's first queue item is the generation staff meeting
  (AMENDMENT v2.2 order: LEARN, then Discovery, then Integrity Gate,
  then Statistical, then Mechanism, then the Director's disposition).
  Deliberately the NEXT session and not this one -- generating at the
  end of a run that just exhausted itself is the pressure condition
  this amendment exists to avoid.

  DRAW: the moment the queue empties DURING a session -- whether at
  the start of the run or three hours in, it is the same event -- the
  session draws the top-ranked inventory entry and works it. No
  meeting is required, because the vetting already happened. This is
  the normal path and should be the common one.

  FALLBACK: queue empty AND inventory empty -- hold the generation
  meeting immediately, under pressure, accepting that this is the
  degraded case. Anything it produces still has to clear the full
  entry bar. The bar does not soften because the shelf is bare.

  TERMINAL: queue empty, inventory empty, and the generation meeting
  produced nothing that clears the bar. The session logs that plainly,
  names what it is waiting on, and ENDS. This is a real and expected
  state, not a failure and not idleness. A session that reaches it
  honestly has done better work than one that scanned something
  marginal to avoid saying so.

  OWNERSHIP: Discovery maintains the file. LEARN supplies the raw
  unexplored space and vets for resurrection. Integrity Gate issues
  the per-variable ruling. Statistical attaches the multiplicity cost.
  Mechanism validates the claim. The Director ranks and approves.

## The guard against manufactured work

This is the part Jason asked for directly. Manufactured work has
recognizable shapes; each gets a named guard.

  RESURRECTION -- re-testing a closed idea under a new descriptor
  name. Guard: LEARN checks by name AND by what is measured, and the
  Integrity Gate rules per variable at insertion.

  COSMETIC NOVELTY -- the same idea at a different bucket boundary,
  a different horizon, a different parameterization. Guard: an entry
  must differ from closed work in its MECHANISM CLAIM, not in its
  parameters. Re-cutting a dead idea is the dead idea. This is the
  most common disguise and the easiest to miss.

  SLICING -- finer and finer cells on the same data until something
  clears. Guard: Statistical attaches the multiplicity cost to every
  entry, and more cells is a cost, never a strategy.

  LOTTERY TICKETS -- testing a variable because the data is on hand,
  with no claim about why it would work. Guard: the mechanism claim
  is an entry requirement, not a nice-to-have.

  BUSY-WORK -- re-documenting, re-deriving, or re-summarizing what is
  already settled, so that a session has something to show. Guard:
  every session report states WHAT NEW INFORMATION THIS RUN PRODUCED.
  Re-documenting existing findings is not new information, and a run
  whose only output is prose about prior results must say so.

  THE STANDING TEST, applied to any proposed entry:

      Would we have proposed this before seeing any data?
      And if it comes back null, will we have learned something?

  If the answer to either is no, it is not research, it is activity.
  Do not add it.

## What does not change

Sessions still work the queue until it is dry (v2.2). Session reports
still have no length cap. Every agent still runs when its input
condition exists. The Integrity Gate audit still closes every session.
RETURNs, the SCOPE BOUNDARY, the MECHANISM GATE and the never-bent
rules (review points, Holdout slots, $5+ spend, live capital) are
untouched.

## Status

The inventory starts EMPTY. The first session to read this therefore
hits the FALLBACK case and holds the generation meeting to seed it.
LEARN's 2026-09-10 finding is the starting material: the two axes it
identified as genuinely untried are short-horizon re-expression of the
five older descriptors never tested below a daily close-to-close
horizon (range_vs_atr, overnight_range_vs_atr, opening_range_vs_atr,
location_in_range, directional_persistence), and cross-instrument
DIVERGENCE / relative-value state (NQ-ZN, NQ-VXN co-movement breaking
down) as a mechanism claim distinct from "instrument X's own level
predicts NQ." Both still have to clear the entry bar per variable.

---

# AMENDMENT v2.4 -- the Operations Manager

Frozen 2026-09-10. Jason's proposal, in his words: a role with "a larger
scope on all the agents and the whole production as a whole," that makes
him "feel like this is up to date, the reports are being up to date, the
sessions are running smoothly, and if there's anything that needs to be
brought up to me it's brought up to me." Explicitly NOT a research role:
"it doesn't have the technological knowledge, that's you."

## Why the role exists

Every agent in this structure examines ONE candidate or ONE question.
Nothing examines the MACHINE. The evidence, all from 2026-09-09/10, all
caught by Jason asking rather than by the system noticing:

  - the console silently stopped refreshing for over an hour
  - a session died mid-run and left the lock reading RUNNING for hours,
    so the whole system reported itself busy while nothing was happening
  - ten stale ledger statuses accumulated over weeks, then two more
    within hours of the first sweep
  - one of the two daily reports failed to send
  - a question parked on Jason sat overnight with no clock on it
  - the governance doc described a stale H118 status for a full day
    after the Integrity Gate had superseded it

None of these are research failures. Every one of them is an operations
failure, and the structure had nobody whose job it was to notice.

## Scope -- absolute, and it holds against Jason himself

The Operations Manager owns the HEALTH OF THE SYSTEM. It has no
authority, no opinion, and no voice on the CONTENT of the research.

It MAY: verify that sessions ran and completed; that reports exist and
are well-formed; that the console refreshed; that the ledger is
internally consistent; that the Mechanism Gate is holding; that
scheduled reports fired; that items parked on Jason have a clock on
them; that runs are producing new information. It may escalate any of
these to Jason directly. It may request a staff meeting.

It MAY NOT, ever: judge whether a result is real; assess a statistical
finding; rule on resurrection; decide what to research next; grade a
candidate; overrule the Integrity Gate or the Research Director on
anything; touch a promoted candidate; or express a view on a research
question.

THE DEFLECTION RULE. This is binding and has no exception. If the
Operations Manager is asked a research question -- BY ANYONE, INCLUDING
JASON DIRECTLY -- it does not answer it. Not partially, not with a
caveat, not "speaking loosely," not "my understanding is." It states
that the question is outside its scope and names the agent that owns
it: statistical validity to STATISTICAL, whether a result can be
trusted to the INTEGRITY GATE, what to research next to the RESEARCH
DIRECTOR, whether an idea is genuinely new to LEARN, why an effect
might exist to MECHANISM, whether there is a way to make money from it
to MONETIZATION.

Jason asked for this explicitly, and the reason is worth stating
plainly: a role that answers research questions without the
qualifications to answer them becomes a shortcut around the entire
review chain. The chain only has value if there is no way around it.
An operations answer that sounds authoritative is more dangerous than
no answer, because it will be believed. The deflection is not
bureaucratic politeness -- it is the control.

## Where it sits

PEER to the Research Director, not subordinate to it. The Director owns
"are we researching the right thing." Operations owns "is this actually
functioning." Both answer to Jason. Operations is Jason's
representative in the room when he is not in it.

Disagreement between them is a staff meeting trigger (v2.1 Rule 3b).
The characteristic case: the Director wants to continue, Operations
reports that the last three runs produced no new information. Both are
legitimate positions and the meeting resolves them. Operations does not
win that argument by default and cannot force a research decision -- it
can only insist the question be ASKED.

The Integrity Gate keeps its veto. Operations has none.

## How it runs -- checks in code, judgment on top

The mechanical half is src/ops_checks.py, covered by
tests/test_ops_checks.py. It returns PASS / WARN / FAIL per check:

    lock             a lock held with no logged activity for 30 min is
                     a session that died, not a session working
    console          state older than 45 min means the refresh step is
                     failing and Jason is reading stale numbers
    reports          every run owes a report, and it owes a shape
    new-information  3 consecutive runs producing nothing is a
                     methodology signal, not a run of bad luck
    ledger           an idea closed by its own later test whose earlier
                     row still reads PROMISING -- the recurring defect
    mechanism-gate   anything past Discovery without a mechanism doc
    awaiting-jason   what is parked on him, and for how long

Putting these in code rather than in an agent's reasoning is
deliberate. It keeps the role cheap, it makes it impossible to fake a
green result, and it stops Operations becoming exactly the thing this
project spent 2026-09-10 designing against: an agent that files a
reassuring report every four hours. The agent's only judgment is what
is worth escalating.

A failing check never halts research. If a check errors, it degrades to
WARN and the run continues -- Operations must not be able to stop the
work by breaking itself.

## Reporting

Runs at session close, alongside the Integrity Gate audit. Its output
is a single OPERATIONS STATUS line plus any non-PASS checks, appended
to the session report. Silence is the normal case.

It notifies Jason only on FAIL, or on a WARN that has persisted across
three consecutive sessions -- a warning nobody clears is a failure with
better manners. This is in addition to the four standing stop points
(Holdout slot, $5+ spend, integrity problem on a promoted candidate,
hard blocker), which are unchanged and remain everyone's obligation.

## Status

Live. src/ops_checks.py and tests/test_ops_checks.py are on disk; the
suite is 219 green. First run found a real FAIL -- two Discovery rows
still reading PROMISING after their own Validation tests rejected them
that morning -- which is the defect class this role exists to catch,
caught within a minute of the role existing.

---

# AMENDMENT v2.5 -- the Upgrade Brief: market map, pipeline restructure, blind Gate, data policy, reporting

Frozen September 11th, 2026, at the adoption staff meeting Jason called
after an outside trading-lens review of the Full Scope doc
(docs/FULL_SCOPE.md). Source: docs/TONY_UPGRADE_BRIEF.md, Jason's
direction decisions in its Section 1 are binding. Reviewer's verdict,
adopted: the research discipline is sound and stays; the project was
over-governed and under-informed -- every safeguard was a filter, none
was a lens. Nothing here weakens a freeze, a review point, or the
evidence bar.

## Rule 1 -- KNOWN STRUCTURE (LEARN bucket 5) and the map anchor

research/market_structure_map.md is a standing document owned by LEARN.
Every scan scope must name the map entry it probes. The Idea Inventory
entry bar gains a FIFTH requirement: a map anchor. An entry with no
anchor is not an entry. Entries that cannot be anchored are SHELVED
(no attempt spent), not closed. A map entry is never closed -- structure
persists; its attempts close.

## Rule 2 -- the pipeline, restructured (replaces the v2 order)

    Jason (direction)
      -> RESEARCH DIRECTOR   scope, freeze, allocation. Absorbs Candidate Triage
                             (A-F issued at scan close) and Re-Evaluation (the one
                             "worth more capital?" call, made once, at the Validation gate).
      -> MECHANISM           written WITH the scope, BEFORE the scan: claim + at least
                             2 predictions + a falsifier. Post-scan it may only ADD
                             predictions; it may not rewrite the claim.
      -> DISCOVERY           scans the frozen scope; reports cells, novelty, exposure.
      -> STATISTICAL         stability, regime, magnitude, selection, multiplicity --
                             AND statistical power at the proposed review point (new,
                             mandatory, see src/h118_power_check.py for the method).
                             Owns the cost model.
      -> INTEGRITY GATE      BLIND checkpoint (Rule 3) before Validation.
      -> VALIDATION          one pre-registered shot.
      -> MONETIZATION        now here: realization path, execution spec, measured cost
                             assumption. "No credible path" is still a valid close.
      -> INTEGRITY GATE      blind checkpoint before Holdout.
      -> HOLDOUT             Jason's slot.
      -> PORTFOLIO           unchanged.

Ten roles for one AI was overhead; the value is in the forcing
questions, not the seats. Triage and Re-Evaluation were the same
judgment twice; Monetization before any out-of-sample result was
premature. Applicability (v2.1 Rule 1), RETURN, staff-meeting triggers,
LEARN-by-name, the Operations Manager and its deflection rule are all
UNCHANGED. The Ops `mechanism-gate` check now fires on any DRAWN scope
without a mechanism doc (earlier, stricter, cheaper), not only on
candidates past Discovery.

Consequence for src/pipeline_sweep.py "next owed" chains: the OPEN chain
is Mechanism doc -> (scan) -> Statistical (with power) -> Integrity Gate
(blind) -> frozen Validation spec -> one-shot Validation -> Monetization ->
Integrity Gate (blind) -> GATED. A candidate already past the old
Director Re-Evaluation + Monetization stages (hyp-000105) keeps that
work; nothing is re-run.

## Rule 3 -- the BLIND Integrity Gate

The two checkpoints run in a fresh context that receives ONLY the packet
built by src/integrity_blind_packet.py: frozen spec, scan/test code,
mechanism doc, and the family's ledger history, with every result figure
masked. It rules on whether the PROCEDURE could fool us. Only after it
rules are the numbers unmasked and the ruling logged alongside them. In
a scheduled cycle this means: build the packet, hand it to a subagent
with no prior context, record its ruling verbatim, then unmask.
Continuous-role duties stay in-session.

## Rule 4 -- data policy (UPGRADE 2)

$20/month cap. Databento yearly-chunk pulls fit; order flow does not and
is deferred until profits fund it (half of net profit reinvested in
data once profitable). Stated plainly: the short-horizon ceiling is set
by data, not ideas -- sub-15-minute microstructure edges are out of reach
for now, and the map is built around what 1-minute bars can see. Free
data to add at $0: economic-release calendar (BLS, Fed), Nasdaq-100
rebalance dates, exchange holiday / early-close schedule (queued; each
is a Discovery/LEARN filing task, none needs a spend). Jason still runs
Databento pulls manually; Ops `data-currency` flags when the live-forward
window is more than 5 sessions stale.

## Rule 5 -- reporting to Jason (UPGRADE 9), fixed shape

- DAILY, 2 lines, Central time: research -- what moved, what's queued;
  execution -- open positions, day P&L, budget remaining, any kill state.
  Carried by the console state document and the cycle's closing summary.
- IMMEDIATE: any capital-protection trigger; any $5+ spend request; any
  integrity flag on promoted work; any awaiting-Jason item older than 48 h.
- WEEKLY: map coverage (which entries scanned, which open), power /
  multiplicity status, and ONE candid sentence from the Director on
  whether the methodology is still finding things.
Involvement scales down (daily -> weekly) once Live-Limited has run 30
days without a trigger.

## Priorities under this amendment

The fast lane is the whole game: the market map and short-horizon scans
are where the first live dollar comes from. H118 is a slow-lane bet
whose locked review point has ~30% power at 40 trades if the true effect
is 0.40R (research/studies/h118-power-check-2026-09-11.md) -- the review
point does not move; Jason now knows what to expect from it.

## Status

Frozen. Code on disk: src/h118_power_check.py, src/capital_protection.py,
src/integrity_blind_packet.py, ops_checks data-currency + widened
mechanism-gate, pipeline_sweep map-ranked draw order; tests for each.
Adoption meeting record: research/sessions/2026-09-11-2348.md.
