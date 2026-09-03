# Post-Release Directional Continuation

**Status: frozen specification, not yet tested** -- drafted 2026-09-03,
after both Claude and the Path-to-Profitability Advisor independently
recommended shelving the options/volatility-structure idea (scope
creep -- a new broker, an unbuilt options-pricing machinery, and a
data cost that isn't even quoted yet, all in service of a structure
with nowhere proven to attach it) and returning to the project's real,
longstanding bottleneck: no directional setup has ever cleared the
promotion bar. This is hypothesis #17.

## Where this came from

exp-039 (CPI/NFP) and exp-040 (FOMC) both confirmed the same thing
twice: NQ moves MORE (larger magnitude) around scheduled macro
releases than on normal days. Both studies deliberately stopped there
-- neither tested whether that extra movement has a predictable
DIRECTION, and both disclosed this as their Step-2-gate condition 5
limitation (no simple mechanical rule specifiable without fitting).

Rather than build a costly options structure to bet on magnitude alone
(the idea just shelved), this study asks the natural next question the
project's own two findings raised: on a day already confirmed to be
unusually volatile because of scheduled news, does the FIRST direction
NQ moves after the release tend to CONTINUE, or does it tend to
reverse? If continuation holds up, it is directly a mechanical
long/short rule -- go with the initial move -- not a magnitude-only
finding like its two predecessors. This was the Advisor's own
recommendation, made independently, after being shown three other
candidates (turn-of-month seasonality, unconditional overnight drift,
order-flow imbalance) and rejecting all three: turn-of-month risks
being a third variant of an already-twice-null calendar-timing family
(day-of-week: exp-031, null; futures expiration: exp-035, null), and
order-flow imbalance repeats the exact shape of the scope creep just
shelved (new data source, unconfirmed cost, new detection machinery).
This idea uses data and machinery the project already has, zero new
cost, and rides the only two confirmed non-null findings in the
project's history.

## What this is NOT

A **characterization study**, structured like exp-039/040, not yet a
full cost-inclusive, promotion-bar-tested strategy. Unlike exp-039/040,
a positive result here WOULD constitute a specifiable mechanical rule
(condition 5 below) -- but clearing the Step 2 gate is still a
characterization finding, not automatic promotion. If this gate
passes, formalizing it into a real exp-XXX backtest with per-trade
costs, stops, and the actual promotion bar (expectancy > 0 after
costs, >= 150 trades, 90% bootstrap CI entirely above zero, Discovery
data) is a separate, explicit future decision -- not assumed here, the
same discipline used every time a characterization study has passed
its gate in this project.

## Definition

### 1. Universe -- all three confirmed release-day calendars, pooled by reusing each source module's OWN classification, unmodified

Rather than write one new unified `classify_day()` (a real risk of
re-deriving the overlap logic incorrectly), this study computes the
CPI/NFP-anchored rows and the FOMC-anchored rows as two separate
passes, each using its own already-frozen source module's own
`classify_day()` exactly as-is:

- **CPI/NFP pass** (8:30 AM anchor): every day `study_economic_calendar.classify_day()`
  returns `"cpi"` or `"nfp"` for. This module has no knowledge of
  FOMC, so the 6 FOMC/CPI same-day dates are included here as ordinary
  `"cpi"` days -- correctly, since their 8:30-11:30 AM window
  (anchor+180min) closes well before the 2:00 PM FOMC announcement on
  those same days and is not contaminated by it.
- **FOMC pass** (2:00 PM anchor): every day `study_fomc_volatility.classify_day()`
  returns `"fomc"` for -- i.e. `FOMC_PRIMARY_DATES` (47 dates), which
  already excludes the 6 FOMC/CPI overlap dates
  (`FOMC_CPI_OVERLAP_DATES`). Those 6 dates are excluded from this
  pass only, for exactly exp-040's reason: same-day morning CPI can
  contaminate interpretation of the afternoon FOMC window, so
  attribution to FOMC alone is ambiguous there.

**Correction from an earlier draft, caught in Advisor review**: that
draft claimed "CPI and NFP are already disjoint from each other and
from FOMC," which is not accurate as a blanket statement --
`FOMC_CPI_OVERLAP_DATES` is non-empty (6 dates) by definition,
`CPI_SET`/`FOMC_SET` are NOT disjoint, and the earlier code never
actually asserts disjointness against the raw `FOMC_SET`/`FOMC_DATES`.
What IS true, and is what this design relies on: `FOMC_PRIMARY_DATES`
(the FOMC pass's universe) is disjoint from `CPI_SET` by construction
-- `FOMC_CPI_OVERLAP_DATES` is defined as exactly `FOMC_SET & CPI_SET`,
so `FOMC_PRIMARY_DATES = FOMC_SET - FOMC_CPI_OVERLAP_DATES` removes
100% of that intersection, a set-algebra guarantee, not an assumption.
`FOMC_NFP_OVERLAP_DATES == 0` is separately asserted in
`study_fomc_volatility.py` already. This module runtime-asserts
`CPI_SET.isdisjoint(FOMC_PRIMARY_DATES)`,
`NFP_SET.isdisjoint(FOMC_PRIMARY_DATES)`, and
`CPI_SET.isdisjoint(NFP_SET)` itself on import, rather than relying on
the construction argument alone -- so each release day contributes
**exactly one row** to the pooled sample (never zero, never two): the
6 overlap days contribute one CPI-anchored row each; every other CPI,
NFP, and primary-FOMC day contributes its own single row.

### 2. Anchor time -- per release type, reusing existing constants

CPI/NFP days anchor at 8:30 AM ET (`OPEN_HOUR`/`OPEN_MINUTE`, the
existing project-wide convention). FOMC days anchor at 2:00 PM ET
(`FOMC_ANCHOR_HOUR`/`FOMC_ANCHOR_MINUTE`, from `study_fomc_volatility.py`).
No new anchor times introduced.

### 3. No new machinery

This study reuses `study_fomc_volatility.compute_forward_return_at()`
unmodified -- already written, already unit-tested against boundary
cases, in production use for exp-040. Zero new detection or timing
code, unlike exp-040 (which had to add that function) or the shelved
options idea (which would have needed pricing/IV-derivation code from
scratch).

### 4. Primary statistic -- signed directional continuation

For each release day, using that day's own anchor:

- `initial_return` = signed return from anchor to anchor+30min
  (`compute_forward_return_at(..., horizon_minutes=30)`) -- **not**
  absolute value, unlike exp-039/040. This is the "first move."
- `total_return` = signed return from anchor to anchor+180min
  (`compute_forward_return_at(..., horizon_minutes=180)`).
- `continuation_return` = `total_return - initial_return` -- the move
  from the 30-minute mark to the 180-minute mark, i.e. what happens
  AFTER the initial move.
- `directional_continuation` = `continuation_return * sign(initial_return)`
  -- positive when the market continues in the direction the initial
  move already went, negative when it reverses. This is exactly the
  P&L (in points, before costs) of the mechanical rule "go with the
  initial 30-minute direction, hold from the 30-minute mark to the
  180-minute mark."
- A day is **excluded** if either `initial_return` or `total_return`
  is `None` (insufficient data, same convention as every prior study),
  or if `initial_return == 0.0` exactly (no direction to test
  continuation of -- flagged in Honesty flags, count reported).

### 5. Primary test -- one-sample, not a two-group comparison

Unlike exp-039/040 (which compared release days to normal days on a
magnitude statistic), this tests whether the pooled release-day sample
of `directional_continuation` values has a mean **reliably above
zero** -- a genuine one-sample question, since "continuation" is a
property of what follows a release's own initial move, not something
normal days (which have no release to anchor to) can be directly
compared against for the primary test. Uses
`study_nq_trend_following.bootstrap_mean_ci()`, reused unmodified (the
one-sample bootstrap-mean-CI helper already written and tested for the
daily-momentum study) -- 90% CI, 2,000 resamples, `RANDOM_SEED = 11`,
same convention as every bootstrap in this project.

### 6. Secondary / descriptive comparisons (never override the primary verdict)

- **By release type**: cpi-only, nfp-only, fomc-only breakdowns of the
  same one-sample statistic -- same "descriptive only" convention as
  exp-039's CPI-only/NFP-only split.
- **Normal-day baseline**: the identical `directional_continuation`
  statistic computed on normal (non-release) days, using the 8:30
  anchor as an analog for the CPI/NFP comparison and the 14:00 anchor
  as an analog for the FOMC comparison. This directly checks whether
  any continuation found is release-specific, or just ordinary NQ
  intraday momentum that would show up on any day regardless of news
  -- an important distinction the primary one-sample test alone cannot
  make. Reported via `bootstrap_mean_diff_ci()` (release vs. matched
  normal-day baseline), reused unmodified, descriptive only.

### 7. Robustness checks (Step-2-gate condition 4)

Identical convention to every prior characterization study: (a) drop
the single largest-|`directional_continuation`| day and re-run the
primary test, (b) first-half vs. second-half chronological split.

### 8. Criteria for declaring the finding meaningful (Step 2 gate)

1. **Statistically credible** -- the 90% one-sample bootstrap CI on
   mean `directional_continuation` (pooled cpi+nfp+fomc) is entirely
   above zero.
2. **Economically meaningful** -- the mean exceeds
   `2 x ROUND_TRIP_COST_POINTS` (the same `ECONOMIC_THRESHOLD_POINTS`
   convention as every prior study).
3. **Plausible mechanism** -- a positive result is consistent with a
   documented information-uptake story (markets absorbing scheduled
   news gradually rather than instantly -- the same underlying idea as
   post-earnings-announcement drift, applied to macro news instead of
   earnings). Note: reversal would also be "plausible" under a
   different, equally real overreaction story -- this condition checks
   the result makes sense, not that continuation had to win.
4. **Not an artifact** -- survives both robustness checks in item 7.
5. **A simple mechanical rule can be specified without fitting to the
   result** -- if conditions 1-4 hold, this one is satisfied by
   construction for the **pooled** population: "on a confirmed
   CPI/NFP/FOMC release day, go with the direction of the first
   30-minute post-release move, hold to the 180-minute mark." Unlike
   exp-039/040, this study is designed so a positive result IS a
   specifiable rule, not a disclosed limitation. **Scoping caveat,
   added in Advisor review**: CPI+NFP (162 obs) outweighs FOMC (47
   obs) roughly 3.4:1 in the pooled sample, so a passing pooled result
   could in principle be carried by CPI/NFP alone while FOMC
   disagrees in sign or shows nothing. The per-type breakdowns (item
   6) are descriptive and do not gate condition 5 -- but if any
   subtype's sign disagrees with the pooled sign, the resulting
   write-up must state that plainly and narrow the "on a confirmed
   release day" rule language to only the subtype(s) that agree,
   rather than presenting a blanket three-subtype rule the data
   doesn't uniformly support.

If any condition fails, or the primary test is null, the finding is
recorded as-is and the study stops there -- same as every prior study.

### 9. Exclusion rules and scope

**Discovery slice only** (`data_split.get_discovery_data()`), same as
every hypothesis's first test in this project. A Validation-slice
replication is a separate, explicit future decision if this comes back
positive -- not automatic, not assumed here.

## Honesty flags

- **Pools three release types with two different anchor times into one
  primary test.** Per-type breakdowns (item 6) are reported so the
  pooled result can't hide a single dominant subgroup driving
  everything else to null.
- **The normal-day baseline comparison is an approximation, not a
  clean control.** Normal days have no "release" of their own to
  anchor a 30-minute initial-move window to -- using 8:30/14:00 as
  stand-in anchors is a reasonable but structural approximation, not a
  confound-free comparison. Disclosed rather than presented as
  equivalent to the CPI/NFP/FOMC anchor logic.
- **The `initial_return == 0.0` exclusion** removes days with no
  direction to test continuation of. The count excluded this way will
  be reported plainly, not folded silently into the sample.
- **A positive Step-2-gate result is a characterization finding, not a
  finished, cost-inclusive, promotion-bar-tested strategy.** Condition
  2's threshold check is a proxy for costs, not a real per-trade
  backtest with actual entries, stops, and slippage. That would be a
  separate follow-up experiment.
- **Sample size context**: roughly 81 CPI + 81 NFP + 47 FOMC ~= 209
  Discovery-window release days before any exclusions -- plausibly
  enough to eventually reach the project's standing >=150-trade
  promotion-bar minimum in a follow-up formal backtest, but that is a
  future consideration, not resolved by this characterization study.
- **Multiple-testing context, stated plainly**: this is hypothesis #17,
  the third test within the scheduled-information family (after
  exp-039 and exp-040, both magnitude-only positives). A null result
  here would not undermine exp-039/040's own findings -- magnitude and
  directional-continuation are different questions about the same
  event days. A positive result here would be judged on this study's
  own frozen criteria, not treated as pre-confirmed by the family's
  prior results.
- `purgedcv` (DSR/PBO) remains unavailable in this environment --
  flagged consistently, as on every experiment to date.

## Status

**Status: Tested. Primary test result: NULL.** Mean directional
continuation (pooled cpi+nfp+fomc, 30min initial -> 180min total) =
-2.947 pts, 90% CI [-11.328, +4.361] -- spans zero. Both robustness
checks confirm the null; the effect's sign is not even stable across
a first-half/second-half split. One disclosed, unplanned
side-observation in the cpi-only descriptive breakdown (a
statistically credible reversal tendency, not pre-registered, not
promoted) -- see `research/experiments/exp-041-post-release-directional-continuation.md`
for full results and honest treatment. No ledger entry.

**Original status line (for the record): Frozen specification, Advisor-reviewed, awaiting Jason's sign-off.**
Drafted 2026-09-03, then revised the same day per the Advisor's
focused technical review (see History). No code has been written.

## History

- 2026-09-03: After shelving the options/volatility-structure idea as
  scope creep, Jason asked to find the next idea to test. A research
  pass proposed three candidates (turn-of-month seasonality,
  unconditional overnight drift, order-flow imbalance); the Advisor
  independently rejected all three and proposed this idea instead --
  directional continuation on the already-confirmed CPI/NFP/FOMC
  release days. Claude agreed it was the strongest option. Jason
  approved drafting this frozen spec.
- 2026-09-03 (same day): Per the mandatory Advisor-consultation rule,
  the Advisor gave this specific draft a focused technical review
  before Jason's sign-off (not a re-litigation of the direction, which
  was already decided). It verified the sample-size figures,
  `compute_forward_return_at()`, and `bootstrap_mean_ci()` claims
  directly against the code and found them accurate, and confirmed the
  core `directional_continuation` algebra genuinely satisfies gate
  condition 5 by construction. It also found one overclaimed
  disjointness statement (CPI is not disjoint from the raw FOMC
  calendar, only from `FOMC_PRIMARY_DATES` after exclusion, and that
  specific fact was never actually runtime-asserted anywhere), one
  resulting ambiguity about whether the 6 FOMC/CPI overlap days count
  as CPI observations or are dropped entirely, and one real gap in
  condition 5's scoping (a pooled positive result could in principle
  be carried by CPI/NFP alone while FOMC disagrees, given CPI+NFP's
  3.4:1 weight advantage). All three are fixed above: the universe is
  now built from two separate passes reusing each source module's own
  `classify_day()` unmodified (resolving the ambiguity in favor of
  including the 6 overlap days as CPI observations, which is also
  what the disjointness argument, now stated correctly and
  runtime-asserted, requires), and condition 5 now carries an explicit
  scoping caveat requiring per-subtype sign agreement to be checked
  and disclosed before stating a blanket three-subtype rule.

- 2026-09-03 (same day): Jason signed off on the Advisor-reviewed
  spec. Implemented and run against real Discovery data. Primary test
  NULL -- gate conditions 1 and 2 both fail, point estimate negative,
  both robustness checks stay null, effect sign unstable across the
  chronological split. One disclosed, unplanned side-observation (a
  statistically credible cpi-only reversal tendency) recorded as a
  lead, not promoted, per this project's rule against fitting a
  hypothesis after seeing the data. Full results in
  `research/experiments/exp-041-post-release-directional-continuation.md`.
  Per the mandatory Advisor-consultation rule, both Claude's and the
  Advisor's independent reads on what this null means for what's next
  are being presented to Jason before any direction is proposed.
