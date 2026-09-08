# Volatility-Regime Overlay Screen — Frozen Spec (2026-09-08)

exp-077 — quick, cheap, non-exhaustive screen, per Jason's explicit direction
("try all the strategies, quick easy tests, don't over-exhaust it"). Tests
whether the range-contraction/volatility-persistence finding (hyp-000046 /
hyp-000048, the first-ever Validation-slice survivor) is useful as a
conditioning overlay on already-tested signals, rather than closing the
line entirely as "just volatility clustering, not tradable."

## Scope, disclosed honestly

"All the strategies" is scoped down to the signals with per-trade dated
results already saved to disk from prior backtests, so this genuinely is
quick and cheap (reuses existing trade files, no new backtest engine
work): the 4 Level Sweep Reversal variants (`close_min_distance` /
`full_bar_range` × `protected` / `not_protected` trend-structure buckets,
exp-023/024/026/027, all previously REJECTED standalone). Other tested
signals (IB Breakout, Fade the Gap, VWAP mean reversion, ZN bond lead)
only have aggregate results saved, not per-trade dated files, and
regenerating those would not be a "quick, easy" test — flagged as a
possible follow-up, not done here.

## Method

For each of the 4 Level Sweep variants: join each trade's entry date to
that day's volatility-persistence regime (narrow/wide/neither, from
`study_intraday_behavior_batch1.build_daily_frame`'s own trailing-range
percentile classification, reused unmodified, computed on Discovery data
only since these trades are all Discovery-slice). Compare each variant's
`r_multiple_net` mean between wide-regime days and narrow-regime days
(bootstrap difference-in-means CI, matching this project's standard
method) — the question is whether conditioning entry on the volatility
regime would have changed the (already-rejected) signal's economics
enough to matter, not whether it makes any of them newly profitable
overall (none were close).

## Decision rule

This is exploratory/diagnostic, not a fresh pre-registered directional
hypothesis — no promotion is possible here regardless of result, since
all 4 underlying signals are already closed as standalone (REJECTED,
no-retuning rule applies to them). A credible regime-conditioned
difference would only be evidence that the volatility-persistence finding
has some conditioning value in general, informing whether it's worth
designing a real overlay on a currently-active or future signal — it does
NOT reopen or retune any of the 4 closed Level Sweep lines themselves.
