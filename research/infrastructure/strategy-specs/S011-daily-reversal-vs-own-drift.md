# S011 — NQ daily reversal, faded at the open, measured against NQ's own next-session drift

SPECIFY, 11:00 pm cycle, 2026-09-18 (Tony, scheduled, unattended). Standing directive
`research/infrastructure/standing-directive-2026-09-15.md` s.2 SPECIFY + AMENDMENT 2.
Lineage: **hyp-000152 / M18** (`research/mechanisms/volume-conditioned-daily-reversal-m18.md`),
closed 2026-09-13 as **P1_PASS_P2_FAIL**; revamp list `research/ledger/revamp_list.json`
tier **top**, closeness 1.0, mechanism HIGH.

---

## 1. What survived the closure, and what did not

Scan 026 (Discovery, n_used=1665) registered ten cells. Two matter here:

| cell | statistic | result |
|---|---|---|
| 1 (P1, GATING) | HIGH-volume sign-adjusted next-session return / ATR14 | n=555, mean **−0.0942**, ci_90 **(−0.1523, −0.0463)** — credibly negative |
| 5 (NULL 1) | **unconditional** sign-adjusted next-session return / ATR14 | mean **−0.0425** |
| 4 (P2) | HIGH − LOW | mean_diff −0.0590, ci_90 (−0.1253, **+0.0054**) — **not** credible |

P1 passed: after a session, the next session's RTH return runs **against** that session's
own direction. P2 failed: volume does not grade it. The closure form's own words —
`research/ledger/closures.jsonl`, hyp-000152 — are "**NQ has an unconditional daily
reversal**; volume level does not grade it", `not_retest: "Volume as a gradient on daily
reversal."`, and the kill check cleared it of being a gap artifact (first-minute share
0.036, threshold 0.5): the reversal **builds in over the session**, which is what makes it
tradeable at all.

## 2. Why there is no volume filter in this strategy — stated plainly

The candidate was sourced as "daily reversal after a **high-volume** session". It is **not**
built that way, for three reasons, and this is the single most important line in the spec:

1. The closure forbids it by name (`not_retest`), and `research/NEXT_UP.md`'s own sourcing
   line for S011 says the spec **may not reintroduce a volume tercile**.
2. The HIGH cell's −0.0942 is not credibly different from the unconditional −0.0425. Picking
   the HIGH cell *because it is the bigger number* is selecting on a difference the data
   refused to support — the exact error the project logs as failure mode #7.
3. A top-tercile filter fires on ~1/3 of sessions (555 / 1665). Unconditional fires on
   **every** session. Amendment 1's top sourcing preference is strategies that trade most days.

So the traded claim is **cell 5**, the unconditional reversal, and the honest expected edge is
**0.0425 × ATR14**, not 0.0942 × ATR14. The volume ratio is recorded in every signal's
`market_context` for the record and is **never** a decision input; no screen output splits on it.

This is the S003 precedent: a raw effect that closed at the hypothesis stage, built for the
first time as a whole trade, with the ledger row saying so.

## 3. The mechanism, and where it is weak — read this before the numbers

**The forced counterparty.** Campbell–Grossman–Wang (1993): a session's move is partly the
price concession that risk-averse liquidity providers demand for absorbing non-informational
order flow they did not choose. They end the session holding inventory on the wrong side of
their own book. Their constraint is capital and overnight risk, not opinion; their deadline
is the next session, when they work the inventory off. Unwinding means buying back what they
sold into a falling tape and selling what they bought into a rising one — pressure **against**
the prior session's direction, spread across the next session rather than concentrated at its
open. The first-minute share of 0.036 is the footprint of exactly that: an unwind worked
through the book over hours, not a gap.

**WHERE THIS IS WEAK, and it is weak.** The mechanism's own size prediction *failed its test*.
If the effect were inventory concession, its magnitude should scale with the size of the flow,
and volume is the best available proxy for flow size — P2 says it does not scale (or that
daily volume is too crude a proxy to see it, which is an untestable excuse, not a defence).
What survives is a **real, measured, session-long reversal with a plausible but unconfirmed
story attached**. It is entirely possible this is index-level negative lag-1 autocorrelation
with no identifiable forced seller behind it — a statistical regularity, not a flow. The
project's standard for a mechanism is a named counterparty who has no choice; here the
counterparty is named but **the evidence tying the effect to him is one-sided**. That is why
the own-drift baseline in section 6 is a gate and not a diagnostic: with the mechanism only
half-standing, the empirical test has to carry the whole weight.

## 4. The whole trade

| | |
|---|---|
| **Instrument** | MNQ, 1 micro, always. No scaling, no pyramiding. |
| **Signal session `P`** | any completed RTH session (09:30 bar present, last RTH bar present). |
| **Signal** | `M(P) = Close(last RTH bar of P) − Open(09:30 bar of P)`. Skip if `M(P) == 0` or `P` is a fragment. |
| **Known at** | `P`'s RTH close. `atr14` (14-session mean RTH range) is lagged one session. Nothing from session `T` is read before the entry. |
| **Direction** | **fade**: `short` if `M(P) > 0`, `long` if `M(P) < 0`. |
| **Entry** | the **OPEN of the 09:30 ET bar of the next RTH session `T`** — the first tradeable price after the decision. |
| **Stop** | `entry ∓ 2.0 × atr14`, a **disaster cap**, not a management stop. `R = 2.0 × atr14`. The measured effect is an unstopped open-to-close return; a strategy must still have a stop, and it is set wide on purpose so the trade stays the trade that was measured. |
| **Target** | **none** — unreachable sentinel (`entry ± 1,000,000`). A reversal-to-the-close trade has no profit target; `risk_multiple` is meaningless here and is reported as such. |
| **Time exit** | **15:55 ET of session `T`**, at that bar's open. Flat before the cash close. Same session as the entry: **no cross-session hold, no `exit_ts`.** |
| **Sizing** | 1 micro. Fixed. |
| **Costs** | `src/cost_model.py`, ASSUMED (s.11), all four combinations below. |

**No look-ahead.** `M(P)` and `atr14` come from bars at or before `P`'s close; the only bar of
session `T` read before the fill is the 09:30 bar's **Open**, which *is* the fill price.

## 5. Costs — all four combinations (AMENDMENT 2, `src/cost_model.py`)

| combination | round trip $ | round trip POINTS | net on the 4.24 pt/trade expected gross edge |
|---|---|---|---|
| **MNQ market (DECISION BASIS)** | $2.60 | **1.300 pt** | +2.94 pt |
| MNQ limit (**OPTIMISTIC**) | $2.10 | 1.050 pt | +3.19 pt |
| NQ market | $14.90 | 0.745 pt | +3.50 pt |
| NQ limit (**OPTIMISTIC**) | $9.90 | 0.495 pt | +3.75 pt |

Every limit row is an **OPTIMISTIC UPPER BOUND**: the screen assumes a resting limit order
always fills at its price. Real ones miss fills and are adversely selected.

**PRE-FREEZE EDGE-vs-COST CHECK (`cost_model.specify_gate`, Amendment 2).** Expected per-trade
gross edge = `0.0425 × ATR14` (cell 5, the *unconditional* mean — not the HIGH cell's 0.0942).
Discovery-era `atr14` runs ~100 pt (median) to ~133 pt (mean), from the 554 already-published
S004 screen trades (`data/screen_S004_with_baseline.json`, `risk_points / 4.0`). At the
**median** that is **4.24 pt/trade** against the **1.300 pt** MNQ-market cost: the gate
**PASSES** (`passes: true`, verdict `SCREEN`). It would still pass if ATR14 were only 31 pt.
**The cost wall is not the binding question for this candidate. The baseline is.**

## 6. THE BASELINE GATE — the two-nulls rule, written into the decision

`research/KNOWLEDGE.md` two-nulls rule: the correct null for a **directional** claim is the
instrument's **own unconditional drift over the same holding period**, never zero. This is
what killed H118 (2026-09-12) and what S004 was rebuilt around.

`src/screen_s011_own_drift_baseline.py` runs the screen **twice** over the same Discovery
slice, same module, same 09:30 entry, same `2.0 × atr14` stop, same sentinel target, same
15:55 exit, same `_resolve_fill_outcome` bookkeeping, same four-way cost overlay:

- **arm A — the strategy**: direction = fade `sign(M(P))`.
- **arm B — the own-drift baseline**: `BASELINE_ALWAYS_LONG = True`, direction forced **long**
  on the identical set of sessions. This is NQ's own next-session drift over the identical
  window. Arm B is **not a strategy**: never registered, never papered, never judged.

**S011 passes SCREEN only if BOTH hold on the MNQ-market basis:**
1. arm A `net_usd_1_micro > 0` (the directive's SCREEN question), **and**
2. `avg net points/trade (A) − avg net points/trade (B) > 0` (the baseline margin).

A positive net with a non-positive margin is a **FAIL** and goes to Salvage, with H118's
epitaph repeated in the ledger row. A fade strategy that merely loses less than buy-and-hold
is not an edge either — condition 1 catches that.

**PRE-FREEZE FALSIFIER, stated in the units the screen reports** (the practice S008/S010
established): *S011 fails if arm A's MNQ-market net is ≤ $0.00, or if the margin over arm B
is ≤ 0.0000 net points per trade.* Both numbers are printed by the screen script.

## 7. Where this should fail — the Salvage menu for S011 (directive s.7)

The mechanism's named failure conditions, pre-registered now so the Salvage cannot be chosen
after seeing results:

1. **High-VXN sessions** (menu condition 1). Inventory unwinds are *larger* when dealers are
   hurt, but so is the risk of a genuine trend day running the fade over. Directional prediction: unknown, and that is the point of splitting it.
2. **Trend vs range** (menu condition 2, prior-day range vs its trailing mean). The
   mechanism's own confound, from Llorente et al. via M18 P3: a large-move session may be
   **informed**, and informed moves *continue*. Fading an informed session is the single most
   likely way this loses money. This is the split that matters most.
3. **Time of day** (menu condition 3) — degenerate here: the entry clock is fixed at 09:30.
   Reported as not applicable rather than silently dropped.
4. **Scheduled-news sessions** (menu condition 4). A session whose move is a reaction to CPI /
   NFP / FOMC is repricing, not inventory. Fading it should fail.
5. **Mechanism-named, beyond the menu**: era decay across Discovery halves (M18 P4 — published
   1993, base case is decayed), and the direction split (fading up-sessions vs down-sessions),
   since a short-only leg would be fighting NQ's own upward drift.

**THE SALVAGE IS CURRENTLY BLOCKED.** Conditions 1 and 4 need VXN (coverage ends 2026-09-02)
and the macro calendar (CPI 2023-12-12, FOMC 2021-09-22, NFP 2023-12-08). Under the standing
reference-data gate (Jason, 2026-09-16) a Salvage on conditions 2 and 3 alone is **not** a
Salvage and must not be run as one. If S011 fails the screen it is recorded
**KILLED-PENDING-SALVAGE** and joins S007, S009 and S004 in `src/rerun_salvages.py`'s owed
list; it is not closed to LEARN until its full menu can run.

## 8. Effective sample — the S004 lesson, applied before any claim

S004's scrutiny (`research/studies/S004-scrutiny-2026-09-17.md`) established that a trade
count is not a sample size when holds overlap. S011 holds **09:30 → 15:55 of one session**:
one trade per session, no two holding windows share a single bar, and consecutive trades share
no price path. The effective sample should therefore equal the trade count, and the screen
verifies it mechanically (distinct dates, zero overlapping windows) rather than assuming it.
The remaining, real dependence is that trade `t`'s *signal* is the session `t−1` was entered
in — a one-lag chain in the **signal**, not in the **outcome**. Reported, not hidden.

## 9. SLOW projection (Amendment 1)

The rule fires on every session with a completed prior RTH session and `M(P) ≠ 0`, so the
expected rate is ~1.00 trades/session → ~126 projected trades in six months, far above 40:
**expected NOT SLOW**, an ordinary six-week clock. The screen's own rate is the number of
record and is printed with the result.

## 10. Registry / freeze

- Spec: this file. Module: `src/strategy_s011_daily_reversal_vs_own_drift.py`.
  Baseline runner (not frozen, not a strategy): `src/screen_s011_own_drift_baseline.py`.
- sha256 of the spec and the module go into `research/ledger/strategies.jsonl` at stage
  FREEZE, **in their own commit, before any outcome data is touched** (s.2 / s.13).
- Not edited after FREEZE. A change is a FIX ONCE, never an edit.

## 11. Reference-data status

S011 is **price-only** (OHLCV bars and the clock). It is **not** blocked by the reference-data
gate at SPECIFY, FREEZE or SCREEN. It **is** blocked downstream: paper scoring
(`step3_paper_scoring`) and the B2 risk-state decision are gated by VXN/CPI/FOMC/NFP, so a
passing S011 is registered and marked **BLOCKED_PENDING_REFERENCE_DATA** for paper entry
rather than forced into a book that cannot score it.
