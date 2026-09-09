# NEXT UP — session handoff baton

PURPOSE: this is the ONE file every work session reads first and rewrites
last. It exists because sessions are stateless: a scheduled run has no
memory of the previous one, and re-deriving "where are we" from the
docs/BACKLOG.md plus the 129-row ledger every 4 hours is expensive and
slow, and it was landing on stale facts.

RULES:
  - Read this FIRST, before anything else. Work the queue below.
  - Rewrite this file LAST, before the session ends, every time --
    even if nothing got done (say so, and why).
  - Keep it under ~400 words. It is a baton, not a record. The
    permanent record stays in research/ledger/hypotheses.jsonl,
    research/experiments/, and docs/BACKLOG.md.
  - Do NOT read docs/BACKLOG.md by default -- only when picking a
    genuinely NEW research direction and you need the idea inventory.
  - Jason works this project ad hoc too. If "Last updated by" says
    Jason/interactive session, that work is already done -- continue
    from it, do not redo it.

## Where things stand (as of 2026-09-09, ~23:00 UTC)

- H118: Integrity Gate PASS, Holdout passed, in FORWARD VALIDATION.
  One OPEN paper position (2026-09-08 entry) -- but see below, this
  entry predates the mechanism's own boundary and is flagged, not
  deleted. No action needed; the daily checker handles new signals.
- BUG FOUND + FIXED this session: src/forward_validate_h118_daily.py
  needed ALLOW_HOLDOUT_DATA=1 to see recent data (data_holdout.py's
  fixed 2026-04-07 cutoff), but had no floor check of its own, so it
  logged a 2026-09-08 signal -- one day before its own frozen spec's
  stated "2026-09-09 forward" boundary, i.e. still Holdout Generation 1
  data, not genuinely forward. Fixed with an explicit
  FORWARD_VALIDATION_ANCHOR=2026-09-09 check (can't recur). The existing
  2026-09-08 entry is left in the log un-edited (never hand-edit
  results) but should be excluded from any future PASS/FAIL read of
  H118 Forward Validation. Full detail + what's still open (whether
  data_holdout.py itself needs a cleaner "Forward Generation" boundary
  helper): docs/BACKLOG.md, "H118 Forward Validation boundary bug found
  + fixed". Jason was notified directly about this (it touches
  CLAUDE.md's most-protected holdout rule) -- check whether he's
  responded with a preference before this matters again (next relevant
  moment: whenever the 2026-09-08 position's 10-day exit resolves,
  ~2026-09-22).
- TRIAGE SWEEP (prior queue item 1): DONE. All 20 stale-looking
  PROMISING ledger rows resolved/verified -- see BACKLOG "Triage Sweep
  complete". Only hyp-000046/048 (range-contraction) remain genuinely,
  correctly PROMISING (validated, awaiting a costed-rule translation).
  Note: found this had been started by an apparently-concurrent/
  overlapping run of this same scheduled task (hyp-000124-126 were
  already there, uncommitted, no process running) -- worth mentioning
  to Jason if it recurs, may indicate a double-fire.
- Price data current through 2026-09-08. Cost logging exists in
  data_fetch_databento.py (data/_databento_cost_log.json).

## Queue — work these in order

1. MULTIPLE-TESTING EXPOSURE (Integrity Gate's own flagged open item):
   project-wide search exposure across ~129 ledger rows never formally
   quantified. Scope + implement a deflated-Sharpe-style adjustment.
2. Continue market-behavior characterization: Scan 003 is a reasonable
   next Discovery Engine step (untested state variables: opening_range
   _vs_atr already implemented but never scanned; a ZN-bond-derived
   state variable, data on disk through 2024-01-03, Discovery-slice-safe)
   -- Research Director's call, not pre-committed.

## Blocked / awaiting Jason

- Spending any of the 5 total Holdout Generation 2 slots (1 used, 4 left).
- Any spend of $5 or more.
- Any live-capital authorization, regardless of statistical result.
- Whether the 2026-09-08 Forward Validation entry's eventual result
  should be discarded/excluded (this session's default) or handled
  differently, and whether data_holdout.py needs a real fix.

## Last updated by

2026-09-09 ~23:00 UTC, automated 4-hourly session. Fixed the Forward
Validation boundary bug, completed the Triage Sweep, notified Jason
about the boundary-rule finding.
