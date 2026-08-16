# exp-008 — Level Sweep Reversal, "full_bar_range" confirmation + video-derived target

**Date:** 2026-08-16
**Status:** retest (tiny sample — 15 trades — one of three confirmation variants being compared, no winner picked yet)

## Hypothesis

Same as exp-006/exp-007 (video-derived TARGET_R_MULTIPLE = 1.35), but
using the **"full_bar_range"** confirmation variant: the ENTIRE
confirming bar (not just its close) must be back beyond the level — its
low (support case) or high (resistance case) also cleared the level.
This is strictly stronger than "close_any" and, by construction, can
never fire on the same bar that did the sweep — confirmation always
comes on a later bar. See `research/setups/level-sweep-reversal.md` for
the full definition.

## Data used

Same real dataset as exp-004/exp-005/exp-006/exp-007:
`data/NQ_1min_2026-08-16.csv`, 2026-07-19 through 2026-08-14 (~24 trading
days).

## Method

`src/detect_level_sweep.py full_bar_range` →
`src/backtest.py setups_level_sweep_full_bar_range.csv` →
`src/score_results.py backtest_results_level_sweep_full_bar_range.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_full_bar_range.csv`.

## Results (net of estimated costs)

- 16 signals, 15 resolved (1 unresolved).
- Win rate 53.3% (95% CI: 28.1%-78.6%).
- Average win +1.33R, average loss -1.01R.
- Expectancy +0.238R, profit factor 1.94, max drawdown -3.02R, total +3.58R.
- Bootstrap: 98.1% of 100-future-trade simulations ended net profitable.

## Interpretation

Landed between exp-006 (+0.132R) and exp-007 (+0.545R) — stricter than
"close_any" but less selective than "close_min_distance" turned out to
be on this data. Same caveat as the other two: 15 trades is too small a
sample to declare this variant better or worse than the others yet.

## Next step

No winner being picked between the three confirmation variants yet, per
Jason's request — accumulate more real trading days and revisit all
three together once there's a larger sample.
