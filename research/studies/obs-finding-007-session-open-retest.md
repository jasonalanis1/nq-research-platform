# OBS-FINDING-007: Session-Open Retest, Normal Regime, Mid-Morning Bucket

Per the Behavioral Finding protocol. Measurement only -- no trade design.

## Definition

Event: first re-touch of today's own 09:30 RTH open price, after price
has moved at least 1x the trailing-20-bar average range away from it,
during 10:30-12:00 ET ("mid_morning" bucket), "normal" volatility
regime. Horizons 15min (n=177, effect=+1.74, ci_90=(0.19,3.34)) and
30min (n=177, effect=+2.60, ci_90=(0.34,4.92)). Source: Observatory v2
scan.

## Why this candidate

Untested family (session_open events were part of v2 but not yet
converted to a hypothesis), reasonable n, decent CI clearance at two
horizons, and a purpose beyond the finding itself: this is the second
test of the ATR-scaled-stop convention adopted after H87
(research/studies/observatory-exit-convention-update.md), to check
whether that improvement generalizes.

## Perspectives

- Path-to-Profitability Advisor: the pooled event doesn't specify
  direction (it fires whenever price returns to the open, regardless
  of which way it departed) -- needs a directional design, same lesson
  learned from H86's momentum-conditioning approach, to avoid an
  ambiguous-mechanism trade.
- Market Behavior Advisor: agrees; proposes conditioning on the
  direction of the ORIGINAL departure from the open (proxied by
  close 5 bars before the retest vs. the open price) -- if price was
  above the open and pulled back to it, treat the open as
  support-in-an-uptrend (LONG); if price was below and rallied back to
  it, treat it as resistance-in-a-downtrend (SHORT). This tests a
  specific, statable mechanism (open acting as an intraday
  support/resistance pivot) rather than "always long."
- Claude: agree, proceeding with that directional design.

## Judgment

Reasonable measurement, mechanism ambiguous until direction-conditioned
-- exactly the kind of caveat this protocol exists to surface before
a trade design gets built around an unstated assumption.

## Status

OPEN -- proceeding to hypothesis spec (H88), second test of the
ATR-scaled-stop convention.
