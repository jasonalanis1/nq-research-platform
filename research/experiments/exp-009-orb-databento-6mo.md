# exp-009 — Opening Range Breakout, 6-month Databento real data

**Date:** 2026-08-16
**Status:** retest (125 trades — big enough sample to take seriously, still just one setup/data-source combination)

## Hypothesis

Same placeholder ORB definition as exp-001/002/004. This run's purpose:
does exp-004's positive result (+0.206R, 19 trades, Yahoo's ~24-day
window) hold up with roughly 6x more data from a better data source?

## Data used

First run on Databento data: `data/NQ_1min_databento_2026-08-16.csv`,
176,174 rows of real 1-minute NQ futures bars (CME Globex GLBX.MDP3
feed, continuous front-month `NQ.c.0`), 2026-02-15 through 2026-08-14
(~6 months). Note: Databento flagged a few days (2026-03-15, 03-16,
03-21, possibly others) as "reduced quality" in this feed — not fixed or
excluded, just worth remembering if results look odd around those dates.

Getting this file to load also surfaced and fixed a real bug: `pd.read_csv(...,
parse_dates=True)` (used identically in 5 different scripts) silently
fails to parse timestamps when a file's date range spans a Daylight
Saving Time change (mixed UTC offsets, e.g. -05:00 in February vs -04:00
in August) — Yahoo's short ~24-day pulls never crossed DST, so this
never surfaced before. Fixed by parsing with `utc=True` first, then
converting to New York time, in all 5 places.

## Method

`src/detect_setups.py` → `src/backtest.py` → `src/score_results.py` →
`src/confidence_analysis.py`. No parameter changes from exp-004 — same
setup logic, only the underlying data changed.

## Results (net of estimated costs)

- 128 signals, 125 resolved (3 unresolved).
- Win rate 52.0% (95% CI: 43.2%-60.8%) — a much tighter, more trustworthy
  range now that we're past 30 trades.
- Average win +0.88R, average loss -1.01R.
- Expectancy -0.028R, profit factor 0.80, max drawdown -18.50R, total -3.51R.
- Bootstrap: only 37.1% of 100-future-trade simulations ended net profitable.

## Interpretation

exp-004's positive result did NOT hold up. -0.028R is essentially
breakeven-to-slightly-negative, a meaningfully different (and more
trustworthy, given the sample size) picture than exp-004's +0.206R on
just 19 trades. This is a useful, sobering example of exactly why this
project's confidence-interval and sample-size warnings exist: a small
sample can look good by chance. Still a generic placeholder setup, not
Jason's real trading idea — this isn't a verdict on whether ORB-style
setups can work, just on this specific untuned version.

## Next step

No further action planned for the ORB placeholder specifically — it
remains a reference/pipeline-validation setup, not something Jason
trades. Keep it around for comparison as Level Sweep Reversal (his real
candidate) continues to develop.
