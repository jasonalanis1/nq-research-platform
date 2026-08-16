# exp-007 — Level Sweep Reversal, "close_min_distance" confirmation + video-derived target

**Date:** 2026-08-16
**Status:** retest (tiny sample — 15 trades — one of three confirmation variants being compared, no winner picked yet)

## Hypothesis

Same as exp-006 (video-derived TARGET_R_MULTIPLE = 1.35), but using the
**"close_min_distance"** confirmation variant: the confirming bar's close
must clear the level by at least MIN_CONFIRM_DISTANCE_POINTS (5.0 points
— an arbitrary illustrative placeholder, not derived from data), instead
of any close back over the line counting. See
`research/setups/level-sweep-reversal.md` for the full definition.

## Data used

Same real dataset as exp-004/exp-005/exp-006:
`data/NQ_1min_2026-08-16.csv`, 2026-07-19 through 2026-08-14 (~24 trading
days).

## Method

`src/detect_level_sweep.py close_min_distance` →
`src/backtest.py setups_level_sweep_close_min_distance.csv` →
`src/score_results.py backtest_results_level_sweep_close_min_distance.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_close_min_distance.csv`.

## Results (net of estimated costs)

- 16 signals, 15 resolved (1 unresolved).
- Win rate 66.7% (95% CI: 42.8%-90.5%).
- Average win +1.33R, average loss -1.03R.
- Expectancy +0.545R, profit factor 4.33, max drawdown -2.04R, total +8.18R.
- Bootstrap: 100.0% of 100-future-trade simulations ended net profitable.

## Interpretation

The strongest of the three variants tested today (vs. exp-006's +0.132R
and exp-008's +0.238R) — highest win rate, smallest drawdown, and every
bootstrap simulation ended profitable. Tempting to call this the winner,
but per Jason's explicit request, no variant is being picked yet — 15
trades is a small enough sample that "filtering out marginal closes
happened to help on this particular 24-day window" and "filtering out
marginal closes is genuinely better" aren't yet distinguishable. Also
worth noting: MIN_CONFIRM_DISTANCE_POINTS (5.0) was picked arbitrarily,
not tuned — a different threshold could look better or worse than this.

## Next step

No winner being picked between the three confirmation variants yet, per
Jason's request — accumulate more real trading days and revisit all
three together once there's a larger sample. If this variant continues
to lead as more data comes in, MIN_CONFIRM_DISTANCE_POINTS itself would
be worth testing at a few different values rather than trusting the
current placeholder of 5.0 points.
