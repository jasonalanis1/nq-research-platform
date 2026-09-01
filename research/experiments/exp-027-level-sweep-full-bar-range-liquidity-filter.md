# exp-027 -- Trend-Structure Liquidity Filter, full_bar_range (Discovery slice)

**Setup:** Level Sweep Reversal, full_bar_range confirmation + trend-structure liquidity filter (per `research/setups/trend-structure-liquidity-filter.md`)
**Variant:** protected-level sweeps only (vs. a not_protected comparison bucket, reported below)
**Date:** 2026-09-01
**Sample Size:** 59 resolved trades (protected bucket)
**Statistically Significant:** **No** (90% bootstrap CI -19.33R to +11.41R, spans zero)
**Status:** retest -- negative point estimate, essentially no separation from the interior bucket, well below the 150-trade promotion-bar minimum

## Hypothesis

Same filter as exp-026 (see that file for the full method), applied to
the full_bar_range confirmation variant instead of close_min_distance.
Run together with exp-026 in the same driver invocation, same data
snapshot, same verified-byte-identical fast-scan reimplementation.

## Data used

Same as exp-026: `data/NQ_1min_databento_2026-08-20.csv`, Discovery slice
(2015-01-01 through 2021-10-03, 2101 trading days).

## Method

See exp-026 -- identical method, run in the same script invocation.
Raw signal count: 565 (vs. exp-024's 558 on a slightly earlier data
pull). Trend context at signal time: 247 UPTREND, 120 DOWNTREND, 198
NO_TREND. 60 signals classified `protected`, 505 `not_protected`.

## Results (net of estimated costs)

**Protected bucket (the actual hypothesis under test):**
- 59 resolved trades (1 unresolved).
- Win rate 44.1% (95% CI 31.4%-56.7%).
- Expectancy **-0.076R** (profit factor 1.10 raw / 0.88 R-normalized).
- Max drawdown -12.15R, total -4.48R.
- Bootstrap: 90% CI on total R is **-19.33R to +11.41R** -- includes zero.
  Only 26.6% of bootstrap-projected 100-future-trade simulations ended
  net profitable.

**Not_protected bucket (diagnostic comparison):**
- 499 resolved trades (6 unresolved).
- Win rate 44.9% (95% CI 40.5%-49.3%).
- Expectancy **-0.084R** (profit factor 1.33 raw / 0.87 R-normalized).
- Bootstrap: 90% CI -82.88R to +1.81R -- includes zero, but barely (95th
  percentile is only +1.81R).

For reference, exp-024 (this same variant, unfiltered, all 565 signals
together) showed -0.083R -- consistent with both buckets here, since
neither differs much from the unfiltered result.

## Interpretation

**Unlike close_min_distance's protected bucket (exp-026), this shows no
support for the filter's thesis at all.** The protected bucket
(-0.076R) and the not_protected bucket (-0.084R) are nearly identical --
whatever is driving full_bar_range's overall negative result, the
trend-structure classification doesn't meaningfully separate it. Both
buckets are also negative point estimates, which is a materially
different read than close_min_distance's positive-but-tiny protected
result. Taken together, exp-026 and exp-027 do not tell a consistent
story about the filter working -- one variant shows a weak, non-
significant hint in the hypothesized direction, and the other shows
nothing. That inconsistency across the two variants that were already
being compared side by side is itself worth weighing against the filter,
not just each result's own individual weak significance. Same multiple-
testing caveat as exp-026 applies (sixth distinct hypothesis tested
against this base thesis, DSR/PBO correction still unavailable --
`purgedcv` not installed).

## Next step

Not promotable, and weaker evidence for the filter than exp-026's already-
weak result. Recommend not prioritizing further work on this specific
filter definition (trend-structure-aware liquidity, `SWING_FRACTAL_K=2`)
without a reason to believe the swing-detection parameters specifically
need adjusting -- the inconsistency between the two variants argues
against a real, filter-driven effect. `docs/BACKLOG.md`'s liquidity-
filter idea can be considered tested, in the same sense the FVG entry
trigger idea was closed out by exp-025.
