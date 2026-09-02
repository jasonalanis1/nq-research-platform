# exp-039: Scheduled Macro-Release Volatility (CPI/NFP)

**Status: characterization study, primary test POSITIVE -- the first
non-null result in this project's history (14 hypotheses, five
mechanism families). No ledger entry yet; per the frozen spec and
Jason's now-mandatory Advisor-consultation rule, both Claude's own
read and the Advisor's independent read are being presented to Jason
before any next step is decided.**

## Hypothesis

Full specification frozen in advance in
`research/studies/economic-release-volatility.md`, following a
dedicated feasibility check (`research/studies/economic-calendar-feasibility.md`,
confirmed FEASIBLE at zero cost) and a Jason decision, made against the
Advisor's specific recommendation, to scope this to CPI/NFP only and
defer FOMC to a separately-scoped future question.

One primary question, pre-committed:

> Does the mean **absolute** (magnitude, not signed) 30-minute
> post-8:30 return differ between CPI/NFP release days (pooled) and
> normal days?

This is deliberately a test of the well-documented
"announcement-volatility-clustering" effect, not a directional-edge
claim -- see the frozen spec's "What this is NOT" section. It is a
**characterization study**, not a strategy: no entry/exit is defined
and no setup file exists in `research/setups/`.

## Data used

Discovery slice only (`data_split.get_discovery_data()`): 2,101
trading days, 2015-01-01 through 2021-10-03. Validation and Holdout
were never touched. Day classification: 1,941 normal days, 81 NFP
days, 79 CPI days. All 2,101 Discovery days are accounted for (no day
is dropped from classification itself). Two of the 81 frozen CPI
calendar dates (2017-04-14 and 2020-04-10, both Good Friday) are not
present in the NQ data at all -- US futures markets are closed that
day -- and so are correctly absent from every count; this was verified
directly rather than assumed.

## Method

Exactly as frozen in the study spec, no deviation:

1. Release-day classification via a frozen, sourced reference calendar
   (81 CPI dates + 81 NFP dates, compiled from bls.gov's own
   year-by-year "Schedule of Releases" archive pages, cross-validated
   by day-of-week, zero overlap between the two lists) --
   `CPI_DATES`/`NFP_DATES` constants in `src/study_economic_calendar.py`.
2. Return: `study_volatility_regime.compute_forward_return()` reused
   unmodified (signed NQ points, Close at 8:30+horizon minus today's
   own 8:30 Open), then absolute value taken.
3. Primary horizon: 30 minutes (this project's Initial Balance window,
   chosen in advance, not because it performed well).
4. Secondary horizons 60/90/120/180 minutes, reported descriptively
   only, never used to judge the study.
5. 90% bootstrap CI (2,000 resamples, seed=11) on the difference in
   **mean absolute** primary-horizon return, via
   `study_futures_expiration.bootstrap_mean_diff_ci()` reused
   unmodified -- it operates identically on an absolute-value series.
6. Two pre-specified robustness checks: (a) drop the single
   largest-|return| day, (b) first-half vs. second-half chronological
   split-sample stability.
7. Descriptive CPI-only vs. NFP-only breakdown, never used to pick a
   "better" grouping.

Implementation: `src/study_economic_calendar.py`. Unit tests (17,
covering the frozen calendar constants' count/disjointness/date-range
properties, `classify_day()`, `scan_all_days()` against hand-built
bars including the forward-return window boundary, `analyze_horizon()`
including its release-type filtering, and both robustness checks):
`tests/test_study_economic_calendar.py`, all passing (138 total in the
suite).

## Results

### Primary test (30-minute horizon, CPI+NFP pooled vs. normal)

| | n | mean \|return\| (pts) |
|---|---|---|
| Release days (CPI+NFP) | 157 | 19.201 |
| Normal days | 1,558 | 7.868 |

Mean difference: **+11.333 points** ($226.65 per contract). 90%
bootstrap CI: **[+8.103, +14.939]** -- entirely above zero.

**Step-2 gate, checked honestly against the pre-committed criteria:**

1. **Statistically credible** (CI excludes zero): **TRUE**.
2. **Economically meaningful** (>= 1.5 pts, 2x round-trip cost):
   **TRUE** -- 11.333 pts is over 7x the threshold.
3. **Plausible mechanism** (release days show *larger* magnitude,
   consistent with announcement-volatility clustering, not a story fit
   to whichever sign appeared): **TRUE** -- the direction is exactly
   the one the mechanism predicts, and the magnitude (roughly 2.4x
   normal-day volatility) is large enough to be a real regime
   difference, not noise.
4. **Not an artifact** -- survives both pre-specified robustness
   checks (detail below): **TRUE**.
5. **A simple mechanical rule can be specified without fitting to the
   result**: **NOT SATISFIED, as disclosed in advance.** This is the
   one gate condition the frozen spec flagged up front as unlikely to
   resolve the usual way -- see Interpretation below.

### Robustness checks

- **Drop single largest-|return| day** (2021-02-24, a normal day,
  excluded): mean diff +11.419 pts, CI **[+8.275, +14.935]** -- both
  the point estimate and the CI barely move. Not driven by one
  outlier day.
- **First-half vs. second-half split**: First half: mean diff +7.479
  pts, CI [+5.036, +10.294]. Second half: mean diff +15.293 pts, CI
  [+9.656, +21.300]. Both halves are statistically credible and
  economically meaningful on their own, and both point the same
  direction -- the effect is not a first-half-only or second-half-only
  artifact. The magnitude roughly doubles in the second half (which
  includes 2020's volatility), which is disclosed honestly rather than
  averaged away: the *existence* of the effect is stable, its *size*
  is not.

### Descriptive breakdown: CPI-only vs. NFP-only

| | n | mean diff vs. normal (pts) | 90% CI |
|---|---|---|---|
| CPI-only | 78 | +12.453 | [+7.453, +18.060] |
| NFP-only | 79 | +10.227 | [+6.722, +14.219] |

Both sub-groups independently clear the same statistical and economic
bars as the pooled result. Neither drives the pooled result alone;
this is reported for transparency, not to promote one over the other.

### Secondary horizons (descriptive only, per the frozen spec)

| Horizon | Mean diff (pts) | 90% CI | Significant? |
|---|---|---|---|
| 60 min | +11.225 | [+7.715, +15.460] | Yes |
| 90 min | +10.370 | [+5.611, +15.631] | Yes |
| 120 min | +7.930 | [+2.067, +14.407] | Yes |
| 180 min | +8.293 | [+1.517, +15.980] | Yes |

Unlike every prior study in this project, all four secondary horizons
are also statistically credible and in the same direction as the
primary result -- consistent with a real, broad volatility-elevation
effect around these releases rather than a 30-minute-specific
coincidence. Still reported descriptively only, per the frozen spec's
no-fishing rule; the primary conclusion rests on the 30-minute result
alone.

## Interpretation

The core hypothesis -- that NQ moves with substantially larger
magnitude around scheduled CPI/NFP releases than on an ordinary day --
is **supported** by every pre-committed test: the primary 30-minute
comparison, both robustness checks, both descriptive sub-group splits,
and all four secondary horizons all agree in direction, all clear the
statistical and economic bars, and the effect is large (roughly
2.4x normal-day volatility) rather than marginal.

This is the first result in this project to clear gate conditions 1-4.
It is honestly **not** a finding that specifies a mechanical long/short
rule the way every prior study's (would-have-been) positive result
would have: this study measured **magnitude**, not **direction**, by
design (see "What this is NOT" in the frozen spec). A trader who knew
in advance that today was a CPI/NFP day would know to expect a bigger
move, but this result alone does not say which way. Per the frozen
spec's own disclosure, the natural next step for a result like this is
a volatility-capture structure (wider stops sized to the expected
move, a straddle-like setup, or a position-sizing/risk-management rule
conditioned on release days) rather than a directional signal -- a
different and heavier design question than every prior mechanical-rule
conversion in this project, and one that has not yet been specified or
frozen.

No ledger entry has been made. No trading rule has been built. This
result changes the shape of the project's overall finding: fourteen
hypotheses have now been tested across five structurally distinct
mechanism families, and for the first time one of them is not a null.

## Next step

Per the project's now-mandatory Advisor-consultation rule
(`docs/PATH_TO_PROFITABILITY_ADVISOR.md`, guardrail 3), both Claude's
own read of what this result means and the Advisor's independent read
are being obtained and presented to Jason side by side, before any
question about next steps is asked or any direction is proposed.
