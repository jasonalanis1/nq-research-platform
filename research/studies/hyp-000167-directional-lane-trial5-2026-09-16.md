# hyp-000167 -- Directional Lane Trial 5: Semi-Monthly Effect, NQ (M35)

**Date**: September 16th, 2026, ~3:00 pm CT scheduled cycle.
**Entry**: Entry 65 / map anchor M35. **Scan**: scan_041 (`src/market_behavior_discovery_scan_041.py`).
**Mechanism doc**: `research/mechanisms/semi-monthly-effect-nq-m35.md` (written before any scan).
**Ledger**: `research/ledger/hypotheses.jsonl:hyp-000167`; `research/ledger/directional_lane.json` (trial 5 of 20, used 4 -> 5).

## Sourcing: candidates considered before this one
Before writing the mechanism doc, four other candidates from the task's
own suggestion list were checked against `research/idea_inventory.md` and
`research/market_structure_map.md` and set aside as duplicates or
unrunnable, not picked past without checking:
- **FOMC/CPI/NFP announcement drift** -- already spent. M3a (CPI/NFP
  release-day reaction) CLOSED; M3b (FOMC post-statement continuation)
  one attempt spent, a second attempt exists but needs a different
  window, not a new candidate; M4 (pre-FOMC drift) CLOSED FOR GOOD,
  2-attempt limit exhausted (`research/market_structure_map.md:51-53`).
- **Turn-of-quarter/quarter-end institutional rebalancing** -- overlaps
  M5 too closely: same participant (pension/balanced-fund rebalancers),
  same anchor (last 2 sessions of month/quarter), attempt 1 already
  spent (`research/market_structure_map.md:54`).
- **Triple/quad-witching-specific effect** -- blocked by a known DATA
  DEFECT, not merely already tested: the continuous NQ 1-min series has
  ZERO usable RTH bars on quarterly witching Fridays (roll-day splice),
  confirmed independently by Entry 2's LEARN note
  (`research/idea_inventory.md:80-85`) and M9's own Scan 018
  (`research/market_structure_map.md:58`). Unrunnable on this data
  without a new purchase, out of scope.
- **January effect / small-cap rotation adapted to NQ** -- its classic
  mechanism (tax-loss-selling reversal in small-cap names) duplicates
  M34's already-CLOSED Santa Claus Rally mechanism (same Reinganum 1983
  citation, overlapping December/January window), and NQ (mega-cap
  Nasdaq-100) is a poor instrument match for a small-cap-rotation claim
  regardless.

**Selected: the semi-monthly effect (Ariel 1987, JFE)** -- a distinct
participant (twice-monthly payroll/pension flow vs. M6's once-monthly),
a distinct window (9-session first half of the month vs. M6's 3-session
start-of-month or M5's 2-session boundary), never tested in this
project, and the best expected statistical power of any directional-lane
entry sourced so far.

## Claim
NQ's mean RTH return on first-half-of-month sessions (trading-day-of-
month 1-9, Ariel's own window length) is credibly POSITIVE relative to
NQ's own unconditional daily RTH return, while the second half is not
credibly different from it.

## Result
**P1 (GATING).** First-half-of-month mean RTH return diff = -0.2047 pts
vs NQ's own unconditional daily RTH return, 90% block-bootstrap CI
(-5.1809, +5.2432) -- includes zero, not credible. Point estimate runs
marginally NEGATIVE (opposite the predicted positive direction), though
the wide CI means this is a clean null, not a wrong-signed credible
result. n=730 first-half sessions -- clears the n=40 floor by a wide
margin, the best-powered directional-lane entry sourced so far (vs.
M33's 348, the previous best).

**P2 (reported, second-half specificity, moot given P1 fail).**
Second-half-of-month diff = +0.1563 pts, CI (-4.1744, +4.3845), also not
credible. Both halves of the month are statistically indistinguishable
from NQ's ordinary unconditional daily return -- no first-half-specific
signature to speak of even setting aside P1's own failure.

**P3 (reported, descriptive, decay check).** First-half years
(2015-2017) first-half-of-month effect: diff = -1.1227, CI
(-5.1745, +3.0994). Second-half years (2018-2021): diff = +0.5279, CI
(-8.0103, +8.6933). Both null -- no decay pattern to report since
neither half shows a credible effect to begin with.

## Verdict
**CLEAN NULL, well-powered.** Closes per the pre-registered falsifier
(a) in `research/mechanisms/semi-monthly-effect-nq-m35.md` Section 5.
Unlike trial 4 (M34, Santa Claus Rally), which was inconclusive at n=6,
this result is definitive at n=730: the well-replicated semi-monthly/
Ariel effect does not transfer to NQ futures RTH sessions at this data
ceiling (2015-01-01 -> 2021-10-03, n=1686 Discovery sessions). This is
the fifth directional-lane trial and the fourth genuinely conclusive
null (trials 1, 2, 3 and 5 all clean; trial 4 alone was underpowered).

## Ledger
`research/ledger/hypotheses.jsonl:hyp-000167` REJECTED.
`research/ledger/directional_lane.json` used 4 -> 5, trial 5 recorded.
`research/idea_inventory.md` Entry 65 CLOSED. `research/market_structure_map.md`
M35 row CLOSED. Directional lane: 5 of 20 trials spent, 4 clean nulls
+ 1 thin-sample-disclosed, 15 remaining.
