# Pre-Move Behavior, Fresh Setups Batch 2 — Fade Variants — Frozen Spec (exp-102/103)

## Why this follow-up is legitimate, not a retune

exp-100 and exp-101 (batch 1) didn't just fail to clear the bar -- both
came back CREDIBLY LOSING (90% CI entirely below zero on net R-multiple).
That is itself informative: a systematic negative bias in a specific,
pre-defined direction is different information from "no effect," and
testing the OPPOSITE direction of the same, already-detected signal is a
standard, legitimate distinct hypothesis (same precedent this project
already uses for subgroup/direction flips -- e.g. hyp-000063's COT
signal itself used the Discovery result to set `long_group=-1.0`, a
fade of the naive direction, before its own separate prospective test).
This is NOT retuning exp-100/101's thresholds after a bad result --
detection logic, lookback, and thresholds are 100% unchanged; only the
trade direction at each already-detected signal event is reversed.

## exp-102: Volume Vacuum FADE

Same detection as exp-100 (unchanged: `VACUUM_LOOKBACK_BARS=60`,
`VACUUM_PCTL=20`, `VACUUM_WINDOW_BARS=5`, `VACUUM_WATCH_BARS=15`) --
same signals, same entry price (breakout bar's close). Direction
reversed: a close above the vacuum range's high is now a SHORT (fading
back into the range), a close below the low is now a LONG. Stop and
target are mirrored across the entry price at the same |risk| distance
as the original (stop = entry -/+ original risk in the new direction;
target = entry +/- 1.35R in the new direction) -- keeps stop-distance
and R-target identical in magnitude to exp-100, isolating direction as
the only changed variable.

## exp-103: Multi-Timeframe Trend Alignment FADE

Same detection as exp-101 (unchanged: 15-min/60-min/day-so-far
alignment at the same hourly checkpoints). Direction reversed: an
alignment that would have gone long now goes short and vice versa,
entered at the same bar/price as exp-101, stop/target mirrored at the
same |risk| distance in the new direction.

## Method

Identical to batch 1: Step 1+2 together (real entry/stop/target, costed
via `backtest.simulate_trade`, `ROUND_TRIP_COST_POINTS` unmodified).
Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000, seed=7, 90% CI on
`r_multiple_net`. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Multiple-testing disclosure

2 pre-registered fade variants, one shared `search_batch_id`
(`batch-2026-09-08-pre-move-behavior-2-fade`), run together, no further
follow-up variants after seeing these results without a new
independently motivated reason.

## Decision rule / pre-commitment

Same as batch 1: a credible, economically-meaningful PASS with n >= 40
gets its own single Validation-slice prospective test before any
promotion consideration. If BOTH fades also fail (whether null or
credibly losing again), that closes the volume-vacuum and
trend-alignment mechanisms entirely (both directions now tested) --
report to Jason rather than spinning further variants of these same two
ideas; any further "fresh behavior" search should look for genuinely
different behaviors, not more direction flips of these two.
