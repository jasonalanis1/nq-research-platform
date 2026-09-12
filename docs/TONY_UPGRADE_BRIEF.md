# Tony — Upgrade Brief

**From:** Jason (direction) via outside review
**Date:** September 11, 2026
**Status:** Direction. Research Director convenes a staff meeting to adopt; Integrity Gate rules on anything that touches frozen work.

---

## 0. What this is

The full-scope document was reviewed by an outside trading lens. Verdict: the research discipline is sound and stays. The project is over-governed and under-informed — every safeguard is a filter, none is a lens. The upgrades below add the lens, remove ceremony, and open a realistic path to capital on the timeline Jason actually has.

Nothing here weakens a freeze, a review point, or the evidence bar.

---

## 1. Direction decisions (Jason's answers, binding)

| Question | Decision |
|---|---|
| Holding period | No preference in principle. Speed of validation is the constraint: prefer candidates that resolve in weeks, not months. |
| Money goal | $1,000/month; $12,000 in the first 12 months. Start small and scale. |
| Scale | Whatever size and trade count the edge supports. Not fixed at 1 micro. |
| Data budget | **$20/month cap now.** Once profitable, **half of net profit** reinvested in data. Order-flow data is deferred until then. |
| Early live | **Yes** — tiny live size on a candidate once execution qualification passes, *before* the statistical review point ends. Capital-protection rules handle risk. |
| Starting risk budget | **$300**, reserved for a short-horizon edge (per-trade swing $50–150 per micro). Up to **$500** only after a fast, measured paper record. H118 excluded. |
| Trailing loss rule | Once profitable, willing to give back about **one-third of peak profit**. Provisional, to be revisited. |
| Involvement | Hands-on as needed now; trending toward brief check-ins. |
| Broker | None yet. Open to recommendation. |

### Decision on the $300 and H118

**$300 is reserved for a short-horizon edge** where one micro's per-trade swing is $50–150. H118 is **not** funded for early live: its risk unit is ~$700 per MNQ and a single 10-day trade swings ±$1,000–1,400, so $300 would be consumed by noise within two or three positions. H118 stays on the research clock only; any future H118 live decision needs its own budget (~$2,000–3,000) and is Jason's call at that time.

Jason would consider **up to $500** only for a candidate that has already shown fast, measured results in paper. No strategy offers guaranteed profit; the practical reading is: the budget rises from $300 to $500 only after the candidate's paper record (20+ trades, slippage measured, positive net) is in hand — never on a backtest.

**Consequence for priorities:** the fast lane is now the whole game. The market map (Upgrade 1) and short-horizon scans are where the first live dollar comes from. H118 is a slow-lane bet that may or may not resolve in 12 months (see Upgrade 5).

---

## 2. Upgrade 1 — The market map (highest priority)

**Problem.** Discovery scans cut generic variables (range/ATR, VWAP distance, volume) into terciles. That is search, not discovery. 132 hypotheses, one survivor, and the current idea shelf is three variants of "range vs. ATR."

**Fix.** A standing document, `research/market_structure_map.md`, owned by LEARN as a fifth bucket: **KNOWN STRUCTURE**. Every scan scope must name which map entry it probes. An idea-inventory entry with no map anchor is not an entry.

Each map entry names who is *forced* to trade, when, and what footprint that should leave in 1-minute NQ data. Seed list (all findable in current data):

| # | Situation | Who is forced, and why | What to measure | Horizon |
|---|---|---|---|---|
| M1 | **Cash close, 15:50–16:00 ET** | Index funds, ETFs, rebalancers must execute at the close (MOC). Futures absorb the imbalance. | Last-10-minute move → next-morning open / first 30 min RTH | Overnight |
| M2 | **RTH open, 9:30–10:00 ET** | Overnight inventory gets resolved; opening auction imbalance. | Opening-range break conditioned on overnight range and gap size | Intraday |
| M3 | **Scheduled macro releases** (CPI/PPI 8:30, FOMC 14:00, NFP) | Everyone reprices at once; options dealers re-hedge. Calendar is public and free. | Post-release continuation vs. reversal, 30/60/120 min | Intraday |
| M4 | **Pre-FOMC drift** | Academically documented (Lucca–Moench): equities drift up the 24h before FOMC statements. | Return from prior-day close to 14:00 on FOMC days vs. baseline | 1 day |
| M5 | **Month-end / quarter-end, last 2 sessions** | Pension and balanced funds rebalance equity vs. bonds. When NQ has outrun ZN over the month, they are forced sellers. | NQ month-to-date vs. ZN month-to-date → last-2-day and first-2-day return (ZN data already on disk for Discovery) | 1–3 days |
| M6 | **Turn-of-month inflows** | Payroll/401k contributions land in the first sessions of the month. | First 3 sessions vs. baseline, conditioned on prior month | 1–3 days |
| M7 | **Vol-control / risk-parity deleveraging** | Funds targeting fixed volatility must sell when VXN spikes and re-buy as it falls, over 1–3 days. Mechanical, well-documented. | VXN change (1d, 3d) → NQ forward 1–3 day return; VXN data already on disk | 1–3 days |
| M8 | **CTA trend flows** | Trend-followers must add after multi-day breakouts and cut after breakdowns. | 20/50-day breakout state → 1–3 day continuation | 1–3 days |
| M9 | **Nasdaq-100 rebalance / reconstitution days** (quarterly, annual Dec) | Index funds must trade the change at the close. Dates are public. | Close-window volume and move vs. normal days; next-day reaction | Overnight |
| M10 | **European close, 11:30 ET / midday lull** | Liquidity providers step back; hyp-000106 already characterized the lull. | Lunch-hour reversal of the morning move; needs a new mechanism claim, not a re-cut | Intraday |
| M11 | **Cross-asset divergence** (already flagged by LEARN 2026-09-10) | NQ–ZN co-movement breaking down forces systematic rebalancing. | Rolling correlation breakdown → NQ 1–3 day | 1–3 days |

**LEARN check before use:** the opex/expiry family (`days_to_monthly_opex`) and the overnight-range family are at the 2-attempt limit. Any map entry touching them must carry a genuinely different mechanism claim or it does not enter. Expiry-day *dealer hedging* is real market structure, but without options data the footprint is weak in 1-minute NQ — deferred until the data budget grows.

**Deliverable:** Discovery drafts the map from this seed list; LEARN files it; Director ranks the first three scopes. Replace the current shelf entries 4–6 only if they cannot be anchored to a map entry.

---

## 3. Upgrade 2 — Data policy

- **Cap: $20/month.** Databento yearly-chunk pulls (~$8–15 per instrument-range) fit. Order-flow (trades/MBP-1) does not, and is **deferred** until profits fund it (half of net profit reinvested).
- **Consequence, stated plainly:** the short-horizon ceiling is set by data, not ideas. Sub-15-minute microstructure edges are out of reach for now. The map above is built around what 1-minute bars *can* see: session boundaries, calendar events, cross-asset state.
- **Free data to add now ($0):** economic-release calendar (BLS, Fed), Nasdaq rebalance dates, exchange holiday/early-close schedule (also resolves the 15:58 missing-bar issue in execution item 1a).
- **Refresh:** Jason still runs Databento pulls manually. Ops Manager tracks data currency and flags when the live-forward window is more than 5 sessions stale.

---

## 4. Upgrade 3 — Pipeline restructure

**Why.** Ten roles for one AI is overhead. The value is in the forcing questions, not the seats. Triage and Director Re-evaluation are the same judgment twice; Monetization before any out-of-sample result is premature.

**New order:**

```
Jason (direction)
  -> RESEARCH DIRECTOR   scope, freeze, allocation. Absorbs Candidate Triage (A–F grade issued at scan close)
       and Re-evaluation (the same "worth more capital?" call, now made once, at the Validation gate).
  -> MECHANISM           written WITH the scope, BEFORE the scan (claim + 2 predictions + falsifier).
                         Post-scan it may only ADD predictions; it may not rewrite the claim.
  -> DISCOVERY           scan the frozen scope; report cells, novelty, exposure.
  -> STATISTICAL         stability, regime, magnitude, selection, multiplicity — AND statistical power
                         at the proposed review point (new, mandatory). Owns the cost model.
  -> INTEGRITY GATE      BLIND checkpoint (Upgrade 4) before Validation.
  -> VALIDATION          one pre-registered shot.
  -> MONETIZATION        now here: realization path, execution spec, measured cost assumption.
                         "No credible path" still a valid close.
  -> INTEGRITY GATE      blind checkpoint before Holdout.
  -> HOLDOUT             Jason's slot.
  -> PORTFOLIO           unchanged.
```

**How it works with the existing workflow:**
- *Applicability*, *RETURN*, *staff-meeting triggers*, *LEARN consultation*, *Ops Manager* — all unchanged.
- *Idea Inventory entry bar* gains a fifth requirement: a map anchor (Upgrade 1). Because Mechanism now precedes the scan, the inventory's one-line mechanism claim becomes the seed of the mechanism doc rather than a separate step.
- *Ops `mechanism-gate` check* moves its trigger from "past Discovery" to "any frozen scope without a mechanism doc" — earlier, stricter, cheaper.
- *Session cost:* one fewer Director pass and Monetization deferred on most candidates (most die before Validation). Expect shorter sessions with the same evidence.

---

## 5. Upgrade 4 — Blind Integrity Gate

The Gate is not independent when the same session that produced a number then reviews it. Fix, one rule:

> The Integrity Gate checkpoint runs in a **fresh session** with no prior context. It receives the frozen spec, the scan/test code, the mechanism doc, and the ledger history — **with all result figures masked**. It rules on whether the *procedure* could fool us. Only after it rules are the numbers unmasked and the ruling logged alongside them.

Continuous-role duties (freeze rules, resurrection checks, multiplicity tracking) stay in-session. Only the two checkpoints go blind.

---

## 6. Upgrade 5 — Power check on H118's review point (do this week)

Statistical computes, once, from the Discovery/Validation/Holdout data: at 40 resolved trades, what is the probability the 90% CI clears zero *if the true effect is 0.40R*? Rough outside estimate is ~40–50%, i.e., the locked review point may return "inconclusive" after a year.

The review point **does not move** — that rule holds. But Jason needs to know now whether the 12-month clock is likely to answer the question, because it changes whether H118 is the slow-lane bet or the wrong bet. Report the number; no action on H118.

---

## 7. Upgrade 6 — Capital-protection rules (written now, frozen before any live authorization)

Per live strategy, in code, checked before every order:

1. **Starting risk budget:** $300, reserved for a short-horizon candidate (per-trade swing $50–150 per micro). Rises to $500 only after a positive measured paper record. H118 is excluded at this budget (Section 1).
2. **Trailing kill:** shut off when equity falls below `max(−$300, peak_profit − max($300, peak_profit / 3))`. In words: you may always give back $300 from the peak, or one-third of peak profit, whichever is larger. Jason marked provisional.
3. **Slippage kill:** measured average fill deviation over the last 20 fills exceeds **25% of the strategy's working edge** in points → suspend, report.
4. **Signal-divergence halt:** any day where the live engine's signal differs from the frozen reference implementation → halt all orders, flag Jason. Zero tolerance.
5. **Per-trade catastrophe stop:** 2R (2× entry-day ATR14) on the execution side, plus a daily loss cap of half the remaining budget. This is an *account* control, not a strategy edit: every trigger is logged as an execution-spec divergence from the research spec. If it triggers more than twice in 40 trades, that is a finding about the strategy's tail, reported, never tuned.
6. **Position/order caps and fail-closed** per the existing safety-controls list.

Statistical kills remain **prohibited** during any forward-validation window. Execution/capital kills are **required** from the first live order.

---

## 8. Upgrade 7 — The early-live path ("Live-Limited")

Jason's speed need and the 12-month H118 review point conflict. Resolution that keeps both intact:

- Insert **Stage 3.5: Live-Limited** between Execution-Qualified and Live-Authorized. Applies to the first short-horizon candidate to reach it; H118 is not eligible at the current budget. Entry: all 14 execution checks pass on paper with a pre-registered minimum sample (proposed: 20 paper trades, slippage measured). Size: minimum contract. Governed entirely by Section 7 rules.
- The research clock is untouched: no statistical read, no status change, no interim peek. Live-Limited P&L is an *execution* record, not evidence about the hypothesis.
- Live-Limited is still **Jason-only authorization**, per the standing rule. The upgrade is that the authorization is allowed to come before the statistical review point closes — not that it is delegated.
- Live-Limited ends only by: capital-protection kill, the statistical review point (then the normal promotion decision), or Jason.

---

## 9. Upgrade 8 — Broker and execution stack

Recommendation for a $20-data-budget, micro-contract, API-driven start:

- **Tradovate** — free paper accounts, native TradingView integration (fits Phase 6), low per-side MNQ commissions, webhook/API path. Verify current API access fee before committing; it has varied.
- **Interactive Brokers** — stronger, better-documented native API and the more serious long-term home, but more setup friction and a stricter paper-account model.

Start on Tradovate paper for Stage 3; move to IBKR if API limits bite. Execution-stack costs (~$60–115/mo, approved 2026-09-10) are a separate line from the $20 data cap — Jason to confirm that approval stands under the new budget framing.

---

## 10. Upgrade 9 — Reporting to Jason

Replace ad-hoc escalation with a fixed shape:

- **Daily (2 lines, local time):** research — what moved, what's queued; execution — open positions, day P&L, budget remaining, any kill state.
- **Immediate:** any capital-protection trigger; any $5+ spend request; any integrity flag on promoted work; any awaiting-Jason item older than 48 hours.
- **Weekly:** map coverage (which entries scanned, which open), power/multiplicity status, one candid sentence from the Director on whether the methodology is still finding things.

Involvement scales down by reducing the daily to weekly once Live-Limited has run 30 days without a trigger.

---

## 11. Sequence

1. This week: Upgrade 5 (H118 power number) — Statistical. Upgrade 4 (blind Gate rule) — Integrity. $300/H118 conflict resolved: H118 not funded for early live.
2. Next: Upgrade 1 (market map drafted, LEARN-checked, three scopes frozen) — Discovery/LEARN/Director. Upgrade 3 adopted by staff meeting.
3. Then: Upgrade 6 rules written into code and tested. Upgrade 8 broker paper account opened (Jason). Execution items 1a/1c/1d proceed.
4. Ongoing: Upgrade 2 and 9 as standing policy.

## 12. For the staff meeting

- Adopt/modify each upgrade; record every agent's position.
- Integrity Gate rules on whether Section 7 item 5 (execution-side stop) is admissible under the scope boundary. Outside view: yes, because it lives in the execution spec and is logged as divergence, never applied to the research record.
- Director names one thing on this list that is process rather than progress, if any.
