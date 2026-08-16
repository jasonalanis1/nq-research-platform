# exp-013 — Opening Range Breakout, 2-year Databento real data

**Date:** 2026-08-16
**Status:** retest (493 trades — large sample, reasonably trustworthy for this specific placeholder setup)

## Hypothesis

Same placeholder ORB definition as exp-001/002/004/009. This run's
purpose: does exp-009's -0.028R (125 trades, 6 months) hold up with
~4x more data?

## Data used

`data/NQ_1min_databento_2026-08-16.csv`, re-pulled with `LOOKBACK_DAYS`
increased from 182 to 730 — 698,873 rows, 2024-08-15 through 2026-08-14
(~2 years). Before pulling, Jason asked for a cost quote first via
Databento's `metadata.get_cost()` endpoint (no charge to check): ~$2.55
for 2 years of `ohlcv-1m`, trivial against his ~$124 remaining balance.
Databento flagged a few more "reduced quality" days across this longer
window (2024-09-18, 2025-09-17, 2025-09-24, possibly others) — noted, not
acted on.

## Method

`src/detect_setups.py` → `src/backtest.py` → `src/score_results.py` →
`src/confidence_analysis.py`. No parameter changes from exp-009 — same
setup logic, only the underlying data window changed (6mo → 2yr).

## Results (net of estimated costs)

- 503 signals, 493 resolved (10 unresolved).
- Win rate 50.5% (95% CI: 46.1%-54.9%) — tight range now.
- Average win +0.88R, average loss -1.02R.
- Expectancy -0.062R, profit factor 0.82, max drawdown -55.39R, total -30.55R.
- Bootstrap: only 6.6% of 493-future-trade simulations ended net profitable.

## Interpretation

Confirms and sharpens exp-009's negative read — with a large, tight
sample, this placeholder ORB looks clearly unprofitable, not just
"roughly breakeven." Consistent story across all three real-data ORB
runs now (exp-004 optimistic on 19 trades → exp-009 flat on 125 → exp-013
clearly negative on 493): more data kept revealing a worse picture, the
opposite of what you'd want to see if there were a real edge being
obscured by noise.

## Next step

No further action planned for the ORB placeholder — treat it as settled
(clearly no edge as currently defined) and keep it only as a reference
point for comparison, not as something to keep re-testing.
