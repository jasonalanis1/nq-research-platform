# hyp-000164 — Directional Lane Trial 2: US daylight-saving-time transition anomaly, NQ (M32)

Written: 2026-09-16, ~9:00 am CT (scheduled cycle).
Mechanism doc: research/mechanisms/dst-anomaly-nq-m32.md (written BEFORE this scan).
Scan: src/market_behavior_discovery_scan_038.py (Scan 038).
Ledger row: research/ledger/hypotheses.jsonl, hyp-000164.
Directional lane: research/ledger/directional_lane.json, trial 2 of 20.

## Claim tested
P1 (GATING). NQ's cumulative RTH return over the calendar week (5
sessions) following a US daylight-saving-time transition (spring-
forward, 2nd Sunday of March; fall-back, 1st Sunday of November) is
credibly NEGATIVE relative to NQ's own unconditional 5-session rolling
return. Source: Kamstra, Kramer and Levi (2000, *American Economic
Review*, "Losing Sleep at the Market: The Daylight Saving Anomaly").

## Result
**P1 FAIL — clean null, and wrong-signed against the predicted
direction.**

- Cell 1 (GATING): transition-week cumulative return +65.85 vs
  unconditional 5-session baseline +14.09, diff **+51.75 pts**, 90%
  block-bootstrap CI **(-13.09, +73.88)** — includes zero, and even
  its point estimate runs POSITIVE, opposite the predicted NEGATIVE
  direction. n=13 transition weeks, clears the pre-registered 12-week
  thin-sample floor (not a thin-sample disclosure).
- Cell 2 (P2, literature-fidelity, reported, moot given P1 fail):
  transition-Monday-only return +19.38 vs NQ's own unconditional daily
  RTH return +2.72, diff **+16.67 pts**, CI **(+5.57, +25.22)** —
  credible, but POSITIVE. The literature predicts the transition Monday
  is the anomaly's sharpest negative leg; NQ shows the opposite sign.
- Cell 3a (P3, descriptive): spring-transition weeks, diff +21.51, CI
  (-52.73, +27.71) — null.
- Cell 3b (P3, descriptive): fall-transition weeks, diff +87.03, CI
  (+47.99, +95.89) — credible POSITIVE, again opposite the literature's
  (stronger) predicted spring effect.
- Cell 4 (NULL 1 reference): unconditional 5-session rolling return
  mean +14.09 pts, n=1682 overlapping windows.
- Cell 5 (thin-sample disclosure): n=13 transition weeks, floor=12,
  NOT thin.

## Interpretation
The pre-registered gating prediction fails outright: the CI on the
transition-week effect includes zero, so there is no credible effect
either way at the gating stage. Beyond that, wherever NQ does show a
statistically credible move around DST transitions in this Discovery
slice (the Monday-only cell, and the fall-weeks cell), the sign runs
positive — the reverse of the sleep-disruption/reduced-risk-tolerance
mechanism the literature describes. This is not "underpowered, retest
later" territory (n=13 clears the pre-registered floor); it is a
genuinely negative result on the mechanism as specified. The daylight-
saving anomaly, as tested here, does not transfer to NQ index futures
at this data ceiling.

Per this project's own culture, a correctly-specified clean null is a
legitimate, reportable outcome, not a failure. One Discovery-stage shot
only this cycle — no Statistical/Director/Gate/Validation run on
hyp-000164 (pipeline sweep rule: one stage per cycle at the daytime
cadence for a Discovery result that failed its gating cell; nothing
further is owed on a P1 FAIL).

## Disposition
- hyp-000164: REJECTED.
- Entry 62 / M32: CLOSED (research/idea_inventory.md, research/market_structure_map.md).
- Directional lane: used 1 -> 2 of 20; 18 trials remain.
- Shelf: falls back to 0/3 DRAWABLE; sourcing owed again next cycle
  (magnitude stays frozen per REFOCUS s.3).
