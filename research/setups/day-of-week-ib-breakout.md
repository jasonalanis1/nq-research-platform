# Day-of-Week Conditioning of Initial Balance Breakout

**Status: frozen definition, not yet tested** — drafted 2026-09-01, at
Claude's own initiative as research lead, continuing per Jason's
standing direction ("get us to the goal") after both the Open Return
Persistence and Volume-Confirmed IB Breakout studies came back null.

## Where this came from

Two characterization studies have now shown that neither the open's own
price direction nor breakout volume carries a detectable linear
relationship to what follows, using this project's own already-tested
Initial Balance Breakout trades as the outcome variable both times. This
document asks a different, independent question about the SAME
already-collected trades: **does which day of the week it is change
anything?**

This is not a made-up idea — day-of-week effects in equity index markets
are a long-documented empirical phenomenon in academic finance (the
"Monday effect" / weekend effect literature going back to French (1980)
and others, though its size and even its persistence have been debated
and it has weakened or reversed in some more recent samples), alongside
turn-of-month and other calendar-position effects. It's a genuinely
different kind of conditioning variable from price or volume — calendar
position, not market-generated data — and needs no new data source: the
timestamp already on every bar carries its own day-of-week for free.

## What this is NOT

This does not change Initial Balance Breakout's definition (range,
entry, stop, target — `research/setups/initial-balance-breakout.md`,
unchanged) in any way. It is a **post-hoc conditioning check** on the
exact same 1654 already-resolved Discovery-slice trades from exp-028 —
same signals, same outcomes, just grouped by an attribute (day of week)
that was always available and never looked at.

## Definition

### 1. The grouping variable: NY calendar day-of-week

Each Initial Balance Breakout signal's `date` (already recorded,
America/New_York timezone throughout this project) is mapped to
Monday/Tuesday/Wednesday/Thursday/Friday. NQ trades nearly 24 hours, but
the 8:30 AM open this entire project is built around only happens on the
five NY business days — weekends and holidays already produce no signal
at all (no bars in `data_loader`'s session), so no separate exclusion
logic is needed here.

### 2. What gets measured, per weekday

For each of the 5 weekday groups, using the SAME resolved trades and the
SAME `r_multiple_net` already computed for exp-028 (no re-backtest, no
parameter change):
- Trade count, win rate.
- Expectancy (mean `r_multiple_net`).
- A 90% bootstrap confidence interval on that weekday's total R (2,000
  resamples, same convention as every other setup in this project).
- Whether that weekday alone clears the full promotion bar (expectancy
  > 0, >= 150 trades, 90% CI entirely above zero) — the same bar every
  other setup has been held to, not a relaxed one just because this is
  a subgroup.

### 3. No cherry-picking the "best" day after the fact

All five weekdays get reported and written up, in the same table,
regardless of which one(s) look best or worst. Reporting only a
standout day and omitting the other four would recreate exactly the
"curated results" problem `docs/RESEARCH_INTEGRITY_PROTOCOL.md`'s
hypothesis ledger exists to prevent — even though this isn't itself a
ledger-eligible strategy hypothesis unless a specific weekday clears the
promotion bar (see Multiple-testing context below).

## Honesty flags

- **Weekday, not a finer calendar split** (e.g. day-of-month, week of
  options expiration, month-end/turn-of-month) — the most commonly
  studied and simplest calendar split, chosen as the natural first cut,
  not because finer splits wouldn't also be worth trying. Each
  additional way of slicing calendar time is itself another test, with
  its own multiple-testing cost — see below.
- **The Monday/weekend effect's own literature is genuinely mixed and
  has weakened over decades of samples** — this is not being treated as
  settled, confirmed fact going in, only as a well-documented,
  legitimate thing to check, exactly the same epistemic status this
  project has given every other externally-sourced idea (the FVG and
  trend-structure ideas, sourced from unverified video clips, were
  given far less benefit of the doubt than this get and are still
  tested with the same rigor).

## Multiple-testing context

Five weekday groups are five separate statistical comparisons against
the same underlying data — reporting all five regardless of outcome
(per #3) is this study's safeguard, but a single weekday showing a
significant-looking result among five tested should still be read with
that in mind, the same caveat this project has applied to the FVG
entry trigger and Initial Balance Breakout's own multiple-hypothesis
history. If any weekday's slice clears the full promotion bar on its
own trade count, treating that finding as a confirmed edge without a
fresh, independent test (ideally re-verified on the Validation slice,
following this project's own promotion path) would be exactly the kind
of overfit-to-a-subgroup result the integrity protocol exists to catch.
`purgedcv` remains unavailable to run the formal DSR/PBO correction.

## Status

**Tested, 2026-09-01, against real Discovery-slice data -- clean,
notably uniform null.** All five weekdays: negative expectancy in a
tight -0.056R to -0.092R band, win rates clustered at 42-44%, no
weekday statistically significant, none within reach of the promotion
bar (largest single-weekday sample: Monday, 346 trades). See
`research/experiments/exp-031-day-of-week-ib-breakout.md` for the full
per-weekday table. The uniformity across days argues against a
day-of-week explanation for Initial Balance Breakout's rejection,
rather than pointing at a hidden good day being averaged out.

## History

- 2026-09-01: this document written, at Claude's own initiative as
  research lead, continuing per Jason's standing direction after two
  prior characterization studies (open-return-persistence,
  volume-confirmed-ib-breakout) both returned clean nulls.
- 2026-09-01 (later same session): tested against the real Discovery
  slice (exp-031). Clean, uniform null across all five weekdays. See
  Status above.
