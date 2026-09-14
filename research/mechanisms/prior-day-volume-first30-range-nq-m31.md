# Mechanism — Prior-day volume vs expected → first-30-minute range, NQ (M31, observatory channel, from the Idea Factory queue)

Written: 2026-09-13, ~7:17 pm CT (7:00 pm test cycle, Sourcing Rule v3). PRE-REGISTERED; footprint
from research/observatory/idea-factory-2026-09-13.md (`volume_vs_expected → range`, HIGH/first30
z ≈ 8.4, n=385). Results of any REGISTERED test: NOT seen.
LEARN consulted by name: `volume_vs_expected` was tested once as a directional/return-persistence
conditioner (Scan 002 cells, closed; hyp-000043 volume level alone, REJECTED; M18 volume-conditioned
reversal, CLOSED P1_PASS_P2_FAIL). None of those tested next-morning RANGE. This is a size claim on a
different outcome and does not reopen the direction family.

## 1. The claim
Sessions following a HIGH-tercile prior-day volume (prior-day RTH volume / its trailing-20d
expectation) show a credibly LARGER first-30-minute range (09:30–10:00 ET, in ATR14 units) than
sessions following LOW-tercile volume. State known at the prior close; outcome starts 09:30.

## 2. Who is on the other side
Institutions completing multi-day executions. Unusually heavy volume yesterday means large orders
were being worked; whatever was not finished is worked at today's open, when liquidity is deepest,
and the overnight re-pricing of that information is resolved in the first half-hour. Participant:
institutional execution desks (VWAP/POV algorithms) — named, mechanical, observable through
volume.

## 3. Why this is not the overfitting trap
One state (already frozen, prior-day, no lookahead), one tercile cut on Discovery, one outcome
window, one direction. Other windows for this state in the queue are not claimed.

## 4. Testable predictions
P1 (GATING). HIGH−LOW first-30 range ratio difference credibly > 0.
P2 (reported). The effect is NOT explained by prior-day RANGE (F-048): residualized on the prior-day
   range tercile, ≥50% retained — heavy volume is not just a wide day restated.
P3 (reported). First-30 MFE/MAE from the open both larger on HIGH (excursion claim).

## 5. What would falsify this
(a) P1 fails → closes. (b) P1 passes, P2 fails → duplicate of F-048, closes as duplicate.
(c) Volume data coverage: `volume_vs_expected` is available on 385 of ~1,700 Discovery days per the
    queue (volume series gaps) — if usable n per tercile < 120, disclose as underpowered.

## 6. Information gain and edge potential
Gain: moderate–high — a pre-open input to the Risk/State Engine that is NOT a range measure (the
first non-volatility input), which is exactly what Portfolio's overlap warning asks for. Edge:
first-30 stop distance for the B3 placeholder's opening range; permission flag on very heavy days.

## 7. Resurrection ruling
NEW as a range claim. Not hyp-000043 / M18 / Scan 002 (all direction). Attempt 1 of 2.

## 8. Instrument-choice gate
NQ only; prior-close state; same-session outcome; magnitude; NULL = unconditional first-30 ratio.

## 9. Frozen scope
ONE scan, Discovery slice, daily aggregation. Cells: (1) HIGH−LOW first-30 range ratio difference,
block CI <== GATING P1; (2) P1 residualized on F-048 tercile (P2); (3) HIGH−LOW first-30 MFE diff;
(4) HIGH−LOW first-30 MAE diff (P3); (5) unconditional reference; (6) volume-coverage disclosure.
Block=10, N_BOOT=3000, SEED=20260913, 90% CI. One shot.

## 10. Prediction status
Untested. DRAWABLE.
