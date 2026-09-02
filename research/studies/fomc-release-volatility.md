# Scheduled Macro-Release Volatility (FOMC)

**Status: Tested. Primary test result: POSITIVE** -- the second
non-null result in this project's history, mirroring exp-039's CPI/NFP
result almost exactly in shape. Mean |return| difference (30-min
horizon, FOMC vs normal) = +13.759 pts, 90% CI [+8.263, +19.831],
n_release=46, n_normal=1580. Survives both robustness checks. See
`research/experiments/exp-040-fomc-release-volatility.md` for full
results. Gate conditions 1-4 all satisfied; condition 5 (a simple
mechanical rule specifiable without fitting) remains the disclosed
limitation, as with exp-039. No ledger entry.

**Original status line (for the record): frozen specification, not yet tested** -- drafted 2026-09-02,
following exp-039's Discovery-and-Validation-confirmed CPI/NFP result
(the first replicated finding in this project's history). Claude and
the Path-to-Profitability Advisor independently agreed FOMC was the
proportionate next step -- cheap, Discovery-only, reuses the same
frozen-spec discipline, and extends a now-twice-confirmed mechanism
family -- and Jason approved proceeding with it before any structure
design or further Validation use.

## Where this came from

exp-039 (CPI/NFP scheduled-release volatility) replicated on both
Discovery and Validation: NQ's post-release |return| magnitude is
reliably larger around CPI/NFP releases than on normal days. FOMC was
deliberately deferred from that study's scope (it releases at 2:00 PM
ET, not 8:30 AM ET, so it can't reuse the existing intraday machinery
without a small addition -- see Definition item 2). With CPI/NFP now
confirmed twice, both Claude and the Advisor agreed FOMC -- the single
most information-dense scheduled US macro event -- was worth testing
next, before any volatility-capture structure design (which is
premature regardless, since no directional setup has ever cleared this
project's promotion bar to attach a risk overlay to) and before
spending another Validation look (reserved for now).

## What this is NOT

Exactly the same framing as exp-039: a **characterization study**, not
a strategy -- no trade, no entry/exit, no setup file. **Not a test of
directional edge** -- the question is whether NQ moves more (in
magnitude) around FOMC decisions than on an ordinary day, not whether
it moves in a predictable direction. See Honesty flags for what a
positive result here would and would not establish.

## Definition

### 1. FOMC decision-day classification -- a frozen, sourced reference list

A trading day is an "FOMC day" if it is a regularly-scheduled FOMC
policy decision/announcement date, per the frozen list below: **53
dates**, 2015-01-28 through 2021-09-22, covering the Discovery window.
Compiled from federalreserve.gov's own year-by-year historical meeting
archive pages (`federalreserve.gov/monetarypolicy/fomchistoricalYYYY.htm`)
and cross-checked against individual press-release pages
(`federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm`),
by an isolated research pass, cross-validated by day-of-week (50
Wednesdays, 3 Thursdays for the rare Wed/Thu-scheduled meetings) and
inter-meeting gap consistency.

**Seven emergency/inter-meeting/non-decision items in this window were
identified and deliberately excluded**, not just missed: the March 3
and March 15, 2020 emergency inter-meeting rate cuts, three March 2020
notation votes, the October 2019 repo-operations statement, and the
August 2020 longer-run-goals strategy statement. None of these was a
regularly-scheduled decision on the pre-published calendar, so none
belongs in a "was this a scheduled release" classification -- including
them would conflate scheduled-information volatility with crisis-period
volatility, a different and much messier question. The regularly-
scheduled March 17-18, 2020 meeting itself was cancelled (superseded by
the emergency actions) and contributes no date either.

Embedded as a frozen `FOMC_DATES` constant directly in
`src/study_fomc_volatility.py`, mirroring `CPI_DATES`/`NFP_DATES`'s
existing pattern.

**Overlap check, run rather than assumed away** (per the risk flagged
in advance in `research/studies/economic-calendar-feasibility.md`,
Risk #2): checked all 53 FOMC dates against `CPI_DATES`/`NFP_DATES`
and against `study_futures_expiration.make_is_expiration_week()`.
Zero FOMC/NFP same-day overlaps. **Six FOMC/CPI same-day overlaps**
(2016-03-16, 2017-03-15, 2017-06-14, 2017-12-13, 2019-12-11,
2020-06-10) -- on these days two distinct scheduled-information
releases (8:30 AM CPI and 2:00 PM FOMC) land on the same trading day,
so attributing any afternoon volatility to FOMC alone is ambiguous.
**These 6 dates are excluded from the primary classification
entirely** (neither "FOMC day" nor "normal day"), leaving **47** FOMC
dates for the primary test -- a clean, pre-registered exclusion, not
one applied after seeing results. Separately, **18 of the 53 FOMC
dates (14 of the 47 after the CPI exclusion) fall inside an
expiration week** per exp-035's own classification -- a much larger
overlap, structural to FOMC's roughly-six-week cadence landing near
quarter-end expiration months. These are **not excluded**: exp-035
already found expiration-week proximity itself carries no significant
effect on intraday behavior (a clean null on Discovery data), so this
is a scheduling coincidence rather than a known confound -- but it is
disclosed here as a real limitation, not silently absorbed, in case
the primary result is later scrutinized against it.

### 2. New machinery required: a 2:00 PM ET reference point

Every existing intraday study in this project (including exp-039)
anchors its forward-return window to the 8:30 AM ET session open via
`study_volatility_regime.compute_forward_return()`, which hardcodes
`OPEN_HOUR`/`OPEN_MINUTE` (8, 30) imported from `detect_ib_breakout.py`.
FOMC statements release at 2:00 PM ET -- a genuinely different time of
day, flagged as exactly this fork in
`research/studies/economic-calendar-feasibility.md` Section 4. This
study introduces one new, small function,
`compute_forward_return_at(day_df, day, hour, minute, horizon_minutes)`,
identical in every respect to `compute_forward_return()` (same window
logic: `[anchor, anchor+horizon)`, same last-bar-before-horizon-end
convention, same `None`-on-insufficient-data behavior) except the
anchor hour/minute is a parameter instead of a hardcoded import. This
is the one genuinely new piece of machinery in this study -- disclosed
in advance, not discovered after the fact -- and it will be unit
tested against the same boundary cases already covering
`compute_forward_return()`.

### 3. Primary statistic -- absolute (not signed) return

Same as exp-039: **|return|**, testing the volatility-clustering
mechanism, not a directional-edge claim.

### 4. Primary horizon -- 30 minutes (2:00-2:30 PM ET)

Same horizon-choice discipline as every characterization study in this
project: chosen in advance, structurally motivated (the first 30
minutes after the scheduled release, before the FOMC press conference
if one occurs), not selected because it performed well.

### 5. Secondary horizons -- 60, 90, 120, 180 minutes

Same menu as every other study, reported descriptively only. Note this
window (2:00-5:00 PM ET) comfortably contains any 2:30 PM press-
conference-driven follow-through move within the same "post-release"
characterization -- no separate press-conference reference point is
being introduced; that is a possible future refinement, not part of
this frozen spec.

### 6. Statistical test and confidence interval

Identical convention to exp-039: 90% bootstrap CI (2,000 resamples,
`RANDOM_SEED = 11`) on the difference in mean **absolute**
primary-horizon return between FOMC days and normal days, via
`study_futures_expiration.bootstrap_mean_diff_ci()` reused unmodified.

### 7. Criteria for declaring the characterization meaningful (Step 2 gate)

Identical five-condition structure to exp-039:

1. **Statistically credible** -- the 90% CI on the mean-|return|
   difference excludes zero.
2. **Economically meaningful** -- the difference exceeds
   2x `ROUND_TRIP_COST_POINTS` (1.5 NQ points).
3. **Plausible mechanism** -- FOMC days show *larger* magnitude,
   consistent with announcement-volatility clustering.
4. **Not an artifact** -- survives the same two pre-specified
   robustness checks as exp-039: (a) drop the single largest-|return|
   day, (b) first-half vs. second-half chronological split.
5. **A simple mechanical rule can be specified without fitting to the
   result** -- same disclosed limitation as exp-039: a magnitude-only
   finding does not specify a directional rule. Doubly true here,
   since no directional setup exists yet to attach any resulting
   risk-overlay idea to (per the Advisor's point after exp-039's
   Validation replication).

If any of the five fail, or the primary test is null, the finding is
recorded as-is and the study stops there -- same as every prior study.

### 8. Exclusion rules

**Discovery slice only** (`data_split.get_discovery_data()`), matching
exactly how exp-039 was first tested. Per the process already
established with exp-039, a Validation-slice replication is a separate,
explicit decision Jason makes only if this primary test comes back
positive -- not an automatic next step, and not assumed here. An FOMC
day is excluded from a given horizon only if that horizon's return
can't be computed, same convention as every prior study.

## Honesty flags

- **This tests magnitude, not direction** -- identical caveat to
  exp-039.
- **Excluded emergency/inter-meeting dates fall into the "normal day"
  pool, not a third bucket.** `classify_day()` follows exp-039's exact
  pattern: any day not in `FOMC_SET` is "normal" by construction. The
  seven emergency/inter-meeting/non-decision dates named in item 1
  were never added to `FOMC_SET`, so trading days among them (e.g. the
  March 3 and March 15, 2020 emergency cuts) fall into "normal" along
  with every other non-FOMC day. This is a **conservative** choice,
  not a silent one: folding a handful of unusually volatile crisis-era
  days into the "normal" baseline can only inflate that baseline and
  understate the FOMC-vs-normal difference, never manufacture a false
  positive. Not corrected, to keep the classification logic identical
  to exp-039's, but stated explicitly rather than left implicit.
- **One new piece of machinery** -- `compute_forward_return_at()` is
  new code (a parameterized generalization of an existing, already-
  tested function), not a reuse-unmodified case like every other part
  of this spec. It will get its own unit tests before being trusted.
- **2015 FOMC statements' exact release-time is not independently
  verifiable from the primary-source press-release page text itself**
  -- the Fed did not begin printing an explicit "For release at 2:00
  p.m." line on statements until 2016; all eight 2015 statements
  instead say only "For immediate release." Contemporaneous market/
  press convention places these at 2:00 PM ET as well, but this is a
  corroborated inference for eight of the fifty-three dates, not a
  press-release-page fact like the other forty-five. Disclosed rather
  than silently treated as equally certain.
- **Multiple-testing context, stated plainly:** this is this project's
  fifteenth hypothesis, and the second test within the scheduled-
  information family, which already has one replicated positive result
  (exp-039). A positive result here would strengthen the family-level
  finding; a null here would **not** undermine exp-039's own already-
  replicated result -- FOMC and CPI/NFP are different mechanisms
  sharing only the "scheduled macro release" family label, and this
  test should be judged on its own frozen criteria, not treated as
  pre-confirmed by CPI/NFP's success or dismissed if it fails.
- `purgedcv` (DSR/PBO) remains unavailable in this environment --
  flagged consistently, as on every experiment to date.

## Status

**Frozen specification. Not yet tested.** Drafted 2026-09-02. No code
has been written. Awaiting Jason's explicit sign-off on this exact
specification before implementation begins -- the same gate already
used for every prior study.

## History

- 2026-09-02: After exp-039 replicated on Validation, both Claude and
  the Advisor independently recommended FOMC as the next step (cheap,
  Discovery-only, extends a confirmed family) over volatility-capture
  structure design (premature -- no directional setup exists to attach
  it to, and no options/broker infrastructure exists either) or
  further Validation use. Jason approved.
- 2026-09-02 (same day): 53 regularly-scheduled FOMC decision dates
  compiled from federalreserve.gov's own historical archive and
  press-release pages, with seven emergency/inter-meeting/non-decision
  items identified and explicitly excluded. This Frozen Study
  Specification drafted, scoped to Discovery only, presented to Jason
  for sign-off before any implementation.
- 2026-09-02 (same day): Per the mandatory Advisor-consultation rule,
  the Advisor reviewed this specific draft spec (not just the
  direction decision) before sign-off. It found the draft sound
  overall but flagged one real gap: the feasibility report's Risk #2
  (calendar overlap with CPI/NFP and expiration weeks) had not
  actually been checked. The overlap check was run: 6 FOMC/CPI
  same-day overlaps found and excluded from the primary classification
  (47 FOMC dates remain), 0 FOMC/NFP overlaps, and 18 FOMC dates
  (14 after the CPI exclusion) found to fall inside an expiration
  week -- disclosed rather than excluded, since exp-035 already found
  expiration-week proximity itself has no significant effect. The
  Advisor also flagged that excluded emergency-date trading days
  silently fall into the "normal" pool under the existing
  classification logic; this is now stated explicitly above as a
  conservative (not bias-inflating) choice rather than left implicit.
  Spec updated accordingly and re-presented for sign-off.

- 2026-09-02 (same day): Implemented and run against real Discovery
  data. Primary test POSITIVE -- the second non-null result in this
  project's history, and the second within the scheduled-information
  family. Full results in
  `research/experiments/exp-040-fomc-release-volatility.md`. Per the
  mandatory Advisor-consultation rule, both Claude's and the Advisor's
  independent reads on what this second result means are being
  presented to Jason before any direction is proposed.
