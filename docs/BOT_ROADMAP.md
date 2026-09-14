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
| B4 | Order path | **SPLIT (Sept 13th, ~10:10 pm CT) — B4a BUILDABLE NOW, B4b needs a broker account** | **B4a (no broker, no money, mine to build):** the whole order path against a simulated broker interface — `Signal` → order construction → submission → acknowledgement → fill record → position reconciliation → crash recovery, plus B6's kill switches wired to it. Every guarantee in the back-half spec is testable here. **B4b (needs Jason):** swap the simulated interface for a real broker's. That is a connector, not a rebuild, once B4a exists. |
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

## Note added September 13th, ~9:55 pm CT (first conditional stack)

Stack A asked the roadmap's own question ahead of the paper run: does B2's expected-range
context change what the B3 opening-range break MEANS? Answer, on Discovery, as a powered
null (hyp-000161): no. The difference between breaks inside and outside the top-tercile
expected-range regime is +0.0247R with a 90% interval of (-0.0496, +0.0976), and the
Sidak-adjusted interval excludes anything above +0.19R.

So B2 stays exactly where the roadmap already puts it -- size, stop, target and permission
-- and is NOT an entry filter. B5's BASE vs BASE+B2 paper comparison still runs, because it
measures something this test did not: whether sizing and permission improve the DISTRIBUTION
of outcomes (drawdown, variance, days avoided). It now carries a stated prior: expect no
change in the entry's expectancy.

## B4 split — why, September 13th ~10:10 pm CT

Broker reality check, researched tonight: **Tradovate** will not issue API credentials against a
free simulation account. It requires a live account funded to **$1,000 equity** plus **$25/month**,
confirmed by their own staff on their forum. (Once subscribed, the API may be pointed at the
simulation environment indefinitely, so the $1,000 is a gate, not a cost.) **Interactive Brokers**
gives a free paper account with the same TWS API the live account uses, but the underlying live
account must be "approved and funded" — no published minimum, and IBKR has no minimum deposit for
an individual cash account, so the qualifying deposit is small rather than four figures.

Neither is available this week. The wrong response is to freeze the trunk behind it, so B4 splits:

**B4a is the honest majority of the work and needs nobody.** Order construction, the submit/ack/fill
state machine, the fill-vs-intended deviation record (points AND R, per side, never assumed zero),
position reconciliation, crash recovery that proves a position cannot be silently left open, and
B6's kill switches wired into the path. All of it is written against a `BrokerInterface` that a
simulated broker implements — one that rejects, partially fills, disconnects mid-order and returns
late acknowledgements on purpose, because those are the cases that break real systems.

**B4b is a connector.** When a broker account exists, it implements the same interface. The
integration risk collapses to one adapter with a contract that is already tested.

This ordering is also better engineering than waiting would have been. A first order path written
directly against a live broker API is a path whose failure modes were never deliberately exercised.
