# hyp-000165 -- Directional Lane Trial 3: Weekend/Monday Effect, NQ (M33)

**Date**: September 16th, 2026, ~11:00 am CT scheduled cycle.
**Entry**: Entry 63 / map anchor M33. **Scan**: scan_039 (`src/market_behavior_discovery_scan_039.py`).
**Mechanism doc**: `research/mechanisms/weekend-effect-nq-m33.md` (written before any scan).
**Ledger**: `research/ledger/hypotheses.jsonl:hyp-000165`; `research/ledger/directional_lane.json` (trial 3 of 20, used 2 -> 3).

## Claim
NQ's Monday (first-trading-day-of-week) same-day RTH return is credibly
NEGATIVE relative to NQ's own unconditional daily RTH return -- the
classic "weekend effect" / "Monday effect" (French 1980, *Journal of
Financial Economics*; Rogalski 1984, *Journal of Finance*; Kamara 1997,
*Journal of Financial and Quantitative Analysis*), never tested against
NQ, or any instrument, in this project as a return-direction claim.

## Result
**P1 (GATING) -- FAIL.** Monday RTH return diff = +3.4269 pts vs NQ's
own unconditional daily RTH return, 90% block-bootstrap CI
(-3.8485, +11.8924). The interval includes zero, and the point
estimate is POSITIVE -- the opposite of the literature's predicted
NEGATIVE direction. n = 348 Monday sessions (Discovery slice,
2015-01-01 -> 2021-10-03), the best-powered directional-lane entry
sourced so far (fires weekly, vs. M28's ~10x/year or M32's 2x/year).

**P2 (reported, Rogalski 1984 specificity, moot given P1 fail).**
Friday-close-to-Monday-open gap return diff = -4.7832 pts vs NQ's own
unconditional overnight return, CI (-12.9000, +3.9585). Not credible
(CI includes zero), though this cell's point estimate does run in the
literature-predicted negative direction, unlike P1's RTH-session cell.

**P3 (reported, descriptive, Kamara 1997 decay check).** First-half
Discovery slice (2015-01-01 -> ~2018-05-17): diff = +0.9237, CI
(-3.5951, +5.7550), null. Second-half (~2018-05-18 -> 2021-10-03):
diff = +5.9740, CI (-8.1896, +20.6428), null. No decay pattern worth
reporting -- neither half shows a credible effect to begin with.

## Verdict
CLEAN NULL. The well-replicated equity weekend/Monday effect does not
transfer to NQ futures RTH sessions at this data ceiling. Closes per
mechanism doc falsifier (a) (`research/mechanisms/weekend-effect-nq-m33.md`
Section 5). No Statistical/Director/Gate/Validation stage owed --
pipeline sweep rule, one Discovery-stage shot per cycle at the daytime
cadence, nothing further owed on a P1 FAIL.

Per this project's standing culture (REFOCUS memo, September 15th), a
correctly-specified clean null is a legitimate, reportable outcome, not
a failure. Directional lane: 3 of 20 trials spent, 3 clean nulls, 17
remaining.

## Full cell table

| cell | n | signal mean | NULL 1 mean | diff | 90% CI | credible |
|---|---:|---:|---:|---:|---|---|
| 1. Monday RTH return (GATING) | 348 | +6.1422 | +2.7153 | +3.4269 | (-3.8485, +11.8924) | no |
| 2. Fri-close->Mon-open gap (P2) | 348 | -1.2593 | +3.5239 | -4.7832 | (-12.9000, +3.9585) | no |
| 3a. First-half Discovery (P3) | 175 | +2.0214 | +1.0977 | +0.9237 | (-3.5951, +5.7550) | no |
| 3b. Second-half Discovery (P3) | 173 | +10.3107 | +4.3367 | +5.9740 | (-8.1896, +20.6428) | no |
| 4. NULL 1 reference (unconditional daily RTH) | 1686 | -- | +2.7153 | -- | -- | -- |
| 5. Thin-sample disclosure | 348 vs floor 40 | -- | -- | -- | -- | not thin |

Statistical convention: block bootstrap, block=5, N_BOOT=3000,
SEED=20260916, 90% CI, "credible" = CI entirely on one side of zero.
Raw scan output: `data/scan_039_2026-09-16_results.json`.

## Next
Shelf falls back to 0/3 (directional lane), sourcing owed next cycle
per SHELF RULE v2 -- non-state directional ideas only (mechanism,
calendar, structure), magnitude stays frozen (REFOCUS s.3).
