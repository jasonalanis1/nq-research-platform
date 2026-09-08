# OBS-FINDING-005: Round-Number Touch, Normal Regime, Open Bucket (Continuation)

Per the Behavioral Finding protocol. Measurement only -- no trade design.

## Definition

Event: first touch (09:30-10:30 ET) of the nearest 50-point NQ round
level (computed forward from the day's own price action, no lookahead),
"normal" volatility regime. Horizons 3min (n=559, effect=+1.81,
ci_90=(0.40,3.30)) and 10min (n=559, effect=+3.37, ci_90=(0.63,5.99)).
Source: Observatory v2 scan, round-number/swing-pivot/session-open
event family.

## Why this is a structurally different candidate

Every finding in pilot round 1 (OBS-FINDING-001 through 004) was a
FADE/mean-reversion shape: touch a reference level, price reverses. This
is the opposite sign and a different mechanism class: touch a round
number during the open, price tends to CONTINUE in the direction it was
already moving, more than the baseline rate. If this monetizes, it
would be this project's first continuation-style (not fade) setup from
either the Observatory or the historical hypothesis set.

## Perspectives

- Path-to-Profitability Advisor: large n (559) and a CI that clears
  zero by a wide margin at both horizons tested -- the strongest single
  measurement this Observatory has produced across both v1 and v2. That
  alone earns a hypothesis attempt.
- Market Behavior Advisor: important caveat -- "touch a round number"
  fires very often (round levels are dense, ~50pts apart on an index
  trading in the 14000-16000s) and isn't inherently directional. A
  positive average forward return here could reflect a general
  upward-drift bias in the opening range on normal-regime days across
  this sample period, showing up on ANY frequent event in that window,
  not something specific to round numbers. This needs to be checked
  against a directional design (does it work both long after touching
  from below AND short after touching from above, or only one way)
  before treating it as a real round-number effect.
- Claude: agree with the caveat. The hypothesis design should test
  DIRECTION explicitly -- go with the direction of the immediately
  preceding short-term move, not just "always long" -- to distinguish
  a genuine round-number-interaction effect from a sample-wide upward
  drift artifact.

## Judgment

Interesting and worth testing, but flagged as the least mechanistically
resolved finding in this project's Observatory work so far -- the
positive-effect-could-be-generic-drift concern is real and unresolved.
Proceeding to a hypothesis that explicitly tests direction-of-touch
(momentum-continuation, not "always long") to address it directly.

## Status

OPEN -- proceeding to hypothesis spec (H86).
