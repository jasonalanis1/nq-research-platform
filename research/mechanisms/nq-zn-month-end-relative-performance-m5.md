# Mechanism — nq_minus_zn_mtd (M5, month-end relative-performance rebalancing)

Written: September 11th, 11:00 pm CT (2026-09-12 04:00 UTC)  ·  Pre-registered
Results seen before writing: no — this doc precedes Scan 015 (not yet written or run).

## 1. The claim
Balanced/pension mandates (typically 60/40 equity/bond, rebalanced on a calendar
schedule) measure their equity-vs-bond drift month to date. When NQ has
meaningfully outrun ZN over the month (equity leg has run ahead of the bond
leg), rebalancers are forced sellers of equity exposure and buyers of duration
in the final sessions of the month to bring the mix back to target — this
selling pressure should show up as weaker NQ returns in the last two sessions
of the month for the HIGH tercile of NQ-minus-ZN month-to-date outperformance,
with the flow reversing or fading out in the first two sessions of the
following month. This is a calendar-driven, price-insensitive flow claim, not
a momentum or sentiment claim.

## 2. Who is on the other side
Counterparty: mandated rebalancers themselves (the flow is being described,
not a speculative counterparty taking the other side of a real information
edge) — they execute regardless of price because the calendar, not a market
view, triggers the trade. The true counterparty accommodating the flow is
whichever liquidity provider or discretionary desk is willing to take the
other side of price-insensitive month-end flow, priced to compensate for
that inventory risk over 2 sessions.

## 3. Testable predictions
P1. In the HIGH tercile of nq_minus_zn_mtd (equity has most outrun bonds),
the gating window (close of session T-3 -> close of last session of month)
shows a more negative NQ return than the LOW tercile.
P2. The reported window (first 2 sessions of the following month) shows at
least partial reversal/fade of the gating-window effect in the HIGH tercile
relative to the LOW tercile — i.e., the flow that pushed price down into
month-end partially unwinds once the rebalancing trade is done.

## 4. What would falsify this
Gating-window return in the HIGH tercile not credibly more negative than the
LOW tercile (i.e., no relationship between relative equity outperformance and
late-month equity weakness), OR a HIGH-tercile gating effect that does NOT
partially reverse in the reported window (a level shift rather than a
temporary flow would argue against a forced-rebalancing story specifically,
though it would not by itself prove no effect exists at all).

## 5. Prediction status
P1 — REFUTED (or underpowered; cannot distinguish, per the pre-registered
power caveat below) — Scan 015 (n=79 usable month-ends, larger than the ~45
estimated at scoping): HIGH tercile gating return -0.0405 ATR, ci_90
[-0.4063, +0.3185] (null, not credibly negative); LOW tercile +0.1960 ATR,
ci_90 [-0.1442, +0.5554] (null); no monotonic gradient across terciles (MID
was the only credible cell, at -0.3988, and in the predicted direction, but
MID being the sole credible cell with HIGH and LOW both null is not a
gradient the mechanism predicts). P1_FAIL.
P2 — not tested — pre-registered scope: the reported/reversal window is
read only if the gating cell (P1) passes; it did not.

## 6. Verdict
REFUTED at Discovery, clean null (not merely a thin-sample non-result: n=79
is nearly double the ~45 originally estimated, and still no credible,
gradient-consistent HIGH-tercile effect emerged). Attempt 1 of 2 on this
mechanism closed. No hypothesis id spent (Discovery-stage scan did not clear
the credible+cost-floor screen). One attempt remains open per the 2-attempt
limit; LEARN entry filed under FAILED (clean null, not a named failure
mode) rather than re-scoping immediately.
