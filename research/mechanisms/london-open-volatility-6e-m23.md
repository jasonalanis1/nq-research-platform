# Mechanism — London FX session-open volatility burst, 6E (M23, map channel, open scope)

Written: 2026-09-13, ~1:15 am CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO.
Source CHANNEL: map (forced participant), literature-supported: FX intraday
volatility is strongly periodic around the world's major trading-session
opens, and the London open (~08:00 GMT / ~03:00 ET) is the single largest
periodicity spike in EUR/USD -- documented since Andersen & Bollerslev
(1998, "Deutsche Mark-Dollar Volatility: Intraday Activity Patterns,
Macroeconomic Announcements, and Longer Run Dependencies", Journal of
Finance) and reconfirmed in later microstructure work (Ito & Hashimoto
2006; Breedon & Ranaldo 2013 on FX order flow around session opens).
London handles roughly 40% of global FX turnover and dealer desks there
open with a backlog: orders accumulated overnight in Asia, corporate/
custodial flow queued for the London fixing windows, and algorithmic
strategies keyed to the session boundary all execute in a short window at
the open.

## 1. Who is forced, and why
London-based bank and non-bank FX dealers are not scheduled by a news
release (unlike M21's ECB press conference) -- they are constrained by
the STRUCTURE of the global trading day itself: liquidity in EUR/USD is
thin through the Asian session (dominated by JPY/AUD pairs, not EUR), and
the moment London desks open, the backlog of overnight orders, corporate
flow, and session-triggered algorithmic strategies must clear against
whatever liquidity exists at that instant. This is a genuinely different
forcing mechanism from every other volatility-magnitude entry in this
project:
- M20 (EIA report) and M21 (ECB decision): forced by a SCHEDULED PUBLIC
  NEWS EVENT that changes fair value and requires repricing.
- M23 (this entry): forced by the STRUCTURE of the trading day itself --
  a liquidity/participation discontinuity at a fixed clock time, with no
  news content at all. The closest analogue in this project is M1 (NQ
  cash close) or M2 (NQ RTH open), both of which are session-boundary
  liquidity effects on NQ -- this is the same class of claim, applied to
  6E's own session structure for the first time. Not a resurrection of
  M20/M21 and explicitly NOT another instance of the "scheduled event ->
  volatility magnitude jump" pattern this project declined to clone a
  third time on 2026-09-12/13 -- there is no scheduled announcement here
  at all, public or private, on any calendar.

## 2. The claim
The one-hour window following the London FX session open (03:00-04:00
ET) shows realized |return|/ATR14 credibly ELEVATED relative to 6E's
unconditional hourly |return|/ATR14 baseline (magnitude claim, not
direction -- same design discipline as M20/M21, avoiding the direction-
ambiguity failure mode). Secondary, non-gating cell: the pre-London hour
(02:00-03:00 ET, tail of the Asian session) reported unpinned as a
specificity check -- if the whole overnight session is uniformly elevated
rather than concentrated at the open, that argues against a genuine
session-boundary effect and toward a broader overnight-volatility
explanation instead (a different, already-partially-explored territory
via the overnight-coil family).
Falsifiable in one sentence: if the London-open hour's |return|/ATR14 CI
does not clear the unconditional hourly baseline with a 90% lower bound
above it, the session-open effect is not visible in 6E futures at this
data ceiling.

## 3. Instrument-choice gate
6E is not the default vehicle here -- it is the mechanism itself, exactly
as ZN was the mechanism for M19/M22 and CL for M20: the claim is about
EUR/USD's own trading-session structure, so the signal and the trade are
both native to 6E. No cross-index comparison needed; standalone magnitude
claim against 6E's own unconditional baseline (two-nulls convention).

## 4. Footprint to measure
London-open hour (03:00-04:00 ET) |return|/ATR14 vs. the unconditional
hourly |return|/ATR14 baseline, built the same way as M20/M21 (every
valid hourly window across the full 24-hour session, ATR14 = trailing-14-
session mean of the RTH-equivalent 09:30-16:00 daily range, consistent
with M21's existing convention so the two are comparable). Block
bootstrap 90% CI (block=10, matching M21's convention for hourly cells).
No event-date list needed -- this fires every trading day, so n is large
(every Discovery-slice trading day, ~1,650 days), the best-powered entry
in the open-scope family so far.

## 5. Kill rule
If the response is concentrated in the single first minute of the London
session (03:00-03:01 ET, a stale-quote/thin-liquidity print artifact
rather than a genuine hour-long liquidity effect), the family terminates
as a print artifact, same standing rule as M19/M20/M21.

## 6. Resurrection check
Not M21 (ECB decision hour, 08:30-09:30 ET, forced by a scheduled news
release, not session structure -- different mechanism, different clock
time, no overlap). Not a third instance of the declined "scheduled
event -> volatility magnitude jump" clone pattern: there is no event,
public or private, calendar-anchored to 03:00 ET -- the forcing is
structural (session-boundary liquidity), the same class as M1/M2 (NQ
cash close / RTH open), never before tested on 6E. Not the overnight-coil
family (hyp-056/057): that is an NQ-only, next-session RANGE persistence
claim; this is a same-session, 6E-only, MAGNITUDE claim anchored to a
specific hour, no persistence/forecasting element at all.

## 7. Data needed
None. 6E 1-minute OHLCV is already on disk with full 24-hour coverage
(confirmed: data spans 00:00-23:59 local, covering Asian, London, and US
sessions). No new source, no new purchase.

## 8. Realization path
Time-based: the claim resolves entirely within a fixed one-hour window,
same day, no forward drift measured. Shortest possible horizon of any
entry sourced this cycle.

## 9. Product track
Directional/risk-execution: same open item as M20/M21 if this passes --
6E currently has zero base strategies to attach a sizing overlay to. But
unlike M20/M21 (news-driven, low daily frequency -- ECB meets ~8x/year,
EIA weekly), this fires EVERY trading day, which is a materially
different profile for eventual use: a daily-recurring session-open
liquidity window is closer to a "cash close" or "RTH open" type fact
(useful for execution timing, stop-width, or even a standalone breakout/
fade base strategy at the open, the same product shape as NQ's RTH-open
family) than a rare-event characterization with nothing to attach to.
This is flagged explicitly because it changes the Monetization
calculus from M20/M21's "no credible path" outcome -- if Discovery
passes, Monetization should evaluate whether the session-open window
itself could seed a simple, standalone 6E base strategy (e.g. an
opening-range breakout/fade AT the London open), not only search for a
pre-existing strategy to size, before concluding there is no path.

## Status
SOURCED, map channel, open scope. Mechanism doc written BEFORE any scan
per the upgrade-brief methodology. DRAWABLE once registered on the map
and in the Idea Inventory. No scan run yet.
