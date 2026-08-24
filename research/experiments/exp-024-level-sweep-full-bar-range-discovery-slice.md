# exp-024 — Level Sweep Reversal, "full_bar_range", first test on the Discovery slice (2015-2021)

**Setup:** Level Sweep Reversal
**Variant:** full_bar_range
**Date:** 2026-08-23
**Sample Size:** 558 resolved trades
**Statistically Significant:** No (90% bootstrap CI on total R: -93.64R to +1.47R, spans zero)
**Status:** retest — clearly negative point estimate, CI's upper edge barely above zero

## Hypothesis

Same underlying rule as exp-008/012/016/018/020/022 (full_bar_range
confirmation + 1.35x-risk video-derived target). Companion run to
exp-023: first test of this variant against
`data_split.get_discovery_data()` (2015-01-01 -> 2021-10-03), per
`docs/RESEARCH_INTEGRITY_PROTOCOL.md`'s chronological split. Shares no
dates with exp-020/022, which tested 2024-08-15 -> 2026-04-06.

## Data used

Same as exp-023: `data/NQ_1min_databento_2026-08-20.csv`, sliced through
`data_split.get_discovery_data()` (legacy holdout excluded first, then
restricted to 2021-10-03 or earlier). 2101 discovery trading days
available; 2100 scanned.

## Method

Same as exp-023: `src/_run_discovery_backtest.py` (temporary, not part
of the permanent pipeline) called `detect_level_sweep.py`'s
`scan_all_days()` and `backtest.py`'s simulation/cost logic directly
against the Discovery-only DataFrame, then `score_results.py` and
`confidence_analysis.py` ran unmodified against the resulting file.

## Results (net of estimated costs)

- 565 signals, 558 resolved (7 unresolved).
- Win rate 44.8% (95% CI: 40.7%-48.9%).
- Average win +1.22R, average loss -1.14R.
- Expectancy **-0.083R** (profit factor 1.30, max drawdown -79.21R, total -46.51R).
- Bootstrap: 90% CI on total R is -93.64R to +1.47R (includes zero, but
  only barely — the upper edge sits just above it). Only 5.3% of
  558-future-trade simulations ended net profitable.

## Interpretation

This is the weakest result `full_bar_range` has shown in any test to
date, and on its largest sample yet (558 resolved trades, nearly 3x
exp-020/022's ~150). Expectancy of -0.083R is roughly double the
magnitude of exp-023's close_min_distance result on the same window, and
the bootstrap CI's upper bound (+1.47R total, essentially breakeven at
best) sits far closer to zero than its lower bound (-93.64R) — this
result is close to being statistically distinguishable from zero on the
negative side, which none of this variant's prior tests came close to.
Combined with exp-020/022 (roughly breakeven on 2024-2026 data), this
variant has now shown a clearly negative result on the larger,
independent 2015-2021 window while showing only a coin-flip result on
2024-2026 — nothing in this variant's history points to a real edge on
any window tested. Not yet run through `larry_validate.py`'s DSR/PBO
check or logged in `research_ledger.py`, for the same reasons noted in
exp-023.

## Next step

Between exp-023 and exp-024, the Discovery-slice results are worse than
anything either variant showed on the smaller, more recent research
window (exp-019 through exp-022). This is consistent with — and
strengthens — the standing read that neither `close_min_distance` nor
`full_bar_range` has a real edge as currently defined. Per
`docs/RESEARCH_ARCHITECTURE.md`'s standing priorities, this is a good
point to weigh continuing to iterate on Level Sweep Reversal's
definition against moving toward a different setup idea entirely — a
decision for Jason, not something to resolve by further retesting the
same rule on the same two remaining slices (Validation, Holdout Gen2),
which stay off-limits until a candidate is actually frozen and promoted.
