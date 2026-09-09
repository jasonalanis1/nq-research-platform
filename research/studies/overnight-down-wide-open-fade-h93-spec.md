# Overnight-Down Wide-Regime Open Fade, Excursion-Derived Exits — Frozen Spec (H93 / exp-121)

## Relationship to H92

H92 tested the same behavior (OBS-FINDING-009) with the ATR(14)-scaled
stop convention (1.0x ATR stop, 1.35x risk target) inherited from
H87/H89. It failed (n=139, mean_r=+0.043, ci_90=(-0.059, 0.136) --
spans zero). Per the project's one-reshaped-attempt precedent
(H81->H82, H87->H89), this is a genuinely different monetization
design for the SAME behavioral observation -- not a retune of H92's
ATR multiple -- frozen before looking at this hypothesis's own result.

## Disclosure: parameters ARE informed by the Discovery sample

Same disclosed technique as H82: stop/target computed from the median
15-minute maximum adverse/favorable excursion (MAE/MFE) of the same
139-140 Discovery-slice events, NOT from H92's trade outcomes, and NOT
re-derived after seeing this hypothesis's own result.

Computed once, frozen here: median 15-min MAE = 13.125 points
(adverse, price moving down from entry), median 15-min MFE = 19.25
points (favorable, price moving up from entry). n=140 events.

## Setup

Identical event detection to H92 (unchanged): overnight-down move
following a wide-regime prior day -> LONG at the 09:30 open.
**Entry:** open bar's close. **Stop:** entry - 13.125 points (fixed).
**Target:** entry + 19.25 points (fixed). Exit via
`backtest.simulate_trade` (unmodified). Cost: `ROUND_TRIP_COST_POINTS`
(unmodified, 0.75).

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Pre-commitment

This is the second and FINAL monetization attempt for OBS-FINDING-009,
per the project's two-attempt limit. If this fails, the finding stands
as documented measurement (per protocol) but the behavior line is
CLOSED to further monetization attempts on this event definition,
exactly as the gap-fade line was closed after H81/H82 and H87/H89.
