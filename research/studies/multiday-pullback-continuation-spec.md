# Multi-Day Pullback Continuation — Frozen Spec (exp-108)

## Why this, not another same-day trigger

exp-100 through exp-107 (7 tests, single-day reactive triggers) all
found gross edge close to zero -- closed per their own pre-commitment.
This is a structurally different direction: a slower, multi-day SWING
setup (trade held for days, not exited same day), the one genuinely
untested structure identified in the 2026-09-08 staff meeting/report.
Daily-bar CANDLE PATTERNS were tested exhaustively (batches 1/2/intraday,
65+ hypotheses) but always with a NEXT-DAY-ONLY outcome measure -- never
a real multi-day HELD TRADE with its own stop/target/timeout. This tests
that missing structure: does an established trend + pullback entry,
given room (days, not hours) to work, behave differently from a same-day
trigger judged on a single day's return?

## Setup: 20-day-MA pullback, trend continuation

**Trend context (daily bars, Discovery only, `build_daily_bars` reused
unmodified from `study_bar_behavior_batch1.py`):**
`TREND_MA = 50` trading days. Uptrend on day T if `Close[T] >
SMA50[T]` AND `SMA50[T] > SMA50[T-10]` (the average itself is rising).
Downtrend is the mirror condition. No trend if neither holds.

**Pullback entry:** `PULLBACK_MA = 20` trading days.
- Uptrend: yesterday's close was below `SMA20`, today's close is back
  above it (first close-back-above after a dip) -> LONG.
- Downtrend: mirror (close back below SMA20 after a pullback up) ->
  SHORT.
- Only the FIRST such re-cross per trend segment counts (no re-entry
  until the trend context itself changes) -- avoids double-counting a
  choppy MA-straddling stretch as many separate "signals."

**Stop:** `ATR_WINDOW = 14` trading days (Wilder-style simple rolling
mean of daily True Range, reused convention from
`pilot_stop_target_tabulation.py`/`study_asymmetric_stop_target_overlay.py`,
both already use `ATR_WINDOW_DAYS = 20` for a slower cadence -- this
setup uses the more standard 14-day window since it's a faster,
pullback-specific stop, not a slow regime filter). Stop = entry -/+
`1.5 * ATR14` in the trade's direction.

**Target:** entry +/- `TARGET_R_MULTIPLE (1.35, imported unmodified
from detect_level_sweep.py)` * risk -- same standard as every setup in
this project, held for as many days as it takes.

**Timeout:** `MAX_HOLD_DAYS = 20` trading days. If neither stop nor
target is touched by then, exit at that day's Close (mark-to-market,
not a forced win or loss).

**Simulation walk-forward (new mechanism -- multi-day, not
`backtest.simulate_trade` which is single-day-bounded):** starting the
day AFTER the signal day, walk forward day by day using daily High/Low
to check stop/target touches (stop-priority if both touch the same day,
conservative convention consistent with this project's existing
same-day tie-breaking in `backtest.py`). `ROUND_TRIP_COST_POINTS`
(unmodified, 0.75) applied once at exit, same as every other setup.

## Method

Step 1+2 together. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Multiple-testing disclosure

1 pre-registered setup, `search_batch_id
batch-2026-09-08-multiday-pullback`. No follow-up variants without a
new independently motivated reason.

## Decision rule / pre-commitment

Credible + economically-meaningful + n >= 40 earns a single Validation-
slice prospective test before any promotion consideration -- standard
path. A null result here means BOTH the fast (single-day) and slow
(multi-day swing) structures have now been tried on this general
"trend/pullback" family without success, which would be a genuinely
comprehensive negative result worth a direct report to Jason rather
than an immediate further variant.
