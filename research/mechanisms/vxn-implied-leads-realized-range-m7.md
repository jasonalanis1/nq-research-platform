# Mechanism — VXN elevated vs. its own norm -> next-day realized RTH range (Entry 8, map anchor M7, range footprint)

Written: September 11th, 9:44 pm CT (2026-09-12 02:44 UTC), extra cycle at Jason's direction  ·  PRE-REGISTERED
Results seen before writing: NO. Attempt 1 on vxn_level_vs_trailing (Scan 002) tested signed RETURNS and closed; this is attempt 2 of 2 and the LAST on this state variable, on a different outcome (magnitude). Transcribed from Entry 8's generation meeting (September 11th, 3:02 pm CT), which wrote the predictions before any number was looked at. Under AMENDMENT v2.5 this doc precedes the scan; after the scan it may only ADD predictions.

## 1. The claim
Options prices embed expected variance. When the market is paying up for NQ variance relative to its own recent norm (VXN close above its trailing-20-day average), the following RTH session's realized range runs above its own recent norm: implied information leads realized. The M7 anchor: vol-targeting and risk-parity books de-lever as VXN rises, and their selling is itself range-generating the next session -- so the footprint is range, not direction (the directional use is closed: hyp-000029/030).

## 2. Who is on the other side
Anyone sizing next-day stops/targets off the trailing realized range alone, ignoring what the options market already paid for. Diffuse, as with every range finding; the operational use is conditioning, not a directional trade.

## 3. Testable predictions
P1 (gating, single cell). HIGH vxn_level_vs_trailing tercile on day t -> day t+1 RTH range / trailing-20d average credibly > 1.0 (90% CI lower bound > 1.0). Falsifying alternative on the identical cell: if elevated VXN is variance-risk-premium noise or LAGS realized vol, the ratio is indistinguishable from 1.0.
P2 (reported). LOW tercile -> ratio credibly < 1.0 (compression).
P3 (separability, gating for ADVANCEMENT not for the Discovery result): the HIGH-VXN effect residualised on overnight_range_vs_atr tercile retains >= 50% of its raw magnitude and stays credible; < 50% = the overnight-coil finding restated through the options market -> CLOSED as redundant at Triage.
P4 (reported, non-restating counterparty check). Effect STRONGER when day t's own realized range was NOT already elevated (VXN high, yesterday quiet = implied leading realized) than when day t was already wild (VXN merely reflecting realized).

## 4. What would falsify this
P1 null (HIGH cell CI includes 1.0); or P3 < 50% retained; or P4 reversed (effect only when yesterday was already wild -- then VXN is a mirror of realized, not a lead).

## 5. Prediction status (updated September 11th, 9:47 pm CT, Scan 014 -- claim above unchanged)
P1 — CONFIRMED. HIGH tercile n=556, next-session range ratio 1.305, ci_90 [1.259, 1.353], credibly elevated.
P2 — CONFIRMED. LOW tercile n=556, ratio 0.796, ci_90 [0.770, 0.825], credibly compressed. MID 1.007 null (clean monotone gradient).
P3 — PASSED the pre-registered >= 50% bar: residualised on overnight_range_vs_atr tercile, 66% of the HIGH-LOW spread retained and the residual HIGH cell stays credibly elevated. corr(vxn_level_vs_trailing, overnight_range_vs_atr) = +0.41 -- the overlap with the coil is real, not identity. Advances to Triage rather than closing as redundant.
P4 — RAN OPPOSITE ITS PREDICTION (reported, not gating). Effect is STRONGER when the prior day was already wild (1.464) than when it was quiet (1.146); both credibly elevated. Reading: VXN partly mirrors yesterday's realized range (the falsifying alternative has a real component) AND still carries next-session range information when yesterday was quiet (the claim's component). Not smoothed over; a Statistical-stage pass must separate the two (e.g. residualise on range_vs_atr as well as overnight range).

## 6. Verdict
CREDIBLE SURVIVOR at Discovery. Logged hyp-000142 (PROMISING), SCAN_REGISTRY scan_014_2026-09-12 promoted_hypothesis_ids updated. Routed to Director (Triage). Not a directional edge -- a next-session RANGE conditioning fact, the same class as the three validated findings; if it survives Statistical -> Director -> blind Gate -> Validation it joins volatility_conditioning.py, it does not become a strategy. LAST attempt on vxn_level_vs_trailing regardless of what follows. State variable: vxn_level_vs_trailing (market_state_primitives_v2.extend_state_frame, unchanged: VXN close / trailing-20d mean, shifted -- the value on day t uses VXN through day t-1's close as the module defines it; the scan documents the exact alignment it uses). Outcome: day t+1 RTH range / trailing-20d average RTH range (build_rth_range_frame convention). Cells: HIGH gating, LOW reported = 2 cells registered. LAST attempt on this variable.

## 7. Validation (September 11th, 9:57 pm CT) -- claim unchanged
ONE-SHOT VALIDATION PASS (hyp-000144, Validation slice 2021-10-04..2024-01-03, frozen Discovery edges): HIGH n=198 ratio 1.120 ci_90 [1.066, 1.177], Sidak-adjusted [1.026, 1.213] > 1.0, economic floor cleared (0.12 >= 0.05). LOW n=166 0.865 [0.822, 0.910] compressed -- P2 also holds out of sample. MID 1.035 null. Effect size fell from 1.305 (Discovery) to 1.120 -- read with the usual caution, but the binding bar is cleared. P4 split out of sample: see data/study_vxn_high_next_day_range_h142_validation_results.json. Blind Integrity Gate ruled CONDITIONAL on three verifiable facts, all resolved in writing before the run (recorded in the spec). Status: VALIDATION CANDIDATE, GATED at Holdout (Jason). Would be the project's fourth range/conditioning fact and the first found by the map-anchored, mechanism-first v2.5 pipeline end to end.
