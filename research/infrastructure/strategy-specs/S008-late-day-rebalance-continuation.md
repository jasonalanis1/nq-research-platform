# S008 — Late-day constant-leverage rebalance continuation

**Status: FROZEN September 16th, 2026.** Module `src/strategy_s008_late_day_rebalance_continuation.py`.
Both files' sha256 are in `research/ledger/strategies.jsonl` at the FREEZE row, written before any
outcome data was touched. Standing directive s.13: neither file is edited after that row. A change is a
FIX ONCE, never an edit.

## 0. Why this candidate is being reopened — an input error, not a salvage

S008 was specified earlier on September 16th and sent to **LEARN without a screen**. It was refused at a
"cost budget" this project invented, which required a gross per-trade edge of **3× the assumed cost**,
where the assumed cost was **$6.00 per micro round trip = 3.00 index points**.

**Both halves of that refusal were wrong.**

1. The $6.00 figure charged a **full-size E-mini (NQ) commission** ($2.50/side) to a **micro (MNQ)**
   contract. The corrected MNQ round trip is **$2.60 = 1.30 index points** at market entry and exit
   (`src/cost_model.py`, sources cited there; write-up
   `research/infrastructure/cost-model-2026-09-16.md`).
2. The **"3× cost" pre-screen was Tony's own invention.** The standing directive has never contained it.
   Jason deleted it in Amendment 2 and replaced it with: *at SPECIFY, reject only if the expected
   per-trade edge is below the corrected per-trade cost itself; otherwise screen it.*

The specified cell's measured gross edge is **+2.55 points per trade** (n = 708, t = 2.11). That is above
**every one of the four corrected costs** — 1.300 / 1.050 / 0.745 / 0.495 points — so the SPECIFY gate
passes and the candidate goes to SCREEN.

**This reopening is an input-error correction.** It is *not* a Salvage (s.7 — S008 has never had one, and
none is spent here), *not* a FIX ONCE (s.6 — no rule of the strategy has changed; the trade below is the
trade that was specified), and *not* a second attempt at a candidate that failed on evidence. S008 was
never screened. It was rejected on an arithmetic error in a rule that did not exist.

## 1. Mechanism — who is on the other side and why they are forced

Constant-leverage products must rebalance **in the direction of the day's move**, near the cash close,
every day, without regard to price. A 3× long ETF that starts the day with $100 of assets and $300 of
exposure finishes an up-1% day with $103 of assets and $303 of exposure — 2.94×, not 3× — and must **buy**
to restore its mandate; an inverse fund must buy on the same up day for the mirror reason; both must
**sell** on a down day. The required notional is approximately proportional to the day's return times the
fund's leverage-weighted assets, so it is small on a quiet day and large on a big one, and it is
concentrated into the last minutes before the 16:00 ET equity close, because that is where NAV is struck.
The rebalancer is price-insensitive and must complete: he is the forced participant. The same day's
direction also drags variable-annuity and risk-parity hedging programmes, which de-risk into losses and
re-risk into gains on the same NAV clock.

The prediction is a **continuation** of the session's direction into the close, with magnitude scaling in
the size of the day's move — which is why the trade is conditioned on large-move days. This is market
mechanics, not a calendar anomaly and not a pattern description.

## 2. The whole trade

| | |
|---|---|
| **Instrument / sizing** | MNQ, **1 micro**, always |
| **Known at** | 15:00 ET, from that session's RTH bars only: `RNG` = High − Low over 09:30–15:00 inclusive; `M` = Close(15:00 bar) − Open(09:30 bar) |
| **Condition** | `\|M\| ≥ 0.50 × median(RNG)` over the **trailing 20 RTH sessions, strictly before this one** |
| **Direction** | `sign(M)` — continuation, never a fade |
| **Entry** | the **next bar's OPEN** after the 15:00 ET bar |
| **Stop** | `0.50 × RNG` against entry (tens of points by construction on these days; median ≈ 46.4 pts) |
| **Target** | `1.50 × risk` (1.5R) |
| **Time exit** | **15:55 ET**, same session. Flat before the cash close, never held through it. No cross-session exit. |
| **Bookkeeping** | the paper loop's own: first touch wins, stop wins a same-bar tie, time exit, session-end fallback (`bot_stack_paper_run._resolve_fill_outcome`) |

**No look-ahead:** the trailing-20 median uses only sessions strictly earlier than the one traded; `RNG`
and `M` come from bars at or before 15:00; the only bar read after the decision is the next bar's open,
which is the fill price by construction.

## 3. Costs — all four combinations, from `src/cost_model.py`

| combination | round trip $ | round trip POINTS | net on the specified cell's +2.55 gross pt/trade |
|---|---|---|---|
| **MNQ market entry + exit** *(decision basis)* | $2.60 | **1.300 pt** | **+1.25 pt/trade** |
| MNQ limit entry, market exit *(OPTIMISTIC)* | $2.10 | 1.050 pt | +1.50 pt/trade |
| **NQ market entry + exit** | $14.90 | **0.745 pt** | **+1.81 pt/trade** |
| NQ limit entry, market exit *(OPTIMISTIC)* | $9.90 | 0.495 pt | +2.06 pt/trade |

Sources are cited in `src/cost_model.py` (IBKR micro futures page; BrokerChooser IBKR MNQ/NQ pages; CME
contract specs). Slippage is **ASSUMED** at 1 tick per side on a market order (s.11) until B4b measures it.

**Every limit-entry figure above and in the screen is an OPTIMISTIC UPPER BOUND.** A resting limit order
does not always fill, and it fills preferentially when the market is about to trade through it (adverse
selection). No historical screen can model a non-fill, so the limit column is a ceiling on what a limit
entry could achieve, never an estimate of it. The decision basis is the honest and most expensive column:
MNQ, market entry and exit.

**SPECIFY gate (Amendment 2):** expected edge +2.55 pt > cost 1.300 pt on the decision basis ⇒ **SCREEN**.
No multiple of cost is applied, because no such rule exists.

## 4. Expected frequency

Fire rate at this condition on the Discovery slice: **0.4390 trades/session → 55.3 trades in 126 sessions**
(≈ six months), i.e. comfortably **NOT SLOW** under Amendment 1. The SLOW label is decided at SCREEN from
the screen's own rate and recorded on the PAPER row.

## 5. Where this should fail — the Salvage menu for this candidate

Written at SPECIFY by Mechanism, as the directive requires, and binding on any later Salvage check (s.7;
menu conditions only, one salvage per strategy — S008 has not spent one):

1. **Days with no meaningful move by 15:00** — the rebalance notional is proportional to the return, so
   there is nothing to trade. (This is the strategy's own filter, so it is not re-split at salvage.)
2. **Quiet-volatility regimes** (VXN low against its trailing level) — small flows, small ranges, and the
   fixed part of the cost dominates.
3. **Half-days and the sessions around them**, where the NAV clock and the equity close do not line up
   with the futures session.
4. **Scheduled-news days**, where a 14:00 ET FOMC-class release, not the rebalance, sets the afternoon
   direction.
5. **Reversal days**, where `sign(M)` at 15:00 is already the exhausted side and the late move is a
   retracement.
6. **Very wide-range days**, where `0.50 × RNG` makes the stop so large that a 1.5R target cannot be
   reached inside 55 minutes.

## 6. What would refute the mechanism

A continuation edge that does not scale with `|M|` — i.e. the same gross points on small-move days as on
large ones — would say the effect is not the rebalance flow, because the flow is proportional to the
return by construction. A screen that is profitable only in one calendar era would say the same.
