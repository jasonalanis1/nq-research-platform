# exp-019 — Level Sweep Reversal, "close_min_distance", first genuinely holdout-respecting test

**Setup:** Level Sweep Reversal
**Variant:** close_min_distance
**Date:** 2026-08-16
**Sample Size:** 173 resolved trades
**Statistically Significant:** No (90% bootstrap CI on total R: -26.38R to +21.45R, spans zero)
**Status:** retest (edge flipped negative once holdout period excluded — see interpretation)

## Hypothesis

Same as exp-007/011/015/017 (close_min_distance confirmation + 1.35x-risk
video-derived target). This run's purpose: exp-015/017 were both run
BEFORE `src/data_holdout.py` existed, so they unknowingly included the
112 most-recent trading days that are now classified as holdout data.
This is the first test of this variant run through the holdout-respecting
pipeline — i.e. the first number here that's actually safe to call
"research-only."

## Data used

`data/NQ_1min_databento_2026-08-16.csv` — Greg re-ran
`data_fetch_databento.py` first to check for anything new since the last
pull; **no new data was available** (identical 698,873 rows, same
2024-08-15 → 2026-08-14 range — Databento's most recently complete
session is still Aug 14). The change in this experiment isn't from new
data; it's from `backtest.py`/`detect_level_sweep.py` now automatically
excluding the 112 holdout days (2026-04-07 onward) that exp-015/017
inadvertently included. Research window used: 2024-08-15 → 2026-04-06,
513 trading days.

## Method

`src/detect_level_sweep.py close_min_distance` →
`src/backtest.py setups_level_sweep_close_min_distance.csv` →
`src/score_results.py backtest_results_level_sweep_close_min_distance.csv` →
`src/confidence_analysis.py backtest_results_level_sweep_close_min_distance.csv`.
Console output confirmed the holdout boundary was applied at every step
("using 513 research trading day(s), excluded 112 holdout day(s)").

## Results (net of estimated costs)

- 175 signals, 173 resolved (2 unresolved).
- Win rate 43.4% (95% CI: 36.0%-50.7%).
- Average win +1.32R, average loss -1.03R.
- Expectancy **-0.014R** (profit factor 1.18, max drawdown -14.85R, total -2.35R).
- Bootstrap: 90% CI on total R is -26.38R to +21.45R (includes zero —
  not statistically significant). Only 43.9% of 173-future-trade
  simulations ended net profitable.

## Interpretation

**The expectancy flipped from positive to negative** once the holdout
period was excluded: exp-017 (same variant, same underlying 2-year
data, but including the now-holdout period) showed +0.043R normal-cost
/ +0.011R stress-cost over 221 trades; this run shows -0.014R over 173
trades. That's a meaningful, honest finding — it means a real chunk of
this variant's apparent edge was concentrated in the most recent ~4
months of data, which is exactly the period now set aside as holdout.
That's not necessarily damning on its own (recent months could
plausibly have been a stronger regime for this pattern), but it's also
exactly the kind of thing that should make you MORE cautious, not less:
a large positive change in expectancy from removing one specific date
range is a classic overfitting/regime-dependency warning sign, not a
reason to think the "real" number is still +0.043R and we're just
temporarily missing some of it.

## Next step

No winner still being picked between the variants. This result argues
for patience — the holdout period exists specifically so a future
one-time check can tell us whether the strength seen in
exp-015/016/017/018 was real or was mostly concentrated in that
excluded window. Continue tracking `close_min_distance` and
`full_bar_range` (exp-020) as real data accumulates, but treat both as
weaker candidates than they looked in earlier sessions, not stronger.

## Note on multiple-testing history

This run (and exp-020) is the fifth round of testing on this
close_min_distance / full_bar_range comparison, following four earlier
rounds (exp-006-008, exp-010-012, exp-014-016, exp-017-018) on
substantially overlapping data, during which a third variant
(close_any) was dropped as weakest. The "not statistically significant"
bootstrap CI reported above treats this as an isolated test and does
not account for that prior selection history. The practical verdict is
unchanged either way (both were already not significant) — this note
exists for the record's honesty, not because it changes the conclusion.
