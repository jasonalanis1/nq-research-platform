# OBS-FINDING-006: Overnight Gap Fade, Open Bucket

Per the Behavioral Finding protocol. Measurement only -- no trade design.

## Definition

Event: the 09:30 RTH open vs. prior RTH close, where |gap| >= 0.5x the
prior day's own RTH range. Measured at the open bar only (once per
day). Two mirrored event types: overnight_gap_down and
overnight_gap_up.

## Measurement

- `overnight_gap_down`, normal regime, open bucket, 1min horizon:
  n=64, effect=+3.54, ci_90=(1.18,5.86) -- price moves UP after a
  gap-down open (bounce).
- `overnight_gap_down`, narrow regime, open bucket, 1min: n=48,
  effect=+3.57, ci_90=(1.36,6.39) -- same direction, different regime.
- `overnight_gap_up`, narrow regime, open bucket, 1min: n=43,
  effect=-2.14, ci_90=(-3.94,-0.41) -- mirror: price moves DOWN after
  a gap-up open.
Source: Observatory v3 scan.

## Perspectives

- Path-to-Profitability Advisor: this is the most mechanistically
  plausible finding of any Observatory scan -- classic, well-documented
  opening-gap mean-reversion, consistent direction across gap-up and
  gap-down, holding in two regimes. Worth a hypothesis on that basis
  alone.
- Market Behavior Advisor: the horizon evidence is thin -- Promising
  only at the 1-minute horizon; longer horizons for these same cells
  landed in Interesting/Weak, meaning the measured edge may decay fast.
  A trade design needs enough room to develop past 1 minute, which is
  in tension with "the effect is only clearly measurable at 1 minute."
  Flagging this explicitly so a fast-decaying-effect result isn't a
  surprise.
- Claude: per the just-completed diagnostic (monetization-diagnostic-
  round1.md), this project's last 6 monetization attempts all had a
  real, small POSITIVE gross edge that a too-tight stop/cost ratio
  wiped out -- not a detection problem. This hypothesis is the first
  deliberate test of that lesson: size the stop off the prior day's
  own daily ATR (much wider than the 1-minute-bar buffer used
  previously) so the fixed cost is a small fraction of risk, even
  though the Market Behavior Advisor's decay concern means this is a
  real bet, not a free improvement.

## Judgment

Real, plausible measurement with a genuine caveat (short-horizon-only
strength) that the hypothesis design should account for rather than
paper over.

## Status

OPEN -- proceeding to hypothesis spec (H87), first monetization
attempt built explicitly around the diagnostic's cost-ratio lesson.
