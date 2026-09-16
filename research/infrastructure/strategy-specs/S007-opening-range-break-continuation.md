# S007 — Opening-range break continuation, opening-range-scaled stop (INTRADAY, fires most days)

FROZEN 2026-09-16 (9:00 am CT cycle). Module:
`src/strategy_s007_opening_range_break_continuation.py`.
Standing directive s.13: neither this file nor the module is edited after the
FREEZE row lands in `research/ledger/strategies.jsonl`. A change is a FIX ONCE
(directive s.6), never an edit.

---

## 1. Why this candidate, and why now (SOURCE)

Jason's **Amendment 1 (September 16th)** puts a new preference at the top of the
directive's s.2 SOURCE list: **intraday strategies that trade most days**, so the
six-week clock works as designed. Every strategy in the paper book is SLOW
(S001a projects 2.4 trades in six months, S002 21.8, S003 1.3, against the 40
required). This is the first candidate sourced under that preference, and it is
chosen precisely because its trigger is present on the large majority of RTH
sessions: the same opening-range break that `src/base_entry_b3.py` fires on
**2,717 of 3,638 sessions (74.7%)** as a placeholder.

**This is not B3.** B3 is frozen plumbing with no claimed edge: it exists so the
order path, execution measurement and kill switches have something ordinary to
carry, and its stop (the far side of the range) and target (one range width) are
explicitly "unconditioned" placeholders chosen for simplicity, never for a
reason. S007 takes the same daily-firing *event* and puts a real trade around
it: a decisiveness requirement on the break, a stop **scaled to the opening
range** rather than parked at the opposite extreme, a reward-to-risk target
justified by a validated magnitude fact, a longer break window that covers the
midday session that fact describes, and a stated failure list that becomes its
Salvage menu. The channel is **market structure + the Observatory's own
validated magnitude fact**, not a published calendar anomaly (0 for 4, last on
the list).

## 2. Mechanism (one paragraph, Mechanism agent)

In the first thirty minutes of the RTH session the market auctions off the
inventory imbalance accumulated overnight, and the participants who take the
other side of that opening flow are short-term liquidity providers — market
makers and fade-the-open scalpers whose entire business is the assumption that
the opening move is an overreaction. They build that inventory *inside* the
opening range, and the opposite extreme of the range is the price at which their
assumption is wrong. When price later closes decisively beyond an opening-range
extreme, those inventories are underwater: the liquidity provider who sold the
opening rally is now short into strength and must buy it back, and the buying is
mechanical, deadline-driven and in the same direction as the break. That is who
is on the other side of this trade — not a slower informed participant, but a
provider covering a position they no longer want. The move extends for as long
as that inventory is being unwound, which is why a break of the first half-hour's
range tends to continue into the midday window instead of immediately reverting.
The project's own validated magnitude fact sets the scale of that continuation:
a wide first half-hour (opening_range_vs_atr HIGH tercile, known at 10:00 ET)
predicts a midday 11:30–13:30 range about **half a trailing average wider**, with
larger excursions in **both** directions (MFE +0.0886 ATR, MAE +0.1108 ATR;
hyp-000162 / M30, `research/KNOWLEDGE.md:54`, Director re-evaluation ADVANCE at
`research/KNOWLEDGE.md:56`). Two consequences follow and both are written into
the rules below: the risk must be **scaled to the opening range** rather than set
at the far side of it, because the opening range is the readable marker of the
day's volatility regime; and because the enlarged excursion is symmetric — the
adverse one is if anything slightly larger than the favourable one — the payoff
must be better than 1:1 or the trade cannot clear costs.

## 3. The whole trade (Monetization agent)

All times America/New_York on 1-minute bars.

| | |
|---|---|
| **instrument** | MNQ (micro NQ), **1 contract, always** |
| **universe** | every RTH session with a complete 09:30–10:00 window (>= 20 bars) and a non-zero opening range |
| **opening range (OR)** | high/low of **09:30:00–09:59:59**; `W = OR_high - OR_low` |
| **break window** | **10:00:00–12:59:59** — through the midday window hyp-000162 describes |
| **trigger** | the first bar in the window whose **CLOSE** exceeds `OR_high + 0.10*W` (long) or falls below `OR_low - 0.10*W` (short). The 0.10*W buffer is the decisiveness requirement: a tick through the extreme is not a break. |
| **one trade a session** | whichever side triggers first; the other side is ignored for the rest of the day, no flip-flopping |
| **entry** | the **NEXT bar's OPEN** after the trigger bar — never the trigger bar's close |
| **stop** | `0.50 * W` against the entry (long: `entry - 0.5*W`; short: `entry + 0.5*W`). Risk is scaled to the opening range, the validated marker of the day's range regime — **not** the far side of the range, which is B3's unconditioned placeholder and risks the whole width. |
| **target** | `entry +/- 1.50 * risk` (**1.5R**), from the symmetric-excursion finding: adverse excursion is enlarged at least as much as favourable, so a 1:1 payoff cannot clear costs. |
| **time exit** | **15:55 ET** (recorded in `market_context["time_exit"]`). The trade never holds past its entry session, so no `market_context["exit_ts"]` is declared. |
| **sizing** | fixed 1 micro for the whole paper run. No scaling, no pyramiding, no discretion. |
| **costs** | **ASSUMED** — $2.50/side commission + 1 tick/side slippage = **$6.00 per micro round trip** (3.0 MNQ points), per directive s.11. Relabelled **measured** only at P2. |

Exit bookkeeping is the paper loop's, unchanged: first touch wins, the stop wins
a same-bar tie, then the time exit, then the session-end fallback
(`src/bot_stack_paper_run.py::_resolve_fill_outcome`), so the screen number and
the paper number cannot drift apart.

No look-ahead: the OR is frozen at 10:00:00; the scan only moves forward; the
only bar read after the trigger is the next bar's open, which *is* the fill by
construction.

## 4. Where this should fail — the Salvage menu (Mechanism agent, directive s.7)

Named **before** any data is touched. If the screen or the paper record fails,
Salvage splits the results by these and nothing else:

1. **Low-volatility sessions** (VXN low relative to its trailing level; menu
   condition 1). No inventory imbalance worth unwinding: the break is noise and
   the covering flow that this trade is paid by never appears.
2. **Range-bound / contracted days** (prior-day range contraction, or the day's
   own range against its trailing average; menu condition 2). This is the
   continuation thesis being exactly wrong — the day's character is that extremes
   get sold, and the liquidity provider who faded the open is *right*.
3. **Late breaks** (menu condition 3, time of day). A break at 12:50 has under
   three hours to extend; the inventory unwind is mostly done by midday.
4. **Scheduled-news sessions** (menu condition 4). A 10:00 ET release manufactures
   a break out of the opening range that has nothing to do with inventory, and
   the reaction reverses as often as it extends.
5. **Narrow opening ranges** (Mechanism's own named condition): when `W` is small
   relative to ATR, a `0.5*W` stop sits inside ordinary bar noise and the trade
   is stopped by chop rather than by being wrong. The magnitude fact that
   motivates the stop is a **HIGH-tercile** finding; the low tercile is where it
   should not hold.
6. **Gap-open sessions** (Mechanism's own named condition): when the session opens
   far from the prior close the 09:30–10:00 window is an unfinished auction, not
   a balance, so "the range" is not the thing the mechanism refers to.

## 5. Disclosures

- The paper engine's Risk/State Engine session gate and the simulated broker's
  hostile rejections/partials apply in PAPER and not in the SCREEN, as for every
  strategy in the book.
- SLOW label (Amendment 1) is decided at SCREEN from this strategy's own rate:
  `trades / sessions_screened * 126 < 40` -> SLOW. An intraday strategy that
  comes back SLOW is a red flag about the sourcing, and is reported as one.
- Exposure: the SCREEN count is logged for information only and is not a gate
  (directive s.12).
