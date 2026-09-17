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
standing-directive-2026-09-15.md + JASON'S AMENDMENT 1 and AMENDMENT 2, both of
September 16th, appended to the same file, summarized at the top of research/NEXT_UP.md).
Read NEXT_UP.md first. The loop is SOURCE -> SPECIFY -> FREEZE -> SCREEN ->
PAPER -> JUDGE -> KEEP / FIX ONCE / KILL -> SALVAGE -> LEARN. The evidence for a
strategy is its paper record. Interrupt Jason only for the three s.10 reasons.

STEP 1 -- PREFLIGHT. python3 src/cycle_preflight.py --owner cycle --note "<cycle>"
   (lock, budget clock 105 min, pipeline sweep, both daily checkers, PAPER BOOK
   status: strategies in paper, trades, days elapsed, judgment point). If
   cycle_budget.py status says UNFINISHED, resume that item/step first.
   THE REFERENCE-DATA GATE (JASON, SEPTEMBER 16th 2026 -- STANDING, his rule, not
   Tony's): ANY REFERENCE DATA PAST ITS COVERAGE DATE BLOCKS THE STEPS THAT USE
   IT AND GETS REPORTED, NEVER DEFAULTED. Preflight runs it
   (cycle_preflight.reference_data_gate; receipt key steps.reference_data_gate)
   against every series in research/ledger/data_coverage.json. BLOCKED IS NOT
   ABORTED: the cycle still runs every step that does not depend on a stale
   series -- sourcing, specifying, freezing and screening price-only candidates
   on the Discovery slice, and close-out -- and the SESSION REPORT MUST STATE
   WHICH STEPS WERE BLOCKED AND WHICH SERIES BLOCKED THEM (session_report
   section 4 OPERATIONS prints it). A series with NO coverage entry at all is
   treated as STALE, not as fine. Do not work around a block, do not default a
   value, do not "assume no event" or carry a level forward: the consumers
   themselves raise ReferenceDataUnavailable and the paper loop records
   outcome "blocked_by_stale_reference_data" and books nothing.
STEP 2 -- DATA CHECK. Is there new price data since the last cycle (ls -la
   data/NQ_1min_databento_*.csv; Jason tops up daily ~7 am CT)? If yes, Step 3.
   If no, do NOT idle and do NOT report "bot checked, not moved": go to Step 4 on
   historical data and say plainly that paper scoring is waiting on data. Data
   stuck > 48 hours = s.10 interrupt reason 3.
STEP 3 -- ADVANCE THE PAPER BOOK. For every strategy at stage PAPER in
   research/ledger/strategies.jsonl (python3 src/strategy_registry.py):
   TONY_PRODUCTION=1 python3 src/bot_stack_paper_run.py --strategy <id>.
   Then python3 src/paper_book.py. Any strategy at 40 TRADES gets a Director
   verdict THIS cycle (s.6: KEEP / FIX ONCE / KILL, recorded in the registry with
   the numbers). AMENDMENT 1: 40 trades is the ONLY judgment point -- nothing is
   ever judged on fewer, SLOW or not; a strategy that passes six weeks under 40
   trades simply keeps trading (no KILL, no verdict); the 15-trade floor is gone.
   SLOW strategies (screen rate * 126 < 40) paper trade in the BACKGROUND, take
   NO QUEUE SLOT, run no clock, and are judged whenever they reach 40 trades. Any KILL -> Salvage check (s.7 menu only) this
   cycle or next; result to LEARN (research/KNOWLEDGE.md) either way. The
   execution dummy and B3 rows are PLUMBING -- never judged, never a candidate.
STEP 4 -- ADVANCE ONE CANDIDATE ONE STAGE. Highest-priority candidate not yet
   in PAPER (registry latest stage; Director priority order in NEXT_UP):
   SOURCE -> SPECIFY (whole trade: entry/exit/stop/sizing/costs from
   src/cost_model.py with all four combinations stated, mechanism paragraph,
   "where this should fail") -> FREEZE (spec file under
   research/infrastructure/strategy-specs/ + src/strategy_s###_*.py, sha256 of
   both into the registry, its own commit, BEFORE any data) -> SCREEN
   (python3 src/screen_strategy.py <module>, Discovery slice only, one number:
   net after ASSUMED costs; > 0 -> register in bot_stack_paper_run.STRATEGIES
   and run it into PAPER today; <= 0 -> SALVAGE by the menu, spawn S###a at
   SPECIFY if a menu condition is profitable, LEARN either way).
   AMENDMENT 2 (Jason, September 16th): COSTS COME FROM src/cost_model.py AND
   NOWHERE ELSE -- MNQ market round trip $2.60 = 1.30 index pt (commission
   $0.25/side + exchange/regulatory/clearing fees $0.55/side + 1 tick/side),
   labelled ASSUMED; the old "$6.00 = 3.0 pt" charged a full-size NQ commission
   to a micro and was 2-3x too high. AT SPECIFY, REJECT ONLY IF THE EXPECTED
   PER-TRADE EDGE IS BELOW THE PER-TRADE COST ITSELF (cost_model.specify_gate);
   OTHERWISE IT GOES TO SCREEN. There is no 3x-cost pre-screen and never was --
   that was Tony's invention and it is deleted. EVERY SCREEN REPORT SHOWS ALL
   FOUR COMBINATIONS SIDE BY SIDE (MNQ market, MNQ limit, NQ market, NQ limit):
   net $, net R, per-trade edge in points vs per-trade cost in points, so it is
   visible whether a losing net is the pattern or the contract (in POINTS the
   full-size NQ costs about HALF the micro). EVERY LIMIT-ENTRY FIGURE IS AN
   OPTIMISTIC UPPER BOUND -- a limit order is assumed always to fill; real ones
   miss fills and are adversely selected -- and is labelled so wherever printed. At SCREEN also
   record the AMENDMENT 1 label on the PAPER row: trades/sessions * 126 < 40 ->
   slow: true (screen_strategy.py prints it; strategy_registry.slow_projection).
   Candidates already in PAPER, SLOW ones included, never block Step 4.
   STANDING OWED ITEM ON STEP 4 -- SALVAGE RERUNS (Jason's follow-up 1,
   September 16th 2026). Step 4 OWNS this and it comes BEFORE sourcing a new
   candidate: the first cycle in which reference-data coverage is current, run
   TONY_PRODUCTION=1 python3 src/rerun_salvages.py --run --write. It re-runs
   every SUPERSEDED salvage (currently S007 and S009, decided on menu condition 4
   labels the code invented past 2021-09-22) against the SAME frozen screen
   results and modules, writes NEW salvage rows that supersede rather than
   replace, and re-decides the spawns under s.7 (one salvage per strategy, menu
   conditions only, and an EX-POST-ONLY condition -- menu 2, the session's own
   range -- cannot carry a spawn). IT REFUSES TO RUN WHILE COVERAGE IS STALE and
   says which updater fixes it; do not force it, do not re-run a salvage by hand
   on stale labels, and do not specify S009a or S010a: both sit at registry stage
   BLOCKED_PENDING_REFERENCE_DATA, take NO queue slot, and their preconditions
   are written on their rows. Preflight prints "salvage reruns owed, blocked by
   <series>" until it fires, then "COVERAGE IS CURRENT: run src/rerun_salvages.py
   THIS CYCLE".
   If the queue is empty, Discovery sources one. SOURCE PRIORITY (Amendment 1):
   **INTRADAY STRATEGIES THAT TRADE MOST DAYS FIRST** -- so the 6-week clock works
   as designed -- then market mechanics, market structure, Observatory, Salvage
   queue, revamp list research/ledger/revamp_list.json; calendar anomalies last.
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
   B4b measures them, and they are read from src/cost_model.py (never
   re-derived, never hard-coded in a study or a strategy). Reporting to Jason: short, his format (found / why it
   matters / next).

STANDING STATE (update each cycle): <one paragraph>
---
