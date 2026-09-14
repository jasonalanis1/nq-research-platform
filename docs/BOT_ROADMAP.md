# The bot is the goal — product roadmap

Written September 13th, ~6:00 pm CT, at Jason's direction: *"A very important
distinction should be this is an end goal trading bot, we should keep that envision
bc our overall goal should be working to that, not being the best research tool."*

This document outranks the research queue. `research/NEXT_UP.md` says what gets
worked on next; **this** says what it is all for. When the two conflict, this wins.

## The failure mode this exists to prevent

Every stage of the current pipeline is gated on finding a directional edge first.
160 attempts say that edge may not arrive. If the bot only gets built after the
edge lands, the bot may never get built — and the project quietly becomes a very
rigorous instrument for producing null results. That is the drift Jason called out,
and it is a real risk, not a hypothetical: today's session produced eleven research
upgrades and zero millimetres of movement toward placing an order.

## The reframe that unblocks it

**A trading bot does not need an edge to exist.** It needs:

> signal → size → order → fill → monitor → kill

Tony has real, validated material for **size**. It has nothing for **signal**. But
the machine can be built and run end to end with a deliberately ordinary, frozen,
publicly-known entry — and the volatility work does the job it is actually good at.

That is not a compromise. It is the honest shape of the thing: the entry is a
placeholder the research pipeline keeps trying to replace, and every future
candidate inherits a machine that already works.

**Stated plainly so it is never misread:** a bot with a placeholder entry is not
expected to make money. It will roughly break even minus costs. Its purpose is to
make the machine real, to measure what execution actually costs, and to test
whether Tony's volatility layer improves a base strategy's risk-adjusted behaviour
versus the same base without it. Real capital waits for evidence, always.

## Milestones

| # | Component | Status | What it is |
|---|---|---|---|
| B0 | Signal contract | **DONE** | `src/strategy_contract.py` — the `Signal` object every strategy emits: instrument, direction, entry, stop, target, risk multiple, validation status. |
| B1 | Signal engine | **DONE for B3** (Sept 13th, 7:00 pm test cycle) | `src/base_entry_b3.py` emits `Signal` objects for the placeholder with a walk-forward audit (exactly-once per day, entry strictly after trigger, all labelled placeholder) — 2,717 signals over 3,638 sessions, 0 violations. The older `execution_clock_signal_engine.py` (H118's rule) is untouched and out of scope. |
| B2 | Risk/State Engine | **BUILT** (Sept 13th, 7:00 pm test cycle: `src/risk_state_engine.py`, frozen params, 9 tests, daily log) | The validated volatility facts turned into a daily decision: expected range, stop distance, target distance, size multiplier, and a trade-permission flag. This is Tony's only real contribution to a live trade today. |
| B3 | Base entry, frozen | **DONE** (spec frozen + coded + 6 tests, Sept 13th, 7:00 pm test cycle: `src/base_entry_b3.py`, fires on 75% of sessions, exactly-once, no lookahead, every signal `placeholder`) | One ordinary, pre-registered, publicly-known entry rule. Explicitly NOT claimed as an edge. Labelled `validation_status="placeholder"` in every signal it emits, so it can never be mistaken for a finding. |
| B4 | Order path | **MISSING — NEXT; needs Jason** (broker paper account: Tradovate per the Sept 11th brief; spend pre-approved, but the account and credentials are his to create) | Broker paper account and the code that turns a `Signal` into an order and records what came back. Spend pre-approved September 10th (~$60–115/mo, Tradovate or IBKR), conditioned on reaching this stage — this milestone is that condition. |
| B5 | Execution measurement | **MISSING** | The 14 frozen checks: signal timing, exactly-once firing, order correctness, fills recorded, expected-vs-actual price, slippage **measured not assumed**, latency, rejects, duplicates, position reconciliation, no orphan positions. |
| B6 | Kill switches wired | **CODE EXISTS, NOT WIRED** | `src/capital_protection.py` already implements the daily loss cap, trailing kill, slippage kill, signal divergence and catastrophe stop. Nothing calls it, because nothing trades. |
| B7 | Continuous paper run | **MISSING** | The whole loop running live on real sessions with simulated fills. Ends on evidence — the minimum execution-validation sample — not on a calendar date. |
| B8 | Live-Limited | **MISSING** | Tiny real size. **Jason's authorization alone, non-delegable.** $300 hard loss budget. No statistical result authorizes capital by itself. |
| B9 | Scale behind evidence | **MISSING** | Size follows the measured record, never precedes it. |

## What research is for, under this ordering

Research is a **feeder**, not the trunk. It has exactly two jobs:

1. **Replace B3** with an entry that is a real edge. This is the Idea Factory's
   whole purpose — the candidate queue exists to find a better signal to drop into
   a machine that already runs.
2. **Improve B2** with better state variables, so sizing, stops and
   trade-permission get sharper. Every volatility fact found goes straight here.

A research result that does neither is knowledge, and gets filed — but it does not
move the project. That test is now applied to every queue item.

## Ordering rule, binding from today

Every cycle works the **lowest-numbered incomplete bot milestone** it can make real
progress on, before it works any research item. Research fills whatever budget is
left. If a cycle cannot advance a milestone (blocked on Jason, blocked on a
purchase, blocked on data), it says which milestone and why, then falls through to
research.

## The one thing this roadmap will not do

It will not let the placeholder entry quietly become "the strategy." B3 signals
carry `validation_status="placeholder"` end to end; the session report states the
base entry by name every time; and no report to Jason describes paper P&L from a
placeholder entry as evidence of an edge. If the volatility layer improves that
base's risk-adjusted behaviour, *that* is the finding worth reporting — not the
P&L.
