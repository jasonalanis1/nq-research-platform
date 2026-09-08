# Intraday Behavior Batch 2 — Frozen Spec (2026-09-08)

Search batch ID: `batch-2026-09-08-intraday-behavior-2`. Step 1 only
(statistical, no costs, no trading rule). Pre-registered as one fixed
batch of exactly 3 conditions, same discipline as batch 1. Discovery
slice only. First batch sourced from the newly-established Market
Behavior Advisor role (docs/MARKET_BEHAVIOR_ADVISOR.md) rather than from
Claude's own reasoning over the ledger.

## Where these came from

The Market Behavior Advisor proposed 5 candidates, reasoned from trading
craft rather than from already-coded machinery, each checked against the
ledger for overlap: effort-vs-result absorption after a breakout attempt,
multi-day base-building before range expansion, a time-of-day lull/
re-engagement transition, overnight-range compression ("pre-open
coiling"), and trend-day-vs-range-day character established in the first
hour. 3 of the 5 were selected for this batch -- the cleanest to
operationalize precisely without further design work; the other 2 (lull/
re-engagement transition, overnight coiling) are logged in the backlog as
candidates for a future batch, not dropped.

## The 3 conditions

**exp-078 — Effort-vs-result absorption.** An "effort" bar is a 1-min bar
whose range AND volume both exceed `EFFORT_MULTIPLE=3.0`x their own
trailing 20-bar averages (same definition as hyp-000045's burst bars,
reused unmodified). Classify each effort bar as **stalled** (absorbed) if
the net range of the following `STALL_WINDOW_MIN=5` minutes is below
`STALL_RANGE_FRACTION=0.5`x the effort bar's own range AND the net
directional move over that window is below `STALL_MOVE_FRACTION=0.3`x the
effort bar's own move; otherwise **continued**. Outcome: cumulative
return over the following `FORWARD_HORIZON_MIN=30` minutes, signed
against the effort bar's own direction for the stalled group (reversal
test) and signed with the effort bar's own direction for the continued
group (continuation test) -- reported separately, no sign pinned on which
group wins. Different from hyp-000045 (single-bar burst continuation,
no stall/absorption component).

**exp-079 — Multi-day base-building breakout.** A "base" is
`BASE_DAYS=5` consecutive days whose combined range (max High to min Low
across the 5 days) is at or below `BASE_RANGE_MULTIPLE=1.5`x the average
single-day range over the same 5 days (i.e., 5 days moving roughly no
more than 1.5 normal single days' worth of total range). The day
immediately following a base is the "breakout day" if it closes outside
the base's high/low. Outcome: next day's (breakout day + 1) return,
signed in the breakout day's own direction (continuation test), no sign
pinned in advance. Different from hyp-000046/048 (single-day range vs.
next-day range ratio, not a multi-day base structure) and from Initial
Balance Breakout (a single-session, not multi-day, definition).

**exp-080 — Trend-day character from first-hour shape.** For each day,
compute the first-60-minute (9:30-10:30 ET) net directional move and its
maximum adverse excursion (MAE) -- the largest retracement against that
net move within the same window, as a fraction of the net move's size
("MAE%"). Classify days with MAE% in the bottom `SHAPE_PCTL=25` (most
one-directional, "trend-like") vs. top 25 (most two-way, "choppy").
Outcome: return from 10:30 ET to the session close, signed in the
first-hour's own net direction (continuation test) -- compare the
trend-like group's continuation to the choppy group's. Different from
Initial Balance Breakout (level-breakout rule) -- this is a shape/
retracement feature of the first hour itself, not a range-breakout test.

## Method

Nonparametric bootstrap, N_BOOTSTRAP=3000, seed=7, matching this
project's standard convention. 90% CI on each group's mean; a group
"passes" Step 1 if its CI is entirely off zero. No costs, no trading
rule, no Step 2 unless Step 1 clears. Any pass is logged PROMISING and
treated as provisional pending its own single pre-registered Validation-
slice prospective test, per the effect-size-inflation diagnostic's
finding -- not trusted on the Discovery-stage CI alone.

## Multiple-testing disclosure

3 pre-registered conditions (6 reportable groups total: exp-078
stalled/continued, exp-079 breakout-day-direction, exp-080 trend-like/
choppy), one shared `search_batch_id`, run together, no data-peeking
between them, no follow-up conditions added after seeing results.
