# Weekly-Resolution Trend Following -- Scoping Proposal (v1, APPROVED and TESTED -- exp-047)

## Status: APPROVED by Jason 2026-09-06, as-is. Built and tested the same day as exp-047. Result: NULL -- a genuine, disclosed near-miss, not promoted. See "Result (2026-09-06, exp-047)" below; the rest of this document is kept as the frozen record of what was authorized and why.

Written per the Research Scoping Agent process (`docs/RESEARCH_SCOPING_AGENT.md`),
after Jason asked, following exp-046's kill, whether this project needs a
structural pivot rather than another single-mechanism search, and the
Path-to-Profitability Advisor's direct recommendation: stop testing new
signals at daily/intraday resolution (both now heavily tested, mostly
null) and test the one resolution never tried -- weekly.

## Result (2026-09-06, exp-047)

Built and run the same day Jason approved this draft as-is. Implementation:
`src/study_nq_weekly_trend_following.py`. Full results:
`data/study_nq_weekly_trend_following_results.json`. Path-to-Profitability
Advisor independently reviewed the implementation and this result before it
was reported -- confirmed the implementation matches the frozen spec, no
lookahead, no parameter search, and that "kill" is the technically correct
call per Section 5's binary gate (both statistical and economic checks
must clear; this spec does not include a "retest" tier).

**Modeling population**: 353 weekly bars resampled from the daily Discovery
series, 300 classifiable (52+ prior weekly returns), 299 with a computed
weekly P&L.

**Result: a genuine, honest near-miss -- NOT statistically credible, so a
NULL per the frozen gate, but the closest any hypothesis in this project
has come.** Mean weekly net P&L +19.38 points, 90% bootstrap CI
[-1.165, +40.414] -- the lower bound sits just barely below zero. Clearly
economically meaningful (far above the 2x-cost-drag threshold: threshold
was 0.221 points, actual mean was 19.38). 22 position flips across 299
weeks -- not a thin 1-2-trend bet.

**Robustness**: dropping the single largest-magnitude week reduces the
mean to +16.06 (CI still spans zero) -- not driven by one outlier week.
Chronological split-half: first half mean +9.93 (CI [-5.75, +25.77]),
second half mean +28.76 (CI [-8.49, +66.40]) -- both halves directionally
positive, no sign flip, though both individually still span zero.

**Why this is NOT promoted, retested, or re-parametrized, even though it's
close**: Section 5 above is explicit -- both the statistical and economic
checks must clear, with no softer tier for a promising-but-underpowered
result, unlike the disclosed escalation path some other studies in this
project have used. Trying a different lookback window or pulling in more
historical data now would be post-hoc parameter mining against the exact
data that produced this near-miss -- the Advisor was explicit that this is
not a legitimate path forward. The only defensible follow-up, if ever
pursued, would be a NEW, separately pre-registered spec testing this exact
signal and lookback on genuinely new future weekly data as it accrues (a
true prospective check) -- not a re-mine of Discovery history. No such
follow-up is authorized at this time.

**Honest bottom line**: weekly-resolution trend following is the most
economically striking result this project has produced (23+ hypotheses
in), but it is still, honestly, a null by this project's own pre-committed
statistical bar. Logged as such -- not oversold, not quietly softened.

## 1. Provenance

Not sourced from a video or outside claim. Directly proposed by the
Advisor during a 2026-09-06 strategic-direction consultation, after
being asked point-blank whether a structural change is warranted given
23 null/near-null hypotheses. This project has tested intraday setups
(ORB, level sweep, VWAP, FVG, liquidity filters) and, as of exp-038,
one daily-resolution momentum signal (null: mean +0.772 pts/day, 90%
CI [-4.075, +5.501], sign unstable across a split-half check). No
hypothesis in this project's 46-experiment history has used
weekly-resolution bars. This is a genuinely new timeframe, not a
variant of anything already tested.

## 2. Reuse over invention

This is a direct weekly-resolution adaptation of exp-038
(`src/study_nq_trend_following.py`), reusing its exact logic and
conventions wherever the coarser resolution allows:
- Same signal family: sign of trailing cumulative log return
  (time-series momentum, Moskowitz/Ooi/Pedersen convention).
- Same causal, no-lookahead construction.
- Same cost-accounting approach (`ROUND_TRIP_COST_POINTS`,
  `FLIP_COST_POINTS` reused unmodified).
- Same robustness checks: drop-largest-day, first-half/second-half
  split-stability.
- Same adapted promotion-bar precedent exp-038 already established
  and Jason already approved (a bootstrap CI on the P&L series plus a
  cost-drag-relative economic threshold, in place of trade-counting,
  since a weekly-rebalanced signal flips even less often than a daily
  one) -- reused, not re-litigated.

The only genuinely new code: resampling the existing daily reference-
close series to weekly bars (standard Friday-close-of-week convention,
or last available session in a short holiday week) before computing
returns and the trailing-momentum signal.

## 3. Every free choice pinned down before any result exists

- **Bar definition**: one bar per calendar week, close = the last
  valid daily reference close within that week (Mon-Fri), using the
  existing `compute_daily_ref_closes()` daily series as the input --
  no new price data needed.
- **Lookback**: 52 weeks (the direct weekly analogue of exp-038's
  ~252-trading-day / ~12-month lookback), trailing cumulative weekly
  log return, sign-based position.
- **Rebalance frequency**: weekly, at each new week's first available
  session.
- **Target variable / P&L**: week-over-week reference-close change,
  in points, position-adjusted, costed via FLIP_COST_POINTS only on
  weeks the position changes.
- **Promotion bar**: the same adapted bar exp-038 used and Jason
  already approved -- 90% bootstrap CI on the weekly P&L series
  entirely above zero, AND mean weekly P&L >= a cost-drag-relative
  economic threshold, in place of a 150-trade minimum (a signal this
  infrequent will never produce 150 "trades" in 6-7 years of weekly
  bars -- disclosed here, not discovered after running it).

## 4. Known risks and reasons for skepticism, disclosed up front

- **Small sample by construction.** ~350 weekly bars across the
  Discovery window (2015-2021), versus exp-038's 1,463 daily bars --
  roughly a 4x reduction in independent observations. exp-038's own
  90% CI (half-width ~4.8 pts) already spanned zero on the larger
  daily sample; a ~4x-smaller weekly sample should be expected to
  produce a CI at least as wide, likely wider. An inconclusive,
  underpowered result -- not a clean pass or fail -- should be treated
  as the MODAL outcome here, not a surprise if it happens.
- **The Advisor was explicit that this is not a confident prediction
  of success** -- daily trend-following already came back null; there
  is a real, live possibility weekly does too. This is scoped as an
  honest, disciplined check of one genuinely untested timeframe, not
  sold as a likely win.
- **Not a substitute for the risk-management idea Jason separately
  raised** (asymmetric stop/target sizing). That is a distinct
  question -- see the companion scoping note on payoff-shaping
  overlays -- and reshapes the payoff of a signal rather than
  creating new directional edge. Conflating the two would make a
  result hard to interpret, so they are scoped and tested separately.

## 5. Path from result to verdict

Same two checks exp-038 used, run in the same order:
1. Statistical check: 90% bootstrap CI on the weekly net-P&L series --
   entirely above zero required to be "significant."
2. Economic check: mean weekly net P&L against the cost-drag-relative
   threshold already established in exp-038's precedent.
Both must clear for anything beyond "null." No new gate invented for
this study.

## 6. Discovery/Validation/Holdout discipline

Discovery slice only, matching every other hypothesis. No Validation-
slice test unless this clears both checks above.

## 7. Multiple-testing accounting

Gets its own exp-XXX number and Research Ledger entry (`strategy_origin:
"derivative"`, direct weekly resample of exp-038's already-logged
hypothesis, parent_hypothesis_id linked). Counts toward the project's
cumulative trial count like everything else.

## 8. What this is NOT

- Not a claim that weekly resolution is likely to succeed where daily
  and intraday did not -- it is the one timeframe genuinely untested,
  scoped honestly, nothing more.
- Not the "let winners run, cut losses fast" risk-management idea --
  that is a separate, distinct hypothesis about payoff-shaping, not
  timeframe.
- Not an adaptive or continuously-learning system -- per the
  Advisor's direct assessment, this project's data volume (~350-1,500
  rows depending on resolution) cannot currently support a trustworthy
  adaptive model without trading honest nulls for overfit false
  confidence. That idea is parked, not pursued, until a real change
  in data volume or granularity (e.g. order-flow data, currently
  cost-blocked at ~$54k/year) makes it viable.
- Not authorized to be built yet. Needs the Advisor's review and
  Jason's explicit sign-off before any code is written, per this
  project's standing frozen-spec discipline.

## 9. ASCII-only

Confirmed.
