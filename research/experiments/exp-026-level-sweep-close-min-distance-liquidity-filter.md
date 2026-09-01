# exp-026 -- Trend-Structure Liquidity Filter, close_min_distance (Discovery slice)

**Setup:** Level Sweep Reversal, close_min_distance confirmation + trend-structure liquidity filter (per `research/setups/trend-structure-liquidity-filter.md`)
**Variant:** protected-level sweeps only (vs. a not_protected comparison bucket, reported below)
**Date:** 2026-09-01
**Sample Size:** 44 resolved trades (protected bucket)
**Statistically Significant:** **No** (90% bootstrap CI -6.78R to +17.16R, spans zero)
**Status:** retest -- positive point estimate, but far below the 150-trade promotion-bar minimum and not statistically significant

## Hypothesis

First test of `research/setups/trend-structure-liquidity-filter.md`'s frozen
definition: every close_min_distance signal `detect_level_sweep.py` already
finds is classified as sweeping a "protected" trend-structure level (the
swing point that, if broken, would flip the prevailing trend) or an
"interior" level, using a 2-day swing fractal with an explicit no-lookahead
confirmation lag (`src/trend_structure.py`). Nothing about detection,
entry, stop, or target changes -- this is a post-hoc filter on the exact
same signals already tested in exp-023.

## Data used

`data/NQ_1min_databento_2026-08-20.csv`, sliced through
`data_split.get_discovery_data()` (2015-01-01 through 2021-10-03, 2101
trading days) -- same slice as exp-023, so directly comparable. Swing
structure was computed from Discovery-slice daily bars only, never
touching Validation or Holdout data.

## Method

A temporary driver (`src/_run_liquidity_filter_discovery_backtest.py`,
kept in the repo since real data access is intermittent for this session
-- not deleted this time) ran `detect_level_sweep.scan_all_days()`'s exact
underlying functions (`compute_levels()`, `scan_for_signal()`, completely
unmodified) via a performance-only reimplementation of the outer day loop
(needed because this session's shell has a per-command time limit against
~2.2M Discovery rows -- see the driver's own docstring). **This
reimplementation was verified byte-identical to calling
`detect_level_sweep.scan_all_days()` directly**, on a 200-day check slice,
before being trusted for the full run (both variants matched exactly, 0
differences). Each signal was then classified via
`trend_structure.classify_signal()` and backtested through
`backtest.simulate_trade()` (also unmodified), split into `protected` and
`not_protected` buckets. `score_results.py` and `confidence_analysis.py`
ran unmodified against both resulting files.

Raw signal count on this data snapshot: 474 (vs. exp-023's 461 on a
slightly earlier data pull -- the small difference is expected, not a bug,
since more recent Databento pulls can add/refine bars near the slice
boundary). Trend context at signal time: 208 UPTREND, 95 DOWNTREND, 171
NO_TREND. 46 signals classified `protected`, 428 `not_protected`.

## Results (net of estimated costs)

**Protected bucket (the actual hypothesis under test):**
- 44 resolved trades (2 unresolved).
- Win rate 50.0% (95% CI 35.2%-64.8%).
- Expectancy **+0.118R** (profit factor 1.26 raw / 1.22 R-normalized).
- Max drawdown -5.41R, total +5.20R.
- Bootstrap: 90% CI on total R is **-6.78R to +17.16R** -- includes zero.
  84.5% of bootstrap-projected 100-future-trade simulations ended net
  profitable, but the CI itself does not rule out zero or negative edge.

**Not_protected bucket (diagnostic comparison, not itself a candidate
strategy anyone would trade):**
- 417 resolved trades (11 unresolved).
- Win rate 42.9% (95% CI 38.2%-47.7%).
- Expectancy **-0.055R** (profit factor 1.09 raw / 0.91 R-normalized).
- Bootstrap: 90% CI -61.12R to +17.44R -- includes zero.

For reference, exp-023 (this same variant, unfiltered, all 461 signals
together) showed -0.038R -- roughly between these two buckets, as
expected from a weighted average.

## Interpretation

The protected bucket's positive point estimate (+0.118R) is directionally
consistent with the filter's underlying thesis -- sweeps of genuine
trend-structure points doing better than interior sweeps (-0.055R) -- but
this is weak evidence, not confirmation. 44 trades is a small sample (well
under the project's 150-trade promotion-bar minimum), the confidence
interval spans comfortably negative to strongly positive, and this is
built on the SAME underlying signals already tested three other ways
(unfiltered close_min_distance in exp-023, plus the base setup's other
confirmation variants). **This is now the sixth distinct hypothesis
tested against the Level Sweep Reversal base thesis**, and
`docs/RESEARCH_INTEGRITY_PROTOCOL.md`'s multiple-testing correction
(Deflated Sharpe Ratio / Probability of Backtest Overfitting) still
cannot be run -- `purgedcv` is not installed on this machine. A positive-
looking small-sample result at this point in the search should be read
as MORE likely to be noise, not less, precisely because of how many
related things have already been tried.

## Next step

Not promotable -- doesn't clear the promotion bar (needs >=150 trades,
positive expectancy, and a 90% CI entirely above zero; this clears none
of the three). Worth revisiting only if more Discovery-era data becomes
available to grow the protected-bucket sample size, or if
`SWING_FRACTAL_K` sensitivity testing (flagged as a future step in the
frozen definition doc) is done first. Not a priority over testing a
genuinely new hypothesis, given how much of this session's evidence now
points at Level Sweep Reversal's base thesis not having a real edge.
