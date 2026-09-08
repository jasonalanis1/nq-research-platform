# Market Behavior Observatory v3 — Frozen Design Spec

Path A of the two-track plan Jason approved (run diagnostics on why
measured behaviors aren't monetizing, AND keep generating candidates
in parallel). Extends v1/v2 with a THIRD event family, structurally
different from both: v1/v2 events are all "price touches a specific
level." v3 events are OCCURRENCES -- something happens (a gap, an
unusual volume bar) rather than a level being crossed. Baseline
construction, ranking rules, horizons, time buckets, regime dimension
all unchanged from v1/v2.

## New event types (v3)

1. **overnight_gap**: the 09:30 RTH open vs. the prior RTH close,
   where |gap| >= 0.5x the prior day's own RTH range (a "meaningful"
   gap, scaled to that day's typical movement rather than a fixed point
   threshold). Direction (gap up / gap down) tracked separately as
   `overnight_gap_up` / `overnight_gap_down`. Measured once per day, at
   the open bar.
2. **volume_spike**: any RTH bar whose volume is >= 3x the trailing
   20-bar average volume, first occurrence per day. Tests reaction to
   an unusual participation burst, independent of any price level.

## Handoff

Same as v1/v2: any Promising/Interesting candidate gets its own
Behavioral Finding (OBS-FINDING-NNN) before any hypothesis spec.
