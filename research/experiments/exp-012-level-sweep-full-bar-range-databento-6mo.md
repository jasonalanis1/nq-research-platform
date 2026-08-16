# exp-012 — Level Sweep Reversal, "full_bar_range" confirmation, 6-month Databento data

**Date:** 2026-08-16
**Status:** retest (60 trades — big enough to take seriously; still one of three variants being compared, no winner picked yet)

## Hypothesis

Same as exp-008 (full_bar_range confirmation + 1.35x-risk video-derived
target), re-tested on ~6 months of real Databento data instead of
Yahoo's ~24-day window.

## Data used

Same Databento dataset as exp-009/exp-010/exp-011:
`data/NQ_1min_databento_2026-08-16.csv`, 2026-02-15 through 2026-08-14
(~6 months).

## Method

`src/detect_level_sweep.py full_bar_range` →
`src/backtest.py setups_level_sweep_full_bar_range.csv` →
`src/score_results.py backtest_results_level_sweep_full_bar_range.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_full_bar_range.csv`.

## Results (net of estimated costs)

- 61 signals, 60 resolved (1 unresolved).
- Win rate 45.0% (95% CI: 32.4%-57.6%).
- Average win +1.32R, average loss -1.02R.
- Expectancy +0.033R, profit factor 1.11, max drawdown -6.01R, total +1.95R.
- Bootstrap: 60.9% of 100-future-trade simulations ended net profitable.

## Interpretation

Stayed positive but, like exp-011, compressed sharply from exp-008's
+0.238R (15 trades) down to +0.033R (60 trades) — barely above
breakeven, and profit factor (1.11) is now the weakest of the two
still-positive variants. Middle-of-the-pack, same ranking as before
(better than close_any, worse than close_min_distance).

## Next step

Still no winner being picked between the three variants — see the
updated comparison table in `research/setups/level-sweep-reversal.md`.
