# Fade the Gap

**Status: frozen definition, not yet tested** — drafted 2026-09-02, at
Claude's own initiative as research lead, per Jason's standing direction
("get us to the goal"), directly triggered by
`research/studies/overnight-gap-behavior.md`'s own Step 3 rule: its
Discovery-slice result (exp-032) found a gap-fill rate significantly
above 50% in both directions and a significant negative correlation
between gap size and the +90-minute forward return, which per that
document's own frozen rule requires defining and testing a concrete
mechanical rule rather than stopping at the characterization.

## Where this came from

This is the first setup in the project's history that is a direct,
mechanical translation of a specific quantitative finding rather than a
named chart pattern or a general market-structure concept applied
fresh. `research/studies/overnight-gap-behavior.md` (exp-032) found,
against the Discovery slice:

- Gap-up days filled back to the prior close by noon ET 58.4% of the
  time (n=784, 90% CI [55.5%, 61.4%]); gap-down days filled 58.1% of
  the time (n=556, 90% CI [54.7%, 61.5%]) — both above the 50%
  coin-flip baseline.
- Correlation(gap, forward return at +90 minutes) = -0.1408, 90% CI
  [-0.2142, -0.0595] — significant, and its sign says a larger gap
  tends to see some reversion by 90 minutes out.

Both findings point the same direction: gaps tend to partially close,
not extend. This setup tests the most direct possible trading
translation of that finding: **at the open, bet on the gap closing.**

**An important limitation this setup does NOT resolve, stated plainly
before any numbers are run:** the mechanical rule below is built from a
relationship discovered on the Discovery slice, and it will also be
FIRST tested on that same Discovery slice. A positive result here is a
necessary check (does the finding survive being turned into an actual
costed trade with realistic stops/targets?) but it is not independent
confirmation of anything — the same data produced both the hypothesis
and the test. Per this project's protocol, real confirmation of any
result requires the separate Validation slice, which is untouched by
this discovery process and which no setup in this project's history has
ever reached. If this setup clears the Discovery promotion bar, that is
the point to raise Validation-slice testing explicitly with Jason as a
deliberate, budgeted next step — not something to do automatically just
because Discovery looked good.

## Definition

### 1. Which days get a signal at all

Every day where `research/studies/overnight-gap-behavior.md`'s gap
computation produces a nonzero `gap` (today's 8:30 AM ET open vs. the
prior day's 4:00 PM ET reference close — see that document's own
honesty flag on why 4:00 PM ET is used for a near-24-hour-traded
instrument). A zero gap has nothing to fade and produces no signal for
that day. `prior_close` and `today_open` are computed by reusing
`study_overnight_gap.py`'s own `get_reference_close()` function and the
existing `OPEN_HOUR`/`OPEN_MINUTE` (8:30) convention from
`detect_ib_breakout.py` — not reimplemented here, so the two can never
silently drift apart.

### 2. Direction — literally "fade the gap"

- Gap **up** (`today_open > prior_close`): go **short** at the open,
  betting the gap closes downward.
- Gap **down** (`today_open < prior_close`): go **long** at the open,
  betting the gap closes upward.

### 3. Entry

The Open price of the first 1-minute bar at or after 8:30 AM ET — the
same "first bar of the session" convention every other setup in this
project uses for its reference open. No confirmation, no waiting for a
breakout or a reversal signal: this tests the gap-fill tendency itself,
at the earliest possible moment, exactly as characterized in the study.

### 4. Target — the gap-fill level itself, not a multiple

`target = prior_close`, literally the level the study measured "did it
fill" against. This is a deliberate, honesty-flagged departure from
every other setup in this project, which all use a fixed R-multiple
(1.35x risk) target. That convention doesn't fit here: the entire
premise being tested is "does price return to this specific level," not
"does price move some multiple of the initial risk." Using the
literature-defined level as the target keeps the test honest to the
actual finding instead of retrofitting the project's usual multiple
onto a different kind of claim.

### 5. Stop — symmetric, for a deliberate 1:1 risk:reward

`risk = abs(target - entry)` (the gap's magnitude). The stop is placed
the same distance on the opposite side of entry: for a short,
`stop = entry + risk`; for a long, `stop = entry - risk`. This makes
every trade exactly 1:1 R:R by construction — also a deliberate
departure from this project's usual 1.35R asymmetric target, made
necessary by the target being a fixed price level rather than a
risk-multiple. **Honesty flag:** a 1:1 setup needs a materially higher
win rate than an 0.74:1-risk / 1.35:1-reward setup (like every other
setup here) to be profitable after costs — roughly 50%+ costs, not the
~43% breakeven-ish threshold IB Breakout's asymmetry allowed. This is
flagged explicitly so a "close to 50%" win rate here is not
misread as being anywhere near as strong as the same win rate would be
under the project's usual 1.35R target.

### 6. Exit window — bounded at noon ET, matching the study's own watch window

Unlike every other setup in this project (which watch for a stop/target
hit through end-of-available-data), this trade's exit window is
explicitly bounded at 12:00 PM ET — the same cutoff
`overnight-gap-behavior.md`'s own Step 1 gap-fill measurement used. If
neither the stop nor the target is hit by noon, the trade is closed at
the last available bar's price before that cutoff (a timed exit, not
"ran out of data for the day" — the data continues, this setup simply
declines to hold past the window the underlying finding was measured
over). This keeps the backtest honest to the actual claim being tested
("does the gap close by noon," not "does the gap eventually close
sometime before the year 2030").

### 7. No lookahead

`prior_close` is fully known and frozen well before `today_open` even
occurs (4:00 PM ET the prior day vs. 8:30 AM ET today); the entry price
itself is the very first bar of the watched window, so there is no
information used in defining entry/stop/target that wasn't already
fully available at the moment of entry.

## Honesty flags — our own choices, not derived from any single source

- **Built directly from a Discovery-slice finding, first tested on that
  same Discovery slice.** Stated at the top of this document and
  repeated here because it is the single most important caveat: this is
  NOT an independent test. See "Where this came from" above.
- **1:1 R:R instead of this project's usual 1.35R target** — a
  necessary consequence of the target being a specific price level
  (the gap-fill point) rather than a risk multiple, not chosen to make
  the math easier. See Definition #5's honesty flag on what win rate
  this actually requires to be profitable after costs.
- **Noon exit cutoff** — chosen for internal consistency with the study
  that produced this setup, not because a gap that fills at 2 PM
  "doesn't count" in any absolute sense. A version of this setup with
  no time cutoff, or a different cutoff, would be a legitimately
  different test and is not what's being run here.
- **Every gap gets a signal, no magnitude threshold.** The frozen study
  deliberately avoided bucketing by gap size before checking the raw
  relationship (to avoid fishing for a threshold); this setup carries
  that same discipline forward — if a magnitude cutoff turns out to
  matter, that would be a distinct, separately-tested follow-up
  question, not folded into this first test.

## Multiple-testing context

This setup is the direct mechanical descendant of exp-032's 7-comparison
characterization (2 fill-rate groups + 5 horizons). Its own backtest
adds an 8th test built on the same underlying days, so any result here
should be read in that fuller context, not in isolation. `purgedcv`
remains unavailable for the formal DSR/PBO correction — flagged
consistently on every experiment in this project to date.

## Status

**Run, 2026-09-02, against real Discovery-slice data -- REJECTED,
statistically decisive.** Full numbers in
`research/experiments/exp-033-fade-the-gap.md`. 1340 raw signals (556
long, 784 short), 1061 resolved. Win rate 52.1% (CI 49.1%-55.1%) --
above 50%, consistent with the underlying gap-fill finding, but not
enough given this setup's forced 1:1 R:R (which needs comfortably more
than a bare majority to overcome costs, unlike this project's usual
1.35R-target setups). Expectancy -0.079R, 90% bootstrap CI -138.82R to
-28.75R, entirely below zero. This does NOT contradict exp-032's
characterization finding -- the gap-fill tendency is still real -- it
shows that this specific, honest translation of it into a costed trade
with a forced symmetric R:R doesn't survive intact. Logged as
`hyp-000012`, REJECTED.

A real data edge case (Sunday's continuous-trading bars only starting at
the ~6pm ET weekly reopen, mismatched against the "first bar at/after
8:30am" entry lookup) was found via a crash on the real run and fixed
with a new guard and unit test -- see exp-033 for the full explanation,
including confirmation that `overnight-gap-behavior.md`'s own exp-032
results are unaffected by the same issue.

## History

- 2026-09-02: this document written, at Claude's own initiative as
  research lead, directly triggered by exp-032's Step 3 rule being met.
- 2026-09-02 (later same session): run against the real Discovery
  slice (exp-033). REJECTED -- see Status above.
