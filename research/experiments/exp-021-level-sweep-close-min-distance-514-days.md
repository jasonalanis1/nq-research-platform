# exp-021 — Level Sweep Reversal, "close_min_distance", re-run on 514-research-day dataset

**Setup:** Level Sweep Reversal
**Variant:** close_min_distance
**Date:** 2026-08-20
**Sample Size:** 172 resolved trades
**Statistically Significant:** No (90% bootstrap CI on total R: -29.57R to +20.56R, spans zero)
**Status:** retest — re-run after the 2026-08-20 rolling-window fix added one research day (513 -> 514). Prior comparable result: exp-019 (173 trades, -0.014R). Essentially unchanged.

## Purpose

Not a new hypothesis or code change to the strategy itself — this re-run
exists purely because `src/data_fetch_databento.py`'s rolling-window bug
was fixed today (anchored to a fixed 2024-08-15 start instead of a
rolling "730 days back from now" window), which shifted the research
portion from 513 to 514 trading days. Re-running confirms the prior
result (exp-019) wasn't an artifact of the old, buggy data window.

This also incidentally re-verifies the newly-extracted
`generate_signals()` Signal-contract adapter (see
`src/strategy_contract.py`) produces the exact same signals as the
existing detection pipeline — confirmed separately, row-for-row, before
this backtest was run.

## Data used

`data/NQ_1min_databento_2026-08-20.csv` — 704,513 rows, 2024-08-14
(NY time) through 2026-08-19. Research portion: 514 trading days
(2024-08-15 -> 2026-04-06), holdout (116 days, 2026-04-07 onward)
correctly excluded throughout.

## Method

`src/detect_level_sweep.py close_min_distance` →
`src/backtest.py setups_level_sweep_close_min_distance.csv` →
`src/score_results.py backtest_results_level_sweep_close_min_distance.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_close_min_distance.csv`.

## Results (net of estimated costs)

- 174 signals, 172 resolved (2 unresolved).
- Win rate 43.0% (95% CI: 35.6%-50.4%).
- Average win +1.32R, average loss -1.03R.
- Expectancy **-0.021R** (profit factor 1.15, max drawdown -13.80R, total -3.69R).
- Bootstrap: 90% CI on total R is -29.57R to +20.56R (includes zero —
  not statistically significant). 39.9% of 172-future-trade simulations
  ended net profitable.

## Interpretation

**Essentially unchanged from exp-019** (-0.014R at 173 trades → -0.021R
at 172 trades) — a difference well within noise, not a meaningful shift.
One extra research day and one fewer resolved trade produced almost the
identical read: still negative, still not statistically distinguishable
from zero. This is a good sign for the pipeline's stability (the one-day
data correction didn't flip or meaningfully move the result) but doesn't
change the conclusion — this variant still shows no research-only edge.

## Next step

No change to prior guidance: this variant remains a weak candidate.
Continue tracking as more real data accumulates; no reason to prioritize
further investigation of this specific variant over `full_bar_range`
(see exp-022) based on this result.
