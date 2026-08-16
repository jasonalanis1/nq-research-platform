# exp-004 — Opening Range Breakout, first REAL-data run

**Date:** 2026-08-16
**Status:** retest (tiny sample — 19 trades — not yet a trustworthy verdict)

## Hypothesis

Same as exp-001/exp-002: the placeholder ORB definition (15-min opening
range, 60-min watch window, 1x-range target) has an edge at the NQ 8:30
NY open. Still a generic placeholder, not Jason's actual setup — see
`research/setups/orb-placeholder.md`.

## Data used

First REAL data pulled by `src/data_fetch.py`: `data/NQ_1min_2026-08-16.csv`,
27,358 rows of 1-minute NQ=F bars from Yahoo Finance, 2026-07-19 through
2026-08-14 (~24 trading days). This run also fixed a bug in
`data_fetch.py`: it previously assumed Yahoo allows 59 days of 1-minute
history in one request; Yahoo's real limit is 30 days total, fetched in
chunks of ~8 days per request. The script now loops over 7-day windows
and stitches them together.

## Method

`src/detect_setups.py` → `src/backtest.py` → `src/score_results.py` →
`src/confidence_analysis.py`. No parameter changes from exp-002 — same
setup logic, only the underlying data changed from synthetic to real.

Also fixed along the way: `score_results.py` and `confidence_analysis.py`
previously had a hardcoded "SYNTHETIC DATA" label in their output/chart
titles regardless of what data was actually used — cosmetic but
misleading. `backtest.py` now records an `is_synthetic` column in its
results CSV, and both scripts read it to label output correctly.

## Results (net of estimated costs)

- 24 days scanned, 20 signals (12 long, 8 short), 4 days with no breakout.
- 19 of 20 resolved; win rate 63.2% (95% CI: 41.5%-84.8%).
- Average win +0.92R, average loss -1.01R.
- Expectancy +0.206R, profit factor 1.38, max drawdown -3.58R, total +3.91R.
- Bootstrap: 98.8% of 100-future-trade simulations ended net profitable.

## Interpretation

First positive result on real data — but treat this as "interesting, not
proven." 19 trades is a very small sample (the confidence interval on win
rate spans 41%-85%, which is wide enough to be nearly uninformative on
its own), and this is a generic placeholder setup, not Jason's real
trading idea. Do not read this as "ORB works" — read it as "the pipeline
now runs cleanly end-to-end on real data, and the placeholder happened to
come out positive on this one ~24-day window." More data (as more days
accumulate) and, more importantly, Jason's actual setup logic are what
would make a result here meaningful.

## Next step

Keep accumulating real data over time (Yahoo only gives a rolling 30-day
window for 1-minute bars, so re-running `data_fetch.py` periodically and
keeping the dated CSVs is how history builds up beyond what one pull
covers). Prioritize refining Level Sweep Reversal (exp-005) since that's
closer to Jason's actual idea.
