# Weekly verification cycle — checklist (queue item 1-VERIFY)

Source: Jason's refocus memo, September 15th, section 7.2
(research/infrastructure/refocus-2026-09-15.md). One cycle a week whose ONLY
job is checking Tony against itself. No research, no sourcing, no draws, no
builds. Every discrepancy becomes a fix (with a test) or a named queue item —
never a logged note. Output: research/integrity/verification-YYYY-MM-DD.md,
every line citing `path:line` (SESSION REPORT FORMAT, 7.4a). Jason books the
trigger; the cycle does not.

## 1. Numbers in the docs vs numbers in the code
- [ ] Sample-size constants: `TARGET_FILLS` in src/session_report.py, the
      40-trade / 12-month H118 window, the 20-fill execution minimum,
      `capital_protection.PAPER_CONFIG` ratios — each quoted figure in
      NEXT_UP.md, docs/BOT_ROADMAP.md and the latest session report matches
      the constant in code. (The 40-vs-20 error travelled through several
      documents before anyone checked.)
- [ ] Budget minutes: NEXT_UP's BUDGET CLOCK section vs `cycle_budget.py`
      default and `CLOSE_OUT_MINUTES`.
- [ ] Shelf floor and shelf count: the sweep line in NEXT_UP.md vs
      `python3 src/pipeline_sweep.py` run fresh.
- [ ] Directional lane: research/ledger/directional_lane.json `used` ==
      number of ledger rows tagged as lane trials; `cap` still 20.
- [ ] Test count quoted in the last session report vs `python3 -m pytest -q`.

## 2. Registry counts vs actual files
- [ ] `SCAN_REGISTRY` in src/project_wide_multiplicity.py: every registered
      scan has its result file on disk; every scan file in research/ has a
      registry row (K is honest in both directions).
- [ ] research/idea_inventory.md entry numbers are contiguous; every
      DRAWABLE entry has its mechanism doc in research/mechanisms/ and its
      map row in research/market_structure_map.md; every PARKED entry's
      header says why.
- [ ] Ledger: `python3 src/ops_checks.py` ledger-consistency check PASS;
      latest row per hypothesis_id agrees with every prose status claim in
      NEXT_UP.md's top sections (the H118 "Holdout passed" stale line is the
      precedent).
- [ ] research/forward_validation/: row counts in bot_stack_paper_log.jsonl
      and order_path_journal/ agree with the Execution block's cumulative
      fills; the b7_replay/ tree is labelled REPLAY and never counted as live.
- [ ] docs/BOT_ROADMAP.md milestone statuses vs the modules and tests that
      exist (session_report.py `product()` is what counts them).

## 3. Booked triggers vs the standing schedule
- [ ] `list_triggers`: exactly the standing day's cycles (9 am, 11 am, 1 pm,
      3 pm, 5 pm, 7 pm, 9 pm, 11 pm CT) plus the weekly review, the weekly
      verification and nothing else — no duplicates, no leftover 1/3/5/7 am
      cycles, no cron routines.
- [ ] research/_cycle_compliance.jsonl for the past 7 days vs the schedule:
      every booked cycle has a close row; missing ones are named
      (`python3 src/cycle_review.py --days 7`).

## 4. Production write guard and test isolation
- [ ] `python3 -m pytest -q` with the conftest redirect fixture mentally
      removed: tests/test_production_paths.py still proves a test cannot
      write a protected path; research/integrity/write-path-audit-2026-09-15.md
      matches `production_paths.PROTECTED` (add any new writer found by
      `grep -n "open(\|write_text\|to_csv\|json.dump" src/*.py`).
- [ ] No synthetic rows in the live execution record (price patterns, dates
      before the anchor, test instruments).

## 5. GitHub
- [ ] `git fetch origin && git status -sb && git log origin/main --oneline -3`:
      origin/main == HEAD, no stale lock files in .git/ (src/git_unlock.sh).

## 6. Report
- [ ] research/integrity/verification-YYYY-MM-DD.md: one line per check,
      PASS / DISCREPANCY (with `path:line` on both sides), and what was done
      about each discrepancy. Session report's OPERATIONS section names the
      file. If nothing is wrong, say so in one line and close early.
