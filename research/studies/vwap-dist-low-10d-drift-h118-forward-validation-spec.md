# VWAP-Distance-Low, 10-Day Drift -- H118 Forward Validation Spec

Frozen 2026-09-09, immediately after H118 cleared the Integrity Gate
(PASS). Phase 6-7 per docs/RESEARCH_INTEGRITY_PROTOCOL.md: Forward
Validation is live/forward data, paper only, ongoing -- not a single
backtest run. This spec freezes exactly what gets tracked and how,
before any forward signal has fired, so nothing can be tuned in
hindsight once real (if paper) results start coming in.

## What is being tracked
Identical, unmodified definition to Discovery/Validation/Holdout: on
any trading day whose vwap_dist_vs_atr (per src/market_state_primitives_v2.py)
falls in the LOW tercile using the bucket edges FROZEN FROM DISCOVERY
([-inf, -0.0460, 0.1471, inf] -- never refit, not even now), open a
paper LONG position at that day's RTH reference close, and close it at
the RTH reference close 10 trading days later. No stop, no target. One
round-trip cost assumed (ROUND_TRIP_COST_POINTS) at exit. No position
sizing decision is in scope here -- this only tracks the raw signal's
R-multiple and point outcome, exactly like every prior stage.

## Data boundary
Forward Validation only uses data from 2026-09-09 (today) forward --
never backtested, only accumulated day by day as it actually happens.
This is NOT a slice of existing historical data (that would just be
more Holdout, and the Holdout budget is separate and already partly
spent). A forward signal cannot be evaluated until 10 trading days
after it fires (the exit is 10 trading days out) -- so no result exists
until roughly mid-to-late October 2026 at the earliest for the first
signal.

## How it runs
A daily check (src/forward_validate_h118_daily.py) computes the current
vwap_dist_vs_atr value from the latest available data, using bucket
edges frozen from Discovery, and appends a row to
research/forward_validation/h118_forward_log.jsonl whenever: (a) a new
signal day occurs (low tercile), or (b) an existing open paper position
reaches its 10-trading-day exit. This needs to be run once per trading
day -- recommended as a scheduled daily task rather than manual, since
a missed day just means a missed signal check, not corrupted data (no
retroactive signal creation).

## Promotion implication
Per the six-state ladder (REJECTED -> PROMISING -> VALIDATION CANDIDATE
-> HOLDOUT PASSED -> FORWARD VALIDATION -> PAPER VERIFIED), enough
forward signals resolving with the same sign and clearing the existing
90% CI + 0.05R bar moves H118 to PAPER VERIFIED -- still not
live-authorized on its own; that remains a separate, explicit decision
requiring Jason's sign-off regardless of any statistical result, per
the standing exception for anything touching real capital.

## Per protocol
No retuning of the definition based on forward results as they trickle
in. If early forward signals look bad, they are logged and reported
honestly, not discarded or reinterpreted. This is the same discipline
as every prior stage.
