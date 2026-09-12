# Standing cycle prompt (the send_later message, verbatim, so it is never lost)

Reconstructed 2026-09-12 18:45 UTC after a context compaction dropped the
prior text. Only the STANDING STATE block changes between cycles.

---
SCHEDULED CYCLE (Tony, 2-hour cadence, unattended). Do not ask Jason
anything; make the reasonable call, state it in the report, proceed. Never
use create_trigger for the cadence: at close-out, list_triggers (duplicate
check), then send_later the NEXT cycle 2 hours after this one's scheduled
time, this same message with only STANDING STATE updated. If the device is
unreachable, schedule the successor FIRST, then retry the device once.

1. Lock: python3 src/worksession_lock.py acquire --owner cycle --note
   "<what>"; cycle_budget.py status (UNFINISHED -> resume that item/step
   first); cycle_budget.py start --minutes 105.
2. Read research/NEXT_UP.md first (source of truth); pipeline_sweep.py
   --write; run the daily checkers (forward_validate_h118_daily.py, info
   only; study_prospective_exp047.py).
3. SOURCING every cycle (SHELF RULE v2): stock the shelf from every
   channel -- map / literature / practitioner / observatory -- via
   research/sourcing/TEMPLATE.md; mechanism doc BEFORE any scan; map row +
   Idea Inventory entry; record the source channel and the information-
   gain / edge-potential lines. Shelf counts DRAWABLE entries only
   (mechanism doc + ruling + data on disk; PARKED/WAITING headers never
   count). Below floor 3 = SOURCING OWED, never a draw, never an invented
   scope. Work the queue in research/NEXT_UP.md (QUEUE v2) in order.
4. If the shelf is at floor and nothing else is owed, DRAW the next entry
   (map-ranked) and run its ONE pre-registered scan at the frozen spec;
   register cells in SCAN_REGISTRY; TWO NULLS; block bootstrap is the CI
   of record; first-minute KILL RULE. Then Statistical -> blind Integrity
   Gate -> one-shot Validation etc. per the pipeline. Holdout slots and
   data purchases are Jason's alone.
5. Close-out, in order: ops_checks.py + pytest; pipeline_sweep --write;
   generate_console_state.py -o research/_console_state.json; console
   push: device_stage_files that file -> cloud Bash cp to
   /home/claude/console_state.json -> Artifact read_db get collection
   "state" doc "current" with out_dir=/home/claude/console_version_check
   -> write_db set file_path=/home/claude/console_state.json with
   if_version pinned (never /tmp, never /mnt/user-data paths); session
   report research/sessions/<date>-<HHMM>.md; append _session_log.txt;
   NEXT_UP "Last updated by"; KNOWLEDGE.md section 4 + decision log if
   anything structural; cycle_budget.py done; git add/commit (attribution
   lines) and push origin main; worksession_lock.py release --owner cycle;
   list_triggers; send_later successor.
6. CHANGE FREEZE on structure until September 19th: defect fixes with
   tests only; observations go to the weekly review. Never display the
   .databento_key. Do not propose data purchases unless Jason asks.
   Reporting to Jason: short updates, his format (found / why it matters /
   next).

STANDING STATE (update each cycle): <one paragraph>
---
