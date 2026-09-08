# H87 Stability Check — Frozen Diagnostic Spec

Not a new hypothesis, not a retune. H87's long leg (gap-down fade,
n=128, mean_r=+0.068, ci_90 narrowly spans zero) is this project's
closest near-miss. Before treating it as a real, worth-revisiting
signal, check whether the positive edge is stable across the Discovery
period or concentrated in one sub-period (the same effect-size-
inflation check applied earlier in this project to the multi-day
pullback setup, exp-108/109).

## Method

Rerun H87's long-leg signal detection UNCHANGED (same gap threshold,
same ATR-scaled stop/target). Split the resulting trade list
chronologically into first-half and second-half of the Discovery
period (by trade date, not by count). Report mean R-multiple and n for
each half separately. No CI recomputation needed for this diagnostic --
sign and rough magnitude consistency is the question, not a fresh
statistical test.

## Reading this result

- Both halves positive, similar magnitude -> the near-miss is a stable,
  real (if still statistically inconclusive) effect -- worth a genuine
  prospective-style re-test as a distinct next step.
- One half strongly positive, other flat/negative -> concentrated,
  likely an artifact of a specific market period -- treat the near-miss
  as noise, same conclusion as if it had failed outright.
