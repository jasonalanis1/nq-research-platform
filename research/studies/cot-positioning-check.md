# CFTC Commitment-of-Traders Positioning -- Cheap Characterization Check (exp-044)

## What this document is

A frozen, pre-registered spec written before any result is looked at,
for the first hypothesis in this project that uses a genuinely
different DATA SOURCE (positioning data, not price action derived from
NQ itself) and a genuinely different resolution (weekly, not
intraday/daily). Per the Path-to-Profitability Advisor's explicit
recommendation (2026-09-03 consultation): start with a small, cheap
check of whether positioning correlates with next-period direction AT
ALL, before building anything resembling a full trading rule.

## Data source and an honest limitation, disclosed up front

Data: CFTC "Traders in Financial Futures" (TFF) report, futures-only,
for "NASDAQ-100 STOCK INDEX (MINI) - CHICAGO MERCANTILE EXCHANGE" --
the official CME E-mini NASDAQ-100 contract, i.e. NQ. This is the same
official CFTC report described at
https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm,
sourced (because direct network access to cftc.gov is blocked from
both this project's cloud sandbox and the local device -- a network
egress restriction, not a data-availability problem) via a GitHub
mirror of the CFTC's own published historical files
(github.com/jensolson/CFTC-COT), spot-checked against the CFTC's own
documented column schema for the TFF report before use.

**Honest limitation**: this mirror's data runs from 2015-01-06 through
2018-12-31 (saved as `data/cftc_tff_nq_mini_2015_2018.csv`, gitignored
like every other CSV in this project). The full Discovery window is
2015-01-01 to 2021-10-03 (`data_split.py`). This check therefore only
covers roughly the first 4 of Discovery's ~6.75 years -- 209 weekly
reports, entirely inside Discovery, zero leakage risk, but not the
full window. If this cheap check clears its bar, extending to
2019-2021 (via a manual download from Jason, since that is the only
currently-known path past the network block) is the natural next step
-- not needed for this first look.

## Point-in-time alignment (the trap this spec is designed to avoid)

Each report's `Report_Date` is the PRIOR TUESDAY's positions, but the
report itself is not published until the FOLLOWING FRIDAY (per CFTC's
own publication schedule). Using `Report_Date` as if the data were
already known on that Tuesday would be lookahead bias. This spec
instead computes, for each report, an `availability_date`:
`Report_Date + 3 calendar days` (lands on the Friday of that week in
the normal case), rolled FORWARD to the next actual classifiable NQ
trading day if that Friday itself has no usable reference close (e.g.
a holiday) -- never rolled backward, so the signal is never treated as
available before it genuinely was.

## Signal definition (frozen)

Only ONE trader category is tested as the primary signal:
**Leveraged Money** (`Lev_Money_Positions_Long_All` /
`Lev_Money_Positions_Short_All` in the TFF schema -- the category
closest to "large speculators / hedge funds" in the academic literature
on COT predictive power, e.g. the S&P 500 futures studies found via
search this session). The other three reportable categories in the
data (Dealer, Asset Manager, Other Reportable, plus Non-Reportable) are
NOT tested in parallel as a menu of alternatives -- testing all of them
and reporting whichever came back significant would be undisclosed
multiple comparisons, the same caution already flagged in this
project's own exp-032 write-up.

`NetLevMoney[t] = Lev_Money_Positions_Long_All[t] - Lev_Money_Positions_Short_All[t]`

`Signal[t] = sign(NetLevMoney[t] - NetLevMoney[t-1])` -- the
week-over-week CHANGE in net leveraged-money positioning, excluding
exact-zero deltas (kept out of both groups, disclosed as excluded
rather than silently dropped).

## Forward return (frozen)

`ForwardReturn[t] = ref_close[availability_date[t+1]] - ref_close[availability_date[t]]`
in NQ points, using `study_volatility_regime.compute_daily_ref_closes`
(reused unmodified) over Discovery-slice NQ data
(`data_split.get_discovery_data`, reused unmodified) -- i.e. the actual
NQ price change between one week's report becoming available and the
next week's report becoming available.

## Step 1 test (primary, descriptive, no cost) -- pre-registered

Split all weeks into two groups by `Signal[t]` (+1 vs -1, zero-delta
weeks excluded). For each group compute the mean `ForwardReturn`, then
compute the DIFFERENCE in means (Signal=+1 group mean minus Signal=-1
group mean) with a 90% bootstrap CI on that difference (each group
resampled independently with replacement, 2000 resamples, same
seed-11 convention as the rest of this project).

**Why the difference-of-means, not each group's CI against zero
separately**: this project's own VXN pricing check (2026-09-03, same
day) caught a false positive from exactly this mistake -- a subgroup
showed a CI entirely above zero, but so did the baseline, because both
just reflected NQ's general upward drift over the period rather than
anything specific to the subgroup. Testing the DIFFERENCE between the
two signal groups, which share the same drift environment, is the
control that avoids repeating that error here.

**Step 1 passes if**: the 90% CI on the difference is entirely on one
side of zero (either sign -- no directional hypothesis is pre-committed;
the academic literature found this session is not itself consistent on
direction, with some studies describing a reversal effect and others
an informative/momentum-like signal, so this is treated as a genuinely
open two-tailed question).

If Step 1 does not clear, the check stops there and is reported as a
null, honestly -- no Step 2.

## Step 2 (costed rule) -- gated, not guaranteed to run

Only if Step 1 clears: a rule that goes long when `Signal[t] = +1` and
short when `Signal[t] = -1` (direction determined by WHICHEVER side of
zero the Step 1 CI landed on -- long the group with the higher forward
return, short the other), held from `availability_date[t]` to
`availability_date[t+1]`, net of one `ROUND_TRIP_COST_POINTS` per week
held, same statistically-credible / economically-meaningful (>= 2x
realized cost drag) gate structure used throughout this project.

## Promotion bar (adapted for weekly resolution)

Same adaptation precedent as exp-038 (this project's first
daily-resolution study): the standard 150-trade minimum was designed
for a much higher-frequency signal. At weekly resolution over even the
FULL 2015-2021 Discovery window, ~355 weeks is the ceiling; this
reduced 2015-2018 sample offers ~207. This check is explicitly scoped
as Step 1 only -- the promotion-bar question only becomes live if
Step 1 clears AND (per the honest limitation above) the sample is
later extended toward the full Discovery window.

## What this is NOT

- Not a full trading rule test. Step 1 only, unless it clears.
- Not a search across multiple trader categories -- Leveraged Money
  only, pre-registered, for the reason given above.
- Not evidence about 2019-2021 Discovery data, which this check does
  not yet have access to.
- Not a substitute for later using `data_split.get_validation_data()`
  should this ever reach a genuinely frozen, promoted candidate -- that
  slice remains untouched here, same as every other hypothesis.
