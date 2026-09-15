# Standing cycle prompt (the send_later message, verbatim, so it is never lost)

Reconstructed 2026-09-12 18:45 UTC after a context compaction dropped the
prior text. REWRITTEN 2026-09-15 (Day One) to the STANDING OPERATING
DIRECTIVE's Step 1-5 order (research/infrastructure/standing-directive-2026-09-15.md
s.3). Only the STANDING STATE block changes between cycles.

---
SCHEDULED CYCLE (Tony, 2-hour cadence, unattended). Do not ask Jason
anything; make the reasonable call, state it in the report, proceed. Never
use create_trigger for the cadence: at close-out, list_triggers (duplicate
check), then send_later the NEXT cycle 2 hours after this one's scheduled
time, this same message with only STANDING STATE updated. If the device is
unreachable, schedule the successor FIRST, then retry the device once.
Before every git command: bash src/git_unlock.sh.

THE STANDING OPERATING DIRECTIVE governs (research/infrastructure/
standing-directive-2026-09-15.md, summarized at the top of research/NEXT_UP.md).
Read NEXT_UP.md first. The loop is SOURCE -> SPECIFY -> FREEZE -> SCREEN ->
PAPER -> JUDGE -> KEEP / FIX ONCE / KILL -> SALVAGE -> LEARN. The evidence for a
strategy is its paper record. Interrupt Jason only for the three s.10 reasons.

STEP 1 -- PREFLIGHT. python3 src/cycle_preflight.py --owner cycle --note "<cycle>"
   (lock, budget clock 105 min, pipeline sweep, both daily checkers, PAPER BOOK
   status: strategies in paper, trades, days elapsed, judgment point). If
   cycle_budget.py status says UNFINISHED, resume that item/step first.
STEP 2 -- DATA CHECK. Is there new price data since the last cycle (ls -la
   data/NQ_1min_databento_*.csv; Jason tops up daily ~7 am CT)? If yes, Step 3.
   If no, do NOT idle and do NOT report "bot checked, not moved": go to Step 4 on
   historical data and say plainly that paper scoring is waiting on data. Data
   stuck > 48 hours = s.10 interrupt reason 3.
STEP 3 -- ADVANCE THE PAPER BOOK. For every strategy at stage PAPER in
   research/ledger/strategies.jsonl (python3 src/strategy_registry.py):
   TONY_PRODUCTION=1 python3 src/bot_stack_paper_run.py --strategy <id>.
   Then python3 src/paper_book.py. Any strategy at 40 trades or 6 weeks gets a
   Director verdict THIS cycle (s.6: KEEP / FIX ONCE / KILL, recorded in the
   registry with the numbers). Any KILL -> Salvage check (s.7 menu only) this
   cycle or next; result to LEARN (research/KNOWLEDGE.md) either way. The
   execution dummy and B3 rows are PLUMBING -- never judged, never a candidate.
STEP 4 -- ADVANCE ONE CANDIDATE ONE STAGE. Highest-priority candidate not yet
   in PAPER (registry latest stage; Director priority order in NEXT_UP):
   SOURCE -> SPECIFY (whole trade: entry/exit/stop/sizing/costs, mechanism
   paragraph, "where this should fail") -> FREEZE (spec file under
   research/infrastructure/strategy-specs/ + src/strategy_s###_*.py, sha256 of
   both into the registry, its own commit, BEFORE any data) -> SCREEN
   (python3 src/screen_strategy.py <module>, Discovery slice only, one number:
   net after ASSUMED costs; > 0 -> register in bot_stack_paper_run.STRATEGIES
   and run it into PAPER today; <= 0 -> SALVAGE by the menu, spawn S###a at
   SPECIFY if a menu condition is profitable, LEARN either way). If the queue
   is empty, Discovery sources one (mechanics, structure, Observatory, Salvage
   queue, revamp list research/ledger/revamp_list.json; calendar anomalies last).
   Never batch_screen.py. Never touch Validation/Holdout data in a screen.
STEP 5 -- CLOSE-OUT, in order: python3 -m pytest -q; ops_checks.py;
   pipeline_sweep --write; session file research/sessions/<date>-<HHMM>.md;
   append _session_log.txt; NEXT_UP "Last updated by"; KNOWLEDGE.md if anything
   was learned; cycle_budget.py done; git add <files> (never -A), commit
   (attribution lines), push, verify origin/main == HEAD; cycle_close.py
   --label "<cycle>"; session_report.py --label --moved --agents (the PAPER BOOK
   section must render); worksession_lock.py release --owner cycle;
   list_triggers; send_later successor. A cycle with genuinely nothing to do --
   no new data, no candidate that can move, no verdict due -- closes early and
   says so. Movement = stage change / paper trade / verdict / Salvage check.

STILL BINDING from the refocus memo (research/infrastructure/refocus-2026-09-15.md):
   daytime 2-hour cycles only; no profit deadline is ever an input; console
   retired; Full Scope weekly or on request; session-report claims cite
   path:line; every production record write runs with TONY_PRODUCTION=1 or
   through an entry point that enables it (src/production_paths.py); Sunday
   1 pm is 1-VERIFY (no research). Never display the .databento_key. Do not
   propose data purchases unless Jason asks. Costs are labeled ASSUMED until
   B4b measures them. Reporting to Jason: short, his format (found / why it
   matters / next).

STANDING STATE (update each cycle): <one paragraph>
---
