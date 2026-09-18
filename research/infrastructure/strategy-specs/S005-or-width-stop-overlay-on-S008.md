# S005 — Opening-range width (hyp-000162) as a STOP-SIZING OVERLAY on S008

Frozen 2026-09-17 (7:00 pm cycle). Module:
`src/strategy_s005_or_width_stop_overlay.py`. Host: S008, late-day
constant-leverage rebalance continuation, frozen 2026-09-16.

## What this is, and what it is NOT

hyp-000162 (opening-range width → midday range) is **VALIDATED_NOT_PROMOTED**.
`research/studies/hyp162-portfolio-2026-09-14.md`: joint residual retention
~17.7% (90% CI −14.3% to +15.1%) against a 50% bar, and adding the 10:00 update
to the existing forecast stack made that forecast **very slightly worse**
(MAE 0.3252 → 0.3256). It is therefore **never a standalone strategy** and this
spec does not make it one.

The one narrow, pre-specified question this spec asks:

> Does using opening-range width to set the stop distance and target on an
> **already-frozen** strategy improve that strategy's screen result?

That is a different question from the Portfolio one. Portfolio asked whether the
fact adds information to a *forecast of the midday range*. This asks whether the
fact, used as a *risk-sizing input* on a live entry rule, improves a *traded*
result. A fact can be redundant for forecasting and still be useful for sizing,
because sizing is a non-linear transform of the forecast (stop placement decides
which trades survive noise), and that is the only reason this is worth one screen.

## Why S008 is the host

S008 is the **best-performing frozen strategy** and, decisively, **the only one
in PAPER that is not SLOW** (screen rate 0.3351 trades/session → 42.2 projected
in six months, against 40), so a real improvement would actually reach a 40-trade
judgment on a working clock. It is also the natural host mechanically: S008
already sizes its stop off an **intraday range** (`0.50 × the 09:30–15:00
range`), so an opening-range-width input substitutes directly for the exact
quantity the overlay would change. S002 is higher-frequency, but it is SLOW and
it is an **overnight carry** whose risk is not sized off an intraday range at
all — there is nothing for this fact to inform there.

## The overlay — the ONLY thing that changes

Everything in S008 is untouched: the large-move condition, the direction, the
15:00 ET decision, the next-bar-open entry, the 15:55 ET time exit, 1 micro MNQ,
1.5R target multiple, and the whole bookkeeping path. S008's frozen spec and
module are **not edited** (directive s.13); this module imports S008 read-only.

Known at **10:00 ET**, from that session's own RTH bars:

    ORW      = High(09:30..10:00) - Low(09:30..10:00)
    ORW_med  = median(ORW) over the trailing 20 RTH sessions, STRICTLY EARLIER
    k        = clip(ORW / ORW_med, 0.75, 1.35)

and the host's risk is rescaled:

    risk'    = k × 0.50 × RNG          (S008: risk = 0.50 × RNG)
    target'  = entry ± 1.50 × risk'    (the 1.5R multiple is unchanged)

Direction of the effect is the validated fact's own: a **wide** opening half-hour
forecasts a **wider** midday/afternoon, so the stop is widened (k > 1) to avoid
being shaken out by the expected noise, and tightened (k < 1) on a narrow open.
The clip band [0.75, 1.35] is a sanity bound fixed here, before any result, not
a tuned parameter: it exists so a single freak opening range cannot set a stop
several times the host's.

If ORW or its trailing median is unavailable for a session (fragmentary bars, no
20-session history), **k = 1.0** and the trade is exactly the host's. The overlay
never creates, suppresses or re-directs a trade: trade count and entry price are
identical to the host's by construction, and only the stop and target move.

**No look-ahead.** ORW is measured at 10:00 ET, five hours before the host's
15:00 decision; the trailing median uses sessions strictly earlier.

## Costs — `src/cost_model.py`, all four combinations (ASSUMED, s.11)

    MNQ market  $2.60 = 1.300 pt   ← decision basis
    MNQ limit   $2.10 = 1.050 pt   OPTIMISTIC UPPER BOUND
    NQ  market  $14.90 = 0.745 pt
    NQ  limit   $9.90 = 0.495 pt   OPTIMISTIC UPPER BOUND

Every limit figure assumes a resting limit order always fills at its price. Real
ones miss fills and are adversely selected; the screen cannot model a non-fill.

**Amendment 2 pre-freeze gate, applied to the overlaid strategy as a whole.**
The host grosses **2.6851 pt per trade**, against the 1.300 pt MNQ market cost.
The overlay rescales risk by at most ±35% and does not change entries, so the
overlaid strategy's expected per-trade edge remains far above the per-trade cost
itself. `cost_model.specify_gate` passes; it goes to SCREEN.

## Where this should fail (its Salvage menu later, s.7)

1. The Portfolio result is simply right and the fact carries nothing the host's
   own 09:30–15:00 range has not already said — RNG and ORW are both range
   measures of the same session, so the scaler is close to noise on a quantity
   the host already uses.
2. Widening the stop on wide-open days widens losses 1:1 while the 1.5R target
   widens too — a symmetric rescale is a **no-op in R** and only changes outcomes
   through which trades touch a level first. If first-touch ordering is
   insensitive to the stop distance in this band, the result is a wash.
3. The clip band binds on most days, flattening k toward 1.

## Decision rule, fixed before the screen

Screened host-with-overlay against host-alone on the **same Discovery slice**,
all four cost combinations, decision basis MNQ market.

* **Improves materially** → register, mark `BLOCKED_PENDING_REFERENCE_DATA` for
  paper entry (scoring is gated), report the SLOW projection.
* **Changes nothing / makes it worse** → record the null plainly, S005 → LEARN.

A null is a **good result** here: it closes a question the project has carried
since the Portfolio stage and confirms that finding from a different angle.
**No variant hunt.** One screen, one number, one decision — searching for a
k-band or a tercile split that looks better is exactly the ex-post slicing the
salvage rule forbids.
