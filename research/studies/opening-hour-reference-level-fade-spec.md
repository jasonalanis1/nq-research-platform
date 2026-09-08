# Opening-Hour Reference-Level Fade — Frozen Spec (exp-110)

## Origin (first hypothesis generated from the Observatory, not intuition)

Observatory v1 (research/studies/observatory-v1-design-spec.md) scanned
348 event x regime x time-bucket x horizon combinations on Discovery
data and surfaced 18 "Promising" candidates (effect size + CI + cross-
period consistency + non-concentration, not p-value gated). 15 of the
18 cluster in the 09:30-10:30 "open" time bucket with one consistent
shape: touching prior-day-high, overnight-high, or VWAP during the open
precedes BELOW-baseline forward returns (a fade/rejection bias);
touching the overnight-low in the same window precedes ABOVE-baseline
returns (the mirror). This is the ONE candidate converted into a
hypothesis from this Observatory run, per its own rule that a
candidate must be written up as its own frozen spec before any
entry/stop/target logic exists -- the Observatory itself never designed
a trade.

Excluded from this hypothesis (disclosed, not silently dropped): the 2
"mid_morning" Promising cells (overnight_high, prior_day_high) and the
single "vwap narrow" open-bucket cell are NOT included here -- scoping
to the dominant, coherent open-bucket/upper-level cluster only, rather
than cherry-picking every Promising cell from the scan.

## Setup

**Short signal ("upper-level fade"):** during 09:30-10:30, the FIRST
bar (across all three levels, whichever comes first) whose High/Low
range touches prior-day's RTH high, OR the overnight (Globex) session
high, OR the session VWAP (i >= 5 bars into RTH, matching the
Observatory's own VWAP-stabilization rule) -> SHORT.

**Long signal ("overnight-low fade"):** during 09:30-10:30, the FIRST
bar that touches the overnight session low -> LONG. Independent of the
short signal (opposite direction, evaluated separately) -- both can
fire on the same day if both levels are touched.

**Entry:** touch bar's close. **Stop:** touch bar's extreme (High for
short, Low for long) +/- a buffer of `1.5 * average 1-minute bar range
over the trailing 20 bars` before the touch (same buffer convention as
this project's other level-based setups, e.g. prior-close-rejection).
**Target:** entry +/- `TARGET_R_MULTIPLE (1.35, unmodified from
detect_level_sweep.py)` * risk. Exit intraday via
`backtest.simulate_trade` (unmodified), cost via
`ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2 together (real entry/stop/target, costed). Bootstrap mean-
R-multiple CI, N_BOOTSTRAP=3000, seed=7, 90% CI on `r_multiple_net`.
Credible = CI entirely above zero AND mean R-multiple net of cost >=
0.05R (this project's standard bar).

## Multiple-testing disclosure

This is hypothesis #81 (first Observatory-sourced hypothesis),
`search_batch_id batch-2026-09-08-observatory-hyp-001`. The Observatory
scan that produced it already disclosed its own combinatorial exposure
(348 combinations, 18 Promising) in its own output -- this hypothesis's
OWN statistical test is independent of that scan and stands on its own
merits, same as every other hypothesis in this project. One setup, one
Discovery test, one Validation prospective test if it passes -- no
further variants of this specific idea without a new independently
motivated reason.

## Decision rule / pre-commitment

Credible + economically-meaningful + n >= 40 earns a single
Validation-slice prospective test before any promotion consideration --
standard path, no different from hypothesis #1-80. A null result closes
this specific setup; the Observatory itself is judged on whether the
NEXT few candidates it produces do any better (the "is this whole
approach better than strategy-first" question its own v1 design exists
to answer), not on any single hypothesis's outcome.
