# exp-011 — Level Sweep Reversal, "close_min_distance" confirmation, 6-month Databento data

**Date:** 2026-08-16
**Status:** retest (63 trades — big enough to take seriously; still one of three variants being compared, no winner picked yet)

## Hypothesis

Same as exp-007 (close_min_distance confirmation + 1.35x-risk
video-derived target), re-tested on ~6 months of real Databento data
instead of Yahoo's ~24-day window.

## Data used

Same Databento dataset as exp-009/exp-010:
`data/NQ_1min_databento_2026-08-16.csv`, 2026-02-15 through 2026-08-14
(~6 months).

## Method

`src/detect_level_sweep.py close_min_distance` →
`src/backtest.py setups_level_sweep_close_min_distance.csv` →
`src/score_results.py backtest_results_level_sweep_close_min_distance.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_close_min_distance.csv`.

## Results (net of estimated costs)

- 64 signals, 63 resolved (1 unresolved).
- Win rate 46.0% (95% CI: 33.7%-58.3%).
- Average win +1.32R, average loss -1.03R.
- Expectancy +0.054R, profit factor 1.45, max drawdown -10.11R, total +3.38R.
- Bootstrap: 69.8% of 100-future-trade simulations ended net profitable.

## Interpretation

Stayed positive, but compressed hard — exp-007's +0.545R (15 trades)
came down to +0.054R (63 trades), barely above breakeven. Still the best
of the three variants on this larger sample (see exp-010/exp-012), same
ranking as the small-sample results, but the MAGNITUDE of the edge looks
far more marginal than exp-007 suggested. A 69.8% chance of net
profitability over the next 100 trades is well short of the near-100%
the small sample implied.

## Next step

Still no winner being picked between the three variants — see the
updated comparison table in `research/setups/level-sweep-reversal.md`.
This variant remains the most promising of the three, but "most
promising of three weak-to-marginal results" is a different claim than
"promising" on its own — worth being explicit about that distinction
with Jason.
