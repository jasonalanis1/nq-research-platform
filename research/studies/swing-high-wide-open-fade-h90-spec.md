# Swing-High Wide-Regime Open Fade — Frozen Spec (H90 / exp-119)

Parent finding: OBS-FINDING-008. First candidate selected via the new
monetization pre-screening rule (large point-effect, not just
statistically distinguishable).

## Setup

During 09:30-10:30 ET, "wide" volatility regime days only, the FIRST
bar whose High/Low range touches the most recent confirmed swing-pivot
high (20-bar lookback, +/-3-bar pivot definition, identical to
Observatory v2's detection) -> SHORT (fade).

**Entry:** touch bar's close. **Stop:** entry + `1.0 * daily ATR(14)`
(current default convention). **Target:** entry - `1.35 * risk`. Exit
via `backtest.simulate_trade` (unmodified, same-day only). Cost:
`ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Pre-commitment

One frozen attempt, selected specifically to test the new screening
rule on this session's strongest-by-points candidate. Regardless of
outcome, this is the last hypothesis before a full session wrap-up.
