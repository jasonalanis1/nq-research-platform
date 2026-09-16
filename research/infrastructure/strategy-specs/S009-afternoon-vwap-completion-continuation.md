# S009 — Afternoon VWAP-completion continuation

**Stage:** SPECIFY → FREEZE (this document is the authority; the module restates it).
**Frozen:** September 16th 2026, 3:00 pm CT cycle. Standing directive s.13 — not edited after the
FREEZE row in `research/ledger/strategies.jsonl`. A change is a FIX ONCE, never an edit.
**Module:** `src/strategy_s009_vwap_completion_continuation.py`
**Sourced under:** Amendment 1's top preference — an **intraday strategy that trades most days** —
from **market mechanics** (forced, price-insensitive flow into a clock), the shape that has worked
best in this project so far (S008).

---

## 1. The mechanism — who is forced, and why

The counterparty is **agency execution: institutional parent orders worked to a full-day VWAP or
percentage-of-volume benchmark**. This is the largest single category of institutional order flow in
US equity-index products, and it is the clearest forced flow available intraday because of three
properties, none of which is a price view:

1. **The quantity is fixed.** A parent order of N contracts (or the index basket equivalent) is
   handed to an algo in the morning. The algo does not get to decide it wants less because the price
   moved; its job is to complete N.
2. **The deadline is a clock, not a level.** A VWAP algo must be done by the cash close. Its
   schedule is a volume curve, and the US equity volume curve is heavily back-loaded — the last two
   hours carry far more of the day's volume than the middle of the day. So whatever quantity is
   still outstanding at the early afternoon is executed into the remaining hours *regardless of
   price*.
3. **Being behind the benchmark forces the algo to press, not to wait.** The algo is measured
   against the session VWAP. When price has drifted well away from the session VWAP by the early
   afternoon, the orders on the side the market has moved *away from* — buyers in a market that has
   risen above its VWAP, sellers in one that has fallen below it — are behind their benchmark with
   quantity left to do. Waiting is not a permitted strategy: the residual has to be worked, and
   working it pushes price further in the direction it has already gone.

That gives a **continuation** prediction, and it gives it in the one measurable quantity the
mechanism is actually defined on: **the distance of price from the session's own volume-weighted
average price**, not the day's directional move. Two days with the same open-to-early-afternoon move
can sit on opposite sides of their VWAP, and it is the VWAP distance — the benchmark gap — that
tells you how much execution is stranded on the wrong side.

The same closing clock binds the constant-leverage/NAV rebalancers that **S008** trades. That is a
real correlation and it is stated here rather than hidden: S008 and S009 both predict late-session
continuation, but they select trades on different quantities (S008 on |Close(15:00) − Open(09:30)|
against a trailing range; S009 on |Close(13:30) − VWAP(09:30–13:30)| against the same session's
range) and they enter at different times. If both ever hold KEEP, the Portfolio agent's question —
do they lose on the same days? — is the right one and it must be asked (directive s.4).

**This is not a resurrection.** It is not M2 / the IB-breakout or gap-fade families (both CLOSED;
no opening-range level is used, no breakout of any level is used). It is not H118 / hyp-000121-134,
whose claim was a *10-day drift* from a *trailing-ATR-normalised* VWAP distance in the LOW tercile
and whose direction is reversion toward VWAP; S009 is a same-session afternoon trade in the
*continuation* direction on the *session* VWAP. It is not `detect_vwap_reversion`'s 2-sigma
reversion, which is the opposite direction on the opposite side of the dislocation. It is not M16
(first-30 → last-30 momentum, clean null), which conditions on a return, not on a benchmark gap.

## 2. The trade, in full

Everything below is known at **13:30 ET** from that session's 09:30–13:30 bars only.

| Element | Rule |
|---|---|
| **Session window** | 09:30 ET through the 13:30 ET bar inclusive, RTH only. A session without a 09:30 bar, without a 13:30 bar, or with fewer than 220 bars in the window is skipped as a fragment. |
| **VWAP** | `sum(TP × Volume) / sum(Volume)` over that window, `TP = (High + Low + Close) / 3`. Zero total volume → no trade. |
| **RNG** | `High(09:30–13:30) − Low(09:30–13:30)`. Must be > 0. |
| **D** | `Close(13:30 bar) − VWAP`. |
| **Condition** | `|D| >= 0.30 × RNG` — price is dislocated from the session's own benchmark by at least 30% of the range it has traded in. |
| **Direction** | `sign(D)` — **continuation**, never a fade. |
| **Entry** | the **next bar's open** after the 13:30 ET bar. |
| **Stop** | `0.50 × RNG` against entry. |
| **Target** | entry ± `1.50 × risk` (1.5R). |
| **Time exit** | **15:55 ET**, same session. Flat before the cash close; no cross-session `exit_ts`. |
| **Sizing** | **1 micro MNQ, always.** No sizing rule beyond that; the stop already scales with the session's own range, which is where the validated magnitude facts enter (s.3). |

**No look-ahead.** VWAP, RNG and D are computed from bars at or before 13:30. The only bar read
after the decision is the next bar's open, which *is* the fill price by construction. The trailing
state used by the SLOW arithmetic is built from strictly earlier sessions. The scan never moves
backwards.

## 3. Where the validated magnitude facts enter

The project owns three validated magnitude facts (VXN level → next-session range; quiet midday →
expanded afternoon; wide opening 30 min → wider midday). They are **stop/sizing inputs**, not
signals, and they enter here structurally: **the risk unit is the session's own realised range**
(`0.50 × RNG`), so the trade is automatically wider on days those facts predict to be wide and
tighter on days they predict to be quiet. That is the lever that makes a fixed dollar cost small:

- median RNG on qualifying sessions (measured, magnitude only, pre-freeze): **67.2 index points**
- median risk `0.50 × RNG`: **33.6 index points**
- MNQ market cost 1.300 pt = **0.039R**. The cost is ~4% of one unit of risk.

A separate "only on large-range days" filter was measured and **rejected**: adding `RNG >= trailing-20
median RNG` cuts the fire rate from 0.3567 to 0.2072 per session (26.1 projected six-month trades),
which would make S009 **SLOW** and defeat the reason it was sourced. The range conditioning is kept
in the risk unit, where it costs no trades.

## 4. Costs — all four combinations (`src/cost_model.py`, ASSUMED, s.11)

| combination | round trip $ | round trip POINTS | as a fraction of the 33.6-pt median risk |
|---|---|---|---|
| **MNQ market entry+exit — THE DECISION BASIS** | **$2.60** | **1.300 pt** | 0.039R |
| MNQ limit entry (**OPTIMISTIC UPPER BOUND**) | $2.10 | 1.050 pt | 0.031R |
| NQ market entry+exit | $14.90 | 0.745 pt | 0.022R |
| NQ limit entry (**OPTIMISTIC UPPER BOUND**) | $9.90 | 0.495 pt | 0.015R |

Every limit figure is an **OPTIMISTIC UPPER BOUND**: a resting limit order is assumed always to fill
at its price, when real ones miss fills and are adversely selected. A historical screen cannot model
a non-fill. Slippage is **ASSUMED** (1 tick/side at market) until B4b measures it.

## 5. The pre-freeze edge-vs-cost check (Amendment 2 / `cost_model.specify_gate`)

Jason's rule: **at SPECIFY, reject only if the expected per-trade edge is below the per-trade cost
itself.** There is no multiple of cost, no budget, no "well north of". Stated before any outcome was
looked at:

- geometry: 1.5R target against a 1R stop → **breakeven hit rate 40.0%**
- median risk R = **33.6 pt** (measured magnitude, no P&L read)
- expected per-trade edge in points = `(2.5p − 1) × 33.6`, p = the share of trades that reach 1.5R first
- **the gate fails only if p ≤ 0.4155** — i.e. only if the forced-completion flow is worth less than
  1.6 percentage points of hit rate over a coin-flip-at-breakeven trade
- the mechanism's own prior — a modest continuation tilt from the stranded execution, taken here as
  **p = 0.45**, five points above breakeven — gives an expected edge of **+4.20 pt/trade**

**+4.20 pt vs 1.300 / 1.050 / 0.745 / 0.495 pt → the gate PASSES in all four combinations → SCREEN.**
p = 0.45 is an assumption, and it is the assumption the screen exists to test; what the gate settles
is only that the trade is not structurally too small to pay for itself, and at 0.039R of cost per
trade it plainly is not.

## 6. Where this should fail — the Salvage menu for S009

Named now, at SPECIFY, so a later Salvage check cannot be a search for a flattering slice
(directive s.7; the Integrity Gate rejects menu-only conditions invented after the fact):

1. **Low-volatility / narrow-range sessions.** When RNG is small the dislocation is small in points
   and the fixed cost is a larger fraction of it. Menu condition 1 (VXN vs trailing) and 2 (range).
2. **Range-bound, two-sided days.** A day that has oscillated puts price far from VWAP without any
   stranded one-sided execution; the gap is noise, not a benchmark gap. Menu condition 2.
3. **Scheduled-news days.** On CPI/NFP/FOMC days the 09:30–13:30 VWAP is dominated by a single
   release print, and the 13:30–15:55 window is driven by the news, not by execution schedules.
   FOMC in particular has its 14:00 statement inside the holding window. Menu condition 4.
4. **The last hour specifically.** If the mechanism is real the flow should be concentrated late; if
   the strategy's result comes entirely from the 13:30–14:30 leg it is not this mechanism.
   Menu condition 3.
5. **Days where price crosses back through VWAP quickly.** A fast re-cross says the gap was not
   stranded execution at all. Mechanism-named condition.

## 7. Disclosures

- Paper runs through the B7 loop, which applies the Risk/State Engine's session gate; the screen
  does not. Stated in every spec.
- The screen's bookkeeping is the paper loop's: first touch wins, a stop wins a same-bar tie, time
  exit from `market_context["time_exit"]`, session-end fallback, fill at `signal.entry`.
- One trade per session, the first (and here only) signal of the session.
- Discovery slice only. Validation and Holdout are not touched.
