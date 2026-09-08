# Intraday Behavior Batch 1 — Frozen Spec (2026-09-08)

Search batch ID: `batch-2026-09-08-intraday-behavior-1`. Step 1 only
(statistical, no costs, no trading rule). Pre-registered as one fixed batch
of exactly 3 conditions, same discipline as `bar-behavior-batch1-spec.md`.
Discovery slice only.

## Why these three, and what was excluded

The Path-to-Profitability Advisor's initial candidate list for this
intraday-characterization phase was: opening-range structure, VWAP
reversion, volume-profile skew, momentum-burst bars, overnight-gap
first-hour fill. Checked against the ledger and existing setup docs before
freezing this batch:

- **Opening-range structure** — already extensively covered by the
  Initial Balance Breakout family (exp-028 base test, plus
  volume-confirmed and day-of-week conditioning variants, all REJECTED).
  Re-testing this would re-mine already-closed ground. EXCLUDED.
- **VWAP mean reversion** — already tested directly as hyp-000013
  (2σ/3σ band mean reversion), REJECTED. EXCLUDED.
- **Overnight-gap first-hour fill** — already tested directly in
  `study_overnight_gap.py` (`analyze_gap_fill`, fill-by-noon watch window).
  EXCLUDED.
- **Volume-profile skew** and **momentum-burst bars** are genuinely new —
  no existing study tests session-shape volume concentration or 1-min-bar
  burst/continuation dynamics. KEPT.
- Added a third, also genuinely new: **range-contraction cycle**
  (narrow-range day → next-day range expansion), a distinct, well-known
  volatility-clustering concept (NR7-style) not previously tested as its
  own standalone hypothesis (bar-behavior-batch1 used a similar range
  multiple only as a conditioning input for wick/rejection patterns, never
  as the hypothesis itself).

## The 3 conditions (all daily-resolution outcome variables; features
derived from 1-min bars where noted — none require order-book/tick data)

**exp-072 — Volume-profile skew.** For each day, compute the fraction of
that day's total 1-min volume occurring in the first 90 minutes of the
session (9:30-11:00 AM ET) vs. its own trailing 20-day average first-90-min
fraction. Classify each day as `front_loaded` (current fraction more than
1 std dev above its trailing mean) or `back_loaded` (more than 1 std dev
below) or normal (excluded from the primary test, descriptive only).
Outcome: next full trading day's log return. No predicted sign pinned in
advance (lesson from bar-behavior-batch1: let the data show direction,
disclose honestly either way).

**exp-073 — Momentum-burst bars.** A 1-min bar is a "burst" if its range
AND its volume both exceed `BURST_MULTIPLE=3.0`x their own trailing
20-bar averages (reuses this project's standard trailing-average
convention). For each burst bar during regular session hours, measure the
cumulative return over the following 15 minutes (`BURST_HORIZON_MIN=15`),
signed in the direction of the burst bar's own return (continuation test).
Bootstrap the mean of these signed 15-min-forward returns against zero.
This is an intraday-horizon test (minutes, not days) — first of its kind
in this project.

**exp-074 — Range-contraction cycle.** A day's full-session range (High -
Low, reusing `build_daily_bars`-style daily construction) is classified
`narrow` if it is below the 20th percentile of its own trailing 20-day
range distribution, `wide` if above the 80th percentile. Outcome: next
day's range (High - Low), relative to its own trailing 20-day average
range (a ratio, so results are comparable across the sample regardless of
absolute volatility level). Predicted direction: narrow days are followed
by wider-than-average ranges (contraction/expansion cycle), tested
honestly either way like the other two conditions above.

## Method

Nonparametric bootstrap, N_BOOTSTRAP=3000, seed=7 (matches
`study_bar_behavior_batch1.py` convention). 90% CI. A condition passes
Step 1 only if its 90% CI is entirely off zero (exp-072, exp-073) or off
1.0 (exp-074, since it's a ratio). No costs, no trading rule, no Step 2
unless Step 1 clears. Any condition clearing Step 1 is logged PROMISING
and, per the effect-size-inflation diagnostic just completed, treated as
provisional pending its own single pre-registered Validation-slice
prospective test — not trusted on the strength of the Discovery-stage CI
alone.

## Multiple-testing disclosure

3 pre-registered conditions, one shared `search_batch_id`, run together,
no data-peeking between them, no follow-up conditions added after seeing
results (matches bar-behavior-batch1 and every prior batch in this
project).
