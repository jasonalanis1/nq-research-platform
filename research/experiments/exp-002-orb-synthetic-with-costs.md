# exp-002 — ORB synthetic baseline, now with cost modeling + confidence range

**Date:** 2026-08-16
**Status:** retest (pipeline validation run, not a real edge test)
**Supersedes (in relevance, not in record):** exp-001 — that entry stays
as-is, unedited, per the project's rules. This is a new entry, not a
correction of the old one.

## What changed vs exp-001

Same setup (ORB placeholder), same synthetic data, same detection logic.
Two additions to the pipeline itself:

1. **Cost modeling** — `backtest.py` now subtracts an estimated
   round-trip cost (commission + slippage) from every resolved trade
   before computing R-multiples. Previously, results were 100% gross
   (frictionless), which flattered every result. See placeholder cost
   assumptions in `src/backtest.py`'s header — these are NOT Jason's
   real costs yet.
2. **Confidence range** — `score_results.py` now reports a rough 95%
   confidence interval on the win rate, and a new script,
   `confidence_analysis.py`, bootstrap-resamples the trade results to
   show a realistic spread of plausible outcomes rather than one single
   number.

## Results (net of estimated costs)

- 46 resolved trades, same as exp-001 (cost modeling doesn't change which
  trades resolve, only what they're worth after costs).
- Win rate: 37.0% (rough 95% confidence range: 23.0%-50.9% — WIDE, because
  46 trades is a small sample; this range should narrow a lot with more
  real trades).
- Expectancy: -0.307R (vs -0.287R gross in exp-001 — costs made a small
  but real negative setup slightly worse, as expected).
- Bootstrap reshuffle of these same 46 trades: median final result -14.23R,
  5th-95th percentile range -24.11R to -4.07R — even reshuffling the exact
  same trades, there's no version of this that ends up profitable.
- Bootstrap projection of 100 more trades (assuming the same distribution
  holds): only 0.1% of simulations ended up net profitable.

## Interpretation

Consistent with exp-001: this is synthetic random-walk data, so a real
setup correctly shows no edge on it. The new pieces here (cost modeling,
confidence range) are validated as working correctly — the win rate CI is
appropriately wide given the small sample, and the bootstrap simulations
correctly show "no plausible path to profitability" on data that has no
real structure to find an edge in. That consistency across the reshuffle
and the forward projection is itself a good sign the analysis method
isn't secretly biased.

## Next step

Same as exp-001: real data + Jason's actual setup. When that happens, pay
attention to whether the confidence interval is narrow enough to trust
(more trades = narrower) before treating any positive result as meaningful.
