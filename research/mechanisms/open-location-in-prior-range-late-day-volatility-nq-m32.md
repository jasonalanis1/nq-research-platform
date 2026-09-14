# Mechanism — Open's location in the prior day's range → later-session range, NQ (M32, observatory channel, from the Idea Factory queue)

Written: 2026-09-14, ~9:25 am CT (9:00 am scheduled cycle, Sourcing Rule v3).
PRE-REGISTERED as a claim; the descriptive footprint that pointed here is
`research/observatory/idea-factory-2026-09-13.md` (`location_in_range → range`,
9 cells, strongest |z| 6.8 at LOW/last_hour). Results of any REGISTERED test:
NOT seen. The queue entry is descriptive and is not evidence.

LEARN consulted by name: `location_in_range` has never been the conditioning
variable of a registered scan. It is distinct from F-048 (prior-day RANGE SIZE —
this is about WHERE the open sits inside that range, not how wide it was) and
from M30/hyp-000162 (opening-range WIDTH, known at 10:00 — this is known at
09:30 and uses the prior day's range, not the first 30 minutes).

## 1. The claim
Sessions that open in the LOW tercile of the prior day's range (near its bottom)
show a credibly LARGER last-hour range (15:00–16:00 ET, as a ratio to the
trailing-20d mean last-hour range) than sessions opening in the HIGH tercile.
Known at 09:30; outcome starts 15:00 (timing rule satisfied by 5.5 hours).

The queue footprint is monotone across every window it covers — LOW is above
all-days in morning, midday, afternoon, last_hour and next_rth; HIGH is below in
all of them — which is why the direction is pre-registered rather than fitted.

## 2. Who is on the other side
This is the volatility asymmetry (the "leverage effect"): index volatility rises
after declines and compresses after advances. Opening near the bottom of
yesterday's range means the overnight session has already moved price against the
prior day's balance. The participants on the other side are (a) index option
dealers, who are structurally short downside convexity and must hedge more
actively as spot falls, and (b) risk-targeting funds — vol-control, risk-parity —
whose mandated exposure falls as realized volatility rises, forcing sales into
weakness that arrive late in the session when rebalancing is executed. Both
mechanisms concentrate into the close, which is why the footprint is strongest in
the last hour rather than the morning. Participant: dealer hedging plus mandated
risk-target rebalancing. Named, observable only through this proxy.

## 3. Why this is not the overfitting trap
One state, already frozen in `market_state_primitives`. One tercile cut fixed on
Discovery. One outcome window pre-declared (last hour) as the gating test, chosen
because it is where the stated mechanism predicts the effect should be largest —
not because it had the largest z (it did, but the mechanism is why it is gating).
The other windows are reported, not claimed. One direction of effect (LOW > HIGH),
fixed in advance from the monotone footprint.

## 4. Testable predictions
- **P1 (GATING).** LOW-tercile minus HIGH-tercile last-hour range ratio, block CI
  on the difference > 0.
- **P2 (reported).** The same difference across morning, midday and afternoon. The
  mechanism predicts it strengthens toward the close; a flat or inverted profile
  across the day is evidence against the stated mechanism even if P1 passes.
- **P3 (CONTROL, GATING).** The effect survives residualizing on the overnight
  gap (`gap_vs_atr` tercile): ≥50% of the P1 difference retained within gap
  strata. "Opened low in yesterday's range" is close to "gapped down", and
  volatility asymmetry after declines is already a known effect — if the whole
  thing is the gap, this is a duplicate wearing a new name.
- **P4 (CONTROL, GATING — added from what hyp-000162 cost us).** The
  shifted-signal placebo must NOT reproduce the effect: *yesterday's*
  `location_in_range` must do materially less work than today's, per
  `src/integrity_checks.py`'s placebo check with its persistence guard. This
  cycle's own draw (hyp-000162) passed every registered prediction and then
  failed exactly this, because a state that persists day to day can look like a
  same-day signal. Pre-registering it here means the answer is known before the
  Gate rather than after.

## 5. What would falsify this
(a) P1 fails → closes; the queue footprint was a Discovery-slice artefact.
(b) P1 passes, P3 fails → duplicate of the gap/leverage effect; closes as
    `duplicate`. (c) P1 passes, P4 fails → the signal is a marker of a
    multi-day volatility regime rather than an open-location effect; closes as
    `valid-but-non-actionable` unless the Director scopes the separation test.
(d) P2 inverted → the stated mechanism is wrong even if the association is real;
    reported to the Gate as a mechanism failure, not a statistical one.
(e) Thin sample: not a concern (~540 days per tercile).

## 6. Information gain and edge potential
Gain: HIGH — a sizing input known at **09:30**, half an hour earlier than M30's,
and the earliest intraday update the Risk/State Engine could act on. Edge:
stop/target distance for anything held into the close, and a direct input to the
afternoon update B2 already exposes separately. Stack A established B2 needs
sizing material; this is sizing material.

Honest caveat on novelty: the leverage effect is among the most documented facts
in equity-index volatility. The novel part is not "volatility rises after
declines" — it is whether the OPEN'S LOCATION IN THE PRIOR RANGE is a usable,
already-known-at-09:30 proxy for it that survives controlling for the gap itself.
P3 is what decides that, and P3 is gating for exactly this reason.

## 7. Resurrection ruling
NEW. Not F-048 (prior-day range SIZE). Not M30/hyp-000162 (opening-range WIDTH,
known at 10:00). Not the closed initial-balance breakout family (direction, not
size). Attempt 1 of 2.

## 8. Instrument-choice gate
NQ only; 09:30 ET state; same-session outcome from 15:00; magnitude not
direction; NULL = unconditional last-hour range ratio. TWO NULLS rule not
triggered (no directional or cross-index claim).

## 9. Frozen scope
ONE scan, Discovery slice, daily aggregation (scan_036 pattern). Cells:
(1) LOW−HIGH last-hour range-ratio difference, block CI **← GATING P1**;
(2) the same difference for morning, midday, afternoon (P2, reported, 3 cells);
(3) P1 stratified on the `gap_vs_atr` tercile + share retained **← GATING P3**;
(4) unconditional last-hour range-ratio reference;
(5) alignment/coverage disclosure.
Then `src/integrity_checks.py` on the occurrence file **before the Gate** — P4.
Block=10, N_BOOT=3000, SEED=20260914, 90% CI. One shot. No new cells, no
retuning after seeing results.

## 10. Prediction status
P1–P4 untested. DRAWABLE.
