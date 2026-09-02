# Futures Expiration/Rollover Proximity Conditioning of Initial Balance Breakout

**Status: frozen definition, not yet tested** — drafted 2026-09-02, at
Claude's own initiative as research lead, continuing per Jason's
standing direction ("keep pushing... staying towards the overall goal")
immediately after VWAP Mean Reversion (exp-034) became the ninth
strategy hypothesis rejected.

## Where this came from

Two things pointed here independently. First, `docs/ROADMAP.md` has
named "a calendar cut fine enough to need data this project doesn't
have yet (an economic-release calendar, futures expiration dates)" as
one of the two most plausible remaining sources of genuinely new ground
since exp-031, without ever actually being tested — it was named as an
open question, not investigated. Second, and more concretely,
`docs/ROADMAP.md`'s own longstanding data-quality note (written back
when this project was still on Yahoo data, carried forward as a general
caveat) already flags that a continuous futures contract series
"introduces small price jumps at contract rollover dates" — a specific,
falsifiable claim about THIS data that has sat unexamined since it was
written.

This reuses the same post-hoc conditioning-check pattern already
established for `research/setups/day-of-week-ib-breakout.md` (exp-031):
group Initial Balance Breakout's already-computed, already-resolved
1654 Discovery-slice trades (from exp-028, unmodified) by a calendar
attribute, with no new backtest and no change to IB Breakout's own
frozen definition. It also adds one genuinely new, non-strategy
measurement: whether the overnight gap itself (already computed and
studied in exp-032) is measurably larger in absolute size near
expiration than elsewhere — a direct test of the rollover-splice
caveat above, independent of any trading rule.

## What this is NOT

This does not change Initial Balance Breakout's definition (range,
entry, stop, target — `research/setups/initial-balance-breakout.md`,
unchanged) in any way, and it does not change Fade the Gap's or the
Overnight Gap Behavior study's gap computation
(`study_overnight_gap.py`'s `get_reference_close()`/gap formula,
reused unmodified). It is a **post-hoc conditioning check** on data
this project has already collected, split by an attribute (proximity
to a public, well-documented futures expiration calendar) that was
always available and never looked at.

## An important honesty flag up front, before the definition

**We do not know the exact roll methodology Databento used to build
this continuous contract series** (a fixed number of days before
expiration, a volume/open-interest crossover, or something else) — that
detail isn't recorded anywhere in this project's data files or docs.
So "proximity to expiration," as defined below, uses the CME's public,
independently-documented quarterly IMM expiration schedule (third
Friday of March/June/September/December, the standard convention for
CME equity index futures including NQ) as a proxy for when a
splice-related anomaly might plausibly appear in this file — not the
actual date(s) any anomaly would really fall on. If this study finds
nothing, that could mean there's no real effect, or it could mean the
actual roll date(s) don't line up closely with the public expiration
date the way this proxy assumes. Both possibilities are reported
honestly in the write-up rather than treating a null result as a final
answer about rollover effects in general.

## Definition

### 1. The grouping variable: Expiration Week (public IMM calendar)

For each of NQ's four quarterly contract months (March, June, September,
December), the standard expiration date is the third Friday of that
month. **Expiration Week** is defined as the five NY business days
(Monday-Friday) of the calendar week containing that Friday. Every
other NY business day in the Discovery slice is **Normal Week**. This
is computed purely from the calendar (Python's own weekday arithmetic)
— no market data is used to define the grouping, so there is no
look-ahead and no fitting to this project's own price series.

### 2. What gets measured — two independent checks

**Check A (reuses exp-028's trades, no re-backtest):** Initial Balance
Breakout's 1654 Discovery-slice trades, split into Expiration Week vs.
Normal Week using each trade's own `date`. For each group: trade count,
win rate, expectancy (mean `r_multiple_net`), and a 90% bootstrap
confidence interval on that group's total R (2,000 resamples, same
convention as every bootstrap check in this project) — same promotion
bar as every other setup/subgroup, not relaxed for being a subgroup.

**Check B (new measurement, not a strategy):** using
`study_overnight_gap.py`'s own unmodified gap computation
(`get_reference_close()`, `compute_day_gap_and_returns()`) re-run across
every Discovery day, the **absolute** overnight gap size (`abs(gap)` in
points) is compared between Expiration Week and Normal Week: mean
absolute gap in each group, and a 90% bootstrap confidence interval on
the DIFFERENCE in mean absolute gap between the two groups (Expiration
Week minus Normal Week). This directly tests the "small price jumps at
rollover" claim from `docs/ROADMAP.md` on its own terms, independent of
whether IB Breakout specifically is affected.

### 3. No cherry-picking

Both groups, in both checks, are reported in full regardless of which
looks better or worse — same discipline as the day-of-week study.

## Honesty flags

- **A calendar-week-wide bucket, not a narrower window** (e.g. only the
  expiration day itself, or only the day after when a splice would
  first be visible) — chosen as the natural first, coarsest cut,
  consistent with how the day-of-week study also started coarse
  (whole weekdays, not a finer session-time split). A narrower window
  is a legitimately different, untested follow-up if this comes back
  positive.
- **The public IMM date is a proxy for the actual (unknown) roll
  date(s) in this file** — see the flag above. A null result here
  cannot rule out a real splice effect on a different date; it can only
  rule out an effect concentrated around the public expiration date
  specifically.
- **Two explicit comparisons** (Check A's expectancy-by-group, Check
  B's gap-magnitude-by-group) — both reported regardless of outcome,
  per #3, but this is itself now the fifth conditioning/characterization
  check run in this project (after price persistence, breakout volume,
  and day-of-week on IB Breakout, plus the overnight gap study itself),
  and the second calendar-based one. `purgedcv` remains unavailable for
  the formal DSR/PBO correction — flagged consistently, as on every
  experiment in this project to date.

## Multiple-testing context

Two independent statistical comparisons (IB Breakout expectancy by
expiration proximity; absolute gap magnitude by expiration proximity),
run against data already used to test IB Breakout (exp-028) and the
gap-fill/correlation finding (exp-032). A positive result in either
check, found this way, would need the same treatment this project has
already given every subgroup-style finding (the day-of-week study, the
trend-structure liquidity filter): a specific, separately-justified
mechanical rule, tested next, not treated as confirmed on the spot.

## Status

**Tested, 2026-09-02, against real Discovery-slice data — clean null
on both checks.** Check A: Initial Balance Breakout's expectancy in
Expiration Week (n=131, -0.086R) and Normal Week (n=1578, -0.067R) are
both negative and statistically indistinguishable from each other —
neither clears the promotion bar, and expiration proximity explains
nothing about IB Breakout's existing rejection. Check B: mean absolute
overnight gap is somewhat larger in Expiration Week (37.03 pts, n=107)
than Normal Week (32.84 pts, n=1609), but the 90% bootstrap CI on that
difference is [-4.12, +13.70] pts — spans zero, not statistically
significant. See `research/experiments/exp-035-futures-expiration-effects.md`
for the full write-up, including the honest caveat that a null result
here cannot rule out a real splice effect on whatever the actual
(unknown) roll date turns out to be, only around the public expiration
date used as this study's proxy.

## History

- 2026-09-02: this document written, at Claude's own initiative as
  research lead, immediately following VWAP Mean Reversion's rejection
  (exp-034) — chosen as the next step because it is a genuinely
  untested calendar dimension that needs no new data acquisition (only
  a public, well-documented expiration calendar and data already
  collected), rather than continuing to generate new strategy variants
  on the gap or VWAP theses without a specific new reason to expect a
  different result.
- 2026-09-02 (later same session): tested against the real Discovery
  slice (exp-035). Clean null on both checks — see Status above.
