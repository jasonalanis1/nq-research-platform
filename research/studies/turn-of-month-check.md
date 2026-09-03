# Turn-of-the-Month Effect -- Cheap Side-Check (exp-043)

## What this document is

A frozen, pre-registered spec for a narrow, deliberately cheap check,
written and run BEFORE looking at any result -- same discipline as
every other hypothesis in this project. This is explicitly scoped as
a side-check, not a headline effort: it reuses machinery that already
exists in this codebase (`study_volatility_regime.compute_daily_ref_closes`
and `compute_daily_log_returns`, imported unmodified) and asks one
narrow question first, with a second question gated behind the first.

## Why this one, and why now

The turn-of-the-month effect is a real, published calendar anomaly
(Lakonishok & Smidt 1988; McConnell & Xu 2008 specifically flagged it
as, in their words, the only calendar effect that remained
statistically and economically significant for S&P 500 FUTURES
specifically; Quantpedia's own backtest across 30+ international index
futures markets, 1926-2005, showed ~7.2% annualized return and a Sharpe
around 1.0 for the strategy). That is a genuinely different published
literature than the two calendar-family hypotheses already tested here.

It is NOT, however, a new direction. This project has already tested
two other calendar-timing hypotheses and found clean nulls on both:
day-of-week (exp-031: expectancy -0.056R to -0.092R on every single
weekday, no exceptions) and options-expiration week (exp-035: clean
null). Turn-of-month was also already considered once before, earlier
in this project's own history, and set aside in favor of what became
exp-041 (see `docs/ROADMAP.md` line ~429 and
`research/studies/post-release-directional-continuation.md`) -- this
is documented history, not something being revisited blind.

Given that track record, the Path-to-Profitability Advisor's explicit
recommendation (2026-09-03 consultation) was: run it, because it costs
almost nothing to check with data already on hand, but do not expect
it to succeed, and do not let it become a rabbit hole. This spec is
built to match that: one descriptive Step 1 test, with Step 2 (a
costed rule) gated behind Step 1 actually clearing a bar -- the same
two-step gating convention already used in exp-029/030 (Step 1 null ->
Step 2 correctly never run) and exp-032/033 (Step 1 cleared -> Step 3
triggered).

## Data and period

Discovery slice only (`data_split.get_discovery_data`, 2015-01-01 to
2021-10-03), NQ daily reference closes computed exactly as in
`study_nq_trend_following.py`: `compute_daily_ref_closes()` over
day-groups from the project's standard price-data loader
(`data_loader.load_price_data`), which already applies the legacy
holdout boundary. No new data source is needed for this check.

## Exact definition (frozen before any result is looked at)

A trading day (from the classifiable-day list already produced by
`compute_daily_ref_closes`, which only includes days with a usable
reference close) is a **turn-of-month day** if it is:

- the LAST classifiable trading day of a calendar month, OR
- one of the first THREE classifiable trading days of the following
  calendar month.

This is the standard 4-trading-day window used in the McConnell & Xu
(2008) and Quantpedia designs cited above. "Classifiable trading day"
means a day that actually has a usable reference close in this
project's data -- so this definition naturally follows the project's
existing calendar (no separate holiday list is needed).

Daily point-return for day `t` is `ref_close[t] - ref_close[t-1]`
(the immediately preceding classifiable day), computed the same way
`compute_daily_pnl`'s `price_change` is computed in
`study_nq_trend_following.py`.

## Step 1 (primary, descriptive, no cost) -- pre-registered

Split all classifiable daily point-returns into two groups: turn-of-month
days vs. all other days. For EACH group independently, compute the mean
daily point-return and a 90% bootstrap CI on that mean (reusing the
`bootstrap_mean_ci` function already defined in
`study_nq_trend_following.py`, same 2000-resample / seed-11 convention).

**Step 1 passes (proceed to Step 2) only if BOTH**:
1. The turn-of-month group's mean point-return is positive, AND
2. The turn-of-month group's 90% CI is entirely above zero (i.e.
   statistically credible on its own, same bar this project uses
   everywhere else).

If Step 1 does not clear both conditions, the check stops there and is
reported as a null, honestly, with no Step 2 run -- exactly the
exp-029/030 precedent.

## Step 2 (costed rule) -- gated, not guaranteed to run

Only if Step 1 clears: a long-only position held on every turn-of-month
day (enter at prior close, exit at that day's close -- one round trip
per turn-of-month day), net of `ROUND_TRIP_COST_POINTS` from
`backtest.py`, reusing `analyze_primary`'s statistically-credible /
economically-meaningful (>= 2x realized cost drag) gate structure from
`study_nq_trend_following.py` unmodified.

## Promotion bar

Standard bar applies if this ever reaches a mechanical-rule test:
expectancy > 0 after costs, >= 150 trades, 90% bootstrap CI entirely
above zero, Discovery data only. Turn-of-month days are ~4 out of every
~21 trading days (~19% of days), so over the ~1,675 Discovery trading
days this gives roughly 300+ qualifying days -- enough that, unlike the
COT weekly-resolution check being run in parallel, no sample-size
adaptation is needed here if it gets that far.

## What this is NOT

- Not a new mechanism family in the sense the checkpoint review used
  that term -- it is the same "calendar timing" family as exp-031 and
  exp-035, both of which came back null.
- Not being treated as a promising lead going in. The published
  literature is real, but this project's own two prior calendar tests,
  plus the project's own earlier documented decision to set this aside
  once already, are reasons for real skepticism, not optimism.
- Not being allowed to become a rabbit hole: one Step 1 run, reported
  honestly either way, with Step 2 only if Step 1 actually clears.
