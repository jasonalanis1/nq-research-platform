# Staff meeting — the per-trade swing band (September 14th, ~8:00 pm CT)

Convened by the Research Director at Jason's request. Subject: the execution record
cannot start because every B7 session is blocked by the $50–150 per-trade swing band.
One disposition comes out of this, with each agent's position recorded so a later
session can see the disagreement and not relitigate it blind.

## CORRECTION FIRST — the premise as stated an hour ago was partly wrong

The evening report said the band was "written in fixed dollars" that had gone stale
as NQ rose from ~4,500 to ~29,500. **The arithmetic is right; the origin is wrong.**
The $50–150 band and the $300 budget are not a decayed 2018 rule — they are **Jason's
own stated risk appetite from the September 11th upgrade brief**, set at today's price
level, three days ago. The 2018 comparison is still informative (it shows what an
ordinary opening-range stop cost then), but the honest framing is:

**Jason's per-trade appetite and the placeholder strategy's natural stop size do not
fit each other at today's index level.** Nothing decayed. Two deliberate choices
collide.

## The facts, checked

- MNQ is $2 per point. $50–150 per trade is therefore a **25–75 point stop**.
  At NQ ≈ 29,500 that is a 0.08–0.25% move — scalp scale.
- B3's stop is the opposite side of the 30-minute opening range, unconditioned
  (`base_entry_b3.py`). The four real sessions had ranges of 136–234 points →
  $272–$468. Across 2,721 historical signals, **2.4% of 2026 signals fit the band.**
- B2 (`risk_state_engine.py`) computes its own stop — 0.5 × expected RTH range —
  which at today's ranges is also ~150–200 points. **B7 does not use B2's stop; it
  uses B3's.** Noted as an architecture fact, not fixed here.
- Every research state the project owns is daily-scale (ATR14, prior-day range,
  overnight coil, VXN). None of it informs a 25–75 point stop.
- The 0.75-point cost assumption is 0.5% of a 150-point stop and **3% of a 25-point
  stop** — inside the 5% screening rule, but six times more exposed to it.
- **We are in paper.** The $300 budget is currently a kill-switch threshold, not money
  at risk. At research-scale stops, one losing trade ($272–$468) exceeds it, so the
  paper record would stop at the first loss even if the band were lifted.
- No trade outcome has ever been observed through the order path (0 orders ever), so
  no change proposed here can be a response to results. That matters for the Gate.

## Positions

**Operations.** The mechanics are trivial either way; the choice is not mechanical.
Whatever is chosen must be written down before the next session is scored, and the
four blocked rows stay in the log as history. No B7 re-anchor is needed — the anchor
governs which sessions are processed, not how they are gated.

**Statistical.** B3 has no claimed edge; it is a placeholder for measuring execution.
Slippage — the thing the record exists to measure — does not depend on the budget
number. The kill switches do. So a paper budget that reflects the strategy's actual
stop size measures execution honestly; a paper budget that trips on the first loss
measures nothing.

**Monetization.** Shrinking the stop to fit the dollars is the one option with a
hidden cost: it moves the strategy toward the scale where the fixed cost dominates,
and the project's screening rule exists precisely to keep candidates away from there.
A $50–150 trade on NQ at 29,500 is a scalp, and the cost model was not built for
scalps.

**Integrity Gate.** No veto, with three conditions. (1) The change must be justified by
an instrument-level fact, not by the blocked signals — and it is: the band-fit rate
tracks index level year by year, independent of any outcome. (2) Pre-register the new
rule before any further session is scored; date it; no retroactive re-scoring of the
four blocked sessions. (3) **Whatever paper budget is used, the paper→live comparison
must be disclosed as a comparison of execution, not of kill-switch behaviour** — if
live runs on Jason's dollars and paper ran on scaled ones, the two records answer
different questions about drawdown and that must be said in every report that cites
both.

**Research Director.** The band and budget are Jason's live appetite and belong to
B8, which is his alone. They should not be the thing that stops a paper record from
existing. Denominate the paper capital model in **R** — one R is whatever the
strategy's own stop is worth in dollars — and keep every ratio Jason set: his $300
budget at a $50–150 trade is two to six R; his $500 is three to ten. Express those as
R and the model scales with any strategy, including the one that eventually earns
B8. The dollar band moves to B8 as the live constraint on what one R may cost.

## Disposition: **MODIFY** — one change

**Denominate the paper capital model in R, not dollars. Move the dollar band to B8.**

Concretely, pre-registered before the next scored session:

- `CapitalConfig` gains `paper_mode` with budgets in R: starting budget **4R**
  (the midpoint of Jason's 2–6R), raised to **6R** after the 20-trade record, trailing
  floor 4R, give-back one-third of peak — every ratio he set, unchanged.
- `swing_fits_budget` in paper mode checks that 1R is **positive and finite**, nothing
  else. The $50–150 dollar check becomes a **live-only** rule, applied at B8, where
  Jason sets the real numbers for the real strategy.
- B3's stop is untouched. B2-vs-B3 stop ownership is logged as an open architecture
  item, not fixed under this disposition.
- Every Execution block that reports paper drawdown states the R-denomination and
  the current dollar value of 1R, so nobody reads a paper drawdown as live dollars.

## What this asks of Jason

**Nothing about real money — that stays exactly where it was, in the brief, for B8.**
One yes/no: is he comfortable with the paper record running at the strategy's own
stop size (currently $270–$470 per trade, in paper), with his $50–150 appetite
applied when — and only when — real dollars are on the line? A "no" is a real answer:
it means the bot must trade a scalp-scale strategy the research does not currently
support, and the execution record waits for one.

Recorded, not applied. The code changes above happen only after his answer.
