# NQ Daily Time-Series Momentum (Trend-Following)

**Status: Tested. Primary test result: NULL.** Frozen 2026-09-02,
following the pivot recorded in `docs/ROADMAP.md` (2026-09-02, PIVOT
entry): after twelve straight null hypotheses across three mechanism
families, the Path-to-Profitability Advisor recommended, and Jason
approved, testing whether the entire project's premise held at a
different timeframe before spending on new data types. This is the
first study in this project's history to test a signal at daily
resolution rather than intraday -- implemented and run against the
Discovery slice the same day. See Status section below for the result.

## Where this came from

Following exp-037's null (ES overnight gap), Claude asked the
Path-to-Profitability Advisor for an independent recommendation on
what to do next, given twelve straight nulls across level-interaction,
volatility-regime, and cross-market mechanisms, all at intraday
(1-minute-bar) resolution. The Advisor's recommendation, which Jason
adopted over Claude's own initial lean: rather than test the two
remaining cross-market candidates or acquire a new data source, run
ONE concrete test of daily/swing-timeframe trend-following using data
already on hand -- a mechanism with real, still-standing academic and
CTA support (Moskowitz, Ooi & Pedersen, "Time Series Momentum," 2012),
structurally different from every sub-hour, level-touch mechanism this
project has tested so far, and one institutional stat-arb is less
likely to have fully competed away than minute-level patterns in a
single liquid index future. A real result answers the premise question
directly; another null is a genuine signal about the approach, not
just one more rejected variant.

Jason and Claude discussed, and Claude presented (with the Advisor's
independent agreement) a further design fork: the project's standing
promotion bar (`docs/ROADMAP.md`, "Promotion bar," 2026-08-18 --
expectancy > 0, >= 150 trades, 90% CI on expectancy) assumes a
discrete, frequently-repeating trade shape. A 252-trading-day momentum
signal flips direction only a handful of times across the entire
6.75-year Discovery window -- nowhere near 150 -- not because any edge
is weak, but because the mechanism itself rebalances slowly. Jason
chose to adapt the bar's mechanics for this one test (evaluate on the
daily P&L series via bootstrap CI, rather than forcing an artificially
short lookback just to manufacture 150+ discrete trades) over the
alternative (shorten the lookback so the existing trade-counting bar
applies unchanged) after being shown the tradeoff explicitly. See "Why
the promotion bar is adapted for this study," below, for the full
reasoning and scope of this exception.

## What this is NOT

This is a **characterization-and-promotion study**, structured exactly
like every prior hypothesis test in this project: one primary
question, one primary outcome, pre-committed before any code is
written, with a Step 2 gate that must be checked honestly. It is not a
loosening of the project's overall standards -- it is a disclosed,
scoped adaptation of HOW those standards are measured for a mechanism
whose natural unit (a slow-moving daily position, not a discrete
intraday trade) doesn't fit the existing trade-counting bar. If this
study's primary test passes its adapted gate, the resulting rule
still goes through the same Validation-slice and sealed-Holdout
process every other candidate would.

## Definition

### 1. Daily return series

Reuses the exact building blocks already frozen and used in three
prior studies, unmodified: `ref_close[t]` from
`study_overnight_gap.get_reference_close()` (the last bar's Close at
or before 4:00 PM ET), and `r[t] = ln(ref_close[t] / ref_close[t-1])`
from `study_volatility_regime.compute_daily_log_returns()`. No new
"daily bar" convention is invented.

### 2. Momentum lookback -- 252 trading days

`mom[t]` = the sum of `r[t-252], ..., r[t-1]` -- the cumulative log
return over the trailing ~12 months strictly before day `t`. 252
trading days is the canonical convention from the academic time-series
momentum literature (approximately one calendar year of trading days),
chosen structurally for that reason, not tuned or tried against
alternatives.

### 3. When the signal becomes known

`mom[t]` depends only on `r[t-1]` and earlier, which depend only on
reference closes through day `t-1`. So day `t`'s position is fully
determined as of 4:00 PM ET on day `t-1` -- strictly before day `t`'s
own session. No information from day `t` or later enters its own
signal.

### 4. Position rule

`position[t] = +1` if `mom[t] > 0`, `-1` if `mom[t] < 0` (in the
practically-impossible case `mom[t] == 0` exactly, `position[t]` holds
the previous day's position). No flat/neutral band -- a simpler rule
with one fewer free parameter than a version with a dead-zone around
zero.

### 5. Continuous daily rebalancing -- a disclosed simplification

The original time-series-momentum literature typically rebalances
monthly; this study evaluates and rebalances the position **daily**
(the 252-day window itself still moves one day at a time). This is
simpler to implement causally and is, if anything, more responsive
(and therefore more conservative on transaction-cost drag, since it
can flip on any day, not just at fixed monthly intervals) than the
literature's discrete-rebalance version -- not a change made because it
performed better; it was never compared against monthly rebalancing.

### 6. Daily P&L and cost model

`pnl[t] = position[t] * (ref_close[t] - ref_close[t-1])` in NQ points
-- today's position (decided using only information through yesterday's
close) applied to today's actual price change. On a day where
`position[t] != position[t-1]` (a flip from long to short or vice
versa), a cost of **2 x `ROUND_TRIP_COST_POINTS`**
(`backtest.py`'s existing 0.75-point constant, imported unmodified) is
subtracted -- one round-trip's worth of cost to close the old position,
another to open the new one, since a flip is economically two
transactions. On a day with no flip, no cost is charged. `net_pnl[t] =
pnl[t]` minus that flip cost when applicable.

### 7. Primary test and confidence interval

90% bootstrap CI (2,000 resamples, `RANDOM_SEED = 11`, matching this
project's current-convention seed) on the **mean daily net P&L**
across every classifiable Discovery day, resampling days with
replacement -- the same nonparametric resample-and-recompute pattern as
every other bootstrap in this project, applied here to a daily P&L
series rather than a trade-level statistic (this is the adaptation
described below). Statistically credible = the CI's lower bound is
strictly above zero.

### 8. Exclusion rules

Discovery slice only. A day is excluded if fewer than 252 prior daily
returns are available (no minimum floor beyond the lookback itself,
same reasoning as the volatility-regime study's approved
no-extra-floor decision). No return-value outlier is removed from the
primary analysis.

### 9. Criteria for declaring the study meaningful (adapted Step 2 gate)

Five conditions, same structure and same underlying principles as
every prior study's gate -- adapted only where the trade-count-specific
mechanics don't apply to a slow-rebalancing signal:

1. **Statistically credible** -- per item 7 above.
2. **Economically meaningful (adapted)** -- mean daily net P&L must be
   >= 2x this strategy's own realized average daily cost drag (total
   flip costs paid across the Discovery sample, divided by the number
   of classifiable days) -- the same "at least double what's actually
   being paid in costs" principle behind every other study's 2x-cost
   threshold, computed against this mechanism's own real cost drag
   rather than a fixed per-trade constant, since discrete trades aren't
   this mechanism's natural unit.
3. **Plausible mechanism** -- a positive result must mean being
   positioned with the trailing 12-month trend was profitable net of
   cost, consistent with the trend-following thesis, not a story
   invented to fit whichever sign appears.
4. **Not an artifact** -- survives two pre-specified robustness checks:
   (a) the primary result with the single largest-magnitude daily P&L
   day removed, and (b) a first-half vs. second-half chronological
   split-sample stability check -- identical convention to exp-036 and
   exp-037.
5. **A simple mechanical rule can be specified without fitting to the
   result** -- already true by construction; the rule is fully
   mechanical from item 4 above regardless of outcome.

If any of the five fail, or the primary test is null, the finding is
recorded as-is and the study stops there -- same standing rule as every
prior study.

### 10. Mandatory disclosure -- number of position flips

Reported explicitly and prominently regardless of the primary test's
outcome: the total number of days on which `position[t] != position[t-1]`
across the Discovery sample. A result resting on only one or two flips
is a bet on one or two big historical trends, not evidence of a
repeatable pattern, and must be read that way even if it technically
clears the adapted gate above.

## Why the promotion bar is adapted for this study

The standing bar (`docs/ROADMAP.md`, "Promotion bar," added
2026-08-18: expectancy > 0, >= 150 trades, 90% CI on expectancy) was
written for, and has so far only ever been applied to, strategies that
generate many discrete, independent entry/exit events -- the natural
shape of every level-interaction and gap-based setup tested to date. A
252-trading-day momentum signal does not have that shape: it flips
direction only a handful of times across a 6.75-year Discovery window
by construction, regardless of whether the underlying edge is real or
strong. Two options were considered: (a) shorten the lookback until it
produces 150+ flips under the existing bar unchanged, or (b) keep the
academically-grounded 252-day lookback and adapt how "promoted" is
measured for this one test. Option (a) was rejected because it would
mean testing a fundamentally faster, different signal than the one
with real literature support -- drifting back toward the same
sub-hour-to-few-week timeframe already tested twelve times and
rejected, which would defeat the entire purpose of this study. Option
(b), adopted here, keeps every underlying principle of the standing
bar (bootstrap-CI statistical credibility, a real cost-relative
economic threshold, artifact/robustness checks, no free-parameter
fishing) and applies them to this mechanism's own natural unit (daily
P&L) instead of forcing an alien unit onto it.

This is a **one-time, explicitly scoped exception**, approved by Jason
for this study only. It does not change the standing 150-trades bar
for any other setup, past or future. Any future strategy sharing this
same slow-rebalancing shape would need its own explicit sign-off to
reuse this adapted form -- it is not an automatic precedent.

## Honesty flags

- The 252-day lookback, daily rebalancing, no-neutral-band position
  rule, and the flip-cost convention are each one frozen choice, not
  the best of several tried. No alternative lookback, rebalance
  frequency, or dead-zone was tested or will be tested under this
  hypothesis.
- The adapted economic-meaningfulness threshold (item 9.2) is a new
  formula, not a reused constant -- disclosed above rather than
  presented as equivalent to the standing bar's fixed threshold.
- With so few expected flips, the split-half robustness check (item
  9.4b) may itself rest on very few flips per half -- this limitation
  is inherent to the mechanism's timeframe, not a defect in the check,
  and is reported honestly regardless of what it shows.
- This is the first daily-resolution study in this project; all prior
  studies operated on 1-minute intraday bars.

## Multiple-testing context

Thirteenth strategy-adjacent hypothesis and eighth
conditioning/characterization-or-promotion study in this project, and
the first at daily resolution. Single pre-committed primary test (one
lookback, one signal, one cost model). `purgedcv` (DSR/PBO) remains
unavailable in this environment -- flagged consistently, as on every
experiment to date.

## Status

**Tested. Primary test result: NULL.** Run against the Discovery
slice on 2026-09-02. Mean daily net P&L was +0.772 points across 1,463
usable days, 90% bootstrap CI [-4.075, +5.501] -- spans zero.
Step-2-gate check 1 (statistically credible) failed, so per this
spec's own rule the study stops there; check 2 (economically
meaningful under the adapted threshold) technically passed but is
disclosed as an easy bar to clear at this low a flip count, and does
not change the outcome since check 1 already failed. Mandatory
disclosure: 44 position flips across 1,463 days (~6.5/year) -- an
actively updating signal, not a thin 1-2-trend bet. Both robustness
checks reported as-is per the frozen spec: dropping the single
largest-magnitude day barely moved the estimate, and a
first-half/second-half split showed the sign itself was unstable
across the sample (positive vs. negative). A real bug in the initial
implementation (day-pairing that dropped two days of P&L per single
missing reference-close day, instead of skipping over it) was caught
via a sanity check on the usable-sample count and fixed before this
result was trusted -- see
`research/experiments/exp-038-nq-daily-trend-following.md` for the
full account. No mechanical rule was proposed or built. No ledger
entry, consistent with a null result.

## History

- 2026-09-02: Path-to-Profitability Advisor recommended testing daily
  time-series momentum as a way to answer both the data-granularity
  question and the deeper approach question at once, at zero
  incremental data cost. Jason adopted the recommendation.
- 2026-09-02 (same day): Jason chose to adapt the promotion bar's
  mechanics for this one test (daily-P&L bootstrap CI) rather than
  shorten the lookback to fit the existing trade-counting bar
  unchanged, after the tradeoffs were presented explicitly.
- 2026-09-02 (same day): This Frozen Study Specification drafted.
  Presented to Jason for sign-off before any implementation.
- 2026-09-02 (same day): Jason approved implementation. Study
  implemented (`src/study_nq_trend_following.py`), a real day-pairing
  bug caught via a sanity check and fixed before trusting the result,
  and run against Discovery data. Primary test came back null (CI
  spans zero). Both robustness checks reported as-is; neither rescues
  the primary result. Written up as
  `research/experiments/exp-038-nq-daily-trend-following.md`. No
  ledger entry, no mechanical rule proposed.
