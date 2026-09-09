# OBS-FINDING-010: Multi-Mechanism Corroboration Strengthens Opening-Hour Fade

Written per the protocol addendum, before any hypothesis spec.

## Definition

On days where 2 or more of 3 independently-discovered mechanisms fire
simultaneously (gap-magnitude, OBS-FINDING-006; overnight-down+wide-
regime, OBS-FINDING-009; opening-hour reference-level touch,
OBS-FINDING-001 -- all unchanged, unmodified definitions), the RTH
10-minute-from-open forward return differs from days where 0-1 fire.
Source: collective-evidence pilot v2 (exp-123), Discovery data.

## Measurement

n=397 (2+ conditions) vs n=920 (0-1 conditions), out of 1317 total
days with usable data. Mean forward return: +1.43pts (2+ group) vs.
-1.77pts (0-1 group), diff=+3.21pts, ci_90=(0.68, 5.91) -- entirely
above zero, credible. The 2+ group trends positive/flat over the first
10 minutes; the 0-1 group trends negative.

## Judgment

Real corroboration signal, genuinely different from pilot v1 (which
tested correlated variants of one signal and found nothing that
survived): these three mechanisms are computed from unrelated inputs
(gap size, overnight direction+regime, absolute price level) and were
discovered independently across 3 different Observatory scan
generations, so their agreement on the same days is a meaningful
signal rather than restating one underlying pattern three times.

**Important disclosed limitation, not yet resolved:** this measurement
does not itself specify a single trade DIRECTION. The 3 source
conditions do not all imply the same fade direction (cond_gap fires on
either a large up or down gap; cond_overnight only fires on
overnight-down; cond_level only checks upper-level touches, implying a
short fade). The "2+ conditions" bucket therefore mixes days with
different implied trade directions, yet still shows a coherent
positive-return effect -- which is itself informative (corroboration
matters even across mixed-direction setups) but is NOT yet a
directional monetization hypothesis. Before any hypothesis spec, this
needs a follow-up measurement that assigns each 2+ day an implied fade
direction (majority vote or a stricter same-direction-only definition)
and re-measures the effect conditioned on direction -- a distinct,
disclosed next step, not a retune of this finding's own conditions.

## Status

Real, credible corroboration effect at the measurement layer. NOT yet
ready for a hypothesis spec -- the direction-assignment follow-up
above is required first, per the honesty standard this project holds
every other candidate to (no hypothesis is written from an ambiguous
or underspecified signal).
