# exp-025 — FVG Entry Trigger, first test on the Discovery slice (2015-2021)

**Setup:** Level Sweep Reversal base + Fair Value Gap Entry Trigger (per `research/setups/fvg-entry-trigger.md`)
**Variant:** fvg_entry_close_any (base rejection gated by `close_any`, per the frozen doc's documented choice)
**Date:** 2026-08-24
**Sample Size:** 500 resolved trades
**Statistically Significant:** **Yes** (90% bootstrap CI on total R: -149.41R to -59.02R, entirely below zero)
**Status:** kill — first statistically decisive result in the project, clearly negative

## Hypothesis

First test of `research/setups/fvg-entry-trigger.md`'s frozen definition:
unchanged Level Sweep Reversal level selection and sweep/rejection logic
(gated by `close_any`), but replacing the "close back beyond the level"
entry with a 3-candle Fair Value Gap that must form within 30 minutes of
rejection. Detection logic lives in `src/detect_fvg_entry.py`, built by
reusing `detect_level_sweep.py`'s `compute_levels()`/`scan_for_signal()`
unchanged (see that file's own docstring for the two implementation
decisions not specified in the frozen doc: `close_any` as the rejection
gate, and "3-candle" meaning 3 consecutive data rows).

## Data used

`data/NQ_1min_databento_2026-08-20.csv`, sliced through
`data_split.get_discovery_data()` — legacy holdout (2026-04-07+) excluded
first via `data_holdout.py`, then restricted to 2021-10-03 or earlier.
2101 discovery trading days available. Same slice as exp-023/024, so
this result is directly comparable to both.

## Method

A temporary driver (`src/_run_fvg_discovery_backtest.py`, deleted after
use, not part of the permanent pipeline) called
`detect_fvg_entry.generate_signals()` — the Signal-contract output — and
adapted it into the CSV shape `backtest.py`'s `simulate_trade()` expects
(`backtest.py` itself isn't wired to consume `Signal` objects yet, per
`strategy_contract.py`'s own status note). `score_results.py` and
`confidence_analysis.py` then ran unmodified against the result.

**A bug was found and fixed before this result was trustworthy.** The
first run produced 3 signals (of 635) with `entry == stop == target`
exactly — a zero-risk "trade" that can't be sized or scored, which
`float('nan')`'d their R-multiple and, via bootstrap resampling, turned
*every* confidence-interval number `NaN` (with only 3 poisoned rows out
of 622, ~95% of the 2000 bootstrap resamples ended up including at least
one). Traced to a real, reproducible case: unlike the original
close-back-beyond-level entry (structurally always on the opposite side
of the level from the stop), this variant's FVG-based entry has no such
guarantee — a later candle's close can coincidentally land on the exact
same price as the earlier sweep extreme. Fixed in `detect_fvg_entry.py`
by treating zero-or-negative-risk FVG matches as a no-trade outcome
(counted separately as `degenerate_zero_risk_days`) rather than emitting
them as signals. Verified via a new regression test
(`test_zero_risk_fvg_is_discarded_not_emitted`, 8th case in
`tests/test_detect_fvg_entry.py`), the full test suite (23/23 passing),
and a direct check of the re-run output (`entry == stop` count: 0,
`NaN` count: 0) before trusting the numbers below.

## Results (net of estimated costs)

- 513 signals, 500 resolved (13 unresolved).
- Win rate 41.0% (95% CI: 36.7%-45.3%).
- Average win +1.22R, average loss -1.20R.
- Expectancy **-0.208R** (profit factor 1.13 — see note below on why
  this doesn't contradict a negative expectancy — max drawdown -111.31R,
  total -104.11R).
- Bootstrap: 90% CI on total R is **-149.41R to -59.02R** — does NOT
  include zero. 0.0% of 500-future-trade simulations ended net
  profitable.

**Note on profit factor (1.13) appearing to contradict a negative
expectancy (-0.208R): both numbers are net of estimated costs** —
`score_results.py` computes `profit_factor` from the same
`pnl_points_net` column `r_multiple_net` is derived from, confirmed by
reading the source directly. The apparent contradiction is a units
issue, not a bug: `profit_factor` sums raw price *points* won vs. lost
with no per-trade risk normalization, while `expectancy` averages
*R-multiples* (each trade's P&L divided by that trade's own risk).
Checked directly against this run's data: winning trades average 16.2
points of risk vs. 12.3 points for losing trades — winners systematically
carry wider stops in this variant, since entry is decoupled from the
level and no longer tied to how far price traveled to sweep it. That
inflates the raw-point total enough to land just above breakeven in
point-space (4334 points won vs. 3850 lost), even though the trade loses
far more often than not in risk-normalized space (295 losses vs. 205
wins) — which is the number that actually determines whether this is
tradeable, since a real position is sized in R, not raw points. Logged
to `docs/BACKLOG.md` as a general `score_results.py` improvement
(an R-normalized profit factor alongside the existing one), since this
divergence has always been possible for any setup with variable
per-trade risk — it just hadn't shown up clearly before this variant.

## Interpretation

**This is the first statistically decisive result in the project's
history.** Every prior test of Level Sweep Reversal's three original
confirmation variants (`close_any`, `close_min_distance`,
`full_bar_range`, across exp-006 through exp-024) came back with a 90%
bootstrap CI spanning zero — "no real edge" was always a plausible
explanation for whatever the point estimate showed. Here, the CI
(-149.41R to -59.02R) sits entirely below zero: the data is more
consistent with a real negative effect from swapping in the FVG entry
than with no effect at all. Combined with a win rate meaningfully below
50% (41.0%, CI 36.7%-45.3%, not overlapping a coin flip) and 0% of
bootstrap-projected future sequences ending profitable, this isn't a
borderline or thin result the way close_min_distance/full_bar_range's
results have consistently been — it's a clear kill.

## Next step

Recommend treating the FVG entry trigger as settled negative on this
evidence — the first variant in this project decisive enough not to
need a second confirming test before drawing that conclusion. Per
`docs/RESEARCH_ARCHITECTURE.md`'s standing priorities, this closes out
the `docs/BACKLOG.md` FVG idea as tested rather than still-open. The
zero-risk-signal bug fix and profit-factor unit-mismatch finding are
both logged in `docs/BACKLOG.md` as follow-up engineering items,
separate from this experiment's verdict.
