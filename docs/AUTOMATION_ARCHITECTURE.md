# Automated Execution Architecture

*2026-08-20. Written in response to Jason's "Automated Trader — Explicit End-State"
document, reconciled against the live `docs/RESEARCH_ARCHITECTURE.md`,
`docs/ROADMAP.md`, and `CLAUDE.md` so it extends them instead of forking a competing
plan. Jason has confirmed: Phases becomes the one canonical numbering (replacing
ROADMAP's Stages), the Signal schema below is approved as-is, and thresholds for
Phases 6-8 (no real money involved) are relaxed — while Phase 10 (real money,
no per-trade approval) stays strict, unchanged from the original draft, on purpose.*

## Where this sits relative to what already exists

RESEARCH_ARCHITECTURE.md already has a "Future execution layer" section with almost
the identical safety list (kill switch, max daily loss, max position size, max
trades, duplicate-order prevention, connection handling, data-quality checks). This
document isn't a new destination — it's the same destination made precise: 11 named
phases instead of one paragraph, and an explicit four-layer separation (Strategy
Engine -> Risk Engine -> Execution Engine -> Broker) instead of "eventually support
execution."

`ROADMAP.md`'s Stages 0-4 map to Phases 1-5 (research infrastructure through
holdout validation); Stage 5 ("Automation") expands into Phases 6-11.
`RESEARCH_ARCHITECTURE.md`'s Layers 1-6 (data, features, strategy engine, etc.)
describe *what's built inside* Phases 1-5 — a different axis (system components)
than Phases (progression stages), not a competing timeline.

## The 11 phases, with promotion criteria

Phases 1-5 already have real, working promotion criteria in the repo today:

| Phase | What it is | Promotion criteria |
|---|---|---|
| 1. Research infrastructure | Data pipeline, holdout split, experiment logging | Working end-to-end (done) |
| 2. Strategy discovery | Turning a claim/idea into precise, testable rules | Rules are objective and mechanically checkable |
| 3. Backtesting | Run the rules against research-only historical data | Expectancy > 0 after realistic costs, >=150 trades, 90% bootstrap CI entirely above zero (the existing "promotion bar" in `ROADMAP.md`) |
| 4. Out-of-sample validation | Robustness checks within research data | Survives cost-stress test, not dependent on one narrow parameter choice |
| 5. Holdout validation | The one-time check against the sealed 2026-04-07+ holdout window | Still positive and statistically real on holdout data — governed by `data_holdout.py` and the `ALLOW_HOLDOUT_DATA` gate in `CLAUDE.md` |

| Phase | What it is | Promotion criteria |
|---|---|---|
| 6. TradingView signal generation | Live alerting via Pine Script (Tony) | Passed Phase 5. Pine Script independently verified line-by-line against the Python reference. Minimum of 5 live signals checked by hand against the formula before being trusted. |
| 7. Live paper trading (human-tracked) | Jason manually logs what would have happened if he'd taken every signal | Minimum of 15 manually-logged paper trades with expectancy sign matching the backtest. |
| 8. Automated paper execution | Software places simulated orders via a broker's paper API | Reliable operation for 10 consecutive trading days with zero missed or duplicated signals, results consistent with Phase 7's manually-tracked numbers. |
| 9. Human-approved live execution | Real money, system proposes and Jason approves each trade in real time | Governed by CLAUDE.md's existing Stage 5 rule: Jason's direct, in-the-moment approval every single time. |
| 10. Limited automated live execution | Real money, no per-trade approval, tight caps (1 contract, one strategy, a hard daily loss cap) | A sustained track record at Phase 9 (60+ human-approved live trades or a fixed time window) with live results consistent with paper and backtest, the full safety-controls checklist built and tested — not just designed — and a separate, explicit, written approval from Jason specifically for automation. |
| 11. Expanded automation | More size, more strategies, or more instruments running automated | Demonstrated reliability at Phase 10 scale over a meaningful period with zero safety-control failures. Each expansion needs its own fresh approval. |

## The execution separation

Strategy Engine produces a Signal only; a Risk Engine decides if/how much/where the
stop and target are; an Execution Engine decides order mechanics; the Broker
executes. `detect_level_sweep.py` and `detect_setups.py` already only produce
signal information — nothing architecturally needs to change to honor this
separation.

Signal schema, approved 2026-08-20 as the target shape for the strategy-contract
generalization work:

```
Signal {
  strategy_name, strategy_version
  timestamp, instrument, timeframe
  direction (long/short)
  entry, stop, target
  risk_multiple (R)
  validation_status (research / holdout-validated / paper / live-approved)
  historical_sample_size, historical_expectancy
  market_context tags (optional)
}
```

Defer: actually writing Risk Engine, Execution Engine, or broker-API code. Phases
6-8 are where this gets built, in order, each gated on the phase before it.

## Safety controls — required before Phase 10, not before

Global kill switch, strategy-level kill switch, max daily loss, max position size,
max simultaneous positions, max trades, max order value, stale-data protection,
duplicate-order protection, connection-loss handling, broker-error handling,
unexpected-position detection, emergency position-close, complete audit logging,
fail-closed behavior. Built and *tested* — not just present in code — as part of
Phase 10, not before.

## Automation-must-be-earned

A strategy becomes eligible for Phase 6+ only by clearing Phases 1-5 on their
existing merits, never because of a high win rate, a trader's claim, a short hot
streak, or recency. This matches the existing promotion bar in `ROADMAP.md` exactly.


## Known gap: Phase 8's "a broker's paper API" was never verified against a real broker

Added 2026-09-02, per a Path-to-Profitability Advisor review (see
docs/PATH_TO_PROFITABILITY_ADVISOR.md) that found "Robinhood" -- the
broker Jason has discussed using -- appeared nowhere in this document,
and Phase 8's "a broker's paper API" was never checked against any
specific broker's actual capabilities. A factual check
(docs/EXECUTION_BROKER_FEASIBILITY.md, full sources there) found:
Robinhood does support real NQ futures trading, but only for a human
tapping the mobile app -- its programmatic "Agentic Trading" API
(equities, options, crypto as of 2026-07) does not currently support
futures. Phases 8 and 10 cannot be built against Robinhood for NQ
specifically as things stand. Tradovate and NinjaTrader are the
established alternative with real futures APIs and existing
TradingView-webhook bridge tooling -- Phase 6's TradingView design
already fits that path unchanged. No phase, threshold, or promotion
criterion above has been changed by this finding -- it's recorded here
so Phase 8 isn't built later against a broker that can't do it, not as
a decision about which broker to actually use.
