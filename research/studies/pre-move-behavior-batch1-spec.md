# Pre-Move Behavior, Fresh Setups Batch 1 — Frozen Spec (exp-100/101)

## Why this, not more conditioning of old setups

Staff-meeting conclusion (2026-09-08): conditioning already-dead setups on
existing volatility facts (tried 4x: exp-077/086/087/093, all null) has a
low ceiling. Jason's direction: build detection + entry/exit FRESH around
a "something is about to happen" market behavior, instead of retrofitting
old signals. These are two new, mechanistically distinct setups, never
tested in this project before -- built the normal way (their own
detection logic, their own entry/stop/target), not overlays.

Both reuse this project's standard trade-mechanics: entry at signal bar's
close, stop/target derived from the setup's own logic, exit intraday via
`backtest.simulate_trade()` unmodified, `TARGET_R_MULTIPLE = 1.35`
(imported from `detect_level_sweep.py`, same constant every setup uses),
cost model `ROUND_TRIP_COST_POINTS` (unmodified).

## exp-100: Volume Vacuum Continuation

**Idea:** A short window of unusually thin 1-minute volume (few
participants, a fragile equilibrium) that then breaks its own range is a
different mechanism from anything tested so far (batch 1/2's rejection
wick and failed-breakout used PRICE range only, never volume). Thin
liquidity breaking should let price move with less opposing flow to
absorb it -- absence of resistance, not a chart shape.

**Detection (RTH 1-min bars, Discovery only):**
1. Rolling 20-bar average volume, `VACUUM_PCTL = 20` -- a bar is "thin"
   if its volume is below the 20th percentile of the trailing 60-bar
   volume distribution (`VACUUM_LOOKBACK_BARS = 60`).
2. A "vacuum window" = `VACUUM_WINDOW_BARS = 5` consecutive thin bars.
3. The vacuum window's high/low is its price range across those 5 bars.
4. Watch the next `VACUUM_WATCH_BARS = 15` bars for the first CLOSE
   beyond the vacuum window's high or low -- that's the signal (long if
   above, short if below). No signal if nothing breaks within the watch
   window.
5. Entry: breakout bar's close. Stop: opposite side of the vacuum
   window's range. Target: entry +/- 1.35R. Skip zero-width vacuum
   ranges (degenerate).

## exp-101: Multi-Timeframe Trend Alignment

**Idea:** Genuinely different mechanism from any prior batch --
confluence across timeframes, not a single-bar or single-day shape.
Never tested in this project.

**Detection (RTH bars, Discovery only), checked once per hour on the
hour (10:30, 11:30, 12:30, 13:30, 14:30 ET -- skips the first hour to
let all three timeframes have data):**
1. Fast: direction of the immediately-preceding closed 15-min bar
   (close vs open).
2. Medium: direction of the immediately-preceding closed 60-min bar
   (close vs open).
3. Day-so-far: sign of today's cumulative return from the day's open to
   the current checkpoint.
4. Signal fires only when all three agree (all up = long, all down =
   short). One signal per day maximum (first checkpoint where alignment
   fires; no re-entry same day).
5. Entry: next 1-min bar's open after the checkpoint. Stop: the
   checkpoint-preceding 15-min bar's opposite extreme (its low for a
   long, its high for a short). Target: entry +/- 1.35R. Skip
   zero-width stops.

## Method

Step 1 (statistical, no costs) AND Step 2 (costed, `ROUND_TRIP_COST_POINTS`
already baked into `simulate_trade`'s R-multiple convention used
elsewhere in this project) run together in one pass, same as every prior
setup detector -- these are full setups with real entry/stop/target, not
a bar-return proxy like the batch studies. Bootstrap mean-R-multiple CI,
N_BOOTSTRAP=3000, seed=7, 90% CI on `r_multiple_net`. Credible = CI
entirely above zero AND mean R-multiple net of cost is economically
meaningful (>= 0.05R average, this project's informal bar for "worth a
prospective test" on a per-trade R basis, consistent with the tiny
per-trade edges implied by this project's 1.35R-target, PROMISING-tier
results to date).

## Multiple-testing disclosure

2 pre-registered setups, one shared `search_batch_id`
(`batch-2026-09-08-pre-move-behavior-1`), run together. No follow-up
variants or threshold changes after seeing results.

## Decision rule / pre-commitment

Each setup evaluated independently against the standard promotion path:
a credible, economically-meaningful Step-1+2 PASS with n >= 40 gets its
own single pre-registered Validation-slice prospective test before any
promotion consideration (no different from every prior setup in this
project). A null result on either or both is not itself a reason to stop
this DIRECTION (fresh-behavior detection) -- Jason's explicit
instruction is to keep investigating this direction even if the first
trials don't work, so a null result here triggers designing the next 1-2
candidate behaviors in the same family, not a pivot away from it.
