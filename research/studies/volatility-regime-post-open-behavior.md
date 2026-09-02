# Volatility-Regime Conditioning of Post-8:30 Directional Return

**Status: frozen specification, not yet tested** — drafted 2026-09-02,
through a formal research-direction review and a two-round sign-off
exchange with Jason (a Phase 2 Research Direction Report, then a
Frozen Study Specification, then one approved modification) before any
code was written — the most deliberately gated study this project has
produced.

## Where this came from

After VWAP Mean Reversion (exp-034) and the Futures Expiration study
(exp-035), Jason asked for a formal research-direction review rather
than another experiment: what strategy families has this project
actually explored, what mechanisms do they cover, and what's left. That
review found that all nine strategy hypotheses tested to date — six
reversal-off-a-swept-level variants, Initial Balance Breakout, Fade the
Gap, and VWAP Mean Reversion — are the same underlying kind of bet:
something happens when price touches, breaks, or reverts to a specific
reference price. Twenty-two of the project's thirty-five experiment
files belong to the reversal family alone. No hypothesis tested so far
has asked whether **volatility regime itself** — a mechanism grounded in
the well-documented empirical fact of volatility clustering, and in
regime-dependent institutional flow (vol-targeting, risk-parity
rebalancing, dealer gamma hedging) — carries information about post-open
behavior, independent of any specific price level.

Jason approved moving forward with this direction, then required the
hypothesis be tightened to one primary question and one primary outcome
before any code was written, and reviewed a full Frozen Study
Specification line by line before authorizing implementation. The one
change made during that review: the originally-proposed "minimum 60
prior classifiable days" eligibility rule was removed rather than kept,
since it could not be justified as methodologically necessary
independent of the eventual result (see Honesty flags below) — the
causal expanding-window classification is what prevents look-ahead, not
an arbitrary minimum-history floor.

## What this is NOT

This is a **characterization study**, not a strategy. No trade is
placed, no entry/exit is defined, and no setup file is created in
`research/setups/`. Per Jason's explicit instruction, a positive,
statistically significant finding here does **not** automatically
become a mechanical trading rule — that requires all five conditions in
the Step 2 gate below to hold, checked honestly, not assumed because the
primary test came back significant.

## Definition

### 1. Realized volatility calculation

A daily return series built from an already-frozen building block, not
a new one: `r[t] = ln(ref_close[t] / ref_close[t-1])`, where
`ref_close[t]` is `study_overnight_gap.py`'s existing
`get_reference_close()` — the last available bar's Close at or before
4:00 PM ET on trading day `t` — reused completely unmodified.

### 2. Trailing lookback

Realized volatility for day `t`, `vol[t]`, is the sample standard
deviation (`ddof=1`) of the 20 most recent daily returns strictly
preceding day `t`: `vol[t] = stdev(r[t-20], ..., r[t-1])`. Twenty
**trading** days, not calendar days.

### 3. When the regime becomes known

`vol[t]` depends only on `r[t-1]` and earlier, which depend only on
reference closes up through day `t-1`. So day `t`'s regime label is
fully determined as of **4:00 PM ET on day `t-1`** — strictly before
day `t`'s overnight session and its own 8:30 AM open. No information
from day `t` or later enters its own regime label.

### 4. Tercile classification — expanding, causal, no minimum floor

Terciles are computed on an **expanding causal window**, never a fixed
whole-Discovery-sample split (which would let a day's label depend on
volatility levels that hadn't happened yet). For day `t`: rank `vol[t]`
by percentile against `{vol[s] : s <= t}` — every classifiable day from
the start of Discovery through `t`, inclusive. High regime = percentile
rank >= 2/3; low regime = percentile rank <= 1/3; middle tercile
excluded from the primary comparison. **No minimum prior-history floor
is imposed** — see Honesty flags for what this means for the earliest
classified days.

### 5. Primary return horizon — 30 minutes

Chosen before any volatility data was examined, justified structurally:
30 minutes is this project's own most fundamental, already-frozen time
window — the Initial Balance window `detect_ib_breakout.py` and the
VWAP setup's warmup period are both built on — not a horizon chosen
because it performed well in any prior study.

### 6. Secondary horizons — 60, 90, 120, 180 minutes

The same horizon menu already used identically in both
`study_open_return_persistence.py` and `study_overnight_gap.py`, reused
here for comparability. Reported descriptively, never used to judge
whether the study succeeded. Explicitly noted: 90 minutes is the
horizon that showed significance in the unrelated Overnight Gap study —
precisely because of that, it is demoted to secondary here rather than
promoted to primary by association.

### 7. Return calculation

Signed return in NQ points: Close at (8:30 + horizon) minus today's own
8:30 AM Open, using the last available Close within the horizon window
— identical logic to the forward-return computation already used in
`study_overnight_gap.py` and `study_open_return_persistence.py`. A day
without enough data to reach a given horizon is excluded from that
horizon only.

### 8. Statistical test and confidence interval

90% bootstrap confidence interval (2,000 resamples, `RANDOM_SEED = 11`)
on the difference in mean primary-horizon return between the high- and
low-regime groups, using the identical `bootstrap_mean_diff_ci()`
already written for the futures-expiration study (exp-035) — imported
and reused unmodified, not reimplemented. Significant = the CI excludes
zero, the same convention used everywhere else in this project. Effect
size reported as Cohen's d alongside the raw point difference. No
additional significance test is stacked on top.

### 9. Exclusion rules

Discovery slice only (`data_split.get_discovery_data()`). A day is
excluded from classification if fewer than 20 prior daily returns are
available. Middle-tercile days are excluded from the primary
comparison (retained only for descriptive context). A day is excluded
from a given horizon only if that horizon's return can't be computed.
No return-value outlier is ever removed from the primary analysis.

### 10. Criteria for declaring the characterization meaningful (Step 2 gate)

All five, all pre-committed before any data is examined:

1. **Statistically credible** — the 90% CI on the primary-horizon mean
   difference excludes zero.
2. **Economically meaningful** — the absolute mean difference exceeds
   twice `backtest.py`'s own existing `ROUND_TRIP_COST_POINTS` (imported
   unmodified, currently 0.75 points), i.e. >= 1.5 NQ points. A
   difference smaller than transaction costs can't be actionable
   regardless of significance.
3. **Plausible mechanism** — the effect's direction is explainable by
   volatility clustering / regime-dependent flow, not a story invented
   to fit whichever sign appears.
4. **Not an artifact** — survives two pre-specified robustness checks:
   (a) the primary result with the single largest-magnitude return day
   removed, and (b) a first-half vs. second-half chronological
   split-sample stability check. Neither is a search for a better cut —
   both are reported as-is.
5. **A simple mechanical rule can be specified without fitting to the
   result** — any proposed rule's direction and sizing must follow
   directly from the characterization's own sign and magnitude.

If any of the five fail, or the primary test is null, the finding is
recorded as-is and the study stops there. That is a successful research
outcome, not a failure requiring a fix.

## Honesty flags

- **The removed minimum-history floor means the earliest classified
  days have small, noisy reference pools.** The first classifiable day
  is ranked against a pool of exactly itself (trivially 100th
  percentile, landing in the high tercile by construction); the next
  few days are ranked against pools of 2, 3, 4 elements. This is an
  honest, inherent property of a purely causal expanding-window design,
  not a defect requiring a hand-picked cutoff — the reference pool
  strengthens naturally as Discovery progresses, and no arbitrary
  parameter was introduced to hide or truncate it. This was a
  deliberate choice, made explicitly with Jason, to avoid adding an
  unjustified free parameter rather than to avoid noise.
- **20-day lookback, tercile split, and 30-minute primary horizon are
  one frozen choice each, not the best of several tried.** No
  alternative lookback, quartile/quintile split, ATR-based volatility
  definition, or horizon was tested or will be tested under this
  hypothesis.
- **Tie-handling in the percentile rank** uses a simple, stated
  convention (fraction of the pool, including the day itself, at or
  below its own value) — not expected to matter in practice given
  continuous-valued volatility, but stated for completeness.

## Multiple-testing context

This is the tenth strategy-adjacent hypothesis and sixth
conditioning/characterization check run in this project, but the first
whose mechanism is not level-interaction. `purgedcv` (DSR/PBO) remains
unavailable in this environment (verified functional in an earlier
session on 2026-08-23, not currently installed) — flagged consistently,
as on every experiment to date. Not expected to matter here regardless,
since this is a characterization study with a pre-committed single
primary test, not a search across many trial configurations.

## Status

**Tested. Primary test result: NULL.** Run against the Discovery
slice on 2026-09-02. The 30-minute primary-horizon mean difference
between high- and low-volatility tercile days was +1.241 points, 90%
bootstrap CI [-0.252, +2.862] — spans zero. Step-2-gate checks 1
(statistically credible) and 2 (economically meaningful, >= 1.5 pts)
both failed, so per this spec's own rule the study stops there — the
remaining three gate conditions were not evaluated. No mechanical
rule was proposed or built. Full results, both robustness checks, and
the secondary-horizon table (reported descriptively only, per the
no-fishing rule above, despite one secondary horizon's CI happening
to exclude zero) are in
`research/experiments/exp-036-volatility-regime-post-open-behavior.md`.
No ledger entry, consistent with a null characterization result.

## History

- 2026-09-02: Phase 2 Research Direction Report delivered; Jason
  approved the volatility-regime direction and required the hypothesis
  tightened to one primary question/outcome.
- 2026-09-02 (same day): Frozen Study Specification drafted and
  presented for review before any code was written.
- 2026-09-02 (same day): Jason approved with one change (the
  minimum-history floor removed) and authorized implementation exactly
  as specified.
- 2026-09-02 (same day): Study implemented and run against Discovery
  data. Primary test came back null (CI spans zero, effect below the
  economic threshold). Both robustness checks reported as-is; neither
  rescues the primary result. Written up as
  `research/experiments/exp-036-volatility-regime-post-open-behavior.md`.
  No ledger entry, no mechanical rule proposed.
