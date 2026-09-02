# exp-040: Scheduled Macro-Release Volatility (FOMC)

**Status: characterization study, primary test POSITIVE -- the second
non-null result in this project's history, and the second within the
scheduled-information family (after exp-039's CPI/NFP result, which
replicated on both Discovery and Validation). No ledger entry.**

## Hypothesis

Full specification frozen in advance in
`research/studies/fomc-release-volatility.md`, following exp-039's
Validation-confirmed CPI/NFP result and a shared Claude/Advisor
recommendation (approved by Jason) to test FOMC next, before any
volatility-capture structure design or further Validation use. The
Advisor also reviewed this specific draft spec before sign-off and
flagged a real gap (an unrun calendar-overlap check) -- addressed
below before implementation began.

One primary question, pre-committed:

> Does the mean **absolute** (magnitude, not signed) 30-minute
> post-2:00-PM-ET return differ between FOMC policy decision days and
> normal days?

Same framing as exp-039: a **characterization study** testing
announcement-volatility clustering, not a directional-edge claim. No
entry/exit is defined, no setup file exists in `research/setups/`.

## Data used

Discovery slice only (`data_split.get_discovery_data()`): 2,101
trading days, 2015-01-01 through 2021-10-03. Day classification: 2,048
normal days, 47 "fomc" days used in the primary test, 6 "fomc" days
excluded entirely from both buckets (see below).

## Method

Exactly as frozen in the study spec, no deviation:

1. **FOMC decision-day classification**: 53 regularly-scheduled FOMC
   policy decisions, 2015-01-28 through 2021-09-22, compiled from
   federalreserve.gov's own historical meeting archive and
   press-release pages. Seven emergency/inter-meeting/non-decision
   items in this window (the March 2020 emergency cuts, three notation
   votes, an October 2019 repo statement, an August 2020 strategy
   statement) were identified and deliberately excluded -- not on the
   pre-published calendar, so not "regularly scheduled."
2. **Overlap check, run rather than assumed away** (the specific gap
   the Advisor flagged before sign-off): all 53 FOMC dates checked
   against `CPI_DATES`/`NFP_DATES` and against
   `study_futures_expiration.make_is_expiration_week()`. Zero
   FOMC/NFP overlaps. **Six FOMC/CPI same-day overlaps** found
   (2016-03-16, 2017-03-15, 2017-06-14, 2017-12-13, 2019-12-11,
   2020-06-10) -- excluded from the primary classification entirely
   (neither "fomc" nor "normal"), leaving 47 dates for the primary
   test. Separately, **14 of the 47 primary FOMC dates fall inside an
   expiration week** -- disclosed, not excluded, since exp-035 already
   found expiration-week proximity itself has no significant effect.
3. **New machinery, disclosed in advance**:
   `compute_forward_return_at(day_df, day, hour, minute,
   horizon_minutes)` -- a direct parameterized generalization of
   `study_volatility_regime.compute_forward_return()` (identical
   window/edge-case logic; only the anchor hour/minute is no longer
   hardcoded to 8:30 AM). Needed because FOMC releases at 2:00 PM ET,
   not 8:30 AM ET. This is the one part of this study that is not a
   reuse-unmodified case.
4. Return: absolute value of the signed return from the 2:00 PM Open
   to the last Close within the horizon window.
5. Primary horizon: 30 minutes (2:00-2:30 PM ET).
6. Secondary horizons 60/90/120/180 minutes, descriptive only.
7. 90% bootstrap CI (2,000 resamples, seed=11) on the difference in
   mean absolute primary-horizon return, via
   `study_futures_expiration.bootstrap_mean_diff_ci()` reused
   unmodified.
8. Two pre-specified robustness checks: (a) drop the single
   largest-|return| day, (b) first-half vs. second-half chronological
   split.

Implementation: `src/study_fomc_volatility.py`. Unit tests (19,
covering the frozen calendar constants and overlap-exclusion counts,
`classify_day()`, the new `compute_forward_return_at()` including its
window-boundary edge cases, `scan_all_days()`, `analyze_horizon()`
(including that overlap-excluded rows are dropped from both buckets,
not folded into either), and both robustness checks):
`tests/test_study_fomc_volatility.py`, all passing (160 total in the
suite).

## Results

### Primary test (30-minute horizon, FOMC vs. normal)

| | n | mean \|return\| (pts) |
|---|---|---|
| FOMC days | 46 | 25.076 |
| Normal days | 1,580 | 11.317 |

Mean difference: **+13.759 points** ($275.18 per contract). 90%
bootstrap CI: **[+8.263, +19.831]** -- entirely above zero.

**Step-2 gate, checked honestly against the pre-committed criteria:**

1. **Statistically credible** (CI excludes zero): **TRUE**.
2. **Economically meaningful** (>= 1.5 pts): **TRUE** -- over 9x the
   threshold.
3. **Plausible mechanism** (FOMC days show *larger* magnitude): **TRUE**
   -- release/normal ratio 2.22x, consistent with the same
   announcement-volatility-clustering mechanism exp-039 already
   confirmed for CPI/NFP.
4. **Not an artifact** -- survives both robustness checks (detail
   below): **TRUE**.
5. **A simple mechanical rule can be specified without fitting to the
   result**: **NOT SATISFIED, as disclosed in advance** -- same
   magnitude-not-direction limitation as exp-039, doubly so here since
   no directional setup exists yet to attach any resulting risk-overlay
   idea to.

### Robustness checks

- **Drop single largest-|return| day** (2020-09-10, excluded): mean
  diff +13.864 pts, CI **[+8.086, +19.795]** -- both barely move. Not
  driven by one outlier day.
- **First-half vs. second-half split**: First half: mean diff +6.379
  pts, CI [+1.938, +11.084]. Second half: mean diff +20.116 pts, CI
  [+11.312, +29.588]. Both halves independently statistically credible
  and economically meaningful; both point the same direction. The
  magnitude roughly triples in the second half (which includes 2020),
  the same pattern already seen in exp-039's own split-half check --
  disclosed honestly, not averaged away: the effect's existence is
  stable, its size is not.

### Disclosure: expiration-week overlap (not a robustness check, does not change the primary result)

14 of the 47 primary FOMC dates (30%) also fall inside an expiration
week per exp-035's own classification -- a structural consequence of
FOMC's roughly six-week cadence landing near quarter-end expiration
months, not a result-fitting choice. Since exp-035 already found
expiration-week proximity itself carries no significant effect on
Discovery data, this overlap is reported as a limitation worth knowing
about rather than treated as a known confound requiring exclusion.

### Secondary horizons (descriptive only, per the frozen spec)

| Horizon | Mean diff (pts) | 90% CI | Significant? |
|---|---|---|---|
| 60 min | +23.700 | [+12.492, +36.656] | Yes |
| 90 min | +22.485 | [+11.043, +36.464] | Yes |
| 120 min | +16.314 | [+4.983, +29.861] | Yes |
| 180 min | +25.270 | [+13.094, +38.926] | Yes |

All four secondary horizons agree in direction and are statistically
credible -- consistent with a real, broad volatility-elevation effect
around FOMC decisions (and, at the longer horizons, likely also
capturing any 2:30 PM press-conference follow-through, which this
study's window structurally includes without a separate reference
point). Reported descriptively only, per the frozen spec's no-fishing
rule.

## Interpretation

The core hypothesis -- that NQ moves with substantially larger
magnitude around FOMC policy decisions than on an ordinary day -- is
**supported** by every pre-committed test, mirroring exp-039's own
result almost exactly in shape: same direction, same order of
magnitude (2.22x normal-day volatility here vs. 2.44x for CPI/NFP on
Discovery), same "effect stable, size grows in the second half"
robustness pattern, same disclosed magnitude-not-direction limitation.

This is the second result in this project's history to clear gate
conditions 1-4, and it strengthens the case that the underlying
mechanism -- markets pricing in more uncertainty around scheduled
macro information releases -- is real and general across at least two
structurally distinct release types (a monthly data release and a
policy-decision announcement), not an artifact specific to how CPI/NFP
happened to be tested.

It does **not** change the practical bottleneck the Advisor identified
after exp-039's Validation replication: this remains a magnitude
finding, not a directional one, and no directional trading setup has
ever cleared this project's promotion bar to attach a volatility-aware
risk overlay to. No ledger entry has been made. No trading rule has
been built.

Per the frozen spec, this study was scoped to Discovery only, matching
how exp-039 was first tested -- a Validation-slice replication is a
separate, explicit decision for Jason to make only if he chooses to,
not an automatic next step.

## Next step

Per the project's mandatory Advisor-consultation rule, both Claude's
own read and a fresh Advisor read on what this second result means
will be presented to Jason side by side before any direction is
proposed.
