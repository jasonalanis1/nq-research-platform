# exp-006 — Level Sweep Reversal, "close_any" confirmation + video-derived target

**Date:** 2026-08-16
**Status:** retest (tiny sample — 16 trades — one of three confirmation variants being compared, no winner picked yet)

## Hypothesis

Same core idea as exp-003/exp-005, but two deliberate changes made after
Jason reviewed the setup definition:

1. **Target rule changed.** The prior version targeted the opposite level
   (support swept → target resistance). Reviewing
   `research/raw/2026-08-16-video-reference-chart.md` against that rule
   showed a mismatch: the video's actual trade targeted only 27 points
   from a 20-point risk (~1.35x risk), not the far opposite level (price
   later ran 8-10x further, but that was what happened after the trade,
   not the target itself). This run uses TARGET_R_MULTIPLE = 1.35,
   Jason's call based on that one concrete data point.
2. **Confirmation rule is now one of three variants**, since Jason
   doesn't yet have a strong feel for which is right and asked to compare
   rather than guess. This experiment uses **"close_any"** — the
   original rule, any close back beyond the level counts (unchanged from
   exp-003/exp-005).

See `research/setups/level-sweep-reversal.md` for the full current
definition.

## Data used

Same real dataset as exp-004/exp-005: `data/NQ_1min_2026-08-16.csv`,
2026-07-19 through 2026-08-14 (~24 trading days).

## Method

`src/detect_level_sweep.py close_any` →
`src/backtest.py setups_level_sweep_close_any.csv` →
`src/score_results.py backtest_results_level_sweep_close_any.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_close_any.csv`.

## Results (net of estimated costs)

- 17 signals, 16 resolved (1 unresolved).
- Win rate 50.0% (95% CI: 25.5%-74.5%).
- Average win +1.32R, average loss -1.06R.
- Expectancy +0.132R, profit factor 2.51, max drawdown -4.17R, total +2.11R.
- Bootstrap: 85.0% of 100-future-trade simulations ended net profitable.

## Interpretation

Flipped from strongly negative (exp-005: -0.822R) to positive. The
target-rule change looks like the dominant factor — exp-005's huge
average winner (+1.83R) paired with a near-zero win rate (7.7%) is
exactly the fingerprint of a target that's usually too far away to reach;
a much closer target naturally lifts win rate. Still only 16 trades, so
this is "promising, needs more data," not confirmed. Compare directly
against exp-007 (close_min_distance) and exp-008 (full_bar_range), run on
the identical data and target rule — the only difference between the
three is the confirmation logic.

## Next step

No winner being picked between the three confirmation variants yet, per
Jason's request — accumulate more real trading days and revisit all
three together once there's a larger sample.
