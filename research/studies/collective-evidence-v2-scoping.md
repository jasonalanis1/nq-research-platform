# Collective-Evidence Pilot v2 -- Scoping (exp-123)

## Provenance and what's different from pilot v1

Pilot v1 (hyp-000025/027, 2026-09-07) explicitly disclosed its own
scope limit: it aggregated correlated VARIANTS of one underlying
signal (4 versions of the same trend momentum computation; 4 exit-rule
variants of the same intraday setups) -- a dry run of the aggregation
machinery, not a real test of independent corroboration. Both failed
their prospective test.

This pilot uses three GENUINELY INDEPENDENT mechanisms discovered by
the Observatory across different scan generations, sharing no
underlying signal computation:
1. **Gap-magnitude fade** (OBS-FINDING-006 / H87-H89): overnight gap
   size relative to prior day's range.
2. **Overnight-direction fade** (OBS-FINDING-009 / H92-H93): overnight
   move direction, conditioned on prior-day volatility regime.
3. **Opening-hour reference-level fade** (OBS-FINDING-001 / H81-H82):
   price touching a specific prior level (prior-day high, overnight
   high, VWAP) during the open.

All three point the same general direction (opening-hour mean
reversion) but are measured from unrelated inputs (gap size vs.
overnight sign+regime vs. absolute price level) and were discovered in
different Observatory scan generations. This is the "genuinely
independent lenses" case pilot v1 could not yet draw on.

## Question (frozen before test, measurement-layer only)

On days where 2 or more of these 3 conditions independently fire
(pre-registered, unmodified event definitions, no new thresholds), is
the opening-hour (09:30-10:30) forward return a MORE reliable fade
(tighter CI, larger effect) than on days where only 0-1 fire? This is
a Layer-1 Observatory-style measurement question -- corroboration
across independently-discovered behaviors -- not a trading rule.
Method: bootstrap-diff CI of RTH-open forward return (10min horizon,
matching the horizon most of the source findings used) between the
"2+ conditions" bucket and the "0-1 conditions" bucket, same technique
as v1-v6.

## Pre-commitment

No condition definition is altered from its own already-frozen source
(gap threshold, regime classifier, level-touch definition all
unchanged). If the corroboration effect is not credible, this closes
the collective-evidence approach for this project (2 pilots now tried,
v1's dry run and this genuine-independence test) rather than being
retried with a different lens selection.
