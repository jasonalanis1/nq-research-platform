# Volume-Confirmed Initial Balance Breakout

**Status: frozen definition, not yet tested** — drafted 2026-09-01, at
Claude's own initiative as research lead, per Jason's standing direction
to keep pushing toward the project's objective without waiting for
further instruction.

## Where this came from

Every hypothesis tested in this project so far — seven rejected
strategies plus the Open Return Persistence characterization study's
clean null — has used exactly one data dimension: **price**. But the
real Databento data on hand also carries genuine per-minute traded
volume (verified 2026-09-01: real, varying values, not a placeholder —
min 1, max ~424,000 contracts across a 200,000-row spot check, zero
all-zero rows). Nothing in this project has used it until now.

"Volume confirms a breakout" is one of the oldest, most established
heuristics in technical analysis (predates any of the ICT/Smart Money
Concepts sources behind this project's other setups by decades) — the
idea that a range breakout accompanied by unusually high participation
(volume) is more likely to represent real, informed conviction and
continue, while a breakout on thin volume is more likely to be noise
that fails. Initial Balance Breakout (exp-028) tested the unconditional
version of this bet and was rejected decisively (1654 trades, 90% CI
entirely below zero). This document tests whether volume confirmation
changes that picture — the same disciplined pattern already used once
this project (`research/setups/trend-structure-liquidity-filter.md`
tested whether trend context rescued the already-rejected reversal
thesis; it didn't, cleanly).

## What this is NOT

This does not change Initial Balance Breakout's range definition, entry,
stop, or target in any way (`research/setups/initial-balance-breakout.md`,
unchanged). It is a **post-hoc filter and characterization**, layered on
top of the exact same already-detected signals: every signal
`detect_ib_breakout.py` already finds gets an additional volume-context
reading, computed from data that already existed before the breakout
window even started (see #1 below — no lookahead).

## Definition

### 1. The volume baseline: this day's own Initial Balance average

For each signal, `ib_avg_volume` = the mean per-minute volume across
that same day's 8:30-9:00 AM Initial Balance window (added to
`detect_ib_breakout_for_day()`'s signal dict, 2026-09-01 — the
detection/entry logic itself is completely unchanged). Comparing each
breakout to **that same day's own** baseline, rather than a fixed
threshold or a baseline from other days, avoids two real problems: (a)
NQ's overall traded volume has grown substantially from 2015 to 2021
across the Discovery slice, so a single fixed volume threshold would
implicitly bias toward flagging later, higher-volume years as
"confirmed" regardless of that day's own character; (b) the IB window
closes at 9:00 AM, strictly before the breakout window (9:00 AM-noon)
even opens, so this baseline is fully known in advance — no future
information is used.

### 2. The signal: relative breakout volume

`rel_volume = breakout_volume / ib_avg_volume`, where `breakout_volume`
is the actual traded volume on the single 1-minute bar whose close
triggered the signal. `rel_volume > 1.0` means the breakout bar traded
more heavily than this day's own IB average; `rel_volume <= 1.0` means
it did not.

### 3. Step 1 — characterize first, before introducing any bucket

Per this project's own evolving practice (established in
`research/studies/open-return-persistence.md`): before splitting into
buckets with a chosen threshold — itself a parameter choice and
overfitting risk — first check the raw, continuous relationship.
Compute the Pearson correlation (with a 90% bootstrap CI, same
convention used throughout this project) between `rel_volume` and each
trade's realized outcome (`r_multiple_net`, from the exact same
backtest already run for exp-028 — entry/stop/target unchanged) across
all Discovery-slice IB Breakout signals. If this shows nothing, a bucket
split is very unlikely to show anything real either, and shouldn't be
constructed just to go looking for one.

### 4. Step 2 — a non-arbitrary bucket split, only if Step 1 warrants it

If (and only if) Step 1 finds a correlation whose 90% CI does not span
zero, split signals into two buckets at `rel_volume = 1.0` — "above this
day's own IB average" vs. "at or below it." This threshold is not a
tuned parameter: 1.0 is `rel_volume`'s own natural neutral point (equal
to the baseline), not a value chosen by looking at what split produces
the best-looking result. Each bucket then gets backtested separately
with `backtest.py`'s unmodified `simulate_trade()`, exactly the same
promotion-bar and significance standard as every other setup.

## Honesty flags — our own choices

- **Same-day IB-window average as the volume baseline**, rather than a
  trailing multi-day average at the same time of day (which would also
  control for intraday volume seasonality and might be a more
  conventional "relative volume" calculation in practice) — chosen here
  specifically to avoid both lookahead and cross-year drift with the
  simplest possible construction, not because it's necessarily the best
  possible baseline. A trailing-average version is a reasonable
  alternative worth testing later if this shows any promise.
- **rel_volume = 1.0 as the bucket boundary** — natural rather than
  arbitrary (see #4), but still just one of many possible ways to split
  a continuous variable into two groups; a different cut point (e.g. the
  observed median, or the 75th percentile as a stricter "confirmed"
  bar) is a reasonable alternative not used here.
- **Using the breakout bar's own single-minute volume**, not a short
  window around it (e.g. the average of the 3 bars including and
  following the breakout) — the simplest, most literal reading of
  "was THIS breakout accompanied by high volume," not necessarily the
  most robust to single-bar noise.

## Multiple-testing context

This is the ninth research artifact in this project (seven rejected
strategy hypotheses, one characterization study, now this) and, if Step
2 is reached, would be the eighth strategy-ledger entry. `purgedcv` is
still not installed on Jason's Mac, so the Deflated Sharpe Ratio /
Probability of Backtest Overfitting correction this project's protocol
calls for still cannot be run — any positive-looking result here should
be read with that same standing caveat as every prior setup.

## Status

**Tested, 2026-09-01, against real Discovery-slice data -- Step 1 null,
Step 2 correctly skipped.** Correlation(`rel_volume`, `r_multiple_net`)
across all 1654 resolved IB Breakout signals: -0.0229, 90% bootstrap CI
[-0.0645, +0.0190] -- spans zero, not significant. Per this doc's own
Step 2 rule, no bucket split was constructed since Step 1 gave no basis
for one. Full write-up: `research/experiments/exp-030-volume-confirmed-ib-breakout.md`,
which also flags a real limitation found after the fact: the same-day
IB-average baseline doesn't control for ordinary intraday volume
seasonality (rel_volume's median across all signals was 2.54, meaning
breakout-window volume is typically several times the IB average for
completely mundane reasons) -- a trailing same-time-of-day baseline
(already flagged as the alternative in the Honesty flags above, before
this result was seen) would be a more rigorous test before concluding
volume has nothing to add here.

## History

- 2026-09-01: this document written, at Claude's own initiative as
  research lead, after Jason reaffirmed the standing mandate to keep
  moving toward the project's objective, following the Open Return
  Persistence study's clean null and the discovery that the project's
  real data includes genuine, previously-unused per-minute volume.
- 2026-09-01 (later same session): tested against the real Discovery
  slice (exp-030). Step 1 (raw correlation) null; Step 2 (bucket split)
  correctly skipped per this doc's own rule. See Status above.
