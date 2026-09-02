# exp-037: ES Overnight Gap as Incremental Information Beyond NQ's Own Gap

**Status: characterization study, result NULL on primary test. No ledger
entry, no mechanical rule proposed or built. Project's first
two-instrument analysis.**

## Hypothesis

Full specification frozen in advance in
`research/studies/es-overnight-gap-incremental-information.md`, itself
built on the ES Cross-Market Feasibility Report
(`research/studies/es-cross-market-feasibility.md`, Mechanism 3) --
before any code was written.

One primary question, one primary outcome, pre-committed:

> In a joint regression of NQ's 90-minute post-8:30 forward return on
> both NQ's own overnight gap and ES's overnight gap, does ES's gap
> coefficient (b2) carry incremental information -- i.e. is its 90%
> bootstrap CI entirely on one side of zero -- after NQ's own gap
> (already found real in exp-032) is already in the model?

This is a **characterization study**, not a strategy. No entry/exit is
defined, no setup file exists in `research/setups/`, and per the study
doc's Step 2 gate, a significant primary result would not by itself
justify building a mechanical rule.

## Data used

Discovery slice only (`data_split.get_discovery_data()`), both
instruments: `NQ_1min_databento_2026-08-20.csv` and
`ES_1min_databento_2026-09-02.csv` (2015-01-01 through 2021-10-03).
Validation and Holdout were never touched.

NQ Discovery: 2,101 calendar-classifiable days, 1,717 with both a valid
reference close and 8:30 open. ES Discovery: identically 2,101 and
1,717. The inner join (frozen spec item 3) dropped **zero** days on
either side -- the two instruments' valid-day sets were exactly
identical, confirming the "very few days expected to drop" prediction
in the feasibility report. 1,716 joint gap-days resulted (one fewer
than 1,717, since the earliest joint day has no prior day to gap
against); 1,687 of those had a full 90-minute forward-return window.

## Method

Exactly as frozen in the study spec, no deviation:

1. `NQ_gap[t]` and `ES_gap[t]`: each instrument's own 8:30 AM ET open
   minus its own prior-day `get_reference_close()` (4:00 PM ET
   convention), computed identically and independently for both
   instruments.
2. Inner join on trading day: a day survives only with valid reference
   points on both instruments. `prior_day` is the immediately preceding
   day in this same joined list (not necessarily the literal previous
   calendar trading day, if a day were excluded from the join -- not
   triggered in this run, since nothing was excluded).
3. Primary horizon: 90 minutes, fixed in advance and anchored to
   exp-032's own already-established finding at that horizon -- not
   selected because ES's gap performed well there.
4. Model: OLS, `NQ_forward_return[t] = b0 + b1*NQ_gap[t] + b2*ES_gap[t]
   + e[t]`. Primary test is on b2 alone.
5. 90% bootstrap CI on b2 (2,000 resamples, seed=11, joint resampling
   of (NQ_gap, ES_gap, forward_return) triples with replacement), via
   the new `bootstrap_regression_coef_ci()` -- the smallest possible
   extension of this project's existing resample-and-recompute
   bootstrap pattern to a regression coefficient.
6. Secondary horizons 30/60/120/180 minutes, reported descriptively
   only, never used to judge the study.
7. Two pre-specified robustness checks: (a) drop the single
   largest-|ES_gap| day, (b) first-half vs. second-half chronological
   split-sample stability.

Implementation: `src/study_es_gap_incremental_info.py`. This required
one small, backward-compatible addition to the shared
`src/data_loader.py` (an optional `symbol` parameter, defaulting to
"NQ" so every existing caller is unaffected) so ES's data file could be
found through the same existing loader rather than duplicating that
logic. Unit tests (10, covering day-data extraction, gap computation
including missing-reference-point edge cases, the inner-join's
day-skip semantics with a hand-verified example, exact-recovery of a
noiseless OLS fit, the bootstrap CI correctly excluding zero for a
strong synthetic effect and correctly spanning zero for pure noise, and
the drop-largest-day robustness check): `tests/test_study_es_gap_incremental_info.py`,
all passing (110/110 in the full suite).

## Results

### Primary test (90-minute horizon, b2 = ES_gap's coefficient)

| | n | b0 | b1 (NQ_gap) | b2 (ES_gap) | 90% CI on b2 |
|---|---|---|---|---|---|
| Joint regression | 1,687 | +1.553 | -0.0159 | **-0.0816** | [-0.432, +0.262] |

CI spans zero. Translated effect (|b2| x ES_gap's interquartile range,
13.25 pts): **1.081 points** ($21.62/contract) -- below the 1.5-point
economic threshold.

**Step-2 gate, checked honestly against the pre-committed criteria:**

1. Statistically credible (CI excludes zero): **FALSE**.
2. Economically meaningful (translated effect >= 1.5 pts): **FALSE**
   (1.081 < 1.5).

Both of the first two gate conditions fail outright. Per the frozen
spec, the remaining three conditions (plausible mechanism, artifact
checks, specifiable rule) are moot -- the primary test is null and the
study stops here.

### Robustness checks (reported for completeness, not used to rescue the primary result)

- **Drop single largest-|ES_gap| day** (2020-11-09 excluded): b2 moves
  to -0.0593, CI [-0.449, +0.319] -- still spans zero, still not
  economically meaningful (0.785 pts). Consistent with the primary
  null; not an artifact of one outlier day.
- **First-half vs. second-half split**: First half: b2 = -0.239, CI
  [-0.855, +0.347] -- CI spans zero, but the translated effect (2.333
  pts) exceeds the economic threshold. Second half: b2 = -0.035, CI
  [-0.407, +0.384] -- flat null, translated effect well below
  threshold (0.678 pts). As with exp-036's split-half check, the two
  halves disagree sharply (roughly 7x in point estimate) and neither
  half's CI excludes zero. This is exactly the instability the check
  exists to surface -- it reinforces the "stop here" conclusion rather
  than suggesting a sub-period worth chasing.

### Secondary horizons (descriptive only, per the frozen spec)

| Horizon | b2 (ES_gap) | 90% CI | Significant? |
|---|---|---|---|
| 30 min | +0.056 | [-0.084, +0.173] | No |
| 60 min | +0.112 | [-0.094, +0.269] | No |
| 120 min | -0.045 | [-0.548, +0.395] | No |
| 180 min | -0.300 | [-0.854, +0.208] | No |

None of the four secondary horizons show a CI excluding zero -- unlike
exp-036, there is no secondary-horizon anomaly to flag here at all.

## Interpretation

The core hypothesis -- that ES's overnight gap carries information
about NQ's forward return beyond what NQ's own already-characterized
gap provides -- is **not supported** by the primary, pre-committed test
on Discovery data. The point estimate on b2 is small and slightly
negative, its CI spans zero by a wide margin relative to the estimate,
and the translated economic effect falls short of the cost-based
threshold even before considering the sign's instability across the
split-half check.

This is a clean, honest null on this project's first two-instrument
hypothesis and its first multivariate-regression test -- the new
statistical machinery (the joint-resampling regression-coefficient
bootstrap) behaved exactly as intended, correctly separating a strong
synthetic signal from pure noise in the unit tests before being trusted
on real data. Combined with the ten hypotheses tested previously (six
reversal variants, IB Breakout, Fade the Gap, VWAP Mean Reversion, and
the volatility-regime characterization), this extends the project's
overall finding: eleven hypotheses spanning three structurally distinct
mechanism families -- level-interaction, volatility-regime, and now
cross-market -- have failed to clear a promotion bar on Discovery data.

## Next step

Per this project's standing instruction, **no mechanical trading rule
is proposed or built from this result**. No ledger entry is made (same
convention as the other characterization studies, exp-029/030/031/035/036).

This result is reported back to Jason for Phase 2 direction: the third
candidate mechanism from the feasibility report (NQ/ES relative-value
spread), the remaining untested family (scheduled economic
information), further conditioning work, or a pivot.
