# Mechanism — intraday periodicity: same half-hour slot, next day (M17, literature)

Written: 2026-09-12, ~4:40 pm CT (TEST cycle, sourcing toward the shelf
floor)  ·  PRE-REGISTERED. Results seen before writing: NO.
Source CHANNEL: literature. Heston, Korajczyk and Sadka (2010), "Intraday
Patterns in the Cross-section of Stock Returns," Journal of Finance 65(4):
a stock's return in a given half-hour interval predicts its return in the
SAME half-hour interval on subsequent days, at daily lags out to ~40 days,
with the effect strongest at the open and close. Attributed to
institutional order execution scheduled at the same clock time each day
(fund flows, VWAP/TWAP program schedules, daily rebalances). Documented in
the cross-section; the index-level version is weaker and is exactly what
this entry tests.

## 1. The claim
For NQ, the sign-adjusted return in half-hour slot k on day t+1, given the
return in slot k on day t, is credibly positive for the OPEN slot
(09:30-10:00) and the CLOSE slot (15:30-16:00) -- the two slots where
scheduled institutional execution concentrates. Falsifiable in one
sentence: if the slot-k(t) -> slot-k(t+1) sign-adjusted mean has a
block-bootstrap 90% CI including zero in BOTH the open and close slots on
Discovery, the periodicity is not present at index level and the entry
closes.

## 2. Who is on the other side
Institutions executing on a SCHEDULE: a fund that must buy a fixed share
of daily volume in the first or last half hour (creation/redemption, NAV
matching, end-of-day rebalance) trades the same direction at the same time
on consecutive days while its program runs. The constraint is the
schedule, not a view; the footprint is same-slot sign persistence across
days. Intermediaries take the other side and are paid for it in the slot.

## 3. Testable predictions (gating marked)
P1 (GATING): sign-adjusted slot return at t+1 given slot return at t is
  credibly positive in the OPEN slot OR the CLOSE slot (block bootstrap,
  block 10 sessions, 90% CI excluding zero). Reported with NULL 1: the
  unconditional mean of that slot's return (open slot and close slot each
  carry their own drift).
P2 (reported): the effect is specific to those two slots -- the same
  statistic on the MIDDAY slot (12:00-12:30) is not credibly positive.
  If midday shows it as strongly, it is generic autocorrelation, not
  scheduled execution.
P3 (reported): decay -- Discovery first half vs second half. Published
  2010; Discovery starts 2015; the base case is decayed.
P4 (reported): dose -- conditioning on the day-t slot return being in its
  top/bottom tercile (by |ret|/ATR) vs the middle. Persistence should be
  stronger after larger day-t slot moves if the mechanism is a running
  program.

## 4. What would falsify this
(a) P1 fails in both slots: no index-level periodicity. Closes.
(b) P1 passes but P2 shows midday equally strong: generic daily
    autocorrelation of intraday returns, not a scheduled-flow footprint;
    recorded "confounded", closes.
(c) KILL RULE: if more than half of the slot-(t+1) response sits in its
    first one-minute bar, the persistence is an auction-print artifact;
    family terminates.
(d) Roll-Friday sessions lacking RTH are dropped and counted.

## 5. Resurrection ruling (LEARN + Integrity)
By name and by what is measured:
- M16 intraday momentum (Entry 20, drawable): SAME-day first-30 -> last-30.
  This is CROSS-day, same slot. Different predictor timing, different
  outcome window; both can be true or false independently. Not a
  resurrection; the two share a participant class (close-scheduled flow)
  and that is disclosed.
- M1 / hyp-000110 closing pressure (CLOSED FOR GOOD): close-window move ->
  NEXT MORNING open. This is close slot -> next day's CLOSE slot. Different
  outcome window. Not a resurrection.
- IB / opening-range breakout family (closed): range break, held all day.
  Not a return-persistence claim across days. Not a resurrection.
- Candlestick/bar-pattern family (closed): no.
- Rejected calendar effects (day-of-week etc.): this conditions on the
  prior day's slot return, not on the calendar. Not a resurrection.
- Overnight/gap families: predictor and outcome are both inside RTH
  slots. Not a resurrection.
RULING: NEW. Enters. Attempt 1 of 2. Integrity signs at sourcing.

## 6. Instrument-choice gate
1. Leads: the index carrying the most schedule-driven ETF/fund flow --
   ES/SPY in the paper's world; NQ/QQQ carries the same flow classes.
2. Minutes not milliseconds: the flow is a 30-minute execution schedule,
   not a race. Kill rule guards the print.
3. NQ is an adequate vehicle; not instrument-ordered like M13.
4. Directional NQ, sign-adjusted. Not relative.
5. NULL 1: each slot's own unconditional drift is reported beside the
   gating cell (the close slot in particular has its own drift).

## 7. Frozen scope (for the scan)
ONE scan, Discovery only. Slots: OPEN 09:30-10:00, MIDDAY 12:00-12:30,
CLOSE 15:30-16:00; slot return = close(last bar) - open(first bar) / ATR14
(lagged). Predictor = slot k return on day t; outcome = slot k return on
day t+1, sign-adjusted by the predictor's sign. Cells to register:
  1. OPEN slot sign-adjusted next-day mean, block CI   <- GATING (P1)
  2. CLOSE slot sign-adjusted next-day mean, block CI  <- GATING (P1)
  3. MIDDAY slot, same statistic (P2, reported)
  4-5. OPEN and CLOSE unconditional slot means (NULL 1, reported)
  6-7. cells 1-2 on Discovery halves (P3, reported, 4 cells)
  8-9. cells 1-2 split by day-t |slot ret| tercile (P4, reported, 6 cells)
  10. share of the day-(t+1) response in its first 1-min bar, both slots
      (kill rule, 2 cells)
17 cells, 2 gating (Sidak at 2). Product track: DIRECTIONAL alpha.
Realization: TIME-BASED, 30-minute hold in the slot on day t+1 in the
direction of day t's slot. Monetization pre-check: the sign-adjusted slot
premium must clear 2x round-trip cost. Data: NQ on disk. DRAWABLE.

## 8. Ranking (information gain x edge potential)
Information gain: MODERATE. Tells us whether scheduled institutional
execution leaves an index-level footprint we can see in 1-minute bars --
the same class of participant the M13/M14/M16 entries lean on; a clean
null here is evidence for the structural conclusion (scheduled flow is
fully competed in NQ) from a fourth angle. P2 is the interesting cell
either way.
Edge potential: LOW-MODERATE. A 30-minute hold on a small persistence;
the paper's effect is strongest in the cross-section, and 2010 is old.
Base case is decayed. It is cheap, fully specified, and nothing to tune.

## 9. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. P4 -- untested.
