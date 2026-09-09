# Pre-NFP Overnight Short, Excursion-Derived Exits -- H114 / exp-129 Frozen Spec

Relationship to OBS-FINDING-012: first monetization attempt on the
newly-discovered pre-NFP overnight drift (credible, negative,
n=74, effect -14.83pts, ci_90 entirely below zero). This is a FRESH
hypothesis with the direction pre-registered from the Observatory
result (negative/short) -- not a same-run flip of hyp-000112, which
stays REJECTED on its own (wrong-direction vs. the ORIGINAL
literature-based pre-commitment). This spec's short direction is
itself now the pre-commitment, frozen BEFORE this hypothesis is run,
exactly as OBS-FINDING-009 -> H92/H93 worked.

## Disclosure: parameters ARE informed by the Discovery sample

Same disclosed technique as H82/H93: stop/target computed from the
median overnight maximum adverse/favorable excursion (MAE/MFE) of the
same 74 Discovery-slice NFP-day events, NOT from this hypothesis's own
trade outcomes, and NOT re-derived after seeing this hypothesis's own
result.

Computed once, frozen here: median overnight MAE (adverse, short) =
26.375 points, median overnight MFE (favorable, short) = 25.375
points. n=74 events. Note MAE > MFE slightly -- the raw excursions are
NOT stacked in the trade's favor even before considering win rate;
this is disclosed honestly rather than adjusted after the fact.

## Setup

Event: NFP day (first Friday of month, per pre-nfp-drift-design-spec.md).
**Entry:** prior trading day's RTH close (16:00 ET), SHORT.
**Stop:** entry + 26.375 points (fixed). **Target:** entry - 25.375
points (fixed). Exit: walks forward through the overnight window
(prior close to NFP-day RTH open) bar-by-bar via backtest.simulate_trade;
if neither level is hit, exits at NFP-day RTH open (time-based
fallback, matching the original Observatory measurement window). Cost:
ROUND_TRIP_COST_POINTS (unmodified, 0.75).

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R (same bar as every other hypothesis this project
has run).

## Risk note (flagged, not yet resolved)

This is the project's first OVERNIGHT-HOLD hypothesis with a
literal stop/target enforced across the full overnight window (H87-H93
family entered AT the open and resolved intraday). Overnight futures
positions carry gap risk our 1-min bar data can't fully capture
(a large move between bars could jump past the stop). This is noted
honestly as a real difference from every prior hypothesis in this
project, and the Discovery-stage result here should be read with that
caveat -- it doesn't block Step 1+2 testing, but it would need to be
addressed before any live authorization discussion (which is not yet
in scope regardless, per the promotion bar).

## Pre-commitment

This is the FIRST monetization attempt for OBS-FINDING-012. Per the
project's two-attempt limit, if this fails, ONE reshaped attempt
(different exit design, not a retuned stop/target) is allowed before
the line closes, same precedent as H92->H93.
