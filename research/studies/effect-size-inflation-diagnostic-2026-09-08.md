# Effect-Size Inflation Diagnostic (2026-09-08)

Process artifact, not a hypothesis test -- no ledger entry, same category as
`meta-review-2026-09-08.md`. Follow-up requested by the Path-to-Profitability
Advisor and approved by Jason 2026-09-08: compare each Discovery-stage
PROMISING point estimate/CI to what the corresponding pre-registered
Validation-slice test actually found, to check whether the promotion
screening is systematically letting inflated effects through.

## Method

Every hypothesis ever logged PROMISING at the Discovery stage that went on to
a pre-registered Validation-slice test (4 cases; excludes hyp-000003/5/7/8,
which were PROMISING→REJECTED same-slice logging corrections, not real
Discovery-to-Validation transitions).

## Findings

| Discovery (PROMISING) | Validation (REJECTED) | Discovery estimate | Validation estimate | Pattern |
|---|---|---|---|---|
| exp-053/hyp-000023 (NQ weekly trend, low-vol regime) | exp-054/hyp-000024 | mean +24.32 pts/wk, CI [3.66, 44.46] (n=111 weeks, only ~7 position flips -- effective n likely much smaller) | Only 8 low-vol weeks appeared in the entire Validation window -- too few to compute a CI at all | Underpowered retest, not a clean disproof -- but the Discovery "n=111" was already flagged by the Advisor as inflated (few truly independent stretches) |
| exp-055/hyp-000025 (trend lenses, weak-trend weeks excluded) | exp-056/hyp-000026 | beat-baseline fraction 0.268, CI (0.185, 0.357) -- entirely below 0.5 | mean net pnl +76.21, CI (-6.32, 156.20) -- crosses zero | Point estimate stayed directionally consistent (filter still looked good) but CI width exploded on fresh data -- statistical credibility, not direction, is what failed |
| exp-057/hyp-000027 (IB breakout, high-vol days excluded) | exp-058/hyp-000028 | beat-baseline fraction 0.4607, CI (0.4372, 0.4848) | mean R -0.0746, CI (-0.1910, 0.0433) | Point estimate flipped sign as well as losing credibility -- the Discovery "edge" didn't even point the right way out of sample |
| exp-061/hyp-000031 (ZN same-day lead on NQ) | exp-062/hyp-000035 | diff +0.001375 (log-return units), CI (0.000320, 0.002375) -- tight, entirely above zero | mean net pnl +5.9971 points, CI (-10.75, 22.29) -- wide, crosses zero | Same direction, but CI width increased roughly 7-8x in relative terms and swallowed zero |

## Reading

All 4 cases show the same shape: the Discovery-stage CI was narrow enough to
call "statistically credible," but the effect did not hold up with anything
like that precision on fresh data -- in 3 of 4 cases the CI simply widened
past zero on directionally similar data; in 1 of 4 (IB breakout) the point
estimate itself flipped sign. None of the four failures look like "bad luck
on an otherwise real effect" -- they look like Discovery-stage noise that
cleared a bar built for detecting real, stable effects.

This is consistent with, not a repeat of, the Advisor's methodology
critique: the promotion bar's CI check is being computed correctly each
time, but Discovery-stage searches (regime splits, exclusion filters,
collective-evidence buckets) generate enough candidate cuts that some will
clear a 90% CI by chance even with no real effect underneath, and the
project's multiple-testing safeguards (disclosed batch IDs, eligibility
floors) reduce but do not eliminate that risk. The practical implication
for the intraday phase: pre-registering a small fixed batch is necessary
but, based on this sample, not sufficient on its own to prevent another
round of "Discovery-promising, Validation-null" -- treat any Discovery
PROMISING result on the new intraday batch as provisional until its
single prospective test, same as always, and do not treat a narrow
Discovery-stage CI alone as strong evidence.

## Bottom line

No process change is being made unilaterally from this diagnostic (per
standing rule, any change to the promotion bar itself needs its own
explicit ask to Jason). This is filed as supporting evidence for the
Advisor's "methodology, not just data ceiling" read of the 0/43 result,
and as context for calibrating how much confidence to place in results from
the incoming intraday-behavior batch.
