# Market Behavior Discovery Engine / Market State Map — Design Spec

Frozen 2026-09-09. Sourced from Jason's structural review of the project after
OBS-FINDING-012 (pre-NFP drift) and the exit-design-mismatch LEARN entry. This
is a MODIFY to the existing methodology (research/studies/two-layer-methodology.md),
not a replacement. The integrity framework — chronological Discovery/Validation/
Holdout splits, frozen specs before implementation, the promotion bar, the
2-attempt limit, the LEARN layer — is unchanged and still governs everything
that comes out of this engine.

## The problem this solves

The existing pipeline is well-built for REJECTING bad hypotheses but was not
designed to efficiently DISCOVER which behaviors are worth testing in the first
place. It assumed we already knew which events/behaviors mattered (macro
announcements, calendar effects, candlestick patterns, closing-pressure
reversal, etc.) and tested them one at a time. 116 rejected hypotheses mean the
particular questions asked so far haven't found a monetizable edge — they do
not mean NQ has no directional/timing/state-dependent structure at all.

## What changes vs. what stays

KEEP, unchanged: the constitution (market-behavior-first philosophy, Discovery/
Validation/Holdout chronological splits, frozen specs before code, the
research ledger, the LEARN layer, the promotion bar of 90% CI entirely above
zero AND >=0.05R AND one pre-registered prospective confirmation, the
2-attempt limit, no retuning after a null).

MODIFY: how candidates enter the pipeline. Instead of hand-picking an event or
pattern and testing whether it predicts an outcome (strategy-first), a new
layer systematically maps the market's conditional behavior across many
observable states, and candidates are drawn from that map (state-first).

## Flow

RAW MARKET (price, volume, volatility, time, session structure, gaps, ranges,
order/price-location proxies derivable from OHLCV, cross-market relationships,
calendar/event context)
  -> MARKET STATE ("what was the market doing immediately before time T?")
  -> TRANSITION ("what did it do afterward?")
  -> CONDITIONAL BEHAVIOR ("when state X occurs, does outcome Y differ from
     baseline, and by how much?")
  -> TRADEABILITY ("can we plausibly capture that difference, and by what kind
     of exposure?")
  -> VALIDATION ("does it survive the existing Discovery -> Validation ->
     Holdout machinery, unmodified?")

This reframes the old question ("which candle pattern predicts a profitable
trade") into: given the observable state of the market at time T, what is the
conditional distribution of what happens next?

## State descriptors (Layer 0 primitives — all derivable from existing OHLCV,
no new data required)

Per bar/session, candidate state variables include: range relative to recent
volatility (ATR-normalized), body/range ratio, upper/lower wick excursion,
location within the preceding N-bar range, distance from VWAP/session
open/high/low, volume relative to expected/trailing volume, time of day,
overnight range, opening-range size, preceding directional persistence
(run length/sign), volatility regime (trailing realized vol percentile), gap
state (size and direction of the open gap), compression/expansion state
(range contracting or expanding vs. trailing average — reuses the 3 validated
findings' own convention), relationship to the previous session's range/close,
relationship to other markets we already hold data for (ES, VXN, etc. where
available).

This list is a starting menu, not a fixed spec — new descriptors get added as
Layer 0 primitives are vetted for correctness, exactly like any other data
source in this project.

## What gets measured per state (the whole distribution, not just the mean)

For each state definition and each forward horizon, measure: forward return
(does price drift?), probability positive (how consistent is the direction?),
forward volatility (how violently does it move?), MAE (does it move against
the "natural" direction first?), MFE (does it eventually move favorably?),
behavior across multiple horizons (how long does the effect persist?),
baseline comparison (is this state's behavior unusual vs. the unconditional
baseline?), conditional-on-regime analysis (does it depend on volatility
regime, day-of-week, session?), cost-adjusted effect size (ATR-normalized,
same convention as the existing cost-dominance screen), and time/regime
stability (is the effect stable across the Discovery window, or concentrated
in a sub-period?).

## Multiple-testing control (critical — this is what keeps Discovery from
turning into p-hacking at scale)

Many state variables x many conditioning splits x many horizons x many
regimes creates a large search space and therefore many chances to find a
spuriously significant result. This engine's output is explicitly NOT a
confirmatory result and NEVER promotes anything directly:

1. Discovery pass over the state map is exploratory and uncorrected — its job
   is to surface candidates, not to confirm them. Every output from this
   stage is provisional by definition, same status as any other Observatory
   scan today.
2. Candidates get RANKED before anything is frozen, using four criteria:
   unusual (large deviation from unconditional baseline), robust (survives a
   simple split-sample or regime check within Discovery itself), economically
   meaningful (clears the ATR-normalized cost floor), and mechanistically
   plausible (a Mechanism Agent pass — see below — can articulate a
   non-arbitrary reason the state would matter, not just "this cell in the
   grid happened to look good").
3. Only ranked, qualified candidates get a frozen spec written and go through
   the UNCHANGED existing confirmation machinery: pre-registered direction,
   Discovery -> Validation -> Holdout, one pre-registered prospective test,
   2-attempt limit, ledger logging regardless of outcome.

This is additive to, not a loosening of, the existing statistical standards —
Discovery was already never allowed to confirm anything; this makes the
scale and the ranking gate explicit before anything reaches frozen-spec
status.

## Natural realization path (new required question before any monetization spec)

Before writing a monetization frozen spec for a qualified candidate behavior,
the spec must state which kind of exposure naturally fits the observed
behavior, chosen from: directional position, time-based exit, trailing exit,
volatility-conditioned exposure, mean-reversion exposure, momentum exposure,
intraday-session exposure, or portfolio/context signal (used as a filter on
another hypothesis rather than a standalone trade). This question is asked
BEFORE the stop/target structure is designed, and the chosen exposure type is
frozen along with everything else in the spec — no post-hoc optimization of
exit structure once results come back.

This directly operationalizes the "exit-design mismatch" LEARN failure mode
(research/studies/two-layer-methodology.md, 6th taxonomy entry): a real,
credible average-price-drift effect (OBS-FINDING-012) failed twice to become
a profitable trade under a binary stop/target structure. The unanswered
question was never asked: does a binary stop/target actually fit how this
particular behavior realizes itself? This section makes asking that question
mandatory going forward.

## Candidate agent roles (refines research/infrastructure/mechanism-research-agent-design.md)

- Discovery Agent: maps unexplored market-state/outcome relationships across
  the state menu above; produces ranked, provisional candidates only.
- Mechanism Agent: for each candidate, assesses whether a plausible
  liquidity/participation/flow/behavioral reason exists for the relationship
  to hold, versus it being an arbitrary grid cell that happened to look good.
- Statistical Agent: assesses robustness (split-sample stability, regime
  sensitivity, effect-size confidence) before a candidate is allowed to reach
  frozen-spec status.
- Monetization Agent: determines the natural realization path (see above) and
  drafts the frozen monetization spec accordingly.
- Research Integrity Agent: guards against contamination, p-hacking, selection
  bias, and hypothesis resurrection (enforces the 2-attempt limit and the
  no-retuning-after-null rule across all of the above).
- Portfolio Agent (future, not built yet): once multiple individually-weak
  behaviors exist, assesses whether they combine into something more useful
  together — out of scope until more candidates exist.

Candidate-vetting/ranking work (Discovery, Mechanism agents) is parallelizable
exactly as before. Frozen-spec EXECUTION against the repo/ledger (Statistical,
Monetization, Research Integrity agents acting on a specific frozen spec)
stays strictly serial — ledger integrity and the no-retuning-after-null rule
depend on this, unchanged from the existing design note.

## Three progress metrics (replaces the old implicit "hypotheses tested ->
validated" framing as the primary progress signal)

1. Research coverage — how much of the market's behavior/state space has
   actually been systematically explored (tracked qualitatively for now: which
   state variables, horizons, and conditioning splits have been scanned).
2. Discovery yield — how often a research avenue (a state variable or family)
   produces a statistically credible behavior, per the ranking criteria above.
3. Monetization yield — how often a credible behavior becomes a validated,
   tradeable edge (this is what the ledger's REJECTED/PROMISING/VALIDATION
   CANDIDATE/etc. counts already measure).

The project has substantial data on #3 (94 rejected, 17 promising, etc. out of
116) but very little on #1 — that is the actual gap this engine closes.

## Status

Frozen spec only. No code has been written against this yet. Per the standing
structure rule, the next concrete action (once the repo is reachable) is to
scaffold research/infrastructure/market_state_primitives.py (Layer 0) — the
same ATR-normalized, cost-aware conventions already used in
volatility_conditioning.py — starting with the state descriptors that reuse
data already validated in this project (range/volatility-based descriptors),
before expanding to the untested ones (location-in-range, VWAP distance,
cross-market relationships).
