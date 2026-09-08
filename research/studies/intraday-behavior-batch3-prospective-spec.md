# Intraday Behavior Batch 3 — Prospective Validation Spec (2026-09-08)

exp-085 — pre-registered prospective test of exp-084 (overnight range
compression / "pre-open coiling", hyp-000056), the one well-powered Step-1
PASS from `intraday-behavior-batch3-spec.md`. Run, unmodified, on the
Validation slice (2021-10-04 to 2024-01-03). exp-083 (lull re-engagement)
already failed Step 1 in batch 3 and is not carried forward.

All thresholds and the exact method (`COIL_PCTL=20`, `LOOKBACK_DAYS=20`,
same overnight/RTH range definitions) are carried over unmodified from
batch 3; no retuning. A Validation-slice failure closes this line for good
per the standing no-retuning rule — same pattern as exp-081/082's
prospective tests.

**exp-085 (overnight coil, RTH range ratio, Validation slice):** same
coiled-day classification and RTH-range-ratio outcome as exp-084, run on
Validation-slice 1-min bars only.
