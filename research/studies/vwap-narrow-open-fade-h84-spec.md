# VWAP Narrow-Regime Open Fade — Frozen Spec (H84 / exp-113)

Parent finding: OBS-FINDING-003. Third candidate of the pilot.

## Setup

**Short signal only:** during 09:30-10:30 ET, on "narrow" volatility
regime days only (prior_day_narrow per volatility_conditioning,
unmodified), the FIRST bar (i >= 5 bars into RTH, matching the
Observatory's own VWAP-stabilization rule) whose High/Low range touches
session VWAP -> SHORT.

**Entry:** touch bar's close. **Stop:** touch bar's high + `1.5 *
average 1-minute bar range over the trailing 20 bars` (same convention
as H81/H83). **Target:** entry - `1.35 * risk` (TARGET_R_MULTIPLE,
unmodified). Exit via `backtest.simulate_trade` (unmodified). Cost:
`ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Pre-commitment

One frozen attempt. Pass, thin pass, or fail -- this is candidate #3
of the 3-5-candidate pilot; per Jason's explicit instruction the pilot
evaluation runs after this candidate regardless of outcome (3 is within
the "roughly 3-5" range he specified), rather than automatically
continuing to a 4th candidate without a checkpoint.
