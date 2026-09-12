# FROZEN Validation spec — hyp-000142 (vxn_level_vs_trailing HIGH -> next-session RTH range)

Frozen: September 11th, 9:52 pm CT (2026-09-12 02:52 UTC), BEFORE any Validation-slice outcome is examined. Extra cycle at Jason's direction; Validation attempts are automated under the OPEN-tier rule ("let it run validation on its own, only holdout needs me").

## What is being tested
State: `vxn_level_vs_trailing` (market_state_primitives_v2.extend_state_frame, unchanged) on row t = VXN close of day t-1 / trailing-20-day mean (through t-2) - 1. Known before day t's RTH opens.
Outcome: day t's RTH range / trailing-20-trading-day average RTH range (build_rth_range_frame, shifted, no lookahead).
Bucket edges: FROZEN from Discovery (Scan 014): LOW <= -0.0608, HIGH > +0.0258. Never refit.

## Pre-registered pass criteria (single shot, Validation slice 2021-10-04 .. 2024-01-03)
Gating cell: HIGH tercile (frozen edge). PASS if the 90% bootstrap CI of the mean range ratio has lower bound > 1.0 AND mean - 1.0 >= 0.05 (economic floor). Project-wide multiplicity: also report the Sidak-adjusted CI at the Validation-stage trial count (project_wide_multiplicity.evaluate, stage="validation"); per the project convention the adjusted CI is the BINDING criterion.
Reported, not gating: LOW cell (predicted < 1.0); MID; the P4 split (prior-day range_vs_atr median within HIGH).
FAIL closes hyp-000142 and CLOSES vxn_level_vs_trailing for good (attempt 2 of 2). No second Validation attempt, no re-cut, no horizon change.

## What is NOT allowed after this point
Changing edges, the lookback (20d), the outcome normalisation, the slice boundary, or adding cells. Any discrepancy between this spec and the Validation script is a finding, not a reason to edit the spec.

## Script
src/study_vxn_high_next_day_range_h142_validation.py (to be written verbatim from this spec; the blind Integrity Gate reviews spec + script + mechanism doc BEFORE the script is run).

## BLIND INTEGRITY GATE CHECKPOINT (fresh subagent, packet research/_blind/vxn_high_next_day_range_h142.md, September 11th, 9:55 pm CT)

Ruling, verbatim: "RULING: CONDITIONAL. Finding: The procedure is unusually disciplined — spec frozen pre-outcome, edges hard-coded from Discovery and never refit, direction pre-registered (P1/P2), an unfavorable finding (P4 reversal) disclosed rather than buried, power computed at the frozen edges blind to outcome, and the binding pass criterion is the Sidak-adjusted CI rather than the raw one. Two gaps remain unverified from the packet alone: (1) no Discovery sample date range is given, so temporal non-overlap between the Discovery scan (source of the frozen edges) and the Validation slice cannot be confirmed. (2) The Validation-stage Sidak trial count ... doesn't show the count is current/inclusive of all concurrent OPEN-tier Validation attempts. Additionally, 'attempt 2 of 2' on the same state variable is legitimate only if the two outcomes are genuinely distinct constructs ... should be confirmed against the Scan 002 closure record before running. Confidence: Medium-high. Novelty: Moderate. Research Value: Real if it clears. Recommendation: CONDITIONAL — before running the Validation script, confirm in writing: (1) the Discovery sample used for Scan 014's edges contains zero dates from the Validation slice; (2) the Sidak trial count passed to project_wide_multiplicity.evaluate reflects the current, complete OPEN-tier Validation attempt count as of today, not a stale snapshot; (3) Scan 002's closure record is checked to confirm the signed-return and magnitude tests are non-overlapping constructs. Once confirmed, run as specified with no further changes."

Conditions resolved BEFORE the script was run (all three are facts checked against the repo, not judgment):
1. Discovery span 2015-01-01 -> 2021-10-01; Validation span 2021-10-03 -> 2024-01-03; overlap 0 days (data_split.get_discovery_data / get_validation_data, checked live).
2. project_wide_multiplicity.compute_stage_trial_counts() is computed live from the ledger at run time, not a snapshot: validation = 19 logged Validation-stage tests as of now (discovery = 303, holdout = 2). The script calls it at run time, so the count used is the current one.
3. Scan 002 (src/market_behavior_discovery_scan_002.py) tested vxn_level_vs_trailing against SIGNED forward RETURNS at horizons 1/3/5/10 days (forward_return of close-to-close). This test's outcome is the next session's RTH RANGE ratio -- a magnitude, not a direction; different outcome statistic and different mechanism claim. Non-overlapping constructs confirmed.
Gate satisfied; VETO not exercised. Run as specified, no changes.
