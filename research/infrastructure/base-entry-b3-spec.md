# B3 — the base entry (placeholder), frozen spec

Written: September 13th, ~7:15 pm CT, 7:00 pm test cycle. Bot milestone B3 per
`docs/BOT_ROADMAP.md`. Status: **SPEC FROZEN, not yet coded to this spec.**

## What this is, and what it is not

This is the ordinary, publicly-known entry rule the first bot runs so that the
order path (B4), execution measurement (B5), kill switches (B6) and the paper run
(B7) can exist and be measured. It is **not an edge and is never claimed as one.**
Every `Signal` it emits carries `validation_status="placeholder"`. Every session
report that mentions it names it as the placeholder. No report to Jason presents
its paper P&L as evidence of anything about the market.

**Honest expectation:** roughly break-even minus costs. Opening-range breakouts are
among the most widely published intraday patterns; on this project's own data the
initial-balance breakout family closed null (exp-028, exp-031, volume-confirmed
variant) and the earlier ORB placeholder was only ever run on synthetic data
(exp-001). There is no reason to expect this entry to make money on its own, and
the bot is not being built on the hope that it does.

**The real test** it exists to enable: *does the Risk/State Engine (B2) improve
this base's risk-adjusted behaviour versus the same base unconditioned?* That is a
comparison of two frozen configurations of the same entry — with the volatility
layer setting size/stop/target/permission, and without it — on the same sessions,
measured in the paper run. If the layer helps, that is the product; if it does not,
that is learned cheaply.

## The rule (frozen)

| Element | Definition |
|---|---|
| Instrument | MNQ (micro Nasdaq-100), one contract before sizing |
| Session clock | America/New_York. RTH open 09:30. |
| Opening range | High and low of all 1-minute bars 09:30:00–09:59:59 (30 minutes — the same window as the project's `opening_range_30m` state primitive) |
| Breakout window | 10:00:00–11:29:59 |
| Long trigger | First 1-minute bar in the breakout window whose **close** is above the opening-range high |
| Short trigger | First 1-minute bar in the breakout window whose **close** is below the opening-range low |
| One trade per day | Whichever trigger fires first; the other is ignored for the day |
| Entry price | Next bar's open after the trigger bar (never the trigger bar's close — you cannot fill on a close you have not seen) |
| Stop (unconditioned) | Opposite side of the opening range |
| Target (unconditioned) | Entry ± 1.0 × opening-range width |
| Stop / target (conditioned) | From B2: `stop_distance_atr` and `target_distance_atr`, in ATR14 points, replacing the unconditioned values |
| Size (conditioned) | From B2: `size_multiplier` × 1 contract, rounded down, minimum 1 |
| Permission (conditioned) | From B2: no entry when `trade_permission` is FALSE |
| Time exit | Flat by 15:55 ET if neither stop nor target hit |
| Costs | The project's standing cost model (`src/backtest.py`: commission + 1 tick slippage per side), then MEASURED once B5 exists |

Two configurations run side by side in paper, same sessions, same entry:
**BASE** (unconditioned stop/target, size 1, always permitted) and **BASE+B2**
(conditioned). The comparison metric is pre-registered here: net R per trade,
MAE, MFE, and max drawdown in R, over the minimum execution-validation sample
defined by the back half (never a calendar date). Nothing about the entry is
tuned to either configuration's results — the anti-optimization rule applies.

## Why this rule and not another

Well known, mechanical, fires most days (so execution measurement accumulates
quickly), needs no secret parameter, and — usefully — the 2026-09-13 Idea Factory
queue's strongest family is `opening_range_vs_atr → range/mfe/mae` (a wide first
30 minutes predicts a wider midday and larger excursions both ways, z ≈ 11). That
is a *size-of-move* fact about the same window, not a direction claim, and it is
exactly what B2 would exploit through stop/target distance. The placeholder and
the volatility layer are built around the same 30 minutes on purpose.

## What broke, found while writing this

Both legacy detectors on disk — `src/detect_setups.py` (the original ORB
placeholder) and `src/detect_ib_breakout.py` — open their window at **08:30 in
the data's own timezone**, and the data is stamped America/New_York. 08:30 ET is
pre-market; the RTH open is 09:30 ET. Whatever those scripts measured was a
pre-market range, not an opening range. exp-001 ran on synthetic data so nothing
was concluded from it; the initial-balance family (exp-028/031) closed null and
stays closed, but its window definition is now known to be wrong. Neither script
is reused for B3. This spec starts from the state primitive
(`opening_range_30m`, 09:30–10:00 ET), which was written later and is correct.

## Not decided here (and not to be decided by a cycle)

Broker (B4) — Tradovate paper first per the September 11th brief, spend
pre-approved. Live authorization (B8) — Jason only. Anything about which way to
trade — not this document's business.
