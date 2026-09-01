# exp-030 — Volume-Confirmed Initial Balance Breakout, Discovery slice (real data)

**Date:** 2026-09-01
**Type:** Characterization + conditional filter test, per
`research/setups/volume-confirmed-ib-breakout.md`'s two-step plan. Step
1 (raw correlation) ran; Step 2 (bucket-split backtest) was correctly
**skipped** because Step 1 didn't warrant it — no new strategy variant
was actually backtested, so this gets no separate hypothesis-ledger
entry (same treatment as exp-029's characterization study).

## Hypothesis

Initial Balance Breakout (exp-028) was rejected decisively on price
alone. "Volume confirms breakouts" is a well-established, independent
technical-analysis heuristic — does a breakout accompanied by unusually
high relative volume behave any differently than one that isn't? Tested
here for the first time in this project using real per-minute volume
data (verified genuine, not a placeholder, on 2026-09-01).

## Data used

`data/NQ_1min_databento_2026-08-20.csv`, Discovery slice only — the same
1709 raw IB Breakout signals already detected for exp-028 (detection
logic completely unchanged), now additionally carrying each signal's
`ib_avg_volume` (that day's own 8:30-9:00 AM average volume) and
`breakout_volume` (the triggering bar's own volume), added directly to
`src/detect_ib_breakout.py`.

## Method

`rel_volume = breakout_volume / ib_avg_volume` for each signal.

**Step 1:** Pearson correlation (with a 90% bootstrap CI, 2,000
resamples) between `rel_volume` and each trade's realized
`r_multiple_net` (from `backtest.simulate_trade()`, unmodified — same
entry/stop/target as exp-028).

**Step 2 (conditional on Step 1):** only if Step 1's CI excludes zero,
split into `rel_volume > 1.0` vs. `rel_volume <= 1.0` and backtest each
bucket separately.

A temporary driver (deleted after use, same pattern as this project's
other one-off drivers) pre-grouped the data by day and called
`detect_ib_breakout.detect_ib_breakout_for_day()` unmodified on each
group — verified byte-identical to the real `scan_all_days()` on a
200-day check slice (148 signals, exact match) before trusting the full
run.

## Results

1709 raw signals, 1654 resolved — identical counts to exp-028, as
expected (nothing about detection changed).

**Step 1:** correlation(`rel_volume`, `r_multiple_net`) = **-0.0229**,
90% bootstrap CI **[-0.0645, +0.0190]** — spans zero, not significant.
`rel_volume` distribution across all signals: min 0.14, median 2.54,
mean 5.78, max 58.39.

**Step 2: skipped**, per the frozen doc's own rule — Step 1 gave no
basis to go looking for a bucket split.

## Interpretation

Another clean null. Relative breakout volume, defined against that
day's own Initial Balance average, shows no detectable relationship to
whether an Initial Balance Breakout trade wins or loses.

**A real limitation worth flagging honestly, not just the result
itself:** the `rel_volume` distribution's median of 2.54 (and mean of
5.78) shows that breakout-window volume is typically 2-6x the IB
window's own average on a completely ordinary basis — almost certainly
reflecting normal intraday volume seasonality (activity picks up
heading toward the 9:30 AM cash-equity open) rather than anything
specific to a genuine "high-conviction" breakout. This same-day baseline
(chosen in the frozen doc specifically to avoid lookahead and cross-year
volume drift) does not control for time-of-day seasonality, which means
this test may be a weaker check of the "volume confirms breakouts"
heuristic than a same-time-of-day trailing-average baseline would be —
see the setup doc's honesty flags, written before this result was seen.
This doesn't overturn the null finding (there's still no correlation
even with this diluted signal), but it does mean this specific test
doesn't fully rule out a real volume effect that a better-controlled
baseline might detect.

## Next step

Kill this specific test (same-day-IB-average relative volume shows no
relationship) but not necessarily the broader idea — a trailing,
same-time-of-day volume baseline (flagged as the alternative in the
frozen doc, not implemented here) would be a more rigorous test of
"volume confirms breakouts" before concluding volume has nothing to add
to this project. Whether that's worth building next, or whether to move
to a different avenue entirely (day-of-week/calendar effects, a
nonlinear conditioning of the open-return-persistence question), is the
next call.
