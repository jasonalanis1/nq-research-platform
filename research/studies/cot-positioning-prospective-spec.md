# CFTC COT Positioning — Validation-Slice Prospective Test (exp-092)

## What this is

The single pre-registered prospective test of exp-091 (hyp-000063),
required before any promotion consideration, per this project's standing
protocol. exp-091 passed both Step 1 and Step 2 on the full Discovery
window (2015-2021, n=350 weeks) — the best Discovery-stage result in
the project's history. This tests it, completely unmodified, on the
Validation slice (2021-10-04 to 2024-01-03), using the same official
CFTC TFF data Jason provided (2022-2023 files, matched across the
mid-2022 CFTC renaming of the contract from "NASDAQ-100 STOCK INDEX
(MINI)" to "NASDAQ MINI" — same CFTC_Contract_Market_Code 209742,
verified by cross-checking both names appear for the same code in the
2022 file).

## Method — identical to exp-091, zero changes

Same signal (sign of week-over-week change in Leveraged Money net
position), same availability-date logic, same long_group direction
(-1.0, i.e. fade the leveraged-money positioning shift — this was
determined by exp-091's Discovery-stage result and is NOT re-derived
here), same costed Step 2 rule, same bootstrap method and thresholds.

**Signal continuity across the Discovery/Validation boundary:** the
week-over-week delta is computed on the full concatenated series
(2015-2023, all 4 provided files), not restarted at the Validation
boundary — the first Validation-era report's delta is a real week-over-
week change from the last Discovery-era report, not an artificial NaN.
Only the resulting forward-return rows whose availability_date falls in
the Validation slice are scored.

## Decision rule

Pre-registered, no exceptions: PASS (credible net-of-cost profit,
CI entirely above zero) means this becomes the project's first
directional signal to reach "VALIDATION CANDIDATE" status — a real
milestone, but still not Holdout-tested or live-authorized. FAIL means
this line closes for good, per the standing no-retuning rule — no
category variants, no threshold changes, no third look. Whichever way
this goes, it gets reported to Jason immediately given the size of the
Discovery-stage result.
