# Collective-Evidence Pilot -- Scoping (exp-055)

## Provenance

Jason proposed (2026-09-07) shifting the research goal from "which
strategy wins" to "what conditions, found across many tested
strategies, change the odds of a good outcome" -- treating each
strategy as a lens on market behavior rather than a final product.
Claude and the Advisor both agreed the instinct is sound but flagged
two specific risks: (1) an "explanation" invented after seeing which
pockets won is not a real constraint unless the candidate conditions
are frozen before looking; (2) strategies built on the same underlying
price days are not independent evidence just because several of them
"agree" -- that can just be the same market days tripping correlated
signals. Jason then wrote his own refined plan incorporating both
fixes (pre-register conditions, aggregate by trading period before
aggregating by strategy, redefine "won" as outcome-vs-baseline rather
than win/loss) and asked to pilot it narrow: the trend/momentum family
plus its closest near-misses, not all 49 experiments. Mechanical
ranking (by a z-like proximity-to-significance score computed from
each experiment's own reported confidence interval, applied uniformly
so this selection wasn't cherry-picked by eye) showed the "closest
near-misses" outside the trend family are all either tiny-sample
(exp-026, n=44, already closed by Jason's own 2026-09-01 decision) or
decisive kills -- there is no bench of several independently-arrived-
at near-misses to draw on yet. Jason chose (2026-09-07): stay narrow,
pilot on the trend family's own variants only.

**What this pilot actually tests, honestly stated:** because exp-047,
exp-048, exp-049 and exp-051 all share the same underlying 52-week
momentum signal (048/049 differ only by exit rule; 051 differs by
blending in 3 other markets), this pilot is NOT yet a test of whether
independent strategies corroborate each other -- it's a dry run of the
AGGREGATION MACHINERY (condition tagging, week-level deduplication,
the outcome-vs-baseline definition of "won", prospective re-validation)
on a small, safe, already-well-understood family, before that machinery
is ever pointed at genuinely independent strategies. That is a
deliberate, disclosed scope limit, not an oversight.

## The strategy pool (4 lenses, 1 underlying signal)

1. exp-047 (hyp-000017) -- raw NQ weekly momentum, no overlay.
2. exp-048 (hyp-000018) -- exp-047 + hard -1R/+2R stop-target overlay.
3. exp-049 (hyp-000019) -- exp-047 + 1R trailing stop overlay.
4. exp-051 (hyp-000021) -- exp-047's signal blended across NQ/ZN/6E/CL
   into one inverse-vol-weighted portfolio.

All four reuse the exact same underlying weekly momentum computation,
unmodified, per each one's own frozen spec. This pilot does not
recompute or alter any of them -- it reads each one's already-existing
weekly P&L output.

## Condition variables (frozen before any result is looked at)

Jason's original list included several intraday/session concepts
(opening-range shape, distance from key intraday reference points,
initial post-open behavior, time-of-day) that do not apply to a
WEEKLY-resolution signal family with no intraday entry logic -- these
are explicitly deferred, not dropped, for when this pilot's machinery
is later pointed at the project's intraday-resolution families
(level-sweep, ORB, gap studies), where they are the natural fit. For
THIS pilot, four causal, point-in-time, already-existing-or-trivial
condition variables are frozen:

1. **Volatility regime** -- `classify_regimes()` from
   `study_volatility_regime.py`, reused unmodified (causal expanding
   tercile: low/mid/high), assigned to each week via that week's own
   first trading day, exactly as exp-053 already does.
2. **Prior-week direction** -- sign of the immediately preceding
   week's own log return (up/down), a trivial causal lookup already
   computed as an intermediate value in every one of these scripts.
3. **Trend strength** -- magnitude (absolute value) of the same
   52-week trailing momentum signal already driving the position
   (not its sign, its size), tercile-split via the same causal
   expanding-rank method as `classify_regimes()` (weak/moderate/
   strong).
4. **Distance from the 52-week moving average** -- the week's closing
   price's distance from its own trailing 52-week simple average of
   weekly closes, as a percentage, tercile-split the same causal way
   (near/mid/far).

No other condition variables are added mid-analysis. If a fifth
condition seems interesting once results are in, it becomes a fresh,
separately pre-registered follow-up, not an addition to this pass.

## Redefining "won": outcome relative to each lens's own baseline

For each of the 4 lenses independently: `baseline` = that lens's own
overall mean weekly net return across its full Discovery-slice sample
(already computed, its own existing headline result). For each week,
`relative_outcome = that week's net return - baseline`. This is what
gets aggregated by condition -- NOT win/loss, NOT a raw return level
(which would just reward the trend family's already-known overall
lean), but whether a condition shifts a lens away from ITS OWN typical
week specifically.

## Aggregation: by week first, then by lens (Jason's core fix)

For each condition variable and each of its 2-3 values (e.g.
volatility = low/mid/high): group by ISO week, not by (week, lens)
pair. For each week in that bucket, record how many of the 4 lenses
have data that week and how many of those beat their own baseline.
Report, per condition value: number of DISTINCT WEEKS in that bucket
(the real, deduplicated sample size -- this is the number that matters
for judging statistical power, not "number of lens-weeks"), and the
average fraction of lenses beating their own baseline in those weeks,
with a bootstrap CI on that fraction across weeks (resampling WEEKS,
never lens-weeks, so a week where all 4 lenses happen to agree cannot
count 4 times in the resample).

## Multiple-comparisons accounting (Advisor-required, v2)

4 condition variables are being scanned: volatility regime (3 values),
prior-week direction (2 values), trend strength (3 values), distance
from the 52-week moving average (3 values) -- **11 buckets total**,
stated here before any result is looked at, so a "promising" bucket is
visibly one candidate out of a known 11, not presented as if it were
the only thing tested. A bucket is not even eligible to be called
promising unless it clears a pre-registered floor of **30 distinct
weeks** -- below that, a week-level bootstrap CI is too noisy to mean
anything (exp-053/054's n=8 result is the cautionary example this floor
exists to prevent). This does not replace the prospective-validation
gate below -- it only sets the bar for what's even worth writing down
as a candidate to re-test.

## Promotion / next-step rule (decided in advance)

This pilot is explicitly exploratory infrastructure-testing, per the
Provenance section above -- nothing found here gets treated as a
tradeable finding regardless of how clean it looks, because the 4
lenses are too correlated with each other to count as independent
corroboration. The concrete next step, if a condition value shows a
real-looking shift here: state it as a single, precise, pre-registered
hypothesis (one signal, one condition, one direction) and test it
prospectively on the Validation slice -- exactly the exp-053 -> exp-054
pattern already used once. Only after a condition survives THAT step
would it be a candidate to re-test against genuinely independent
strategy families (the next phase Jason described).

## What this is NOT

- Not a search across all 49 experiments -- explicitly scoped to 4
  correlated variants of one signal family, by Jason's own choice.
- Not proof that any condition matters -- a machinery dry run.
- Not a change to any of the 4 underlying strategies' own frozen specs
  or results -- reads their existing outputs only.

## ASCII-only

Confirmed.
