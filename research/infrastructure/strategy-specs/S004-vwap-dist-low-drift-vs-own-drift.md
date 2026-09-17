# S004 — VWAP-distance-low 10-session drift, measured against NQ's own drift

**Status: FROZEN September 17th, 2026 (9:00 pm cycle).** Module
`src/strategy_s004_vwap_dist_low_drift.py`. Both files' sha256 are in
`research/ledger/strategies.jsonl` at the FREEZE row, written before any outcome data was touched.
Standing directive s.13: neither file is edited after that row. A change is a FIX ONCE, never an edit.

Lineage: H118 / hyp-000121/122/123/126/130/134 (`research/studies/vwap-dist-low-10d-drift-h118-spec.md`,
`research/mechanisms/h118-vwap-dist-low.md`). **S004 is a new candidate, not a re-run of H118.** H118's
frozen spec, module and forward log are untouched by this file (scope boundary, `research/NEXT_UP.md`).

## 0. Why this candidate exists — the correction that killed H118

H118 passed Discovery, Validation and Holdout and was then **REJECTED on September 12th 2026** by a
baseline diagnostic (`research/studies/h118-baseline-diagnostic-2026-09-12.md`): its LOW-tercile 10-day
drift is **not distinguishable from NQ's own unconditional 10-day drift over the same slice**.

| slice | ALL days mean R | LOW tercile mean R | LOW − ALL | block-10 bootstrap CI on the difference |
|---|---|---|---|---|
| Discovery (1717 days) | +0.5004 | +0.6166 (n=554) | **+0.1162** | (−0.2630, +0.4895) — does not clear zero |
| Validation (582 days) | +0.1996 | +0.2477 (n=216) | **+0.0481** | (−0.5851, +0.6255) — does not clear zero |

It made money because NQ went up over ten days, not because the signal knew anything. In the Full Scope's
words: it "passed all three validation stages and turned out to be the stock market going up."

**The two-nulls rule (`research/KNOWLEDGE.md`) is therefore written into this spec as a decision rule, not
a footnote.** The correct null for a directional claim is **NQ's own unconditional drift over the same
holding period**, not zero. S004 is only worth a PAPER slot if it clears BOTH:

1. **net > 0 after ASSUMED costs** (the directive's SCREEN question), and
2. **net per trade > the identical trade taken unconditionally on every session** (the own-drift baseline),
   measured in the same units, on the same slice, with the same entry clock, the same exit clock, the same
   stop and the same cost overlay — the only difference being the LOW-tercile filter.

Failing (2) while passing (1) is **not** a pass. That is exactly the failure H118 was killed for.

## 1. Mechanism — who is forced and why

NQ's session VWAP is the benchmark that agency execution is measured against. When the RTH close prints a
long way **below** that day's VWAP, the average institutional buyer who worked an order that day filled
*worse* than the tape's own average price, and the average seller filled *better*. Two participants are
then under pressure. First, the agency broker who is behind on a multi-day buy programme: his slippage is
scored against VWAP, the shortfall is realized, and the mandated quantity does not go away — it has to be
worked in the following sessions, at whatever price, because the order is a commitment and the benchmark
clock keeps running. Second, the systematic seller who has just pushed price below the day's own average
has, by construction, exhausted the willing supply at those levels; what is left in the book is
liquidity-providing bids, not motivated sellers. A close far under VWAP is thus a marker that the forced
flow in the next sessions is *buying* leftover quantity into a thinner offer.

The prediction is a **positive drift over the following ten sessions**, i.e. a slow, non-intraday
continuation of mean reversion toward the volume-weighted average.

**And here is the honest problem with that mechanism, stated at SPECIFY rather than discovered later.**
NQ drifts up over ten sessions *anyway*. Over the Discovery slice an unconditional ten-day hold returns
+0.50 R. Any story about forced buyers has to earn its keep **on top of** that, because the trade it
motivates — be long the index for ten sessions — is the market's default state. This is the single reason
S004 exists as a separate candidate and the reason the own-drift baseline is a gate in section 5, not a
diagnostic in an appendix.

## 2. The whole trade

| | |
|---|---|
| **Instrument / sizing** | MNQ, **1 micro**, always. No scaling, no pyramiding. |
| **Signal session `P`** | any completed RTH session |
| **Descriptor** | `vwap_dist_vs_atr(P)` = (RTH close of `P` − that session's own RTH VWAP at its last bar) / `atr14(P)`, where `atr14` is the 14-session mean daily RTH range **lagged one session**. Identical to H118's descriptor (`market_state_primitives_v2._rth_volume_and_close_vwap_dist_by_day`). Known at `P`'s close. |
| **Condition** | `vwap_dist_vs_atr(P)` falls in the **LOW tercile** on bucket edges **frozen from Discovery and never refit**: `(-inf, -0.04604781358468863]`. These are H118's own published Discovery edges (`data/study_vwap_dist_low_10d_drift_h118_results.json`), hardcoded in the module so no slice is ever re-fitted at paper time. |
| **Direction** | **long** only. The mechanism is one-sided; there is no short leg and no fade. |
| **Entry** | the **OPEN of the 09:30 ET bar of the next RTH session** `P+1`. Not `P`'s close: the descriptor is only known once `P`'s last bar has printed, so entering on `P` would be look-ahead. |
| **Exit** | the **OPEN of the 09:30 ET bar of session `P+11`** — exactly **10 RTH sessions held**, declared as an absolute `market_context["exit_ts"]` and bookkept by the paper loop's cross-session walk (choice 7, `bot_stack_paper_run.cross_session_exit_ts`). |
| **Stop** | `entry − 4.0 × atr14`, a **disaster cap**, not a management stop (H118 itself had no stop; a strategy must have one). `R = 4.0 × atr14`. |
| **Target** | **NONE.** A drift trade has no profit objective; an unreachable sentinel is used and `risk_multiple` is meaningless for this strategy, exactly as for S003. |
| **One trade a session** | the paper loop's rule. A new LOW signal while a position is open produces a separate session's signal; the loop takes the first signal of each session and the screen does the same. |
| **Bookkeeping** | the paper loop's own: first touch wins, stop wins a same-bar tie, time exit at `exit_ts`, session-end fallback (`bot_stack_paper_run._resolve_fill_outcome`). |

**No look-ahead.** The descriptor uses only bars of session `P`; `atr14` is lagged one session; the entry
price is the open of the first bar of `P+1`, the first bar read after the decision; the exit timestamp is a
calendar/session fact declared at entry. When session `P+11` is not yet on disk the module emits the signal
with a placeholder exit timestamp that the loop's cross-session guard refuses — the session is deferred
whole, nothing is booked, and it is re-scored when the exit session exists. The placeholder can never book
a trade.

**S004 reads NO reference data.** Its entry rule, its stop and its exit are price-only: RTH bars, session
VWAP and ATR. It does not read VXN, the macro calendar, or any other series in
`research/ledger/data_coverage.json`. The validated VXN→next-session-range sizing fact was **deliberately
not used** for the stop, because using it would make a price-only candidate depend on a stale series and
block its own screen. The stop is therefore ATR-based. This is a design choice recorded at SPECIFY, not a
convenience discovered later.

## 3. Costs — all four combinations, from `src/cost_model.py`

Expected per-trade edge used at the gate is the **baseline-corrected** one, not the raw statistic: from the
published Discovery numbers, LOW = +83.26 net points/trade and ALL-days = +67.57 net points/trade in the
same units (both at H118's old 3.00-point cost), so the edge **over NQ's own drift** is **+15.69 points per
trade**. The raw (vs-zero) figure of +83.26 is *not* the number this spec relies on.

| combination | round trip $ | round trip POINTS | net on the +15.69 pt/trade baseline-corrected edge |
|---|---|---|---|
| **MNQ market entry + exit** *(decision basis)* | $2.60 | **1.300 pt** | **+14.39 pt/trade** |
| MNQ limit entry, market exit *(OPTIMISTIC)* | $2.10 | 1.050 pt | +14.64 pt/trade |
| **NQ market entry + exit** | $14.90 | **0.745 pt** | **+14.95 pt/trade** |
| NQ limit entry, market exit *(OPTIMISTIC)* | $9.90 | 0.495 pt | +15.20 pt/trade |

Sources are cited in `src/cost_model.py` (IBKR micro futures page; BrokerChooser IBKR MNQ/NQ pages; CME
contract specs). Slippage is **ASSUMED** at 1 tick per side on a market order (s.11) until B4b measures it.

**Every limit-entry figure above and in the screen is an OPTIMISTIC UPPER BOUND.** A resting limit order
does not always fill and fills preferentially when the market is about to trade through it (adverse
selection); no historical screen can model a non-fill. The decision basis is the honest and most expensive
column in points: MNQ, market entry and exit.

Note the structural point for a ten-session hold: at 1.300 points per round trip the cost is a rounding
error against a hold whose typical excursion is tens of points. **Costs are not what decides S004. The
baseline is.**

**SPECIFY gate (Amendment 2, `cost_model.specify_gate`):** expected edge **+15.693 pt > cost 1.300 pt** on
the decision basis ⇒ **SCREEN**. No multiple of cost is applied, because no such rule exists.

## 4. Expected frequency

H118's own Discovery rate: 554 signal days in 1717 sessions = **0.3227 trades/session → 40.7 trades in 126
sessions** (≈ six months). That is **marginally NOT SLOW** under Amendment 1, and marginal enough that the
label must be taken from the screen's own rate, not from this estimate. The SLOW label is decided at SCREEN
(`screen_strategy.py` / `strategy_registry.slow_projection`) and recorded on the PAPER row.

## 5. THE BASELINE GATE — the correction, written into the decision

`src/screen_s004_own_drift_baseline.py` runs the **identical trade on every RTH session of the same
Discovery slice** — same 09:30 entry, same ten-session hold, same `4.0 × atr14` stop, same sentinel target,
same `_resolve_fill_outcome` bookkeeping, same four-way cost overlay — with the LOW-tercile filter removed
and nothing else changed. S004 passes SCREEN only if:

- `net_usd_1_micro > 0` on the MNQ-market decision basis, **AND**
- `avg net points per trade (S004) − avg net points per trade (all-sessions baseline) > 0`.

A positive net against zero with a non-positive margin over the baseline is reported as a **FAIL** and sent
to Salvage, with the sentence that killed H118 repeated in the ledger row: the strategy is the stock market
going up. The margin is reported in points per trade and in R, next to the raw net, in the screen report and
in the registry SCREEN row.

## 6. Where this should fail — the Salvage menu for this candidate

Written at SPECIFY by Mechanism, as the directive requires, and binding on any later Salvage check (s.7;
menu conditions only, one salvage per strategy — S004 has not spent one):

1. **High-volatility regimes** (VXN elevated against its trailing level) — a ten-session hold with a
   `4.0 × atr14` disaster cap is a short-volatility position in disguise; the cap is hit on the drawdowns
   that only happen when volatility expands. *(Menu condition 1 — needs the VXN series.)*
2. **Trending-down slices**, where NQ's own ten-day drift is negative — if the LOW filter carries no
   information, S004 is simply long the index and loses with it. *(Menu condition 2.)*
3. **Time of day is not a live axis here** — entry and exit are both fixed at 09:30 — so menu condition 3
   degenerates for S004 and should be recorded as inapplicable rather than run. *(Menu condition 3.)*
4. **Scheduled-news days inside the ten-session window**, where an FOMC-class release, not the leftover
   agency quantity, sets the ten-day path. *(Menu condition 4 — needs the macro calendar.)*
5. **Overlapping positions**: ten-session holds overlap heavily, so consecutive signals are nearly the same
   trade. A result driven by a handful of non-overlapping episodes is a sample-size illusion.
6. **The baseline itself**: any era in which the unconditional drift is large enough to account for the
   whole result.

**Conditions 1 and 4 require reference series that are stale as of this cycle** (VXN ends 2026-09-02;
FOMC ends 2021-09-22, CPI 2023-12-12, NFP 2023-12-08). Under Jason's standing reference-data rule
(September 16th 2026) a Salvage for S004 is therefore **BLOCKED** while they are stale, and a partial
salvage on conditions 2, 3 and 5 alone is **not permitted** — one salvage per strategy, and spending it on
half the menu would spend it on the wrong half.

## 7. What would refute the mechanism

A drift that is the same size on days the close is *far* below VWAP as on days it is *barely* below would
say the effect is not leftover agency quantity, because the shortfall to be worked is proportional to the
distance by construction. A result that survives against zero but not against the unconditional hold says
the same thing H118's diagnostic said, and is the null this candidate was built to test.
