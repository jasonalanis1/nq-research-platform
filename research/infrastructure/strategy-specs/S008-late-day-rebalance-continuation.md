# S008 — Late-day constant-leverage rebalance continuation

**Status: SPECIFIED, NOT FROZEN, CLOSED TO LEARN AT MONETIZATION.**
The standing directive s.4 gives Monetization the ruling "no credible path", which
"sends the candidate to LEARN without a screen". That is what happened here, and it
happened at the pre-freeze cost-budget check this spec states below — before a spec
hash, before a module, before a screen row. Nothing about S008 is frozen; this file is
the record of a candidate that was specified and refused, not a frozen contract.

Sourced under Jason's **Amendment 1** top preference (intraday strategies that trade
most days), and under the lesson the 9:00 am cycle recorded from S007
(`research/KNOWLEDGE.md`): **ask for per-trade edge first, fire rate second.**

---

## 1. The cost budget — stated first, on purpose

This is the number S007 was not made to answer before it was frozen.

- ASSUMED costs: $2.50/side commission + 1 tick/side slippage = **$6.00 per micro
  round trip** (`src/paper_book.py`, labelled ASSUMED until B4b measures it).
- MNQ is **$2.00 per index point**, so the round trip is **3.00 index points**.
- A trade is worth running at 1 micro only if its **gross expectancy per trade is
  well north of 3.00 points**. "Well north" is made concrete here as **at least
  3× the cost, i.e. ≥ 9.0 gross points per trade**, so that costs are ≤ ~1/3 of the
  edge rather than 17× it as they were for S007 (+$0.35 gross against $6.00).
- Equivalently: with a stop-and-target structure of R points, the trade must earn
  more than `3.0 / R` in R terms just to break even. A structure with R = 50 points
  pays 0.06R of cost; a structure with R = 12 points pays 0.25R.

**The budget therefore demands both halves: a stop measured in tens of points AND a
gross edge measured in tens of points. Either alone fails.**

## 2. Mechanism — who is on the other side and why they are forced

Constant-leverage products must rebalance in the direction of the day's move, near
the cash close, every day, without regard to price. A 3× long ETF that starts the
day with $100 of assets and $300 of exposure finishes an up-1% day with $103 of
assets and $303 of exposure — 2.94×, not 3× — and must **buy** to restore the
mandate; an inverse fund must buy on the same up day for the mirror reason; both must
**sell** on a down day. The required notional is approximately proportional to the
day's return times the fund's leverage-weighted assets, so it is small on a quiet day
and large on a big one, and it is concentrated into the last minutes before the 16:00
ET equity close because that is where the fund's NAV is struck. The rebalancer is
price-insensitive and must complete: he is the forced participant. The same day's
direction also drags variable-annuity and risk-parity hedging programmes, which
de-risk into losses and re-risk into gains on the same NAV clock. The prediction is a
**continuation** of the session's direction into the close, with magnitude scaling in
the size of the day's move — which is why the candidate is conditioned on large-move
days: the fixed $6.00 is a smaller share of a bigger forced flow.

This is market mechanics, not a calendar anomaly and not a pattern description.

## 3. The whole trade (what would have been frozen)

| | |
|---|---|
| **Instrument / sizing** | MNQ, **1 micro**, always |
| **Known-at** | 15:00 ET: `M = Close(15:00) − Open(09:30)`, and `RNG` = the 09:30–15:00 RTH range |
| **Condition** | `|M| ≥ 0.5 × median(RNG)` over the trailing 20 sessions — a large-move day, where the forced rebalance is large |
| **Direction** | `sign(M)` — continuation, never a fade |
| **Entry** | the next bar's OPEN after 15:00 ET |
| **Stop** | `0.50 × RNG` against entry (tens of points by construction on these days; median 46.4 pts) |
| **Target** | `1.5 × risk` |
| **Time exit** | 15:55 ET, same session (flat before the cash close, never held through it) |
| **Costs** | ASSUMED $6.00 per micro round trip = 3.00 index points |

Fire rate at that condition: **0.439 trades/session → 55.3 trades in 126 sessions**,
i.e. comfortably **not SLOW** under Amendment 1. The frequency half of the design
works. The edge half does not.

## 4. The pre-freeze budget check — the reason this was never frozen

`src/study_s008_intraday_cost_budget.py` on the Discovery slice (2,101 sessions;
descriptive, no spec hashed, no screen row, no Validation or Holdout data touched);
full numbers in `data/study_S008_cost_budget.json` and
`research/studies/S008-cost-budget-2026-09-16.md`.

- **The specified cell** (T = 15:00, `z ≥ 0.5`): n = 708, **gross +2.55 points per
  trade**, t = 2.11, median half-range stop 46.4 pts. Against a 3.00-point cost that
  is **−0.45 points net per trade** — a losing trade before a single fill is
  simulated. Against the stated budget of ≥ 9.0 gross points it misses by 3.5×.
- **The whole family misses.** Across a 36-cell grid of decision times
  (10:00–15:30 ET) × move thresholds (`z` ≥ 0.0/0.5/0.8/1.0), every gross expectancy
  lands between **−0.9 and +5.5 points**. The single best cell of 36 is +5.54 pts
  (T = 13:30, `z ≥ 0.5`, t = 2.93) — still short of the budget, and it is the maximum
  of a grid, which is the ex-post selection this project has now refused twice.
- **The reversion family fails the same way, from the other side.** The RTH VWAP
  2σ-band reversion (the honest version of `src/detect_vwap_reversion.py`, moved off
  its 08:30 pre-market open to the 09:30 RTH open, with a real 1:1 stop and a VWAP
  target) fires on 92.7% of sessions — 1,513 signals — at **gross +0.043R** with a
  median risk of 17.6 points, i.e. **−1.55 points net per trade**. Its gross R edge
  is flat across distance buckets (+0.098 / +0.038 / −0.014 / +0.012 / +0.082), so
  the only bucket that nets positive (> 50 pts, +7.9 pts) is positive because the
  distance is large, not because the edge is.
- **The validated magnitude facts were used as the spec requires, and they do not
  rescue it.** The quiet-midday fact selects days whose afternoon range is *smaller*
  in absolute points (median 27.4 pts vs 38.2), which is the wrong direction for a
  fixed cost. The wide-opening-range fact (hyp-000162 / M30) splits 48.3% of sessions
  and leaves the morning-entry continuation at +3.1 / −0.8 / +0.7 / +1.1 points
  (t = 1.05 / −0.30 / 0.27 / 0.43) — no edge to widen a stop around.

**Ruling (Monetization, directive s.4): NO CREDIBLE PATH at 1 micro on the ASSUMED
cost basis. S008 goes to LEARN without a screen. It is not frozen, no screen is
spent, and no slice of the grid is taken.**

## 5. Where this should fail — its Salvage menu, had it been frozen

Recorded because it is what the Mechanism agent owes at SPECIFY, and because
anything revisiting this mechanism inherits the list:

1. Days with no meaningful move by the decision time — the rebalance notional is
   proportional to the return and there is nothing to trade.
2. Quiet-volatility regimes (VXN low against its trailing level) — small flows,
   small ranges, the fixed cost dominates.
3. Half-days and the sessions around them, where the NAV clock and the equity close
   do not line up with the futures session.
4. Scheduled-news days, where the 14:00 ET FOMC-class release, not the rebalance,
   sets the afternoon direction.
5. Reversal days, where `sign(M)` at 15:00 is already the exhausted side.
6. **The cost side itself** — this is the condition that actually fired: a mechanism
   can be real and still be too small to pay for a $6.00 round trip.

## 6. What would have to change for this mechanism to be worth revisiting

Not a filter. A bigger per-trade structure: a measured (not assumed) cost basis from
B4b, a larger instrument, or a hold long enough for the forced flow to accumulate
into tens of points. The mechanism is not refuted here. What is refuted is that
**$6.00 a trade is affordable out of a 2–5 point intraday drift.**
