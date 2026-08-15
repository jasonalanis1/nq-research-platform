# Experiments Index

The running scoreboard of everything tested. This file is the source of
truth for what's been tried — update it every time a backtest variant
runs, and never overwrite a previous row's results (add a new row/file
instead, even if it's a re-run of a similar idea).

| ID | Hypothesis | Date | Win Rate | Expectancy | Verdict |
|----|-----------|------|----------|------------|---------|
| exp-001 | Opening Range Breakout (15-min range, 60-min watch, 1x-range target) has an edge at the NQ 8:30 NY open | 2026-08-15 | 37.0% | -0.29R (gross, no costs) | retest — pipeline validation only, see notes |
| exp-002 | Same as exp-001, now with commission/slippage cost modeling + bootstrap confidence range added to the pipeline | 2026-08-16 | 37.0% (95% CI: 23.0%-50.9%) | -0.31R (net of estimated costs) | retest — pipeline validation only, see notes |
| exp-003 | Level Sweep Reversal (support/resistance from prior-day + pre-market highs/lows, close-back confirmation) has an edge at the NQ 8:30 NY open | 2026-08-16 | 2.6% (95% CI: 0.0%-7.7%) | -0.68R (net of estimated costs) | retest — pipeline validation only, see notes |

**Verdict key:** `keep` (worth pursuing further) · `kill` (edge not
supported, drop it) · `retest` (inconclusive as tested — data, sample
size, or setup definition needs to change before this row means
anything)

**Note on exp-001:** this was run on SYNTHETIC (fake, random-walk) data
as a way to prove the backtest pipeline itself works correctly, not as a
real test of the ORB pattern. A random dataset showing no edge is the
*correct* result. This row should not be read as "ORB doesn't work" —
it means "the code correctly found no edge in data that has none." Real
verdict pending: real data + (likely) Jason's actual setup definition
rather than this placeholder.
