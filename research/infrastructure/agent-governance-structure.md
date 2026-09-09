# Agent Governance Structure -- Research Director, Candidate Triage, and agent role charter

Frozen 2026-09-09. Supersedes the six-agent list in
research/infrastructure/mechanism-research-agent-design.md and the
"Candidate agent roles" section of
research/infrastructure/market-behavior-discovery-engine-design.md --
those documents described WHAT each agent checks; this document adds
WHO decides whether a candidate is worth pursuing at all, and freezes
the reporting format every agent uses. Source: Jason's structural
review, 2026-09-09, second pass (after the initial Discovery Engine
design spec and Scan 001's split-sample results).

## What changed and why

The prior six-agent pipeline (Discovery -> Mechanism -> Statistical ->
Monetization -> Validation, with Research Integrity across everything)
is a strong execution pipeline but has no agent whose job is deciding
whether the pipeline is investigating the right things. It will
happily keep running mechanism/statistical/monetization passes on
whatever Discovery surfaces, without ever asking "is this the
highest-value use of the next research cycle?" Scan 001 made the gap
concrete: 16 of 48 cells passed an individual threshold, and without a
triage step every one of them could have consumed a full
Mechanism+Statistical pass before anyone asked whether they were
mostly the same handful of correlated series.

Two additions close that gap. Everything else about the existing
integrity framework, ledger, promotion bar, and 2-attempt limit is
unchanged.

## Pipeline (updated)

    Jason
      |
      v
    RESEARCH DIRECTOR  (strategic authority -- not an execution step)
      |
      v
    DISCOVERY AGENT  (maps candidate behaviors, reports novelty + search exposure)
      |
      v
    CANDIDATE TRIAGE  (a function the Research Director performs, not a 7th agent)
      |
      v
    MECHANISM AGENT  (testable mechanism predictions, not post-hoc stories)
      |
      v
    STATISTICAL AGENT  (stability, regime dependence, magnitude, selection sensitivity)
      |
      v
    MONETIZATION AGENT  (natural realization path; "no credible path" is a valid conclusion)
      |
      v
    DISCOVERY -> VALIDATION -> PROMOTION  (existing pipeline, unchanged)

Wrapping the whole thing, independently of each other and of the
Research Director:

    RESEARCH INTEGRITY  -- are we doing this honestly? (freeze rules, contamination,
                            multiple-testing tracking, 2-attempt limit, no resurrection)
    LEARN                -- what do we already know? (known-true, known-failed,
                            known-failure-modes, known-unexplored)

Research Integrity and the Research Director have different jobs and
neither can override the other's domain: the Director can want a
candidate pursued; Integrity can still veto the proposed test as
contaminated. That separation is deliberate.

## Research Director

Not a pipeline step -- the strategic authority over the pipeline. Its
question is always: "Is this the highest-value research we could be
doing right now?" It reviews what's already been tested, what failed,
what succeeded, what's genuinely unexplored, what Discovery is
finding, whether candidates are novel or rediscoveries, how much
multiple-testing exposure has accumulated, what data is available or
would materially expand the research space, and whether the current
research family shows diminishing returns.

Authority: CONTINUE / MODIFY / PIVOT / ABANDON on any research thread
or family, at any point -- including after Discovery has already
surfaced candidates and before Mechanism spends time on them. This
operationalizes the existing methodology principle that the project
should change methodology when methodology itself stops producing
useful discoveries, rather than endlessly generating strategies.

Also performs Candidate Triage: classifies every Discovery-Agent
candidate before Mechanism sees it --
  A. Novel and potentially important -- worth investigating
  B. Probably known/duplicative -- compare against existing findings
     before spending research resources
  C. Statistical artifact / multiple-testing concern -- do not advance yet
  D. Economically too small -- close
  E. Interesting behavior, unclear monetization -- keep as behavioral
     knowledge (LEARN), don't force a strategy
  F. Redundant with an existing hypothesis -- don't retest merely
     because the formulation looks different

Example: Scan 001's overnight_range_vs_atr/mid/10d survivor is a B/C
borderline case (same predictor as the validated overnight-coil range
finding, still-unresolved regime-contamination question) -- exactly
the kind of candidate this layer exists to catch before a full
Mechanism+Statistical pass is spent on it.

## Discovery Agent (refined objective)

Objective changes from "maximize statistically interesting results" to
"discover candidate market behaviors." Every candidate it reports
carries, at minimum:
  - state definition and observed behavior
  - effect size and sample size
  - search exposure (how many states x horizons x conditions were
    scanned to produce this candidate -- Scan 001's 48-cell grid /
    ~12-effectively-independent-series figure is the model)
  - known-relationship overlap (does this reuse a predictor already
    behind a validated finding?)
  - novelty: Low / Medium / High
  - economic magnitude (ATR-normalized, existing convention)
  - status: always EXPLORATORY CANDIDATE, never "finding"

"Statistically significant" is reported with its search-exposure
context attached, not as a bare number -- 10 tests and 10,000 tests
producing the same p-value are not the same evidence.

## Mechanism Agent (refined standard)

Not asked "can you think of a reason this might work" (too easy --
plausible post-hoc stories are cheap). Asked instead: "what observable
market mechanism could have generated this relationship, and what
evidence would distinguish that mechanism from coincidence?" Output is
a testable mechanism PREDICTION (if mechanism X is real, we should
observe Y/Z under independently measurable conditions; absence of Y/Z
lowers confidence in X) -- not a narrative.

## Statistical Agent (refined standard)

Four required questions, not just first-half-vs-second-half agreement:
  1. Stability -- does the behavior persist across time?
  2. Regime dependence -- does it only exist in one market environment?
  3. Magnitude -- is the effect economically meaningful?
  4. Selection sensitivity -- does the result survive reasonable
     changes to the measurement definition without becoming parameter
     optimization?
Plus a mandatory disclosure: was this candidate selected because it
looked good in the same data now being used to evaluate it? If yes,
the analysis is explicitly labeled EXPLORATORY, never confirmatory --
this is already how the Scan 001 split-sample screen was run and
reported (see research/infrastructure/market-behavior-discovery-engine-design.md
and docs/BACKLOG.md's 2026-09-09 entries).

## Monetization Agent (unchanged in spirit, reaffirmed)

Stays last in the pipeline, deliberately. Determines the natural
realization path (already specified in the Discovery Engine design
spec) and is explicitly permitted to conclude "interesting behavior,
no credible monetization mechanism identified" -- that is a successful
research outcome, not a failure to force a strategy. Directly
reaffirms the exit-design-mismatch LEARN entry from OBS-FINDING-012 /
H114/H115.

## Portfolio Agent (unchanged: dormant)

Not built. Becomes relevant only once multiple validated-but-
individually-weak behaviors exist to potentially combine. Zero
validated directional strategies exist today -- building this now is
infrastructure ahead of need. Specification stays on file
(research/infrastructure/market-behavior-discovery-engine-design.md),
no research effort spent implementing it.

## Research Integrity (unchanged role, reaffirmed as independent)

Freeze rules, contamination prevention, multiple-testing tracking, the
2-attempt limit, no hypothesis resurrection. Operates across every
stage above, independently of the Research Director -- see governance
note above.

## LEARN (strengthened into explicit institutional-memory structure)

Maintains, and the Research Director consults before triaging or
prioritizing:
  KNOWN TRUE: range contraction -> future range contraction (hyp-046/048);
    overnight coil -> same-day range contraction (hyp-056/057); midday
    contraction -> afternoon contraction (OBS-FINDING-011, hyp-105/106)
  KNOWN FAILED: gap fade; overnight directional fade (H93); pre-NFP
    trade implementations (H114/H115); Turn-of-the-Month; closing-
    pressure reversal; pre-FOMC drift
  KNOWN FAILURE MODES (6, from two-layer-methodology.md): cost-
    dominance; thin-sample overconfidence; correlated-lens double-
    counting; direction-ambiguity in pooled measurements; marginal-
    Discovery-passes-don't-replicate; exit-design mismatch
  KNOWN UNEXPLORED: cross-market relationships (ES/VXN), VWAP distance,
    volume-vs-expected, directional_persistence (needs a non-tercile
    discretization -- degenerate in Scan 001), regime-conditioned
    versions of the Scan 001 survivors

## Reporting format (standard across every agent from here forward)

Every agent report ends with the same five fields, replacing free-form
narrative:
  Finding -- what did we actually learn?
  Confidence -- how strong is the evidence?
  Novelty -- genuinely new, or rediscovery?
  Research Value -- does this materially increase understanding or the
    probability of finding an edge?
  Recommendation -- CONTINUE / MODIFY / PIVOT / ABANDON

## Reframed central research question

From: "What important and repeatable behaviors does intraday NQ
exhibit?"

To: "What conditional market states contain information about future
price behavior that is sufficiently persistent, economically
meaningful, and independently verifiable to potentially support an
executable trading edge?"

Three filters this adds over the old framing: information (is there
actually information about the future?), persistence (does it keep
existing?), economic usefulness (can it actually be captured?). Keeps
the project anchored to "profitable trading system," not "NQ behavior
encyclopedia."

## Status

Frozen governance spec. No code changes required by this document
itself -- it changes decision authority and reporting format, not the
Layer 0/1 scan mechanics already built (market_state_primitives.py,
market_behavior_discovery_scan.py, discovery_scan_001_split_sample_robustness.py).
Next application: the Research Director role formally reviews Scan
001's 3 split-sample survivors (Candidate Triage classification A-F)
before any further Mechanism-Agent-style regime-contamination work
continues on them.
