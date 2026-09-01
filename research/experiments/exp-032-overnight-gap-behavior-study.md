# exp-032 — Overnight Gap Behavior Study, Discovery slice (real data)

**Date:** 2026-09-01
**Type:** CHARACTERIZATION STUDY, not a strategy backtest. See
`research/studies/overnight-gap-behavior.md` for the frozen definition.
**This study's own Step 3 trigger was met — see "Next step" below and
`research/experiments/exp-033-fade-the-gap.md` for the resulting
mechanical-rule test.**

## Question

The first study in this project to look at the jump BETWEEN sessions
rather than behavior inside one: does NQ's overnight gap (today's 8:30
AM open vs. the prior day's 4:00 PM ET reference close) tend to fill,
and does its size/direction predict anything about forward returns?

## Data used

`data/NQ_1min_databento_2026-08-20.csv`, Discovery slice only.

## Method

Exactly as frozen in `research/studies/overnight-gap-behavior.md`:
`prior_close` = last available bar at/before 4:00 PM ET on the prior
trading day; `gap` = today's 8:30 AM open minus `prior_close`. Step 1:
plain fill-rate (does price touch back to `prior_close` by noon ET),
reported separately for gap-up and gap-down days, with a 90% bootstrap
CI on the proportion. Step 2: Pearson correlation (90% bootstrap CI, no
threshold) between `gap` and forward return from today's open at five
fixed horizons (+30/60/90/120/180 min), same methodology and bootstrap
convention as `research/studies/open-return-persistence.md`.

Ran via a temporary, verified performance-only driver (deleted after
use, byte-identical to the direct `scan_all_days()` on a 200-day check
slice) against 1716 usable Discovery days.

## Results

**Step 1 — gap-fill rate by noon:**

| Group | n | Filled | Rate | 90% CI |
|---|---|---|---|---|
| Gap up | 784 | 458 | 58.4% | [55.5%, 61.4%] |
| Gap down | 556 | 323 | 58.1% | [54.7%, 61.5%] |

Both confidence intervals sit entirely above 50% — statistically
distinguishable from a coin flip.

**Step 2 — correlation(gap, forward_return):**

| Horizon | n | Correlation | 90% CI | Significant? |
|---|---|---|---|---|
| +30 min | 1345 | -0.0601 | [-0.1370, +0.0166] | No |
| +60 min | 1345 | -0.0735 | [-0.1556, +0.0111] | No |
| +90 min | 1318 | -0.1408 | [-0.2142, -0.0595] | **Yes** |
| +120 min | 1318 | -0.0771 | [-0.1585, +0.0122] | No |
| +180 min | 1318 | -0.0484 | [-0.1267, +0.0409] | No |

## Interpretation

**The first result in this project that isn't a clean null.** Both
findings point the same direction and are mutually consistent: gaps
fill somewhat more often than chance in both directions (~58% vs. a
50% baseline), and a larger gap is associated with a more negative
90-minute forward return (i.e., some reversion, not further extension,
by that specific horizon). Neither effect is huge — a 58% fill rate is
a real edge over a coin flip but far from dramatic, and only one of five
horizons was significant on the correlation check — but this is the
first time in this project's history that evidence has pointed toward a
real, non-null relationship rather than confirming "no edge here."

**Read this cautiously, not triumphantly, for two honest reasons.**
First, multiple-testing context: Step 1 (2 groups) plus Step 2 (5
horizons) is 7 comparisons on the same underlying days, and only 1 of
those 7 (the +90min correlation) was individually significant beyond
the fill-rate finding itself — a single "hit" among several tests
carries less weight than a single pre-registered test would. Second,
and more fundamentally: this characterization and any mechanical rule
built from it would both be evaluated on the SAME Discovery slice — a
rule constructed to exploit a pattern found on this data will tend to
look good on this same data almost by construction. That is exactly why
this project's promotion path requires a genuinely separate Validation
slice before treating anything as real, and why a positive Discovery
result here is a reason to test further, not a reason to conclude
anything is proven yet.

## Next step

Per this study's own frozen Step 3 rule, this trigger condition is met
(a horizon correlation's CI excludes zero). A frozen, mechanical
"fade-the-gap" trading rule has been defined
(`research/setups/fade-the-gap.md`) and is being backtested fresh
against the Discovery slice as exp-033 — not because this study proves
an edge, but because the disciplined next step this project has always
taken when a characterization shows something real is to turn it into
an actual, costed, testable rule and hold it to the exact same
promotion bar as everything else.
