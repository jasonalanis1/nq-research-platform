# Bar-Level Behavior Study, Batch 1 -- Frozen Spec (exp-066/067/068)

## Status: FROZEN 2026-09-08, before any Discovery-slice number is looked at.

## Where this came from

Jason redirected the project's mission (2026-09-08): instead of "find a
profitable strategy," discover repeatable market behaviors at the level
of individual bars, determine the conditions under which they occur,
and test whether a strategy can exploit them -- market behavior ->
condition -> strategy -> trade -> measured outcome. The Path-to-
Profitability Advisor reviewed this redirection and flagged the real
risk: candle/bar patterns are a large, loosely-bounded hypothesis space
(dozens of possible shapes), exactly what this project's no-shotgun
rule exists to prevent. Its fix, adopted here: pre-register a SMALL
FIXED LIST (3, not 20) with exact mechanical definitions, tested as ONE
joint batch with a shared search_batch_id, before looking at any
result.

## Scope discipline (binding)

Exactly 3 behaviors below. No 4th pattern gets added because these 3
didn't work. If none clear Step 1, this batch is closed for good, same
no-retuning discipline as every other line in this project. All 3 use
DAILY bars (not intraday) -- this project's existing daily-resolution
convention (compute_daily_ref_closes / get_reference_close, the 4pm ET
reference close already used throughout), reusing infra rather than
building new intraday plumbing. "Key levels" reuse the prior trading
day's high/low, already computed in this project's own daily OHLC
convention (trend_structure.py's groupby-agg pattern) -- not the
premarket-session levels detect_level_sweep.py uses, to keep this a
clean daily-bar-only test with no new intraday code.

Target/forward variable for all 3 (same as every daily-resolution study
in this project): the sign and magnitude of the NEXT full trading day's
close-to-close log return (compute_daily_log_returns, reused
unmodified).

## The 3 frozen behaviors

**exp-066: Bearish rejection at resistance (long upper wick).**
Day T's upper wick (High - max(Open, Close)) is >= 2.0x its body
(|Close - Open|), AND Day T's High >= prior day's High (price reached
into resistance before rejecting). Predicted direction: NEXT day's
return should be negative (rejection => expect pullback).
Test statistic: mean next-day log return on days meeting this
condition. Statistically credible = 90% bootstrap CI entirely BELOW
zero.

**exp-067: Bullish rejection at support (long lower wick).**
Mirror image: Day T's lower wick (min(Open, Close) - Low) is >= 2.0x
its body, AND Day T's Low <= prior day's Low. Predicted direction:
NEXT day's return should be positive.
Statistically credible = 90% bootstrap CI entirely ABOVE zero.

**exp-068: Failed breakout (large-range day followed by opposite-
direction day).**
Day T's range (High - Low) is >= 1.5x its own trailing 20-day average
daily range (frozen threshold, structural choice -- not tuned against
results), AND Day T closes in one direction (Close > Open = "up day",
or Close < Open = "down day"). Day T+1 closes in the OPPOSITE direction
from Day T (a literal failure to follow through). Predicted direction:
Day T+2's return should continue the REVERSAL implied by Day T+1 (i.e.,
same sign as Day T+1's close-to-open direction, opposite of Day T's).
Statistically credible = 90% bootstrap CI on Day T+2's mean return,
signed to the predicted direction, entirely above zero.

Edge case: if T, T+1, T+2 aren't all valid/available trading days
(missing data, or crossing the Discovery/Validation boundary), that
instance is dropped and the drop count disclosed.

## Statistical gate

Step 1 only (no costs, no trade construction) -- same gate as every
other single-condition test in this project (exp-059 through exp-065).
Each of the 3 tested independently on the Discovery slice, but logged
under ONE shared search_batch_id in the ledger, so the ledger's own
batch-size field discloses that 3 simultaneous trials were run, not 1
-- readers of the ledger see the multiple-testing context directly
rather than each result looking like an isolated single test.

No costed Step 2 rule is built for anything that passes Step 1 without
a separate scoping/sign-off step (matching every prior line -- Step 1
passing means "worth designing a real rule for," not "done").

## What happens if all 3 fail

Per Jason's 2026-09-08 standing instruction (go for it, no check-in
needed unless $ or a 90%-bar pass), a clean 0-for-3 result on this
batch does not need to be reported before moving to the next thing --
logged, committed, and Claude + Advisor decide the next direction.
