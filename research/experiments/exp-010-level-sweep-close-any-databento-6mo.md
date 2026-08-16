# exp-010 — Level Sweep Reversal, "close_any" confirmation, 6-month Databento data

**Date:** 2026-08-16
**Status:** retest (68 trades — big enough to take seriously; still one of three variants being compared, no winner picked yet)

## Hypothesis

Same as exp-006 (close_any confirmation + 1.35x-risk video-derived
target), re-tested on ~6 months of real Databento data instead of
Yahoo's ~24-day window, to see whether exp-006's positive result holds
up with a much bigger sample.

## Data used

Same Databento dataset as exp-009: `data/NQ_1min_databento_2026-08-16.csv`,
2026-02-15 through 2026-08-14 (~6 months), including the timestamp
parsing (DST) bugfix described in exp-009.

## Method

`src/detect_level_sweep.py close_any` →
`src/backtest.py setups_level_sweep_close_any.csv` →
`src/score_results.py backtest_results_level_sweep_close_any.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_close_any.csv`.

## Results (net of estimated costs)

- 69 signals, 68 resolved (1 unresolved).
- Win rate 42.6% (95% CI: 30.9%-54.4%).
- Average win +1.31R, average loss -1.07R.
- Expectancy -0.052R, profit factor 1.41, max drawdown -9.23R, total -3.50R.
- Bootstrap: 32.6% of 100-future-trade simulations ended net profitable.

## Interpretation

Flipped negative — exp-006's +0.132R (16 trades) did not hold up at 68
trades. Same pattern as exp-009 (ORB): the small-sample result was
optimistic. Of the three confirmation variants, close_any is now the
weakest on the larger sample (see exp-011/exp-012 for the other two).

## Next step

Still no winner being picked between the three variants — see the
updated comparison table in `research/setups/level-sweep-reversal.md`.
The overall picture across all three on 6 months of data is much less
encouraging than the initial ~24-day results suggested; worth discussing
with Jason whether any variant is still worth pursuing, or whether the
underlying idea needs a bigger rethink (level selection, watch window,
etc.) rather than just tuning the confirmation rule.
