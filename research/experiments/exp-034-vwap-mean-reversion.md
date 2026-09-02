# exp-034 — VWAP Mean Reversion, Discovery slice (real data)

**Date:** 2026-09-02
**Status:** kill (2066 resolved trades — largest sample and most decisive rejection of any setup tested in this project)

## Hypothesis

First setup in this project sourced from external day-trading-technique
research rather than a market-structure concept applied fresh or a
direct mechanical translation of one of this project's own
characterization findings. Jason asked, after Fade the Gap's rejection,
for research into how real day traders operate and which techniques are
widely used, as a source for the next hypothesis. Full research and
filtering reasoning, plus why VWAP mean reversion specifically was
chosen over ICT liquidity concepts, volume profile/value area
reversion, floor-trader pivot points, and further ORB variants:
`research/setups/vwap-mean-reversion.md`.

Core claim: session VWAP (cumulative volume-weighted average price from
the 8:30 open) is a real institutional execution benchmark, not a
technical chart level, and a close beyond its 2-sigma band tends to
revert back toward it.

## Data used

`data/NQ_1min_databento_2026-08-20.csv`, Discovery slice only
(`data_split.get_discovery_data()`, 2015-01-01 through 2021-10-03, 2101
trading days) — the same slice every setup has been tested against
since exp-019.

## Method

`src/detect_vwap_reversion.py` (reusing `detect_ib_breakout.py`'s
`OPEN_HOUR`/`OPEN_MINUTE`, not reimplemented) → `backtest.py`'s own
unmodified `simulate_trade()` (no time cutoff, unlike Fade the Gap) →
`src/score_results.py` → `src/confidence_analysis.py`.

Because `detect_vwap_reversion.scan_all_days()` re-filters the full
DataFrame by date on every call (too slow against 2101 Discovery days
in this environment), a temporary driver
(`src/_run_vwap_reversion_discovery.py`, deleted after use, not part of
the permanent pipeline) pre-grouped the data by day once and called the
unmodified `detect_vwap_reversion_for_day()` on each day's pre-sliced
group instead — a performance-only change, no detection logic touched.
Verified byte-identical to the real `scan_all_days()` on a 200-day
check slice before trusting the full run.

**Two real bugs found and fixed during testing, before trusting any
result — both changing the frozen definition from its first draft:**

1. **Stop placed on the wrong side of entry.** The first version
   defined the stop as a fixed `VWAP +/- 3*sigma` band level, assuming
   entry always sits close to the 2-sigma trigger line. A diagnostic
   check on 300 real Discovery days found the entry's actual distance
   from VWAP at signal time averaged 3.57 sigma (median 2.29, max 176) —
   a fast 1-minute move can close well past 2 sigma, sometimes past
   where the fixed 3-sigma stop would have been. On the first real
   backtest attempt this produced obviously broken statistics (average
   win +2.62R, exceeding the intended +2R ceiling; average loss -2.49R,
   exceeding the intended -1R floor) — a bookkeeping artifact of the
   stop definition, not a real result. Confirmed directly: 51/296 (17%)
   of signals in that diagnostic sample had a stop already on the wrong
   side of entry. Fixed by anchoring the stop to ENTRY (always exactly
   1 sigma away, same direction as the excursion) instead of a fixed
   absolute band level — this makes risk always exactly 1 sigma by
   construction, regardless of how far past the 2-sigma trigger the
   actual close landed. Covered by a new regression test,
   `test_stop_stays_on_adverse_side_even_for_a_large_overshoot`.
2. **Zero-risk signals after rounding.** Even after fix #1, 11 of 2081
   signals on the real run had `r_multiple_net` come out `NaN`,
   breaking `confidence_analysis.py`'s bootstrap entirely (every
   reported number came out `NaN`). Cause: when sigma is a tiny
   fraction of a point (a very quiet stretch right after warmup),
   rounding entry and stop to the instrument's usual 2-decimal
   convention can collapse them to the identical price — a zero-risk
   signal after rounding, the same failure class as
   `detect_fvg_entry.py`'s earlier zero-risk-signal fix in this
   project. Fixed by skipping such a bar and continuing to watch for a
   later, non-degenerate signal that day, rather than returning a
   degenerate one. Covered by a new regression test,
   `test_zero_risk_signal_skipped_after_rounding`.

Both fixes are documented in the setup doc's own Definition section (not
silently corrected) and in `src/detect_vwap_reversion.py`'s docstring.

## Results (net of estimated costs)

- 2081 raw signals (1009 long, 1072 short) on 2081 of 2101 Discovery
  days (20 days had no 2-sigma band touch after the 30-minute warmup
  window at all).
- 2066 resolved, 15 unresolved (neither level hit before the day's
  data ended).
- Win rate 28.7% (95% CI: 26.7%-30.6%).
- Average win +1.93R, average loss -1.65R.
- Expectancy -0.628R, profit factor 0.79 (raw points) / 0.47
  (R-normalized), max drawdown -1297.78R, total -1296.70R.
- Bootstrap: 90% CI on total R across 2066 trades is **-1450.38R to
  -1134.35R — entirely below zero.** 0.0% of 2066-future-trade
  simulations ended net profitable.

## Interpretation

**This is the largest and most decisive rejection in this project's
history** — larger than Initial Balance Breakout's 1654 trades and
nearly twice the resolved sample, with a total R loss (-1296.70R) an
order of magnitude worse than any prior setup. The 90% CI sitting
entirely below zero, with 0% of forward-projected simulations
profitable, leaves no real ambiguity: "no edge" is not the right
description of this result either — the data is consistent with a
real, decisively negative expectancy as defined.

**Why so many signals, and what that says about the setup's own
design.** 2081 signals on 2081 of 2101 days — a nearly daily
occurrence — is a real property worth being honest about, not a sign
of a bug. Every other reversion-style setup in this project (Level
Sweep Reversal, Fade the Gap) fires on a comparatively rare, specific
event. VWAP Mean Reversion's watch window runs from 9:00 AM ET through
the end of whatever data exists for that calendar day — for this
near-24-hour-traded instrument, that can be 12+ hours. Over a window
that long, some 2-sigma excursion off the session's own cumulative
VWAP is close to inevitable, which means this setup is really testing
"the first sizeable stretch away from VWAP on almost any given day,"
not the comparatively rare "extreme, exhausted move" the source
material's framing implied. That framing gap — not the band math
itself — is arguably the more important honest finding here: a
technique described in trading education content as identifying
selective, high-conviction setups turns out, once defined precisely
and run against a full session, to fire on 99% of days.

**A win rate of 28.7% against a built-in 2:1-or-better R:R is a
meaningfully worse result than a coin flip would need to break even
here** (roughly 33% at exactly 2:1, more once the realized average
win/loss ratio of about 1.17:1 — pulled down from the 2:1 floor by
costs and the sizing of unresolved-at-noon-equivalent exits — is used
instead). This is not a close call.

The two bugs found and fixed during this test are worth restating for
the record: both were caught BEFORE trusting any result (the first via
a diagnostic on real data showing broken statistics, the second via a
downstream tool — `confidence_analysis.py` — silently producing `NaN`
across the board), both are now unit-tested regressions, and neither
was a data-driven retuning — both were corrections to make the
implementation match the frozen definition's own stated intent ("risk
is exactly 1 sigma by construction").

## Next step

**Kill.** The core VWAP-reversion claim, tested as directly and
literally as the source material's own band structure supports, fails
decisively and on the largest sample yet collected in this project. Two
honest, narrower follow-up directions exist if VWAP is revisited later
— a bounded intraday watch window (matching this project's other
morning-session setups, rather than running to end of data) to test
whether the "near-daily occurrence" issue was masking a real effect at
a more selective threshold, or a higher sigma multiple (e.g. 2.5 or 3)
requiring a genuinely rarer excursion before triggering — but neither is
being pursued automatically here; per this project's standing
discipline, that would need its own specific justification rather than
being tried just because the first version didn't work. Logged as
`hyp-000013`, REJECTED.
