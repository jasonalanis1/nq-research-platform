# exp-005 — Level Sweep Reversal, first REAL-data run

**Date:** 2026-08-16
**Status:** retest (tiny sample — 13 trades — not yet a trustworthy verdict)

## Hypothesis

Same as exp-003: price sweeping through a meaningful reference level
(yesterday's high/low, or today's pre-market high/low) near the 8:30 NY
open, then closing back beyond that level, signals a tradeable reversal.
See `research/setups/level-sweep-reversal.md`.

## Data used

Same real dataset as exp-004: `data/NQ_1min_2026-08-16.csv`, 2026-07-19
through 2026-08-14 (~24 trading days), pulled from Yahoo Finance.

## Method

`src/detect_level_sweep.py` → `src/backtest.py setups_level_sweep.csv` →
`src/score_results.py backtest_results_level_sweep.csv` →
`src/confidence_analysis.py backtest_results_level_sweep.csv`. No
parameter changes from exp-003 — same setup logic, only the underlying
data changed from synthetic to real.

## Results (net of estimated costs)

- 17 signals detected (3 days skipped for missing prior-day/pre-market
  data, 3 days with no sweep+reversal).
- 13 of 17 resolved; win rate 7.7% (95% CI: 0.0%-22.2%) — only 1 winner.
- Average win +1.83R, average loss -1.04R.
- Expectancy -0.822R, profit factor 0.54, max drawdown -9.52R, total -10.69R.
- Bootstrap: 0.0% of 100-future-trade simulations ended net profitable.

## Interpretation

Unprofitable on real data too, and more decisively negative than exp-004
was positive — 0% of bootstrap simulations came out ahead. But the sample
is still very small (13 resolved trades), and just as importantly: this
is Claude's first pass at translating Jason's video reference into
concrete rules (level selection, confirmation logic), not something
Jason has validated against real price action himself yet. A weak result
here could mean "the pattern doesn't have an edge" OR "the rules as coded
don't quite match what Jason actually watches for" — those need to be
told apart before drawing a real conclusion, and only Jason can do that
by reviewing `research/setups/level-sweep-reversal.md` against what he'd
actually trade.

## Next step

Jason to review `research/setups/level-sweep-reversal.md` against real
charts/his own judgment and flag anything the coded rules got wrong
(e.g. which level gets used, how "close back beyond the level" is
defined, the watch window). Re-test as exp-006+ after any rule changes,
and keep accumulating more real trading days in the meantime.
