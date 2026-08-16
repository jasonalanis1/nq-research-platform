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
| exp-004 | Same ORB placeholder as exp-001/002, first run on REAL Yahoo Finance data (~24 trading days) instead of synthetic | 2026-08-16 | 63.2% (95% CI: 41.5%-84.8%) | +0.206R (net of estimated costs) | retest — tiny sample (19 trades), see notes |
| exp-005 | Same Level Sweep Reversal as exp-003, first run on REAL Yahoo Finance data (~24 trading days) instead of synthetic | 2026-08-16 | 7.7% (95% CI: 0.0%-22.2%) | -0.822R (net of estimated costs) | retest — tiny sample (13 trades), see notes |
| exp-006 | Level Sweep Reversal, "close_any" confirmation + new video-derived target (1.35x risk, replacing "opposite level") | 2026-08-16 | 50.0% (95% CI: 25.5%-74.5%) | +0.132R (net of estimated costs) | retest — one of 3 confirmation variants being compared, no winner picked, see notes |
| exp-007 | Level Sweep Reversal, "close_min_distance" confirmation (close must clear level by 5pts) + video-derived target | 2026-08-16 | 66.7% (95% CI: 42.8%-90.5%) | +0.545R (net of estimated costs) | retest — one of 3 confirmation variants being compared, no winner picked, see notes |
| exp-008 | Level Sweep Reversal, "full_bar_range" confirmation (whole bar back beyond level) + video-derived target | 2026-08-16 | 53.3% (95% CI: 28.1%-78.6%) | +0.238R (net of estimated costs) | retest — one of 3 confirmation variants being compared, no winner picked, see notes |

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
