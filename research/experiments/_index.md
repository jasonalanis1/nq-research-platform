# Experiments Index

The running scoreboard of everything tested. This file is the source of
truth for what's been tried — update it every time a backtest variant
runs, and never overwrite a previous row's results (add a new row/file
instead, even if it's a re-run of a similar idea).

**Structured format (upgraded 2026-08-16, per docs/RESEARCH_ARCHITECTURE.md's
architecture review, recommendation #3):** each metric now has its own
column instead of being buried in free-text prose. `-` means the value
wasn't recorded for that run (mainly the two earliest experiments,
before this file settled into a consistent write-up format) — never
guessed or backfilled from memory. **Statistically Significant** is
`Not tested` unless a run specifically went through
`confidence_analysis.py`'s bootstrap significance check (see that
script's `Significant (95% two-sided)` line) — a positive expectancy
alone does NOT mean `Yes`.

| ID | Setup | Variant | Date | Sample Size | Win Rate | Expectancy | Profit Factor | Max Drawdown | Statistically Significant | Verdict |
|----|-------|---------|------|--------------|----------|-------------|----------------|----------------|------------------------------|---------|
| exp-001 | ORB | placeholder | 2026-08-15 | 46 | 37.0% | -0.287R (gross, no costs) | 0.51 | -15.10R | Not tested | retest — pipeline validation only, see notes |
| exp-002 | ORB | placeholder | 2026-08-16 | 46 | 37.0% (23.0%-50.9%) | -0.307R (net of costs) | - | - | Not tested | retest — pipeline validation only, see notes |
| exp-003 | Level Sweep Reversal | baseline (pre-variant-split) | 2026-08-16 | 38 | 2.6% (0.0%-7.7%) | -0.684R (net of costs) | 0.36 | -32.02R | Not tested | retest — pipeline validation only, see notes |
| exp-004 | ORB | placeholder | 2026-08-16 | 19 | 63.2% (41.5%-84.8%) | +0.206R (net of costs) | 1.38 | -3.58R | Not tested | retest — tiny sample, see notes |
| exp-005 | Level Sweep Reversal | baseline (pre-variant-split) | 2026-08-16 | 13 | 7.7% (0.0%-22.2%) | -0.822R (net of costs) | 0.54 | -9.52R | Not tested | retest — tiny sample, see notes |
| exp-006 | Level Sweep Reversal | close_any | 2026-08-16 | 16 | 50.0% (25.5%-74.5%) | +0.132R (net of costs) | 2.51 | -4.17R | Not tested | retest — 1 of 3 variants compared, no winner picked, see notes |
| exp-007 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 15 | 66.7% (42.8%-90.5%) | +0.545R (net of costs) | 4.33 | -2.04R | Not tested | retest — 1 of 3 variants compared, no winner picked, see notes |
| exp-008 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 15 | 53.3% (28.1%-78.6%) | +0.238R (net of costs) | 1.94 | -3.02R | Not tested | retest — 1 of 3 variants compared, no winner picked, see notes |
| exp-009 | ORB | placeholder | 2026-08-16 | 125 | 52.0% (43.2%-60.8%) | -0.028R (net of costs) | 0.80 | -18.50R | Not tested | retest — exp-004's positive result did NOT hold up, see notes |
| exp-010 | Level Sweep Reversal | close_any | 2026-08-16 | 68 | 42.6% (30.9%-54.4%) | -0.052R (net of costs) | 1.41 | -9.23R | Not tested | retest — exp-006's positive result did NOT hold up, see notes |
| exp-011 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 63 | 46.0% (33.7%-58.3%) | +0.054R (net of costs) | 1.45 | -10.11R | Not tested | retest — edge compressed hard from exp-007, stayed positive, see notes |
| exp-012 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 60 | 45.0% (32.4%-57.6%) | +0.033R (net of costs) | 1.11 | -6.01R | Not tested | retest — edge compressed hard from exp-008, stayed positive, see notes |
| exp-013 | ORB | placeholder | 2026-08-16 | 493 | 50.5% (46.1%-54.9%) | -0.062R (net of costs) | 0.82 | -55.39R | Not tested | kill — clearly negative at 493 trades, treating as settled, see notes |
| exp-014 | Level Sweep Reversal | close_any | 2026-08-16 | 237 | 42.6% (36.3%-48.9%) | -0.063R (net of costs) | 1.36 | -24.21R | Not tested | retest — confirms exp-010's negative read, weakest of 3 variants, see notes |
| exp-015 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 221 | 45.7% (39.1%-52.3%) | +0.043R (net of costs) | 1.33 | -14.85R | Not tested | retest — held stable vs exp-011, strongest of 3 variants, no winner picked yet, see notes |
| exp-016 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 197 | 45.7% (38.7%-52.6%) | +0.042R (net of costs) | 1.19 | -13.77R | Not tested | retest — held stable vs exp-012, near-tied with close_min_distance, no winner picked yet, see notes |
| exp-017 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 221 | 45.7% (unchanged by cost) | +0.011R (2x-cost stress; was +0.043R normal) | 1.29 (2x-cost stress) | -16.25R (2x-cost stress) | **No** (90% bootstrap CI on total R: -18.89R to +37.08R, spans zero) | retest — thin edge, survives cost stress barely, not yet statistically significant, see notes |
| exp-018 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 197 | 45.7% (unchanged by cost) | +0.010R (2x-cost stress; was +0.042R normal) | 1.16 (2x-cost stress) | -15.04R (2x-cost stress) | **No** (90% bootstrap CI on total R: -17.98R to +34.56R, spans zero) | retest — thin edge, survives cost stress barely, not yet statistically significant, see notes |
| exp-019 | Level Sweep Reversal | close_min_distance | 2026-08-16 | 173 | 43.4% (36.0%-50.7%) | -0.014R (net of costs) | 1.18 | -14.85R | **No** (90% bootstrap CI on total R: -26.38R to +21.45R, spans zero) | retest — FIRST holdout-respecting test of this variant; flipped negative once the 112-day holdout was excluded (was +0.043R when it was included), see notes |
| exp-020 | Level Sweep Reversal | full_bar_range | 2026-08-16 | 151 | 44.4% (36.4%-52.3%) | +0.008R (net of costs) | 1.10 | -13.77R | **No** (90% bootstrap CI on total R: -21.83R to +24.90R, spans zero) | retest — FIRST holdout-respecting test of this variant; shrank to roughly breakeven once the 112-day holdout was excluded (was +0.042R when it was included), see notes |
| exp-021 | Level Sweep Reversal | close_min_distance | 2026-08-20 | 172 | 43.0% (35.6%-50.4%) | -0.021R (net of costs) | 1.15 | -13.80R | **No** (90% bootstrap CI on total R: -29.57R to +20.56R, spans zero) | retest — re-run after the 2026-08-20 rolling-window fix added one research day (513->514); prior comparable result exp-019 (173 trades, -0.014R), essentially unchanged, see notes |
| exp-022 | Level Sweep Reversal | full_bar_range | 2026-08-20 | 150 | 44.0% (36.1%-51.9%) | -0.001R (net of costs) | 1.07 | -12.71R | **No** (90% bootstrap CI on total R: -23.49R to +23.44R, spans zero) | retest — re-run after the 2026-08-20 rolling-window fix added one research day (513->514); prior comparable result exp-020 (151 trades, +0.008R), essentially unchanged, now dead flat, see notes |
| exp-023 | Level Sweep Reversal | close_min_distance | 2026-08-23 | 461 | 43.6% (39.1%-48.1%) | -0.038R (net of costs) | 1.10 | -31.55R | **No** (90% bootstrap CI on total R: -58.67R to +22.21R, spans zero) | retest — FIRST test on the Discovery slice (2015-01-01 to 2021-10-03, non-overlapping with exp-019/021); largest sample yet, negative, see notes |
| exp-024 | Level Sweep Reversal | full_bar_range | 2026-08-23 | 558 | 44.8% (40.7%-48.9%) | -0.083R (net of costs) | 1.30 | -79.21R | **No** (90% bootstrap CI on total R: -93.64R to +1.47R, spans zero but barely) | retest — FIRST test on the Discovery slice (2015-01-01 to 2021-10-03, non-overlapping with exp-020/022); weakest result yet for this variant, see notes |

**Verdict key:** `keep` (worth pursuing further) · `kill` (edge not
supported, drop it) · `retest` (inconclusive as tested — data, sample
size, or setup definition needs to change before this row means
anything)

**Note on exp-001:** this was run on SYNTHETIC (fake, random-walk) data
as a way to prove the backtest pipeline itself works correctly, not as a
real test of the ORB pattern. A random dataset showing no edge is the
*correct* result. This row should not be read as "ORB doesn't work" —
it means "the code correctly found no edge in data that has none." Real
verdict pending: real data + (likely) Jason's actual setup definition
rather than this placeholder.

**Note on exp-019/exp-020:** these were the fifth round of testing on
this close_min_distance / full_bar_range comparison, following four
earlier rounds (exp-006-008, exp-010-012, exp-014-016, exp-017-018) on
substantially overlapping data, during which a third variant (close_any)
was dropped as weakest. The "not statistically significant" bootstrap
CI reported for both treats each as an isolated test and does not
account for this prior selection history. The practical verdict is
unchanged either way (both were already not significant) — this note
exists for the record's honesty, not because it changes the conclusion.
