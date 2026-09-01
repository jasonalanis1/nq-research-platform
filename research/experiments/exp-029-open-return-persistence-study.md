# exp-029 — Open Return Persistence Study, Discovery slice (real data)

**Date:** 2026-09-01
**Type:** CHARACTERIZATION STUDY, not a strategy backtest. No trades, no
entry/stop/target, no hypothesis ledger entry — `research_ledger.py`'s
schema is for strategy backtests, which this isn't. See
`research/studies/open-return-persistence.md` for the frozen definition
and full reasoning.

## Question

Seven strategy hypotheses (spanning both the reversal thesis and the
continuation thesis) have now been tested and rejected. Rather than
inventing an eighth named chart pattern, this asks the question those
patterns were all implicitly betting on, directly and without any
pattern imposed: **does the Initial Balance's own directional return
predict anything about what happens afterward, at any of several fixed
time horizons?** A positive correlation would support continuation; a
negative correlation would support reversal; no significant correlation
at any horizon would mean neither thesis has a basis in the raw,
unconditional data — a more fundamental finding than any one pattern's
rejection.

## Data used

`data/NQ_1min_databento_2026-08-20.csv`, Discovery slice only
(`data_split.get_discovery_data()`, 2015-01-01 through 2021-10-03).

## Method

`src/study_open_return_persistence.py`, computing per day: the Initial
Balance return (8:30-9:00 AM ET, the same window frozen in
`research/setups/initial-balance-breakout.md`, reused unmodified — not a
new window), and the forward return from 9:00 AM to each of five fixed
horizons (+30, +60, +90, +120, +180 minutes). For each horizon: Pearson
correlation with a 90% bootstrap CI, and the conditional-mean difference
between IB-up days and IB-down days, also with a 90% bootstrap CI.

Because the direct day-by-day scan was too slow for this environment
against ~2.2M Discovery-slice rows, a temporary driver
(`src/_run_open_return_study_discovery.py`, deleted after use, same
pattern as this project's other one-off drivers) pre-grouped the data by
day and called the study's own `compute_day_returns()` unmodified on
each pre-sliced group — verified to produce an identical DataFrame to
calling `scan_all_days()` directly on a 200-day check slice before
trusting the full run.

## Results

1715 Discovery days had a usable Initial Balance window. Per horizon
(days with data reaching that far out only — see the study doc's
missing-horizon handling):

| Horizon | n days | IB-up / IB-down | Correlation | 90% CI | Significant? | Mean fwd return, IB-up | Mean fwd return, IB-down | Diff 90% CI |
|---|---|---|---|---|---|---|---|---|
| +30 min | 1713 | 841 / 826 | +0.0724 | [-0.0287, +0.1669] | No | +0.08 pts | +0.00 pts | [-0.96, +1.01] |
| +60 min | 1686 | 827 / 815 | +0.0105 | [-0.0647, +0.0826] | No | +0.26 pts | +2.23 pts | [-4.58, +0.67] |
| +90 min | 1686 | 827 / 815 | +0.0084 | [-0.0757, +0.0891] | No | +0.96 pts | +1.71 pts | [-4.29, +2.62] |
| +120 min | 1686 | 827 / 815 | -0.0363 | [-0.1087, +0.0342] | No | -0.74 pts | +2.78 pts | [-7.60, +0.37] |
| +180 min | 1686 | 827 / 815 | -0.0022 | [-0.0814, +0.0744] | No | +1.44 pts | +2.46 pts | [-5.64, +3.59] |

Every correlation is within about ±0.07 of zero, every 90% CI (both on
the correlation and on the up/down mean difference) spans zero, and
there's no consistent sign pattern across horizons (weakly positive at
30/60/90 min, weakly negative at 120 min, back near zero at 180 min) —
the shape of noise, not of a real relationship that happens to be small.

## Interpretation

**Clean null result, well-powered.** With roughly 1,686-1,713 days per
horizon — more than triple the FVG entry trigger's 500-trade sample and
comparable to Initial Balance Breakout's 1654 — this isn't a
small-sample "can't tell" result. The Initial Balance's own direction
carries no detectable linear relationship, in either direction, to what
happens over the following 30 minutes to 3 hours, in the Discovery
slice.

This reinforces, at a more fundamental level, why both major thesis
families tested so far in this project have failed: reversal setups
(Level Sweep Reversal, the FVG entry trigger, the trend-structure
liquidity filter — all six variants) are, at bottom, bets on a negative
relationship between an early move and what follows; the Initial Balance
Breakout is, at bottom, a bet on a positive one (conditional on a
breakout actually occurring). This study asks the same underlying
question without any pattern, entry rule, or breakout condition standing
in the way, and finds essentially nothing in either direction. It
doesn't prove no edge exists anywhere in this data — only that a simple
linear relationship between the IB's own direction and the specific
horizons tested here doesn't. A genuinely nonlinear relationship (e.g.
only after an unusually large IB move, or only on certain days of the
week) wouldn't necessarily show up in this test, and isn't ruled out.

## Next step

Not a "kill" in the strategy sense (there's no strategy here to kill),
but a strong signal about where more chart-pattern hypotheses are
unlikely to pay off. Two lines of evidence — seven rejected strategy
hypotheses across two theses, and now a clean null on the raw
unconditional relationship itself — point the same direction: continuing
to test more intraday-price-action-only chart patterns around the 8:30
open has a low expected payoff without new information. Worth
considering next, in rough order of how much new infrastructure each
would need: (1) whether the data's `Volume` column carries real,
usable values (untested so far — every setup to date has used price
only) and whether volume-conditioned behavior around the open looks any
different; (2) day-of-week or calendar-position effects (e.g. does
Monday/Friday or month-end behave differently — no new data needed);
(3) a genuinely nonlinear or conditional version of this same
persistence question (e.g. only on days with an unusually large or
small IB range) rather than a plain linear correlation. Deciding among
these, or a fourth direction entirely, is the next call to make.
