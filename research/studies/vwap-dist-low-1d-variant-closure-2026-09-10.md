# vwap_dist_vs_atr LOW, 1-day variant — CLOSED (null, Validation)

Written 2026-09-10, automated session. Closes the item NEXT_UP.md had
flagged as neglected across 3 prior sessions.

## Portfolio incremental-information check (slice 1e — required regardless of outcome)

Question: same latent effect as H118 restated in a shorter window, or
independent information? Answer, now moot for promotion purposes (the
candidate did not clear Validation, so Portfolio's FULL promotion bar
was never in reach) but recorded per Jason's explicit instruction that
this check runs regardless of outcome: the Discovery-slice numbers for
this candidate and H118 ARE the same underlying state (same variable,
same frozen bucket edges) at different horizons, so by construction any
Discovery-stage signal in one is mechanically related to the other —
never independent in the way two structurally different candidates
would be. What this session's result actually shows is that they are
NOT interchangeable as evidence: the 1-day slice failed Validation
where the 10-day slice passed it (barely). That is itself the
informative fact for LEARN below — same latent state, but the two
horizon cuts behave differently under out-of-sample testing, so neither
should be treated as confirming or standing in for the other. Portfolio
does not activate (full promotion bar not cleared); this section exists
so the check is on record rather than silently skipped because the
outcome made it feel unnecessary.

## LEARN entry (KNOWN FAILED, new)

vwap_dist_vs_atr/LOW, 1-day horizon, LONG, time-based exit: Discovery-
slice credible and economically meaningful (n=558, R=0.1097 net,
CI_90 [0.053,0.165]), cost-robust (survives ~5x realistic cost stress),
clean on both volatility-regime and trend-regime splits, one caution on
chronological split-sample (first half not independently credible).
Validation-slice (n=218, single pre-registered shot): NOT credible
(CI [-0.033,0.127]), NOT economically meaningful (R=0.047 < 0.05
floor). REJECTED. hyp-000136 (Discovery) -> hyp-000137 (Validation).

Structural lesson (distinct from "no edge here" — see the
ib-breakout-afternoon-conditioned-stop-overlay closure earlier
2026-09-10 for the format this follows): a state variable/bucket that
shows a clean, front-loaded effect shape within ONE Discovery sample
(most of a longer horizon's return arriving in the first day) does NOT
mean the short-horizon slice of that shape is more robust to
Discovery-stage selection than the full-horizon aggregate is. Here the
1-day cell shrank from Discovery to Validation by essentially the same
proportion (57%) the 10-day H118 figure did (55%), and lost credibility
entirely where the 10-day figure barely kept it. Future candidates:
"the effect looks concentrated in the first N days of a longer window"
is a real, testable, worthwhile question (as this session's mechanism
doc treated it) — but it is NOT a reason to expect the short-window cut
to validate more easily. If anything this one data point suggests the
opposite: the short cut has less data (n=558 vs would-be larger pools)
and no more Discovery-stage selection protection than the long cut.

## vwap_dist_vs_atr/LOW — family status

2-ATTEMPT LIMIT NOW EXHAUSTED. Attempt 1 (H118, 10-day): PROMISING ->
VALIDATION CANDIDATE -> HOLDOUT PASSED -> FORWARD VALIDATION (frozen,
outside automated scope, untouched by this session). Attempt 2 (this
variant, 1-day): PROMISING (Discovery) -> REJECTED (Validation),
CLOSED. No further attempts on this state variable/bucket at any other
horizon or sub-window without a new staff-meeting-level justification
per the 2-attempt limit. H118 itself is completely unaffected by this
result — STRICT SEPARATION held throughout, no H118 row touched, no
H118 spec or status file modified, this candidate's null does not and
cannot revisit H118's already-passed Holdout or its ongoing forward
test.

## Candidate Triage final disposition

REJECTED at Validation, per this project's standing practice (matches
the H116/H117/original-vwap_dist-attempt-1-if-it-had-failed pattern —
a Discovery pass that does not replicate out of sample closes, it does
not get a third look). No hypothesis ID freed or reused; hyp-000136 and
hyp-000137 stand as the permanent record.

## Files

- research/studies/vwap-dist-low-1d-variant-integrity-preclearance-2026-09-10.md
- research/studies/vwap-dist-low-1d-variant-spec.md (+ addendum)
- research/mechanisms/vwap-dist-low-1d-variant.md (P2 contradicted, verdict REFUTED/CLOSED)
- research/studies/vwap-dist-low-1d-variant-statistical-director-integrity-2026-09-10.md
- src/study_vwap_dist_low_1d_variant.py, src/study_vwap_dist_low_1d_variant_stability_check.py
- data/study_vwap_dist_low_1d_variant_discovery_results.json
- data/study_vwap_dist_low_1d_variant_validation_results.json
- data/study_vwap_dist_low_1d_variant_stability_results.json
