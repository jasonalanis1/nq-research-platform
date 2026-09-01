# exp-028 — Initial Balance Breakout, Discovery slice (real data)

**Date:** 2026-09-01
**Status:** kill (1654 resolved trades — largest sample of any setup tested in this project, statistically decisive)

## Hypothesis

First continuation-thesis test in this project. Every prior hypothesis
(Level Sweep Reversal's three variants, the FVG entry trigger, the
trend-structure liquidity filter) tested the same underlying bet — a
significant level sweeps, price reverses — and all six failed to clear
the promotion bar. This tests the opposite thesis: price breaks out of
the Initial Balance (the range set in the first 30 minutes after the
8:30 AM NY open, 8:30-9:00) and continues in that direction, per Market
Profile / Auction Market Theory. Full frozen definition:
`research/setups/initial-balance-breakout.md`.

Selected by Claude as research lead, at Jason's explicit direction, to
pick the next research area based on established market-structure
concepts rather than continuing to vary the already-six-times-failed
reversal thesis — see the setup doc's "Where this came from" section for
the full reasoning.

## Data used

`data/NQ_1min_databento_2026-08-20.csv`, Discovery slice only
(`data_split.get_discovery_data()`, 2015-01-01 through 2021-10-03, 2101
trading days) — the same slice every setup has been tested against since
exp-019.

## Method

`src/detect_ib_breakout.py` → `src/backtest.py`'s `simulate_trade()`
(reused unmodified) → `src/score_results.py` → `src/confidence_analysis.py`.

Because `detect_ib_breakout.scan_all_days()` re-filters the full
DataFrame by date on every call (too slow in this environment against
2101 Discovery days), a temporary driver
(`src/_run_ib_breakout_discovery_backtest.py`, deleted after use, not
part of the permanent pipeline -- same pattern as exp-025's
`_run_fvg_discovery_backtest.py`) pre-grouped the data by
day once and called the unmodified `detect_ib_breakout_for_day()` on
each day's pre-sliced group instead — a performance-only change, no
detection logic touched. Verified byte-identical to the real
`scan_all_days()` on a 200-day check slice (148 signals, exact match)
before trusting the full run.

## Results (net of estimated costs)

- 1709 raw signals (871 long, 838 short), 1654 resolved (55 unresolved),
  389 days had a degenerate or missing Initial Balance range (no trade),
  3 days had no breakout by noon.
- Win rate 42.6% (95% CI: 40.2%-44.9%).
- Average win +1.27R, average loss -1.07R.
- Expectancy -0.077R, profit factor 0.80 (raw points) / 0.88 (R-normalized),
  max drawdown -130.53R, total -126.85R.
- Bootstrap: 90% CI on total R across 1654 trades is **-202.05R to
  -48.21R — entirely below zero.** Only 0.2% of 1654-future-trade
  simulations ended net profitable.

## Interpretation

This is the largest and most decisive sample of any setup tested in this
project — bigger than the FVG entry trigger's 500 trades (the project's
previous most-decisive result) and more than 3x the old ORB placeholder's
493. The 90% CI sitting entirely below zero means "no real edge" isn't a
plausible read of this result; the data is consistent with a real,
negative expectancy as currently defined.

This also reinforces, rather than independently confirms, the project's
existing ORB placeholder finding: `exp-013` (2026-08-16, 493 trades,
-0.062R, "settled... no further testing planned") already found a
similarly-shaped breakout-continuation idea unprofitable, under the old
pre-Discovery-slice methodology. Two meaningfully different definitions
of "trade the breakout of an early-session range" — a naive 15-minute
window with an arbitrary range-width target, and a Market-Profile-
grounded 30-minute Initial Balance with the project's standard 1.35R
target — both now fail decisively. That consistency across two
independent definitions is itself a stronger signal against the broader
continuation thesis than either result alone.

389 of 2101 days (18.5%) had a degenerate or missing Initial Balance
range and produced no trade — worth noting for anyone revisiting this
setup, though not investigated further here since the result is already
decisive without those days.

## Next step

**Kill.** The continuation thesis, tested twice now under two different
definitions (the old ORB placeholder and this Initial Balance version),
has failed both times, the second time decisively on the largest sample
in the project. No further variants of "trade the breakout" are planned
without a specific, concrete reason to expect a different definition
would behave differently — continuing to vary parameters on a thesis
that has now failed twice would be exactly the kind of search this
project's integrity rules exist to prevent. Deciding what to test next
is the following step.
