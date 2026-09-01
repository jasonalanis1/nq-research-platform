# Overnight Gap Behavior Study

**Type: CHARACTERIZATION STUDY, not a strategy.** No entry, stop, or
target unless Step 2 below is reached; no ledger hypothesis entry
unless a specific mechanical rule is actually backtested.

**Status: frozen definition, not yet run** — drafted 2026-09-01, at
Claude's own initiative as research lead, continuing per Jason's
standing direction ("get us to the goal") after three straight
conditioning checks on Initial Balance Breakout's trades (price
persistence, volume, day-of-week) all came back null.

## Where this came from

Everything tested in this project so far — seven rejected strategies
and three conditioning checks — has looked at behavior INSIDE the
regular session, starting no earlier than the 8:30 AM open itself. None
of it has asked about the jump BETWEEN sessions: the "overnight gap,"
one of the most widely referenced, independently well-established
phenomena in index/futures trading (distinct from anything in this
project's prior video-sourced ideas) — the empirical tendency for a
price gap between one session's close and the next session's open to
partially or fully "fill" (retrace back to the prior close) during the
new session, and the related question of whether the gap's own size and
direction says anything about what the day does next. This is
genuinely new ground, not another cut of the same already-three-times-
rejected Initial Balance Breakout trade set.

## Definition

### 1. A necessary honesty flag before anything else: what counts as "the prior close"

NQ futures trade nearly 24 hours a day (this project's own real data
spans 00:00-23:59 ET with no universal daily gap), so there is no
naturally occurring "market closed" boundary the way there is for
equities. This study adopts the standard convention used across
financial media and most index-futures gap analysis: **4:00 PM ET**,
the NYSE cash-equity close, as the reference "prior close" time, even
though NQ itself keeps trading afterward. This is a deliberate,
literature-standard choice, not one invented for this project — but it
is still a choice, and a different one (e.g. the settlement time CME
itself uses, or literally the last bar of the prior calendar day) would
define a different, also-defensible "gap."

`prior_close` = the Close of the last available 1-minute bar at or
before 4:00 PM ET on the trading day immediately preceding the day in
question (using whatever bar the data actually has at/near that time,
same "last available bar" convention already used elsewhere in this
project, e.g. `detect_ib_breakout.py`'s IB-window handling).

### 2. The gap itself

`today_open` = the Open of the first bar at or after 8:30 AM ET (the
same open-of-session convention every other setup in this project
already uses). `gap = today_open - prior_close`. A day is excluded if
either `prior_close` or `today_open` can't be determined (missing data
around either reference point).

### 3. Step 1 — gap-fill rate (a plain descriptive statistic, no threshold)

For each day with a nonzero gap, does price touch back to `prior_close`
at any point from 8:30 AM through 12:00 PM ET (the same morning-session
window this project has used throughout, e.g. Initial Balance
Breakout's own breakout window)? Reported separately for gap-up days
and gap-down days, with a plain fraction and count — no bucket
threshold on gap SIZE at this step, since a size-based bucket is itself
a parameter choice best deferred until the raw relationship is checked
first (per this project's now-established practice from the Open Return
Persistence study).

### 4. Step 2 — does the gap predict forward returns? (reusing the persistence-study methodology exactly)

Pearson correlation (with a 90% bootstrap CI, 2,000 resamples — same
convention throughout this project) between `gap` and the forward
return from `today_open` at the same five horizons already used in
`research/studies/open-return-persistence.md`: +30, +60, +90, +120, and
+180 minutes. This asks, in the same rigorous no-threshold way as that
study: does the SIZE and DIRECTION of the overnight jump say anything
about what the day does next, independent of the gap-fill question in
Step 3.

### 5. Step 3 — only if Step 1 or Step 2 shows something real

If the gap-fill rate is decisively lopsided (e.g. materially different
from a coin flip with a tight confidence interval) or a horizon
correlation's CI excludes zero, define a specific, mechanical
"fade-the-gap" or "gap-fill" trading rule (entry, stop, target) and test
it fresh against the Discovery slice through this project's full
pipeline, exactly like every other setup — not fast-tracked just because
the underlying characterization looked promising.

## Honesty flags

- **4:00 PM ET as "the prior close"** — see #1. Standard, but a choice,
  not the only defensible one for a near-24h-traded instrument.
- **Gap-fill window through noon ET**, matching this project's other
  morning-session conventions, rather than through end-of-day (a gap
  could still fill later in the session, just outside this study's
  window) — chosen for consistency with everything else tested here,
  not because afternoon fills don't count as "real" fills.
- **No gap-magnitude bucketing in Step 1** — a small gap (a few points,
  likely just overnight noise) and a large gap (a real news-driven jump)
  probably don't behave the same way, but splitting by magnitude before
  checking the raw relationship would be exactly the kind of
  fishing-for-a-threshold this project's rules exist to catch. Left for
  a Step 3 mechanical-rule definition if Steps 1/2 show enough to
  justify building one.

## Multiple-testing context

Step 1 (2 groups: gap-up, gap-down) plus Step 2 (5 horizons) is 7
separate comparisons on the same underlying days. Per this project's
established practice, all results are reported regardless of outcome —
no result gets suppressed for looking uninteresting, and no single
"significant-looking" result among 7 should be read as strong evidence
on its own without that context. `purgedcv` remains unavailable for the
formal DSR/PBO correction.

## Status

**Run, 2026-09-01, against real Discovery-slice data -- the first
result in this project that ISN'T a clean null, and Step 3 is
triggered.** Full numbers in
`research/experiments/exp-032-overnight-gap-behavior-study.md`. Headline
findings:

- **Step 1 (gap-fill rate):** gap-up days filled by noon 58.4% of the
  time (n=784, 90% CI [55.5%, 61.4%]); gap-down days filled 58.1% of the
  time (n=556, 90% CI [54.7%, 61.5%]). Both CIs sit entirely above 50%
  -- statistically distinguishable from a coin flip, on a well-powered
  sample.
- **Step 2 (correlation with forward returns):** four of five horizons
  were not significant, but the +90 minute horizon showed correlation
  -0.1408, 90% CI [-0.2142, -0.0595] -- SIGNIFICANT, and its sign is
  consistent with the fill-rate finding (a larger gap tends to see some
  reversion by 90 minutes out, not further extension).

**Per this document's own Step 3 rule** ("if the gap-fill rate is
decisively lopsided... or a horizon correlation's CI excludes zero,
define a specific mechanical rule and test it fresh"), that trigger is
met. A frozen mechanical rule (`research/setups/fade-the-gap.md`) has
been defined and is being tested as a follow-up
(`research/experiments/exp-033-fade-the-gap.md`) -- see that setup doc
for an important caveat this study's own result doesn't resolve on its
own: a rule built directly from a finding computed on the Discovery
slice, then backtested on that same Discovery slice, is not independent
confirmation, only a check that the finding survives being turned into
an actual costed trade. Real confirmation, if this clears the Discovery
promotion bar, would require this project's own Validation-slice step
-- something no setup in this project has reached yet.

## History

- 2026-09-01: this document written, at Claude's own initiative as
  research lead, continuing per Jason's standing direction after three
  straight conditioning checks on Initial Balance Breakout's trades
  (price persistence, volume, day-of-week) all came back null.
- 2026-09-01 (later same session): run against the real Discovery
  slice (exp-032). Gap-fill rate significantly above 50% in both
  directions; +90min correlation significant. Step 3 triggered -- see
  Status above and `research/setups/fade-the-gap.md`.
