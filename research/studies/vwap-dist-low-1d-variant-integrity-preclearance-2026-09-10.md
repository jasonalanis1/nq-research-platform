# Integrity Gate Pre-Clearance -- vwap_dist_vs_atr LOW, 1-Day Variant

Written 2026-09-10, automated work session. Governance ruling only --
no result has been looked at. Per NEXT_UP.md's queued item (Jason,
2026-09-10), slice 1a: LEARN consultation + Integrity Gate pre-
clearance BEFORE any spec is written or any result examined.

## LEARN consultation (by name, per Rule 5)

KNOWN TRUE: vwap_dist_vs_atr/LOW is a validated Discovery-Engine
candidate (H118, hyp-000121, Scan 002). Its mechanism doc
(research/mechanisms/h118-vwap-dist-low.md), written 2026-09-10,
already examined the SAME Scan 002 Discovery numbers across all four
horizons scanned (1d/3d/5d/10d) as prediction P2 ("front-loaded
absorption") and found: two-thirds of the 10-day effect lands within
day 1, then goes flat through day 5, then jumps again 5->10. That
finding already exists on disk; this variant does not discover it, it
proposes to TEST it prospectively on data the 1-day cell itself has
never been evaluated against out of sample.

KNOWN FAILED / KNOWN FAILURE MODES: no closed hypothesis matches this
exact (state variable, bucket, horizon) triple. No prior attempt has
run a 1-day-hold Validation-slice test on vwap_dist_vs_atr/low.

KNOWN UNEXPLORED: this specific gap -- "is H118's edge front-loaded
(absorption, mechanism-consistent) or does it require the full 10 days
(implying either a second slower effect or partial Discovery-stage
noise)" -- is explicitly still open per the mechanism doc's Verdict
section and is the reason this item was queued by Jason.

Resurrection check: NOT a resurrection. Same underlying state variable
and bucket edges as H118, different (shorter, pre-existing-in-the-scan-
data) horizon, answering a different question (front-loading, not
"does the signal have edge"). H118's own Validation/Holdout tests were
run ONLY at the 10-day horizon; the 1-day horizon has never been
Validation- or Holdout-tested.

## Integrity Gate questions (governance ruling)

**Q1 -- genuinely new hypothesis, or second attempt on the vwap_dist
family?** Second attempt. H118 (10d) is attempt 1 of 2 on
vwap_dist_vs_atr/LOW. This is attempt 2 of 2. It is DIFFERENTLY
MOTIVATED, not a retune: it does not touch the state variable, the
bucket edges, or the direction -- it changes the holding period to test
a specific mechanism question (front-loaded absorption vs. a second,
slower effect) that H118's own mechanism doc raised. This is exactly
the canonical example of a permitted second attempt on record elsewhere
in this project's history (docs/BACKLOG.md, H116/H117 2-attempt note:
"testing whether the effect concentrates in a sub-window of the holding
period" is explicitly named as a legitimate differently-motivated second
attempt, not a cosmetic re-cut). COSMETIC-NOVELTY guard checked and
passed: the mechanism claim differs (absorption speed, not "does a
value/absorption signal exist"), not merely the parameter.

**Q2 -- does the 2-attempt limit bind?** Yes, and this consumes it.
After this candidate resolves (promote, close, or null), vwap_dist_vs_
atr/LOW's attempt budget is EXHAUSTED regardless of outcome. No third
attempt at any other horizon (3d, 5d, or otherwise) without a new,
separately-motivated staff-meeting-level justification.

**Q3 -- is it a resurrection?** No -- see LEARN consultation above.
Distinct question, distinct (never-tested) horizon, distinct out-of-
sample data to be used for Validation.

**Q4 -- is picking a different cell from a scan after seeing which cell
won acceptable here, given all 44 Scan 002 cells were disclosed and
already counted in multiple-testing exposure?** Yes, acceptable, with
the record straight about why: this is not "we scanned 44 cells and
this is the one we liked" -- the LOW/vwap_dist cell already won and was
promoted (H118). This is a follow-up question about the horizon
STRUCTURE of an already-promoted effect, using numbers already reported
in the Scan 002 writeup and the H118 mechanism doc before this document
was written. Discovery-stage exposure: the 1d/3d/5d/10d horizon sweep
was part of the original 44-cell Scan 002 (research/NEXT_UP.md quotes
all four horizon numbers as "Scan 002 Discovery numbers"), so this does
NOT add a new Discovery-stage trial to SCAN_REGISTRY in
src/project_wide_multiplicity.py -- it is a re-expression of an
already-counted cell, not a fresh search. It WILL add one new
Validation-stage trial if/when slice 1d (the Validation-slice test)
runs, exactly as any other candidate's first Validation attempt does.

## Verdict: PASS

No conditions. Proceed to 1b (frozen spec). Binding constraints carried
forward: same state variable and FROZEN bucket edges as H118
([-inf, -0.0460, 0.1471, inf], never refit here); 1-day hold;
entry/exit convention stated explicitly before any result is examined;
realistic (not optimistic) costs; direction pre-registered POSITIVE
(matches sign at every horizon in Scan 002); this is the LAST attempt
on vwap_dist_vs_atr/LOW under the 2-attempt limit; never logged as an
H118 row or edit; strict separation both directions from H118's forward
test (per NEXT_UP's HARD CONSTRAINTS).

Recorded per AGENT PROTOCOL Rule 5 (LEARN consulted by name) and the
MANDATORY INTEGRITY GATE checkpoint before this candidate enters formal
Discovery evaluation.
