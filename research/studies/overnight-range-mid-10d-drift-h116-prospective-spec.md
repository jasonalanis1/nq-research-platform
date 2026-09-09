# Overnight-Range-Moderate 10-Day Drift -- H116 Prospective Validation Spec

Frozen 2026-09-09, immediately after H116's Discovery-slice pass
(research/studies/overnight-range-mid-10d-drift-h116-spec.md). Single
pre-registered Validation-slice prospective test, per the Research
Integrity Protocol (Discovery -> Validation -> Holdout; frozen specs
before implementation; no retuning after a null result).

## What is being tested

Exactly the H116 Discovery-slice definition, completely unmodified:
long entry at RTH reference close on a day whose overnight_range_vs_atr
falls in the MIDDLE tercile, exit at RTH reference close 10 trading
days later, no stop/target, one round-trip cost, R-multiple against
entry-day ATR(14).

## Frozen from Discovery -- nothing refit here

The tercile bucket edges for overnight_range_vs_atr are frozen exactly
as computed on the full Discovery sample in H116's Discovery-slice
script (src/study_overnight_range_mid_10d_drift_h116.py). This
Validation-slice test reuses those SAME edges -- it does not recompute
percentiles on Validation data. Refitting bucket edges on the
Validation slice would defeat the entire purpose of an out-of-sample
test.

## Discovery-slice result being tested prospectively

n=435, mean_r_multiple_net=+0.682, ci_90=[0.506, 0.854],
statistically_credible=True, economically_meaningful=True (>=0.05R).
Verdict: DISCOVERY_PASS.

## Pre-registered direction

POSITIVE net R-multiple (matches Discovery-slice sign and every prior
exploratory pass).

## Promotion bar (unchanged, applied here for real)

90% bootstrap CI on R-multiple entirely above zero, AND economically
meaningful (mean >= 0.05R). This is the ONE pre-registered prospective
test required by the protocol before promotion can be considered. A
pass here, combined with the Discovery-slice pass, clears the full
promotion bar and requires looping Jason in per the project's standing
exception. A null here closes this specific frozen definition -- per
the 2-attempt limit, one further differently-motivated attempt on this
candidate is permitted before the line is closed to LEARN.

## Method

Validation-slice data only (data_split.get_validation_data). Bootstrap
90% CI (N_BOOTSTRAP=3000, seed=7, identical convention). No parameter
changes of any kind from the Discovery-slice script.
