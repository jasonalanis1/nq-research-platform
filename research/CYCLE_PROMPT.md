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
   BUDGET USE (staff meeting, September 12th, ~4:10 pm CT): the budget is
   a ceiling, not a target -- but do not stop at the first clean
   sub-step if the queue item has more honest, pre-specified sub-steps
   left and budget remains. Continue through the item's own listed next
   steps (e.g. Observatory's remaining resolutions/views) until the
   budget is genuinely used, the item is genuinely exhausted, or sourcing
   is owed instead -- never by inventing new sub-steps, adding scan
   cells, or re-touching anything past its one pre-registered stage just
   to fill time. An early finish is still correct when the reason is
   real; it is the QUEUE that should be sized to the budget, not the
   cycle padded to match it.
4. If the shelf is at floor and nothing else is owed, DRAW the next entry
   (map-ranked) and run its ONE pre-registered scan at the frozen spec;
   register cells in SCAN_REGISTRY; TWO NULLS; block bootstrap is the CI
   of record; first-minute KILL RULE. Then Statistical -> blind Integrity
   Gate -> one-shot Validation etc. per the pipeline. Holdout slots and
   data purchases are Jason's alone.
5. Close-out, in order: ops_checks.py + pytest; pipeline_sweep --write;
   (console retired September 15th -- no state JSON, no push); session
   report research/sessions/<date>-<HHMM>.md; append _session_log.txt;
   NEXT_UP "Last updated by"; KNOWLEDGE.md section 4 + decision log if
   anything structural; cycle_budget.py done; git add/commit (attribution
   lines) and push origin main; worksession_lock.py release --owner cycle;
   list_triggers; send_later successor.
6. REFOCUS (Jason, September 15th, research/infrastructure/refocus-2026-09-15.md)
   governs: daytime 2-hour cycles only; magnitude research FROZEN, no
   batch_screen.py; queue 0-DIR (directional lane, 20 trials, count in
   research/ledger/directional_lane.json) outranks everything research;
   a cycle with no real queue item closes early and says so; no profit
   deadline is ever an input; session-report claims cite path:line;
   anything that appends to a production record runs with
   TONY_PRODUCTION=1 or through an entry point that enables it
   (src/production_paths.py); Full Scope is weekly or on request only. Never display the
   .databento_key. Do not propose data purchases unless Jason asks.
   Reporting to Jason: short updates, his format (found / why it matters /
   next).

STANDING STATE (update each cycle): <one paragraph>
---
