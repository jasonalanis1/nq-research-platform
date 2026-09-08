# Mid-Morning Reference-Level Fade — Frozen Spec (H83 / exp-112)

Parent finding: OBS-FINDING-002 (research/studies/obs-finding-002-midmorning-reference-level-cluster.md).
Second candidate of the 3-5-candidate Observatory pilot.

## Setup

**Short signal only** (no long-side candidate cleared the Promising bar
in this bucket): during 10:30-12:00 ET, the FIRST bar (whichever level
touches first) whose High/Low range touches prior-day RTH high OR the
overnight session high, "normal" volatility regime day (reusing
volatility_conditioning's existing regime classification, unmodified)
-> SHORT.

**Entry:** touch bar's close. **Stop:** touch bar's high + `1.5 *
average 1-minute bar range over the trailing 20 bars` (identical buffer
convention to H81 -- deliberately NOT importing H82's excursion-derived
parameters, to keep this a clean first attempt on a new candidate).
**Target:** entry - `TARGET_R_MULTIPLE (1.35, unmodified)` * risk. Exit
via `backtest.simulate_trade` (unmodified). Cost:
`ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2 together, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Disclosed risk (from OBS-FINDING-002)

n is thin at the source (52-64 events per cell in the Observatory scan);
the trade-level n after entry/stop/target filtering will likely be
similar or smaller. A NO_DATA or PASS_TOO_THIN_FOR_PROSPECTIVE verdict
is an expected possible outcome, not a sign of a bug.

## Pre-commitment

One frozen attempt. Pass, thin pass, or fail -- moves to candidate #3
regardless of outcome, per the pilot design. A null or too-thin result
here is informative for the pilot itself (does the Observatory only
work in some time-of-day windows, not others).
