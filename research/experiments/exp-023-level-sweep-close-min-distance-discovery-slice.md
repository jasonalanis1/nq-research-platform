# exp-023 — Level Sweep Reversal, "close_min_distance", first test on the Discovery slice (2015-2021)

**Setup:** Level Sweep Reversal
**Variant:** close_min_distance
**Date:** 2026-08-23
**Sample Size:** 461 resolved trades
**Statistically Significant:** No (90% bootstrap CI on total R: -58.67R to +22.21R, spans zero)
**Status:** retest — negative point estimate on a much larger, older window than any prior test of this variant

## Hypothesis

Same underlying rule as exp-007/011/015/017/019/021 (close_min_distance
confirmation + 1.35x-risk video-derived target). This run's purpose:
the first test of this variant against `data_split.get_discovery_data()`
— the oldest ~60% of the newly-extended 2015-2026 dataset
(2015-01-01 -> 2021-10-03), per `docs/RESEARCH_INTEGRITY_PROTOCOL.md`'s
chronological Discovery/Validation/Holdout-Gen2 split. This window
shares no dates with any prior experiment on this variant — exp-019/021
both tested the 2024-08-15 -> 2026-04-06 research window, entirely
outside this Discovery slice.

## Data used

`data/NQ_1min_databento_2026-08-20.csv` (the 2015-01-01 -> present
Databento pull, committed as c16a105), sliced through
`data_split.get_discovery_data()`: legacy holdout (2026-04-07+) excluded
first via `data_holdout.py`, then restricted to 2021-10-03 or earlier.
2101 discovery trading days available; 2100 scanned (excludes the first,
which has no prior day).

## Method

A temporary driver script (`src/_run_discovery_backtest.py`, not part of
the permanent pipeline — `data_split.py` is still not wired into any
detector/backtest script) called `detect_level_sweep.py`'s
`scan_all_days()` and `backtest.py`'s `simulate_trade()`/cost logic
directly against the Discovery-only DataFrame, then wrote output through
the normal `score_results.py` and `confidence_analysis.py` scripts
unmodified (filename-based, so no code changes were needed there).
Console output confirmed the legacy holdout boundary was applied before
the Discovery slice was taken.

## Results (net of estimated costs)

- 474 signals, 461 resolved (13 unresolved).
- Win rate 43.6% (95% CI: 39.1%-48.1%).
- Average win +1.29R, average loss -1.07R.
- Expectancy **-0.038R** (profit factor 1.10, max drawdown -31.55R, total -17.67R).
- Bootstrap: 90% CI on total R is -58.67R to +22.21R (includes zero —
  not statistically significant). Only 23.8% of 461-future-trade
  simulations ended net profitable.

## Interpretation

This is the largest single sample this variant has ever been tested on
(461 resolved trades, more than double exp-019/021's ~172), and it comes
out net negative — a similar magnitude of negative expectancy to
exp-019 (-0.014R) and exp-021 (-0.021R), though this time on data that
predates both of those runs entirely rather than overlapping with them.
That's a meaningfully different piece of evidence than another retest
of the same recent window: it shows the negative read from exp-019/021
isn't just a property of 2024-2026's specific market conditions — the
same rule also failed to show a real edge across 2015-2021, a period
spanning several very different market regimes (including 2020's COVID
crash and recovery). Combined with exp-019/021, three non-overlapping
windows now all show flat-to-negative results for this variant. Not yet
run through `larry_validate.py`'s DSR/PBO check (that requires a defined
trial set/lineage, which hasn't been built for this variant) or logged
in `research_ledger.py` (explicitly not authorized for real hypotheses
yet, per that file's status note).

## Next step

This result, taken together with exp-019/021, argues for treating
`close_min_distance` as a weak candidate across every window tested so
far — recent (2024-2026), and now the much larger and older
2015-2021 Discovery slice. See exp-024 for the companion
`full_bar_range` result on the same slice.
