# S010 — Thin-participation afternoon completion continuation

**Stage:** SPECIFY → FREEZE (this document is the authority; the module restates it).
**Frozen:** September 16th 2026, 5:00 pm CT cycle. Standing directive s.13 — not edited after the
FREEZE row in `research/ledger/strategies.jsonl`. A change is a FIX ONCE, never an edit.
**Module:** `src/strategy_s010_thin_participation_completion.py`
**Sourced under:** Amendment 1's top preference — an **intraday strategy that trades most days** —
from **market mechanics** (forced, price-insensitive flow into a clock), the shape that has worked
best in this project so far (S008).

---

## 1. The mechanism — who is forced, and why

The forced counterparty is the one S008 and S009 already name: **benchmark- and close-referenced
institutional execution** — VWAP/POV parent orders, index and NAV-referenced funds, constant-leverage
rebalancers. Its two defining properties are unchanged: **the quantity is fixed** in the morning and
the algo does not get to want less, and **the deadline is a clock** (the cash close), not a level.

What is new here is the **denominator**. S008 selects days by how far price has already moved; S009
selected them by the benchmark gap. Both are numerator variables — how much pressure. **S010 selects
on how much liquidity that pressure has to be pushed through.** Market impact is a function of order
size *relative to available volume* — the square-root law, `impact ≈ σ·√(Q/ADV)` — so the same
unfinished residual moves price further on a thin day than on a busy one.

A session whose cumulative 09:30–14:00 volume is **below its own trailing-20-session norm** is a
session where participation did not show up. The completion residual is not smaller for that: the
parent orders were sized in the morning against an expected day, and the deadline did not move. The
last two hours therefore have to absorb an unchanged quantity into a thinner book, and the price
impact of completing it is mechanically larger.

The **direction** that residual presses is the direction the session has already gone, for S009's
reason: the side price has moved *away from* is the side that is behind its benchmark with quantity
left to do, and being behind forces an algo to press rather than to wait. So **thin participation
selects the day, the day's own move gives the sign, and the trade is continuation into the close.**

**The correlation with S008 is real and is stated here rather than hidden.** Both predict late-session
continuation and both take `sign(day's move)` as the direction. They differ in the variable that
selects the day (S008: `|Close(15:00) − Open(09:30)|` against a trailing *range*; S010: 09:30–14:00
*volume* against its trailing median — a quantity that is not a price at all), and in the entry clock
(15:00 vs 14:00). If both ever hold KEEP, the Portfolio agent's question — do they lose money on the
same days? — is the right one and it must be asked (directive s.4). It is expected that they will
overlap on some days; the screen and the paper record are the place that shows how much.

**This is not a resurrection.** It is not hyp-000152 (volume-conditioned daily *reversal*, CLOSED):
that tested the **next day's** return, graded by **daily** volume, in the **reversion** direction; this
is a same-session afternoon trade in the **continuation** direction selected by an **intraday**
volume deficit. It is not hyp-000043 (volume level alone). It is not M2 / the IB-breakout or gap-fade
families (no opening-range level, no breakout of any level, no gap). It is not S007 (opening-range
break continuation, KILLED). It is not H118 / hyp-000121-134 (a 10-day drift on a trailing-ATR-
normalised VWAP distance). It is not S009 (the 13:30 session-VWAP gap), whose one salvage is spent.

## 2. The trade, in full

Everything below is known at **14:00 ET** from that session's 09:30–14:00 bars and from **strictly
earlier** sessions.

| Element | Rule |
|---|---|
| **Session window** | 09:30 ET through the 14:00 ET bar inclusive, RTH only. A session without a 09:30 bar, without a 14:00 bar, or with fewer than 250 bars in the window is skipped as a fragment. |
| **VOL** | `sum(Volume, 09:30–14:00)`. Must be > 0. |
| **TRAILING** | the **median VOL of the previous 20 sessions**, strictly earlier, shifted by one so a session never sees itself. No 20-session history → no trade. |
| **RNG** | `High(09:30–14:00) − Low(09:30–14:00)`. Must be > 0. |
| **M** | `Close(14:00 bar) − Open(09:30 bar)`. |
| **Condition** | `VOL <= 1.00 × TRAILING` — a participation deficit — **and** `M ≠ 0`. |
| **Direction** | `sign(M)` — **continuation**, never a fade. |
| **Entry** | the **next bar's open** after the 14:00 ET bar. |
| **Stop** | `0.50 × RNG` against entry. |
| **Target** | entry ± `1.50 × risk` (1.5R). |
| **Time exit** | **15:55 ET**, same session. Flat before the cash close; no cross-session `exit_ts`. |
| **Sizing** | **1 micro MNQ, always.** No sizing rule beyond that; the stop already scales with the session's own range. |

**No look-ahead.** VOL, RNG and M are computed from bars at or before 14:00; TRAILING is built from
strictly earlier sessions (`rolling(20).median().shift(1)`); the only bar read after the decision is
the next bar's open, which *is* the fill price by construction. The scan never moves backwards.

**The threshold is the median, not a tail.** `1.00 × TRAILING` is chosen so the strategy fires on
roughly half the sessions — the Amendment 1 requirement that it trade often enough for the six-week
clock to mean something. It is not tuned: the median is the one non-arbitrary point on the
distribution, and no other fraction was measured.

## 3. Where the validated magnitude facts enter

The project's three validated magnitude facts (VXN level → next-session range; quiet midday →
expanded afternoon; wide opening 30 min → wider midday) are **stop/sizing inputs**, not signals, and
they enter structurally: **the risk unit is the session's own realised range** (`0.50 × RNG`), so the
trade is automatically wider on days those facts predict to be wide. The second fact is directly
relevant here — a quiet midday predicts an expanded afternoon, and a thin-participation day is a
quiet-midday day by construction — which is a reason to expect the afternoon leg to carry range, not
a second filter, and it is not used as one.

Measured pre-freeze on the Discovery slice, **magnitude only, no outcome read**:

- qualifying sessions: **801 of 2,101** (fire rate **0.3812 per session**)
- median RNG on qualifying sessions: **51.75 index points**
- median risk `0.50 × RNG`: **25.875 index points**
- MNQ market cost 1.300 pt = **0.050R**. The cost is ~5% of one unit of risk.

**SLOW projection (Amendment 1), stated before the screen:** `0.381247 × 126 = 48.04` projected
six-month trades against the 40 required → **NOT SLOW**. That is why this candidate was sourced this
cycle: S008 is the only strategy on a live six-week clock, and the six-week answer needs more than
one strategy that trades often enough to reach 40 trades. The screen's own rate is the number of
record and is recorded on the PAPER row.

## 4. Costs — all four combinations (`src/cost_model.py`, ASSUMED, s.11)

| combination | round trip $ | round trip POINTS | as a fraction of the 25.875-pt median risk |
|---|---|---|---|
| **MNQ market entry+exit — THE DECISION BASIS** | **$2.60** | **1.300 pt** | 0.050R |
| MNQ limit entry (**OPTIMISTIC UPPER BOUND**) | $2.10 | 1.050 pt | 0.041R |
| NQ market entry+exit | $14.90 | 0.745 pt | 0.029R |
| NQ limit entry (**OPTIMISTIC UPPER BOUND**) | $9.90 | 0.495 pt | 0.019R |

Every limit figure is an **OPTIMISTIC UPPER BOUND**: a resting limit order is assumed always to fill
at its price, when real ones miss fills and are adversely selected. A historical screen cannot model
a non-fill. Slippage is **ASSUMED** (1 tick/side at market) until B4b measures it.

## 5. The pre-freeze edge-vs-cost check (Amendment 2 / `cost_model.specify_gate`)

Jason's rule: **at SPECIFY, reject only if the expected per-trade edge is below the per-trade cost
itself.** No multiple, no budget, no "well north of". Stated in the units the screen will report,
before any outcome was looked at:

- geometry: 1.5R target against a 1R stop → **breakeven hit rate 40.0%**
- median risk R = **25.875 pt** (measured magnitude, no P&L read)
- expected per-trade edge in points = `(2.5p − 1) × 25.875`, p = the share of trades that reach 1.5R first
- **the gate fails only if p ≤ 0.4201** (MNQ market) — i.e. only if thin-book completion pressure is
  worth less than **2.01 percentage points** of hit rate over a breakeven coin flip.
  The same threshold is 0.4162 on MNQ limit, 0.4115 on NQ market, 0.4077 on NQ limit.
- the mechanism's own prior — a modest continuation tilt from the stranded residual, amplified by the
  thin book — taken here as **p = 0.45**, five points above breakeven, gives an expected edge of
  **+3.23 pt/trade**

**+3.23 pt vs 1.300 / 1.050 / 0.745 / 0.495 pt → the gate PASSES in all four combinations → SCREEN.**
p = 0.45 is an assumption and it is the assumption the screen exists to test; what the gate settles is
only that the trade is not structurally too small to pay for itself, and at 0.050R of cost per trade
it plainly is not. **The stated falsifier is `p ≤ 0.4201`.**

## 6. Where this should fail — the Salvage menu for S010

Named now, at SPECIFY, so a later Salvage check cannot be a search for a flattering slice
(directive s.7; the Integrity Gate rejects conditions invented after the fact):

1. **High-volatility sessions.** A thin day inside a high-VXN regime is thin because participants are
   standing aside from risk, not because the day is calm; the residual then meets a book that is thin
   *and* jumpy, and the stop is hit before the completion pressure pays. Menu condition 1.
2. **Range-bound, two-sided days.** If the 09:30–14:00 move is small and oscillating, `sign(M)` is
   noise and there is no side that is systematically behind its benchmark. Menu condition 2.
3. **Scheduled-news days.** On CPI/NFP/FOMC days volume is *not* thin for the usual reason, and the
   afternoon is driven by the release, not by execution schedules; FOMC's 14:00 statement lands
   exactly on the decision bar. Menu condition 4.
4. **The first half hour after entry specifically.** If the mechanism is real the flow should build
   into the close; a result that comes entirely from the 14:00–14:30 leg is not this mechanism.
   Menu condition 3.
5. **Half-days and holiday-adjacent sessions.** Volume is thin for a calendar reason and the
   completion residual is thin with it, so the mechanism's premise (unchanged quantity, thinner book)
   is false. Mechanism-named condition.
6. **Days where the participation deficit is marginal.** If the result lives only in the deepest
   part of the deficit (`VOL` far below TRAILING) and not in the half of qualifying days nearest the
   median, the median threshold is carrying the strategy rather than the mechanism.
   Mechanism-named condition.

## 7. Disclosures

- Paper runs through the B7 loop, which applies the Risk/State Engine's session gate; the screen
  does not. Stated in every spec.
- The screen's bookkeeping is the paper loop's: first touch wins, a stop wins a same-bar tie, time
  exit from `market_context["time_exit"]`, session-end fallback, fill at `signal.entry`.
- One trade per session, the first (and here only) signal of the session.
- Discovery slice only. Validation and Holdout are not touched.
- Volume is Databento's 1-minute bar volume for the front NQ contract as loaded by
  `src/data_loader.py`. On roll days the front contract changes and the measured volume is the new
  front month's; that is the same convention every other study in this project uses and it is not
  corrected for here.
