# exp-033 — Fade the Gap, Discovery slice (real data)

**Date:** 2026-09-02
**Status:** kill (1061 resolved trades, statistically decisive 90% CI entirely below zero)

## Hypothesis

Direct mechanical translation of `research/studies/overnight-gap-behavior.md`'s
(exp-032) own Step 3 trigger. That characterization study found, on the
Discovery slice: a gap-fill-by-noon rate significantly above 50% in both
directions (58.4% gap-up, 58.1% gap-down, both 90% CIs entirely above
50%), and a significant negative correlation between gap size and the
+90-minute forward return (-0.1408, 90% CI [-0.2142, -0.0595]). Both
findings point the same way: gaps tend to partially close, not extend.
This setup bets on that directly — fade the gap at the open. Full frozen
definition: `research/setups/fade-the-gap.md`.

Selected by Claude as research lead, per Jason's standing direction
("get us to the goal"), as the mandatory next step once exp-032's own
Step 3 rule was triggered by a real (not null) characterization result —
the first time that's happened in this project.

## Data used

`data/NQ_1min_databento_2026-08-20.csv`, Discovery slice only
(`data_split.get_discovery_data()`, 2015-01-01 through 2021-10-03, 2101
trading days) — the same slice every setup has been tested against since
exp-019.

## Method

`src/detect_fade_the_gap.py` (reusing `study_overnight_gap.py`'s
`get_reference_close()` and `detect_ib_breakout.py`'s
`OPEN_HOUR`/`OPEN_MINUTE`, not reimplemented) →
`simulate_fade_the_gap_trade()` (a noon-bounded wrapper around
`backtest.py`'s own unmodified `simulate_trade()`) →
`src/score_results.py` → `src/confidence_analysis.py`.

Because `detect_fade_the_gap.scan_all_days()` re-filters the full
DataFrame by date on every call (too slow in this environment against
2101 Discovery days), a temporary driver
(`src/_run_fade_the_gap_discovery.py`, deleted after use, not part of
the permanent pipeline — same pattern as every other performance driver
in this project) pre-grouped the data by day once and called the
unmodified `detect_fade_the_gap_for_day()` on each day's pre-sliced pair
instead — a performance-only change, no detection logic touched.
Verified byte-identical to the real `scan_all_days()` on a 200-day check
slice before trusting the full run.

**A real bug found and fixed during this run, not anticipated by the
unit tests' clean synthetic data:** the first full-Discovery attempt
crashed inside `backtest.py`'s `simulate_trade()`. Cause: NQ's data is
nearly continuous (00:00-23:59 ET), so a Sunday "calendar day" has bars
only from its ~6:00 PM ET weekly reopen onward — no session between
midnight and then. The "first bar at/after 8:30 AM" lookup was matching
that evening reopen bar as if it were a real 8:30 AM entry, on 370 such
days, and then trying to simulate a trade in a data window that ended
before the entry it had just manufactured. Fixed by adding an explicit
guard to `detect_fade_the_gap_for_day()`: if the earliest available bar
at/after 8:30 already falls at or past the noon watch-end cutoff, return
`None` — there's no real watch window left, so it isn't a real signal.
Covered by a new unit test
(`test_entry_after_watch_window_returns_none`). **Checked separately:
`study_overnight_gap.py`'s own exp-032 results are NOT affected by this
same issue** — its Step 1/Step 2 computations use time-windowed slices
that come up naturally empty for these degenerate days and are already
excluded via existing `None`-handling, not a dedicated guard like the
one this setup needed for its actual trade simulation. No correction to
exp-032 is needed.

## Results (net of estimated costs)

- 1340 raw signals (556 long/gap-down, 784 short/gap-up) — matches
  exp-032's Step 1 gap-up/gap-down counts exactly, as expected since both
  come from the same underlying gap computation.
- 370 days excluded for the Sunday-reopen edge case above; 384 days had
  no usable prior-day reference close; 6 days had a literal zero gap.
- 1061 resolved, 279 unresolved by the noon cutoff (closed at whatever
  price prevailed at noon, not at stop or target).
- Win rate 52.1% (95% CI: 49.1%-55.1%) — above 50%, consistent with the
  underlying gap-fill finding, but see Interpretation below on why this
  setup needs more than a bare majority to be profitable.
- Average win +0.92R, average loss -1.17R.
- Expectancy -0.079R, profit factor 1.17 (raw points) / 0.86
  (R-normalized), max drawdown -102.84R, total -83.57R.
- Bootstrap: 90% CI on total R across 1061 trades is **-138.82R to
  -28.75R — entirely below zero.** Only 1.1% of 1061-future-trade
  simulations ended net profitable.

## Interpretation

**A win rate above 50% still isn't enough here, and that's the whole
point of the setup doc's honesty flag on this.** Every other setup in
this project uses a 1.35R target against a 1R stop, so a ~43% win rate
can be profitable. This setup's target is a fixed price level (the
gap-fill point) rather than a multiple, forcing a symmetric 1:1 R:R by
construction — which needs comfortably more than 50% wins, not just a
hair over it, to overcome round-trip costs. 52.1% clears the coin-flip
line but not that higher bar, and the noon-cutoff exits make the
asymmetry worse in practice: a full winning trade nets +1R before costs,
but a trade that's still open at noon closes at whatever price is
prevailing then, which is very often still on the losing side of entry
(average loss -1.17R, actually worse than a clean -1R stop-out, because
some noon-cutoff exits land past where a real stop would have already
triggered had this setup allowed one — it doesn't, by design, since the
premise being tested is specifically the noon watch window from
`overnight-gap-behavior.md`).

This result does NOT contradict exp-032's characterization finding — the
gap-fill tendency and the +90-minute correlation are still real,
statistically supported findings on their own terms. What it shows is
that a specific, honest translation of that finding into a trade with
realistic costs and a forced 1:1 structure doesn't survive intact. A
different mechanical translation (a smaller target short of full
gap-fill, an asymmetric R:R closer to this project's usual 1.35, a
volatility- or magnitude-based filter on which gaps to trade) might
behave differently — but that would be a distinct, separately-justified
follow-up test, not evidence that this specific result should be
second-guessed or retested until something works, which is exactly the
kind of search this project's integrity rules exist to prevent.

The same-slice-circularity caveat flagged up front in the setup doc
(this rule was built from and first tested on the same Discovery slice
that produced the underlying finding) is worth restating for completeness,
but doesn't need to be argued through here: there is no positive result
to independently confirm. A decisively negative result on the same slice
that produced the hypothesis is, if anything, a slightly stronger kind of
rejection than a positive one would have been a confirmation.

## Next step

**Kill.** The literal "bet on the gap closing all the way back to the
prior close, by noon, at forced 1:1 R:R" trade does not survive contact
with realistic costs, despite a real and statistically supported
underlying tendency for gaps to partially close. Two honest, narrower
follow-up directions exist if this is revisited later — a partial-fill
target (e.g. 50% of the gap, closer to this project's usual R-multiple
shape) or a magnitude-based filter on which gaps are worth trading — but
neither is being pursued automatically here; per this project's
standing discipline, that would need its own specific justification
rather than being tried just because the first version didn't work.
Logged as `hyp-000012`, REJECTED.
