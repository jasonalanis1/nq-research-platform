# exp-003 — Level Sweep Reversal, synthetic-data baseline

**Date:** 2026-08-16
**Status:** retest (pipeline validation only, not a real edge test)

## Hypothesis

Price sweeping through a meaningful reference level (yesterday's
high/low, or today's pre-market high/low) near the 8:30 NY open, then
closing back beyond that level, signals a tradeable reversal. See
`research/setups/level-sweep-reversal.md` for the full definition and
where this idea came from.

## Data used

Same synthetic dataset as exp-001/exp-002 — 90 fake trading days, random
walk, NOT real market data.

## Method

`src/detect_level_sweep.py` → `src/backtest.py setups_level_sweep.csv` →
`src/score_results.py backtest_results_level_sweep.csv` →
`src/confidence_analysis.py backtest_results_level_sweep.csv`.

## Results (net of estimated costs)

- 89 days scanned (first day excluded, no prior day to reference), 48
  signals (26 long, 22 short), 41 days with no sweep+reversal.
- 38 of 48 resolved; win rate 2.6% (95% CI: 0.0%-7.7%) — only 1 winner.
- Average win +20.32R, average loss -1.25R (very asymmetric — makes
  sense, since the target here is often a distant opposite level rather
  than a fixed multiple).
- Expectancy -0.684R, profit factor 0.36, max drawdown -32.02R.
- Bootstrap projection of 100 more trades: only 4.5% of simulated futures
  ended up net profitable.

## Interpretation

Unprofitable on synthetic data, as expected/correct — same conclusion as
exp-001/exp-002, this data has no real structure for any setup to find
an edge in. What's notable: this setup's *shape* is structurally
different from ORB's (rare, huge wins vs. ORB's more frequent, modest
wins) even though both fail on the same underlying random data. That's a
useful sanity check — it means the pipeline is genuinely modeling each
setup's own mechanics rather than just producing generic/identical
output regardless of input.

## Next step

Real data is even more important for this setup than for ORB, since a
"prior day high/low" and "pre-market range" only mean something on real
market structure — on this narrow synthetic window they're a weak proxy
at best. Re-test (as exp-004 or later, never overwriting this entry) once
real data is flowing.
