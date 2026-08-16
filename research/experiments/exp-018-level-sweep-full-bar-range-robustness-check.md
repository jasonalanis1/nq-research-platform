# exp-018 — Level Sweep Reversal, "full_bar_range", robustness check (significance + cost stress)

**Date:** 2026-08-16
**Status:** retest (197 trades — not a new backtest run, a deeper look at exp-016's existing 2-year result, plus one new stress-cost variant)

## Purpose

Same two follow-up questions as exp-017, applied to exp-016's 2-year
result (+0.042R, 197 trades) instead of close_min_distance's.

## Part 1 — statistical significance (zero-expectancy check)

Method: same as exp-017 — `src/confidence_analysis.py`'s bootstrap
reshuffle of the 197 actual trade outcomes, 2,000 resamples, 90%
confidence interval on total/expectancy R.

Result: **5th pct -17.98R, median +8.06R, 95th pct +34.56R.**

**Zero is comfortably inside this range**, same conclusion as
close_min_distance: not statistically distinguishable from "no real
edge" at 90% confidence.

## Part 2 — cost stress test (2x commission/slippage)

Method: same as exp-017 — `COST_STRESS_MULTIPLIER=2` (commission
$2.50→$5.00/side, slippage 1→2 ticks/side). Output saved separately as
`backtest_results_level_sweep_full_bar_range_stress2x.csv` — exp-016's
normal-cost file was not touched.

Result: **expectancy +0.010R** (down from +0.042R at normal costs), win
rate unchanged at 45.7%, profit factor 1.16 (down from 1.19), total R
+1.91 (down from +8.21).

**Plain English: still positive, but only barely** — almost identical
picture to close_min_distance (roughly a quarter of the edge survives
doubled costs), and this variant's normal-cost profit factor (1.19) was
already the weaker of the two, so it has even less room before flipping
negative under real-world friction.

## Interpretation

Same combined read as exp-017: not statistically distinguishable from
zero, and a thin edge that's easily overwhelmed by moderately worse
costs. Between the two variants, close_min_distance and full_bar_range
are now essentially tied on every axis tested (expectancy, significance,
cost sensitivity) — there's no data-driven reason yet to prefer one over
the other.

## Next step

Same as exp-017 — keep accumulating data, and get Jason's real
commission/slippage numbers into the cost model rather than relying on
this stress test's rough 2x guess.
