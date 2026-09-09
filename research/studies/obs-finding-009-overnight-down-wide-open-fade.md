# OBS-FINDING-009: Overnight-Down-Move Fade in Wide-Volatility Regime, Opening Hour

Written per the protocol addendum, before any hypothesis spec.

## Definition

Event: day's overnight session (prior 16:00 close -> current 09:30
open) moved DOWN, AND the prior day was classified "wide" (top-20th-
percentile trailing-20-day range, unchanged definition from
volatility_conditioning.py). Outcome: RTH forward return from the open
during the 09:30-10:30 bucket, vs. baseline (unconditional RTH bars in
the same regime/bucket). Source: Observatory v5 scan, 36 combinations,
Discovery data.

## Measurement

n=140. Effect is POSITIVE and consistent across 1/3/5/10-minute
horizons (+4.35, +7.12, +7.33, +6.63 points), all credible (90% CI
entirely above zero at every horizon). Shape: quick initial move
(1min) that continues building through 3-5min then holds/plateaus by
10min, rather than decaying -- consistent with an initial reversion
that then stabilizes, not a one-bar artifact. Cost-relevant: the
ATR-normalized effect at 3-10min horizons (0.052-0.057) clears the
project's cost-viability floor (0.05) -- comparable in relative size
to H87/H89's near-miss, in a larger sample (n=140 vs n=128) and with a
cleaner, wider CI margin above zero. The 15-30min horizons decay back
toward baseline (Weak, cost-dominated) -- the effect is specifically an
opening-hour phenomenon, not a持续 all-day drift.

## Judgment

Real-looking, not an obvious scan artifact: 4 consecutive horizons
(1/3/5/10min) all credible with the same sign and a coherent
build-then-plateau shape, not an isolated single-horizon spike.
Plausible mechanism: an overnight decline following an already-volatile
prior day plausibly overshoots on thin overnight liquidity, and RTH
opening-hour liquidity/participation corrects part of that overshoot --
ordinary opening-hour mean-reversion, same general family as
OBS-FINDING-001 (opening-hour reference-level fade) but keyed on
overnight DIRECTION+regime rather than a specific price level.

Caveat: descriptive evidence from a 36-combination scan (fewer
combinations than v1's 348, so less multiple-testing exposure, but
still exploratory, not confirmatory). Restricting to the "wide" regime
means this is a relatively rare setup (140 events across 2101 Discovery
days, roughly 1 in 15 days) -- a real Layer 2 hypothesis needs to
account for that low frequency in any economic assessment (few trades
per year even if profitable per-trade).

## Status

Real, cost-viable, multi-horizon-consistent candidate. Proceeding to a
frozen monetization hypothesis (parent_finding_id: OBS-FINDING-009).

## Outcome

Two monetization attempts: H92 (ATR-scaled stop, same convention as
H87/H89) failed Step 1+2 (n=139, mean_r=+0.043, ci_90 spans zero). H93
(excursion-derived fixed stop/target, same technique as H82) passed
Step 1+2 on Discovery -- the first candidate in this project's history
to do so -- but the pass was marginal (ci_90 lower bound ~0, essentially
touching zero) and did NOT replicate on the pre-registered Validation-
slice prospective test (n=50, mean_r=-0.120, ci_90=(-0.366, 0.176) --
negative point estimate, spans zero). Per pre-commitment and the
two-attempt limit, this closes OBS-FINDING-009 to further monetization
attempts. The finding itself (the underlying Observatory measurement)
is not falsified by this -- consistent with the project's standing
principle that a failed trade design doesn't disprove the behavior --
but as with every other candidate tried so far, no tested trade
structure has captured it profitably net of cost and out of sample.
