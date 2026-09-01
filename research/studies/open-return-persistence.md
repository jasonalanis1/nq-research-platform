# Open Return Persistence Study

**Type: CHARACTERIZATION STUDY, not a strategy.** No entry, stop, or
target; no trades; no ledger hypothesis entry (`research_ledger.py`'s
schema is for strategy backtests with a `trade_count`/`expectancy_r`,
which this isn't). This is a direct, model-free question asked of the
data, distinct from every setup in `research/setups/`.

**Status: frozen definition, not yet run** — drafted 2026-09-01, at
Claude's own initiative as research lead, per Jason's direction to keep
moving without waiting for further instruction.

## Where this came from

Seven straight hypotheses have now been tested and rejected: three Level
Sweep Reversal confirmation variants, the FVG entry trigger, two
trend-structure-liquidity-filter variants (all reversal-thesis), and the
Initial Balance Breakout (continuation-thesis) — the latter on the
largest, most statistically decisive sample of any setup tested so far
(exp-028, 1654 trades, 90% CI entirely below zero). Both broad families
of "sweep/break a level, then something predictable happens" have now
failed.

Inventing an eighth named chart pattern next — another ICT/SMC-style
idea, another confirmation-rule variant — would risk exactly the kind
of search this project's integrity rules exist to catch, with
diminishing information value: each new pattern is one more roll of the
dice, not a step toward understanding *why* the prior seven failed.

**The more useful question at this point isn't "does pattern #8 work,"
it's "does the early open carry any predictive information about what
follows, in any form, at any time horizon — independent of any specific
chart pattern someone happened to name?"** This is a standard, textbook
market-microstructure question (serial correlation / autocorrelation of
returns, momentum vs. mean-reversion), more foundational than any of the
seven named patterns tested so far, and it answers Jason's stated
objective directly rather than through the proxy of one more specific
rule: "determine whether there are robust, repeatable behaviors around
the NQ 8:30 AM New York open." Whatever this finds is useful either way
— a real correlation at some horizon says exactly where to build the
next mechanical setup from evidence; a null result across all horizons
is itself a strong, well-powered finding that argues for looking outside
pure intraday price-action (volume, calendar/macro conditioning) rather
than continuing to guess at chart patterns.

## Definition

### 1. The reference window: the Initial Balance, reused unchanged

Uses the exact same 8:30-9:00 AM ET Initial Balance window already
frozen in `research/setups/initial-balance-breakout.md`
(`OPEN_HOUR`/`OPEN_MINUTE`/`IB_MINUTES`, imported directly from
`detect_ib_breakout.py`, not redefined) — not a new, separately-chosen
window. This keeps this study directly comparable to exp-028 rather than
introducing a fresh, unjustified parameter.

### 2. The predictor: the IB's own directional return

For each day with a non-empty IB window:
`ib_return = (close of the last IB bar) - (open of the first IB bar)`.
No minimum-move threshold, no chart pattern, no breakout requirement —
just the raw signed price change during the IB window. Positive means
price net rose during the IB; negative means it net fell. A day where
`ib_return == 0` exactly is `NO_TREND` for this purpose and still
included (raw persistence is being measured, not a directional bet).

### 3. The outcome: forward returns at five fixed horizons

Measured from the moment the IB window ends (9:00 AM):
`fwd_return_Hm = (close of the last bar within H minutes after 9:00 AM) - ib_close`,
for `H` in `{30, 60, 90, 120, 180}` minutes. 180 minutes lands at
12:00 PM ET — deliberately the same breakout-window end used by
`initial-balance-breakout.md`, so these horizons span the same morning
session already established as the project's window of interest, not an
arbitrarily longer or shorter one.

### 4. What gets measured, per horizon

- **Pearson correlation** between `ib_return` and `fwd_return_Hm` across
  all valid days, with a bootstrap 90% confidence interval on that
  correlation (same resampling convention `confidence_analysis.py`
  already uses elsewhere in this project — reshuffle-with-replacement,
  2,000 resamples).
- **Conditional means**: average `fwd_return_Hm` on days where
  `ib_return > 0` vs. days where `ib_return < 0`, with the same
  bootstrap approach applied to the difference between the two groups,
  so a positive correlation reads as "continuation" (IB up → later
  prices tend to be higher) and a negative correlation reads as
  "reversal" (IB up → later prices tend to be lower) — the same two
  theses already tested via specific chart patterns, now checked
  directly and without any pattern-specific machinery in the way.
- Reported in raw NQ points (no risk/R-multiple conversion — there's no
  stop or entry rule here to normalize against), alongside plain sample
  counts so the reader can judge how much data backs each horizon.

## Honesty flags — our own choices

- **The IB window as the fixed "early move" reference**, rather than,
  say, the first 5 or 15 minutes — chosen for direct comparability with
  the already-frozen Initial Balance definition, not because 30 minutes
  is definitionally the "right" early-move window. Worth
  sensitivity-testing at other window lengths later if this shows
  anything at all.
- **Five specific horizons (30/60/90/120/180 min)** rather than a
  continuous horizon sweep — a reasonable, evenly-spaced set spanning
  the same morning session already established as this project's window
  of interest, not an exhaustive search. Testing every possible horizon
  and reporting only the significant ones would itself be a
  multiple-testing problem; reporting all five regardless of outcome is
  the safeguard against that here.
- **No minimum-move / no-trade threshold on `ib_return`** — every valid
  day is included, even a nearly-flat IB. A stricter definition (e.g.
  "only count days where the IB moved at least N points") is a
  reasonable alternative not used here, since the goal is measuring the
  data's raw behavior, not the profitability of a specific trade rule.

## Multiple-testing context

This is explicitly NOT hypothesis #8 in the strategy-ledger sense — it
produces no trades and gets no `hyp-` entry. But the five horizons
tested here are still five separate statistical tests run on the same
data, and should be read with that in mind: one nominally "significant"
correlation among five, with no adjustment for testing five, is weaker
evidence than the same result would be as a single pre-registered test.
If any horizon here does show a real relationship, the natural next
step — building an actual mechanical setup around it and testing that
setup fresh against the Discovery slice — would itself be the real
test of whether the effect holds up as a tradeable rule, not this study
alone.

## Status

**Run, 2026-09-01, against real Discovery-slice data -- clean null
result across all five horizons.** `src/study_open_return_persistence.py`
ran (via a temporary, verified performance-only driver, deleted after
use) against 1715 usable Discovery-slice days. At every horizon --
+30, +60, +90, +120, and +180 minutes after the Initial Balance ends --
the correlation between the IB's own return and the forward return was
close to zero (range: -0.036 to +0.072) with a 90% bootstrap CI spanning
zero in every case, and the conditional-mean difference (average forward
return after an IB-up day minus after an IB-down day) was likewise not
significant at any horizon. Full numbers in
`research/experiments/exp-029-open-return-persistence-study.md`.

**Read plainly: on this data, in this window, the Initial Balance's own
direction carries no detectable linear relationship to what happens in
the following 30 minutes to 3 hours** -- not a weak continuation signal,
not a weak reversal signal, just noise, on a well-powered sample
(~1,686-1,713 days per horizon). This is a second, more fundamental line
of evidence pointing the same direction as the seven rejected strategy
hypotheses: it isn't only that seven specific chart-pattern
implementations failed to find an edge, it's that the raw, unconditional
data doesn't show one either, at least not in this linear,
single-predictor form. See `docs/ROADMAP.md`'s 2026-09-01 entry for what
this suggests about where to look next.

## History

- 2026-09-01: this document written, at Claude's own initiative as
  research lead, after seven straight strategy hypotheses (spanning both
  the reversal and continuation theses) failed to clear the promotion
  bar, per Jason's standing direction to keep moving without waiting for
  further instruction.
- 2026-09-01 (later same session): run against the real Discovery slice.
  Clean null result at all five horizons -- see Status above.
