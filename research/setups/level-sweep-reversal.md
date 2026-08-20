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

| Variant | ~24 days (Yahoo) | ~6 months (Databento) | ~2 years (Databento, incl. now-holdout period) | Research-only, 513 days | **Research-only, 514 days (2026-08-20)** | Experiments |
|---|---|---|---|---|---|---|
| close_any | +0.132R (16 trades) | -0.052R (68 trades) | -0.063R (237 trades) | not re-tested (already settled negative) | not re-tested | exp-006 / exp-010 / exp-014 |
| close_min_distance | +0.545R (15 trades) | +0.054R (63 trades) | +0.043R (221 trades) | -0.014R (173 trades) | **-0.021R (172 trades)** | exp-007 / exp-011 / exp-015 / exp-019 / exp-021 |
| full_bar_range | +0.238R (15 trades) | +0.033R (60 trades) | +0.042R (197 trades) | +0.008R (151 trades) | **-0.001R (150 trades)** | exp-008 / exp-012 / exp-016 / exp-020 / exp-022 |

(Expectancy in R, net of estimated costs, at each sample size.)

**Important correction (2026-08-16, exp-019/020):** the "~2 years"
column above is now known to have been misleading — it was run BEFORE
`src/data_holdout.py` existed, so it unknowingly included the 112 most
recent trading days that are now set aside as holdout. Once a genuinely
research-only test was run (excluding those 112 days), `close_min_distance`
**flipped negative** (-0.014R) and `full_bar_range` **shrank to roughly
breakeven** (+0.008R). This means a meaningful share of both variants'
apparent "stabilizing" edge was concentrated in the most recent ~4
months — exactly the kind of pattern that should raise suspicion of
overfitting/regime-dependency rather than confidence. Neither variant
currently shows a research-only edge worth acting on.

**Still no variant formally picked as "the" setup, but a clearer picture
has emerged across three sample sizes:** `close_any` looks settled as the
weakest — negative at both 6 months and 2 years, essentially the same
number both times (-0.052R, -0.063R). `close_min_distance` and
`full_bar_range` both **stabilized** going from 6 months to 2 years
(+0.054R→+0.043R and +0.033R→+0.042R respectively) rather than continuing
to shrink toward zero the way the 24-day→6-month jump did — the first
sign these two might reflect something real rather than pure small-sample
noise. They're also now close enough to each other (+0.043R vs +0.042R)
that the gap between them isn't meaningful on expectancy alone anymore.

None of this is proof of a tradeable edge — a few hundredths of an R per
trade is a thin margin before accounting for anything not modeled here
(e.g. real fills vs. assumed close-price entries, discretionary
judgment calls a human would actually make) — but it's a meaningfully
more encouraging signal than the 6-month checkpoint alone gave.

**Robustness check (exp-017/018, on the 2-year results):** Jason asked
two follow-up questions before trusting the "stabilized" result above.
(1) Is either variant's expectancy statistically distinguishable from
zero? **No** — a 90% bootstrap confidence interval on total R spans
comfortably negative to strongly positive for both (close_min_distance:
-18.89R to +37.08R; full_bar_range: -17.98R to +34.56R). (2) Does either
survive a stress test with double the assumed commission/slippage?
**Barely** — both stay positive, but drop to roughly a quarter of their
normal-cost expectancy (close_min_distance: +0.043R → +0.011R;
full_bar_range: +0.042R → +0.010R). Honest summary: neither variant has
a confirmed edge yet, and what edge the numbers do show is thin enough
that it wouldn't take much (real fills, Jason's actual broker costs
instead of the generic placeholder, a slightly worse stretch of trades)
to erase it.

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
- 2026-08-16: re-tested all three variants on ~6 months of real Databento
  data (exp-009/010/011/012, including the ORB comparison setup) instead
  of Yahoo's ~24-day window. All three edges compressed sharply;
  close_any flipped negative. See updated comparison table above.
- 2026-08-16: re-tested all three variants again on ~2 years of Databento
  data (exp-013/014/015/016), after Jason confirmed the cost (~$2.55,
  quoted before running) was trivial against his account balance.
  close_any confirmed negative; close_min_distance and full_bar_range
  both stabilized rather than continuing to shrink. See updated
  comparison table above.
- 2026-08-16: robustness-checked close_min_distance and full_bar_range's
  2-year results (exp-017/018) — bootstrap significance test (neither
  distinguishable from zero expectancy at 90% confidence) and a 2x
  cost-stress test (both survive, but barely). See notes above.
- 2026-08-16: a genuine out-of-sample holdout was carved out
  (`src/data_holdout.py`, 112 most-recent trading days set aside,
  untouched). Re-tested close_min_distance and full_bar_range against
  the research-only portion for the first time (exp-019/020) — both got
  meaningfully worse: close_min_distance flipped negative, full_bar_range
  shrank to roughly breakeven. See "Important correction" note above.
- 2026-08-20: `data_fetch_databento.py`'s rolling-window bug was fixed
  (anchored to a fixed 2024-08-15 start instead of a rolling window),
  adding one research day (513 -> 514). Re-tested both variants
  (exp-021/022) to confirm exp-019/020 weren't artifacts of the old,
  buggy window — both essentially unchanged: close_min_distance -0.014R
  -> -0.021R, full_bar_range +0.008R -> -0.001R (now dead flat). Neither
  shows a research-only edge worth acting on; the earlier
  "close_min_distance is the stronger of the two" read no longer clearly
  holds now that both are at or below breakeven.
