# exp-035 — Futures Expiration/Rollover Proximity Study, Discovery slice (real data)

**Date:** 2026-09-02
**Status:** clean null on both checks — no mechanical rule triggered

## Hypothesis

Two independent checks of whether proximity to NQ's public quarterly
IMM futures expiration date (third Friday of March/June/September/
December) is associated with anything unusual in this project's own
data: (A) does Initial Balance Breakout's already-tested, already-
rejected trade set (exp-028, 1654 Discovery trades) perform differently
in the calendar week containing an expiration date versus a normal
week, and (B) is the overnight gap (already studied in exp-032)
measurably larger in absolute size near expiration — a direct test of
`docs/ROADMAP.md`'s longstanding, never-investigated claim that a
continuous futures contract series "introduces small price jumps at
contract rollover dates." Full frozen definition:
`research/studies/futures-expiration-effects.md`.

Selected by Claude as research lead, per Jason's standing direction to
keep pushing without waiting for further instruction, immediately after
VWAP Mean Reversion (exp-034) became the ninth rejected strategy
hypothesis. Chosen specifically because it required no new data
acquisition — only a public, well-documented expiration calendar
applied to data already collected — rather than generating another
strategy variant on the gap or VWAP theses without a fresh, specific
reason to expect a different result.

## Data used

Check A reuses `data/backtest_results_ib_breakout_discovery.csv`
(exp-028's 1654 resolved Discovery-slice trades) unmodified — no
re-backtest. Check B reuses `study_overnight_gap.py`'s own gap
computation, re-run across the same Discovery slice
(`data/NQ_1min_databento_2026-08-20.csv`, 2015-01-01 through
2021-10-03, 2101 trading days).

## Method

`src/study_futures_expiration.py` implements `third_friday()` (the
standard CME quarterly expiration convention),
`make_is_expiration_week()` (a pure calendar lookup — no market data
involved, so no look-ahead), `analyze_ib_breakout_by_expiration()` (a
pandas groupby on the existing trades CSV), and
`analyze_gap_magnitude_by_expiration()` (reusing
`study_overnight_gap.py`'s `compute_day_gap_and_returns()` unmodified).

Because `study_overnight_gap.scan_all_days()` re-filters the full
DataFrame by date on every iteration (too slow in this environment
against the full ~2.24M-row Discovery slice), a temporary driver
(`src/_run_futures_expiration_study.py`, deleted after use, not part of
the permanent pipeline — same pattern as every other performance driver
in this project) pre-grouped the data by day once via a real
`df.groupby(df.index.date)` and called the unmodified
`compute_day_gap_and_returns()` on each pre-sliced pair instead — a
performance-only change, no computation logic touched. Verified
byte-identical to the real `scan_all_days()` on a 200-day check slice
(147 matching rows) before trusting the full run.

## Results

**Check A — Initial Balance Breakout trades by expiration proximity:**

| Group | n | Win rate | Expectancy | 90% bootstrap CI on total R | Clears promotion bar? |
|---|---|---|---|---|---|
| Expiration Week | 131 | 38.2% | -0.086R | [-31.60R, +9.61R] | No |
| Normal Week | 1578 | 41.4% | -0.067R | [-182.57R, -32.33R] | No |

Both groups are negative and close in magnitude (-0.086R vs -0.067R).
Expiration Week's CI spans zero (not statistically distinguishable from
zero on its own, smaller sample), while Normal Week's CI sits entirely
below zero (consistent with exp-028's own overall decisive rejection,
since Normal Week is nearly the entire sample). There is no meaningful
separation between the two groups — expiration proximity does not
explain any part of IB Breakout's existing rejection.

**Check B — overnight gap magnitude by expiration proximity:**

| Group | n | Mean \|gap\| |
|---|---|---|
| Expiration Week | 107 | 37.03 pts |
| Normal Week | 1609 | 32.84 pts |

90% bootstrap CI on the difference (Expiration Week − Normal Week):
**[-4.12, +13.70] points — spans zero, not statistically significant.**
The point estimate is directionally consistent with the "price jumps at
rollover" claim (larger average gap near expiration), but the interval
is wide relative to the difference and includes zero, so this data
cannot distinguish that claim from ordinary sampling variation at this
sample size (107 expiration-week days out of 2101).

## Interpretation

**Clean null on both checks — no mechanical rule to build, no ledger
entry (per this project's characterization-study convention, matching
every prior conditioning check except exp-032's non-null gap-fill
finding).** Neither check found something requiring further mechanical
testing under this study's own frozen Step 3-equivalent rule.

Two honest limits on how much this null actually settles, both flagged
in the frozen study doc up front rather than added after the fact:

1. **The public IMM expiration date is a proxy, not the actual roll
   date used to build this continuous contract series.** Databento's
   real roll methodology (fixed days before expiration, a volume/open-
   interest crossover, or something else) isn't recorded anywhere in
   this project's data or docs. A null result on the public-date proxy
   cannot rule out a real splice effect landing on a different date —
   it only rules out an effect concentrated around the public
   expiration date specifically.
2. **A whole calendar week is a coarse bucket.** If a splice effect is
   real but concentrated on a single day (the actual roll date, whenever
   that is), diluting it across five days of "Expiration Week" could
   wash out a real, narrower signal. This is a legitimately different,
   untested follow-up if there's ever a way to pin down the actual roll
   date(s) this data used.

Both are named honestly rather than treated as reasons to keep
re-slicing the same calendar idea narrower and narrower looking for a
positive result — consistent with this project's standing discipline
against exactly that kind of search.

## Next step

**No ledger entry — this is a characterization study, not a strategy,
and both checks came back null.** `research/studies/futures-expiration-effects.md`
is updated with this result and closed out. This resolves the
"futures expiration dates" item `docs/ROADMAP.md` had named as an open,
untested candidate for new ground since exp-031 — it has now been
looked at, honestly, and found nothing actionable with the data and
proxy available. The other named candidate (an economic-release
calendar) would require a genuinely new data source this project
doesn't have, unlike this one; whether to pursue acquiring that data is
a decision worth surfacing rather than assuming.
