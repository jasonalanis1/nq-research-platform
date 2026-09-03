# exp-041: Post-Release Directional Continuation

**Status: characterization study, primary test NULL.** Hypothesis #17,
third test in the scheduled-information family, first to test
DIRECTION rather than magnitude. One unplanned, worth-disclosing
side-observation in the descriptive breakdown -- see Interpretation.
No ledger entry.

## Hypothesis

Full specification frozen in advance in
`research/studies/post-release-directional-continuation.md`, Advisor
technical-reviewed before Jason's sign-off. One primary question,
pre-committed:

> On a confirmed CPI/NFP/FOMC scheduled-release day, does NQ's initial
> 30-minute post-release move tend to CONTINUE (same sign) over the
> following 150 minutes (the 30-to-180-minute mark), pooled across all
> three release types?

Unlike exp-039/040 (magnitude only), a positive result here would be
directly a specifiable mechanical rule: go with the initial move's
direction, hold to the 180-minute mark. Still a characterization
study, not yet a cost-inclusive, promotion-bar-tested strategy.

## Data used

Discovery slice only (`data_split.get_discovery_data()`): 2,101
trading days, 2015-01-01 through 2021-10-03. Universe: 81 CPI + 81 NFP
+ 47 primary FOMC dates = 209 candidate release days. 198 survived to
analysis (75 cpi, 77 nfp, 46 fomc) -- 11 excluded for insufficient
price data near an anchor or an exactly-zero initial move (no
direction to test continuation of), the same small, unremarkable rate
of exclusion seen throughout this project.

## Method

Exactly as frozen in the study spec, no deviation:

1. Two anchors, reused unmodified: CPI/NFP at 8:30 AM ET, FOMC at 2:00
   PM ET. Each release day contributes exactly one row (verified by
   construction and by the module's own disjointness assertions,
   which pass at import).
2. `initial_return` = signed return, anchor to anchor+30min.
   `total_return` = signed return, anchor to anchor+180min.
   `continuation_return = total_return - initial_return`.
   `directional_continuation = continuation_return * sign(initial_return)`
   -- the exact point-P&L of "go with the initial direction, hold to
   the 180-minute mark."
3. Primary test: one-sample 90% bootstrap CI (2,000 resamples,
   seed=11) on the mean of `directional_continuation`, pooled across
   all three release types, via
   `study_nq_trend_following.bootstrap_mean_ci()` reused unmodified.
4. Secondary/descriptive: per-type (cpi/nfp/fomc) breakdowns, and a
   normal-day baseline comparison at each matching anchor (restricted
   to days that are ordinary in BOTH the CPI/NFP and FOMC
   classifications, so no release day's own "other" anchor leaks into
   the baseline pool).
5. Two pre-specified robustness checks: (a) drop the single largest-
   |directional_continuation| release-day row, (b) first-half vs.
   second-half chronological split.

Implementation: `src/study_post_release_continuation.py`. No new
calendar data, no new detection machinery -- reuses
`CPI_DATES`/`NFP_DATES`/`classify_day()` from
`study_economic_calendar.py`, `FOMC_PRIMARY_DATES`/
`FOMC_CPI_OVERLAP_DATES`/`classify_day()`/`compute_forward_return_at()`
from `study_fomc_volatility.py`, and `bootstrap_mean_ci()`/
`bootstrap_mean_diff_ci()` from `study_nq_trend_following.py`/
`study_futures_expiration.py`, all unmodified. Unit tests (16,
covering the reused disjointness properties, `scan_all_days()`'s
per-anchor row construction including the true-normal-day baseline
rule, the continuation sign algebra, exclusion counting, and both
robustness checks): `tests/test_study_post_release_continuation.py`,
all passing (176 total in the suite).

## Results

### Primary test (pooled CPI+NFP+FOMC, 30min initial -> 180min total)

| | n |
|---|---|
| Release days (pooled) | 198 |

Mean `directional_continuation`: **-2.947 points** (-$58.94 per
contract). 90% bootstrap CI: **[-11.328, +4.361]** -- spans zero.

**Step-2 gate, checked honestly against the pre-committed criteria:**

1. **Statistically credible** (CI excludes zero): **FALSE**.
2. **Economically meaningful** (mean >= +1.5 pts): **FALSE** -- the
   point estimate is negative, not just below threshold.

Per this project's established convention when gate condition 1 fails
outright (see e.g. `research/studies/volatility-regime-post-open-behavior.md`,
`research/studies/nq-daily-trend-following.md`), conditions 3-5 are
not formally evaluated. The robustness and descriptive checks below
were still run and are disclosed in full for context, not because they
change the verdict.

### Robustness checks (descriptive -- primary already null)

- **Drop single largest-|directional_continuation| day** (2020-09-04,
  0830 anchor, excluded): mean -0.928 pts, CI **[-8.172, +5.740]** --
  still spans zero, still null. Not a single-outlier artifact of
  either sign.
- **First-half vs. second-half split**: First half: n=99, mean +1.003
  pts, CI [-4.106, +6.163]. Second half: n=99, mean -6.896 pts, CI
  [-21.554, +7.355]. Both null individually. Worth noting honestly:
  the point estimate's *sign itself* flips between halves (mildly
  positive, then more negative) -- the opposite of exp-039/040's
  pattern, where the effect's sign was stable and only its size grew.
  Further evidence against treating the pooled point estimate as a
  real, stable effect.

### Descriptive breakdown: cpi-only / nfp-only / fomc-only (never gates the study)

| Type | n | mean (pts) | 90% CI |
|---|---|---|---|
| cpi | 75 | -11.023 | [-22.560, -0.436] |
| nfp | 77 | +1.805 | [-12.762, +15.608] |
| fomc | 46 | +2.266 | [-14.251, +17.543] |

nfp and fomc disagree in sign with the pooled (negative) result -- per
the frozen spec's condition-5 scoping caveat, this would have blocked
stating a blanket three-subtype rule even had the pooled test passed.
Moot here since the pooled test is null regardless.

**Worth flagging precisely, not glossed over**: the module's own
`significant` flag only tests one direction (CI entirely *above*
zero, matching gate condition 1's continuation hypothesis), so it
printed "not significant" for cpi even though **the cpi-only 90% CI,
[-22.560, -0.436], is entirely BELOW zero** -- a statistically
credible result, just of the opposite sign from what this study was
built to detect. Taken at face value, this says CPI days specifically
show a real tendency to partially *reverse* the initial 30-minute
move rather than continue it. This is a genuine, disclosed
observation, not a confirmed finding: it was not the pre-registered
primary test (which was pooled and continuation-directional), finding
it only after seeing the data is exactly the kind of after-the-fact
pattern this project's own integrity rules exist to guard against, and
it has not been robustness-checked on its own. It would need its own
freshly-frozen spec, written in advance, before being treated as
anything more than a lead. Recorded here so it isn't lost, not
promoted.

### Secondary/descriptive: normal-day baseline comparison

| Comparison | Normal-day mean (pts) | Release-vs-normal diff 90% CI | Significant? |
|---|---|---|---|
| cpi+nfp vs normal (0830 anchor) | -0.251 | [-14.014, +4.961] | No |
| fomc vs normal (1400 anchor) | +0.154 | [-14.015, +17.683] | No |

Neither release-vs-normal comparison is distinguishable from zero.
Note the cpi+nfp comparison pools cpi with nfp, which dilutes any
CPI-specific signal -- this comparison does not, on its own, resolve
whether the cpi-only reversal observation above is release-specific or
just noise; that would require its own targeted test.

## Interpretation

The pre-registered hypothesis -- that NQ's initial post-release move
tends to continue -- is **not supported**. The pooled primary test is
a clean null: gate conditions 1 and 2 both fail, the point estimate is
negative rather than merely insignificant, both robustness checks stay
null, and the effect's sign is not even stable across the first-half/
second-half split. This is this project's fourteenth null hypothesis
(counting distinct hypotheses, not sub-variants) out of seventeen
tested.

One disclosed, unplanned observation: the cpi-only descriptive
breakdown shows a statistically credible (CI entirely below zero)
tendency toward reversal rather than continuation on CPI days
specifically. This is recorded honestly as a lead, not a finding --
it wasn't pre-registered, wasn't robustness-checked, and this
project's own rules require a hypothesis to be frozen in advance of
seeing the data it will be tested against, not fitted afterward. If
pursued, it would need its own fresh frozen spec (a genuine reversal
hypothesis, CPI-specific, written before looking at any further data)
-- a separate future decision, not an automatic next step.

This null does **not** undermine exp-039 or exp-040's own findings, as
disclosed in advance in the frozen spec: magnitude and directional
continuation are different questions about the same event days.
CPI/NFP/FOMC releases reliably make NQ move more (confirmed twice);
they do not reliably make it move in a way that continues predictably
afterward, at least not pooled across all three release types the way
this study tested it.

Per the frozen spec, this study was scoped to Discovery only. A null
primary result ends the process here -- no Validation check, matching
this project's standing practice of only spending a Validation look on
a result that passed its Discovery gate.

## Next step

Per the project's mandatory Advisor-consultation rule, both Claude's
own read and a fresh Advisor read on what this null (and the
disclosed CPI-only side-observation) means for what's next will be
presented to Jason side by side before any direction is proposed.
