# Location-in-Range-Low, Uptrend-Conditioned, 10-Day Drift -- H117 Prospective Validation Spec

Frozen 2026-09-09, immediately after H117's Discovery-slice pass
(research/studies/location-in-range-low-uptrend-10d-drift-h117-spec.md).
Single pre-registered Validation-slice prospective test, per the Research
Integrity Protocol.

## What is being tested
Exactly the H117 Discovery-slice definition, unmodified: long entry at
RTH reference close on a day where location_in_range falls in the LOW
tercile AND trailing-60-day trend is positive, exit at RTH reference
close 10 trading days later, no stop/target, one round-trip cost,
R-multiple against entry-day ATR(14).

## Frozen from Discovery -- nothing refit here
Both the location_in_range tercile bucket edges and the uptrend
threshold (trailing 60-day return > 0) are frozen exactly as computed
on the full Discovery sample in H117's Discovery-slice script. This
test reuses those same edges/threshold -- no recomputation on
Validation data.

## Discovery-slice result being tested prospectively
n=342, mean_r_multiple_net=+0.451, ci_90=[0.223, 0.679],
statistically_credible=True, economically_meaningful=True.
Verdict: DISCOVERY_PASS.

## Pre-registered direction
POSITIVE net R-multiple.

## Promotion bar (unchanged)
90% bootstrap CI on R-multiple entirely above zero, AND economically
meaningful (mean >= 0.05R). A pass here, combined with the Discovery
pass, clears the full promotion bar -- the one case in this pipeline
that requires looping Jason in. A null here closes attempt 1 of 2 for
this candidate.

## Method
Validation-slice data only. Bootstrap 90% CI (N_BOOTSTRAP=3000, seed=7).
No parameter changes from the Discovery-slice script.
