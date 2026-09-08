# Market Behavior Observatory v2 — Frozen Design Spec

Extends v1 (research/studies/observatory-v1-design-spec.md) with a
structurally different event family, per the pilot-round-1 conclusion:
5 hypotheses against reference-level touch-and-fade all failed: before
judging the Observatory methodology itself, test whether it does
better on a different kind of behavior. Everything else (baseline
construction, non-p-value ranking, horizons, time buckets, regime
dimension) is UNCHANGED from v1 -- only EVENT_TYPES changes.

## New event types (v2)

1. **round_number**: first touch of the nearest NQ round level in
   50-point increments (e.g. 15000, 15050, 15100) during the session,
   computed from the day's own opening price forward (no lookahead --
   the nearest round level is determined at each bar from price
   already seen). Tests a pure "psychological level" story, independent
   of any prior-session reference price.
2. **prior_swing_high / prior_swing_low**: the most recent local
   pivot high/low in the prior 20 RTH bars (a bar whose high/low is the
   max/min of a +/-3-bar window around it, standard swing-pivot
   definition), first touched intraday. Tests short-term technical
   structure rather than session-boundary levels.
3. **session_open**: first RE-touch of today's own 09:30 RTH open price
   after price has moved at least 1x the trailing-20-bar average range
   away from it. Tests "return to today's open" as a distinct
   mean-reversion anchor from yesterday's or overnight levels.

Formal first-touch, baseline-relative measurement, and non-p-value
Promising/Interesting/Weak/No-meaningful-difference ranking rules are
identical to v1 -- see that spec for the full definitions.

## Handoff

Same as v1: the Observatory itself never designs a trade. Any Promising
or Interesting candidate this scan surfaces gets its own Behavioral
Finding (OBS-FINDING-NNN) written and frozen, independent of any trade
design, before a hypothesis spec is drafted -- per the protocol
addendum from pilot round 1.
