# exp-016 — Level Sweep Reversal, "full_bar_range" confirmation, 2-year Databento data

**Date:** 2026-08-16
**Status:** retest (197 trades — large sample; still one of three variants being compared, no winner picked yet)

## Hypothesis

Same as exp-008/exp-012 (full_bar_range confirmation + 1.35x-risk
video-derived target), re-tested on ~2 years of real Databento data
instead of the 6-month window.

## Data used

Same 2-year Databento pull as exp-013/014/015:
`data/NQ_1min_databento_2026-08-16.csv`, 2024-08-15 through 2026-08-14.

## Method

`src/detect_level_sweep.py full_bar_range` →
`src/backtest.py setups_level_sweep_full_bar_range.csv` →
`src/score_results.py backtest_results_level_sweep_full_bar_range.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_full_bar_range.csv`.

## Results (net of estimated costs)

- 204 signals, 197 resolved (7 unresolved).
- Win rate 45.7% (95% CI: 38.7%-52.6%).
- Average win +1.32R, average loss -1.03R.
- Expectancy +0.042R, profit factor 1.19, max drawdown -13.77R, total +8.21R.
- Bootstrap: 69.2% of 197-future-trade simulations ended net profitable.

## Interpretation

Also held up well — +0.042R at 197 trades vs exp-012's +0.033R at 60
trades, essentially unchanged. Like exp-015, this is a sign of
stabilization rather than continued shrinkage. Now nearly tied with
close_min_distance (+0.043R) on this larger sample, closer than the
6-month gap between them suggested.

## Next step

Still no winner being picked between the three variants — see the
updated comparison table in `research/setups/level-sweep-reversal.md`.
close_min_distance and full_bar_range are now close enough to each
other that picking between them on expectancy alone isn't very
meaningful yet; other factors (which one matches Jason's actual
real-time read of price action, trade frequency, drawdown shape) may
matter more than the small expectancy gap.
