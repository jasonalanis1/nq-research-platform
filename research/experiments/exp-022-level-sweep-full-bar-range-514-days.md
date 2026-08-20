# exp-022 — Level Sweep Reversal, "full_bar_range", re-run on 514-research-day dataset

**Setup:** Level Sweep Reversal
**Variant:** full_bar_range
**Date:** 2026-08-20
**Sample Size:** 150 resolved trades
**Statistically Significant:** No (90% bootstrap CI on total R: -23.49R to +23.44R, spans zero)
**Status:** retest — re-run after the 2026-08-20 rolling-window fix added one research day (513 -> 514). Prior comparable result: exp-020 (151 trades, +0.008R). Essentially unchanged, now dead flat.

## Purpose

Same purpose as exp-021: re-run to confirm the prior result (exp-020)
wasn't an artifact of the old, buggy rolling-window data fetch, and to
incidentally re-verify the new `generate_signals()` Signal-contract
adapter (`src/strategy_contract.py`) against this variant too.

## Data used

Same as exp-021: `data/NQ_1min_databento_2026-08-20.csv`, 514 research
trading days (2024-08-15 -> 2026-04-06), holdout (116 days) excluded.

## Method

`src/detect_level_sweep.py full_bar_range` →
`src/backtest.py setups_level_sweep_full_bar_range.csv` →
`src/score_results.py backtest_results_level_sweep_full_bar_range.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_full_bar_range.csv`.

## Results (net of estimated costs)

- 156 signals, 150 resolved (6 unresolved).
- Win rate 44.0% (95% CI: 36.1%-51.9%).
- Average win +1.32R, average loss -1.04R.
- Expectancy **-0.001R** (profit factor 1.07, max drawdown -12.71R, total -0.13R).
- Bootstrap: 90% CI on total R is -23.49R to +23.44R (includes zero —
  not statistically significant). 48.8% of 150-future-trade simulations
  ended net profitable — a coin flip.

## Interpretation

**Essentially unchanged from exp-020** (+0.008R at 151 trades → -0.001R
at 150 trades) — both numbers round to "flat," well within noise of each
other. The one-day data correction pushed this specific point estimate
from barely-positive to barely-negative, which on its own sounds like a
meaningful flip, but given the sample size and how close both values are
to zero, this is exactly the kind of noise-level movement expected for a
result with no real edge. Not a new finding — confirms the prior
breakeven read, doesn't contradict it.

## Next step

No change to prior guidance. Between the two variants, neither shows a
research-only edge worth acting on. `close_min_distance` (exp-021,
-0.021R) and `full_bar_range` (exp-022, -0.001R) are now both at or
below breakeven — the "close_min_distance was best" ranking from earlier
sessions no longer clearly holds now that both are essentially flat to
slightly negative.
