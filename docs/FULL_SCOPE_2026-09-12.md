---
title: "Tony — The Full Scope"
subtitle: "An automated NQ futures research operation: what it's for, how it's structured, how it researches and learns, and how the agents run it"
author: "Jason Alanis"
date: "September 12, 2026"
---

# Why this document exists

This is the complete scope of a project I call Tony, in one place, written so someone outside it can critique it. It combines the vision, the operating rules, the research methodology, the agent structure, and the learning system. Nothing here is aspirational shorthand; every rule described is one the system actually runs under today.

I am not a statistician or a programmer. I direct this project; an AI agent team builds and runs it. What I want from a reader is candor: where is this structure fooling itself, where is it over-engineered, where is it missing something a professional would consider obvious, and does the whole thing actually point at the goal.

This version is dated September 12, 2026 and supersedes the September 11 version. A lot changed in one day, and Section 3 says exactly what.

# 1. The vision

I'm trying to build an automated system that actually makes money trading NQ futures. Not a good backtest — a real system, running itself, that I can trust with capital.

The honest alternative outcome is finding out cheaply that no such edge is available from what we can test. Both of those outcomes are acceptable. Expensive self-deception is not.

In my own words, the goal is an AI-automated trading bot: a system that does quality research, identifies new trading edges, and analyzes the market through a professional trader's lens. The project always had proficient research but for a long time no discovery function — rigor without discovery only proved the guesses wrong. The restructure described here exists to fix that.

The top priority is the holistic lens: are we looking at this the right way to reach the goal? Learning, research, discovery, testing, and calculated adjustment are the method, not the objective.

# 2. The central belief — everything follows from this

The default outcome in this field is fooling yourself. Markets are mostly noise. Search hard enough and something will always look like an edge. Every rule in this document blocks one specific way of being fooled. When a rule feels inconvenient, that is usually the moment it is doing its job.

Three consequences govern everything:

**A dead candidate is a success, not a failure.** Finding out cheaply that something doesn't work IS the product. Nothing here has ever cleared a correctly-specified promotion bar. That is a real result, not a sign anything is broken. A dead candidate is never softened, reframed, or resurrected to keep it alive.

**Looking and finding out are different activities.** Discovery data is where you are allowed to search. Validation and Holdout are where you find out. The moment those blur, the project learns nothing.

**Freeze before you test.** Definition, direction, thresholds, windows, exit rule — all fixed in writing before any result is seen. A change made after seeing a result is not an improvement; it is a new hypothesis.

# 3. The honest current state

137 distinct hypotheses have been tested. **Zero have ever cleared a correctly-specified promotion bar.** No strategy has ever been executed, even on paper with real orders.

The change since the September 11 version of this document is that H118 — the one candidate that had cleared the bar, a VWAP-distance / 10-day-drift long — was **reclassified REJECTED on September 12**. A diagnostic asked the question nobody had asked it: compared to what? H118 was a long-only effect measured against zero, on an asset that drifts up. Measured against NQ's own unconditional drift over the same windows, the edge disappears — the difference is +0.12 ATR on Discovery with a 90% confidence interval of −0.26 to +0.49, and on Validation the HIGH bucket actually beat the LOW bucket the strategy traded. It passed three stages because at every stage its benchmark was the wrong one. That failure mode is now named (baseline confusion), has a standing rule against it, and six related hypotheses were reclassified with it.

What survives is real but is not a strategy:

- **Three volatility facts**, each confirmed out-of-sample: range contraction/expansion persists; a coiled overnight range predicts a compressed day session; a quiet midday predicts a quieter afternoon (ratio ~0.74 — the cleanest result in the project, and it passed Holdout). None is directional. All are state variables that belong to a risk/sizing product, not a trade signal. **The largest open loose end in the project is that none of them has ever been built into anything.**
- **One gated candidate**: a VXN-conditioned next-session range effect that passed Validation and is waiting at Holdout for my sign-off. I'm holding it for a cleaner story. Two of five Holdout slots are spent; three remain.
- **One tracker**: a weekly momentum idea that was rejected at Discovery and is being followed forward anyway, as a calibration check on our own rejection decisions. Week 3 of 260.

Whether this project ever produces a profitable automated system is unknown and may be no. What it has produced so far is a reliable machine for finding that out.

# 4. How the research is structured

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

# 5. How we research — the front half

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

Concretely, discovery runs as scans: a frozen scope names a state variable (something measurable about the market), the buckets it is cut into, and the horizon measured. The scan reports which cells clear a pre-set gate. Survivors go into the agent pipeline in Section 7. Non-survivors close and are logged.

The standing research priority is short horizons — intraday, overnight, one to a few days. They accumulate evidence far faster than a 10-day hold. The tradeoff is understood: short horizons are execution-fragile, because a few points of slippage is a rounding error against a large edge and a quarter of a small one. Costs are measured, never assumed, and a candidate that only survives on optimistic costs is dead.

**Every family carries a kill rule.** If the response to a signal is concentrated in the first one-minute bar, the family terminates immediately — that is a speed race we would lose, not an edge — and it is never re-tuned toward a slower version of itself.

## Where ideas come from — the sourcing stage (added September 12)

The front of the pipeline used to be its weakest part. Ideas were generated in bursts, and when the list ran dry the system got creative in the wrong way. The fix is a formal sourcing stage that runs **every cycle**, before anything else:

Four channels are worked continuously and their hit rates are tracked: the **forced-participant map** (who in this market is required to trade, regardless of opinion, and what footprint does that leave), **academic literature**, **practitioner claims**, and the **Observatory** (characterizing behavior across instruments without claiming a trade). Every candidate enters through one template and is not an entry until every field is filled: the source channel and citation, a falsifiable one-sentence claim, the constrained participant and what forces them, the exact pre-registered specification, the published effect size and post-publication decay evidence, a resurrection ruling checked against the ledger by name and by what is measured, the known confounds and the check that separates them, the data needed and whether we have it, the kill rule, and the multiplicity cost.

Entries are ranked by **expected information gain × edge potential** — what the result teaches us either way, times what it is worth if it's real. Explicitly **not** by the probability of a positive result. A long-shot that settles a design question or decides a data purchase outranks a likely but minor pass. This is the rule I most want critiqued.

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

I considered buying the data that would see them and decided, on September 12, **not to** — the cost was real and the return wasn't demonstrable. So the ceiling is fixed and acknowledged: one-minute bars on four instruments. Five otherwise-good entries are parked against it and are listed as parked, not quietly abandoned. If a price-only result ever earns the purchase, we'll revisit it then.

# 6. How we prove we can execute it — the back half

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

# 7. The agents — how the work is done and reviewed

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

# 8. How we learn — and how we guard against fake work

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

# 9. Rules that never bend

**Anti-optimization.** A frozen strategy is frozen. "Fewer trades than expected, loosen the filter." "Lost three in a row, adjust the stop." "Regime changed, adapt it." All three are new hypotheses that enter the front half at the back of the queue under the two-attempt limit. They are never edits. The only permitted responses to disappointing behavior are retain, restrict, suspend, retire — and those are my calls.

**Scope boundary.** Automated sessions work only below the forward-validation line. Anything promoted is frozen to them: no re-analysis, no new statistical lenses, no status changes. Flag and stop, never act. A process that can re-analyze a frozen candidate every few hours will eventually find a lens that changes the answer — that is multiple testing applied to methods.

**Pre-registered review points never move.** Not tighter, not looser, not because we got impatient.

**Two different kills.** A statistical kill ("did the hypothesis stop looking good?") is not allowed during a predetermined forward-validation period. An execution kill ("is the machine doing something we didn't authorize?") is required once live. Protecting the purity of the experiment at the expense of the trading account is the wrong trade.

**Decide what would make us stop before we know whether we'll need to stop.** Stop and suspend conditions are written and frozen before live authorization.

**Speed comes from the right places only.** Prefer short horizons and cut wasted calendar time. Never reduce required evidence.

**Change freeze.** Added September 12, after a day in which the structure changed more than the research did: no changes to the pipeline, the rules, or the templates until a scheduled review. Defect fixes with tests are allowed. Observations go into the weekly review, not into live edits. The system is now required to run under its own rules long enough to produce evidence about them.

# 10. Autonomy — what runs without me and what doesn't

The team runs continuously on its own judgment. It does not hand me forks, does not end reports on open questions, and does not narrate each step. The Research Director plus Integrity Gate structure is the mechanism for deciding what to research next and whether to trust a result — in place of asking me.

Exactly three things require me and cannot be delegated:

1. Spending one of the five Holdout slots, win or lose.
2. Any spend of $5 or more.
3. Live-capital authorization — always, regardless of any statistical result. No number ever authorizes capital on its own.

Plus: flag and stop on any integrity problem with something already promoted.

## How sessions run

An autonomous cycle runs every two hours, around the clock, and schedules its own successor. Each run takes a lock (two writers corrupt the ledger), reads a single baton file for current state and the ordered queue, sources the shelf, works whatever the pipeline is owed, checkpoints after every item (a run can die without warning; anything uncheckpointed is lost), writes a session report listing every agent as ran or not run, runs the Integrity Gate audit and the operations checks, updates a status document that feeds a console I read, commits everything to version control, and releases the lock. Candidates are classified OPEN (fully automated through Validation), GATED (Holdout is next — the cycle prepares and stops for my sign-off), or FROZEN (past Holdout — untouched until the pre-registered window closes).

Two governance habits were added on September 12: a **weekly review** every Saturday, and a **checkpoint** on September 19 that asks the blunt question — what has survived, what is it worth, and is the right move to continue, buy the data that would see the invisible participants, or stop looking for a signal and build the product around the volatility facts we already trust.

# 11. What I want critiqued

I am not asking whether the writing is clear. I am asking whether the structure is right. Specifically:

- With 137 hypotheses tested and now **zero** survivors — after the one that looked like a survivor turned out to be measured against the wrong benchmark — is the expected value of continuing positive, and what would change your answer?
- The finding that killed H118 is that a long-only edge on a drifting asset must be measured against that drift. That's elementary. It survived three stages of a pipeline explicitly designed to catch self-deception. What does that say about the rest of the controls, and what else of this kind should we be checking for?
- Is the promotion bar (90% CI above zero, 0.05R after costs, one pre-registered confirmation, correct null) the right bar, too loose, or too tight for this data and this number of attempts?
- Does the chronological split, the two-attempt limit, and the five-slot Holdout actually control the multiple-testing problem, or is there a leak I'm not seeing?
- Is ranking research by **information gain × edge potential** rather than probability of success the right call, or is it a sophisticated way to justify testing things we expect to fail?
- We concluded that the profitable participants aren't visible in one-minute bars, and then declined to buy better data. Is that the right read of the evidence, or is it a conclusion that conveniently ends an expensive question?
- Is the shelf rule — never draw when fewer than three vetted ideas are ready — a real defense against manufactured work, or does it just relocate the problem to the sourcing stage?
- Is a blind adversarial Integrity Gate, with veto, the right control — and is it truly independent when the same underlying AI plays every role?
- Does the back half (forward test → paper → live, two clocks, two kinds of kill) match how professionals actually take a strategy from research to capital?
- Three volatility facts have been confirmed out-of-sample and none has been built into anything. Is the highest-value next move to keep hunting for a directional edge, or to build the sizing product around what we already know is true?
- What is the single biggest way this project could still be fooling itself?
