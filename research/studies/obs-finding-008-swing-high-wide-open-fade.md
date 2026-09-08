# OBS-FINDING-008: Prior Swing-High Touch, Wide Regime, Open Bucket

Per the Behavioral Finding protocol, first candidate selected using the
new pre-screening rule (research/studies/monetization-screening-rule.md).

## Definition

Event: first touch of the most recent confirmed swing-pivot high
(20-bar lookback, +/-3-bar pivot definition) during 09:30-10:30 ET,
"wide" volatility regime. Horizon 30min: n=360, effect=-6.91,
ci_90=(-12.31,-1.58). Also Promising at 10min (n=360, effect=-3.77) and
15min (n=360, effect=-5.81) -- consistent negative direction across
horizons. Source: Observatory v2 scan.

## Why this passes the new screening filter

Effect size in POINTS (-6.9 at 30min) is nearly double H87's gap-fade
effect that produced this project's closest near-miss, on a larger
sample (n=360 vs. n=128) and a wide-regime day where daily ATR is
already elevated -- meaning a cost-aware ATR-scaled stop will be even
larger relative to this effect than it was for H87, the exact
condition the screening rule was designed to select for.

## Perspectives

- Path-to-Profitability Advisor: best-scoring candidate by the new
  rule of any tried this session -- large point effect, large n,
  consistent across 3 horizons. Strong candidate for a genuine test.
- Market Behavior Advisor: wide-regime days are volatile by
  definition -- a swing-high fade there could just be "any large move
  tends to partially retrace in a volatile market," a generic
  volatility-mean-reversion story rather than something specific to
  swing pivots. Worth noting as a mechanism caveat, not a reason to
  skip the test.
- Claude: agree, proceeding with the ATR-scaled-stop convention.

## Status

OPEN -- proceeding to hypothesis spec (H90).
