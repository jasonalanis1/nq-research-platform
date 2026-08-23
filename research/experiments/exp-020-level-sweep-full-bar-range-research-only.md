# exp-020 — Level Sweep Reversal, "full_bar_range", first genuinely holdout-respecting test

**Setup:** Level Sweep Reversal
**Variant:** full_bar_range
**Date:** 2026-08-16
**Sample Size:** 151 resolved trades
**Statistically Significant:** No (90% bootstrap CI on total R: -21.83R to +24.90R, spans zero)
**Status:** retest (edge shrank to roughly breakeven once holdout period excluded — see interpretation)

## Hypothesis

Same as exp-008/012/016/018 (full_bar_range confirmation + 1.35x-risk
video-derived target). Same purpose as exp-019: exp-016/018 both
predate `src/data_holdout.py` and unknowingly included the 112
most-recent trading days that are now holdout. This is the first
genuinely research-only test of this variant.

## Data used

Same as exp-019: `data/NQ_1min_databento_2026-08-16.csv`. Greg checked
for new data first — none was available (identical 698,873 rows, same
date range). Research window: 2024-08-15 → 2026-04-06, 513 trading
days, with the 112-day holdout (2026-04-07 onward) automatically
excluded by the now-consolidated `src/data_loader.py`.

## Method

`src/detect_level_sweep.py full_bar_range` →
`src/backtest.py setups_level_sweep_full_bar_range.csv` →
`src/score_results.py backtest_results_level_sweep_full_bar_range.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_full_bar_range.csv`.
Console output confirmed the holdout boundary was applied at every step.

## Results (net of estimated costs)

- 157 signals, 151 resolved (6 unresolved).
- Win rate 44.4% (95% CI: 36.4%-52.3%).
- Average win +1.32R, average loss -1.04R.
- Expectancy **+0.008R** (profit factor 1.10, max drawdown -13.77R, total +1.21R).
- Bootstrap: 90% CI on total R is -21.83R to +24.90R (includes zero —
  not statistically significant). 51.6% of 151-future-trade simulations
  ended net profitable — essentially a coin flip.

## Interpretation

Shrank from +0.042R (exp-016/018, including the now-holdout period) to
+0.008R here — essentially flat/breakeven, and the weakest result this
variant has shown yet. Same pattern as exp-019 (close_min_distance):
some of the apparent edge was concentrated in the excluded recent
months. `full_bar_range` is now barely distinguishable from a coin flip
on research-only data.

## Next step

Same as exp-019. Between the two, neither currently shows a
research-only edge worth acting on — `close_min_distance` is actually
negative here, `full_bar_range` is roughly breakeven. Continue
accumulating real research-period data (new trading days will land
before the holdout boundary moves, since it's fixed) before drawing
firmer conclusions.

## Note on multiple-testing history

This run (and exp-019) is the fifth round of testing on this
close_min_distance / full_bar_range comparison, following four earlier
rounds (exp-006-008, exp-010-012, exp-014-016, exp-017-018) on
substantially overlapping data, during which a third variant
(close_any) was dropped as weakest. The "not statistically significant"
bootstrap CI reported above treats this as an isolated test and does
not account for that prior selection history. The practical verdict is
unchanged either way (both were already not significant) — this note
exists for the record's honesty, not because it changes the conclusion.
