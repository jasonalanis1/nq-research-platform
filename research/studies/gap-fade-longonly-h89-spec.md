# Gap-Down Fade, Long-Only — Frozen Spec (H89 / exp-118)

Parent: H87 (hyp-000087), reshaped per its own near-miss. One
materially different, disclosed reattempt -- same precedent as
H81->H82.

## Disclosure and rationale

H87 combined a gap-down-fade LONG leg (n=128, mean_r=+0.068,
economically meaningful, ci_90 narrowly spanning zero) with a
gap-up-fade SHORT leg (n=146, mean_r=-0.085, credibly losing) as one
hypothesis. The stability check (research/studies/h87-stability-check-spec.md,
run before this spec was written) found the LONG leg's edge is stable
across both halves of the Discovery period (first half n=64
mean_r=+0.056, second half n=64 mean_r=+0.080) -- not concentrated in
one sub-period, i.e. not the effect-size-inflation pattern seen
earlier in this project's multi-day pullback work. The short leg was
never stability-checked and its own Observatory finding (OBS-FINDING-
006) already flagged it as the weaker-measured mirror.

This hypothesis tests the LONG leg ALONE, dropping the short leg
entirely as a separate, weaker-evidenced mechanism rather than
combining it with a real one. Same signal, entry, stop, and target as
H87's long leg -- NO parameter retuning, only the removal of the
short leg from the combined statistic.

## Setup (identical to H87's long leg)

Gap-down open (>= 0.5x prior-day RTH range) -> LONG at open bar close.
Stop: entry - `1.0x daily ATR(14)`. Target: entry + `1.35 * risk`.
Same-day exit only, cost 0.75pt round-trip.

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R. (Numerically this will reproduce H87's long-leg
figures exactly -- the only change is that this is now evaluated and
logged as its OWN hypothesis rather than diluted by the short leg.)

## Pre-commitment

This is the final reattempt for the gap-fade behavior (H87 + H89 = two
attempts, same as the H81/H82 precedent). If this also fails to clear
the CI-entirely-above-zero bar, the behavior is closed -- no H90
variant of gap-fade. If it passes Step 1+2 (n=128 >= MIN_PROSPECTIVE_N
=40), it proceeds to the standard next step: a single pre-registered
Validation-slice prospective test, per this project's promotion
process -- the point at which Jason gets looped in regardless of
outcome, per his own standing $-and-90%-bar trigger.
