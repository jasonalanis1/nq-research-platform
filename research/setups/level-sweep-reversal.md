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
4. **Reversal confirmation:** a bar's CLOSE moves back on the other side
   of the level — can be the same bar that swept it (the cleanest case,
   matching what was visible in the video) or a later bar.
5. **Entry:** the close of the confirming bar.
   **Stop:** the most extreme price reached during the sweep.
   **Target:** the opposite level (support swept → target resistance, and
   vice versa), falling back to a 1x-risk target if the opposite level
   isn't a sensible distance away.

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

## History

- 2026-08-16: defined and first tested (exp-003).
