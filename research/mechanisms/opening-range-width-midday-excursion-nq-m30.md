# Mechanism — Opening-range width → midday range and excursion, NQ (M30, observatory channel, from the Idea Factory queue)

Written: 2026-09-13, ~7:15 pm CT (7:00 pm test cycle, Sourcing Rule v3). PRE-REGISTERED as a claim;
the descriptive footprint that pointed here is research/observatory/idea-factory-2026-09-13.md
(`opening_range_vs_atr → range/mfe/mae`, strongest family, z ≈ 11 HIGH/midday). Results of any
REGISTERED test: NOT seen. The queue entry is descriptive and is not evidence.
LEARN consulted by name: the state variable `opening_range_vs_atr` has never been the conditioning
variable of a registered scan (Scan 002 used it only as a same-day descriptor, no claim); the
initial-balance breakout family (exp-028/031) tested DIRECTION after the first 30 minutes and closed
null — this is a SIZE claim, not a direction claim, and does not reopen that family.

## 1. The claim
Sessions whose first 30 minutes (09:30–10:00 ET) span a HIGH-tercile range in ATR14 units show a
credibly LARGER midday range (11:30–13:30 ET) and larger maximum excursions from the midday open in
both directions than LOW-tercile sessions. Known at 10:00 ET; outcome starts 11:30 ET (timing rule
satisfied by 90 minutes).

## 2. Who is on the other side
Intraday liquidity providers and the systematic "opening drive" desks. A wide first half-hour means
the open did not find balance: inventory was transferred at a range of prices, dealers are carrying
imbalanced books into the quietest part of the day, and their hedging (and the momentum funds that
key off the opening range) keeps repricing through midday instead of resting. Participant:
market-maker inventory management. Named, observable only through this proxy.

## 3. Why this is not the overfitting trap
One state (already frozen in market_state_primitives), one tercile cut fixed on Discovery, one
outcome window pre-declared (midday), one direction of effect (larger). The Idea Factory's other
windows for this state (morning, afternoon, last hour) are NOT part of this claim; reported only.

## 4. Testable predictions
P1 (GATING). HIGH-tercile opening range → midday range ratio (midday range / trailing-20d mean
   midday range) credibly ABOVE the LOW-tercile ratio; block CI on the HIGH−LOW difference > 0.
P2 (reported). HIGH-tercile → larger midday MFE and MAE from the midday open (both signs) — the
   excursion claim, which is what an exit rule would use.
P3 (reported). The effect survives residualizing on prior-day range tercile (F-048): the opening
   range is not merely yesterday's volatility restated. ≥50% retained.

## 5. What would falsify this
(a) P1 fails → closes; the queue footprint was a Discovery-slice artefact or already captured by
    F-048. (b) P1 passes, P3 fails → duplicate of F-048; closes as duplicate (closure form status
    "duplicate"). (c) Thin-sample: not a concern (~560 days per tercile).

## 6. Information gain and edge potential
Gain: HIGH — a fifth candidate input to the Risk/State Engine that is known at 10:00 ET, i.e. an
INTRADAY update between the pre-open number and the 14:00 afternoon update. Edge: sizing/stop
distance for anything entered after 10:00, including the B3 placeholder entry, whose breakout window
starts exactly then. This is the first queue family that plugs directly into the bot.

## 7. Resurrection ruling
NEW. Not exp-028/031 (direction after the initial balance; closed). Not F-048 (prior-DAY range; P3
tests the distinction). Not M9. Attempt 1 of 2.

## 8. Instrument-choice gate
NQ only; 10:00 ET state; same-session outcome from 11:30; magnitude not direction; NULL = unconditional
midday range ratio. TWO NULLS rule not triggered (no directional or cross-index claim).

## 9. Frozen scope
ONE scan, Discovery slice, daily aggregation (scan_027/030 pattern). Cells: (1) HIGH−LOW midday range
ratio difference, block CI  <== GATING P1; (2) HIGH−LOW midday MFE difference (P2); (3) HIGH−LOW midday
MAE difference (P2); (4) P1 residualized on F-048 tercile (P3); (5) unconditional midday ratio
reference; (6) alignment/coverage disclosure. Block=10, N_BOOT=3000, SEED=20260913, 90% CI.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
P1–P3 untested. DRAWABLE.
