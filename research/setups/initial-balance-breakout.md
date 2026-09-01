# Initial Balance Breakout (Continuation)

**Status: frozen definition, not yet tested** — drafted 2026-09-01, at
Jason's explicit direction, after the trend-structure liquidity filter
closed out the sixth straight test of the "sweep a level, expect a
reversal" thesis without clearing the promotion bar. Jason directed
Claude to act as research lead, pick the next area based on established
NQ/market-structure concepts rather than his own guess, explain the
reasoning, and proceed without waiting for further instruction — this
document, and the code that follows it, is that next step.

## Where this came from

Not sourced from a backlog item or a video clip — this is a deliberate
pivot in research *direction*, chosen by Claude as research lead per
Jason's instruction, and reasoned about explicitly here so the choice is
checkable rather than just asserted.

**Why a new direction, not another variant:** every hypothesis tested so
far — Level Sweep Reversal's three confirmation-mode variants
(`close_any`, `close_min_distance`, `full_bar_range`), the FVG entry
trigger, and the trend-structure liquidity filter — shares one
underlying bet: a significant level gets swept, and price reverses.
Six variants of that same thesis have now failed to clear the promotion
bar. Continuing to test more reversal variants (a different level
selection, a different confirmation rule, a different trend filter)
would be exactly the kind of "keep varying one idea until something
looks positive" search that `docs/RESEARCH_INTEGRITY_PROTOCOL.md` exists
to catch, even if each individual variant looks superficially novel.

**Why Initial Balance breakout specifically:** it is a genuinely
different underlying thesis — continuation, not reversal — so a
negative or positive result here says something new, not another point
on the same reversal curve. It is not a fringe idea: the "Initial
Balance" is a specific, decades-old concept from Market Profile /
Auction Market Theory (developed at the CBOT in the early 1980s by
J. Peter Steidlmayer), not a social-media pattern. The core claim: the
first stretch of trading after a session opens establishes a price
range (the Initial Balance), and what happens afterward tends to sort
into two broad regimes — the range holds and price reverts back into it
(a "range day"), or the range breaks and price actually continues in
that direction (a "trend day" / "range extension"). This project has
already tested for reversal-after-a-level; this tests for the opposite
and complementary case, continuation-after-a-range-break. It requires no
new data source (the same 1-minute NQ bars already on hand) and is tied
directly to this project's stated objective — robust, repeatable
behavior specifically around the NQ 8:30 AM New York open, since the
Initial Balance is by definition anchored to that exact moment.

## Relationship to the existing ORB placeholder — read this before testing

`research/setups/orb-placeholder.md` / `src/detect_setups.py` already
implement a superficially similar idea: a 15-minute opening range
(8:30-8:45), a 60-minute breakout window (8:45-9:45), first close beyond
either side triggers, stop at the opposite side, target one range-width
beyond entry. It was tested with real data at increasing sample size
(exp-004: 19 trades, exp-009: 125 trades, exp-013: 493 trades) and
killed decisively — exp-013 found -0.062R over 493 trades on 2 years of
real Databento data, only 6.6% of bootstrap simulations ending
profitable, logged as "settled... no further testing planned."

This is **not being treated as a clean slate.** It is the same broad
family (breakout continuation off an early-session range), and this
document's hypothesis counts as a direct descendant of that result for
multiple-testing purposes — see the section below. But it is not a
duplicate test, for reasons that matter mechanically, not just
rhetorically:

1. **Different, non-arbitrary range definition.** The old placeholder's
   own doc says plainly: "Parameters (15/60/1x) are arbitrary reasonable
   defaults, not tuned or validated against anything." This document's
   30-minute Initial Balance window is grounded in an actual named
   concept from market-structure literature, not a round number picked
   for convenience.
2. **Never tested under the current protocol.** Per `docs/ROADMAP.md`'s
   own "Bottom line" note, ORB was "already clearly negative before the
   holdout even mattered" — it was killed under the *old* methodology,
   tested against the full, chronologically-contaminated 2-year window,
   before `data_split.py`'s Discovery/Validation/Holdout Gen2 split
   existed. It was never specifically re-run against the Discovery slice
   the way `close_min_distance` and `full_bar_range` were in exp-023/024
   despite also having looked "stabilized" pre-protocol. This document's
   test will be the first Initial-Balance-family result produced under
   the current, more rigorous pipeline.
3. **Materially different breakout window.** 9:00 AM-12:00 PM here (a
   3-hour opportunity window) versus the old placeholder's 45-minute
   window (8:45-9:45) — a large enough difference that a breakout late
   in the morning the old definition would never see at all is a valid
   signal here.
4. **Different, standardized target.** This uses the project's existing
   1.35R target multiple (`TARGET_R_MULTIPLE`, same constant used by
   every Level Sweep Reversal variant and the FVG trigger) instead of
   the placeholder's ad hoc "one range-width" target, so this result is
   directly comparable to everything else in `_index.md` on the same R
   basis, which the old ORB rows never were.

If this comes back negative too, that will be read as *reinforcing*
exp-013's finding, not as an independent new data point — see the
Multiple-testing section.

## Definition

### 1. The Initial Balance window: 8:30-9:00 AM ET (30 minutes)

The high and low of price during the first 30 minutes after the 8:30 AM
NY open define the Initial Balance (IB) range for that day.
`IB_MINUTES = 30` was chosen because 30 minutes (two 30-minute Market
Profile "TPO periods") is the most common definition of the Initial
Balance in the source literature — not tuned against this project's
data. This is a genuinely different window from the old ORB
placeholder's 15 minutes, chosen for source-fidelity, not to produce a
different result.

### 2. Breakout window: 9:00 AM-12:00 PM ET

Starting immediately when the IB window ends, watch for the first
1-minute bar whose **close** is beyond either side of the IB range,
through 12:00 PM ET. No trade for the day if neither side breaks by
noon. `BREAKOUT_WINDOW_END = 12:00 PM` was Jason's own choice, covering
the entire NY morning session rather than an arbitrary short window —
distinct from (and much longer than) the old placeholder's 45-minute
watch.

### 3. First breakout only — no flip-flopping

The first 1-minute bar (in either direction) whose close breaks beyond
the IB range is the signal. If price later closes back the other way
too, that second break is ignored — only the first breakout of the day
is tradeable, matching how every other setup in this project treats "the
first qualifying event" (Level Sweep Reversal's first rejection, the
FVG trigger's first qualifying gap).

### 4. Entry, stop, target

- **Entry:** the close of the breakout bar (same immediate-close-price
  entry convention used throughout this project — no separate confirm
  bar, no waiting for a retest).
- **Direction:** long if the close breaks above the IB high, short if it
  breaks below the IB low.
- **Stop:** the opposite side of the Initial Balance range (IB low for a
  long, IB high for a short) — symmetric with how every other setup in
  this project defines its stop as "the level whose invalidation proves
  the trade wrong."
- **Target:** `entry ± TARGET_R_MULTIPLE × risk`, where
  `risk = |entry - stop|` and `TARGET_R_MULTIPLE = 1.35` — the exact
  same constant already used by every Level Sweep Reversal variant and
  the FVG entry trigger, reused unmodified so this result sits on the
  same R basis as everything else in `_index.md`, not a new target
  convention invented for this one setup.

### 5. Degenerate-range safeguard

If the Initial Balance range has zero width (IB high == IB low — no
price movement at all in the first 30 minutes, e.g. a data gap or a
halted session), no trade is generated for that day. This mirrors the
zero-risk-signal fix made to `detect_fvg_entry.py` for exp-025 (a
zero-width range would produce an undefined/zero risk trade, which is a
degenerate case to discard, not a real signal).

### 6. No look-ahead, by construction

Unlike the trend-structure liquidity filter, this setup needs no
explicit confirmation-lag mechanism: the IB range is fully known and
frozen the moment the 9:00 AM window closes, and the breakout scan only
ever looks forward from that point using data that has already
occurred. There is no future information that could leak backward into
an earlier decision.

## Honesty flags — our own choices, not derived from any single source

Per this project's standing rule against treating an assumed default as
if it were derived from evidence:

- **30-minute Initial Balance window** — the most common convention in
  the Market Profile literature, but the literature itself is not fully
  uniform (some practitioners use the first 60 minutes, or extend the IB
  to a third TPO period on a clear trend day). 30 minutes was picked as
  the standard baseline case, not the only defensible one — worth
  sensitivity-testing (e.g. 60 minutes) later if this shows any promise.
- **Breakout window ending at noon** — Jason's own choice; a defensible
  alternative would extend to the full session or use a shorter fixed
  window like the old ORB placeholder's 45 minutes.
- **First-breakout-only, no re-entry** — a simplifying choice consistent
  with how every other setup in this project treats "first qualifying
  event," not something Market Profile theory itself mandates. A trend
  day can, in principle, break out, fail, and break out again the other
  direction — this definition would miss that second move entirely.
- **1.35R target instead of a Market-Profile-native target** (e.g.
  "IB range projected as a measured move," which is closer to how the
  theory is traditionally applied) — chosen specifically so this result
  is comparable to every other setup already tested in this project, at
  the cost of not testing the theory's own native target convention.

## Multiple-testing context (read before trusting any result)

This is the seventh distinct hypothesis tested in this project overall,
and the first testing a *continuation* thesis rather than *reversal* —
see `research/experiments/_index.md` for the full list (`close_any`,
`close_min_distance`, `full_bar_range`, the FVG entry trigger, and the
two trend-structure-liquidity-filter variants, all reversal-thesis,
all REJECTED). It is directly related to — and should be read partly as
a follow-up test of — the already-killed ORB placeholder result
(exp-013: 493 trades, -0.062R, settled). `purgedcv` is still not
installed on Jason's Mac as of this session, so the Deflated Sharpe
Ratio / Probability of Backtest Overfitting correction
`docs/RESEARCH_INTEGRITY_PROTOCOL.md` calls for still cannot actually be
run — a positive-looking result here should be read as preliminary for
that reason, same caveat as every prior setup in this folder.

## Status

**Tested, 2026-09-01, against real Discovery-slice data -- REJECTED
(kill).** `src/_run_ib_breakout_discovery_backtest.py` ran the frozen
definition above against the full Discovery slice (2101 trading days),
after its performance-only day-grouping was verified byte-identical to
`detect_ib_breakout.py`'s own unmodified `scan_all_days()` on a 200-day
check slice. Result: 1654 resolved trades (long: 871, short: 838) --
the largest sample of any setup tested in this project so far --
expectancy -0.077R, 90% bootstrap CI -202.05R to -48.21R, **entirely
below zero**. Only 0.2% of bootstrap simulations ended net profitable.
Statistically decisive, comparable to the FVG entry trigger's exp-025
result as the project's most conclusive findings. Logged as
`hyp-000011` in the hypothesis ledger, full write-up in
`research/experiments/exp-028-initial-balance-breakout.md`.

This reinforces, rather than independently confirms, the project's
existing ORB placeholder finding (exp-013, 493 trades, -0.062R, killed
2026-08-16) -- two meaningfully different definitions of "trade the
breakout of an early-session range" have both now failed decisively.
The continuation thesis does not appear to have an edge as tested here.
No further Initial-Balance-family variants are planned without a
specific, concrete reason to expect a different definition would behave
differently.

## History

- 2026-09-01: this document written, at Jason's explicit direction to
  pick and justify the next research area without waiting for further
  instruction, after the trend-structure liquidity filter closed out
  the reversal thesis (0 for 6). Pivots to a continuation thesis
  (Initial Balance breakout), explicitly compared against the project's
  existing (and already-killed) ORB placeholder result above.
- 2026-09-01 (later same session): tested against the real Discovery
  slice (exp-028) -- REJECTED, statistically decisive on the largest
  sample of any setup tested so far. See Status above.
