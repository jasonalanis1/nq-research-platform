# Bar Behavior, Intraday Resolution — Frozen Spec (exp-094 through exp-099)

## Why this test

All 6 daily-bar directional mechanisms tested so far (rejection wick x2,
failed breakout, engulfing x2, three-bar sequence -- batches 1 and 2, all
REJECTED) were tested at DAILY resolution. The project's only two
Validation-survivors (range-contraction, overnight coil) both came from
INTRADAY granularity, not daily bars. This is the one dimension not yet
controlled for: same pattern shapes, different bar size. Per the staff-
meeting discussion (2026-09-08), this is "pulling the lever" of testing
whether daily-bar efficiency, not the pattern ideas themselves, was the
real reason nothing survived.

## Bar construction

60-minute bars built from 1-minute RTH data (09:30-16:00 ET), yielding
up to 6.5 bars/day (last bar partial, 15:30-16:00, kept as its own bar
-- NQ trades all 6.5 RTH hours, no bar is dropped for being short).
Chosen over a shorter intraday bar (5/15-min) to keep the same rough
information content per bar as the daily tests (a meaningful chunk of
session activity), while still being ~6.5x more granular than daily.

## The 6 conditions -- identical logic to batches 1+2, only the bar unit changes

Reused UNMODIFIED except for the bar-construction substitution:
`WICK_TO_BODY_RATIO=2.0`, `LARGE_RANGE_MULTIPLE=1.5` (batch 1);
engulfing/three-bar definitions (batch 2). Lookback windows are
redefined in BAR units instead of DAY units, scaled to keep roughly the
same real-time lookback (20 daily bars ~= 20 trading days; the intraday
equivalent uses `RANGE_LOOKBACK_BARS=20` 60-minute bars ~= a bit over 3
trading days -- disclosed as a genuinely different lookback window in
real time, not a claim of equivalence, since 20 hourly bars is a
different amount of history than 20 days).

- **exp-094 bearish rejection at resistance**, **exp-095 bullish
  rejection at support**: same wick-ratio-vs-body, prior-BAR's high/low
  test as batch 1's exp-066/067, at 60-min resolution. Outcome: next
  60-min bar's return.
- **exp-096 failed breakout continuation**: same large-range-bar ->
  opposite-direction-next-bar -> measure bar-after-that test as
  exp-068, at 60-min resolution.
- **exp-097 bullish engulfing**, **exp-098 bearish engulfing**: same
  body-containment definition as exp-088/089, at 60-min resolution.
- **exp-099 three-bar directional sequence (continuation)**: same
  definition as exp-090, at 60-min resolution.

## Method

Nonparametric bootstrap, N_BOOTSTRAP=3000, seed=7, 90% CI, Step 1 only
(statistical, no costs -- consistent with every prior bar-behavior
batch). Credible = signed-to-prediction CI's lower bound above zero.
Any Step-1 PASS with n >= 40 gets a single Validation-slice prospective
test; thinner results are flagged, not tested further.

## Multiple-testing disclosure

6 pre-registered conditions, one shared `search_batch_id`
(`batch-2026-09-08-bar-behavior-intraday`), run together, no follow-up
conditions or threshold changes after seeing results.

## Pre-committed interpretation

If this batch ALSO comes back null across all 6, that's real evidence
the daily/bar-pattern search itself (not just the daily timeframe) is
exhausted for this project, regardless of resolution -- a stronger
conclusion than the earlier daily-only trigger. If ANY condition
survives Step 1 well-powered, run its Validation prospective test before
any further conclusion.
