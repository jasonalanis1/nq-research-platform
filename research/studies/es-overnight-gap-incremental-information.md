# ES Overnight Gap as Incremental Information Beyond NQ's Own Overnight Gap

**Status: Tested. Primary test result: NULL.** Frozen 2026-09-02,
following the ES Cross-Market Feasibility Report
(`research/studies/es-cross-market-feasibility.md`), Mechanism 3 as
recommended in that report's Section 9. Implemented and run against the
Discovery slice the same day -- see Status section below for the
result.

## Where this came from

After exp-036 (volatility regime, clean null), the Phase 2 review
identified two untested families: scheduled economic information, and
cross-market/relative value. Before choosing or freezing a cross-market
hypothesis, a strict data-feasibility-only study was run first (per
Jason's explicit instruction): the ES Cross-Market Feasibility Report
evaluated data cost, data access, technical integration, and research
design across three candidate mechanisms, and confirmed STATUS:
FEASIBLE with a live Databento cost quote ($8.351282700896, confirmed
by Jason's own successful call, not an estimate). That report
recommended Mechanism 3 -- of the three candidates, the one with the
clearest causal design, the lowest multiple-testing risk, and the most
direct connection to a finding this project has already established
(exp-032's NQ overnight-gap correlation at the +90-minute horizon).

Jason approved the purchase. ES Discovery-period 1-minute data has been
downloaded and is present at `data/ES_1min_databento_2026-09-02.csv`,
covering 2015-01-01 through 2021-10-03 -- confirmed to match NQ's own
Discovery-period coverage exactly.

## What this is NOT

This is a **characterization study**, not a strategy. No trade is
placed, no entry/exit is defined, and no setup file is created in
`research/setups/`. This is the project's first two-instrument
analysis; per the Step 2 gate below, a significant finding does not
automatically become a mechanical rule. This is also not a test of the
other two candidate mechanisms considered in the feasibility report --
not a lead-lag/lag-correlation search (Mechanism 1) and not an
NQ/ES relative-strength spread (Mechanism 2). Only Mechanism 3 is
specified here.

## Definition

### 1. NQ overnight gap

Identical to exp-032's already-frozen definition, reused unmodified:
`NQ_gap[t]` = NQ's 8:30 AM ET Open on trading day `t` minus NQ's
`get_reference_close()` (the existing 4:00 PM ET causal convention) on
day `t-1`.

### 2. ES overnight gap

`ES_gap[t]` = ES's 8:30 AM ET Open on trading day `t` minus ES's
`get_reference_close()` on day `t-1`, computed by applying the
identical `study_overnight_gap.get_reference_close()` function to ES's
own 1-minute data. No new reference-close convention is invented for
ES.

### 3. Day alignment

Inner join on trading day: a day is included only if it has a valid
NQ reference close, NQ 8:30 open, ES reference close, and ES 8:30 open.
Both instruments trade the same CME Globex calendar, so very few days
are expected to drop from this join; the actual count of dropped days
is reported in the results, not assumed in advance.

### 4. NQ forward return (dependent variable)

Identical to exp-032's definition, reused unmodified: signed NQ points,
Close at (8:30 + horizon) minus today's own 8:30 AM Open, using the
last available Close within the horizon window.

### 5. Primary horizon -- 90 minutes

Chosen in advance, anchored structurally to exp-032's own
already-established, pre-committed finding: +90 minutes was the one
horizon (of five) where NQ's own overnight gap showed a statistically
credible correlation with NQ's forward return. Using that same horizon
here is a deliberate, disclosed reuse of a project precedent -- not a
horizon chosen because ES's gap happens to perform well there, and not
a fresh horizon search.

### 6. Secondary horizons -- 30, 60, 120, 180 minutes

Same five-horizon menu already used in `study_overnight_gap.py`,
reused for comparability. Reported descriptively only, per this
project's standing no-fishing rule -- never used to judge whether the
study succeeded, regardless of what any secondary horizon's CI shows.

### 7. Model and primary test

Ordinary least squares regression of NQ's primary-horizon forward
return on both gaps, with an intercept:

`forward_return[t] = b0 + b1 * NQ_gap[t] + b2 * ES_gap[t] + e[t]`

The primary test is on **b2**, the ES-gap coefficient. By construction,
b2 measures ES's gap's association with NQ's forward return *after*
NQ's own gap is already in the model -- this is the nested,
incremental-information test the feasibility report specified, not a
bare correlation between ES's gap and NQ's return.

### 8. Confidence interval

90% bootstrap CI on b2: 2,000 resamples, `RANDOM_SEED = 11` (the
project's current convention, matching exp-035/exp-036, not exp-032's
older seed=42). Each resample draws (NQ_gap, ES_gap, forward_return)
triples with replacement, using trading days as the resampling unit --
the same nonparametric convention as every other bootstrap in this
project -- refits the OLS regression, and records b2. Significant = the
90% CI excludes zero. This requires one new small helper function,
`bootstrap_regression_coef_ci()`, generalizing the existing
`bootstrap_mean_diff_ci()` / `bootstrap_correlation_ci()` pattern
(resample days, recompute a statistic, take the percentile CI) to a
regression coefficient -- the smallest addition needed, not new
statistical machinery.

### 9. Exclusion rules

Discovery slice only, both instruments
(`data_split.get_discovery_data()` applied to each before the day-level
join in item 3). A day is excluded if either instrument lacks a valid
reference close, 8:30 open, or the primary horizon's forward-return
bar. A day is excluded from a given secondary horizon only if that
horizon's return can't be computed. No return-value outlier is removed
from the primary analysis.

### 10. Criteria for declaring the characterization meaningful (Step 2 gate)

All five, all pre-committed before any data is examined -- same
structure as exp-036's gate:

1. **Statistically credible** -- the 90% CI on b2 excludes zero.
2. **Economically meaningful** -- b2 times the interquartile range
   (IQR) of ES_gap in the realized sample, holding NQ_gap fixed, must
   be >= 1.5 NQ points (the same 2x-`ROUND_TRIP_COST_POINTS` bar used
   in the volatility-regime study). Reported alongside the raw
   coefficient, not in place of it.
3. **Plausible mechanism** -- the sign is consistent with "ES's
   overnight move carries market-wide information beyond what NQ's own
   gap already captures," not a story invented to fit whichever sign
   appears.
4. **Not an artifact** -- survives two pre-specified robustness checks:
   (a) the primary result with the single largest-magnitude ES_gap day
   removed, and (b) a first-half vs. second-half chronological
   split-sample stability check, same convention as exp-036.
5. **A simple mechanical rule can be specified without fitting to the
   result** -- any proposed rule's direction and sizing must follow
   directly from the characterization's own sign and magnitude.

If any of the five fail, or the primary test is null, the finding is
recorded as-is and the study stops there. That is a successful research
outcome, not a failure requiring a fix.

## Honesty flags

- This is the project's first two-instrument analysis and its first
  multivariate-regression test. The regression-coefficient bootstrap is
  a new (small) statistical tool, not previously used anywhere in this
  project's studies -- disclosed here rather than added silently.
- b1 (NQ_gap's own coefficient in this joint model) is reported for
  completeness only. It is not the primary test, and it is not
  interpreted as a replication of exp-032's univariate correlation --
  it is expected to differ somewhat from that univariate figure,
  precisely because this model now also controls for ES_gap.
- The primary horizon (+90 minutes) is anchored to exp-032's own
  already-established finding at that same horizon. This is a
  deliberate, disclosed reuse of a project precedent, not a freshly
  chosen or tested horizon.
- Multiple-testing exposure is low by design: one pre-committed primary
  test (one coefficient, one horizon) -- the lowest multiple-testing
  risk of the three candidate mechanisms, per the feasibility report's
  own comparison.

## Multiple-testing context

This is the eleventh strategy-adjacent hypothesis and seventh
conditioning/characterization check run in this project overall, and
the second study in the new cross-market family (following the ES
Cross-Market Feasibility Report, which was explicitly a
feasibility-only study, not a hypothesis test). `purgedcv` (DSR/PBO)
remains unavailable in this environment -- flagged consistently, as on
every experiment to date. Not expected to matter here: this is a
characterization study with a single pre-committed primary test, not a
search across trial configurations.

## Status

**Tested. Primary test result: NULL.** Run against the Discovery
slice on 2026-09-02. The 90-minute primary-horizon regression's ES_gap
coefficient (b2) was -0.0816, 90% bootstrap CI [-0.432, +0.262] --
spans zero. Translated economic effect (|b2| times ES_gap's
interquartile range): 1.081 points, below the 1.5-point threshold.
Step-2-gate checks 1 (statistically credible) and 2 (economically
meaningful) both failed, so per this spec's own rule the study stops
there -- the remaining three gate conditions were not evaluated. No
mechanical rule was proposed or built. The inner join with NQ's data
dropped zero days on either side. Full results, both robustness
checks, and the secondary-horizon table are in
`research/experiments/exp-037-es-gap-incremental-information.md`. No
ledger entry, consistent with a null characterization result.

## History

- 2026-09-02: ES Cross-Market Feasibility Report completed;
  STATUS: FEASIBLE (data cost confirmed live at $8.351282700896).
  Mechanism 3 recommended in that report's Section 9.
- 2026-09-02 (same day): Jason approved the purchase. ES
  Discovery-period 1-minute data downloaded and confirmed present at
  `data/ES_1min_databento_2026-09-02.csv` (2015-01-01 through
  2021-10-03, matching NQ's Discovery coverage).
- 2026-09-02 (same day): This Frozen Study Specification drafted,
  grounded in exp-032's real, re-verified results (n=1318,
  correlation=-0.1408, 90% CI [-0.2142, -0.0595] at the +90-minute
  horizon, re-checked against the actual experiment file rather than
  relying on memory, per project discipline) rather than a fresh
  design. Presented to Jason for sign-off before any implementation.
- 2026-09-02 (same day): Jason approved implementation. Study
  implemented (`src/study_es_gap_incremental_info.py`, plus a small
  backward-compatible `symbol` parameter added to the shared
  `data_loader.py` so ES's data could be found through the same
  existing loader rather than duplicating that logic) and run against
  Discovery data. Primary test came back null (CI spans zero, effect
  below the economic threshold). Both robustness checks reported
  as-is; neither rescues the primary result. Written up as
  `research/experiments/exp-037-es-gap-incremental-information.md`. No
  ledger entry, no mechanical rule proposed.
