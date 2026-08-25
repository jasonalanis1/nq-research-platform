# Fair Value Gap (FVG) Entry Trigger

**Status: frozen definition, not yet tested** — drafted 2026-08-24, at
Jason's request, to give the backlog's FVG idea a precise, mechanically
checkable definition before any backtest is run. No detection code
exists for this yet.

## Where this came from

From `docs/BACKLOG.md`'s "Fair Value Gap (FVG) lower-timeframe entry
trigger" item (considered 2026-08-18, sourced from a YouTube Short,
ICT/Smart Money Concepts style). Same core thesis as Level Sweep
Reversal (sweep a significant level, price fails to close beyond it,
reversal expected), but with a mechanically different entry trigger:
instead of "close back beyond the level" (the three variants already
tested in `level-sweep-reversal.md`), wait for a 3-candle Fair Value Gap
on a lower timeframe once the higher-timeframe rejection is confirmed.
The source claim ("catches 3.6R almost every day") was one cherry-picked
anecdotal example with no sample size or losing trades shown — not
evidence, and not weighted here. This document exists solely to remove
the ambiguity the backlog note flagged, same honesty standard as every
other setup doc in this folder.

## Definition

1. **Base setup: identical to Level Sweep Reversal, unchanged.** Reuses
   `research/setups/level-sweep-reversal.md`'s level selection
   (SUPPORT/RESISTANCE from yesterday's high/low + today's pre-market
   high/low), 90-minute watch window, sweep definition, and
   rejection/reversal confirmation exactly as-is — none of that logic is
   being retested here. The only thing this document changes is what
   happens AFTER rejection is confirmed.

2. **New entry trigger — 3-candle Fair Value Gap (FVG) on 1-minute
   bars**, replacing Level Sweep Reversal's "close back beyond the
   level" entry rule:
   - **Bullish FVG:** candle 1's high is below candle 3's low, leaving
     an untouched price zone between them.
   - **Bearish FVG:** candle 1's low is above candle 3's high (mirror
     image of the bullish case).
   - The gap is confirmed at candle 3's close — a partially-formed gap
     (only 1 or 2 candles in) doesn't count yet.

3. **Timing — when the FVG sequence is allowed to start and run:**
   - The rejection-confirming candle can never double as FVG candle 1.
     Candle 1 of the FVG sequence must be the first candle whose open
     time is at or after the rejection-confirming candle's close time.
   - Let `window_start` = the rejection-confirming candle's close time.
     The 30-minute window gates when candle 1 is allowed to **start**,
     not when the whole pattern must **finish**: candle 1's open time
     must satisfy the half-open interval
     `window_start <= open_time < window_start + 30min`.
   - Once a qualifying candle 1 begins inside that window, candles 2 and
     3 are allowed to complete the pattern even if that pushes slightly
     past the 30-minute mark — the window only constrains the start of
     the sequence, not its completion.
   - If no candle 1 opens inside `[window_start, window_start + 30min)`,
     no trade for the day under this variant.

4. **Which FVG, if multiple qualifying sequences form:** use the first
   one only (the earliest candle 1 that satisfies the window condition
   above and produces a valid gap at its candle 3). Any later FVGs are
   ignored.

5. **Entry:** at the close of candle 3 (the moment the FVG is
   confirmed) — no waiting for price to pull back into the gap itself.

6. **Stop / target: unchanged from Level Sweep Reversal.** Stop at the
   most extreme price reached during the sweep; target at
   `entry ± TARGET_R_MULTIPLE × risk` (currently 1.35 — same constant,
   same reasoning, as the base setup).

## What's genuinely new here vs. borrowed

Steps 1 and 6 are the existing, already-defined Level Sweep Reversal
logic, reused as-is — not re-derived or re-justified in this document.
Steps 2-5 (the FVG detection itself, the timing/window rule, first-gap-
only, and immediate-close entry) are the only additions here, and are
exactly what a future backtest of this variant would actually be
testing.

## Honesty flags — NOT confirmed from the source video

Per this project's standing rule against treating an assumed default as
if it were derived from evidence, the following choices above are OUR
OWN reasonable defaults, not anything stated or shown in the source
clip:

- **Timeframe (1-minute bars for the FVG check)** — the source didn't
  specify what "lower timeframe" meant; 1-minute was picked because
  it's the finest granularity this project's data already supports, not
  because the source used it.
- **30-minute window** to look for the FVG after rejection — an
  arbitrary, illustrative choice, in the same spirit as the base
  setup's `MIN_CONFIRM_DISTANCE_POINTS` placeholder, not something
  implied by the source. The half-open, start-gates-not-finish
  interpretation of that window is also our own mechanical choice, made
  precise here specifically so it's checkable in code — the source
  never addressed this level of detail at all.
- **"First gap only" rule** — the source never addressed what happens
  if multiple FVGs form in the window; picking the first is a
  simplifying default, not a confirmed rule.

All of these should be treated as parameters worth sensitivity-testing
later (the same way Level Sweep Reversal's three confirmation-rule
variants were compared side by side rather than picked by guess), not
as settled choices, if/when this setup is actually backtested.

## Status

Frozen definition only, as of 2026-08-24. No detection code has been
written (no `src/detect_fvg_entry.py` or equivalent exists yet). Per
`docs/RESEARCH_INTEGRITY_PROTOCOL.md`, any future backtest of this
variant would go through the same Discovery-slice-first pipeline as
everything else — no fast-tracking just because the underlying thesis
overlaps with an already-tested setup.

## History

- 2026-08-18: idea logged to `docs/BACKLOG.md`, sourced from a YouTube
  Short (ICT/Smart Money Concepts style); flagged as not evidence (one
  cherry-picked anecdotal example) and as requiring a precise,
  non-cherry-pickable definition before testing.
- 2026-08-24: this document written to give the idea that frozen,
  precise definition, at Jason's request. No detection code yet.
