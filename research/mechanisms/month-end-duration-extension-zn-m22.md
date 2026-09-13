# Mechanism — Month-end index duration-extension flow, ZN (M22, map channel, open scope)

Written: 2026-09-13, ~9:15 pm CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO.
Source CHANNEL: map (forced participant), with literature support: bond
index providers (Bloomberg US Aggregate / Bloomberg US Treasury Index and
predecessors) rebalance their published index composition once a month
(month-end, effective the following month), incorporating new Treasury
issuance. New issuance is usually longer-dated on net, so the index's
duration typically LENGTHENS at month-end. Funds and separate accounts
benchmarked to the index (index funds, and active managers who must not
drift too far from tracking error) must extend their own portfolio
duration to match, and the fastest, cheapest way to do that in size is
Treasury futures (buying longer-dated contracts / rolling exposure
longer), concentrated in the last 1-2 sessions of the month. This flow is
widely discussed in fixed-income practitioner literature (e.g., dealer
"index extension" estimates published monthly by Barclays/Bloomberg index
teams) and is mechanically distinct from equity-side month-end
rebalancing.

## 1. Who is forced, and why
Index-tracking bond funds and index-benchmarked separate accounts are
constrained by their mandate to track the published index's duration
within a tolerance; they do not choose whether to extend, only when and
how, and month-end is calendar-fixed by the index provider's own
rebalancing schedule. This is a genuinely different participant from:
- M19 (auction concession): primary dealers, obliged to bid at
  scheduled auctions, driven by inventory/balance-sheet risk around a
  specific auction date.
- M5 (month-end NQ-vs-ZN relative performance, CLOSED, clean null):
  pension/balanced (60/40-style) mandates rebalancing EQUITY vs. BOND
  weights against each other; the claim there was about NQ's cross-asset
  return relative to ZN. This claim is entirely INSIDE ZN -- it says
  nothing about NQ and does not use NQ's return as either signal or
  outcome.
- M1 (cash close MOC): equity index funds/ETFs executing the closing
  auction; different instrument, different participant, daily not
  monthly.

## 2. The claim
Over the LAST 2 RTH sessions of each calendar month, ZN's close-to-close
return / ATR14 is credibly POSITIVE relative to ZN's unconditional
2-session drift (NULL 1) -- i.e., ZN price is systematically bid up as
duration-extension buying concentrates into month-end. A conditioning
split by months where net Treasury issuance data (from TreasuryDirect,
already on disk from M19) shows the auction calendar added net long-dated
supply that month vs. months that didn't (a rough proxy for "index
duration actually lengthened this month") is the secondary, non-gating
cell -- flagged in advance as low-power (small n once split) and
descriptive only, not a second gate.
Falsifiable in one sentence: if the last-2-session ZN return, net of its
own unconditional 2-session drift, does not clear a 90% block-bootstrap
CI excluding zero, the flow is not visible in ZN futures at this data
ceiling and the entry closes.

## 3. Instrument-choice gate
ZN is not just the default vehicle here -- it is the mechanism itself: the
flow IS the extension buying in Treasury futures (funds transact in
futures precisely because it is the fastest, most liquid way to adjust
duration without touching the cash bond portfolio). No cross-index
comparison is needed; this is a standalone directional claim in ZN,
against ZN's own baseline (NULL 1), consistent with the project's
two-nulls convention for a single-instrument directional claim.

## 4. Footprint to measure
Last-2-RTH-session close-to-close return / ATR14 in ZN, anchored on the
last trading day of each calendar month (NYSE holiday calendar already on
disk), compared to ZN's unconditional 2-session-window drift computed the
same way as M19's and M5's pooled baseline (every valid 2-session window
in the Discovery slice). Block-bootstrap 90% CI (block=5, consistent with
M19) is the CI of record.

## 5. Kill rule
If the response is concentrated in the single last trading day's final
bar (a settlement-price/marking artifact rather than a multi-session flow
building in), the family terminates as a print artifact per the
project's standing first/last-minute concentration rule -- computed as
the share of the 2-session move attributable to the final RTH minute of
the month, same convention as M19/M20/M21's kill checks.

## 6. Resurrection check
Not the auction-concession claim (M19, closed -- different participant,
different calendar anchor, auction date vs. calendar month-end). Not M5
(cross-asset NQ-vs-ZN, closed -- different instrument pairing and
different claim entirely: this is unconditional-in-ZN, not relative
performance). Not turn-of-month (hyp-000108, closed -- that was an NQ
equity-flow claim, first-3-sessions-of-month, different instrument and
different window: LAST 2 sessions BEFORE month-end here, not the first
sessions after). Genuinely distinct claim, distinct participant, distinct
instrument-internal mechanism.

## 7. Data needed
None beyond what is already on disk: ZN 1-minute OHLCV (already loaded
for M19), NYSE holiday/trading-calendar (already in use project-wide).
No new purchase, no new source.

## 8. Realization path
Time-based: enter at the RTH close 2 sessions before month-end, exit at
month-end close. No stop/target ambiguity (matches the exit-design
question required before freezing any monetization spec, per the
upgrade-brief methodology).

## 9. Product track
Directional, single-instrument (ZN). If Discovery passes and it survives
Statistical/Director/Monetization, it would need a ZN base strategy or a
sizing overlay decision exactly like M20/M21's open item -- flagged in
advance so this does not surprise Monetization later: ZN currently has no
existing base strategy either (same gap as CL/6E), so even a Discovery
pass here would likely end at NO CREDIBLE PATH unless a very simple
"trade the flow itself, flat by month-end" base strategy is judged
sufficient as its own monetization vehicle (a real possibility, since the
realization path above is already flat/time-boxed and does not require
attaching to a separate pre-existing strategy the way a volatility-only
magnitude fact does).

## Status
SOURCED, map channel, open scope. Mechanism doc written BEFORE any scan
per the upgrade-brief methodology. DRAWABLE once registered on the map
and in the Idea Inventory. No scan run yet.

## 10. Disposition (2026-09-13, ~3:20 am CT, scheduled cycle)
Scan 027 run, Discovery slice only (82 calendar month-ends, 2015-01
through 2021-10). Result:
  - GATING cell (last-2-RTH-session ZN return/ATR14, net of ZN's own
    unconditional 2-session drift): n=82, mean=+0.1022,
    ci_90=(-0.1210,+0.2630) -- does NOT credibly clear zero (the CI
    straddles it, though the point estimate is positive and in the
    predicted direction).
  - Kill check: final-minute share=0.096 (well under the 0.5 threshold)
    -- NOT concentrated in a settlement-price artifact.
  - Secondary issuance-direction split: OMITTED. The only issuance file
    on disk (data/treasury_auctions_notes_2015_2021.csv, used by Scan
    024/M19) has 10-year note auction DATES only, no issuance SIZE and
    no other maturity terms -- there is no way to classify "months where
    the auction calendar added net long-dated supply" from what is
    actually on disk without inventing a proxy the doc did not specify.
    Per the standing rule against fabricating data when a real source
    cannot be found, this cell was skipped rather than approximated
    (same precedent as Scan 024's own omitted bid-to-cover cell). The
    doc marked this cell non-gating and low-power in advance, so the
    entry's verdict does not depend on it.
VERDICT: P1_FAIL. Per Section 2's own falsifier: "if the last-2-session
ZN return, net of its own unconditional 2-session drift, does not clear
a 90% block-bootstrap CI excluding zero, the flow is not visible in ZN
futures at this data ceiling and the entry closes." Entry CLOSED.
Logged: hyp-000153 (REJECTED), ledger data_slice=discovery.
THIN-SAMPLE CAVEAT (flagged in the doc from the outset): n=82 month-ends
is a small sample for a monthly-frequency test, comparable to M19's
n=40 auction events. The point estimate is positive and economically
plausible in size, but the confidence interval is wide enough that this
null does not rule out a real, smaller effect than the CI's power can
detect -- it only says the flow is not visible at this data ceiling,
the same framing already applied to M19's closure.
Next owed: none for M22 -- CLOSED.
