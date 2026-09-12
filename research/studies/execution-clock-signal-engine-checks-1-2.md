# Execution Clock — Signal Engine, checks 1-2 (queue item 1b)

Frozen 2026-09-11. Automated session. Spec governing this work:
research/infrastructure/back-half-production-integrity-v3.md (AMENDMENT
v3.1) and research/NEXT_UP.md (SCOPE DISPUTE RESOLVED note, queue item
1b, unblocked 2026-09-11).

## What checks 1-2 mean (v3.1 section 4)

1. **Signal occurs when the spec says it should.**
2. **Signal occurs exactly once when it should.**

These are the first 2 of the 14 execution checks that gate Stage 3
(Execution-Qualified) of the back-half ladder. They are about the
**signal engine itself** — does it correctly and deterministically
decide, from the frozen rule and data on disk, when H118 fires — not
about order placement, fills, or broker behavior (checks 3-14, later
queue items 1c/1d).

## What was built

- `src/execution_clock_signal_engine.py` — the signal engine.
  `generate_signals_walkforward()` walks every trading day the data
  covers, IN CHRONOLOGICAL ORDER, and decides per day whether it is an
  H118 signal day (vwap_dist_vs_atr LOW tercile, bucket edges frozen
  from Discovery — same frozen constants `study_vwap_dist_low_10d_drift_h118.py`
  and `forward_validate_h118_daily.py` already use, imported rather than
  retyped). For each signal, it computes the entry timestamp (signal
  date, 15:58:00 America/New_York) and the exit timestamp (signal date +
  10 trading days, same time), per the frozen execution-approximation
  spec (`research/studies/h118-execution-approximation-spec.md`), and
  records whether a tradeable 1-minute bar actually exists at that exact
  timestamp.
- `src/execution_clock_check_1_2.py` — the proof harness. Runs the
  engine, then independently re-derives the forward validator's own
  per-day signal test (same frozen constants, a second implementation,
  applied to every day in sequence) and diffs the two signal-date sets.
- `tests/test_execution_clock_signal_engine.py` — 8 pytest tests: fires
  on exactly the LOW days and no others; no duplicate signal dates; a
  prefix of the walk-forward loop produces the same decisions as the
  full run (no lookahead); entry/exit timestamps carry the frozen
  15:58:00 time in a timezone-aware timestamp; a missing execution bar
  is flagged, never silently dropped or papered over; an unresolved
  (horizon not yet elapsed) signal carries no fabricated exit; the audit
  function itself can detect a duplicate when one is injected; and one
  integration test running the real comparison harness against whatever
  price data is on disk (skipped, not failed, if none is present).

## How this proves checks 1-2

**Check 1** (fires when the spec says, exactly once): `audit_signals()`
counts unique signal dates vs. total signals emitted by the walk-forward
loop. On the full price history on disk (2015-01-02 through
2026-09-08, 2992 trading days): **1009 signal days, 1009 unique dates,
zero duplicates.**

**Check 2** (matches the already-existing forward validator): the
comparison harness reimplements `forward_validate_h118_daily.py`'s own
per-day new-signal test — `pd.notna(latest_bucket) and
str(latest_bucket) == BUCKET` against the same Discovery-frozen bin
edges — as a second, independent code path (never calling that script's
`main()`, so `h118_forward_log.jsonl` is never touched), and diffs its
output against the signal engine's walk-forward output. Result over all
2992 trading days: **exact match — 0 signal dates only in the engine's
output, 0 only in the recomputation.**

Run yourself:
```
python3 src/execution_clock_check_1_2.py
```

## Scope boundary — what this is NOT

- No order submission, no broker connection, no fill tracking, no
  deviation measurement (points/R, expected-vs-actual fill). Those are
  checks 3+ (queue item 1c), which also needs 1a's execution-checks-
  concrete work first.
- Never writes to `research/forward_validation/h118_forward_log.jsonl`
  or any H118 ledger row. Read-only against H118's frozen rule and
  price data on disk.
- Never modifies, retunes, or reinterprets H118's frozen definition
  (bucket edges, LOW tercile, 10-trading-day horizon) — imports the
  same frozen constants the existing production scripts already use.

## Flagged, not resolved (binding Integrity Gate guardrail on this item)

The frozen execution-approximation convention specifies a single
deterministic timestamp — 15:58:00 America/New_York — with no fallback
if the market is closed or half-day-shortened that day. Checking every
signal/exit day against the actual 1-minute bars on disk:

- **18 of 1009** entry (signal) days have no 15:58:00 NY bar (market
  holidays and early-close sessions).
- **41 of the 968 resolved-horizon** exit days have no 15:58:00 NY bar.

Example dates: 2015-02-16, 2015-05-25, 2015-07-08, 2015-12-24 (entry
side); 2015-09-07, 2016-07-04, 2016-11-24 (exit side) — the full list is
in each run's console output and in `audit_signals()`'s returned
`entry_bar_missing_dates` / `exit_bar_missing_dates`.

This is a genuine executability finding about the frozen convention,
not a defect in the engine, and per the binding guardrail on this item
it is reported here rather than resolved by picking a substitute
timestamp (nearest available bar, session close, etc.) — any of those
would be a reinterpretation of the frozen rule, which is explicitly out
of scope. **This needs Jason's decision** (as part of 1a's execution-
checks-concrete work, or as a standalone freeze) before the execution-
qualification stage can treat these days consistently.

## Frozen inputs (unchanged by this work)

- `research/studies/vwap-dist-low-10d-drift-h118-spec.md` — H118's
  frozen signal rule.
- `research/studies/h118-execution-approximation-spec.md` — the frozen
  15:58:00 America/New_York, 1 MNQ, deterministic-timestamp convention.
- `src/study_vwap_dist_low_10d_drift_h118.py` — source of `VAR`,
  `BUCKET`, `HORIZON_DAYS`, `compute_bin_edges()`, imported not retyped.
