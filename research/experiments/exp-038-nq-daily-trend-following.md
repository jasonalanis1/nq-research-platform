# exp-038: NQ Daily Time-Series Momentum (Trend-Following)

**Status: characterization-and-promotion study, result NULL on primary
test. No ledger entry, no mechanical rule promoted. First
daily-resolution study in this project's history.**

## Hypothesis

Full specification frozen in advance in
`research/studies/nq-daily-trend-following.md`, including a disclosed,
one-time adaptation of the standing promotion bar (see that doc's "Why
the promotion bar is adapted for this study," and the matching note in
`docs/ROADMAP.md`'s "Promotion bar" section) -- reviewed and approved
by Jason before any code was written.

One primary question, one primary outcome, pre-committed:

> Is the mean daily net P&L of a 252-trading-day time-series-momentum
> position (long when the trailing ~12-month log return is positive,
> short when negative, daily rebalanced, fully causal) positive and
> statistically credible -- 90% bootstrap CI on the mean entirely above
> zero?

## Data used

Discovery slice only (`data_split.get_discovery_data()`),
`NQ_1min_databento_2026-08-20.csv`, same file used by every prior
study. 2,101 total Discovery calendar days; 1,763 classifiable once
252+ prior daily returns exist; 1,463 with a computed daily P&L (a day
is excluded from P&L if it, or its nearest prior valid day, lacks a
reference close -- see Honesty flags for a bug caught and fixed during
implementation).

## Method

Exactly as frozen in the study spec, no deviation:

1. `mom[t]` = sum of the 252 most recent daily log returns strictly
   before day `t`, using `study_volatility_regime.py`'s existing
   `compute_daily_ref_closes()` / `compute_daily_log_returns()`
   building blocks, reused unmodified.
2. `position[t] = sign(mom[t])`, no neutral band, ties hold the
   previous position.
3. Daily rebalancing (a disclosed simplification of the literature's
   discrete monthly rebalance).
4. `net_pnl[t] = position[t] * (ref_close[t] - ref_close[t-1])`,
   minus `2 x ROUND_TRIP_COST_POINTS` on any day the position flips
   relative to the prior valid day.
5. 90% bootstrap CI (2,000 resamples, seed=11) on mean daily net P&L,
   via a new `bootstrap_mean_ci()` -- the same resample-and-recompute
   pattern as every other bootstrap in this project.
6. Adapted Step-2-gate check 2: mean daily net P&L must be >= 2x this
   strategy's own realized average daily cost drag (not a fixed
   per-trade constant, since discrete trades aren't this mechanism's
   natural unit).
7. Two pre-specified robustness checks: (a) drop the single
   largest-magnitude daily P&L day, (b) first-half vs. second-half
   split-sample stability.
8. Mandatory disclosure: total number of position flips.

Implementation: `src/study_nq_trend_following.py`. Unit tests (11,
covering the momentum-window math, tie-holding and its first-day
default, hand-checked daily P&L and flip-cost application, the
day-skipping join behavior described below, the bootstrap CI correctly
separating a strong effect from pure noise, and the drop-largest-day
robustness check): `tests/test_study_nq_trend_following.py`, all
passing (121/121 in the full suite).

## Results

### Primary test (mean daily net P&L)

| n | mean net P&L (pts) | 90% CI | Statistically credible? |
|---|---|---|---|
| 1,463 | +0.772 | [-4.075, +5.501] | **No** |

CI spans zero by a wide margin relative to the point estimate.

**Step-2 gate, checked honestly against the pre-committed (adapted) criteria:**

1. Statistically credible (CI excludes zero): **FALSE**.
2. Economically meaningful (>= 2x own realized cost drag, 0.0902 pts):
   **TRUE** (0.772 >= 0.090) -- but see Honesty flags: with only 44
   flips over 1,463 days, the realized cost drag is tiny, making this
   adapted threshold easy to clear whenever the point estimate is
   positive at all. It does not rescue the result, since condition 1
   already fails and the frozen spec's own rule stops the study there
   regardless of condition 2.
3. **Mandatory disclosure -- position flips: 44** across 1,463
   classifiable days (~6.5/year over 6.75 years) -- an actively
   updating signal, not a bet on one or two isolated historical
   trends.

Per the frozen spec, condition 1 fails outright, so the study stops
here -- conditions 3-5 (plausible mechanism, artifact checks beyond
what's reported below, specifiable rule) are moot.

### Robustness checks (reported for completeness, not used to rescue the primary result)

- **Drop single largest-magnitude daily P&L day** (2020-03-16, the
  COVID-crash volatility spike): mean net P&L rises to +1.355 pts, CI
  [-3.459, +6.303] -- still spans zero. Consistent with the primary
  null; not an artifact of one outlier day.
- **First-half vs. second-half split**: First half: mean net P&L
  +2.130 pts, CI [-1.652, +5.648] -- CI still spans zero, though the
  point estimate clears the (low) economic threshold. Second half:
  mean net P&L -0.584 pts, CI [-9.961, +8.028] -- negative point
  estimate, fails the economic check outright. As with exp-036's and
  exp-037's own split-half checks, the two halves disagree sharply
  (positive vs. negative) and neither CI excludes zero -- the exact
  instability pattern this check exists to surface.

## Interpretation

The core hypothesis -- that a classic, academically-grounded
time-series-momentum signal carries a real, tradeable edge on NQ at
daily resolution -- is **not supported** by the primary, pre-committed
test on Discovery data. The point estimate has the plausible sign
(positive) and the signal updates at a reasonable frequency (44 flips,
not a thin 1-2-trend bet), but the CI is wide enough to span zero by a
large margin, and the split-half check shows the sign itself is
unstable across the sample rather than a consistent effect.

This is the first daily-resolution test in this project's history, and
it answers both questions the pivot was meant to settle: the
timeframe change alone did not surface an edge (ruling out "wrong
granularity" as the sole explanation for twelve straight intraday
nulls), and a mechanism with genuine outside academic support still
failed to clear even an adapted, appropriately-scoped bar on this
specific instrument and cost model. Combined with the twelve
hypotheses tested previously across level-interaction, volatility-regime,
and cross-market mechanisms, this is now **thirteen for thirteen**
across four structurally distinct mechanism families and two
timeframes.

## Bug caught and fixed during implementation

The initial implementation of `compute_daily_pnl()` walked every
classifiable day in sequence and skipped a pairing whenever either day
lacked a valid reference close -- which meant a single day with a
missing reference close (384 of 2,101 Discovery days, a pre-existing
data characteristic already present in every prior study, e.g.
exp-032's and exp-037's own ~1,716-1,717-of-2,101 valid-day counts)
silently cost up to *two* days of P&L instead of one, since both its
own row and its successor's row (whose "prior day" pointed at the
missing day) were dropped. This nearly halved the usable sample (1,164
of a possible ~1,762 pairs) before the fix. Caught by sanity-checking
the gap between "classifiable days" (1,763) and "days with computed
P&L" (originally 1,164) before trusting the result, rather than
assuming the shortfall was expected. Fixed by filtering to
valid-reference-close days FIRST, then walking consecutive pairs in
that filtered list -- the exact convention already established in
`study_es_gap_incremental_info.build_joint_dataset()` for the same
kind of gap. After the fix, 1,463 of 1,762 possible pairs are usable.
The primary result's conclusion (null) was unchanged by the fix, but
the point estimate, CI, and flip count all changed materially, so this
is recorded here rather than silently corrected.

## Next step

Per this project's standing instruction, **no mechanical trading rule
is proposed or built from this result**. No ledger entry is made (same
convention as the other characterization studies).

This result, together with the pivot that led to it, is reported back
to Jason. Thirteen hypotheses across four mechanism families and two
timeframes have now failed to clear a promotion bar on Discovery data
-- a genuine decision point on where the project goes from here.
