# CFTC COT Positioning — Full-Discovery-Window Follow-Up (exp-091)

## What this document is

A fresh, pre-registered follow-up to exp-044 (`cot-positioning-check.md`),
written before looking at any of the newly-added data. exp-044 disclosed
a known limitation up front (before it was ever run): its GitHub-mirror
data source only covered 2015-2018 (209 weekly reports), a bit over half
of Discovery's full 2015-01-01 to 2021-10-03 window, purely because that
mirror didn't have more recent history — not a deliberate design choice.
exp-044 came back Step-1 FAIL on that partial window.

**Why this is a legitimate follow-up and not a retune-after-a-bad-result:**
exp-044's own spec named "extending to 2019-2021" as the natural next
step *before* any result existed, contingent on getting the data past
the network block. Jason manually downloaded the CFTC's own official
2019/2020/2021 TFF archive files (cftc.gov, blocked from both the cloud
sandbox and the device) and provided them directly — the same official
source, same report, same market row (`NASDAQ-100 STOCK INDEX (MINI) -
CHICAGO MERCANTILE EXCHANGE`), same columns. This extends the sample to
the intended full window; it does not change the signal construction,
the classification rule, the bootstrap method, or the pass/fail bar in
any way in response to exp-044's null result.

## Method — identical to exp-044, zero changes

Reused unmodified from `study_cot_positioning.py`: `load_cot_signal`,
`resolve_availability_dates`, `build_forward_returns`, `bootstrap_diff_ci`,
`run_step1`, `run_step2`. Same signal (week-over-week sign of the change
in Leveraged Money net position), same point-in-time availability-date
logic (Report_Date + 3 days, rolled forward to the next classifiable
trading day, never backward), same Step 1 gate (90% CI on the
difference-of-means entirely on one side of zero), same Step 2 gate
(only run if Step 1 passes).

**The only change:** `COT_CSV` now points to the concatenation of the
original `cftc_tff_nq_mini_2015_2018.csv` (209 reports) and the new
`cftc_tff_nq_mini_2019_2021.csv` (156 reports, 2019-01-08 through
2021-12-28, same 13-column schema, filtered to the identical market row),
sorted by `Report_Date_as_YYYY-MM-DD`, deduplicated on that column if any
overlap exists.

## Decision rule

Same as exp-044: if Step 1 fails, this is a clean, final kill of the COT
positioning line at this weekly resolution with the Leveraged Money
category — no further category variants (e.g. Asset Manager, Other
Reportables) or resolution changes without a new, independently
motivated reason. If Step 1 passes, Step 2 (a costed weekly rule) runs
automatically per the frozen method, same as exp-044 would have.
