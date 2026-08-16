# Level Sweep Reversal

**Status: Jason's first real candidate setup** (not a placeholder like
the ORB one) — defined together on 2026-08-16 by reverse-engineering the
general concept from a screenshot Jason shared of a trading video, then
Jason making the concrete calls on level selection and confirmation
logic in conversation.

## Where this came from

Jason sent two videos, one showing a TradingView chart with an "Entry:
30033 / Stop: 30013 / Target: 30060" box near a sharp reversal at the NY
open, with several highlighted price levels drawn on the chart. Reading
the chart: price ground down into a highlighted level, reversed sharply,
and the entry/stop were both placed tight to that level rather than to
an arbitrary range. That's a specific instance of a generic, widely
taught trading concept — reacting to significant reference levels rather
than arbitrary time windows — not something proprietary to that video.
This is our own implementation of that general idea, not a copy of
anyone's code (which we never saw).

## Definition (as coded in `src/detect_level_sweep.py`)

1. **Levels, computed fresh each day:**
   - SUPPORT = the lower of {yesterday's low, today's pre-market low}
   - RESISTANCE = the higher of {yesterday's high, today's pre-market high}
2. **Watch window:** the 90 minutes starting at the 8:30 AM NY open.
3. **Sweep:** price trades through a level (e.g. a bar's low goes below
   support).
4. **Reversal confirmation — THREE VARIANTS, not yet decided between**
   (Jason reviewed this on 2026-08-16 and didn't have a strong enough
   feel from experience to pick one, so instead of guessing, all three
   are implemented and compared side by side — see `exp-006`/`exp-007`/
   `exp-008`):
   - `close_any` (the original rule): any bar's CLOSE moves back on the
     other side of the level — same bar that swept it, or a later one.
   - `close_min_distance`: the close must clear the level by at least
     `MIN_CONFIRM_DISTANCE_POINTS` (currently 5.0 points — an arbitrary
     illustrative placeholder, not tuned from data).
   - `full_bar_range`: the ENTIRE confirming bar (not just its close)
     must be back beyond the level. Strictly stronger than `close_any`;
     by construction this can never confirm on the same bar that did the
     sweep, only a later one.
   Select which one to run with `python3 src/detect_level_sweep.py <mode>`.
5. **Entry:** the close of the confirming bar.
   **Stop:** the most extreme price reached during the sweep.
   **Target (changed 2026-08-16):** `entry ± TARGET_R_MULTIPLE × risk`,
   where `TARGET_R_MULTIPLE = 1.35`. This replaced the original "target
   the opposite level" rule after Jason pointed out it didn't match the
   video: the video's actual trade (entry 30033, stop 30013, target
   30060) targeted only 27 points against 20 points of risk — a modest
   ~1.35x-risk target, not the far opposite level (price running 8-10x
   further afterward was what happened AFTER the trade, not the target
   itself). 1.35 is Jason's call, taken directly from that one concrete
   example — worth revisiting once there's more than one reference trade
   to calibrate from.

## Known limitations

- "Yesterday" and "pre-market" are computed from whatever data we have —
  on the synthetic dataset (6:00-11:00 AM window only) there's no true
  overnight session, so "pre-market" really just means "today, before
  8:30, within our narrow data window." Real (non-synthetic) data should
  make this much more meaningful, since it will actually include
  overnight hours.
- Only two levels (one support, one resistance) are considered per day —
  whichever is more extreme in each pair. A version that tracks more
  distinct levels (initial balance, weekly open, etc.) is a possible
  future refinement, not built yet.
- The confirmation rule (any close back beyond the level) is deliberately
  simple and may trigger on weak/marginal reversals — untested whether a
  stricter confirmation (e.g. a full bar's range fully back beyond the
  level) would filter better on real data.

## First test result

See `research/experiments/exp-003-level-sweep-synthetic-baseline.md` —
run on synthetic data, unprofitable (as expected/correct for random
data), but structurally distinct from the ORB setup: much lower win rate
(2.6%) with a much bigger average winner (+20R), i.e. this setup's shape
is "rare big wins" rather than ORB's "moderate wins/losses" shape — a
useful sanity check that the two setups aren't just producing the same
numbers by some pipeline bug.

## Real-data results (2026-08-16)

First run on real data (`exp-005`) with the original "opposite level"
target was strongly unprofitable (7.7% win rate, -0.822R expectancy) —
a near-zero win rate paired with a huge average winner, the fingerprint
of a target that's usually too far away to reach. After Jason reviewed
this file against the video reference and the target rule changed to
1.35x-risk (see above), all three confirmation variants turned
profitable on the same data:

| Variant | Win rate | Expectancy | Experiment |
|---|---|---|---|
| close_any | 50.0% | +0.132R | exp-006 |
| close_min_distance | 66.7% | +0.545R | exp-007 |
| full_bar_range | 53.3% | +0.238R | exp-008 |

**No variant has been picked as "the" setup yet** — each result is from
only 15-16 trades, too small a sample to trust the ranking above. This
table exists to track the comparison as more real data accumulates, not
to declare a winner.

## History

- 2026-08-16: defined and first tested (exp-003).
- 2026-08-16: first real-data test (exp-005), strongly unprofitable.
- 2026-08-16: Jason reviewed this definition against the video reference.
  Target rule changed from "opposite level" to a 1.35x-risk target
  (Jason's call, from the video's actual entry/stop/target). Confirmation
  rule split into three variants for comparison, since Jason didn't have
  a strong enough feel to pick one from experience (exp-006/007/008, all
  now profitable on the same real-data window — see table above). Levels,
  watch window, and sweep definition all left unchanged — Jason had no
  reason to revise those without evidence.
