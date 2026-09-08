# Intraday Behavior Batch 2 — Prospective Validation Spec (2026-09-08)

exp-081/082 — pre-registered prospective tests of exp-078 (effort-vs-result
absorption, stalled/reversal group only) and exp-080 (trend-day shape,
choppy group only), the two well-powered Step-1 PASS results from
`intraday-behavior-batch2-spec.md`. Both run, unmodified, on the
Validation slice (2021-10-04 to 2024-01-03). exp-079 (multi-day base
breakout, n=9) is explicitly excluded from prospective testing — see its
ledger entry (hyp-000051) for why: the Discovery sample is too thin for a
prospective test to be informative either way.

All thresholds and the exact method are carried over unmodified from
batch 2; no retuning. A Validation-slice failure closes each line for
good per the standing no-retuning rule.

**exp-081 (effort-vs-result absorption, stalled/reversal group,
Validation slice):** same effort-bar definition, stall classification,
and reversal-test method as exp-078's stalled group, run on Validation-
slice 1-min bars only. The continued/continuation group already failed
Step 1 in batch 2 and is not re-tested.

**exp-082 (trend-day shape, choppy group, Validation slice):** same
first-hour MAE% classification and afternoon-continuation outcome as
exp-080's choppy group, run on Validation-slice days only. The trend_like
group already failed Step 1 in batch 2 and is not re-tested.
