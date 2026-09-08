# OBS-FINDING-002: Mid-Morning Reference-Level Touch Cluster

Per the Behavioral Finding protocol (observatory-finding-protocol-addendum.md).
Measurement only -- no trade design.

## Definition

Event: first touch (10:30-12:00 ET, "mid_morning" bucket) of prior-day
RTH high OR overnight session high, "normal" volatility regime.
Source: Observatory v1 scan (research/studies/observatory-v1-design-spec.md),
348 combinations, Discovery data.

## Measurement

Two Promising cells, same mechanism (mid-morning touch of an upper
reference level), different levels/horizons:
- `overnight_high normal mid_morning`, horizons 3min and 30min, n=64.
- `prior_day_high normal mid_morning`, horizon 30min, n=52.
Both cells' effect direction is below-baseline (fade), consistent with
the open-bucket cluster's shape but in a later time window. Treated as
ONE finding (same mechanism, two reference levels) per protocol.

## Perspectives (staff-meeting takes folded in per Jason's efficiency instruction)

- Path-to-Profitability Advisor: structurally distinct from the closed
  open-bucket cluster (different time-of-day) -- a genuinely new test
  of whether the Observatory generalizes, which is the point of the
  pilot.
- Market Behavior Advisor: n=52-64 is thin. Even a real effect may not
  clear n=40 for prospective testing after Discovery-slice attrition
  from a costed entry/stop/target. Flagging this now, before any
  hypothesis is built, so a thin-sample result isn't a surprise later.
- Claude: agree with combining into one finding. Proceeding to a
  hypothesis spec with the sample-size caveat disclosed up front.

## Judgment

Plausible-but-thinner version of the same mean-reversion-off-reference-
levels mechanism as OBS-FINDING-001, shifted later in the session.
Sample size is the primary risk to a monetization attempt reaching a
statistically meaningful test, not the effect's plausibility. Not an
obvious scan artifact (consistent direction across 2 levels), but the
smaller n means more weight should go on whether ANY effect is
detectable at all (Step 1+2 credibility) than on precise effect size.

## Status

OPEN -- proceeding to hypothesis spec (H83) using the same generic
buffer-stop/1.35R convention as H81 (not H82's excursion-derived
design, to keep this a clean first attempt on a new candidate rather
than importing a previously-tuned parameter set).
