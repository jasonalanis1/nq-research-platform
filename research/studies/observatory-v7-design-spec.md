# Observatory v7 Design Spec

Frozen 2026-09-09. Chosen per the mechanism-first selection principle
from the 2026-09-09 staff meeting: prioritize event families with a
plausible liquidity/participation mechanism over merely-untried event
types.

## Mechanism

Midday (12:00-14:00 ET) is this market's lowest-participation window
(well-documented "lunch lull"). Power hour (14:00-16:00 ET) is where
institutional participation and algorithmic flow resume in force. The
hypothesis: an unusually LOW-participation midday (measured by its own
range, a proxy for activity) represents pent-up/undecided interest that
resolves into an unusually ACTIVE afternoon once participation resumes
-- the same underlying mechanism as the project's only 2 validated
findings (range-contraction persistence, hyp-000046/048; overnight
coil, hyp-000056/057), applied to a session transition instead of a
day-to-day or overnight-to-day transition. Not a retest of either --
different session windows, different underlying data (midday RTH range
vs. prior full-day range / overnight range).

## Definition (magnitude-based, not directional -- avoids the
direction-ambiguity failure mode entirely)

Event: midday range (High-Low, 12:00-14:00) in the bottom 20th
percentile of its own trailing 20-day distribution ("narrow midday").
Outcome: afternoon range (High-Low, 14:00-16:00) relative to ITS OWN
trailing 20-day average afternoon range (a ratio, same convention as
hyp-000046/048's analyze_range_contraction). Compared against the
complement (not-narrow middays).

## Method

Bootstrap mean-ratio CI (N_BOOTSTRAP=3000, seed=7, 90% CI), credible =
CI entirely above/below 1.0. Same volatility-regime conditioning as
prior scans is NOT applied here (this measurement IS itself a
regime-style measurement -- the midday classification already plays
that role). ATR-normalized cost-aware framing does not directly apply
either (this is a magnitude/range finding like hyp-046/048, not a
directional return finding) -- if credible, its economic use (like
hyp-046/048) would be as a volatility-conditioning input, not a
standalone directional trade.

## Per protocol

A credible result gets its own Behavioral Finding before being
considered for any use (e.g. folding into volatility_conditioning.py,
or as a conditioning input for an existing directional candidate).
