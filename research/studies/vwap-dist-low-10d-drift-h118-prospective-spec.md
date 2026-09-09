# VWAP-Distance-Low, 10-Day Drift -- H118 Prospective Validation Spec

Frozen 2026-09-09, immediately after H118's Discovery-slice pass
(research/studies/vwap-dist-low-10d-drift-h118-spec.md). Single
pre-registered Validation-slice prospective test.

## What is being tested
Exactly the H118 Discovery-slice definition, unmodified: long entry at
RTH reference close on a day whose vwap_dist_vs_atr falls in the LOW
tercile, exit at RTH reference close 10 trading days later, no
stop/target, one round-trip cost, R-multiple against entry-day ATR(14).

## Frozen from Discovery -- nothing refit here
Bucket edges ([-inf, -0.0460, 0.1471, inf]) frozen exactly as computed
on the full Discovery sample. Reused unmodified here.

## Discovery-slice result being tested prospectively
n=554, mean_r_multiple_net=+0.617, ci_90=[0.453, 0.785],
statistically_credible=True, economically_meaningful=True.
Verdict: DISCOVERY_PASS.

## Pre-registered direction
POSITIVE net R-multiple.

## Promotion bar (unchanged)
90% bootstrap CI on R-multiple entirely above zero, AND economically
meaningful. A pass here, combined with the Discovery pass, clears the
full promotion bar -- the case that requires looping Jason in. A null
here closes attempt 1 of 2 for this candidate.

## Method
Validation-slice data only. Bootstrap 90% CI (N_BOOTSTRAP=3000, seed=7).
No parameter changes from the Discovery-slice script.
