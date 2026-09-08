# Pre-Move Behavior, Target Sensitivity Check — Frozen Spec (exp-106)

## Why this test

All 6 fresh-behavior signals tested today (exp-100/101/102/103/104/105)
came back credibly LOSING at the project's standard `TARGET_R_MULTIPLE =
1.35`. Before designing more distinct behaviors, this checks whether the
fixed 1.35R target itself (not the underlying trigger idea) is the
reason -- these are short-horizon, single-day, 1-minute-bar reactive
entries, a different animal from the swing-style setups 1.35R was
originally used for (imported from `detect_level_sweep.py`, a level-
sweep-reversal setup with wider swing-based stops). A short-fuse entry
might reach a smaller target far more often than a 1.35R one, changing
the win rate enough to flip net expectancy even with the same stop.

## Method

Reuses the EXACT SAME detection logic and stop placement already run
today for all 6 signal streams (`detect_vacuum_signals_for_day`,
`detect_alignment_signal_for_day`, `fade_signal`,
`detect_volume_imbalance_signal_for_day`,
`detect_prior_close_rejection_signal_for_day` -- all unmodified,
imported directly). Only the TARGET price changes: for each already-
detected signal, target is recomputed at `TARGET_R_MULTIPLE_GRID =
[0.5, 0.75]` (vs. today's already-reported 1.35 baseline) while the
STOP (and therefore the R-unit itself) stays exactly as originally
detected. Re-run `simulate_trade` at each grid point. Same bootstrap
method (N_BOOTSTRAP=3000, seed=7, 90% CI on `r_multiple_net`), same
credibility bar (CI entirely above zero, mean R >= 0.05).

## This is diagnostic, not a new pre-registered hypothesis search

This is checking a specific, narrow question (is the loss target-driven)
using data already collected today -- not a new multiple-testing
exposure, since no new detection logic or thresholds are being searched.
If a signal x target combination shows a credible, economically
meaningful result here, it is NOT treated as promotable on the spot --
it gets its own single freshly-pre-registered Discovery run (this
project's existing "at any specific R-multiple" would technically be a
new degree of freedom no matter how it's framed) plus the standard
Validation-slice prospective test before any promotion consideration.
This run's job is only to tell us whether it's worth doing that at all.

## Decision rule

If NONE of the 6 signals x 2 new targets shows a credible positive
result, that closes the "target-mismatch" theory -- the 6 fresh
behaviors tested today are genuinely dead at any of the R-multiples
checked, not just the 1.35R default, and further work in this direction
should design new detection logic, not just retarget existing signals.
