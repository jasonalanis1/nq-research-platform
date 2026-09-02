# exp-036: Volatility-Regime Conditioning of Post-8:30 Directional Return

**Status: characterization study, result NULL on primary test. No ledger
entry, no mechanical rule proposed or built.**

## Hypothesis

Full specification frozen in advance in
`research/studies/volatility-regime-post-open-behavior.md`, through a
formal Phase 2 Research Direction Report, a Frozen Study Specification
reviewed line-by-line, and one Jason-approved modification (removal of
an originally-proposed minimum prior-history floor), all before any
code was written.

One primary question, one primary outcome, pre-committed:

> Does the mean 30-minute post-8:30 directional return (Close at 9:00
> minus the 8:30 Open) differ between days classified into the high
> realized-volatility tercile versus the low realized-volatility
> tercile, where the tercile is computed causally from a 20-trading-day
> trailing lookback and an expanding percentile-rank pool?

This is a **characterization study**, not a strategy. No entry/exit is
defined, no setup file exists in `research/setups/`, and per the study
doc's Step 2 gate, a significant primary result would not by itself
justify building a mechanical rule.

## Data used

Discovery slice only (`data_split.get_discovery_data()`): 2,101 trading
days, 2015-01-01 through 2021-10-03. Validation and Holdout were never
touched. 2,061 of those days were classifiable (had 20+ prior daily
returns available); 850 landed in the high tercile, 748 in the low
tercile, and 463 in the excluded middle tercile.

## Method

Exactly as frozen in the study spec, no deviation:

1. Daily return `r[t] = ln(ref_close[t] / ref_close[t-1])`, using
   `study_overnight_gap.get_reference_close()` unmodified (last bar's
   Close at/before 4:00 PM ET).
2. `vol[t]` = sample stdev (`ddof=1`) of the 20 most recent `r` values
   strictly before day `t`.
3. Regime for day `t` is fully determined as of 4:00 PM ET on day
   `t-1`, before day `t`'s own overnight session or open.
4. Tercile via expanding causal percentile rank against `{vol[s] : s <=
   t}` -- no minimum pool-size floor (the one change Jason required
   before implementation). High = rank >= 2/3, low = rank <= 1/3,
   middle excluded from the primary comparison.
5. Primary horizon: 30 minutes post-8:30 (structurally chosen in
   advance -- the project's Initial Balance window -- not selected
   because it performed well).
6. Secondary horizons 60/90/120/180 minutes, reported descriptively
   only, never used to judge the study.
7. 90% bootstrap CI (2,000 resamples, seed=11) on the difference in
   mean primary-horizon return, via
   `study_futures_expiration.bootstrap_mean_diff_ci()` reused
   unmodified.
8. Two pre-specified robustness checks: (a) drop the single
   largest-magnitude return day, (b) first-half vs. second-half
   chronological split-sample stability.

Implementation: `src/study_volatility_regime.py`. Unit tests (11,
covering the log-return math, the trailing-volatility window edges,
the causal-classification behavior including a hand-verified
all-time-low and a hand-verified mid-tercile case, and the
forward-return window boundary): `tests/test_study_volatility_regime.py`,
all passing.

## Results

### Primary test (30-minute horizon, high vs. low tercile)

| | n | mean (pts) | median (pts) | std |
|---|---|---|---|---|
| High-vol regime | 701 | +1.118 | +0.75 | 22.55 |
| Low-vol regime | 615 | -0.123 | 0.00 | 9.89 |

Mean difference: **+1.241 points** ($24.82 per contract). 90% bootstrap
CI: **[-0.252, +2.862]** -- spans zero. Cohen's d = 0.070 (negligible).

**Step-2 gate, checked honestly against the pre-committed criteria:**

1. Statistically credible (CI excludes zero): **FALSE**.
2. Economically meaningful (|mean diff| >= 1.5 pts): **FALSE** (1.241 <
   1.5).

Both of the first two gate conditions fail outright. Per the frozen
spec ("if any of the five fail, or the primary test is null, the
finding is recorded as-is and the study stops there"), the remaining
three conditions (plausible mechanism, artifact checks, specifiable
rule) are moot -- the primary test is null and the study stops here.

### Robustness checks (reported for completeness, not used to rescue the primary result)

- **Drop single largest-magnitude day** (2021-02-24 excluded): mean
  diff rises slightly to +1.447 pts, CI [-0.011, +2.912] -- still spans
  zero, still not economically meaningful. Consistent with the primary
  null; not an artifact of one outlier day.
- **First-half vs. second-half split**: First half (2015-2018ish):
  mean diff +0.055 pts, CI [-1.418, +1.482] -- flat null. Second half
  (2018-2021ish): mean diff +1.986 pts, CI [-0.845, +4.790] -- larger
  in magnitude and crosses the 1.5-point economic threshold, but the CI
  still spans zero (not statistically credible) and the two halves
  disagree with each other by roughly 36x in point estimate. This is
  exactly the kind of instability the split-half check exists to
  surface: the primary result is not stable across the sample, which
  independently reinforces the "stop here" conclusion rather than
  suggesting a sub-period worth chasing.

### Secondary horizons (descriptive only, per the frozen spec)

| Horizon | Mean diff (pts) | 90% CI | Significant? |
|---|---|---|---|
| 60 min | +1.809 | [-0.270, +3.914] | No |
| 90 min | +2.740 | [-0.682, +6.322] | No |
| 120 min | +4.485 | [+0.334, +8.903] | **Yes** |
| 180 min | +4.347 | [-0.783, +9.458] | No |

The 120-minute horizon's CI happens to exclude zero. Per the frozen
spec, secondary horizons are explicitly **never used to judge whether
the study succeeded**, precisely to prevent exactly this outcome from
being treated as a discovery. The spec pre-committed to this rule for
exactly this reason: with five horizons examined descriptively, seeing
one nominally "significant" result by chance is expected, not
noteworthy, and promoting it to primary status after the fact would be
the "best horizon" fishing the spec explicitly prohibited. It is
reported here for transparency and is not evidence of anything on its
own.

## Interpretation

The core hypothesis -- that realized-volatility regime alone carries
information about the direction of the post-open move, independent of
any specific price level -- is **not supported** by the primary,
pre-committed test on Discovery data. The point estimate has the
plausible sign (high-vol days show a larger, more positive mean move)
but the effect is both statistically indistinguishable from zero and
below the economic bar even before considering costs, and the
split-half check shows the estimate is unstable across the sample
rather than a consistent underlying effect.

This is a clean, honest null on a genuinely different, non-level-based
mechanism -- the first of its kind in this project's history. Combined
with the nine level-interaction hypotheses (six reversal variants, IB
Breakout, Fade the Gap, VWAP Mean Reversion) tested previously, this
extends the project's overall finding: ten hypotheses spanning two
structurally distinct mechanism families have now failed to clear (or,
in this case, even approach) a promotion bar on Discovery data.

## Next step

Per Jason's explicit and repeated instruction, **no mechanical trading
rule is proposed or built from this result**, regardless of the
descriptive secondary-horizon finding. No ledger entry is made (same
convention as the other characterization studies, exp-029/030/031/035).

This result, together with the rest of the Phase 2 review, is reported
back to Jason for his decision on Phase 2 direction (continue mining
the remaining untested families -- scheduled economic information,
cross-market/relative value -- modify further, or pivot).
