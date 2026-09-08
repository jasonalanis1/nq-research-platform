# Bar Behavior Batch 2: Engulfing + Three-Bar Sequence — Frozen Spec (2026-09-08)

exp-088/089/090 — second batch of daily-bar candle patterns, completing
the candle/bar-level family Jason asked for on 2026-09-08 (batch 1,
exp-066/067/068, covered rejection wicks and failed breakout — both
REJECTED). This batch covers the two remaining named patterns:
engulfing and multi-bar sequences. Search batch ID:
`batch-2026-09-08-bar-behavior-2`. Step 1 only, Discovery slice.

**Explicit pre-commitment (per the Path-to-Profitability Advisor,
agreed before running anything):** this is now the 5th distinct
daily/bar-level directional mechanism tested (wick rejection, failed
breakout, engulfing, multi-bar sequence, plus the earlier price/time
and alt-data families) — 0 have survived. If this batch also comes
back null, that is the trigger for a real "is NQ too efficient at
daily/intraday-bar resolution" conversation with Jason, not a quiet
pivot to a 6th candidate family.

## Reused, unmodified

`build_daily_bars`, `bootstrap_mean_ci`, `analyze_condition` from
`study_bar_behavior_batch1.py` — same daily-bar construction (4pm ET
reference close), same nonparametric bootstrap (N=3000, seed=7, 90%
CI), same single-sample-signed-to-prediction convention.

## The 3 conditions

**exp-088 — Bullish engulfing.** Day T's real body (Open-to-Close)
fully contains day T-1's real body, T-1 was a down day (Close < Open),
T is an up day (Close > Open). Classic reversal-signal folklore:
predicted direction = up. Outcome: day T+1's signed daily return.

**exp-089 — Bearish engulfing.** Mirror of exp-088: T's body fully
contains T-1's body, T-1 up, T down. Predicted direction = down.
Outcome: day T+1's signed daily return.

**exp-090 — Three-bar directional sequence (momentum continuation).**
Three consecutive days (T-2, T-1, T) all closing in the same direction
(all Close > Open, or all Close < Open) — deliberately tests the
CONTINUATION/strength folklore ("three white soldiers" /"three black
crows"), a genuinely different mechanism from batch 1's reversal-style
conditions (wick rejection, failed breakout) and from exp-088/089's
reversal framing — not a repeat of the same hypothesis shape.
Predicted direction = the 3-day sequence's own direction. Outcome: day
T+1's signed daily return.

## Method

Same as batch 1: nonparametric bootstrap, N_BOOTSTRAP=3000, seed=7, 90%
CI, Step 1 only (statistical, no costs). Credible = the signed-to-
prediction CI's lower bound is above zero (same convention as
exp-066/067/068's `analyze_condition`). Any Step-1 PASS with n >= 40
(this project's working threshold for "not too thin to prospective-
test," consistent with the exp-051/hyp-000051 n=9 precedent on the
other side) gets a single pre-registered Validation-slice prospective
test; anything thinner is flagged and not tested further, same as
exp-079.

## Multiple-testing disclosure

3 pre-registered conditions, one shared `search_batch_id`, run
together, no follow-up conditions or threshold changes after seeing
results.
