---
title: "Tony — The Full Scope"
subtitle: "An automated NQ futures trading bot, built by a research operation: what it's for, how it's structured, how it finds and tests ideas, how the agents run it, and how it gets to a live order"
author: "Jason Alanis"
date: "September 13, 2026"
---

# Why this document exists

This is the complete scope of a project I call Tony, in one place, written so someone outside it can critique it. It combines the vision, the operating rules, the research methodology, the agent structure, the learning system, and — new in this version — the product roadmap. Nothing here is aspirational shorthand; every rule described is one the system actually runs under today.

I am not a statistician or a programmer. I direct this project; an AI agent team builds and runs it. What I want from a reader is candor: where is this structure fooling itself, where is it over-engineered, where is it missing something a professional would consider obvious, and does the whole thing actually point at the goal.

This version is dated September 13, 2026 and supersedes the September 12 version. On September 13 I gathered six independent outside reviews of the September 12 scope, held the checkpoint that had been scheduled for the 19th, lifted the change freeze, and made one correction that reorders everything else: **the goal is a trading bot, not the best research tool.** Section 3 says what changed; Section 4 shows how every piece connects; Section 7 is the roadmap that now outranks the research queue.

# 1. The vision

I'm trying to build an automated system that actually makes money trading NQ futures. Not a good backtest — a real system, running itself, that I can trust with capital.

The honest alternative outcome is finding out cheaply that no such edge is available from what we can test. Both of those outcomes are acceptable. Expensive self-deception is not.

The correction made on September 13 is about ordering, not ambition. For months the project's whole pipeline was gated on finding a directional edge first — and 160 attempts say that edge may not arrive. If the bot only gets built after the edge lands, the bot never gets built, and the project quietly becomes a rigorous instrument for producing null results. So the bot now comes first: **a trading bot does not need an edge to exist.** It needs signal → size → order → fill → monitor → kill. Tony has validated material for *size* and nothing yet for *signal*; the first bot runs an ordinary, publicly-known placeholder entry that is never claimed as an edge, and the research operation's job becomes replacing that placeholder and sharpening the sizing. Research is the feeder. The bot is the trunk.

The top priority is still the holistic lens: are we looking at this the right way to reach the goal? Learning, research, discovery, testing, and calculated adjustment are the method, not the objective.

# 2. The central belief — everything follows from this

The default outcome in this field is fooling yourself. Markets are mostly noise. Search hard enough and something will always look like an edge. Every rule in this document blocks one specific way of being fooled. When a rule feels inconvenient, that is usually the moment it is doing its job.

Three consequences govern everything:

**A dead candidate is a success, not a failure.** Finding out cheaply that something doesn't work IS the product. Nothing here has ever cleared a correctly-specified promotion bar. That is a real result, not a sign anything is broken. A dead candidate is never softened, reframed, or resurrected to keep it alive.

**Looking and finding out are different activities.** Discovery data is where you are allowed to search. Validation and Holdout are where you find out. The moment those blur, the project learns nothing. September 13 added the corollary: *looking* is allowed to be cheap and broad, precisely because *finding out* is expensive and narrow.

**Freeze before you test.** Definition, direction, thresholds, windows, exit rule — all fixed in writing before any result is seen. A change made after seeing a result is not an improvement; it is a new hypothesis.

# 3. The honest current state

159 hypothesis records across 117 idea families have been logged; 33 pre-registered scans have been run; 451 Discovery-stage trials are counted against every future result. **Zero have ever cleared a correctly-specified promotion bar for a directional edge.** No strategy has ever been executed, even on paper with real orders.

What survives is real, and September 13 stopped calling it a consolation prize:

- **Four volatility facts**, each confirmed out-of-sample, two at Holdout: range contraction persists; a coiled overnight session predicts a compressed day; a quiet midday predicts a quieter afternoon (ratio ~0.74, Holdout passed); and an elevated VXN — the options market's expectation of movement — relative to its own norm predicts a wider next session (ratio 1.24 at Holdout, which *strengthened* out of sample, unusual here). None is directional. All are state variables. Three of five Holdout slots are spent.
- **Three Discovery-stage volatility bursts around scheduled events** — EIA report (crude), ECB decision (euro), London FX open (euro). Previously filed as "real but nowhere to put it"; on September 13 reclassified as one family, because micro contracts exist for both instruments and the family is the same question three times.
- **One tracker**: a weekly momentum idea rejected at Discovery and followed forward as a calibration check. H118, the candidate that once cleared all three stages, remains **rejected** (baseline confusion) with its forward log kept for information only.

Two things the six reviews said in unison: the validation machinery is the asset, and the idea-generation front end was the bottleneck. Two of them said *why*: the sourcing bar required a citation and a written mechanism before anyone was allowed to look at data, which selects for ideas already in print and already traded away. Four literature-sourced ideas failed in one day; that was the filter working as designed, against us. The September 13 changes in Section 6 are the response.

What the checkpoint concluded (held September 13, `research/weekly/2026-09-13.md`): **continue**, and move the target from "find direction" to "build on structure." The volatility facts become a risk engine; the Observatory is allowed to look before anyone theorizes; execution gets measured now with a placeholder signal; the data ceiling stays, with a written trigger for when a purchase would earn it.

# 4. How it all fits together — one loop

Everything in this document is one closed loop. Read it once end to end before the sections that follow, because each section describes one station on this loop and none of them makes sense alone.

    ┌───────────────────────────────────────────────────────────────────────┐
    │  LOOK (Observatory · Idea Factory)                                     │
    │  every on-disk market state × every session window × the outcome       │
    │  battery, Discovery slice only, descriptive, timing rule enforced.     │
    │  Output: a RANKED CANDIDATE QUEUE. Costs nothing. Proves nothing.      │
    └──────────────────────────────┬────────────────────────────────────────┘
                                   │ Sourcing Rule v3: take the top family with no mechanism
                                   ▼
    ┌───────────────────────────────────────────────────────────────────────┐
    │  EXPLAIN (LEARN → Mechanism → Director)                                │
    │  LEARN: has this been closed before? Mechanism: who is forced to       │
    │  trade, and what would prove it wrong — written BEFORE any test.       │
    │  Director: is it worth a slot? Grade A–F. Freeze the scope.            │
    └──────────────────────────────┬────────────────────────────────────────┘
                                   │ one registered scan, every cell counted forever
                                   ▼
    ┌───────────────────────────────────────────────────────────────────────┐
    │  TEST (Discovery → Statistical → blind Gate → Validation → Gate →      │
    │        Holdout [Jason])                                                │
    │  Mechanical integrity suite runs before the Gate. One shot per stage.  │
    │  Most candidates die here. Every death produces a CLOSURE FORM.        │
    └───────┬──────────────────────────────────────────┬────────────────────┘
            │ died                                      │ survived
            ▼                                           ▼
    ┌──────────────────────┐             ┌────────────────────────────────────┐
    │  NEGATIVE KNOWLEDGE  │             │  FACT REGISTRY                      │
    │  what not to retest, │             │  a validated market fact: what,     │
    │  under what single   │             │  where, how strong, what it is      │
    │  condition it may    │             │  good for (size, stop, permission,  │
    │  come back           │             │  or — never yet — direction)        │
    └──────────┬───────────┘             └──────────────────┬─────────────────┘
               │ feeds LEARN                                │ feeds the engine
               ▼                                            ▼
    ┌───────────────────────────────────────────────────────────────────────┐
    │  THE BOT (Section 6)                                                   │
    │  signal (B3 placeholder, or a real edge if research ever supplies one) │
    │  → size / stop / target / permission (B2 Risk/State Engine, built from │
    │    the fact registry)                                                  │
    │  → order (B4) → fill measured (B5) → kill switches (B6)                │
    │  → paper run (B7) → Live-Limited, Jason only (B8) → scale (B9)         │
    └──────────────────────────────┬────────────────────────────────────────┘
                                   │ execution data: fills, slippage, latency,
                                   │ MFE/MAE by state — NEVER touches the
                                   │ confirmation slices
                                   ▼
                        back to LOOK and EXPLAIN as new state variables,
                        exit-rule evidence, and cost reality

Three things make it a loop and not a line. **Failures are stored, not discarded** — a closure form says what was learned and the one condition under which the idea may return, and LEARN checks it by name before the next idea is written. **Facts are stored as assets, not trophies** — the fact registry is the Risk/State Engine's input, so every validated fact immediately changes how the bot sizes and stops. **Execution feeds back without contaminating** — what the bot measures in real time becomes new questions for the Observatory and new evidence for exit design, but never enters Validation or Holdout, which stay sealed.

The cycle that runs every two hours walks this loop in a fixed order: advance the lowest incomplete bot milestone it can; then work the pipeline's owed stages; then source from the queue; then close out. The bot is the trunk. The rest is the feeder.

# 5. How the research is structured

## Data is split by time, and the split is sacred

- **Discovery** (through October 3, 2021) — the only place anyone may search.
- **Validation** (October 4, 2021 through January 3, 2024) — one pre-registered shot per candidate.
- **Holdout** (January 4, 2024 through April 6, 2026) — final confirmation. Five uses ever, two spent.
- **Live-forward** — everything after today.

Definitions, bucket edges, and thresholds freeze on Discovery and are reused unchanged downstream. Nothing is ever refit per slice.

## The promotion bar — all four required

1. 90% bootstrap confidence interval entirely above zero.
2. Effect of at least 0.05R after realistic, measured costs.
3. Confirmation by one pre-registered prospective test on data never used to find it.
4. **Measured against the right null** (added September 12, see below). A number that clears (1)–(3) against the wrong benchmark clears nothing.

## The two nulls — the rule that killed H118

Every claim now has to beat the thing it would otherwise be mistaken for, and the comparison is specified before the test:

- A **directional** claim is measured against the instrument's own unconditional drift over the identical window — never against zero. On an asset that goes up, "it went up" is not a finding.
- A **cross-instrument** claim is measured against the beta-implied residual — what the relationship alone would have predicted — never against the raw move.

Overlapping-horizon results use a block bootstrap as the confidence interval of record, because overlapping windows make ordinary intervals look tighter than they are.

## Scarce resources, enforced

- Two attempts per hypothesis family, ever. Then it closes, and its failure reason becomes standing knowledge.
- Five Holdout slots, ever. Each use is consumed win or lose and requires my explicit sign-off first.
- Project-wide multiple-testing correction (Šidák family-wise) is computed in code and cited for every candidate at every stage, using the project-wide trial count — not assessed informally per candidate. Every cell of every scan is registered in a scan registry before the scan runs.

# 6. How we research — the front half

We start from market behavior, not trade ideas. Order matters:

    observe what the market actually does
    -> identify a recurring condition
    -> measure what happens next
    -> characterize it and baseline it
    -> assess robustness
    -> freeze the definition
    -> ask how it could be monetized
    -> validate it

Starting from "here's a strategy, let's test it" is how you end up testing your own imagination.

Concretely, discovery runs as scans: a frozen scope names a state variable (something measurable about the market), the buckets it is cut into, and the horizon measured. The scan reports which cells clear a pre-set gate. Survivors go into the agent pipeline in Section 9. Non-survivors close and are logged.

The standing research priority is short horizons — intraday, overnight, one to a few days. They accumulate evidence far faster than a 10-day hold. The tradeoff is understood: short horizons are execution-fragile, because a few points of slippage is a rounding error against a large edge and a quarter of a small one. Costs are measured, never assumed, and a candidate that only survives on optimistic costs is dead.

**Every family carries a kill rule.** If the response to a signal is concentrated in the first one-minute bar, the family terminates immediately — that is a speed race we would lose, not an edge — and it is never re-tuned toward a slower version of itself.

## Where ideas come from — the Idea Factory (rebuilt September 13)

The sourcing stage of September 12 was a review process wearing a generation process's clothes: an idea could not become an entry until it had a citation, a published effect size, decay evidence, a named forced participant, confounds, a kill rule, and a multiplicity cost. That is the right bar for *testing* something and the wrong bar for *finding* something, because only ideas that already exist in print can clear it on paper.

The front end now has three layers, in order:

**1. Look first (the free-look, `src/observatory_free_look.py` and `src/idea_factory.py`).** The Observatory crosses every market state already on disk — eleven of them: prior-day range, overnight range, opening range, gap, location in the trailing range, directional persistence, volume versus expected, VWAP distance, VXN versus its norm, VXN versus realized volatility, day of week — against eight session windows (overnight, first thirty minutes, morning, midday, afternoon, last hour, the whole session, the next session) and a five-part outcome battery: net move, range, maximum favourable excursion, maximum adverse excursion, and time to the window's extreme. On the Discovery slice only. Descriptively. It spends no hypothesis ID and registers no scan. It emits a **ranked candidate queue** of the strongest patterns that are neither circular nor restatements of what is already known.

**The timing rule** makes this legitimate rather than fishing. Every state carries the moment its value is actually known, and it may only be crossed with a window that starts at or after that moment. The rule exists because the engine's first run ranked "close-to-VWAP distance predicts the session's move" at twenty standard deviations — and that state is measured *at the close*, so the "discovery" was a definition. 315 such cells are dropped before ranking. A queue entry is never evidence and is never reported to me as a result; it is a place to point the ladder.

**2. Write the mechanism from the queue (Sourcing Rule v3).** Each cycle takes the highest-ranked family with no mechanism document and writes one — who is on the other side, why they are forced to act, what would prove it wrong. A queue entry with no defensible participant is skipped and the skip is noted, never forced. Only when the queue is exhausted of writable families does a cycle fall back to the literature and practitioner channels, which stay open at a higher bar. The forced-participant map still governs what enters; the map channel outperformed the literature channel this week and now gets the weight.

**3. Test once (unchanged).** Mechanism document before any scan; one pre-registered scan with every cell counted; the ladder in Section 9.

The first queue, run September 13: 1,045 comparisons ranked, 143 candidates in 19 families — and **zero of them about direction**. Every surviving candidate concerns how much price moves or how far a move runs before it turns. At far higher resolution than anything done before, direction still isn't there, and the excursion families are the raw material an exit rule is designed from.

Entries are still ranked by **expected information gain × edge potential**, with the reviews' amendment adopted in principle: divide by research cost and weight strategic reusability. A result that changes many future decisions outranks one that settles an obscure calendar effect.

**Conditional retests** of dead ideas are now a formal channel with an eight-condition protocol: a documented null; the condition chosen before rerunning; the condition drawn from an independently established mechanism or validated fact; one new variable; both versions reported; a new ID linked to the original; fresh Validation and Holdout; the family's attempt count incremented. The first sanctioned one — Level Sweep Reversal only after a compressed prior day — ran September 13 and closed clean (131 trades, no credible gap). The methodology worked; the answer for that pattern was no.

## The shelf — why we don't draw thin

A ranked list of vetted, unscanned entries sits in front of the pipeline. Three rules make it honest:

1. An entry counts as **drawable** only when its mechanism document is written, its resurrection ruling is signed, and its data is actually on disk. An entry that is waiting on data I haven't bought is on the list but is not on the shelf.
2. If fewer than three drawable entries exist, the cycle's owed work is **more sourcing** — never a draw. The system is not allowed to scan something marginal because it feels idle.
3. If three consecutive cycles go by without the shelf being restocked, that is an alert to me, not something the system works around.

There is an honest terminal state: nothing drawable and nothing worth sourcing. A cycle that reports that has done better work than one that manufactured a scan to avoid saying so. This replaced an earlier "queue exhausted" alarm that was pushing the system toward exactly the behavior it was meant to prevent.

## What we're allowed to search (scope, opened September 12)

The search used to be bounded by "NQ, 1-minute bars," which quietly limited what could even be proposed. It is now bounded by two hard constraints instead:

- The idea must resolve in **hours to a few days**.
- It must survive the existing out-of-sample discipline.

NQ is the **default execution vehicle, not the search space**. Every entry must state which instrument should carry the signal and which should carry the trade, and why — and answer whether NQ is genuinely the cheapest way to express the idea. If the mechanism says the effect lives somewhere else, that is what we say, even when it means we can't test it yet.

## What we've concluded about where the edge isn't

After eleven forced-participant entries produced nine clean nulls, one near-miss, and one untestable, four independent reads converged on the same conclusion: **scheduled, public flows are the most competed part of this market, and nine nulls there is the expected outcome.** The participants who actually leave money on the table — dealers hedging options, basis arbitrageurs, intraday liquidity takers — are not visible in one-minute open/high/low/close/volume data. Widening the search without new data produces lottery tickets with better stories.

I considered buying the data that would see them and decided, on September 12, **not to** — the cost was real and the return wasn't demonstrable. So the ceiling is fixed and acknowledged: one-minute bars on four instruments. Five otherwise-good entries are parked against it and are listed as parked, not quietly abandoned. The rule is now written down as a **Data Acquisition Trigger**: buy only when an existing price-based discovery establishes a credible mechanism, the missing variable is specifically required to test it, expected information gain is high, the candidate cannot be falsified with current data, the likely edge justifies the cost, and the purchase resolves a defined decision. All six, or no.

# 7. The bot — the product roadmap (added September 13)

This section outranks the research queue. `docs/BOT_ROADMAP.md` is the working copy; when the two conflict, the roadmap wins.

**The failure mode it prevents.** Every stage of the pipeline was gated on finding a directional edge first. September 13 produced eleven research upgrades in one afternoon and zero movement toward placing an order. That drift is the risk, and it is real.

**The reframe.** A bot needs signal → size → order → fill → monitor → kill. We have validated material for size and nothing for signal, so the first bot runs a deliberately ordinary, frozen, publicly-known entry — the opening-range breakout is the obvious candidate — labelled `placeholder` in every signal it emits. It is not expected to make money; it will roughly break even minus costs. Its purpose is to make the machine real, to measure what execution actually costs, and to answer one question: **does Tony's volatility layer improve an ordinary strategy's risk-adjusted behaviour versus the same strategy without it?** If yes, we have a product and the research just needs a better entry to drop in. If no, we learned it cheaply. Real capital waits for evidence, always.

**Milestones and where they stand.**

| # | Component | Status |
|---|---|---|
| B0 | Signal contract — the object every strategy emits | Done |
| B1 | Signal engine — walk-forward, no lookahead, exactly-once; checks 1–2 passed on 2,992 days | Partial (built around H118's since-rejected rule; needs repointing at B3) |
| B2 | Risk/State Engine — the four validated facts as a daily decision: expected range, stop distance, target distance, size multiplier, trade-permission flag; combined by residual, never product; no P&L claim | Spec'd |
| B3 | Base entry, frozen — ordinary, pre-registered, never claimed as an edge | Missing — **the unlock**: it makes the order path legitimate |
| B4 | Order path — broker paper account; spend pre-approved September 10, conditioned on reaching this stage | Missing |
| B5 | Execution measurement — the 14 frozen checks; slippage measured, never assumed | Missing |
| B6 | Kill switches — daily loss cap, trailing kill, slippage kill, divergence halt, catastrophe stop | Code exists, nothing calls it |
| B7 | Continuous paper run — ends on evidence, not a calendar | Missing |
| B8 | Live-Limited — tiny real size; my authorization alone | Missing |
| B9 | Scale behind evidence | Missing |

**The ordering rule, binding.** Every cycle advances the lowest-numbered incomplete milestone it can make real progress on before it works any research item. Research fills whatever budget remains. Research now has exactly two jobs: replace B3 with a real edge, and improve B2 with better state variables. A result that does neither is filed as knowledge and does not move the project.

**The one thing this roadmap will not do** is let the placeholder quietly become "the strategy." Its signals carry the placeholder label end to end, every session report names it, and no report to me presents its paper P&L as evidence of an edge.

# 8. How we prove we can execute it — the back half

Promotion is not the finish line. The standard must not weaken once something finally works — that is exactly when it is most tempting.

    Research-Validated
    -> Prospective Statistical Forward Test
    -> Paper Trading / Execution Qualification
    -> Live Authorization
    -> Live Monitoring
    -> Retained / Restricted / Suspended / Retired

Three things that are never conflated:

- **Prospective Statistical Forward Test** — the frozen strategy evaluated on unseen data as it arrives. Asks: does the validated behavior persist? It is not paper trading.
- **Paper Trading** — the frozen strategy running in real time through a real signal engine and order path against simulated execution. Asks: can our implementation actually capture it, against real fills, slippage, latency, and operational failure? Nothing has reached this.
- **Live Trading** — real capital, under capital-protection controls.

Two clocks run in parallel: the research clock (frozen forward test) and the execution clock (building the machinery). They advance independently and meet only at live authorization. Neither waits for the other. The execution clock is currently **parked on purpose** — it had been unblocked for H118, and H118 is gone. It restarts when a candidate earns it, not before.

Paper trading is another experiment, not a rehearsal for pressing "live." It ends on evidence — a pre-registered minimum sample plus passing checks — never on a calendar date.

A Production Integrity Layer will monitor four things once anything is executable: signal integrity, execution integrity, statistical integrity, and regime drift. It diagnoses and authorizes. It never optimizes.

The execution build is specified as eleven phases. Phases 1–5 (research infrastructure through holdout validation) exist today. Phases 6–11 (signal generation, human-tracked paper trading, automated paper execution, human-approved live, limited automated live, expanded automation) are designed with promotion criteria but not built, on purpose — nothing has earned them. The design separates a Strategy Engine (produces a signal only), a Risk Engine (decides if, how much, and where the stop and target are), an Execution Engine (order mechanics), and the Broker. A full safety-controls list (kill switches, daily loss cap, position and order caps, stale-data and duplicate-order protection, fail-closed behavior) is required, built and tested, before any unattended live trading.

# 9. The agents — how the work is done and reviewed

The research runs through a fixed pipeline of specialized agents. Each examines one candidate or one question. The order is the control.

    Jason (direction, not routine sign-off)
      |
    SOURCING               four channels, one template, ranked by information gain x edge potential
      |
    THE SHELF              drawable entries only; below floor = source more, never draw
      |
    RESEARCH DIRECTOR      what is worth pursuing; owns the freeze; CONTINUE / MODIFY / PIVOT / ABANDON
      |
    MECHANISM              written BEFORE the scan: who is forced to trade, and why it leaves a footprint
      |
    DISCOVERY              one pre-registered scan at the frozen spec
      |
    STATISTICAL            stability, regime dependence, magnitude, power, the two nulls
      |
    DIRECTOR RE-EVALUATION does this evidence justify spending more research capital?
      |
    MONETIZATION           natural realization path; "no credible path" is a valid, successful conclusion
      |
    INTEGRITY GATE         blind adversarial review with VETO the Director cannot override
      |
    VALIDATION (one shot)  -> INTEGRITY GATE (blind) -> HOLDOUT (my sign-off only)
      |
    PORTFOLIO              first job is "is this new information or the same state restated?"

The single most important ordering change: **the mechanism document is written before the scan, not after.** A mechanism written after a result is a story explaining a number, and it will always sound good.

Alongside the chain:

- **LEARN** — institutional memory, four buckets: KNOWN TRUE, KNOWN FAILED, KNOWN FAILURE MODES, KNOWN UNEXPLORED. Consulted by name before any scope is frozen and before any candidate is re-tested. Answers two questions: has this been closed before under another name, and does it match a known failure mode. Since September 12 it also maintains a single one-page knowledge file — what's true, what failed and why, what's parked, what's open, and a dated decision log — so a future session or a new reader starts from one page instead of reconstructing from a 14,000-word backlog.
- **OPERATIONS MANAGER** — a peer to the Research Director that owns the health of the machine, not the content of the research. Checks in code: lock held with no activity, console stale, missing session reports, consecutive runs producing no new information, ledger inconsistencies, anything past Discovery without a mechanism document, items parked on me with no clock. It has a binding deflection rule: asked any research question, by anyone including me, it refuses and names the agent that owns it. A role that answers research questions without qualification becomes a shortcut around the whole review chain.

## The Integrity Gate

This is the structural correction the project made after a candidate reached Holdout on the strength of checks its own builder performed. Research Integrity is not background process. It runs continuously (freeze rules, contamination, multiple-testing tracking, the two-attempt limit, no resurrection) AND as a mandatory explicit stop before any candidate crosses Discovery → Validation or Validation → Holdout.

Those stops are **blind**: the candidate is packaged without its name, its story, or its results and handed to a reviewer with no context from the work that produced it. Its standing brief: "Assume this candidate is wrong. Find every reason we could be fooling ourselves." It examines leakage, contamination, selection after seeing results, multiplicity exposure, whether related hypotheses were tested before, whether the candidate is distinct from prior findings, whether direction was pre-registered or fit to the result, whether anything changed after seeing results, and whether this is a resurrection of something closed.

It has veto authority the Director cannot override. A candidate the Gate does not clear does not proceed, regardless of how promising the numbers look.

## Rules that make the agents actually run

Measured in the first days of autonomous operation, the running chain was Discovery → Statistical → dead; nothing else fired. Three fixes are now standing rules:

**Applicability.** An agent is never skipped because a session is busy — only because its input condition was not met. Every session report lists every agent as either RAN or NOT RUN with the unmet condition named. An agent omitted entirely is itself an audit finding.

**RETURN.** At the close of every session the Integrity Gate audits each candidate that moved. If a required stage was skipped, the candidate goes back to the missing stage, at the top of the next session's queue. A RETURN is a course correction, not a block and not a kill. This was chosen deliberately over a hard gate, which would stall work until a human intervened — the dependency the project is trying to remove.

**Mechanism Gate.** No mechanism document, no advance. Binding.

**Staff meetings.** Any agent may request one; only the Director convenes one. Mandatory on five triggers: a second RETURN on the same candidate; conflicting recommendations between agents; a zero-survivor scan or every third closed scan (the methodology review — is the approach itself still producing discoveries?); any agent requesting one with a reason; and the shelf running dry. A staff meeting produces exactly one disposition plus the change that follows from it, and records every agent's position, not just the outcome, so a later session doesn't relitigate it blind. The Integrity Gate's veto survives inside the meeting — no majority overrules it.

## The Observatory's new job (September 13)

The Observatory used to be a measurement layer that characterized behavior without proposing trades. It is now also the project's generation engine. It is the only role allowed to look at Discovery data without a written mechanism, and the rules that make that safe are the ones above: descriptive only, no hypothesis ID, no scan registered, timing rule enforced, output is a queue and never a result. The Mechanism role still owns the story; the Observatory owns the looking. Splitting those two was the single most consequential change of the day.

## Two changes to the Integrity Gate (September 13)

The reviews agreed the Gate is procedurally but not epistemically independent — one model in every role shares one set of blind spots, and H118's baseline confusion passed three stages because every reviewer had the same gap. Two fixes, both adopted:

**Structural blindness.** The Gate receives the frozen candidate, the raw cell outputs, the ledger rows, the benchmark results, and the audit rules — and not the mechanism narrative, the Discovery prose, the expected result, or the Director's recommendation. Don't ask the skeptic to review the sales pitch.

**A mechanical suite, in code.** Drift null, overnight/intraday split, cost sensitivity at double costs, roll-date contamination, subperiod stability, concentration in the top 5% of observations, and placebo (shifted and inverted signals) — run on every candidate before the Gate, green or red, so a green result can never depend on someone remembering to ask. Any red is a blocking finding, not an automatic close.

## The multiplicity correction, diagnosed

One review claimed the project-wide correction double-counts. It does not: the code uses three separate stage-specific trial counts (Discovery 451, Validation 20, Holdout 3), and Discovery trials are never re-counted at Validation. What *is* true is that the Discovery bar tightens for the life of the project — every scan cell ever run is added forever, 275 → 451 in three days — and it has already closed one candidate (hyp-139) that Validation could have judged. Whether to switch to within-scan false-discovery-rate control and let Validation/Holdout be the project-wide control is a bar change and my call. It is open.

# 10. How we learn — and how we guard against fake work

## What was added to the learning system on September 13

**The closure form.** Every closed hypothesis now gets a fixed record: closure status (clean null · near miss · data limitation · execution limitation · valid-but-non-actionable · invalid premise · duplicate), the primary outcome as registered, sample adequacy, the mechanism verdict (falsified · weakened · untested-by-this-result), robustness and cost flags, what was learned in one searchable sentence, what must not be retested, the one permitted future condition, and a capacity action for its family. Filed as Section 12 of the mechanism document and mirrored in an append-only closures ledger. This is what turns "FAILED" into knowledge LEARN can actually consult; a retroactive pass over this week's twelve closures is owed.

**The fact registry** (`research/registry/facts.md`). One row per validated fact: what it says in plain language, instrument, horizon, mechanism, stage reached, stability, which facts it relates to, and which strategies use it. Seeded with the four validated facts and the three event-volatility passes. The Risk/State Engine reads from it; every strategy must link back to the fact IDs it uses. A feature library — definition cards for every state variable, with its exact calculation and the moment it is known — sits beside it, and is where the timing rule's register lives.

**The economic-validity checklist.** Before Statistical, every candidate answers: which null is correct and why; whether the effect is directional, relative, conditional, or a risk-state effect; which measurement (raw points, ATR-normalized, R-multiple, benchmark-relative) and why; concentration by year, regime, time of day, and event; placebo results (shifted, inverted, random entry); and a one-line verdict on each alternative explanation (trend, volatility, seasonality, drift, liquidity, beta). The correct-null part has been in force since the baseline fix; placebo, concentration and alternative-explanation checks are the September 13 additions, and the mechanical suite runs them.

**Yield metrics replace "hypotheses closed."** Progress is now read as: actionable-pass rate; strategy-conversion rate (facts that became an executable component); paper-trade fidelity; research-family yield (which channels and families actually produce); reuse rate; reproducibility rate; defect escape rate; and open research debt. "We tested eleven things" is no longer a sentence that appears in a report without the next sentence saying what any of it was good for.

**The swing question, parked correctly.** I asked for "swing trading with a particular exit strategy." I don't yet have the exit rule, so Tony wrote the question instead of an answer — what a swing strategy would be in this system's terms (entry, exit, size, permission), which of five pre-declared exit shapes (fixed stop and target; fixed stop plus time exit; fixed stop plus volatility-scaled trailing stop; fixed stop plus session-end exit; one exit conditioned on a validated fact) to test first, and whether a swing may hold through a scheduled release. Exit parameters will be calibrated from the bot's measured excursion data, never from a backtest. Nothing is built until I come back with an answer.

## Named shapes of manufactured work, each with a guard

- **Resurrection** — re-testing a closed idea under a new name. Guard: LEARN checks by name and by what is measured; Integrity rules per variable at insertion.
- **Cosmetic novelty** — the same idea at a different bucket boundary, horizon, or parameterization. Guard: an entry must differ from closed work in its mechanism claim, not its parameters. Re-cutting a dead idea is the dead idea.
- **Slicing** — finer and finer cells on the same data until something clears. Guard: every cell is registered before the scan; more cells is a cost, never a strategy.
- **Lottery tickets** — testing a variable because the data is on hand, with no claim about why it would work. Guard: the mechanism claim, with a named forced participant, is an entry requirement.
- **Busy-work** — re-documenting or re-summarizing what is settled so a session has something to show. Guard: every session must state what new information it produced; three cycles of nothing is an alert to me.
- **Baseline confusion** (added September 12) — measuring a claim against a benchmark that flatters it. Guard: the two-nulls rule, specified before the test.

The standing test for any proposed entry: would we have proposed this before seeing any data, and if it comes back null, will we have learned something? If either answer is no, it is activity, not research.

## The failure-mode taxonomy

Every closure files its reason into one of seven named modes, each with real examples from our own ledger: cost dominance; thin-sample overconfidence; correlated-lens double-counting; direction ambiguity in pooled events; marginal Discovery passes that don't replicate; exit-design mismatch (a real drift destroyed by a stop that races it); and baseline confusion. Every new candidate is checked against all seven before it advances.

We also track which **sources** of ideas have ever produced anything real: pattern-guessing 0%, intuition roughly 1 in 8, behavior-first observation roughly 1 in 3, the forced-participant map 0 for 11. The literature, practitioner, and observatory channels started being measured on September 12. This is the number that tells us whether the front of the pipeline is working, and it is the reason the sourcing stage exists.

The ledger of every hypothesis is append-only and honest, including unflattering results. Nothing is ever hand-edited; if a result looks wrong, the fix is in the code, then re-run.

# 11. Rules that never bend

**Anti-optimization.** A frozen strategy is frozen. "Fewer trades than expected, loosen the filter." "Lost three in a row, adjust the stop." "Regime changed, adapt it." All three are new hypotheses that enter the front half at the back of the queue under the two-attempt limit. They are never edits. The only permitted responses to disappointing behavior are retain, restrict, suspend, retire — and those are my calls.

**Scope boundary.** Automated sessions work only below the forward-validation line. Anything promoted is frozen to them: no re-analysis, no new statistical lenses, no status changes. Flag and stop, never act. A process that can re-analyze a frozen candidate every few hours will eventually find a lens that changes the answer — that is multiple testing applied to methods.

**Pre-registered review points never move.** Not tighter, not looser, not because we got impatient.

**Two different kills.** A statistical kill ("did the hypothesis stop looking good?") is not allowed during a predetermined forward-validation period. An execution kill ("is the machine doing something we didn't authorize?") is required once live. Protecting the purity of the experiment at the expense of the trading account is the wrong trade.

**Decide what would make us stop before we know whether we'll need to stop.** Stop and suspend conditions are written and frozen before live authorization.

**Speed comes from the right places only.** Prefer short horizons and cut wasted calendar time. Never reduce required evidence.

**The change freeze is lifted; the decision log replaces it.** The September 12 freeze existed so the structure would run long enough to produce evidence about itself. The checkpoint was held on September 13 instead of the 19th, on six outside reviews, and the freeze was lifted in full. What remains is the habit it was protecting: every structural change gets a dated line in `research/KNOWLEDGE.md` saying what changed and why, its own document or test, and never an edit to a frozen candidate's definition.

**The timing rule.** A market state may only be crossed with an outcome window that starts at or after the moment the state is known. Binding on every generation pass, because a definition restated as a discovery is the cheapest way to fool a whole pipeline at once.

# 12. Autonomy — what runs without me and what doesn't

The team runs continuously on its own judgment. It does not hand me forks, does not end reports on open questions, and does not narrate each step. The Research Director plus Integrity Gate structure is the mechanism for deciding what to research next and whether to trust a result — in place of asking me.

Exactly three things require me and cannot be delegated:

1. Spending one of the five Holdout slots, win or lose.
2. Any spend of $5 or more.
3. Live-capital authorization — always, regardless of any statistical result. No number ever authorizes capital on its own.

Plus: flag and stop on any integrity problem with something already promoted.

## How sessions run

An autonomous cycle runs every two hours, around the clock, and schedules its own successor. Each run takes a lock (two writers corrupt the ledger), reads a single baton file for current state and the ordered queue, advances the lowest incomplete bot milestone it can, sources the shelf from the Idea Factory queue, works whatever the pipeline is owed, checkpoints after every item (a run can die without warning; anything uncheckpointed is lost), writes a session report listing every agent as ran or not run, runs the Integrity Gate audit and the operations checks, updates a status document that feeds a console I read, commits everything to version control, and releases the lock. Candidates are classified OPEN (fully automated through Validation), GATED (Holdout is next — the cycle prepares and stops for my sign-off), or FROZEN (past Holdout — untouched until the pre-registered window closes).

The September 19 review was cancelled — the checkpoint was held on the 13th. A routine one-page weekly review resumes Saturday September 26, written by the first cycle of the morning, no separate scheduled task. Three questions are parked for me alone and the system does not raise them: what exit architecture I mean by "swing trading with a particular exit" (a question is written up for outside feedback, nothing is built); whether to change the Discovery-stage multiplicity bar; and what a realistic money goal is — deferred until paper trading has a record to calibrate against.

# 13. What I want critiqued

I am not asking whether the writing is clear. I am asking whether the structure is right. Specifically:

- The project now says a trading bot does not need an edge to exist, and builds one around a placeholder entry plus a validated sizing layer. Is that the right unblock, or a sophisticated way to ship something that cannot make money?
- Is "does the volatility layer improve an ordinary strategy's risk-adjusted behaviour versus the same strategy without it" the right first test of a product — and what would a professional insist on measuring that we haven't named?
- With 159 records and zero directional survivors — now confirmed at time-of-day × state resolution with a full outcome battery — is the expected value of continuing to search for direction positive at all, or should research be entirely about the sizing layer and the exits?
- The Idea Factory ranks 143 candidates in 19 families from a single pass. Is the timing rule plus "mechanism before test, one shot, every cell counted" enough to keep that from being a fishing expedition with better paperwork?
- The multiplicity diagnosis says the correction does not double-count but the Discovery bar tightens forever. Within-scan FDR with out-of-sample slices as the project-wide control — right, wrong, or a false choice?
- The Integrity Gate now runs blind and has a mechanical check suite. Is that independence, or is it still one model grading its own homework with a blindfold on?
- Is ranking research by information gain × edge potential ÷ cost the right call, or a way to justify testing things we expect to fail?
- The data ceiling is fixed and a six-condition trigger governs any purchase. Is that discipline, or a conclusion that conveniently ends an expensive question?
- Does the back half — placeholder signal, risk engine, order path, measured execution, evidence-based paper, Live-Limited under my authorization only — match how professionals actually take a strategy from research to capital?
- Three of the four validated facts predict range, not direction, and one predicts the shape of a session. Is the swing-exit question best answered from their excursion data, or is swing trading a different project wearing this one's clothes?
- What is the single biggest way this project could still be fooling itself?
