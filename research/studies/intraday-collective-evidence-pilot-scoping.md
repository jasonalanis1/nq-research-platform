# Intraday Collective-Evidence Pilot -- Scoping (exp-057)

## Provenance

Follow-on to exp-055/056 (the trend-family collective-evidence pilot,
2026-09-07). exp-055 found one candidate condition (weak-trend weeks)
but exp-056's prospective test on the Validation slice failed --
CI [-6.32, +156.20] crosses zero. Per the pre-registered rule, that
line is closed, and per Jason's own stated plan ("I would not let the
AI immediately run the entire 49-study collective... start with the
narrow pilot. If that pilot produces a condition that survives
out-of-sample testing, then expand the collective") expanding the
aggregation machinery to the full strategy library is NOT yet earned.

Jason asked "what should we do next" (2026-09-07). Claude and the
Path-to-Profitability Advisor gave independent takes and agreed: don't
expand the collective machinery yet; instead point it at genuinely new
ground -- the intraday condition variables from Jason's original
proposal (opening-range shape, distance from key intraday reference
points, initial post-open behavior, time-of-day) that were explicitly
deferred in exp-055's scoping (not dropped) because they don't apply
to a weekly-resolution signal family. The natural home for them is
this project's intraday-resolution strategy families. Jason approved
("Yes") scoping this next.

**Honest framing, stated up front:** unlike the trend family (exp-047,
this project's closest-ever near-miss), every intraday family tested
so far is either a decisive, statistically significant KILL (exp-025
FVG entry trigger, exp-028 Initial Balance Breakout, exp-033 Fade the
Gap -- all CIs entirely below zero) or a flat/inconclusive result
(the Level Sweep Reversal variants, CIs spanning zero). This pilot is
NOT looking for "which of these secretly works" -- none of them do,
overall. It is asking a narrower, still-legitimate question: within
each setup's own (mostly negative) sample, are there identifiable
market conditions where it does meaningfully better or worse than its
own average day? That is squarely what the collective-evidence
methodology was designed to detect, and it is honest infrastructure
-dry-run work, exactly like exp-055 was -- not a claim that a hidden
edge is expected.

## The strategy pool (4 lenses)

Two are correlated variants of the same underlying signal (same
caveat as exp-055's trend-family pilot); two are genuinely different
setups, unlike exp-055's pool, which is worth stating explicitly:

1. **Level Sweep Reversal -- close_min_distance exit, not
   protected-level filtered** (hyp tied to exp-023) -- level-sweep
   entry, one exit-rule variant.
2. **Level Sweep Reversal -- full_bar_range exit, not
   protected-level filtered** (hyp tied to exp-024) -- same entry,
   different exit rule. Correlated with #1 (same entry signal, same
   days).
3. **Initial Balance Breakout (Continuation)** (exp-028) -- a
   different underlying thesis (trend/continuation through the
   30-minute opening range, not a level-sweep reversal). Independent
   entry logic from #1/#2.
4. **Fade the Gap** (exp-033) -- a third, independent thesis
   (overnight-gap mean reversion at the open). Independent entry
   logic from #1/#2/#3.

Lenses #1 and #2 already have persisted per-trade Discovery-slice CSVs
(`data/backtest_results_level_sweep_*_not_protected_discovery.csv`),
read unmodified. Lenses #3 and #4 do not have persisted per-trade
output yet -- their existing frozen, unmodified detection/backtest
code (`detect_ib_breakout.py`, `detect_fade_the_gap.py`, `backtest.py`)
will be re-run exactly as already specified (no logic changes) to
produce per-trade Discovery-slice CSVs for this pilot to read.

## Condition variables (frozen before any result is looked at)

Four causal, point-in-time condition variables, assigned to each
trade by its own entry day:

1. **Volatility regime** -- `classify_regimes()` from
   `study_volatility_regime.py`, reused unmodified (causal expanding
   tercile: low/mid/high), by the trade's entry day.
2. **Prior-day direction** -- sign of the immediately preceding
   trading day's own daily return (up/down), a trivial causal lookup.
3. **Opening-range width** -- the first 30 minutes' high-low range
   (9:30-10:00am ET, the same IB window `detect_ib_breakout.py`
   already uses, reused unmodified), as a percentage of that day's
   prior-20-day average daily range (for scale-comparability across
   the sample), causal-expanding-tercile classified via
   `causal_expanding_tercile()` (exp-055, reused unmodified)
   (narrow/typical/wide).
4. **Time-of-day of entry** -- the trade's own entry timestamp,
   bucketed into three fixed session windows already implicit in this
   project's setups: open (9:30-10:30am ET), midday (10:30am-1:00pm
   ET), afternoon (1:00-4:00pm ET). Categorical, no ranking needed.

Jason's remaining original idea ("distance from key reference points")
is deferred again here, specifically because it needs a precise,
pre-registered definition of "key reference point" per setup (prior
high/low? prior close? overnight high/low?) that differs meaningfully
between a level-sweep setup and a gap-fade setup -- collapsing them
into one shared definition would not be a fair single condition. Left
for a future, separately-scoped follow-up if this pilot's simpler
conditions prove useful.

No other condition variables are added mid-analysis.

## Redefining "won": outcome relative to each lens's own baseline

Same rule as exp-055: for each of the 4 lenses independently,
`baseline` = that lens's own overall mean per-trade net R-multiple
(or net points, for lenses reporting points) across its full
Discovery-slice sample. For each trade, `relative_outcome = that
trade's net result - baseline`. Aggregated by condition -- not
win/loss, not raw R level.

## Aggregation: by day first, then by lens

Same core fix as exp-055, adapted to daily resolution (intraday
setups trade at most once per day, not once per week): group by
calendar trading day, not by (day, lens) pair. For each day in a
condition bucket, record how many of the 4 lenses have a trade that
day and how many of those beat their own baseline. Report, per
condition value: number of DISTINCT DAYS in that bucket, and the
average fraction of lenses beating their own baseline on those days,
with a bootstrap CI on that fraction across days (resampling DAYS,
never lens-days).

## Multiple-comparisons accounting (same discipline as exp-055)

4 condition variables: volatility regime (3 values), prior-day
direction (2 values), opening-range width (3 values), time-of-day (3
values) -- **11 buckets total**, stated here before any result is
looked at. A bucket is not eligible to be called promising unless it
clears a pre-registered floor of **30 distinct days** -- the same
floor exp-055 used, for the same reason (a week-level or day-level
bootstrap CI below that is too noisy to mean anything).

## Promotion / next-step rule (decided in advance, same as exp-055)

Exploratory infrastructure-testing only. A condition value that looks
real here becomes a single, precise, pre-registered hypothesis (one
lens or a natural combination, one condition, one direction) and gets
tested prospectively on the Validation slice -- the same exp-055 ->
exp-056 pattern, run once, no retuning regardless of outcome.

## Advisor review (v2 -- 3 required fixes, all incorporated before any code runs)

The Advisor reviewed this scope before implementation and flagged three
real problems, all addressed here:

1. **Mixing decisive-loser lenses with a flat lens under "beat own
   baseline" can manufacture false agreement.** A statistically
   rejected setup's baseline is deeply negative, so merely breaking
   even in some subset looks like a big relative win -- that can be
   plain regression to the mean in the tails of a bad strategy, not a
   shared market phenomenon. Fix: every bucket report shows each
   lens's OWN beat-rate individually, not just the aggregated
   cross-lens fraction, so a finding driven by one lens's noise (not a
   pattern shared across independent setups) is visible before it is
   ever called a candidate.
2. **Day-first aggregation only works if lenses actually co-occur on
   the bucketed days.** Level Sweep and Fade the Gap trade on a
   minority of days; Initial Balance Breakout trades most days. A
   30-distinct-day floor could be cleared almost entirely by one
   lens's activity while being reported as a 4-lens finding. Fix: a
   bucket is only eligible if, in addition to the 30-distinct-day
   floor, **at least 3 of the 4 lenses have at least 10 of their own
   trades** falling in that bucket. Per-lens trade counts are reported
   alongside every bucket result.
3. **No pre-registered rule for which candidate goes to prospective
   validation if more than one bucket clears the floor.** Fix,
   decided now, before any result: if multiple buckets are eligible
   and look separated from the 0.5 baseline, only the SINGLE most
   statistically extreme one (by the same proximity-to-significance
   score used to rank exp-055's original strategy pool: SE ~=
   (CI_upper - CI_lower) / (2*1.645), z = |point_estimate - 0.5| / SE)
   goes forward to the one prospective test. Ties broken by larger
   distinct-day count. No second attempt on a runner-up.

## What this is NOT

- Not a claim that any of these 4 setups has a hidden edge overall --
  3 of 4 are documented kills or flat results.
- Not a search across the full 49-experiment library -- 4 lenses,
  chosen for genuine setup diversity plus reuse of already-persisted
  data where available.
- Not a change to any of the 4 underlying setups' own frozen specs --
  reads/re-runs their existing, unmodified logic only.

## ASCII-only

Confirmed.
