# Pre-Move Behavior, Fresh Setups Batch 3 — Frozen Spec (exp-104/105)

## Why these two, not more variants of batch 1/2

Batch 1/2 closed volume-vacuum and trend-alignment (both directions,
both credibly losing -- an entry-timing problem, not a directional
one). These are two genuinely different mechanisms, using a different
data dimension (signed volume) and a different reference (a fixed
external level, not a rolling window) respectively -- not flips or
retunes of anything already tested.

## exp-104: Opening Signed-Volume Imbalance

**Idea:** A crude order-flow proxy from OHLCV alone (no real order-flow
data -- that was already priced out at ~$54k/yr and dropped). For each
1-min bar in the opening 30 minutes (09:30-10:00 RTH), compute
`sign(Close - Open) * Volume` and sum it -- a rough measure of whether
buying or selling volume dominated the open. If the sign of that sum is
non-zero, trade in that direction starting at 10:00.

**Detection:** `imbalance = sum(sign(bar.Close - bar.Open) * bar.Volume
for bar in 09:30-10:00 bars)`. Long if `imbalance > 0`, short if
`imbalance < 0`, no trade if exactly 0. Entry: 10:00 bar's open. Stop:
opening 30-min window's opposite extreme (low for long, high for
short). Target: entry +/- 1.35R.

## exp-105: Prior-Close Rejection

**Idea:** A fixed, universally-watched reference level (yesterday's RTH
close/settlement), not a rolling price window -- genuinely different
reference type from every prior setup (which all used either a
same-day range, a swing point, or a rolling percentile).

**Detection:** Watch the first touch of the prior RTH day's closing
price during 09:30-12:00. "Touch" = a bar whose High >= prior_close >=
Low (price traded through/at the level) after having been on one side
of it since the open. Look at the next `CONFIRM_BARS = 3` bars after
the touch bar: "rejection" = price closes back on the SAME side of the
level it approached FROM, for all 3 confirm bars (i.e., it failed to
hold beyond the level) -- trade fading back in the direction it came
from (continuation of the pre-touch approach direction). No signal if
price holds beyond the level (that's acceptance, not tested here -- a
separate, later hypothesis if this rejection variant is worth
following up). Entry: close of the 3rd confirm bar. Stop: beyond the
touch bar's extreme on the level side (a small buffer:
`prior_close +/- 2 * average 1-min range over the prior 20 bars`, sized
to survive a further wick through the level without being unreasonably
wide). Target: entry +/- 1.35R.

## Method

Identical to batch 1/2: Step 1+2 together, costed via
`backtest.simulate_trade`, `ROUND_TRIP_COST_POINTS` unmodified.
Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000, seed=7, 90% CI. Credible
= CI entirely above zero AND mean R-multiple net of cost >= 0.05R.

## Multiple-testing disclosure

2 pre-registered setups, one shared `search_batch_id`
(`batch-2026-09-08-pre-move-behavior-3`), run together. No follow-up
variants (including fades) without a new independently motivated
reason, consistent with how batch 1 earned its one fade follow-up by
coming back credibly losing rather than merely null.

## Decision rule / pre-commitment

Same promotion path as every setup in this project: credible +
economically-meaningful + n >= 40 earns a single Validation-slice
prospective test. A null (or credibly-losing) result on either does not
end the fresh-behavior direction -- Jason's standing instruction is to
keep investigating even through failed first trials.
