# Write-path audit — September 15th, 2026 (refocus memo 7.3)

Source: Jason's refocus memo, section 7.3 (research/infrastructure/refocus-2026-09-15.md:98-103):
"production paths refuse writes unless an explicit production flag is set, so a test cannot
reach them by default. Audit every path the code writes to and report which are protected and
which aren't."

Method: `grep -n "open(\|write_text\|to_csv\|json.dump" src/*.py` (every writer under src/), each
target classified, then the guard wired into every writer of a PRODUCTION RECORD. Guard:
src/production_paths.py (default-deny; `TONY_PRODUCTION=1` in the environment, set by the
standing entry points' `if __name__ == "__main__"` blocks or by hand for one-off scripts).
Tests: tests/test_production_paths.py (8), and tests/conftest.py:46-63 strips the flag at session
start and asserts it is absent around every test. Line numbers below are as of commit time.

## Tally

| | writers | targets |
|---|---|---|
| PROTECTED (guard called before the write) | 13 scripts, 18 call sites | 13 files + 2 trees + 1 glob |
| NOT protected, by design (ops scratch, regenerable, per-run outputs) | ~150 scripts | data/ results, receipts, locks, reports |

## A. PROTECTED — the production record

| writer | target | guard call | entry point enables |
|---|---|---|---|
| src/research_ledger.py `log_hypothesis` | research/ledger/hypotheses.jsonl (append) | src/research_ledger.py:298 | callers run `TONY_PRODUCTION=1 python3 src/<scan>.py` (34 scan scripts, ~17 Statistical/Validation scripts call it) |
| src/research_ledger.py `update_status` | research/ledger/hypotheses.jsonl (append) | src/research_ledger.py:350 | same |
| (no writer yet) | research/ledger/directional_lane.json | listed in PROTECTED_FILES; the cycle that spends trial 1 writes it through `assert_writable` | — |
| src/study_prospective_exp047.py `append_log` | research/ledger/prospective_exp047_log.jsonl (append) | src/study_prospective_exp047.py:134 | its `__main__` (preflight runs it as a subprocess) |
| src/bot_stack_paper_run.py `append_row` | research/forward_validation/bot_stack_paper_log.jsonl (append) — THE live execution log | src/bot_stack_paper_run.py:238 | its `__main__` |
| src/bot_stack_paper_run.py `_execution_anchor` | research/infrastructure/b7-execution-anchor.json (write once) | src/bot_stack_paper_run.py:181 | its `__main__` |
| src/order_path.py `OrderPathJournal.append` | research/forward_validation/order_path_journal/<date>.jsonl (append) — the journal a test contaminated on Sept 14th | src/order_path.py:73 | via bot_stack_paper_run / b7_replay `__main__` |
| src/b7_replay.py `_reset`, `main` | research/forward_validation/b7_replay/ (tree: replay_log, journal/, replay_report.json) | src/b7_replay.py:67, :194 | its `__main__` |
| src/bot_forward_log.py `append_row` | research/forward_validation/bot_stack_forward_log.jsonl (append, statistical clock) | src/bot_forward_log.py:85 | its `__main__` |
| src/risk_state_engine.py `freeze_params` | research/infrastructure/risk-state-engine-frozen-params.json (frozen spec) | src/risk_state_engine.py:155 | its `__main__` (`--freeze`) |
| src/risk_state_engine.py `main --log` | research/forward_validation/risk_state_engine_log.jsonl (append) | src/risk_state_engine.py:280 | its `__main__` |
| src/forward_validate_h118_daily.py `save_log` | research/forward_validation/h118_forward_log.jsonl (REWRITES the whole file) | src/forward_validate_h118_daily.py:83 | its `__main__` (preflight subprocess) |
| src/batch_screen.py `save_state` | research/_batch_screen_state.json | src/batch_screen.py:360 | its `__main__` — FROZEN by refocus s.3, must not be run |
| src/batch_screen.py `append_survivors` | research/idea_inventory.md (append) | src/batch_screen.py:661 | same |
| src/cycle_budget.py `done` | research/_cycle_history.jsonl (append) — busy-work alarm's input | src/cycle_budget.py:171 | its `__main__` |
| src/cycle_close.py `main` | research/_cycle_compliance.jsonl (append) — the day's record, minutes-used input | src/cycle_close.py:218 | its `__main__`; its pytest subprocess is run with the flag STRIPPED (src/cycle_close.py `_run`) |
| src/data_topup_databento.py `main` | data/NQ_1min_databento_<date>.csv (new file, never edits the old one) | src/data_topup_databento.py:151 | its `__main__` |
| src/data_fetch_databento.py `save_to_csv` | data/NQ_1min_databento_<date>.csv | src/data_fetch_databento.py:325 | its `__main__` |

PROTECTED_GLOBS `data/*_1min_*.csv` also covers the ES/RTY/6E/CL/ZN series files, but see B.3.

## B. NOT PROTECTED — and why

1. **Ops scratch that a cycle rewrites every run** (no history, regenerable, never evidence):
   research/_cycle_checkpoint.json (src/cycle_budget.py:136,146,168), research/_cycle_preflight.json
   (src/cycle_preflight.py:139,178), research/_worksession.lock + .meta (src/worksession_lock.py:77,148,160),
   data/pipeline_sweep.json and NEXT_UP.md's auto sweep block (src/pipeline_sweep.py:278,286),
   dashboard.html (src/generate_dashboard.py:449). Tests already monkeypatch these; a stray test
   write would be overwritten by the next preflight. Not worth a guard that the cycle would have
   to satisfy from four more scripts.
2. **Per-run analysis outputs under data/** (`*_results.json`, `study_*`, `observatory_*`,
   `idea_factory_*.json`, `backtest_results_*.csv`, `setups_*.csv`, `multi_factor_features_*.csv`,
   `stack_*_occurrences.jsonl`, `scan_*_occurrences.jsonl`): written by ~130 one-off scan / study /
   observatory / detect / backtest scripts plus src/stack_scan_runner.py:212 and
   src/idea_factory.py:259,288,505,563. They are the OUTPUT of a run, re-creatable from the frozen
   spec + the data, and the ledger row (protected) is the record of what they found. Guarding
   them would mean 130 edits for no change in what can be corrupted.
3. **Non-NQ Databento fetchers** — src/data_fetch_databento_cross_asset.py:191,
   src/data_fetch_databento_es.py:174, src/data_fetch_databento_rty.py:168 (series files, matched
   by the glob but the writers do not call the guard) and the two cost logs
   (src/data_fetch_databento.py:173 `_databento_cost_log.json`, src/data_fetch_databento_cross_asset.py:221).
   They need an API key and real money to run at all; no test can reach them. Left unguarded as
   one-time scripts; wire `assert_writable` in if any is ever run again.
   src/data_fetch.py:154 (the retired Yahoo fetcher) likewise.
4. **Stage artifacts written by name to research/studies, research/integrity,
   research/observatory** — src/h118_baseline_diagnostic.py:113-114, src/observatory_free_look.py:168,191,
   src/statistical_stage_hyp156.py:169,189, src/statistical_hyp162.py:205, src/validate_hyp162.py:275,
   src/portfolio_hyp162.py:211, src/monetization_hyp162.py:200, src/gate_conditions_hyp162.py:190,
   src/learn_closed_family_audit.py:138, src/integrity_checks.py:494, src/integrity_blind_packet.py:140,
   src/validate_hyp156.py:225, src/session_report.py:361 (`-o`). Each is a dated, named file a
   human reads; a test writing one would be visible in `git status` and could not alter a
   status of record (the ledger is). Not guarded.
5. **research/sessions/, research/NEXT_UP.md prose, research/KNOWLEDGE.md, research/idea_inventory.md
   edits other than batch_screen's append** — written by the cycle itself (the assistant), not by
   code. Nothing to guard in src/.

## C. What the guard does NOT do

- It is not a permission system: any process that sets `TONY_PRODUCTION=1` may write. Its job
  is to make an ACCIDENTAL write from a test impossible, which is the failure that happened.
- It does not stop the conftest redirect fixture from being needed for behaviour tests — those
  still redirect to tmp_path so the writer's logic can be exercised.
- The relative-path form of the ledger default (`research/ledger/hypotheses.jsonl`) is matched on
  its spelling as well as its resolution (src/production_paths.py `is_protected`), so running a
  scan script from another cwd cannot slip past it.

## D. Verification run (September 15th)

- `python3 -m pytest -q`: green with the guard in place (count in the session report).
- `python3 src/bot_stack_paper_run.py --strategy dummy`: ran normally through its `__main__`,
  "0 new row(s) appended" (data on disk still ends 2026-09-14 11:14 ET; both remaining sessions
  correctly skipped as incomplete), no guard error, log unchanged at 22 rows.
- `python3 src/cycle_preflight.py --skip-lock --skip-budget`: both daily checkers ran as
  subprocesses and wrote their logs through their own `__main__` enablement.
- tests/test_production_paths.py: the real ledger, the real execution log and the real journal
  are refused at their real paths with the conftest redirect undone, and are byte-for-byte
  unchanged afterwards.
