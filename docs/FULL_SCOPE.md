---
title: "Tony — The Full Scope"
subtitle: "An automated NQ futures research operation: what it's for, how it's structured, how it researches and learns, and how the agents run it"
author: "Jason Alanis"
date: "September 11, 2026"
---

# Why this document exists

This is the complete scope of a project I call Tony, in one place, written so someone outside it can critique it. It combines the vision, the operating rules, the research methodology, the agent structure, and the learning system. Nothing here is aspirational shorthand; every rule described is one the system actually runs under today.

I am not a statistician or a programmer. I direct this project; an AI agent team builds and runs it. What I want from a reader is candor: where is this structure fooling itself, where is it over-engineered, where is it missing something a professional would consider obvious, and does the whole thing actually point at the goal.

# 1. The vision

I'm trying to build an automated system that actually makes money trading NQ futures. Not a good backtest — a real system, running itself, that I can trust with capital.

The honest alternative outcome is finding out cheaply that no such edge is available from what we can test. Both of those outcomes are acceptable. Expensive self-deception is not.

In my own words, the goal is an AI-automated trading bot: a system that does quality research, identifies new trading edges, and analyzes the market through a professional trader's lens. The project always had proficient research but for a long time no discovery function — rigor without discovery only proved the guesses wrong. The restructure described here exists to fix that.

The top priority is the holistic lens: are we looking at this the right way to reach the goal? Learning, research, discovery, testing, and calculated adjustment are the method, not the objective.

# 2. The central belief — everything follows from this

The default outcome in this field is fooling yourself. Markets are mostly noise. Search hard enough and something will always look like an edge. Every rule in this document blocks one specific way of being fooled. When a rule feels inconvenient, that is usually the moment it is doing its job.

Three consequences govern everything:

**A dead candidate is a success, not a failure.** Finding out cheaply that something doesn't work IS the product. Roughly 1 in 100 hypotheses here has survived. That is expected, not a sign anything is broken. A dead candidate is never softened, reframed, or resurrected to keep it alive.

**Looking and finding out are different activities.** Discovery data is where you are allowed to search. Validation and Holdout are where you find out. The moment those blur, the project learns nothing.

**Freeze before you test.** Definition, direction, thresholds, windows, exit rule — all fixed in writing before any result is seen. A change made after seeing a result is not an improvement; it is a new hypothesis.

# 3. The honest current state

About 123 real hypotheses have been tested. One has ever cleared the full promotion bar (H118, a VWAP-distance / 10-day-drift candidate). Three others found real volatility and range facts, none of them directional or tradeable. No strategy has ever been executed, even on paper with real orders. Whether this project ever produces a profitable automated system is unknown and may be no.

H118 is currently in a prospective statistical forward test, live since September 8, 2026, with a pre-registered review point of 40 resolved trades AND 12 calendar months, whichever comes later. One look, no early peeks.

# 4. How the research is structured

## Data is split by time, and the split is sacred

- **Discovery** (through October 3, 2021) — the only place anyone may search.
- **Validation** (October 4, 2021 through January 3, 2024) — one pre-registered shot per candidate.
- **Holdout** (January 4, 2024 through April 6, 2026) — final confirmation. Five uses ever. One spent.
- **Live-forward** — everything after today.

Definitions, bucket edges, and thresholds freeze on Discovery and are reused unchanged downstream. Nothing is ever refit per slice.

## The promotion bar — all three required

1. 90% bootstrap confidence interval entirely above zero.
2. Effect of at least 0.05R after realistic, measured costs.
3. Confirmation by one pre-registered prospective test on data never used to find it.

## Scarce resources, enforced

- Two attempts per hypothesis, ever. Then it closes, and its failure reason becomes standing knowledge.
- Five Holdout slots, ever. Each use is consumed win or lose and requires my explicit sign-off first.
- Project-wide multiple-testing correction (Šidák family-wise) is computed in code and cited for every candidate at every stage, using the project-wide trial count — not assessed informally per candidate.

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

Concretely, discovery runs as scans: a frozen scope names a state variable (something measurable about the market, like where price sits relative to VWAP scaled by ATR), the buckets it is cut into, and the horizon measured. The scan reports which cells clear a pre-set gate. Survivors go into the agent pipeline in Section 7. Non-survivors close and are logged.

The standing research priority is short horizons. Short-horizon candidates (intraday, overnight, one to two days) accumulate evidence far faster than a 10-day hold. The tradeoff is understood: short horizons are execution-fragile, because a few points of slippage is a rounding error against a large edge and a quarter of a small one. Costs are measured, never assumed, and a candidate that only survives on optimistic costs is dead.

# 6. How we prove we can execute it — the back half

Promotion is not the finish line. The standard must not weaken once something finally works — that is exactly when it is most tempting.

    Research-Validated
    -> Prospective Statistical Forward Test
    -> Paper Trading / Execution Qualification
    -> Live Authorization
    -> Live Monitoring
    -> Retained / Restricted / Suspended / Retired

Three things that are never conflated:

- **Prospective Statistical Forward Test** — the frozen strategy evaluated on unseen data as it arrives. Asks: does the validated behavior persist? H118 is here. It is not paper trading.
- **Paper Trading** — the frozen strategy running in real time through a real signal engine and order path against simulated execution. Asks: can our implementation actually capture it, against real fills, slippage, latency, and operational failure? Nothing has reached this yet.
- **Live Trading** — real capital, under capital-protection controls.

Two clocks run in parallel: the research clock (frozen forward test) and the execution clock (building the machinery). They advance independently and meet only at live authorization. Neither waits for the other.

Paper trading is another experiment, not a rehearsal for pressing "live." It ends on evidence — a pre-registered minimum sample plus passing checks — never on a calendar date.

A Production Integrity Layer will monitor four things once anything is executable: signal integrity, execution integrity, statistical integrity, and regime drift. It diagnoses and authorizes. It never optimizes.

The execution build is specified as eleven phases. Phases 1–5 (research infrastructure through holdout validation) exist today. Phases 6–11 (TradingView signal generation, human-tracked paper trading, automated paper execution, human-approved live, limited automated live, expanded automation) are designed with promotion criteria but not built, on purpose — nothing has earned them. The design separates a Strategy Engine (produces a signal only), a Risk Engine (decides if, how much, and where the stop and target are), an Execution Engine (order mechanics), and the Broker. A full safety-controls list (kill switches, daily loss cap, position and order caps, stale-data and duplicate-order protection, fail-closed behavior) is required, built and tested, before any unattended live trading.

# 7. The agents — how the work is done and reviewed

The research runs through a fixed pipeline of specialized agents. Each examines one candidate or one question. The order is the control.

    Jason (direction, not routine sign-off)
      |
    RESEARCH DIRECTOR      what is worth pursuing; owns the freeze; CONTINUE / MODIFY / PIVOT / ABANDON
      |
    DISCOVERY              maps candidate behaviors; reports novelty and search exposure
      |
    CANDIDATE TRIAGE       Director function; grades A–F; D/F closes without spending a hypothesis ID
      |
    MECHANISM              testable predictions about WHY, written before measurement — not post-hoc stories
      |
    STATISTICAL            stability, regime dependence, magnitude, selection sensitivity; must disclose same-data selection
      |
    DIRECTOR RE-EVALUATION explicit second look: does this evidence justify spending more research capital?
      |
    MONETIZATION           natural realization path; "no credible path" is a valid, successful conclusion
      |
    INTEGRITY GATE         independent adversarial review with VETO the Director cannot override
      |
    DISCOVERY -> VALIDATION -> HOLDOUT
      |
    PORTFOLIO              only after the full promotion bar; first job is "is this new information or the same state restated?"

Alongside the chain:

- **LEARN** — institutional memory, four buckets: KNOWN TRUE, KNOWN FAILED, KNOWN FAILURE MODES, KNOWN UNEXPLORED. Consulted by name before any scan scope is frozen and before any candidate is re-tested. Answers two questions: has this been closed before under another name, and does it match a known failure mode.
- **OPERATIONS MANAGER** — a peer to the Research Director that owns the health of the machine, not the content of the research. Checks in code: lock held with no activity, console stale, missing session reports, three consecutive runs with no new information, ledger inconsistencies, anything past Discovery without a mechanism document, items parked on me with no clock. It has a binding deflection rule: asked any research question, by anyone including me, it refuses and names the agent that owns it. A role that answers research questions without qualification becomes a shortcut around the whole review chain.

## The Integrity Gate

This is the structural correction the project made after H118 reached Holdout on the strength of checks the builder performed on its own work. Research Integrity is not background process. It runs continuously (freeze rules, contamination, multiple-testing tracking, the 2-attempt limit, no resurrection) AND as a mandatory explicit stop before any candidate crosses Discovery → Validation or Validation → Holdout.

Its standing brief on every candidate: "Assume this candidate is wrong. Find every reason we could be fooling ourselves." It examines data leakage, Discovery/Validation contamination, selection after seeing results, multiple-testing exposure (naive and effective-independent), whether related hypotheses were tested before, whether the candidate is distinct from prior findings, whether direction was pre-registered or fit to the result, whether anything changed after seeing results, leakage across candidates, and whether the candidate is a resurrection of something closed.

It has veto authority the Director cannot override. A candidate the Gate does not clear does not proceed, regardless of how promising the numbers look.

## Rules that make the agents actually run

Measured in the first days of autonomous operation, the running chain was Discovery → Statistical → dead; nothing else fired. Three fixes are now standing rules:

**Applicability.** An agent is never skipped because a session is busy — only because its input condition was not met. Every session report lists every agent as either RAN or NOT RUN with the unmet condition named. An agent omitted entirely is itself an audit finding.

**RETURN.** At the close of every session the Integrity Gate audits each candidate that moved. If a required stage was skipped, it issues a RETURN: the candidate goes back to the missing stage, at the top of the next session's queue. A RETURN is a course correction, not a block and not a kill. This was chosen deliberately over a hard gate, which would stall work until a human intervened — the dependency the project is trying to remove.

**Mechanism Gate.** No mechanism document, no advance. Binding.

**Staff meetings.** Any agent may request one; only the Director convenes one. Mandatory on five triggers: a second RETURN on the same candidate; conflicting recommendations between agents; a zero-survivor scan or every third closed scan (the methodology review — is the approach itself still producing discoveries?); any agent requesting one with a reason; and the queue running dry. A staff meeting produces exactly one disposition plus the change that follows from it, and records every agent's position, not just the outcome, so a later session doesn't relitigate it blind. The Integrity Gate's veto survives inside the meeting — no majority overrules it.

# 8. How we learn — and how we guard against fake work

## The Idea Inventory

When the queue runs dry, generating new ideas under pressure produces whatever sounds plausible in the moment. That is exactly how four already-closed idea families were once queued as "genuinely new." So ideas are now generated in slack time and spent under load.

The inventory is a ranked list of vetted, unscanned research directions. An entry requires all four of: a state variable specified precisely enough to implement without interpretation; a one-line mechanism claim in market terms (who is on the other side of this trade and why do they keep taking it — a claim that could fail, not a narrative); a horizon, with short preferred; and an explicit Integrity Gate ruling of "new" or "second attempt on a closed family." An entry lacking any of the four is not an entry.

Cadence: the Integrity Gate counts the inventory at every session close; below three entries, the next session's first item is a generation meeting (LEARN reports first on what is actually unexplored, then Discovery proposes, then Integrity rules per variable, then Statistical states the multiplicity cost of scanning at all, then Mechanism states which directions can carry a prospective prediction, then the Director freezes one scope). When the queue empties mid-session, the session draws the top entry and works it — no meeting, because the vetting already happened.

There is an honest terminal state: queue empty, inventory empty, and the generation meeting produced nothing that clears the bar. The session logs that plainly and ends. A session that reaches it honestly has done better work than one that scanned something marginal to avoid saying so.

## Named shapes of manufactured work, each with a guard

- **Resurrection** — re-testing a closed idea under a new name. Guard: LEARN checks by name and by what is measured; Integrity rules per variable at insertion.
- **Cosmetic novelty** — the same idea at a different bucket boundary, horizon, or parameterization. Guard: an entry must differ from closed work in its mechanism claim, not its parameters. Re-cutting a dead idea is the dead idea.
- **Slicing** — finer and finer cells on the same data until something clears. Guard: Statistical attaches the multiplicity cost to every entry; more cells is a cost, never a strategy.
- **Lottery tickets** — testing a variable because the data is on hand, with no claim about why it would work. Guard: the mechanism claim is an entry requirement.
- **Busy-work** — re-documenting or re-summarizing what is settled so a session has something to show. Guard: every session report states what new information the run produced.

The standing test for any proposed entry: would we have proposed this before seeing any data, and if it comes back null, will we have learned something? If either answer is no, it is activity, not research.

## Every closure becomes knowledge

A hypothesis that closes doesn't just die — its failure reason is filed into LEARN's failure-mode bucket and checked against every future candidate. The ledger of every hypothesis is append-only and honest, including unflattering results. Nothing is ever hand-edited; if a result looks wrong, the fix is in the code, then re-run.

# 9. Rules that never bend

**Anti-optimization.** A frozen strategy is frozen. "Fewer trades than expected, loosen the filter." "Lost three in a row, adjust the stop." "Regime changed, adapt it." All three are new hypotheses that enter the front half at the back of the queue under the 2-attempt limit. They are never edits. The only permitted responses to disappointing behavior are retain, restrict, suspend, retire — and those are my calls.

**Scope boundary.** Automated sessions work only below the forward-validation line. Anything promoted is frozen to them: no re-analysis, no new statistical lenses, no status changes. Flag and stop, never act. A process that can re-analyze a frozen candidate every few hours will eventually find a lens that changes the answer — that is multiple testing applied to methods.

**Pre-registered review points never move.** Not tighter, not looser, not because we got impatient.

**Two different kills.** A statistical kill ("did the hypothesis stop looking good?") is not allowed during a predetermined forward-validation period. An execution kill ("is the machine doing something we didn't authorize?") is required once live. Protecting the purity of the experiment at the expense of the trading account is the wrong trade.

**Decide what would make us stop before we know whether we'll need to stop.** Stop and suspend conditions are written and frozen before live authorization.

**Speed comes from the right places only.** Prefer short horizons and cut wasted calendar time. Never reduce required evidence.

# 10. Autonomy — what runs without me and what doesn't

The team runs continuously on its own judgment. It does not hand me forks, does not end reports on open questions, and does not narrate each step. The Research Director plus Integrity Gate structure is the mechanism for deciding what to research next and whether to trust a result — in place of asking me.

Exactly three things require me and cannot be delegated:

1. Spending one of the five Holdout slots, win or lose.
2. Any spend of $5 or more.
3. Live-capital authorization — always, regardless of any statistical result. No number ever authorizes capital on its own.

Plus: flag and stop on any integrity problem with something already promoted.

## How sessions run

An autonomous cycle runs every two hours. Each run takes a lock (two writers corrupt the ledger), reads a single baton file for current state and the ordered queue, works the queue until it is dry, checkpoints after every item (a run can die without warning; anything uncheckpointed is lost), writes a session report listing every agent as ran or not run, runs the Integrity Gate audit and the operations checks, updates a small status document that feeds a console I read, and releases the lock. Candidates are classified OPEN (fully automated through Validation), GATED (Holdout is next — the cycle prepares and stops for my sign-off), or FROZEN (past Holdout — untouched until the pre-registered window closes).

# 11. What I want critiqued

I am not asking whether the writing is clear. I am asking whether the structure is right. Specifically:

- Is the promotion bar (90% CI above zero, 0.05R after costs, one pre-registered confirmation) the right bar, too loose, or too tight for this data and this number of attempts?
- Does the chronological split, the 2-attempt limit, and the five-slot Holdout actually control the multiple-testing problem, or is there a leak I'm not seeing?
- Is the agent pipeline doing real work, or is it ceremony? Where would a professional research desk cut it down, and where would they add something?
- Is an independent adversarial Integrity Gate, with veto, the right control — and is it truly independent when the same underlying AI plays every role?
- Is the Idea Inventory plus the named guards a real defense against manufactured work, or does it just relocate the problem?
- Does the back half (forward test → paper → live, two clocks, two kinds of kill) match how professionals actually take a strategy from research to capital?
- With ~123 hypotheses tested and one survivor in a forward test with a 12-month clock, is the expected value of continuing positive, and what would change your answer?
- What is the single biggest way this project could still be fooling itself?
