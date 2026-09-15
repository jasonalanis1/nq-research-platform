# hyp-000166 -- Directional Lane Trial 4: Santa Claus Rally / Turn-of-Year Effect, NQ (M34)

**Date**: September 16th, 2026, ~1:00 pm CT scheduled cycle.
**Entry**: Entry 64 / map anchor M34. **Scan**: scan_040 (`src/market_behavior_discovery_scan_040.py`).
**Mechanism doc**: `research/mechanisms/santa-claus-rally-nq-m34.md` (written before any scan).
**Ledger**: `research/ledger/hypotheses.jsonl:hyp-000166`; `research/ledger/directional_lane.json` (trial 4 of 20, used 3 -> 4).

## Preflight: sanity-check of trials 1-3
Before sourcing trial 4, scan_037/038/039 (`src/market_behavior_discovery_scan_037.py`,
`_038.py`, `_039.py`) were read side by side and checked against the house
return convention (`src/market_state_primitives.py:116` `gap_vs_atr = Open -
prior_close`; `src/data_loader.py:66` tz-aware `America/New_York` parsing).
Finding: **clean, no bug**. All three scans compute `rth_return = close - open`
identically, all three `overnight_return = open(t) - close(t-1)` identically
and consistently with the house convention, all three `cell_vs_null1()`
functions and their `p1_pass` sign checks match each scan's own stated
predicted direction (037: predicted positive, gate is `ci_90[0] > 0`; 038/039:
predicted negative, gate is `ci_90[1] < 0`), and the price index is
tz-aware ET throughout so `between_time("09:30","16:00")` and
`.dayofweek`/`.date` calendar logic are not exposed to a UTC/ET flip. Three
wrong-signed nulls in a row is therefore read as a real result, not a bug
symptom: M28/M32/M33 are all decades-old, extremely well-replicated equity
anomalies with no single named forced counterparty (flagged in advance in
each entry, `research/idea_inventory.md:1876,2516,2601`), the kind of edge
most likely to have already been arbitraged out of modern, deep-liquidity
index futures.

## Claim
NQ's Santa Claus Rally window (last 5 RTH sessions of December + first 2 RTH
sessions of January, Hirsch 1972) cumulative RTH return is credibly POSITIVE
relative to NQ's own unconditional 7-session rolling RTH return.

## Result
**Pre-registered THIN-SAMPLE OVERRIDE triggered.** This window fires once a
year; the Discovery slice (2015-01-01 -> 2021-10-03) contains only n=6
complete windows (years 2015-2020), well below the ordinary n=40 project
floor -- disclosed in advance in the mechanism doc (Section 5c) as the
expected outcome, not discovered after the fact.

**P1 (GATING, reported for completeness).** diff = +15.9750 pts (point
estimate runs in the PREDICTED positive direction, unlike trials 2 and 3),
90% block-bootstrap CI (-71.7472, +110.4496) -- very wide, includes zero.
Not credible, consistent with severe underpowering at n=6 rather than a
clean absence of effect.

**P2 (reported, Dec-leg/Jan-leg specificity).** December leg diff = -8.2015,
CI (-67.0348, +74.6735), null. January leg diff = +25.3611, CI
(-34.4806, +77.8611), null. Neither leg individually credible.

**P3 (reported, descriptive, decay check).** First-half years (2015-2017):
diff = -36.2750, CI (-89.3562, +24.3534). Second-half years (2018-2020):
diff = +68.2250, CI (-73.1969, +209.5608). Both null, n=3 each -- far too
few observations to read as a decay pattern.

## Verdict
**THIN_SAMPLE_DISCLOSED**, closed per the pre-registered thin-sample
override (mechanism doc falsifier c) -- not treated as a clean null the way
trials 1-3 were, since this entry was never adequately powered to detect the
claimed effect. Unlike M28/M32/M33, the point estimate here runs in the
literature-predicted direction; the honest read is "inconclusive at this
data ceiling," not "refuted." A future cycle with a longer Discovery slice
(more calendar years) could revisit this at attempt 2 of 2 if ever warranted,
but is not owed and is not scheduled by this closure.

## Ledger
`research/ledger/hypotheses.jsonl:hyp-000166` REJECTED (thin-sample
disclosure, not a promotable pass). `research/ledger/directional_lane.json`
used 3 -> 4, trial 4 recorded. `research/idea_inventory.md` Entry 64 CLOSED.
`research/market_structure_map.md` M34 row CLOSED. Directional lane: 4 of 20
trials spent, 3 clean nulls (wrong-signed) + 1 thin-sample-disclosed,
16 remaining.
