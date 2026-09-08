# OBS-FINDING-004: Overnight-High Touch, Wide-Regime, Open Bucket

Per the Behavioral Finding protocol. Measurement only -- no trade design.

## Definition

Event: first touch (09:30-10:30 ET, "open" bucket) of the overnight
session high, "wide" volatility regime day (prior day's range in the
top percentile band). Horizon 15min. n=142. Source: Observatory v1 scan.

## Why this is a distinct candidate

Completes the regime-conditioning question OBS-FINDING-003 started:
H84 tested the open-bucket fade on NARROW-regime days and it failed.
This tests the mirror -- WIDE-regime days -- to see whether the effect
concentrates at the opposite end of the volatility spectrum instead
(wide days: level touches may reflect genuine breakout continuation
risk rather than mean-reversion, which would argue the opposite
direction; this finding keeps the same SHORT/fade direction as the
pooled cluster to test that directly, not to fish for a reversed
signal).

## Perspectives

- Path-to-Profitability Advisor: worth one clean test to close out the
  regime question (narrow tested, wide untested) rather than leaving
  it open -- if wide also fails, that's a clean "the effect is not
  regime-concentrated" conclusion, useful either way.
- Market Behavior Advisor: n=142 over a 15-min horizon is the smallest,
  shortest-horizon cell used yet in this pilot -- flagging low power up
  front, same caveat pattern as OBS-FINDING-002.
- Claude: agree, proceeding. This is deliberately the LAST candidate of
  this pilot round (round total: 4 findings, 5 hypotheses) regardless
  of outcome, per the 3-5 range Jason specified.

## Judgment

Reasonable, well-motivated completion of a question this pilot itself
raised (H84). Thin sample is the main risk to a clean read, disclosed
up front.

## Status

OPEN -- proceeding to hypothesis spec (H85), final candidate of round 1.
