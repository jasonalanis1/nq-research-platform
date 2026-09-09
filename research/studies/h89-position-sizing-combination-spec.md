# H89 + Position-Sizing Combination Test — Frozen Spec (exp-127)

## Rationale

Every prior attempt to use the project's 2 validated volatility facts
on H87/H89 tested whether they changed the WIN RATE / mean R-multiple
(overlay screen 3, 2026-09-09: no credible split). That is not the
only way to combine validated knowledge with a near-miss candidate.
This test asks a different, previously untried question: does applying
the already-validated, already-built position_size_multiplier()
(inverse-volatility sizing, from src/volatility_conditioning.py) to
H89's trades change the RISK-ADJUSTED profile (variance, Sharpe-style
ratio) of the same trade series, even if the raw mean R-multiple is
mechanically similar by construction?

This is a genuine combination of 2 already-validated, already-built
project components (H89's signal, the sizing module) -- not a new
Observatory candidate, not a retune of either component.

## Method

Regenerate H89's exact Discovery-slice signal/entry/stop/target
(unchanged). For each trade date, look up
get_volatility_conditioning()'s expected_range_multiplier (built from
the SAME 2 validated facts, unchanged) and compute
position_size_multiplier() from it (unchanged, clipped 0.5x-1.5x).
Compare two series: (a) UNWEIGHTED R-multiples (H89 as originally
tested), (b) SIZE-WEIGHTED R-multiples (r_multiple * size_multiplier
for each trade). Report mean, std, and a simple Sharpe-style ratio
(mean/std) for both, plus the bootstrap CI of the size-weighted mean
(same 90% CI convention as every other test).

## Pre-commitment

No parameter of H89 or the sizing module is changed. This is
diagnostic -- even a positive result does not itself constitute a new
promotable hypothesis (position sizing changes risk profile, not the
underlying edge, and this project's promotion bar is defined on
R-multiple, not Sharpe) -- but it answers the combination question
honestly, one way or the other, and would inform whether combining
validated facts is a fruitful direction to keep pursuing.
