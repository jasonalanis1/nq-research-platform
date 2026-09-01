# Trend-Structure-Aware Liquidity Filter

**Status: frozen definition, not yet tested as of writing this file** --
drafted 2026-09-01 during an unattended overnight work session (Jason
asked Claude to push forward as far as safely possible without him
present), to give `docs/BACKLOG.md`'s "Trend-structure-aware liquidity
filter" idea (considered 2026-08-18) a precise, mechanically checkable
definition before any backtest is run -- same honesty standard as
`fvg-entry-trigger.md`. No detection code existed for this until this
session; see `src/trend_structure.py`.

## Where this came from

From `docs/BACKLOG.md`, sourced from a YouTube Short (ICT/Smart Money
Concepts style): the claim is that sweeping "interior" liquidity (a
swing high/low sitting inside an already-established trend) behaves
differently than sweeping the "protected high/low" -- the specific
structural point that, if broken, would flip the trend classification
itself. The former is framed as a normal stop-hunt-then-continuation;
the latter as a genuine reversal signal. This points at a real gap in
the current Level Sweep Reversal setup (`research/setups/level-sweep-reversal.md`):
it treats every prior-day/pre-market level sweep identically, with no
awareness of the broader trend context the level sits in.

`docs/BACKLOG.md` explicitly flagged the risk here: "swing high,"
"protected high," and "break of structure" have no single standard
definition, and programmatically defining them introduces new parameter
choices that are themselves an overfitting risk. This document exists
to make those choices explicit, defensible, and out in the open, not to
pretend they're the only possible reading.

## What this is NOT

This is not a new setup and does not change Level Sweep Reversal's
levels, watch window, sweep definition, confirmation modes, or
entry/stop/target rules in any way. It is a **post-hoc filter**: every
signal `detect_level_sweep.py` already finds gets classified into
exactly one of two buckets -- `protected` or `not_protected` -- based on
the trend context at the time it fired. Nothing about how a signal is
detected or how a trade would be managed changes.

## Definition

### 1. Trend structure is computed from DAILY bars, not 1-minute bars

The 1-minute price data is resampled to one row per trading day (daily
High = max of that day's 1-minute highs, daily Low = min of that day's
1-minute lows). Reasoning: the levels Level Sweep Reversal already
watches (previous day's high/low, today's pre-market high/low) are
themselves daily-level concepts, and "market structure" (higher-highs/
higher-lows vs. lower-highs/lower-lows) is conventionally read off daily
swings, not noisy intraday wiggles. This is our own choice, not
something the source video specified.

### 2. Swing points: a 2-day fractal (`SWING_FRACTAL_K = 2`)

A trading day D is a confirmed **swing high** if its daily High is
strictly greater than the daily High of each of the `SWING_FRACTAL_K`
trading days immediately before D **and** each of the
`SWING_FRACTAL_K` trading days immediately after D. A **swing low** is
the symmetric case on daily Low. `SWING_FRACTAL_K = 2` (a 5-day-wide
fractal) is a standard, simple, well-known choice -- the same window
used by the common "Williams Fractal" indicator -- picked for being
conventional and simple, not tuned against this project's data. It is
exactly the kind of knob `docs/BACKLOG.md` warned about and should be
sensitivity-tested later, the same way Level Sweep Reversal's three
confirmation-rule variants were compared side by side rather than
picked by guess.

### 3. No-lookahead confirmation lag (this matters -- read carefully)

A swing point at day D can only be confirmed once `SWING_FRACTAL_K`
trading days AFTER D have happened. If a Level Sweep Reversal signal
fires on day X, using a swing point that needed price data from day X
or later to confirm would be look-ahead bias -- classifying a trade
using information that didn't exist yet at the time of the trade. So:
when classifying a signal on day X, only swing points confirmed on or
before day X-1 are used (i.e., a swing at day D counts only if
`D + SWING_FRACTAL_K <= X - 1`). Swing points that technically exist in
the data but weren't yet confirmable as of day X are treated as unknown
for that signal's classification, exactly as they would have been in
real time.

### 4. Trend state as of day X

Using only swing points known per #3, take the two most recent known
swing highs and the two most recent known swing lows (in chronological
order):

- **UPTREND** if the latest known swing high is above the prior known
  swing high, AND the latest known swing low is above the prior known
  swing low (a higher-high/higher-low structure).
- **DOWNTREND** if the latest known swing high is below the prior known
  swing high, AND the latest known swing low is below the prior known
  swing low (lower-high/lower-low).
- **NO_TREND** otherwise -- this covers both a genuinely mixed structure
  (e.g. higher high but lower low) and the case where fewer than two
  confirmed swing highs and two confirmed swing lows exist yet (not
  enough history to classify).

### 5. The "protected" level as of day X

- In an **UPTREND**: the most recent known swing LOW -- the higher-low
  that, if broken, would end the higher-low sequence and invalidate the
  uptrend read. Call this `protected_low`.
- In a **DOWNTREND**: the most recent known swing HIGH, symmetric logic
  -- `protected_high`.
- In **NO_TREND**: no protected level exists for that day.

### 6. Classifying a signal as `protected` vs. `not_protected`

- A **long** signal (support was swept) is `protected` if, as of that
  signal's day, the trend is UPTREND **and** the level actually swept
  (`level_swept`, from `detect_level_sweep.compute_levels()`) is at or
  below `protected_low` -- i.e. the sweep reached at least as far as the
  point that defines the uptrend's structure, not a shallower interior
  pullback level. Everything else (DOWNTREND, NO_TREND, or an UPTREND
  where the swept level sits above `protected_low`) is `not_protected`.
- A **short** signal (resistance was swept) is `protected` if trend is
  DOWNTREND **and** `level_swept` is at or above `protected_high`.
  Everything else is `not_protected`.
- No tolerance/fuzz band is used -- an exact numeric comparison, since
  `level_swept` and the swing prices come from the same underlying
  1-minute series with no independent source of noise between them. If
  this turns out to be too brittle in practice, a small tolerance is a
  future knob to consider -- not introduced now without a concrete
  reason to believe it's needed.

## Honesty flags -- our own choices, not confirmed from any source

Per this project's standing rule against treating an assumed default as
if it were derived from evidence:

- **Daily bars, not intraday, for swing structure** -- our choice, for
  the reasons in #1, not something the source specified.
- **`SWING_FRACTAL_K = 2`** -- a conventional, simple choice, not tuned
  against this project's data. Worth sensitivity-testing (K=1, K=3, ...)
  later if this filter shows any promise at all.
- **Mixed-structure days classified as NO_TREND rather than "closest
  prior trend carried forward"** -- a simplifying choice. Carrying the
  prior trend forward through a consolidation is an equally defensible
  alternative reading that was not implemented here.
- **Exact-comparison, no tolerance band, for "at or beyond" the
  protected level** -- see #6. A reasonable alternative would allow the
  swept level to come within some small distance of the protected level
  and still count; not implemented here.
- **The source (a YouTube Short) never gave a precise, checkable
  definition of "protected high/low" at all** -- this document's
  definition is Claude's own operationalization of the general idea,
  not a translation of anything the source specified in checkable
  detail. Treat the source's claim as an unverified idea worth testing
  mechanically, not as evidence.

## Multiple-testing context (read before trusting any result)

This is now the fifth distinct hypothesis tested against the Level
Sweep Reversal base thesis (after `close_any`, `close_min_distance`,
`full_bar_range`, and the FVG entry trigger -- see
`research/experiments/_index.md`). `docs/RESEARCH_INTEGRITY_PROTOCOL.md`
specifically calls for Deflated Sharpe Ratio / Probability of Backtest
Overfitting analysis to correct for exactly this kind of accumulating
search -- trying enough variations on one underlying idea eventually
produces a positive-looking result by chance alone, even with no real
edge. `src/larry_validate.py` sketches how that check would work, but
**`purgedcv` is not installed on Jason's Mac as of this session, so that
correction cannot actually be run right now.** Any positive-looking
result from this filter should be read as more preliminary than usual
for that reason, not less -- this note exists so that caveat isn't lost
by the time anyone reads the result.

## Status

Frozen definition only as of first writing. Detection/classification
code: `src/trend_structure.py`. See `research/experiments/_index.md` for
whether and how this has since been tested.

## History

- 2026-08-18: idea logged to `docs/BACKLOG.md`, sourced from a YouTube
  Short (ICT/Smart Money Concepts style); flagged as pointing at a real
  gap but needing a precise, non-cherry-pickable definition, and as
  carrying real overfitting risk in how that definition gets made.
- 2026-09-01: this document written to give the idea that frozen,
  precise definition, during an unattended session (Jason's explicit
  go-ahead to push forward without him present, same spirit as the
  2026-08-15 precedent recorded in `docs/ROADMAP.md`).
