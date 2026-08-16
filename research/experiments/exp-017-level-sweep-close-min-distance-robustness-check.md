# exp-017 — Level Sweep Reversal, "close_min_distance", robustness check (significance + cost stress)

**Date:** 2026-08-16
**Status:** retest (221 trades — not a new backtest run, a deeper look at exp-015's existing 2-year result, plus one new stress-cost variant)

## Purpose

Two follow-up questions on exp-015's 2-year result (+0.043R, 221 trades),
requested directly by Jason before trusting it further: (1) is this
distinguishable from zero expectancy ("no edge"), or is zero still
plausible given the sample? (2) does it survive materially higher
cost assumptions?

## Part 1 — statistical significance (zero-expectancy check)

Method: `src/confidence_analysis.py`'s existing bootstrap ("reshuffle the
same trades" step) resamples the 221 actual trade outcomes with
replacement 2,000 times and reports the 5th/50th/95th percentile of the
resulting total R — this is a standard 90% bootstrap confidence interval
on the total (equivalently, mean/expectancy) R-multiple.

Result: **5th pct -18.89R, median +8.73R, 95th pct +37.08R.**

**Zero is comfortably inside this range.** Plain English: this result is
NOT statistically distinguishable from "no real edge" at 90% confidence
— the data is consistent with the true expectancy being anywhere from
meaningfully negative to strongly positive. The positive median is the
best single guess, but the current sample size isn't enough to rule out
zero (or negative) as the true long-run number.

## Part 2 — cost stress test (2x commission/slippage)

Method: added a `COST_STRESS_MULTIPLIER` environment variable to
`backtest.py` (defaults to 1.0, i.e. no change to any past result) that
scales both commission and slippage by that factor. Ran with
`COST_STRESS_MULTIPLIER=2`: commission $2.50→$5.00/side, slippage
1→2 ticks/side, round-trip cost 0.75pt→1.50pt. Output saved separately
as `backtest_results_level_sweep_close_min_distance_stress2x.csv` — the
normal-cost result (exp-015's file) was not touched.

Result: **expectancy +0.011R** (down from +0.043R at normal costs), win
rate unchanged at 45.7% (cost doesn't change which trades win/lose, only
how much each nets), profit factor 1.29 (down from 1.33), total R +2.50
(down from +9.42).

**Plain English: still positive, but only barely** — roughly a quarter
of the edge survives doubled trading costs. This is a thin margin, not a
comfortable one.

## Interpretation

Combining both checks: this variant has NOT been shown to have a
statistically reliable edge (Part 1), and what edge the point-estimate
does show is thin enough that doubling costs nearly erases it (Part 2).
Neither finding kills the idea outright — 221 trades isn't nothing, and
"barely positive under stress" is a real result, not a failure — but
together they argue for real caution before trusting this variant, not
excitement.

## Next step

Same as exp-015/016: continue accumulating real data over time rather
than concluding anything final now. If Jason wants a firmer answer
sooner, the two levers that would help most are (a) more resolved trades
(time), or (b) getting his real broker's actual commission/slippage
numbers into `backtest.py` instead of the current generic placeholders,
since the stress test above is a rough "what if costs are worse"
guess, not his real costs.
