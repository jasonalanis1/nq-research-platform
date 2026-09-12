# Scan 005 — Closure, Candidate Triage, and Zero-Survivor Staff Meeting

Written 2026-09-10, automated session. Scan run:
src/market_behavior_discovery_scan_005.py, frozen scoping:
research/studies/scan-005-scoping-2026-09-10.md. Results:
data/market_behavior_discovery_scan_005_results.json.

## Result summary

24 cells scanned (2 variables x 3 buckets x 4 horizons). 5 cleared the
raw credible-vs-zero + cost-floor screen (same screening convention as
Scans 001-004, for comparability). Sanity-checked against a
computation bug (bucket edges, sizes, z-score distribution all
reasonable — not a bug): results printed in the run output.

**D1 (nq_zn_divergence): 0/12 cells cleared even the raw screen.**
Complete null.

**D2 (nq_vxn_divergence): 5/12 cleared the raw screen, but checked
against the PRE-REGISTERED monotonic-reversion shape (LOW positive,
HIGH negative) — the actual falsifiable claim this scan exists to
test:**
    h=1d  MID  +7.72 vs baseline   (shape n/a — MID not predicted either sign)
    h=2d  MID +11.21 vs baseline   (shape n/a)
    h=3d  MID +11.01 vs baseline   (shape n/a)
    h=5d  MID  +8.12 vs baseline, HIGH -9.48 vs baseline — shape_match=True
LOW bucket never independently cleared the credible-vs-zero screen at
any horizon. The pre-registered prediction required LOW positive AND
HIGH negative, both credible; only HIGH-at-5d delivers its half, LOW
never does. **The pre-registered mechanism claim is NOT confirmed.**

**The unpredicted pattern:** MID (near-zero divergence, i.e. NQ moving
roughly as its trailing co-movement with VXN would imply) shows a
positive, credible, cost-floor-clearing excess return at every one of
the 4 horizons tested. This is a real pattern in the data (sanity-
checked), but it was NOT what this scan was built to test, and it
carries NO mechanism claim — pursuing it now would fail the STANDING
TEST's own bar ("would we have proposed this before seeing any data" —
no, we would not have; this was found only after looking) and would be
exactly the COSMETIC-NOVELTY / LOTTERY-TICKET pattern the Idea
Inventory's entry bar exists to block. NOT advanced. Logged below for
LEARN and the Idea Inventory instead, to be picked up only if a future
session can state an actual pre-registered mechanism for it before
looking at this data again.

## Candidate Triage

D1 (nq_zn_divergence): GRADE F. Complete null, closes with no
hypothesis ID spent (none was ever at risk — Discovery-Engine scans
don't log to the ledger by convention, matching Scans 001-004).
D2 (nq_vxn_divergence), pre-registered reversion claim: GRADE D. Thin,
one-sided partial match (HIGH-at-5d only), LOW side never confirms —
not enough to advance to Mechanism. Closes.
D2's unpredicted MID-bucket pattern: NOT GRADED — not a candidate,
a raw observation. Logged to LEARN/KNOWN UNEXPLORED, not the ledger.

## Zero-survivor scan — MANDATORY STAFF MEETING (AMENDMENT v2.1 Rule 3c)

Trigger: Scan 005 closes with zero survivors on its own pre-registered
terms (D1 complete null, D2's actual falsifiable claim not confirmed).
Convened per Rule 3 — Director chairs, every agent's position recorded.

**LEARN:** cross-instrument divergence, AS A REVERSION STORY, is now a
KNOWN FAILED direction for NQ-ZN entirely, and thin/unconfirmed for
NQ-VXN. Record precisely what failed (residual-from-rolling-beta,
z-scored, monotonic reversion prediction) so a future session doesn't
re-test the same construction under a new name. The MID-bucket
continuation pattern is KNOWN UNEXPLORED, explicitly flagged as
requiring its own fresh mechanism claim, not a re-cut of this one.

**DISCOVERY:** the short-horizon re-expression direction (option A from
the original Scan 005 scoping choice, set aside this round) remains
available and untried. Also available: a continuation-framed (not
reversion-framed) divergence mechanism, IF a real mechanism claim can
be written for why near-zero cross-asset divergence would predict
NQ continuation — genuinely not obvious, needs real thought, not a
same-session rationalization of what the numbers already showed.

**INTEGRITY GATE:** no veto exercised — nothing here is being
advanced, so there is nothing to gate. Explicitly notes the discipline
that WAS exercised: the MID-bucket pattern was found and NOT chased in
the same session, which is the guard working as designed, not a missed
opportunity.

**STATISTICAL:** this scan adds 24 Discovery-stage trials project-wide
(SCAN_REGISTRY needs a scan_005_2026-09-10 entry, 0 promoted — done
below). No candidate is currently mid-pipeline, so no in-flight CI
gets tightened by this addition.

**MECHANISM:** the honest reading of the MID-bucket finding, if it's
ever pursued: "NQ tracking its usual cross-asset relationships more
closely than usual" would need a claim for why that predicts
CONTINUATION rather than nothing — e.g. an "orderly, low-dispersion
regime" story (calm cross-asset relationships coincide with trending,
low-surprise markets) is a plausible candidate claim, but it is a
DIFFERENT mechanism from anything scanned here and must be pre-
registered fresh, with its own falsifiable prediction, before any
further data is looked at.

**DIRECTOR — disposition: PIVOT.** Cross-instrument divergence-as-
REVERSION is closed, this scan's specific construction is not
reusable, and nothing from Scan 005 advances. Pivoting Scan 006 (next
Discovery-scope work) to draw from the Idea Inventory once one exists
(TOP UP, below) rather than immediately re-attempting direction A from
this scoping round under load — consistent with AMENDMENT v2.3's whole
point (vet in slack, don't generate under the pressure of "the last
scan just came back empty").

## SCAN_REGISTRY update (project_wide_multiplicity.py)

Added below: scan_005_2026-09-10, cells_scanned=24, promoted=[].
