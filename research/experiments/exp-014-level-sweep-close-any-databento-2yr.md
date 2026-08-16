# exp-014 — Level Sweep Reversal, "close_any" confirmation, 2-year Databento data

**Date:** 2026-08-16
**Status:** retest (237 trades — large sample; still one of three variants being compared, no winner picked yet)

## Hypothesis

Same as exp-006/exp-010 (close_any confirmation + 1.35x-risk video-derived
target), re-tested on ~2 years of real Databento data instead of the
6-month window.

## Data used

Same 2-year Databento pull as exp-013: `data/NQ_1min_databento_2026-08-16.csv`,
2024-08-15 through 2026-08-14.

## Method

`src/detect_level_sweep.py close_any` →
`src/backtest.py setups_level_sweep_close_any.csv` →
`src/score_results.py backtest_results_level_sweep_close_any.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_close_any.csv`.

## Results (net of estimated costs)

- 240 signals, 237 resolved (3 unresolved).
- Win rate 42.6% (95% CI: 36.3%-48.9%).
- Average win +1.30R, average loss -1.08R.
- Expectancy -0.063R, profit factor 1.36, max drawdown -24.21R, total -14.92R.
- Bootstrap: 19.9% of 237-future-trade simulations ended net profitable.

## Interpretation

Stayed negative and got a tighter, more convincing negative read (-0.063R
vs exp-010's -0.052R on 68 trades) — consistent story, not a reversal.
Of the three confirmation variants, close_any remains the weakest, now
more confidently so.

## Next step

Still no winner being picked between the three variants — see the
updated comparison table in `research/setups/level-sweep-reversal.md`.
close_any is looking increasingly like it should be dropped from
consideration given two consecutive negative results at growing sample
sizes, but that call is Jason's to make.
