# Overnight-High Wide-Regime Open Fade — Frozen Spec (H85 / exp-114)

Parent finding: OBS-FINDING-004. Fourth/final candidate of pilot round 1.

## Setup

**Short signal only:** during 09:30-10:30 ET, on "wide" volatility
regime days only (prior_day_wide per volatility_conditioning,
unmodified), the FIRST bar whose High/Low range touches the overnight
session high -> SHORT.

**Entry:** touch bar's close. **Stop:** touch bar's high + `1.5 *
average 1-minute bar range over the trailing 20 bars` (same convention
as H81/H83/H84, for cross-candidate comparability). **Target:** entry -
`1.35 * risk` (TARGET_R_MULTIPLE, unmodified). Exit via
`backtest.simulate_trade` (unmodified). Cost:
`ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Pre-commitment

Final candidate of pilot round 1 (4 findings, 5 hypotheses total across
the round). Whatever the result, the full-round methodology verdict
(research/studies/observatory-pilot-evaluation-round1.md) is finalized
after this, not chased with a 6th candidate without a new, separately
motivated reason.
