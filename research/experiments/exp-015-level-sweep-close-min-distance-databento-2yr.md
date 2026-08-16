# exp-015 — Level Sweep Reversal, "close_min_distance" confirmation, 2-year Databento data

**Date:** 2026-08-16
**Status:** retest (221 trades — large sample; still one of three variants being compared, no winner picked yet)

## Hypothesis

Same as exp-007/exp-011 (close_min_distance confirmation + 1.35x-risk
video-derived target), re-tested on ~2 years of real Databento data
instead of the 6-month window.

## Data used

Same 2-year Databento pull as exp-013/exp-014:
`data/NQ_1min_databento_2026-08-16.csv`, 2024-08-15 through 2026-08-14.

## Method

`src/detect_level_sweep.py close_min_distance` →
`src/backtest.py setups_level_sweep_close_min_distance.csv` →
`src/score_results.py backtest_results_level_sweep_close_min_distance.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_close_min_distance.csv`.

## Results (net of estimated costs)

- 224 signals, 221 resolved (3 unresolved).
- Win rate 45.7% (95% CI: 39.1%-52.3%).
- Average win +1.32R, average loss -1.03R.
- Expectancy +0.043R, profit factor 1.33, max drawdown -14.85R, total +9.42R.
- Bootstrap: 70.8% of 221-future-trade simulations ended net profitable.

## Interpretation

Held up well — +0.043R at 221 trades is very close to exp-011's +0.054R
at 63 trades, not a further collapse like the earlier 24-day→6-month
jump showed. This is the first sign of the result actually stabilizing
rather than continuing to shrink toward zero as sample size grows.
Still the strongest of the three variants across every sample size
tested so far.

## Next step

Still no winner being picked between the three variants — see the
updated comparison table in `research/setups/level-sweep-reversal.md`.
Given this variant's stability across 15 → 63 → 221 trades, it may be
worth a more focused round of attention (e.g. does it hold up
out-of-sample on future data as it comes in, or does performance vary a
lot by month/regime) rather than treating all three variants as equally
open questions going forward.
