# Scheduled Macro-Release Volatility (CPI/NFP)

**Status: frozen specification, not yet tested** -- drafted 2026-09-02,
following `research/studies/economic-calendar-feasibility.md`
(STATUS: FEASIBLE at zero cost). Jason chose to scope this to CPI/NFP
only, deferring FOMC (which would need its own 2:00 PM ET reference
point, per the feasibility report's Section 4) to a separate, later
question -- against the Path-to-Profitability Advisor's independent
recommendation to include FOMC now; both takes were shown to Jason
before this choice, per this project's standing mandatory-consultation
rule (`docs/PATH_TO_PROFITABILITY_ADVISOR.md`, guardrail 3).

## Where this came from

After exp-038 (daily time-series momentum, null -- thirteen straight
hypotheses null across four mechanism families and two timeframes),
the Advisor recommended one more test before treating the accumulated
evidence as this data's honest answer: scheduled economic information,
the one mechanism family genuinely untested and structurally distinct
from level-interaction, volatility-regime, cross-market, and trend
mechanisms already tried. Jason approved a feasibility check first
(rather than assuming the data would be free and available, the same
discipline applied before the ES purchase); it confirmed CPI and NFP
release dates and their fixed 8:30 AM ET release time are available at
zero cost from bls.gov's own official Schedule of Releases archive.
Jason then chose to scope the frozen hypothesis to CPI/NFP only.

## What this is NOT

A **characterization study**, not a strategy -- no trade, no entry/exit,
no setup file. It is also, deliberately, **not a test of directional
edge**. The primary question is whether NQ moves *more* (in magnitude)
around CPI/NFP releases than on an ordinary day -- the well-documented
"announcement volatility clustering" effect from market microstructure
research -- not whether it moves in a *predictable direction*, which
would require correctly anticipating the surprise itself and has a much
weaker economic prior (this project's own prior signed-difference
tests, e.g. the volatility-regime study, already came back null on a
related but distinct question). See Honesty flags for what a positive
result here would and would not establish.

## Definition

### 1. Release-day classification -- a frozen, sourced reference list

A trading day is a "release day" if it is a CPI or NFP release date,
per the frozen date list below (81 CPI dates + 81 NFP dates = 162
release days total across Discovery, verified zero same-day overlap
between the two series). Compiled from bls.gov's own year-by-year
"Schedule of Releases" archive pages (`bls.gov/schedule/{year}/home.htm`,
2015 through 2021) by an isolated research pass, cross-validated
against each date's published day-of-week for internal consistency,
and embedded directly as frozen constants in
`src/study_economic_calendar.py` for transparency -- not pulled from
any paid or scraped commercial source (see
`research/studies/economic-calendar-feasibility.md` for why
Investing.com and ForexFactory were ruled out). Release time confirmed
8:30 AM ET for both series, with no exception found across 2015-2021,
via `bls.gov/schedule/news_release/cpi.htm` and
`bls.gov/schedule/news_release/empsit.htm`.

This is the first study in this project's history whose grouping
variable comes from an external, non-derivable reference calendar
(unlike futures expiration, which `study_futures_expiration.py`
computes algorithmically from a fixed quarterly rule).

### 2. Primary statistic -- absolute (not signed) return

The primary comparison is on **|return|** -- the magnitude of the
post-8:30 move -- not the signed return. This directly tests the
volatility-clustering mechanism (item 3 below), rather than a
directional-edge claim this study is not designed or intended to
support.

### 3. Return calculation

Reuses `study_volatility_regime.compute_forward_return()` unmodified
(signed NQ points, Close at 8:30+horizon minus today's own 8:30 Open),
then takes the absolute value. No new return convention invented.

### 4. Primary horizon -- 30 minutes

Same structural justification as the volatility-regime study: this
project's own Initial Balance window, chosen before any release-day
data was examined, not because it performed well.

### 5. Secondary horizons -- 60, 90, 120, 180 minutes

Same menu as every other study. Reported descriptively only, never
used to judge whether the study succeeded.

### 6. Statistical test and confidence interval

90% bootstrap CI (2,000 resamples, `RANDOM_SEED = 11`) on the
difference in **mean absolute** primary-horizon return between release
days and non-release days, via
`study_futures_expiration.bootstrap_mean_diff_ci()` reused unmodified
-- it operates identically on an absolute-value series as on a signed
one. Significant = the CI excludes zero, same convention as everywhere
else.

### 7. Criteria for declaring the characterization meaningful (Step 2 gate)

Same five-condition structure as exp-036:

1. **Statistically credible** -- the 90% CI on the mean-|return|
   difference excludes zero.
2. **Economically meaningful** -- the difference exceeds
   2x `ROUND_TRIP_COST_POINTS` (1.5 NQ points), same bar as every prior
   study.
3. **Plausible mechanism** -- release days show *larger* magnitude,
   consistent with announcement-volatility clustering -- not a story
   invented to fit whichever sign appears (a *smaller* magnitude on
   release days would be the surprising, implausible direction).
4. **Not an artifact** -- survives two pre-specified robustness checks:
   (a) the primary result with the single largest-|return| day removed,
   (b) a first-half vs. second-half chronological split-sample
   stability check.
5. **A simple mechanical rule can be specified without fitting to the
   result** -- disclosed limitation: a magnitude-only finding does not
   by itself specify a *directional* long/short rule the way every
   prior study's signed-difference findings would. A positive result
   here would point toward a volatility-capture structure (e.g. wider
   stops, a straddle-like setup) as the natural next step, not a
   simple long/short signal -- a heavier design lift than this
   project's prior mechanical-rule conversions, disclosed now rather
   than discovered after the fact.

If any of the five fail, or the primary test is null, the finding is
recorded as-is and the study stops there.

### 8. Descriptive breakdown -- CPI-only vs. NFP-only

Reported for transparency, never used to pick a "better" grouping:
the same primary-horizon comparison run separately for CPI-only release
days (n=81) and NFP-only release days (n=81), alongside the pooled
primary result (n=162). If one sub-group drives the pooled result while
the other doesn't, that is reported honestly, not treated as license to
promote the stronger-looking sub-group as if it had been the primary
test all along.

### 9. Exclusion rules

Discovery slice only (`data_split.get_discovery_data()`). A release
day is excluded from a given horizon only if that horizon's return
can't be computed (same convention as every prior study). No
return-value outlier is ever removed from the primary analysis.

## Honesty flags

- **This tests magnitude, not direction.** Even a fully successful
  result (all five gate conditions pass) would establish that NQ moves
  more around CPI/NFP releases -- not that the direction of that move
  is predictable. This is deliberately the more defensible question,
  but it means a positive result's path to an eventual mechanical rule
  looks different from every prior study's (see item 7.5).
- **FOMC is explicitly out of scope for this specification.** The
  Advisor recommended including it now; Jason chose to defer it. If
  FOMC is tested later, it needs its own frozen specification with its
  own 2:00 PM ET reference point -- not a silent extension of this one.
- **The release-date list is a frozen, sourced external input, not
  derived from any rule.** Unlike every prior study's grouping
  variable (all computable from the price data or a fixed calendar
  rule), this one depends on an outside compilation being accurate.
  Compiled from bls.gov's own primary-source archive pages with a
  day-of-week cross-check, not copied from a third party -- but this
  is a genuinely different kind of dependency than anything tested so
  far, and is flagged as such rather than treated as equivalent to a
  computed constant.
- 30-minute primary horizon and the pooled-then-split-descriptively
  grouping choice are each one frozen decision, not the best of several
  tried.

## Multiple-testing context

Fourteenth hypothesis and ninth conditioning/characterization-or-
promotion study in this project overall; first in the scheduled-
information family (the fifth structurally distinct mechanism family
tested). Per the hard stop already recorded in `docs/ROADMAP.md`'s
2026-09-02 entries: if this study also returns null, that is 14/14
across five mechanism families, and the pre-committed next step is a
genuine reconsideration of the project's overall approach -- not a
fifteenth variant. `purgedcv` (DSR/PBO) remains unavailable in this
environment -- flagged consistently, as on every experiment to date.

## Status

**Frozen specification. Not yet tested.** Drafted 2026-09-02. No code
has been written. Awaiting Jason's explicit sign-off on this exact
specification before implementation begins -- the same gate already
used for every prior study.

## History

- 2026-09-02: Economic-calendar feasibility report confirmed
  FEASIBLE at zero cost; flagged the CPI/NFP-vs-FOMC timing fork for
  the frozen spec to resolve.
- 2026-09-02 (same day): Per the mandatory Advisor-consultation rule,
  both Claude's lean (CPI/NFP only, defer FOMC) and the Advisor's
  independent recommendation (include FOMC now, as the single most
  information-dense scheduled event, rather than risk it becoming a
  15th-variant follow-up later) were shown to Jason side by side.
  Jason chose CPI/NFP only.
- 2026-09-02 (same day): This Frozen Study Specification drafted,
  scoped to CPI/NFP per that decision, framed around magnitude rather
  than direction for the reasons in "What this is NOT" above.
  Presented to Jason for sign-off before any implementation.
