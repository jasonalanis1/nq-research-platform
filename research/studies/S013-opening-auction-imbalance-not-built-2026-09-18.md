# S013 — opening-auction order imbalance, NQ: CLOSED TO LEARN AT SOURCE, NOT BUILT

**Date:** 2026-09-18, 11:00 am CT cycle. **Lineage:** hyp-000076
(`opening_volume_imbalance`, Discovery, REJECTED, expectancy −0.0614 R, n=1684,
ci_90 (−0.1047, −0.0170)). **Disposition:** LEARN. No spec, no freeze, no screen.
**Slice touched:** Discovery only (the overlap measurement). Validation and
Holdout untouched.

## 1. The closure-form check (the standing process change, run FIRST)

hyp-000076 has **no U8 closure row** in `research/ledger/closures.jsonl` (that
file holds 13 rows, hyp-000146..hyp-000162 only). It therefore carries **no
`not_retest` string and no `condition` field of its own**, and it is not named in
any other row's `not_retest`. On the letter of the check it is **not banned**.

It is, however, covered by a **pre-committed decision rule** recorded in the
ledger note of its sibling hyp-000078
(`research/ledger/hypotheses.jsonl`, `volume_imbalance_alignment_confluence`):

> "Closes the single-day reactive-trigger 'fresh pre-move behavior' direction per
> the pre-committed decision rule -- 7 of 7 tests (6 individual + this
> confluence) found no gross edge, cost-dominated losses throughout. Further
> search in this specific vein needs either **a genuinely new data source or a
> longer holding-period structure, not another intraday reactive trigger**."

hyp-000076 is one of those 7. S013 as sourced is another intraday reactive
trigger on the same 09:30–10:00 window, from price and volume only — no new data
source, no longer holding structure. **The rule bans it in substance even though
no `not_retest` string exists.** This is the third cycle running (S006, S012,
now S013) in which a candidate reached the front of the queue on a *closeness*
ranking while its closure condition forbade the work. The closeness field ranks
how near a number came to credibility; it says nothing about whether the family
is open. LEARN: **the closure-form check must read the lineage's siblings'
pre-committed decision rules, not only its own `not_retest`/`condition` pair** —
pre-Gate rows carry their bans in prose, in the sibling that closed the vein.

## 2. The mandatory S011 overlap check (condition 2) — RUN, and it PASSED

Measured, not assumed: `src/overlap_check_s013_vs_s011.py`, Discovery slice
(2,101 sessions, 2021-10-03 or earlier), output `data/overlap_S013_vs_S011.json`.
No costs, no expectancy, no outcome — selection and direction only.

| quantity | value |
|---|---|
| sessions S011 selects | 1,669 |
| sessions the S013 rule selects | 1,686 |
| jointly selected | 1,667 |
| session-selection overlap (Jaccard) | **98.76 %** |
| share of S013 sessions S011 also takes | 98.87 % |
| **same direction on joint sessions** | **856 / 1,667 = 51.35 %** |
| opposite direction on joint sessions | 811 |

**Correction to the standing description of S011.** S011 does *not* fire "after
high-volume sessions". Its frozen module
(`src/strategy_s011_daily_reversal_vs_own_drift.py:15-22`) trades cell 5, the
**unconditional** daily reversal, and states there is no volume filter on
purpose, because hyp-000152's `not_retest` is "Volume as a gradient on daily
reversal". S011 therefore fires on essentially **every** session. The ~99 %
session overlap is a mechanical consequence of that and carries no information.

The question with content is direction, because both trades sit in the same
instrument on the same session and exit at 15:55 ET of that session — where the
two agree, they are one position, not two bets. Agreement is **51.35 %**, a coin
flip. **S013 is an independent direction rule, not an S011 variant.** Condition 2
is satisfied and is *not* the reason S013 closes. The portfolio note for any
future revival: running both would mean doubled same-session exposure on ~51 % of
sessions and a flat book on ~49 %, so they would still have to be sized jointly.

## 3. Condition 3 (sign-flipping forbidden) — this is what kills it

hyp-000076 closed **credibly negative**, CI entirely below zero. A continuation
mechanism can be stated and named: opening-window imbalance reveals a metaorder
the executing desk must work through the session, and the forced counterparty is
the liquidity provider filling the remainder of that parent order. That story is
exactly what was tested, and it **lost money credibly**. The only construction
with a positive expectancy is the fade — and "the continuation rule lost money,
so fade it" is the forbidden rationale, pre-registered as condition 3 in S013's
own SOURCE row. A credibly negative expectancy **measured against zero on a
drifting instrument** is in any case substantially a statement about drift and
costs, not about a fadeable behaviour; the original never carried an own-drift
baseline arm. The mechanism paragraph cannot stand without the minus sign.
**S013 closes at SOURCE, per its own pre-registered condition 3.**

## 4. Data Acquisition Trigger (recorded, not acted on)

S013 was sourced under the name "opening-auction **order imbalance**". Exchange
opening-auction imbalance (the Nasdaq/NYSE imbalance feed) is **not on disk**.
What is on disk, and what hyp-000076 tested, is a price+volume **proxy**:
sign(Close−Open)×Volume summed over 09:30–09:59 one-minute bars. The proxy is the
thing that already failed. The genuine construction is exactly the "genuinely new
data source" the vein-closure rule names as the one admissible route back.
**Trigger:** real opening-auction imbalance data. Until it exists, this family
stays closed.

## 5. What was NOT done

No spec, no sha256 freeze, no screen, no salvage (salvage is gate-blocked this
session and a partial salvage is not permitted). Nothing was papered and no
strategy was registered. The overlap script is a measurement tool, not a
strategy: it is not frozen, not registered and not in any paper path.
