# NEXT UP — session handoff baton

The ONE file every work session reads FIRST and rewrites LAST. Sessions are
stateless; this exists so no run re-derives context from the 14k-word
docs/BACKLOG.md or the 137-row ledger. Keep it under ~400 words — prune,
don't grow. Permanent record stays in research/ledger/, research/experiments/,
docs/BACKLOG.md. Do NOT read BACKLOG.md unless choosing a genuinely new
research direction. Jason also works this project ad hoc — if "Last updated
by" says an interactive session, that work is done; continue, don't redo.

## In forward validation (paper only, no capital) — DO NOT TOUCH, see scope boundary below

- **H118** vwap_dist_vs_atr LOW tercile, 10-day drift. **REJECTED AS AN EDGE
  September 12th** (Jason, 10:25 am CT, "just apply that and move on") on
  hyp-000121/122/123/126/130/134. The baseline diagnostic
  (research/studies/h118-baseline-diagnostic-2026-09-12.md) showed the
  LOW-tercile 10-day drift is NOT distinguishable from NQ's OWN 10-day drift:
  LOW minus ALL-days is +0.1162 on Discovery with a block-bootstrap CI of
  (-0.2630, +0.4895), and +0.0481 on Validation with (-0.5851, +0.6255).
  Neither clears zero. It made money because NQ went up over 10 days, not
  because the signal knew anything. **Retained as knowledge (failure mode #7),
  no capital, NO PROMOTION PATH, do not re-raise.** The forward log and the one
  open paper position (opened 2026-09-08 at 29538.00, exits ~2026-09-22) keep
  running FOR INFORMATION ONLY -- they are not evidence for anything and the
  position is not a validated trade. Daily checker handles it.
  THIS BULLET SAID "Holdout passed" UNTIL 2026-09-14 and that stale line caused
  a staff meeting to recommend building the live bot around a rejected
  hypothesis. Anything reading this file: the LEDGER's latest row per
  hypothesis_id is the status of record, not prose written before it. A project-wide multiplicity
  check (2026-09-09) found H118's Validation leg alone doesn't survive a
  Sidak correction at N=18 (Discovery and Holdout legs both do) — disclosed
  diagnostic only, no status change. Detail: research/studies/project-wide-multiplicity-2026-09-09.md.
  Jason (interactive, 23:40) also documented a shielded daily-track
  exception and flagged an undefined PAPER VERIFIED review threshold as an
  open governance gap — see _session_log.txt / his own edits for detail,
  not this session's to act on.
- **hyp-000105/106/141 midday-lull range persistence** -- HOLDOUT PASSED
  September 11th, 7:29 pm CT (slot 2 of 5). Conditioning fact (sizing input),
  not a strategy; no forward test as a strategy. Owed: Portfolio question (queue 0).
- **EXP047** weekly momentum tracker (rejected at Discovery, tracked forward
  anyway). Week 3/260. Cumulative +153.5 pts, CI [6.75, 95.58]. Next
  checkpoint week 104. Needs a fresh week of data to advance.

## UPGRADE BRIEF ADOPTED (September 11th, 6:48 pm CT, Jason's direction) — read AMENDMENT v2.5 + v3.2 before working

- Pipeline order CHANGED: Director (absorbs Triage + Re-Eval, one capital call at
  the Validation gate) -> MECHANISM BEFORE THE SCAN -> Discovery -> Statistical
  (+ POWER at the review point) -> BLIND Integrity Gate -> Validation ->
  Monetization -> BLIND Integrity Gate -> Holdout (Jason) -> Portfolio.
- Every scope needs a MAP ANCHOR: research/market_structure_map.md (LEARN
  bucket 5). Inventory entry bar is now FIVE items. Shelf: Entry 8 (M7), 9 (M10,
  rank 1), 10 (M11, rank 2), 11 (M1, rank 3); Entries 6/7 SHELVED (no anchor).
- BLIND Gate checkpoints: build the packet with src/integrity_blind_packet.py and
  hand it to a fresh-context subagent; record its ruling before unmasking.
- Capital protection is code: src/capital_protection.py ($300 -> $500 after a
  measured paper record; H118 excluded). Live-Limited = stage 3.5, Jason-only.
- Data: $20/mo cap, 1-minute bars only. Ops `data-currency` flags >5 stale sessions.
- Reporting shape: daily 2 lines / immediate triggers / weekly map coverage.
- H118 power at the locked review point: ~30% at 40 trades if true 0.40R
  (research/studies/h118-power-check-2026-09-11.md). Review point does NOT move.
- Full record: research/sessions/2026-09-11-2348.md, docs/TONY_UPGRADE_BRIEF.md.

## PIPELINE SWEEP RULE (set by Jason September 11th, 3:44 pm CT) — how every cycle chooses its work

- The 2-hour cadence exists to keep the WHOLE pipeline moving, not just the
  front. Each cycle sweeps every live candidate for the next stage it is OWED
  (front to back, cheapest first) and works as many as the 90-min budget allows.
  A candidate is touched only when owed a stage it has not had; never re-run a
  stage on the same data.
- Tiers: OPEN (Discovery..Validation) fully automated — including spending a
  Validation attempt unattended, Jason's decision September 11th, 3:44 pm CT ("let it run validation
  on its own, only holdout needs me"), but only after Statistical -> Director
  Re-Evaluation (separability first) -> Monetization -> Integrity Gate checkpoint,
  spec frozen before Validation data is touched, one shot.
  GATED (Holdout): cycle prepares the frozen spec + Gate checkpoint, then STOPS
  and lists it under "Waiting on Jason". Only Jason spends a Holdout slot.
  FROZEN (Holdout-passed and beyond: H118, EXP047): untouched until the
  candidate's pre-registered evidence window closes (H118: 40 trades AND 12
  months). Evidence-based, never calendar-based.
- The sweep table lives below under "## Pipeline sweep"; rebuilt each cycle.
- One-time backlog for the first sweep cycle: explicit disposition (advance or
  close to LEARN) for the 8 legacy PROMISING rows: hyp-000023, 025, 027, 031,
  051 (Discovery) and hyp-000106, 057, 048 (Validation-waiting).

## Pipeline sweep

(auto-built by src/pipeline_sweep.py -- do not hand-edit; rebuilt every cycle. Counts: OPEN 2, GATED 0, FROZEN 3.)

- SHELF: Shelf 4/3 DRAWABLE (Entry 32, 33, 35, 36; pending: Entry 15) -> next DRAW: Entry 32 (oldest drawable)
- OPEN hyp-000156 london_open_volatility_burst_6e_m23: reached Statistical -> OWED: Director capital call at the Validation gate (separability first): worth a one-shot Validation attempt?
- OPEN hyp-000162 opening_range_width_midday_range_excursion_nq_m30: reached Director CONTINUE -> OWED: BLIND Integrity Gate checkpoint (src/integrity_blind_packet.py, fresh context, VETO)
- FROZEN EXP047 prospective_validation_weekly_trend_exp047: reached FORWARD VALIDATION -> OWED: nothing -- evidence window open (H118: 40 trades AND 12 months); daily checker only
- FROZEN hyp-000105 midday_lull_afternoon_expansion (re-expressions: hyp-000106, hyp-000133, hyp-000141): reached HOLDOUT PASSED -> OWED: nothing -- Portfolio review complete (see research/studies/, KNOWN TRUE); daily checker only
- FROZEN hyp-000142 vxn_level_vs_trailing_high_next_day_range (re-expressions: hyp-000143, hyp-000144, hyp-000151): reached HOLDOUT PASSED -> OWED: nothing -- Portfolio review complete (see research/studies/, KNOWN TRUE); daily checker only

## EXECUTION BLOCK RULE (Jason, September 14th, data-refresh queue item S3) -- binding
Every cycle report that touches execution (a replay, a live paper session, a fill) ends its report
section with the **Execution** block printed by `python3 src/execution_block.py` (fills this cycle,
REPLAY vs LIVE labelled; cumulative live fills toward 40, slippage measurable at 20; measured cost or
"no live fills yet"; mechanical defects and whether fixed). No separate stream, no new document type.
Flag Jason ONLY on a capital-protection trip, an integrity problem with promoted work, or a defect that
changes a frozen spec's meaning. Never end on a fork.

## SESSION HANDOFF RULES (set by Jason 2026-09-11) — binding for every session, interactive or scheduled

- **EVERY CYCLE CLOSES WITH `python3 src/cycle_close.py --label "<which cycle>"`,** after the
  commit+push and the lock release. It verifies the mechanical half of close-out -- tests pass,
  ops_checks is not FAIL, the work is committed AND PUSHED (not just committed), the lock was
  released, and this cycle's own preflight receipt is present and clean -- then appends ONE ROW to
  research/_cycle_compliance.jsonl. It does NOT write the session report, NEXT_UP or KNOWLEDGE:
  those carry judgment, and a script that generated them would produce exactly the reassuring
  filler the Operations role is warned against. It also does not commit, push or release the lock
  -- it verifies those happened, because a checker that performs the work it checks cannot fail.
  If it reports CLOSE INCOMPLETE, say so in the session report; do not describe the cycle as clean.
- **`python3 src/cycle_review.py`** prints the whole day's cycles side by side from that log --
  which ran, which were complete, which moved the pipeline, and which are DUE BUT HAVE NO RECORDED
  CLOSE. A cycle that fired and died leaves no row, and the absence is the finding, so missing
  cycles are named rather than omitted. This is what Jason reads to check an unattended day.
- **SCHEDULING (changed 2026-09-14):** the day's cycles are PRE-BOOKED as independent one-shots,
  not chained. Previously each cycle scheduled its successor at close-out, so one cycle dying took
  the rest of the day with it silently. The last pre-booked cycle of a day books the next day's.
  A recurring schedule is not available here -- it would require a fresh session per fire and lose
  the handoff context this session carries.
- **EVERY CYCLE OPENS WITH `python3 src/cycle_preflight.py --owner cycle --note "<which cycle>"`.**
  One command: lock, budget clock, pipeline sweep, H118 daily checker, EXP047 weekly checker, and
  the shelf/sourcing position. It writes a receipt to research/_cycle_preflight.json and
  ops_checks' `preflight` check FAILS without a fresh clean one. Added 2026-09-14 after an audit
  found the H118 checker had not run in FOUR consecutive cycles and nothing detected it -- the
  opening sequence used to be a prose protocol a cycle had to remember, while the headline build
  was the part that showed. Skipping it is now visible instead of silent. The preflight makes no
  judgments: choosing the work item (BOT_ROADMAP before research) is still the cycle's own call,
  and SOURCING is still a judgment the cycle performs -- the preflight only reports that it is owed.


- Lock ONLY through `python3 src/worksession_lock.py acquire|heartbeat|release|status`
  (owner = interactive | cycle). Never write research/_worksession.lock by hand.
- Heartbeat before anything slow and at least every 15 min; a holder silent 30+ min
  is dead and the next session takes over AND finishes the orphan's close-out first.
- A scheduled cycle that finds the lock BUSY defers (retry in 15 min), never dies,
  and ALWAYS reschedules its successor before ending — the chain must not break.
- 90-minute budget per cycle; checkpoint into queue item 0 if the work runs long.
- Interactive sessions release the lock at the end of every turn that took it.
- All human-readable times in Central via `python3 src/local_time.py` (TIME RULE).
- Test suite tests/test_worksession_lock.py pins these guarantees. Set up September 11th, 12:36 pm CT.

## SCOPE BOUNDARY (set by Jason 2026-09-09) — read before touching anything above

Automated sessions work BELOW the Forward Validation line only: Discovery,
Triage, Mechanism, Statistical, Director Re-Evaluation, Monetization,
Integrity Gate, Validation-slice tests, tooling, ledger hygiene — for
not-yet-promoted candidates. FORBIDDEN on H118/EXP047 (promoted): no
re-analysis, no re-expression under new methods, no status/spec/log edits.
If you find a genuine integrity problem with a promoted candidate: flag
Jason and STOP, never act on it yourself.

SCOPE DISPUTE RESOLVED (Jason, 2026-09-11, staff meeting: Research
Director / Operations Manager / Integrity Gate): the frozen-H118 rule means
no re-analysis, no edits, no retuning of H118's DEFINITION -- it does NOT
block building the signal-engine tooling in 1b, which only reads the
already-frozen rules and generates signals from them. 1b is UNBLOCKED,
effective immediately (queue item 1 below).

GUARDRAIL (Integrity Gate condition, binding on 1b and everything built
under it): the signal engine's only job is to faithfully reproduce H118's
frozen rules. Any discrepancy between what the frozen spec says and what
the engine actually does -- timing precision, what counts as a fire,
anything -- gets REPORTED, never quietly tuned away. If the engine can't
exactly reproduce the frozen rule, that is a finding about executability
(flag it, log it), not a reason to adjust the engine's behavior toward a
more convenient interpretation. This guardrail applies for the life of the
Execution Clock work, not just its first session.

## BACK-HALF ARCHITECTURE v3 — governs everything after promotion (PERMANENT, never prune)
Full spec: research/infrastructure/back-half-production-integrity-v3.md (frozen 2026-09-10).

Post-promotion ladder: Research-Validated -> Statistical Forward Test ->
Execution-Qualified -> Live-Authorized -> Live-Monitored -> Retained /
Restricted / Suspended / Retired. H118 is at STAGE 2 ONLY.

ANTI-OPTIMIZATION RULE, binding on every session including automated ones:
a frozen strategy is frozen. "Fewer trades than expected, loosen the
filter", "lost three in a row, adjust the stop", "regime changed, adapt it"
are ALL NEW HYPOTHESES -- they enter the front half at the BACK of the
queue under the 2-attempt limit. They are never edits to a promoted
strategy. The only permitted responses to disappointing behavior are
retain, restrict, suspend, retire -- and those are Jason's calls.

A statistical forward test ("does the signal still produce the validated
distribution?") is NOT execution qualification ("does the implementation
capture it under real orders, fills, slippage, latency?"). Never conflate
them. No execution infrastructure exists yet, so stage 3 cannot run for any
strategy today -- H118 can finish stage 2 and still not be live-ready.

## Operational constraints

- Databento fetch cannot run in an automated/bridged session (egress
  blocked; package not installed). Jason runs it manually in Terminal.app.
- Price data current through 2026-09-08. Mounted-folder mtimes unreliable —
  check contents, not mtimes.
- `purgedcv` (DSR/PBO library) AND `pytest` are NOT pre-installed in every
  automated session's shell -- `pip install purgedcv pytest` (or
  `--break-system-packages` if the shell requires it) when a test/script
  needs them. Both confirmed real, working, pip-installable packages.
  Done again this session (2026-09-10 16:xx run).
- **Concurrency**: 3+ automated sessions plus Jason's interactive edits
  overlapped ~23:07-23:40 on 2026-09-09 — still needs Jason's attention
  (trigger cadence/overlap). No ledger corruption found across 3 checks
  since. Leftover scratch, not cleaned up (no delete permission in an
  automated session): `_tmp_patch_larry_validate.py`,
  `src/study_project_wide_multiple_testing_exposure.py` + its spec doc,
  `research/_scratch_worksession/`.

## Done previously (2026-09-10, automated -- 7th automated run today, ~20:15-20:5X UTC)

Queue item 0 (Idea Inventory top-up) run to completion: folded
research/_queue_three_levers.md in as G1/G2 input (G3 already spent as
Scan 005), generation staff meeting added Entry 2 + Entry 3 to
research/idea_inventory.md (3-entry floor briefly met), then per the
DRAW rule drew Entry 1 (overnight_range_vs_atr, first-RTH-hour reaction)
and ran it as Scan 006 (src/market_behavior_discovery_scan_006.py) --
0/3 cells ranked, clean well-powered null, no monotonic gradient.
2-attempt limit on overnight_range_vs_atr now EXHAUSTED (H116 10-day
drift = attempt 1, closed at Validation; this = attempt 2, closed at
Discovery). Mandatory zero-survivor staff meeting held, disposition
PIVOT. idea_inventory.md back to 2 live entries -- TOP-UP owed again,
now queue item 0 above. SCAN_REGISTRY updated (scan_006, 3 cells). No
hypothesis ID spent. Mid-session bridge drop recovered cleanly (lock
found FREE with no explanatory log line on reconnect -- re-acquired,
no data loss, flagged for Jason as a possible gap in the unlogged-
release path; see session report). Self-caught and fixed a lock-
timestamp format bug this session's own first lock-write introduced
("... UTC" suffix breaks ops_checks' parser -- corrected to the format
every other session has used). Test suite 228/228 green. H118/EXP047
untouched, no spend, no Holdout slot used. DISPUTED READING on Execution
Clock 1b still unresolved, still not acted on (5th automated session
running now to leave it). Full: research/sessions/2026-09-10-2015.md.

## Done previously (2026-09-10, automated -- 4th automated run that day, ~12:22-12:40 UTC)

Queue item 0 (costed conditioning-overlay study on hyp-000106) run to
completion and CLOSED. Full detail: research/sessions/2026-09-10-1222.md,
research/studies/ib-breakout-afternoon-conditioned-stop-overlay-spec.md.

LEARN + Integrity Gate pre-clearance (PASS, conditional) first -- confirmed
not a resurrection of the 4 prior overlay screens (exp-077/086/087/093,
all binary group-splits on a static flag; this is a paired mid-trade
stop-width adjustment, mechanistically and statistically distinct, and
fills a 2-day-old KNOWN UNEXPLORED gap). Design: IB Breakout (hyp-000011),
stop re-anchored from entry at 14:00 ET using get_afternoon_conditioning()'s
confirmed multiplier (hyp-000106), target untouched, for trades still open
at that point. Result: only 82/1709 signals (4.8%) ever reached 14:00 still
open -- IB Breakout resolves too fast for this test to have real power.
Affected-only diff -0.0004R, CI [-0.0571, 0.0456], not credible; null holds
under 2x cost stress. Per the pre-registered rule: CLOSES this pairing, no
retuning. Structural LEARN lesson logged (distinct from "no edge to
condition"): this conditioning fact needs a setup with materially longer
time-in-trade to get a fair test -- not a fast-resolving breakout. Ledger:
hyp-000135 REJECTED (parent hyp-000011, diagnostic, not a promotion event).
No staff-meeting trigger met (checked all 4). Test suite 202/202 green
(purgedcv reinstalled). H118/EXP047/EXECUTION CLOCK untouched, no spend, no
Holdout slot used.

## STANDING RESEARCH PRIORITY — favor fast-resolving candidates
Set by Jason 2026-09-10. Validation speed is governed by HOLDING PERIOD,
not by process. A 10-day-hold candidate needs ~8 months to accumulate 40
resolved forward trades. A 1-day-hold candidate needs ~2 months. An
intraday candidate, weeks. Same statistical bar, far faster answer.

So: when scoping any new Discovery scan, prefer SHORT horizons — intraday,
overnight/1-day, and up to ~2-day holds — over the 10-day horizons the
engine has defaulted to (H118 and every Scan 003 candidate were h10d).
This does NOT lower any standard and does NOT retire multi-day work; it
changes which candidates get search budget.

Three honest caveats, which make discipline MORE important here, not less:
  1. COSTS BITE HARDER. One round-trip cost is a large fraction of a small
     intraday move and a trivial fraction of a 10-day move. Realistic costs
     must be applied, and a short-horizon edge that dies on costs is dead --
     do not relax the cost model to save a candidate.
  2. MORE RESEARCHER DEGREES OF FREEDOM. Intraday has many more possible
     windows, anchors and thresholds than daily bars. The project's own
     advisor flagged this. Pre-register exact windows/anchors/thresholds
     BEFORE looking at any result, every time, no exceptions.
  3. MULTIPLE-TESTING EXPOSURE GROWS FASTER. More candidate cells per scan
     means N climbs quickly. Keep SCAN_REGISTRY in
     src/project_wide_multiplicity.py updated every scan so the correction
     stays honest.


## STAFF MEETING DISPOSITION 2026-09-14 (MODIFY) -- BINDING until Jason answers the fork

1. ~~**THE SIZING QUEUE IS PAUSED AT FOUR INPUTS.**~~ **LIFTED 2026-09-14, 11:00 am CT cycle.**
   The pause's stated reason was that the blind Gate's answer on hyp-000162's regime question
   "decides whether B2 has FOUR inputs or ONE wearing four hats". The Director Re-Evaluation
   answered it earlier and more directly: hyp-000162 retains 79.8% holding VXN level fixed,
   75.3% holding the overnight coil fixed, 83.6% holding prior-day range fixed, and 87.2%
   holding ITS OWN LAGGED SELF fixed -- all against a 50% bar. B2's inputs are distinct.
   Leaving a pause whose question is answered would be theatre. The Gate's independent say on
   the placebo is unaffected. Original text follows for the record:
   ORIGINAL -- No further SIZING candidate is drawn until the
   blind Gate answers hyp-000162's regime question, because that answer decides whether B2 has
   FOUR inputs or ONE wearing four hats (prior-day range, coiled overnight, VXN level, M30 -- and
   hyp-000162's placebo red says they may all be readings of one volatility regime). Adding a fifth
   reading of the same regime is not progress. M32/Entry 36 stays DRAWABLE but is NOT drawn under
   this pause. Entries 32/33/35 are unaffected -- they are not sizing inputs.
2. **THE IDEA FACTORY MUST REPORT ITS QUEUE SPLIT BY JOB** (entry-edge vs sizing), with the
   DIRECTION count stated even when it is zero. Today it is zero out of 19 families and nothing in
   the tooling said so. A ranked list where size always wins looks like a healthy queue right up
   until someone asks what is feeding the entry slot. Build this into idea_factory.py's output.
3. Not decided here: hyp-000162's regime question (blind Gate's), and the conditional-stack
   format's last powered null (U28 found nothing that stands out -- stays "not yet").

## BOT MILESTONES — THE TRUNK (Jason, September 13th ~6:00 pm CT: "this is an end goal trading bot... our overall goal should be working to that, not being the best research tool")

  B4a/B7-EARLY — STATISTICAL FORWARD TEST OF THE BOT STACK, STARTS NOW, COSTS NOTHING
  (added September 13th ~10:30 pm CT, Jason: "can we paper trade until we can move to
  the TradingView option?"). Answer: yes, the FREE half of it. Build
  `src/bot_forward_log.py` on the H118 forward-validation pattern -- each session, run
  src/base_entry_b3.py's signal for the day and src/risk_state_engine.py's decision for
  the day, simulate the fill from the session's own bars, and append one row to
  research/forward_validation/bot_stack_forward_log.jsonl: date, permission, size
  multiplier, signal or none, simulated entry/stop/target, simulated R, and the reason
  for any no-trade. TWO CLOCKS RULE, binding: this is a STATISTICAL forward test and is
  labelled that way everywhere. It measures whether the stack behaves as expected on
  unseen days. It measures NOTHING about execution -- no real fills, no slippage, no
  latency, no rejects -- and its output is never described as paper trading and never
  compared with a broker paper run. The B3 entry remains a placeholder whose P&L is never
  evidence; this log is about the MACHINE's behaviour, not about an edge.
  Blocked on nothing. Start it the first cycle B4a's core is in place.
Full document: docs/BOT_ROADMAP.md. IT OUTRANKS THIS QUEUE. Every cycle works the
lowest-numbered incomplete milestone it can actually advance, BEFORE any research
item; research fills the remaining budget. If no milestone can move, say which one
is blocked and why, then fall through.

  B0 Signal contract ................ DONE  (src/strategy_contract.py)
  B1 Signal engine .................. DONE for B3 (src/base_entry_b3.py, walk-forward audit 0 violations)
  B2 Risk/State Engine .............. BUILT 7:05 pm CT (src/risk_state_engine.py, frozen params, tests, daily log)
  B3 Base entry, frozen ............. DONE 7:20 pm CT (spec + src/base_entry_b3.py + tests; placeholder, never an edge)
  B4a Order path (simulated) ........ BUILT 11:00 pm CT (src/broker_interface.py,
                                      src/simulated_broker.py, src/order_path.py;
                                      spec: research/infrastructure/b4a-order-path-spec.md;
                                      34 tests; capital_protection.pre_order_check
                                      called before every order -- B6 is now WIRED,
                                      not just present)
  B4b Order path (real broker) ...... BLOCKED ON JASON -- IBKR futures permission
                                      in 30-day cooldown (~Oct 13th); adapter target
                                      is IB Gateway on Jason's Mac once granted
  B4a/B7-EARLY bot stack forward log  BUILT 11:00 pm CT (src/bot_forward_log.py,
                                      9 tests; STATISTICAL forward test only, two
                                      clocks rule -- never compared with B4a/B7's
                                      execution run; ran clean, 0 eligible sessions
                                      yet, data through 2026-09-08)
  B5 Execution measurement .......... FIRST CUT 11:00 pm CT (src/execution_measurement.py,
                                      4 tests; the 14 checks computed against
                                      whatever order_path journal exists; reports
                                      INSUFFICIENT SAMPLE honestly rather than a
                                      false pass; does NOT itself authorize stage 3 --
                                      that needs a pre-registered minimum sample
                                      once B7 is producing a real run)
  B6 Kill switches wired ............ WIRED 11:00 pm CT -- src/order_path.py calls
                                      capital_protection.pre_order_check() before
                                      every order, fail-closed; blocked-order path
                                      tested
  B7 Continuous paper run ........... LIVE, thin first version, 1:00 am CT
                                      (src/bot_stack_paper_run.py, 14 tests;
                                      own execution anchor 2026-09-08, separate
                                      from the statistical log's forward anchor --
                                      see the file's own header). First real run:
                                      1 session, correctly gate-blocked by B6
                                      (stop too wide for the $50-150 swing band).
                                      execution_measurement.py still INSUFFICIENT
                                      SAMPLE (0 order_intents) -- ends on evidence,
                                      not a calendar date.
  B8 Live-Limited ................... MISSING (Jason's authorization ALONE, $300 cap)
  B9 Scale behind evidence .......... MISSING

RESEARCH'S TWO JOBS UNDER THIS ORDERING: (1) replace B3 with a real edge -- that is
what the Idea Factory queue is FOR; (2) improve B2 with better state variables. A
result that does neither is filed as knowledge and does not move the project.

## SOURCING RULE v3 (2026-09-13, ~5:40 pm CT -- replaces "think of an idea each cycle")
Sourcing no longer means inventing a candidate. Every cycle, sourcing means:
  1. Read the current Idea Factory queue (research/observatory/idea-factory-<date>.md,
     regenerate with `python3 src/idea_factory.py` if older than a week or if a new
     state variable was added).
  2. Take the highest-ranked family that has no mechanism doc yet, and write one --
     the queue entry supplies the pattern, the mechanism doc must supply WHO is on
     the other side and WHAT would prove it wrong. A queue entry with no defensible
     mechanism is SKIPPED, not forced; note the skip and move down the list.
  3. Only if the queue is exhausted of writable families does a cycle source from
     the literature/practitioner channels.
BINDING: the queue is DESCRIPTIVE. A queue entry is never evidence, never a finding,
never quoted as a result to Jason. It is a place to point the normal ladder.
TIMING RULE (binding on every future generation pass): a state may only be crossed
with an outcome window that starts at or after the moment the state is known.
src/idea_factory.py KNOWN_AT is the register; add an entry there before adding any
new state variable, or the engine will rank a definition as a discovery.

## UPGRADE QUEUE v3 (approved by Jason September 13th; freeze fully lifted ~4:55 pm CT) -- BUILD CONTINUOUSLY: every cycle takes the next undone U-items in order after the sweep's owed stages, until the list is empty. The THIS WEEK / WEEKS 2-3 / WEEKS 4-8 labels below are ORDER, not pacing -- Jason (5:08 pm CT): "we need to incorporate those changes now."
Source: research/infrastructure/outside-review-synthesis-2026-09-13.md (six outside
reviews consolidated; section 6 = decisions, section 7 = sequence). Each item names
the review(s) that proposed it so the reasoning is traceable. Rules for this queue:
each item is a pre-registered piece of work with its own doc/test; no item may edit a
frozen candidate's definition; every rule change gets a KNOWLEDGE.md decision-log
line; nothing here touches H118/EXP047 or spends a Holdout slot.

DECISIONS TAKEN (Jason, September 13th): D1 lift for named list -- YES. D2 two-track
mandate -- YES. D3 paper-trade the Risk/State Engine ALONE first (no directional
trigger) -- YES. D4 un-park execution-clock MEASUREMENT (dummy signal, free paper
endpoint) -- YES. D5 Sidak: diagnose read-only first -- YES. D6 Integrity Gate: both
blind packet tightening AND mechanical test suite -- YES. D7 Economic Validity Gate
additions (placebo, concentration, alternative-explanation) -- YES. D8 Observatory
free-look rule -- YES. D9 sourcing emphasis map/structure up, literature higher bar, no
hard percentages -- YES. D10 conditional-retest protocol (F's 8 conditions) -- YES.
D11 swing strategy: Jason has NOT named an exit rule; instead Tony PROPOSES THE
QUESTION (what a swing strategy looks like in Tony's terms + how it plugs into the
current pipeline) for Jason to get outside feedback on -- see
research/infrastructure/swing-strategy-question-2026-09-13.md. D12 goal/capital fit
-- DEFERRED by Jason until paper trading is actually running ("we could talk about
how much money is realistic once we start actually doing paper trading"). D13
reclassify M20/M21 into the scheduled-event volatility family -- YES. D14 source the
VXN-minus-realized-range state variable -- YES. D15 registries/libraries/forms in
cheapness order -- YES. D16 yield metrics + weekly scorecard -- YES. D17 data purchase
still NO, write the six-condition trigger -- YES.

THIS WEEK (no new infrastructure; fits the 2-hour cycles):
  U1. [DONE Sept 13th 5:15 pm CT -- does not double-count; policy note for Jason] Sidak stacking diagnosis, READ-ONLY (review A). Output: research/studies/
      sidak-stacking-diagnosis-2026-09-1X.md -- does the Validation-stage cumulative
      correction re-count Discovery trials against an independent sample? No bar
      change; Jason rules after reading it.
  U2. [DONE 7:10 pm CT -- PASS x4 incl. Sidak N=451; VALIDATION CANDIDATE; blind Gate CONDITIONAL (5 conditions); Validation blocked on 6E data] M23 Statistical stage (owed anyway; reviews B, C, E).
  U3. [M26 DONE 5:00 pm CT -- P1_FAIL, hyp-000159; M27 DONE 7:15 pm CT -- Scan 034 P1_FAIL, Tokyo hour credibly quieter, hyp-000160] M26 and M27 exactly as frozen (C, F). M26 = first sanctioned conditional retest.
  U4. [DONE Sept 13th 5:05 pm CT -- M29 / Entry 33] Source the VXN-minus-realized-range state variable to the shelf as a Layer-0
      primitive (D): VXN daily vs NQ trailing realized range; mechanism = dealer
      positioning dampens (implied >> realized) or amplifies (implied << realized).
  U5. Register review A's three conditional candidates as ONE-condition families:
      (a) fade-to-VWAP x forecast-compressed prior day; (b) overnight-vs-intraday
      return split on NQ vs the drift null; (c) scheduled-event volatility as ONE
      family = M20 + M21 + M23 + NFP/CPI/FOMC on NQ (this is also D13). Mechanism
      docs first, per the existing template.
  U6. [SPEC DONE 5:18 pm CT -> research/infrastructure/upgrade-specs-2026-09-13.md; BUILD owed: integrity_blind_packet.py tightening + src/integrity_checks.py + tests] Write the Integrity Gate blindness spec (B) + the mechanical integrity test
      suite spec (A: drift null, overnight/intraday split, cost sensitivity, roll-date
      contamination, subperiod stability) as pre-registrations; build in U11.
  U7. [CHECKLIST DONE 5:18 pm CT -> upgrade-specs; BUILD owed: template Section 8b + scan-result fields] Write the Economic Validity Gate additions as a checklist (B: placebo -- shifted /
      inverted / random entry; concentration by year / regime / event; alternative-
      explanation list: trend, volatility, seasonality, drift, liquidity, beta).
  U8. [DONE 7:16 pm CT -- 12 closure forms appended (Section 12) + research/ledger/closures.jsonl] Write the closure form (F) and apply it retroactively to this week's eleven
      closures (M13, M14, M17-M25); this seeds the negative-knowledge library.
  U9. Swing-strategy question doc (D11) -- DONE September 13th, see file above; Jason
      takes it out for feedback; nothing built until he returns with an answer.
  U10. Write the Data Acquisition Trigger (B's six conditions) into KNOWLEDGE.md (D17).

WEEKS 2-3 (structural; freeze lifted for these):
  U11. [DONE 5:15 pm CT -- src/observatory_free_look.py; first read-out research/observatory/free-look-2026-09-13.md: direction is noise at time-of-day x state too; M29 distinct but sign opposite] Observatory FREE-LOOK mode (D): descriptive time-of-day windows (overnight,
       first 30 min, midday, last hour, around events) x validated states, on the
       Discovery slice ONLY, spends NO hypothesis ID, registers NO scan; output is a
       descriptive table; anything with a footprint then goes through mechanism doc ->
       registered family -> normal pipeline. This is a rule change: log it.
  U12. [BUILT + RUN 2026-09-13 ~5:40 pm CT -- src/idea_factory.py; first queue
       research/observatory/idea-factory-2026-09-13.md: 1045 cells ranked, 315
       dropped circular by the new TIMING RULE, 143 candidates in 19 families,
       ZERO direction families. Run 1 of the engine produced a z=-20.4 "discovery"
       that was circular (vwap_dist known at the close, tested against the same
       session) -- the timing rule was added because of it and is now binding on
       all generation.] Discovery Engine v2 (A): per state variable, a pre-registered OUTCOME
       BATTERY -- mean vs drift-null, range ratio, MFE/MAE, time-to-resolution -- cut
       by session window, FDR within the battery, every cell registered up front.
       Extend with B/E/F question dimensions as families get registered.
  U13. [= BOT MILESTONE B2 -- BUILT 7:05 pm CT: src/risk_state_engine.py + frozen params + 9 tests + daily log] Risk/State Engine spec (A, B, E): inputs = validated range facts (range
       contraction, overnight coil, midday-lull/afternoon, VXN level, +U4 if it
       passes); outputs per session = expected range, target distance, stop distance,
       size multiplier, trade-permission flag. Frozen, versioned, NO P&L claim. This is
       what gets paper-traded first (D3).
  U14. Execution-clock MEASUREMENT (A, D4): dummy signal on the H118 order path via the
       free paper endpoint; measure fills vs reference, slippage, latency,
       reconciliation; sets the "unset" thresholds. Spend pre-approved 9/10.
  U15. Integrity Gate build (U6): tighten src/integrity_blind_packet.py (evidence in,
       narrative out) + mechanical suite as ops_checks-style code.
  U16. [SEEDED 5:20 pm CT -> research/registry/facts.md; feature cards owed] Fact registry / market-behavior library (C, E) + feature-library definition
       cards (F) -- start from the existing validated facts.
  U17. Family-level attempt accounting in src/project_wide_multiplicity.py (C, F).

WEEKS 4-8:
  U18. Shadow/paper engine running the Risk/State Engine on live sessions, logging every
       signal, blocked trade, exception, expected vs assumed fill (C, E, F).
  U19. Exit research pipeline on the first prototype (F, A): MFE/MAE, time-to-target,
       P(target before stop), by vol state and session; the five-exit predeclared
       family (fixed stop+target / +time exit / +vol-trailing / +session-end / one
       state-conditioned exit). Parameters from paper excursion data, never backtests.
  U20. Intake + test-design forms as queue gates; idea genome lineage (E, F).
  U21. Metrics dashboard on the ten yield metrics / weekly scorecard shape (C, F).
  U22. Day-60 review: Data Acquisition Trigger check; D12 goal/capital conversation
       once paper trading has a record.
  U23. [DONE Sept 13th ~6:05 pm CT -- console v23 published: Bot panel at the top of the Now tab, H118 card corrected to rejected/information-only, budget copy 90->105 min] Console: render the bot-milestone table (research/_console_state.json now carries
       `bot_milestones`, `upgrade_queue`, `ordering_principle` as of Sept 13th ~5:55 pm
       CT; the published console HTML does not display them yet). Add a "Bot" panel at
       the TOP of the console, above the research funnel -- the bot is the goal, the
       funnel is the feeder. Republish the artifact.
       CONSOLE v25 (Sept 13th ~9:15 pm CT, Jason's request): the two 'How it works' diagrams are now
       interactive -- every stage in the idea-journey diagram and every box in the work-sourcing diagram has
       a tap target that opens a written expander below it (what happens there, who runs it, what kills it).
       Keep those expanders in sync when a stage's rules change.
       CONSOLE v24 (Sept 13th ~9:05 pm CT): new 'How hypotheses are shaped' card driven by a `methodology`
       key in the state doc (summary, build U25-U30 with statuses, stacks_attempted, in_flight, rules). Every
       console push must PRESERVE and update that key (tick U25-U30 statuses; bump stacks_attempted when a
       stack is registered). State doc is now version 85.
  U24. [DONE Sept 13th ~9:35 pm CT -- update_status guard + status vocabulary + 5 tests] Status-transition guard in src/research_ledger.py (from the 7pm test cycle): refuse
       VALIDATION CANDIDATE unless a Validation-slice result is attached; PROMISING is the
       only pre-Validation status. (hyp-156 was mislabelled and ops_checks flagged a Holdout slot.)

CONDITIONAL STACK FORMAT (ADOPTED at the Sept 13th ~9:00 pm CT staff meeting, disposition MODIFY;
record: research/infrastructure/staff-meeting-conditional-stack-2026-09-13.md; proposal:
research/infrastructure/conditional-stack-implementation-proposal-2026-09-13.md). Build order,
AFTER any bot milestone that is unblocked and AFTER the hyp-156 Gate conditions:
  U25. [DONE ~9:08 pm CT -- src/stack_spec.py + STACK_REGISTRY/register_stack/stacks_attempted + 8 tests] [S1] Stack spec schema (JSON: layers with variable/edges/known-at, order, trigger, horizon,
       exit, cost model, floor, MDE) + spec HASH written into SCAN_REGISTRY at registration
       (src/project_wide_multiplicity.py). A different hash is a different trial. K look-cells
       from the free-look interaction table are recorded alongside the hash.
  U26. [DONE ~9:12 pm CT -- TEMPLATE 4a/4b/9a, UNDERPOWERED status, Gate brief] [S3+S5] Mechanism template Sections 4a (one mechanism per layer), 4b (interaction claim),
       9a (floor + minimum detectable effect, set BEFORE Discovery); closure status `underpowered`
       (distinct from `data limitation`; consumes an attempt); Gate standing brief +2 lines
       (every layer coded, one mechanism per layer, interaction stated, no layer added after a
       null, hash matches, look-table attached).
  U27. [DONE ~9:20 pm CT -- src/stack_scan_runner.py + 5 tests] [S2] src/stack_scan_runner.py: frozen spec in -> layers evaluated in time order (refuses
       out-of-order known-at), year-chunked occurrences with entry timestamps, pre-registered
       cells, PAIRED mode (trigger alone vs trigger inside context; the claim is the difference).
  U28. [S4] src/idea_factory.py --interactions: pairwise state cross-tabs, timing rule on BOTH
       layers, same circularity guard; output is a queue table, never evidence.
  U29. [DONE ~9:30 pm CT -- Stack A registered (hash 4df7b408) and RUN: POWERED NULL, hyp-000161; study research/studies/stack-a-2026-09-13.md] [S6] Stack A, paired, registered as TWO trials: B3 breakout alone vs inside HIGH
       expected-range context (B2 tercile). Mechanism doc first. Floor 100 occurrences + MDE
       pre-registered. Ceiling 2 layers until the format has one result. One stack in flight at a time.
  U30. Stack B (ICC pullback, deterministic 5-min structure turn) only after Stack A closes, on
       novelty grounds; format KILL = two powered nulls -> close the format, record in KNOWLEDGE.

## Queue

   0-NEW. LEARN / METHOD ITEM, queued September 14th 5:00 pm CT by the Portfolio stage --
      NOT a re-litigation and nothing promoted is modified by it. SINGLE-FACT SEPARABILITY
      AT THE 50% BAR IS TOO WEAK A TEST. hyp-000162 cleared it against every validated fact
      individually (75-88% at Discovery, 69-96% replicated out of sample) and then retained
      only 18% (linear) / 52% (stratified) against the three held JOINTLY, with neither
      interval clearing the bar, and added nothing to the stack's forecast. Every
      conditioning fact in the registry was cleared against the one-at-a-time version.
      OWED: (a) make the JOINT residual test (src/portfolio_hyp162.py, T1+T2+T3) the
      standard Portfolio test and say so in the agent protocol; (b) re-check hyp-000105 and
      hyp-000142 against it -- hyp-000142 already showed 53% against two facts jointly and
      was promoted anyway. A re-check that fails does NOT retract a promoted result on its
      own; it produces a finding for Jason and the Director.


   0. FRONT OF QUEUE (September 11th, 7:35 pm CT): FIRST -- Portfolio's activation
      question for hyp-000105 (HOLDOUT PASSED, conditioning fact): incremental
      information beyond range contraction (hyp-046/048) and overnight coil
      (hyp-056/057), or the same latent volatility state restated? Method:
      partial-correlation / conditional-effect check of the afternoon-range ratio
      on narrow-midday controlling for the other two states, Discovery+Validation
      data only (Holdout is spent, do not reopen). Record in research/studies/,
      LEARN KNOWN TRUE either way. THEN the shelf draw below.
      (Was, 6:48 pm CT:)

   0b. DONE September 11th, 9:32 pm CT -> research/studies/learn-closed-family-audit-2026-09-12.md
       (37 claim clusters, 0 new shelf entries, 3 parked on data). Original text:
       LEARN CLOSED-FAMILY AUDIT (Jason, September 11th, 7:50 pm CT: "yes queue
       it"). One-time, one cycle, AFTER the Portfolio question in item 0 and
       BEFORE the Entry 9 scan. For every closed idea family in the ledger
       (group by idea key; ~100 families): record (1) attempts spent (1 or 2),
       (2) how it closed (clean null / named failure mode / cost-dominated /
       closed-on-Validation), and (3) for families with ONE attempt left only:
       does any research/market_structure_map.md entry supply a genuinely
       DIFFERENT mechanism claim -- a new reason the market would do it -- not
       a new filter, horizon, or bucket boundary? Integrity Gate rules per
       family: NEW CLAIM (eligible for a shelf entry, attempt 2 of 2, map
       anchor required) or CLOSED FOR GOOD (written down so it is never asked
       again). Output: research/studies/learn-closed-family-audit-<date>.md
       with the full table, plus shelf entries for any that pass (Director
       ranks them against Entries 9-11; they do not jump the queue). Expected
       outcome, stated up front so the audit is not pressured to find things:
       most families are CLOSED FOR GOOD. Two are already re-entered this way
       (M1 <- closing_pressure_reversal, M4 <- pre_fomc_drift); do not
       duplicate them. Cost: no scans, no data, ledger read only.
 the "## Pipeline sweep"
      section above is authoritative for candidates. Under AMENDMENT v2.5 the
      shelf draw (Entry 9, map-ranked #1) owes a MECHANISM DOC BEFORE ANY
      SCAN: write research/mechanisms/<name>.md (claim, counterparty, 2
      predictions, falsifier, pre-registered) for Entry 9, then 10, then 11,
      in that order, one per cycle if the budget is tight. Only then scope
      and run the scan. hyp-000105 owes its BLIND Integrity Gate checkpoint
      (packet builder) before it is listed as Waiting on Jason. Free $0
      calendars (BLS/Fed release dates, Nasdaq-100 rebalance dates, CME
      holiday/early-close) are a Discovery filing task under data/calendar/
      -- no spend, no approval needed; note egress may block it in a cycle,
      in which case list what is needed and move on.

   0a. DRAFT AWAITING MECHANISM + DIRECTOR REVIEW (not yet an inventory
       entry, routed 2026-09-11): event-conditioned re-cut of
       exp-110/hyp-000081 (Opening-Hour Reference-Level Fade). Full
       resurrection check, mechanism claim, and pre-registered predictions
       in research/studies/event-conditioned-reference-level-fade-h81-recut-draft.md.
       DO NOT pull event-calendar data until this writeup clears Mechanism
       and Director. Wide original version (Jason's uploaded doc) considered
       and declined as drafted -- parked in docs/BACKLOG.md ("Parked"
       section) as re-mining already-closed ground.
      (volume_vs_expected LOW, next-day RTH range vs trailing-20d
      average) added, floor restored to 3 (Entry 4, 5, 6). No TOP-UP
      currently owed. If the queue empties, draw order is Entry 4, then
      Entry 5, then Entry 6.

   1. EXECUTION CLOCK — running NOW, in PARALLEL with H118's frozen
      statistical forward test. Approved by Jason 2026-09-10. Spec:
      research/infrastructure/back-half-production-integrity-v3.md
      (AMENDMENT v3.1). Build the MINIMUM execution-validation layer for H118
      only — no production stack, no dashboards, no multi-strategy
      architecture. Target: the 14 execution checks in v3.1 section 4.
      H118's frozen spec is INPUT ONLY; never modify it to suit the
      implementation.

      JASON'S STANDING DIRECTION (2026-09-10): start now with what we have,
      don't wait for a perfect design. Iterating on the MACHINERY (fill
      measurement, order timing, logging) is expected and good. Iterating on
      the STRATEGY because execution disappointed is a NEW HYPOTHESIS — back
      of the front-half queue, never an edit to a promoted strategy.

      Work in this order. 1b is UNBLOCKED -- scope dispute resolved by
      Jason 2026-09-11 (see SCOPE DISPUTE RESOLVED note above). The
      Integrity Gate guardrail there is BINDING on this item: reproduce
      H118's frozen rules faithfully, report any discrepancy, never tune
      the engine toward convenience.

      1b. SIGNAL ENGINE -- DONE 2026-09-11 (checks 1-2 of 14 PROVEN).
          src/execution_clock_signal_engine.py (walk-forward, no
          lookahead, H118's frozen rule + frozen 15:58:00 America/
          New_York entry/exit convention) + src/execution_clock_check_1_2.py
          (independent comparison harness vs. forward_validate_h118_daily.py's
          own logic, never touches h118_forward_log.jsonl) +
          tests/test_execution_clock_signal_engine.py (8 tests) +
          research/studies/execution-clock-signal-engine-checks-1-2.md.
          RESULT on full data on disk (2015-01-02..2026-09-08, 2992
          trading days): 1009 signal days, 0 duplicates (CHECK 1 PASS);
          exact match against the forward validator's own logic on every
          day, 0 mismatches (CHECK 2 PASS). FLAGGED, not resolved (binding
          guardrail): 18/1009 entry days and 41/968 resolved exit days
          have no 1-min bar at the frozen 15:58:00 NY timestamp (holidays/
          early closes) -- needs Jason's input, likely folds into 1a.
          Full: research/sessions/2026-09-11-0302.md.
      1a. EXECUTION-QUALIFICATION SPEC — UNBLOCKED 2026-09-10. Jason chose
          OPTION B: a single market order at 15:58:00 America/New_York on
          both the signal date and the exit date, 1 MNQ, deterministic
          timestamp (not a window -- a window invites discretion, and
          discretion is unmeasurable). Frozen at
          research/studies/h118-execution-approximation-spec.md. That spec
          is the INPUT to this item, not a substitute for it: still to do
          here is making the 14 execution checks concrete for H118 and
          pre-registering the MINIMUM EXECUTION SAMPLE (evidence-based,
          not calendar-based) that ends stage 3.
          NON-NEGOTIABLE, carried from the frozen spec: every fill records
          the intended reference close, the actual fill, and the deviation
          in BOTH points and R, per side, at fill time. The deviation is
          never assumed zero and never silently folded into the result.
          Scale of what is being measured: the working effect is ~0.40R
          (~147 pts). 2 pts/side is noise; 15 pts/side is a fifth of the
          effect. We do not yet know which world we are in.
      1c. Order construction, logging, position reconciliation against a free
          broker paper endpoint. Measure fill vs expected, slippage, latency.
          Needs 1a answered first.
      1d. Failure handling: prove a crash cannot silently leave a position
          open. Full reconstruction logs.

      ANSWERED 2026-09-10 (was the blocking question for 1a): the research
      assumes entry AND exit at the RTH reference close, but you cannot
      transact at a close you have not yet observed. How the implementation
      approximates it
      must be decided by Jason, frozen, then the deviation MEASURED, not
      assumed negligible. Does NOT block 1b. OUT OF AUTOMATED SCOPE (touches
      H118) -- flag and stop only, never act.

## BUDGET CLOCK / RESUME / BUSY-WORK ALERT (Jason, September 11th ~9:55 pm CT; PERMANENT)
- Budget is 105 of the 120-minute cadence. `python3 src/cycle_budget.py start --minutes 105` right after the lock; `checkpoint --item --step [--files]` after EVERY stage artifact lands; `remaining` BEFORE starting any new stage (exit 3 = <=15 min left: close out now; exit 4 = over: checkpoint and close out immediately); `done` at close (writes the value snapshot).
- Resume: step 2 of every cycle runs `python3 src/cycle_budget.py status`. UNFINISHED = the prior cycle hit budget mid-task: resume THAT item at THAT step first. Never re-register a scan that is already in SCAN_REGISTRY; never re-run a stage whose artifact exists; a file listed under `files` is half-written until its stage's artifact says otherwise.
- Alert: ops_checks `value` FAILs on BUSY WORK (3 closed cycles with zero artifact deltas) or QUEUE EXHAUSTED (nothing owed + empty shelf). Either is an IMMEDIATE item: message Jason, do not manufacture work. `checkpoint` WARN = unfinished work to resume.

## Blocked — needs Jason
- **THE $50-150 PER-TRADE SWING BAND HAS GONE STALE AGAINST NQ'S PRICE LEVEL -- YOUR CALL.**
  The data top-up landed September 14th (cost $0.018). Four complete sessions (Sept 8-11) ran
  through B7 for real and ALL FOUR were blocked by capital protection, every one for swing width
  ($272-$468 per micro against a $50-150 band). Not bad luck: across 2,721 B3 signals the share
  fitting the band is 36% overall but **2.4% in 2026** (median swing $376), against 77% in 2018
  (median $85). The band is written in fixed dollars and NQ has gone from ~4,500 to ~29,500, so the
  same percentage stop is now several times the dollars. At 2.4%, B7 sees a tradeable signal about
  once every 40 sessions and the 40-fill execution sample takes YEARS. B6 is working correctly;
  what it protects against has moved. OPTIONS: (a) leave it -- safe, and the execution record stays
  frozen indefinitely, along with everything gated on it including hyp-000162's open cost clause;
  (b) re-express the band as a fraction of contract notional or in ATR units so it scales with the
  instrument, keeping the dollar figure as an absolute ceiling -- restores the rule's original
  INTENT where fixed dollars have lost it, but changes a frozen capital parameter; (c) keep the band
  and accept that B3 (an explicit placeholder) is not the strategy that produces the record -- which
  means waiting for a validated directional candidate the project does not currently have.
  STAFF RECOMMENDS (b) with the ceiling kept. Nothing changed automatically.
  Full diagnostic: research/integrity/swing-band-vs-instrument-price-2026-09-14.md

- **STAFF MEETING 2026-09-14 "what to do" -- **CORRECTED 2026-09-14 ~10:00 am CT, ITS CENTRAL
  PREMISE WAS FALSE.** The meeting said the project has one directional Holdout-passed edge
  (H118) and recommended building the live bot around it. **H118 WAS REJECTED ON SEPTEMBER
  12TH** and the note said "do not re-raise". The project has ZERO validated directional
  edges. Option (a) as written is VOID -- there is nothing to build a live bot around.
  What survives: the finding that the generation engine produces 0 direction candidates out
  of 19 families -- the entry slot has nothing feeding it, at ANY horizon.
  **SCOPE, corrected by Jason 2026-09-14 ~10:10 am CT (an earlier line in this file said
  "larger trades only" -- that was my overreading and is WRONG):** INTRADAY REMAINS THE
  PRIMARY SEARCH TARGET AND THE PROJECT'S DIRECTION. Larger / multi-day candidates are NOT
  disqualified for being larger -- if one appears it is legitimate and gets worked. NO
  HORIZON BOUNDARY IS IMPOSED YET; we are still looking and the search stays open. See the CORRECTION section of
  research/infrastructure/staff-meeting-what-to-do-2026-09-14.md.
- **SUPERSEDED (kept for the record):** the original fork text. Full record:
  research/infrastructure/staff-meeting-what-to-do-2026-09-14.md. The finding: the project's ONE
  directional Holdout-passed edge (H118) is a 10-DAY SWING trade that the intraday bot's own
  capital rules EXCLUDE BY NAME (capital_protection excluded_strategies, ~$1,000-1,400 swing vs the
  $50-150 band). The bot's entry slot is still the B3 placeholder, which its own spec says is never
  an edge -- so B8 (live) is unreachable on the current path. And the generation engine cannot fix
  it: of 19 candidate families in today's Idea Factory queue, 17 are SIZING and **0 are DIRECTION**,
  because volatility is predictable and direction is not, so size wins every |z| ranking on merit.
  OPTIONS: (a) build the live bot around the edge we actually found -- i.e. the swing strategy, D11,
  currently "awaits Jason -- do not build"; the intraday bot becomes an execution testbed;
  (b) keep the intraday bot and fund a real hunt for an intraday directional edge, ~200+ more trials
  on Statistical's numbers with no guarantee, and the generation engine needs rebuilding to even
  produce candidates; (c) keep both as-is, intraday bot stays paper-only indefinitely, and the
  project stops describing B8 as reachable. STAFF RECOMMENDS (a), caveat stated: most of the
  engineering to date becomes infrastructure for a strategy it was not designed around, and the
  capital model needs rewriting from its band upward.
- **DATA REFRESH -- APPROVED (Jason, September 14th, queue item). ONE COMMAND OWED FROM YOUR TERMINAL:**
  `cd ~/Documents/nq-research-platform-live && python3 src/data_topup_databento.py` -- quotes the exact
  cost first, refuses above $15 (top of the approved $5-15 estimate; `--cap` to raise), writes a NEW
  NQ file (old one untouched), logs the real dollar figure to data/_databento_cost_log.json, runs the
  continuity check. Neither sandboxed shell can reach hist.databento.com (proxy 403, verified). Once the
  file lands the next cycle owes, in order: Step A `python3 src/b7_replay.py` (mechanical replay, must be
  clean) -> Step B live paper (`bot_stack_paper_run.py`, ends on evidence) -> Step C forward clocks resume.
  Order-flow / order-book data remains NOT approved. Was: the unanswered operating-cost call above.
- **6E VALIDATION DATA PULL (hyp-000156) -- YOUR CALL, unchanged.** Statistical PASS x4, all five
  blind-Gate conditions resolved in writing, validate_hyp156.py written and hashed before data
  exists. Validation cannot run without the 6E validation slice. A standing "no" is a fine answer;
  it just means hyp-000156 sits where it is indefinitely, and better decided than defaulted.

- **H118 FORWARD VALIDATION: the one open position predates the forward anchor. YOUR CALL.**
  Found by the 2026-09-14 automation audit (research/integrity/automation-audit-2026-09-14.md,
  finding 1). `forward_validate_h118_daily.py` sets FORWARD_VALIDATION_ANCHOR = 2026-09-09 and
  refuses to log any signal before it, on the stated grounds that an earlier session is Holdout
  Generation 1 data, not genuinely forward. The forward log's ONE row is signal_date 2026-09-08 --
  a day before the anchor. Git shows why: commit c1dc7b2 (Sept 9th 22:57) fixed the boundary bug,
  and a3d6730 (23:02, five minutes later) committed the log still containing the row the bug wrote.
  The guard was never applied retroactively to the one row that predated it. Options: (1) void the
  row and start forward validation clean at the anchor, costing 1 of the 40 trades; (2) keep it,
  annotated as pre-anchor and excluded from the 40-trade count, resolving for information only;
  (3) keep it as-is with the reasoning recorded. NOT ACTED ON: H118 is frozen and an automated
  cycle must never edit a forward-validation evidence log on its own initiative. Until decided,
  H118's honest forward record is "zero genuinely-forward observations, one pre-anchor position
  open" (resolves ~2026-09-22).


  * BROKER ACCOUNT — UPDATE September 13th ~11:15 pm CT: Jason opened an INTERACTIVE BROKERS
    (IBKR Pro) individual account tonight and funded it; the PAPER TRADING ACCOUNT was created
    at ~11:10 pm CT (assisted in his browser, manual-approve mode). FUTURES trading permission
    was DECLINED on the application and is IN COOLDOWN -- retry not possible before ~October
    13th. Options/warrants "more info needed" -- not needed, ignore. So B4b's real adapter is
    IBKR (TWS API / IB Gateway on Jason's Mac, paper port 4002/7497), and real-broker futures
    paper trading waits for the permission. OPEN QUESTION to verify at gateway-connect time:
    whether the IBKR paper account simulates futures without the live permission. Do NOT
    re-raise the permission with Jason before mid-October; do NOT touch the financial profile.
    B4a proceeds regardless.
  * (superseded, kept for history) BROKER ACCOUNT — REFRAMED September 13th ~10:10 pm CT, NO LONGER BLOCKING THE TRUNK.
    Researched tonight: Tradovate requires a live account funded to $1,000 equity + $25/mo before
    it issues API credentials (their own staff, on their forum) -- a free sim account does NOT
    qualify, and neither does a TradingView account. IBKR gives a free paper account on the same
    API the live account uses, but the live account must be "approved and funded"; no published
    minimum and no minimum deposit on an individual cash account, so the qualifying deposit is
    small. Jason does not have the $1,000 available. DO NOT re-ask, do not nag, do not raise
    money questions (D12 stays deferred). B4 is now SPLIT in docs/BOT_ROADMAP.md: B4a (the order
    path against a simulated broker interface, including the deliberate-failure broker and B6's
    kill switches) is BUILDABLE NOW and is the trunk work; B4b (the real broker adapter) is a
    connector against an already-tested contract, and waits until an account exists. When Jason
    raises it, IBKR is the cheaper path to price out first.

  * 6E VALIDATION-SLICE DATA PULL (new, September 13th ~9:40 pm CT). hyp-000156's five
    blind-Gate conditions are now resolved in writing and src/validate_hyp156.py is written
    and hashed, so the only thing between this candidate and its one-shot Validation is the
    data: 6E 1-minute OHLCV, 2021-10-04 -> 2024-01-03, via src/quote_data_pulls.py on
    Jason's Terminal (neither shell can reach Databento). Same data type and vendor as the
    Discovery file; expected cost in the band of the September 12th quotes. $5+ rule: his
    call. NOT a purchase anyone else may make.

CONSOLE PUSH PATHS (binding, corrected live with Jason September 12th,
8:09 am CT -- this supersedes any cycle prompt wording that says "a
scratchpad path"): the Artifact tool is given ONLY paths inside the cloud
workspace. read_db out_dir = /home/claude/console_version_check (exactly).
write_db file_path = /home/claude/console_state.json (exactly, after the
cloud-Bash cp from the staged upload). Never /tmp, never /mnt/user-data.
Verified live: both calls complete with no approval request. The full
sequence is: device_stage_files the console JSON -> cloud Bash cp to
/home/claude/console_state.json -> read_db get with that out_dir (version
only) -> write_db set with if_version pinned.

CHANGE FREEZE -- LIFTED (Jason, September 13th, ~4:55 pm CT): the checkpoint was held
today instead of the 19th (research/weekly/2026-09-13.md). The named list is
"## UPGRADE QUEUE v3" below; with no separate 19th review, nothing else remains
frozen. Routine rule still applies: any structural change gets a KNOWLEDGE.md
decision-log line and its own doc/test; frozen candidates' definitions are never
edited.

WEEKLY REVIEW (Jason, September 12th, amended September 13th): the first cycle on or after
Saturday 8:00 am CT writes research/weekly/YYYY-MM-DD.md -- one page: shelf state,
what closed and why, what is parked, source-channel hit rates, UPGRADE QUEUE v3
progress, loose ends, and "are we changing things faster than we are learning from
them?" -- and messages Jason with it. The September 19th review is CANCELLED (the
checkpoint was held September 13th; its trigger is deleted). Next routine one:
Saturday September 26th.

KNOWLEDGE.md (Jason, September 12th, 10:44 am CT): research/KNOWLEDGE.md is the organizational
memory -- what is true, what failed and why, what is parked, what is open,
and the dated decision log. Every cycle updates it at close (LEARN update
step) when anything in those sections changed. It is the first thing a new
session reads after this file.

LOOSE ENDS (named September 12th, 10:44 am CT): (1) the three volatility facts have never been
turned into a product -- the vol-conditioned sizing overlay on a simple base
is the biggest open item and a candidate for the checkpoint recommendation;
(2) execution clock (signal engine) is PARKED explicitly now that H118 is
closed; (3) four overlapping governance documents -- consolidation goes on
the review list, not into the freeze window; (4) VXN gated at Holdout, held.

CHECKPOINT (set September 12th, 10:35 am CT, Jason's worry about whether anything will be found):
the new front end gets a defined run -- through September 19th (Jason moved it
up from the 26th), or the first six entries through Discovery, whichever comes first. At that point one page
to Jason: what survived, what it is worth per trade after costs, and ONE
recommendation. If at least one entry has reached Validation, continue. If
none has, the honest conclusion is that this data tier is exhausted for
entry signals and the decision is between (a) buying the data that sees the
participants, or (b) building the product around what has held up --
volatility-conditioned sizing and execution on a simple base. Neither is
failure. Cycles: do not soften a null to avoid this checkpoint.

SHELF RULE v2 (Jason, September 12th, 10:00 am CT: "put the shelf back, keep the research
ideas stuff, use all areas of research"). The shelf stays. Two bolts
tightened:
- SOURCING RUNS EVERY CYCLE, FIRST, FROM EVERY CHANNEL. Before the sweep is
  worked, a fixed slice of the budget (target 20 of 105 minutes; more when
  the shelf is below the floor) goes to reading and scoping: the forced-
  participant map, the literature, practitioner practice, and cross-market
  Observatory relationships. Every entry records its SOURCE CHANNEL so hit
  rates by channel accumulate in LEARN (map / literature / practitioner /
  observatory / gut). We already know map > gut and behavior-first > map;
  now the rest gets measured instead of argued.
- THE SHELF COUNTS ONLY DRAWABLE ENTRIES: written up, mechanism doc done,
  resurrection ruling signed, data on disk. Entries waiting on data or on
  Jason are PENDING, shown separately, never counted. pipeline_sweep.py
  reports "Shelf X/3 DRAWABLE (pending: ...)". The number is honest even
  when it is zero -- and today it is zero.
- FLOOR 3. Below the floor the owed action is MORE SOURCING, never a draw
  and never an invented scope. If three consecutive cycles cannot restock,
  ops_checks raises SHELF STARVING to Jason -- a sourcing problem, not a
  reason to draw thin.
- DRAW only from the shelf, only when the sweep owes nothing else, active
  slate capped at 5. Ranking rule (information gain x edge potential)
  decides draw order.

QUEUE v2 (Jason, September 12th ~9:10 am CT, after three outside-AI responses
were folded in -- research/infrastructure/outside-ai-synthesis-2026-09-12.md
is the reasoning; this block is the work). Cycles work it front to back under
the normal budget clock. HOLD LIFTED (September 12th, 10:33 am CT, Jason): cycles DRAW and SCAN
shelf entries on their own under the normal sweep rules -- no per-entry go
from Jason. Holdout slots and purchases remain his alone. Active slate is
capped at 5 families at any time; everything else sits in research/sourcing/.

1. DONE September 12th, 9:03 am CT -- two-nulls amendment filed (two-layer-methodology.md),
   src/baseline_relative.py + 4 tests, H118 diagnostic run: LOW minus ALL-
   days does NOT clear zero on Discovery (+0.12, block CI -0.26..+0.49) or
   Validation (+0.05, block CI -0.59..+0.63); no gradient; Validation HIGH
   bucket beat LOW. Jason messaged. NEEDS JASON: H118 status (Director
   recommends: reclassify to "not distinguishable from baseline -- closed as
   an edge, retained as knowledge"; keep the free forward log running).
   Original item text follows for the record.
   TWO NULLS + H118 DIAGNOSTIC (Statistical). Amend research/studies/two-
   layer-methodology.md (dated, cite Scan 019 / M12 doc Section 10): every
   long-only directional claim is reported as effect MINUS the unconditional
   drift over the same slice and horizon; every cross-index claim uses the
   residual r_NQ - beta*r_ES (beta from prior data only, frozen within each
   OOS stage) as its outcome. Add src/baseline_relative.py (both helpers) +
   tests. Then the H118 all-days-baseline DIAGNOSTIC on Discovery and
   Validation slices, frozen edges, read-only, nothing frozen touched. File
   research/studies/h118-baseline-diagnostic-2026-09-12.md. One line to
   Jason only if the LOW-minus-baseline CI fails to clear zero.
2. SOURCING STAGE. research/sourcing/TEMPLATE.md with: claim; instrument(s)
   (free field, NQ = default vehicle); holding period (hard filter, hours to
   a few days); forced/constrained participant; mechanism; INSTRUMENT-CHOICE
   GATE (which contract should lead and why at minutes not milliseconds; is
   NQ the vehicle; directional or relative; survives a beta-neutral
   benchmark); footprint; natural resolution and why; exact published spec;
   publication date; published effect size; decay evidence; resurrection
   ruling by name AND by what is measured; product track (directional /
   relative-value / risk-execution); realization path; data needed; KILL
   RULE (if the response is concentrated in the first 1-min bar the family
   terminates, no re-tuning). Then write entries in this order, each a full
   mechanism doc + Idea Inventory entry anchored to a new map row:
   RANKING RULE (Jason, September 12th ~9:50 am CT): order by EXPECTED
   INFORMATION GAIN x EDGE POTENTIAL, not by probability of a positive
   Discovery result. Write-ups and later scans follow this order:
   a. PARKED (not testable at ceiling: needs RTY/ES). LETF close rebalancing, instrument as a factor (RTY/ES/NQ), flow
      measured from AUM. Written (Entry 17 / M13). Either outcome is decisive
      about whether "search where the forcing is largest" is a principle.
   b. PARKED (not testable at ceiling: needs ES). Written September 12th, 9:30 am CT (Entry 18 / M14, waiting on ES data). Hedging-demand intraday momentum (Baltussen et al. 2021 JFE), price-
      only base with gamma regime computed from ES. Low pass odds, highest
      strategic information: it is the gate on buying options data.
   c. DONE September 12th, 11:00 am CT cycle (Entry 19 / M15, DRAWABLE). Overnight-vs-intraday tug-of-war (Lou, Polk, Skouras 2019 JFE).
      Probably true; explains H118; tells us where NQ's return lives; also
      a fast trade in its own right (hold overnight, flat by the open).
      Ruling vs gap-fade family and H116.
   d. PARKED (needs ES + SPY/QQQ). Cash-open acceptance/rejection of the pre-open NQ/ES residual --
      the cheapest test of whether ANY cross-index relative-value effect
      survives at minute resolution; a kill-rule outcome settles the tick-
      data question for the whole track. Needs SPY/QQQ bars.
   e. DONE September 12th, 11:00 am CT cycle (Entry 20 / M16, DRAWABLE). Intraday momentum (Gao, Han, Li, Zhou 2018 JFE). Ruling vs hyp-000076
      and the IB family. Mostly informative about literature decay; also
      the confound for (a).
   f. PARKED (needs ES + ZT). Curve-conditioned NQ/ES rotation.
   NEXT UP UNDER THE CEILING: c and e are written and DRAWABLE (shelf 2/3). Item 4 closed. Next sourcing toward the floor: item 6 (event reaction shape) and further literature/practitioner entries; then item
   4 Observatory on the FOUR instruments on disk (NQ/ZN/6E/CL), item 5
   practitioner proxies, item 6 event reaction shape. Scans run on the
   cycle's own authority once an entry is DRAWABLE.
   Mechanism doc BEFORE any scan. One shot at the exact published spec.
3. DATA -- CLOSED, NO PURCHASE (see PARKED). Original text kept for the record: in order, each via metadata.get_cost FIRST; any single pull at
   $5.00 or more stops and lists the number under "needs Jason" unless he
   has set a cap (see PARKED below): (i) ES, RTY, YM 1-min OHLCV, outright
   contracts where the feed allows; (ii) NQ outright contract months for the
   witching weeks only -- revives M9; (iii) SPY, QQQ, IWM, DIA 1-min;
   (iv) ZT or SR3; (v) free: VIX/VXN futures settlements from CBOE, LETF
   AUM/shares outstanding from issuer files (manual assembly). Register each
   file in data_loader with a coverage test. If no API key is available to
   the cycle, stop and say so under needs Jason.
4. OBSERVATORY PROGRAM -- CLOSED AT THE DATA CEILING (September 12th, 4:30 pm CT test cycle): all listed sub-steps done -- separability (all 3 pairings separable), lead-lag v1+v2 (none at >=5 min, both sessions, shock-conditioned too; research/studies/observatory-information-transmission-v2-2026-09-12.md), fixed state classifier (variance states condition range two-sided; rate state conditions nothing; research/studies/observatory-state-classifier-v1-2026-09-12.md). Remaining spec items need ES/RTY/YM -- parked with the ceiling. Earlier note (3pm cycle): separability of the 3rd volatility fact confirmed (both pairings separable, research/studies/portfolio-range-contraction-separability-2026-09-12.md); info-transmission v1 done for NQ/ZN/6E/CL 15-min RTH (no lead-lag, research/studies/observatory-information-transmission-v1-2026-09-12.md). NEXT under this item: overnight session, other resolutions (5/30/60-min), shock-conditioned view, then the fixed state classifier. Original spec: an information-
   transmission map across ES/NQ/RTY/YM/ZN/6E/CL at 5/15/30/60-minute bars
   built from the 1-min data: shock -> first responder -> lag -> decay ->
   reversal, conditioned on the three validated vol states + semivariance.
   Plus a FIXED, interpretable state classifier (broad-equity agreement /
   NQ-only residual / rate-confirmed / rate-conflicted / high vs low
   overnight and cash-session variance) reporting forecast return, range and
   MAE per state. No ML. Portfolio's separability check of the range-
   contraction fact vs the other two comes first. Output = map-ready
   entries, not trades. This absorbs the day-type program.
5. PRACTITIONER STREAM (OPENED September 12th, 11:00 am CT cycle; three seeded claims ruled, no entry yet): research/sourcing/practitioner.md -- claims enter
   only via mechanical proxy; seed with day-type by 10:30, opening-drive
   exhaustion, VWAP reclaim after failed breakdown; Mechanism rules on each.
6. LOW PRIORITY, sourcing only: event reaction SHAPE across FOMC/CPI/NFP
   pooled (new claim, small n).

SKIP LIST (consolidated, binding): candlesticks; ORB variants; VWAP/level
fades; gap rules; rejected calendar effects; daily lagged cross-asset
regressions; correlation-regime screens; multi-asset 1-5 day trend; Russell
reconstitution (n~11); CFTC weekly positioning; ML feature matrices; opaque
GEX/"smart money" products; pure 1-minute cross-index lead/lag as a TRADE.

Order: 1 -> 2a-f (write-ups) -> 3 -> 4 -> 5 -> 6. Daily checkers every cycle.

PARKED, NOT FORGOTTEN -- Jason's items, raise only if he asks:
- H118 DECIDED (September 12th, 10:25 am CT, Jason: "just apply that and move on"): reclassified
  REJECTED on hyp-000121/122/123/126/130/134 -- closed as an edge, retained
  as knowledge (failure mode #7). Forward log keeps running for information
  only; no capital, no promotion path. Do not re-raise.
- DATA DECISION (Jason, September 12th, 10:16 am CT): NO PURCHASE. Exact quotes were obtained
  (ES $14.69, RTY $10.77, YM $14.31 -- $39.77 for batch 1) and Jason chose not
  to spend. WORKING ASSUMPTION, binding until he says otherwise: the data
  ceiling is 1-minute OHLCV for NQ, ZN, 6E, CL and nothing else. Entries that
  need other data are PARKED as "not testable at the current ceiling" -- not
  closed, not counted, not re-raised. Research proceeds on what is testable
  now. Do not quote, price, or propose data purchases again unless Jason asks.
- M9 (Nasdaq rebalance): re-parked on a data gap; Jason is sourcing
  roll-day data himself. Details: research/mechanisms/nasdaq-rebalance-
  close-window-m9.md Section 6.
- Data ceiling: both pulls PRICED, nothing bought, in research/
  infrastructure/data-ceiling-pricing-2026-09-12.md. Exact quotes come free
  from Databento metadata.get_cost with a free API key. Jason sets the
  ceiling from those, if and when.
- Baseline problem: long-only directional claims have been tested against
  zero, not against the unconditional drift (+0.18-0.20 ATR / 3 days in
  Discovery). H118 is the one candidate in that shape; the all-days-baseline
  diagnostic has never been run and would not touch its frozen spec.
  research/mechanisms/cross-asset-correlation-convergence-m12.md Section 10.
- Cross-asset (M12): drawn and closed 1:52 am CT, refuted with no gradient
  at n=553/tercile. Attempt 1 of 2; no different forced-flow proxy exists
  at the current data ceiling.

HOLD -- NOT REQUESTING A SLOT (Jason's call, September 11th, ~10:xx pm CT):
hyp-000142/144 VXN elevated vs its own norm -> next-session RTH range (map M7,
Idea Inventory Entry 8) is deliberately NOT going to Holdout yet. Jason's
decision: wait until there's a cleaner story before spending a slot on this
one -- the shrinking effect (1.31 Discovery -> 1.12 Validation), the ~half
overlap with the existing overnight-coil conditioning fact, and it being a
range-only (not directional) signal made this not worth a slot right now.
Full v2.5 chain up through Validation + frozen Holdout spec + resolved blind
gate stays on record and does not need to be redone: mechanism doc
pre-registered -> Scan 014 (HIGH 1.305, LOW 0.796) -> Statistical PASS +
Sidak + power -> Director CONTINUE -> blind Gate CONDITIONAL (resolved) ->
ONE-SHOT VALIDATION PASS (HIGH 1.120 [1.066,1.177], Sidak-adjusted
[1.026,1.213]) -> Monetization (conditioning input, zero cost) -> frozen
Holdout spec -> blind Gate CONDITIONAL (resolved in writing). Spec on file:
research/studies/vxn-high-next-day-range-h142-holdout-spec-frozen-2026-09-12.md
-- stays frozen, untouched, no script written. 3 of 5 Holdout Gen 2 slots
remain (none spent on this). Re-open only if Jason asks, or if a future
cycle finds something that meaningfully cleans up the story (e.g. cuts the
overlap with the overnight-coil fact, or firms up the effect size).


HOLDOUT SLOT 2 SPENT September 11th, 7:29 pm CT (Jason's sign-off): hyp-000105/106
midday-lull range persistence HOLDOUT PASSED (hyp-000141, n=130, ratio 0.739,
CI [0.686, 0.796]). 3 of 5 Holdout Gen 2 slots remain. Nothing on Jason for it.

RESOLVED September 12th (Jason, interactive): item (2) below closed --
the $60-115/mo execution-stack approval of 2026-09-10 is RECONFIRMED as a
standing pre-clearance. It is NOT a one-time yes needing to be re-asked;
spend it the moment a candidate actually reaches execution-qualification
(Tradovate connection + signal-relay service), no further sign-off needed
at that trigger. Separate from the $20/mo data cap (data funds research,
this funds order execution) -- does not draw from or count against it.
Still explicitly NOT to be built/spent before something has passed and is
ready for that stage -- do not build early "just in case."

STILL PARKED (48-hour clock per UPGRADE 9): (1) open a Tradovate paper
account (Jason's action; recommendation in AMENDMENT v3.2) -- no automated
action needed here, Jason's own step whenever he's ready.

Holdout Gen2 slot (1/5 used). A 2nd slot for the midday-lull narrow-midday
characterization (hyp-000106) would be a natural confirmatory step given
exp-127's costed-overlay attempt closed null on structural (not
statistical) grounds -- flagged, not requested; opening a Holdout slot is
never automated, win or lose. Also blocked, unchanged: spend >= $5,
live-capital authorization, manual data refresh, the concurrency problem.

(SCOPE BOUNDARY reading for 1b: RESOLVED 2026-09-11, no longer blocked --
see note near the top of this file.)

## AGENT PROTOCOL — binding from 2026-09-10 (PERMANENT, never prune)

Full text: research/infrastructure/agent-governance-structure.md,
AMENDMENT v2.1. This section is the operating summary. Every session
follows it.

### A. Run the agent whose input exists

You do not skip an agent because the session is short. You skip it only
because its input condition was not met, and you say so in the report.

  LEARN .................. before freezing any scope, before re-testing
                           anything. By name. Resurrection + known
                           failure-mode check.
  Director (entry) ....... before scoping. Sets direction, owns freeze.
  Discovery .............. a frozen scope exists.
  Candidate Triage ....... a scan cleared >=1 cell. Grade A-F. D/F closes
                           with no hypothesis ID spent.
  Mechanism .............. candidate graded C+. Writes research/mechanisms/
                           <name>.md. NO DOC, NO ADVANCE.
  Statistical ............ candidate has a mechanism doc. 4 questions +
                           same-data selection disclosure.
  Director Re-Eval ....... candidate survived Statistical. Second look:
                           is it worth spending the rest of the pipeline?
  Monetization ........... Director said CONTINUE at Re-Eval. "No credible
                           path" is a valid success.
  Integrity Gate ......... before Discovery->Validation or Validation->
                           Holdout. VETO, not advice.
  Integrity Gate (audit) . ALWAYS at session close. See B.
  Portfolio .............. full promotion bar cleared. Dormant now.

Every agent report: Finding / Confidence / Novelty / Research Value /
Recommendation (CONTINUE / MODIFY / PIVOT / ABANDON).

### B. Close every session with the Integrity Gate audit

Before releasing the lock, audit each candidate that moved this session
against section A. A skipped stage produces a RETURN:

  - route the candidate back to the missing stage
  - put it at the TOP of the queue, ahead of new work
  - record it in the session report

A RETURN corrects course. It does not block, kill, reject, or spend or
free a hypothesis ID.

EXCEPTION: promoted candidates (H118, EXP047) are outside automated
scope. The audit may FLAG a gap on them. It may not route, re-run or
modify them. Flag and stop.

### C. Call a staff meeting when you need one

Any agent may REQUEST one. Only the Research Director convenes. MUST be
convened, within the next step, when:

  a. a candidate gets a SECOND RETURN
  b. two agents return CONFLICTING recommendations on one candidate
  c. a scan closes with ZERO survivors, or every 3rd closed scan
  d. any agent asks, with a stated reason

Output: ONE disposition (CONTINUE / MODIFY / PIVOT / ABANDON) plus the
specific change. Record every agent's position, not just the outcome.

### D. Write the session report

research/sessions/YYYY-MM-DD-HHMM.md, before releasing the lock, even on
a short or interrupted run. Sections: Agents (RAN with 5-field report, or
NOT RUN with the unmet condition) / Returns / Staff meeting / Moved /
Queued next.

## MECHANISM GATE — binding from 2026-09-10 (PERMANENT, never prune)

No candidate advances from Statistical to Monetization without a mechanism
document in research/mechanisms/. A candidate with no mechanism is returned
to Mechanism or closed — never promoted. The Integrity Gate checks for the
file and its quality as part of its standing brief.

A mechanism doc must carry: the causal claim in market terms; WHO IS ON THE
OTHER SIDE and why (naming "unknown" is allowed and is a red flag, not a
footnote); at least two testable predictions that are NOT restatements of the
effect; what would falsify it; whether it was written pre-registered or
post-hoc; and the status of each prediction. See research/mechanisms/README.md
and TEMPLATE.md. A post-hoc mechanism is a HYPOTHESIS, not evidence. It earns
weight only by correctly predicting something it was not built to explain.

STATUS 2026-09-10: every candidate above Discovery has a mechanism doc.
All queued predictions across the 3 volatility-conditioning docs are
TESTED -- see research/studies/statistical-stage-pass-2026-09-10.md. Still
queued, unchanged: H118 prediction P3 (is the effect stronger after FAST
declines into the LOW state, versus slow grinds down?) -- untested,
requires classifying the approach by speed and volume. A mechanism test,
not a strategy change; does not touch H118's frozen definition.

## vwap_dist LOW, 1-DAY VARIANT — CLOSED 2026-09-10 (automated session)

REJECTED at Validation (single pre-registered shot: n=218, mean R=0.047,
CI_90 [-0.033,0.127], not credible, not economically meaningful), after
a clean Discovery-slice pass (n=558, R=0.110, CI [0.053,0.165]).
vwap_dist_vs_atr/LOW's 2-attempt limit now EXHAUSTED (H118=attempt 1,
promoted; this=attempt 2, closed null) -- no further horizon cuts on
this state variable without a new staff-meeting-level justification.
Also found and corrected: the "Scan 002 Discovery numbers" table
elsewhere in this project's history (pts/R per horizon) uses a
screening-stage approximation (baseline-subtracted, avg-ATR-normalized)
that is NOT the same statistic as a frozen candidate script's own
canonical per-trade-ATR R -- flagged so future sessions don't expect a
frozen-script confirmation run to reproduce that table's numbers
exactly. Full: research/studies/vwap-dist-low-1d-variant-closure-2026-09-10.md,
research/mechanisms/vwap-dist-low-1d-variant.md. Ledger: hyp-000136
(Discovery, corrected to REJECTED via update_status) -> hyp-000137
(Validation, REJECTED).

## Done this run (2026-09-11, automated -- Idea Inventory DRAW, Entry 2)

Queue item 0 (Idea Inventory) was CLEARED at 3 live entries when this
session started; per the DRAW rule, drew Entry 2 (days_to_monthly_opex,
pre/post-expiry volatility compression, oldest vetted) and ran its
single pre-registered Discovery-stage test as Scan 007
(src/market_behavior_discovery_scan_007.py): day-before/after-opex RTH
range vs trailing-20d average, non-witching months primary, 4
quarterly-witching months reported separately per LEARN's data-
integrity flag. RESULT: clean null on both primary predictions --
before_opex_non_witching n=54 ratio=1.038 CI_90[0.938,1.149] (predicted
<1, not confirmed); after_opex_non_witching n=53 ratio=0.922
CI_90[0.789,1.070] (predicted >1, not confirmed, point estimate even
opposite-signed, not credibly so). Witching cells (n=27 each) also
null. CLOSES Entry 2 per its own pre-registered terms -- 2-attempt
limit on days_to_monthly_opex now exhausted (Scan 004 return-direction
= attempt 1, this range-compression test = attempt 2). Ledger:
hyp-000138 (Discovery, REJECTED). SCAN_REGISTRY +1 (scan_007, 4 cells,
0 promoted). Mandatory zero-survivor staff meeting held, disposition
PIVOT (idea-shelf cadence only). Shelf back to 2 live entries (Entry 3,
Entry 4), TOP-UP owed again as queue item 0 above. H118/EXP047
untouched, no spend, no Holdout slot used. Execution Clock item 1b left
untouched (disputed scope reading, 5th session to decline it, same
reasoning as prior sessions). Test suite 228/228 green. ops_checks:
WARN x2, both pre-existing (EXP047 mechanism-gate, an earlier report's
missing new-information line), no new issue introduced. Console pushed
live cleanly (write_db, version 25->26). Full:
research/sessions/2026-09-11-0240.md.

## Done this run (2026-09-11, automated -- Statistical stage, hyp-000139 CLOSED)

Queue item 0 (STATISTICAL stage on hyp-000139) run to completion:
src/statistical_stage_hyp139.py, research/studies/hyp139-statistical-
stage-2026-09-11.md. 4 questions + same-data selection disclosure + the
mechanism doc's own P1-P3, on the Discovery-slice sample (matches Scan
008's baseline exactly, n=364 HIGH tercile). Q3 (project-wide
multiplicity correction, this project's binding constraint since
2026-09-10) FAILS: Sidak-adjusted 90pct CI [-0.2119, 0.0626] crosses
zero at N_discovery=275, despite the raw CI [-0.1371,-0.0099] not
crossing it. Q1 (stability) also fails independently (only 1 of 2
chronological halves credible). Q2 (regime) not concentrated in one
regime but neither half independently credible either -- a further
power flag. Q4 shows a real, modest selection-sensitivity flag (top-25pct
loses credibility; top-20pct and the frozen top-33.33pct do not).
Mechanism predictions mixed: P2 (10d/30d window generalization)
CONFIRMED cleanly; P1 (overnight- vs RTH-driven split) same sign,
underpowered, neither subgroup independently credible; P3
(volume-conditioning) NOT confirmed and ran OPPOSITE the doc's own
volume-independence prediction (reversion concentrated in HIGH-volume
days, absent in LOW-volume days) -- also contradicts the entry's
original P1/persistence story (wrong sign). CLOSED, REJECTED per this
project's established Q3 binding-constraint convention (same check
closed range-contraction and overnight-coil 2026-09-10). Ledger:
hyp-000139 (PROMISING -> REJECTED via update_status). Mechanism doc
Sections 5-6 updated with final prediction status/verdict. idea_
inventory.md Entry 3 marked CLOSED, STATUS/cadence note updated -- live
count now 2, TOP-UP owed as new queue item 0. H118/EXP047/Execution
Clock untouched, no spend, no Holdout slot used, no 1a/1c work started.
Test suite 236/236 green (unchanged, no new test file needed). ops_checks:
WARN x2, both pre-existing (EXP047 mechanism-gate, one earlier report's
missing new-information line), no new issue introduced. Console pushed
live cleanly (write_db). Full: research/sessions/2026-09-11-0751.md.

## Done this run (2026-09-11, automated -- Idea Inventory TOP-UP, Entry 6)

Queue item 0 (Idea Inventory TOP-UP) run to completion: generation staff
meeting (LEARN -> Discovery -> Integrity Gate -> Statistical -> Mechanism
-> Director) added Entry 6 (volume_vs_expected LOW tercile, next-day RTH
range vs trailing-20d average -- second and final attempt on this state
variable, ruled NOT cosmetic vs Scan 002's closed 10-day return-direction
test: different variable role, outcome statistic, and horizon), restoring
the 3-entry floor (Entry 4, Entry 5, Entry 6). No draw made this session
-- floor restored is the queue item's full scope. No hypothesis ID spent,
no scan run, no SCAN_REGISTRY change needed. H118/EXP047/Execution Clock
untouched, no spend, no Holdout slot used, no 1a/1c work started (both
remain Jason's calls). Test suite 236/236 green (unchanged, no new test
file needed). ops_checks: WARN x2 at session start (console -- 253 min
stale, cleared by this session's regenerate+push; mechanism-gate --
pre-existing, EXP047), no new issue introduced, no FAIL. FYI: the
~08:07 UTC cycle was skipped by a brief device-link outage; confirmed
recovered on its own before this session started. Console pushed live
cleanly (write_db). Full: research/sessions/2026-09-11-1213.md.

## Done this run (2026-09-11, automated -- Idea Inventory DRAW, Entry 4)

Queue item 0 (Idea Inventory) was CLEARED at 3 live entries when this
session started; per the DRAW rule (Entry 4's own Cadence note), drew
Entry 4 (day_of_week==Friday, same-day RTH range vs trailing-20d
average, oldest vetted) and ran its single pre-registered Discovery-
stage cell as Scan 009 (src/market_behavior_discovery_scan_009.py).
RESULT: clean null -- n=307, mean_ratio=1.0319, ci_90=[0.9736,1.0929],
neither P1 (compression) nor P2 (elevation) confirmed. No hypothesis ID
spent (same convention as Entry 1/Scan 006's null closure). The entry's
own non-gating P3 volume-conditioning check split sharply (low-volume
Fridays compressed and credible, high-volume Fridays elevated and
credible, opposite-signed, consistent with the pooled null) -- reported
per the entry's own pre-registered scoping, explicitly NOT promoted to
a new hypothesis or entry this run (would be results-informed post-hoc
generation). CLOSES Entry 4 per its own terms. SCAN_REGISTRY +1
(scan_009, 1 cell, 0 promoted), registered before the scan ran. Shelf
back to 2 live entries (Entry 5, Entry 6), TOP-UP owed again as queue
item 0 above. Mandatory zero-survivor staff meeting held, disposition
PIVOT (idea-shelf cadence only; the entry's own contingent Monday
second cell is now moot, not run). H118/EXP047 untouched, no spend, no
Holdout slot used. Execution Clock 1a/1c left untouched (Jason's open
items); 1b stays DONE. Item 0a (event-conditioned draft) untouched,
still held per Jason's instruction. Test suite 236/236 green. ops_checks:
WARN x1 at close, pre-existing (EXP047 mechanism-gate), no new issue
introduced. Console pushed live cleanly (write_db). Full:
research/sessions/2026-09-11-1422.md.

## Last updated by
September 14th, ~6:15-7:00 pm CT -- INTERACTIVE (Jason ran the approved data pull from his own Terminal). **DATA REFRESH DONE. COST $0.0185** (quoted and logged; the $5-15 estimate was an order of magnitude high -- a 5-day top-up is nearly free). 5,055 bars added, NQ series now runs to 2026-09-14 11:14 ET. **FIRST RUN FAILED AND THAT WAS MY BUG**: the script asked for end=NOW and GLBX.MDP3's historical end lags real time ~20 minutes, which Databento rejects outright (422 data_end_after_available_end) rather than returning what exists. Nothing was purchased on the failed run. Fixed by reading metadata.get_dataset_range and clamping, with a now-minus-30-minutes fallback; 3 regression tests. CONTINUITY CHECK PASS on the refreshed file: schema, monotone/unique, every old bar present AND bit-identical, extends, junction gap 0.0h / price step 0.008%; the one WARN is the expected pair of partial buckets (Sept 8 evening 240 bars, Sept 14 in progress 675). **STEP A REPLAY FOUND TWO REAL DEFECTS -- exactly what it exists for.** (1) 2026-09-13 is a SUNDAY: Globex reopens 18:00 ET and a Sunday-evening-only block looked like a session, producing a log row with no RTH in it at all. (2) 2026-09-14, the CURRENT day, was scored with data ending 11:14 ET -- it happened to be gate-blocked, but had it FILLED, _resolve_fill_outcome would have hit its session_end_fallback and booked a FABRICATED exit for a trade still open in the real world. FIXED before live paper began: bot_stack_paper_run.session_is_complete() refuses any session with no RTH bars or a last bar before 15:55 ET; b7_replay uses the same function so the two cannot drift; 5 new tests, 467 total. Re-ran Step A: 8/8 clean, 4 scored + 2 correctly skipped. **STEP B RAN. 3 new live sessions logged (Sept 9, 10, 11); execution record now 4 rows, STILL ZERO ORDERS AND ZERO FILLS.** Every one blocked by capital protection for swing width. **THAT IS THE NEW BLOCKER AND IT IS STRUCTURAL, NOT A BUG** -- see the new Blocked-needs-Jason item: the $50-150 band is in fixed dollars, NQ has gone ~4,500 -> ~29,500, and the share of B3 signals fitting the band is 2.4% in 2026 (median swing $376) vs 77% in 2018 (median $85). At that rate the 40-fill sample takes years. Diagnostic: research/integrity/swing-band-vs-instrument-price-2026-09-14.md. Staff recommends re-expressing the band in units that scale with the instrument, keeping the dollar figure as an absolute ceiling; NOTHING CHANGED AUTOMATICALLY. Execution block now produced every cycle that touches execution (src/execution_block.py). NEXT: 7:00 pm cycle -- hyp-000156's Director call, then queue item 0-NEW.
Previous: September 14th, 5:00-5:50 pm CT -- SCHEDULED 5:00 PM CYCLE. Preflight clean, close recorded. BOT: nothing can move (B7 data-blocked pending Jason's one-command top-up; B4b cooldown; B8 his alone) -- stated, not skipped. **PORTFOLIO hyp-000162: DO NOT PROMOTE.** The incremental-information question, answered on the Validation slice with every coefficient fit on Discovery only. T1 JOINT RESIDUAL: raw spread +0.289 (+0.193,+0.384); residual after the WHOLE existing stack (VXN level + overnight coil + prior-day range) = +0.059 ci_90 (-0.029,+0.151), NOT CREDIBLE; retained 17.7%, lower bound -14.3% vs the 50% bar. T2 FORECAST (the decisive practical test): MAE 0.3252 baseline vs 0.3256 with the candidate -- it makes the forecast very slightly WORSE, not credible either way; correlation 0.403 -> 0.409. **ADDING IT TO THE STACK BUYS NOTHING MEASURABLE.** T3 CONTROLS (because the method changed from stratification to regression): single-fact separability REPLICATES out of sample -- vxn 68.7%, coil 74.8%, prior-day range 94.4%, own lagged self 95.6% -- so the collapse is JOINT-vs-SINGLE, not linear-vs-stratified; the joint stratified version is 52.0% with a lower bound of 14.9%, and NEITHER method's interval clears the bar. The point estimate IS method-dependent (18% vs 52%) and the verdict rests only on what both methods agree on. PLAIN READING: the candidate's whole appeal was that it is a 10:00 ET UPDATE while every stack input is known pre-open -- the test says that update carries no measurable information about the midday range beyond what was already knowable at the open. The opening half-hour mostly CONFIRMS an already-visible volatility state rather than revealing a new one. STATUS: **VALIDATED_NOT_PROMOTED**. Not added to B2's stack; **NO HOLDOUT SLOT REQUESTED** (3 of 5 Gen-2 slots remain, scarce); NOT closed as null -- it stays in the registry as a real standalone fact for any future use that needs a midday range estimate WITHOUT the pre-open stack. 'No credible portfolio path' is a valid successful outcome and the pipeline did its job: four stages said advance, and the stage whose question is 'does this add to what we already own' said no, with numbers, out of sample. **NEW QUEUE ITEM 0-NEW (method/LEARN): single-fact separability at the 50% bar is too weak and should stop being decisive** -- make the joint test standard, and re-check hyp-000105 and hyp-000142 against it (hyp-000142 already showed 53% against two facts jointly and was promoted anyway). Nothing promoted is modified by this cycle. NEXT: hyp-000156's Director call (still owed, NOT blocked on our side), then queue item 0-NEW or a shelf draw. Shelf 4/3.
Previous: September 14th, 3:00-3:45 pm CT -- SCHEDULED 3:00 PM CYCLE. Preflight clean, close recorded. BOT: nothing can move (B7 data-blocked pending Jason's one-command top-up; B4b cooldown; B8 his alone) -- stated, not skipped. **ONE-SHOT VALIDATION hyp-000162: PASS.** Spec was FROZEN, HASHED AND COMMITTED BEFORE THE RUN (commit ee53308, sha256 7a32377d74cf306f43c950f93a4a5fbaa8c64a0b3a04364961c39a14ea142462, matched at run time) -- first time this project pre-registered a Validation test as a separate earlier commit; KEEP THIS AS THE PATTERN, it makes the pre-registration verifiable from git history by someone who does not trust the write-up. V1: spread +0.3223, Sidak N=20 ci (+0.1673,+0.4856), entirely above zero. V2 (the Gate's discriminating cell, pre-registered as GATING with failure semantics written first): retained share holding t-1 opening range fixed = **99.6%, ci_90 (91.4%,107.5%), lower bound 91.4%** vs the 50% bar -- vs 87% at Discovery. THE GATE'S CENTRAL DOUBT IS ANSWERED OUT OF SAMPLE: this is a same-session fact. **EFFECT SHRANK A THIRD: +0.32 out of sample vs +0.49 at Discovery (66% retained)** -- expected and pre-stated, because the Discovery estimate was SELECTION-CONFIRMATORY (max of a 1045-cell sweep). Observed sits above the pre-registered MDE of 0.287 but NOT BY MUCH, so the honest statement is 'credibly positive, materially smaller than Discovery advertised'. **TWO DISCOVERY CLAIMS DID NOT REPLICATE AND ARE HEREBY CORRECTED: (1) the MID-stratum POINTS sign-flip flagged in this morning's Monetization was NOISE -- all three prior-day-range strata are positive out of sample in both units (+23.8/+12.7/+15.7 pts); (2) the Director's 'the effect SCALES WITH volatility' does NOT hold -- the largest spread out of sample is in the LOW stratum. The instruction to Monetization to treat magnitude as conditional on that basis is WITHDRAWN.** D1: the Gate's edge defect was real but cheap -- full-sample edges +0.313 vs trailing real-time edges +0.322, so fixing it cost nothing and made the rule implementable at 10:00 ET. D3: 571 of 700 sessions scored, 177 HIGH/201 LOW, no single year carries it. STATUS: **VALIDATED**. STILL FORBIDDEN: attaching to B2 live sizing -- Gate condition 7's cost clause is OPEN and research cannot close it (no measured slippage exists project-wide; the order path has ZERO FILLS EVER). OWED NEXT: **Portfolio's incremental-information question** before any Holdout slot is requested (3 of 5 Gen-2 slots remain). PERMANENT DISCLOSURES travel with every future statement of this result: P1 at Discovery was selection-confirmatory; the discriminating test was post-hoc at Discovery (V2 is its pre-registered out-of-sample form, and it passed). METHOD PRIOR WORTH KEEPING: expect ~a third of a selection-confirmatory Discovery effect to evaporate out of sample, and size Validation power for the SHRUNK number. hyp-000156's Director call is still owed and NOT blocked on our side. Shelf 4/3.
Previous: September 14th, 1:00-1:55 pm CT -- SCHEDULED 1:00 PM CYCLE. Preflight clean, close recorded. BOT: nothing can move (B7 data-blocked -- the approved top-up needs Jason's terminal; B4b IBKR cooldown; B8 Jason's alone) -- stated, not skipped. MONETIZATION hyp-000162: **CREDIBLE PATH EXISTS** -- sizing input only (a range forecast has no sign), as a THIRD conditioning window (pre-open -> 10:00 midday -> 14:00 afternoon). Expected-midday-range multiplier x0.76 LOW / x1.26 HIGH = 14.3pt of expected range = ~7.2pt of B2 stop distance. Screening rule cleared (cost 2.8-3.7% of stop) BUT the honest number is the INCREMENT: 0.75pt cost is 10.5% of the change this fact makes. Survives the existing pre-open multiplier at 70-115% -- combine by residual. NEW CAVEAT THIS STAGE FOUND: the RATIO effect is regime-stable (+0.49/+0.29/+0.46) but the POINTS effect FLIPS SIGN in the MID prior-day-range stratum (-3.5pts) -- the multiplier applies to each session's own trailing average so the ratio is the decision unit, but 'scales with volatility' must NOT be read as 'more points in every regime'. BLIND INTEGRITY GATE hyp-000162: **CONDITIONAL, 7 conditions**, ruled by a subagent on a masked packet, ruling recorded VERBATIM before unmasking (research/studies/hyp162-blind-gate-2026-09-14.md). **THE GATE FOUND TWO REAL DEFECTS NO PRIOR STAGE RAISED**: (1) the CI of record resampled blocks of consecutive WITHIN-ARM observations -- ten consecutive HIGH sessions can span months, so the block never contained the calendar clustering the placebo red is about; (2) the tercile edges were FULL-DISCOVERY percentiles, not knowable at 10:00 ET, fine for a descriptive scan and not fine for a claimed real-time sizing input. It also called the packet's own framing of the placebo backwards, correctly: LOW overlap between placebo and real selection makes a reproduced effect MORE damning, not less. 6 OF 7 CONDITIONS DISCHARGED THIS CYCLE (src/gate_conditions_hyp162.py): discriminating cell WITH AN INTERVAL, holding t-1 opening range fixed = 87.4% retained ci_90 (82.0%,92.6%), bar cleared by the INTERVAL not a point estimate; calendar-time block bootstrap raw +0.5196 (+0.4489,+0.5923) vs the scan's +0.5193 (+0.4475,+0.5975) -- materially identical, the CI was NOT an artifact; atr14 leakage DOES NOT EXIST (rolling(14).mean().shift(1), current session excluded); multiplicity K=1045 sweep look-cells disclosed, Sidak at K=1045 -> (+0.366,+0.689) still above zero; MDE at 80% power vs the 50% bar = 0.58 (observed 87%, not a coin flip); trailing-250-session shifted edges raw +0.487 (+0.411,+0.566), retention 88.4% (82.7%,93.7%). **THE 7TH CONDITION'S COST CLAUSE IS OPEN AND RESEARCH CANNOT CLOSE IT** -- no measured slippage figure exists project-wide because the order path has ZERO FILLS EVER, which is the same blocker the approved data refresh addresses. DISPOSITION: CONDITIONAL SATISFIED EXCEPT THE MEASURED-COST CLAUSE. hyp-000162 may proceed to a FROZEN ONE-SHOT VALIDATION SPEC written against the TRAILING-EDGE definition, carrying two PERMANENT DISCLOSURES (P1 is selection-confirmatory; the discriminating test was post-hoc). It may NOT attach to B2 live sizing until a measured cost figure exists. METHOD NOTE FOR THE WHOLE PROJECT: retention bars have been point estimates against a 50% line (H116 98%, hyp-000140 32%); the paired-resample form built this cycle should become the standard. NEXT: the frozen Validation spec for hyp-000162 (trailing-edge definition); hyp-000156's Director call is also owed and NOT blocked on our side. Shelf 4/3.
Previous: September 14th, ~12:35-1:00 pm CT -- INTERACTIVE (Jason: "Let's run this, I don't have access to my terminal so do as much as you can on your own" -- the data-refresh queue item). PURCHASE APPROVED by Jason: NQ 1-min Sept 8th -> current, then kept current, est. $5-15 against the untouched $20/mo cap. THE PULL ITSELF CANNOT RUN FROM HERE: verified the device shell gets HTTP 403 from its egress proxy for hist.databento.com; .databento_key stays on Jason's machine, never printed or moved. EVERYTHING ELSE BUILT so it is one command for him: src/data_topup_databento.py (incremental top-up: start = last bar + 1 min UTC, quotes via metadata.get_cost, REFUSES above --cap $15, writes a NEW file, old bars authoritative on overlap, logs the REAL cost, runs the continuity check); src/data_continuity_check.py (7 checks: schema, monotone/unique, every old bar present AND bit-identical, extends, junction gap/price step, thin-session WARN); src/b7_replay.py (STEP A harness: real run_session over every session since the anchor into research/forward_validation/b7_replay/ -- own log + journal, two clocks kept apart, rebuilt from scratch each run; 8 mechanical checks R1-R8 + the 14 execution_measurement checks labelled REPLAY); src/execution_block.py (the S3 Execution block for cycle reports). 15 new tests, 461/461 total. Replay run against the one session on disk: 8/8 PASS, 0 orders (Sept 8th correctly B6-blocked) -- the machinery is proven end-to-end but has not yet seen an order on real data; the tests exercise the fill path with a $80-swing synthetic day. docs/BOT_ROADMAP.md B7 row and the Blocked section brought current. Nothing purchased, cost log unchanged. Also committed the direction-problem consult prompt (was untracked). 1:00 pm scheduled cycle is next.
Previous: September 14th, 11:00-11:35 am CT -- SCHEDULED 11:00 AM CYCLE. Preflight clean, close recorded. BOT: nothing can move (B7 data-blocked, prices end 2026-09-08 and NO PURCHASE stands; B4b on the IBKR cooldown; B8 Jason's alone) -- stated, not skipped; fell through to research. DIRECTOR RE-EVALUATION hyp-000162: **ADVANCE**. The question is IS IT NEW, not is it real. Raw spread reproduced from Scan 036 (+0.5193), then residualised against every validated volatility fact the project holds PLUS the U6 placebo's own suspect: vxn_level_vs_trailing (hyp-000142) 79.8% retained; overnight_range_vs_atr (the coil, hyp-056/057) 75.3%; range_vs_atr prior day (F-048) 83.6% -- reproduces scan_036's P3 exactly, method control; and opening_range_vs_atr AT T-1 (the placebo's suspect) **87.2%**. Worst 75.3% vs a 50% bar. **THE PLACEBO RED IS EXPLAINED, NOT DISMISSED** -- both are true at once: yesterday's opening range IS informative about today's midday (volatility persists; that was the placebo finding and it is real), AND today's carries information BEYOND yesterday's (87.2% survives holding yesterday fixed). The placebo detected PERSISTENCE IN THE VARIABLE, not REDUNDANCY IN THE CANDIDATE. Method note worth keeping: a high placebo score is a reason to run the residualised test, not a verdict on its own -- the suite should keep flagging it (the flag did its job by forcing this analysis) but the disposition belongs to the stage that can hold the suspect fixed. CARRIED TO MONETIZATION: in ALL FOUR strata the effect is LARGEST in the HIGH tercile (0.64 / 0.51 / 0.58 / 0.54 vs mid-stratum ~0.29-0.35) -- it SCALES WITH volatility rather than merely surviving it, so magnitude is conditional, not constant. LIMITATION STATED: retained share is a point estimate with no CI (same as the H116 / hyp-000140 precedents); the disposition rests on four tests landing in the same place with every per-stratum spread keeping its sign. SIZING-QUEUE PAUSE LIFTED (see disposition item 1 above) -- B2's inputs are four things, not one. A REVIEW ITEM JASON UPLOADED WAS REVIEWED AND NOT ACTED ON per his explicit instruction; 3 of its 5 claims were checked against code and are factually wrong about current state (Sidak is already stage-specific 467/20/3 not 467 throughout; the three 'unset' cost thresholds are all set with numbers in capital_protection; flow hypotheses HAVE run -- month-end and opex families, closed). Two items are strong and new. NO CHANGES MADE. NEXT: Monetization for hyp-000162, then the blind Gate -- hand it the NARROWED question (the effect scales with volatility; is the mechanism doc's story still right for an effect that behaves that way?), not a general 'is this real'. hyp-000156's Director call is also owed and is NOT blocked on our side. Shelf 4/3, draw authorised. B7 data-blocked.
Previous: September 14th, 9:00-9:55 am CT -- SCHEDULED 9:00 AM CYCLE. First cycle of the pre-booked unattended day, and the first to open with cycle_preflight.py and close with cycle_close.py. PREFLIGHT CLEAN -- and the first time the H118/EXP047 daily checkers ran inside the opening sequence rather than being remembered. ORDERING PRINCIPLE: no bot milestone can move, stated not skipped -- B7 is DATA-blocked (bot_stack_paper_run ran, nothing new; price data still ends 2026-09-08 and new data is a purchase, Jason's standing NO PURCHASE decision stands), B4b is on the IBKR cooldown (~Oct 13th, not re-raised), B8 is Jason's alone. Fell through to research as prescribed. STATISTICAL STAGE hyp-000162 (M30): **PASS**, construction reproduced from Scan 036 exactly. Full sample n=555/556 diff +0.5193 ci_90 (+0.4475,+0.5975). Q1 halves both credible same sign (+0.4676 / +0.5794). Q2 regime both credible same sign (low-vol +0.4560 / high-vol +0.6082). Q3 Sidak N_discovery=467 BINDING -> adjusted (+0.3511,+0.6875), SURVIVES. Q4 four midday-window variants all credible within +/-0.04 of the frozen one. POWER at one-shot Validation: 700 sessions ~233/arm, 1.000 at the Discovery effect, 0.815 at HALF of it -- a Validation null would be informative, not ambiguous. Write-up: research/studies/hyp162-statistical-stage-2026-09-14.md. THE U6 PLACEBO RED IS CARRIED FORWARD UNCHANGED -- separating 'wide opening range' from 'wide multi-day volatility regime' needs a NEW conditioning variable (prior-day OPENING range, never in the registered scope) and therefore a NEW trial; that is the Director's call, not this stage's to absorb. Q2 is the closest this stage legitimately gets and it CUTS BOTH WAYS: credible in both regimes (not just turbulence) but larger in the high-vol half. SOURCING (owed, shelf was at the floor, skipped for several cycles): Entry 36 / M32, OBSERVATORY channel -- `location_in_range`, where the open sits inside the prior day's range, known at 09:30, HALF AN HOUR EARLIER than M30's state and the earliest intraday sizing input B2 could act on. Never the conditioning variable of a registered scan. Queue footprint is MONOTONE across every window so the direction is pre-registered, not fitted. Mechanism: volatility asymmetry (dealer hedging of short downside convexity + vol-control funds cutting mandated exposure, both concentrating into the close -- hence a LAST-HOUR gating window). TWO GATING CONTROLS: P3 residualizes on the overnight gap (if it is all gap, it is a duplicate of a known effect) and **P4 requires the shifted-signal placebo to FAIL to reproduce it -- written in directly because hyp-000162 passed every registered prediction this morning and then tripped exactly that check.** Shelf 3/3 -> 4/3. NEXT / BINDING CONSTRAINT: the DIRECTOR CAPITAL CALL at the Validation gate, now owed on TWO candidates -- hyp-000162 (Statistical PASS, one integrity red, well-powered Validation available) and hyp-000156 (Statistical PASS x4, Validation blocked on the 6E data pull parked on Jason). Nothing advances past it. Then the blind Gate for hyp-000162, handed the SPECIFIC question (distinct fact vs marker of a multi-day volatility regime), not a general 'is this real'.
Previous: September 14th, ~7:45-8:05 am CT -- 7:00 AM CYCLE RUN AS CATCH-UP. SHELF DRAW, AND A SURVIVOR. Drew Entry 34 (M30) over the older Entry 32 under SHELF RULE v2's ranking rule (information gain x edge potential, NOT age -- ops_checks' 'oldest drawable' line is a default, not the rule): Stack A established B2 is a SIZING/permission layer, and M30 is the only drawable entry producing sizing material, known at 10:00 ET -- an intraday update between B2's pre-open number and its 14:00 afternoon update, landing in the B3 placeholder's own breakout window. scan_036 REGISTERED BEFORE THE RUN (36 scans, 362 cells cumulative). SCAN 036 -> hyp-000162, PROMISING. ALL THREE registered predictions PASSED, one shot, frozen 6-cell scope, block=10 N_BOOT=3000 SEED=20260913, Discovery only, n=555 HIGH / 556 LOW: P1 GATING midday range-ratio HIGH-LOW +0.5193 ci_90 (+0.4475,+0.5975) PASS; P2 MFE +0.0886 ATR ci_90 (+0.0741,+0.1047) and MAE +0.1108 ATR ci_90 (+0.0908,+0.1307), both credibly positive; P3 residualized on the prior-day range tercile (F-048) 83.6% retained vs a 50% bar, PASS -- NOT prior-day range restated. First Discovery survivor since hyp-000151, and the first ever sourced from the Idea Factory queue. *** BLOCKING FINDING FOR THE BLIND GATE, from U6's suite (built ONE CYCLE AGO, applied here per the standing change made at 7:45 am): 4 green, 1 RED, 2 not run. The RED is PLACEBO -- the shifted (t+1) signal reaches 0.2040 vs the real 0.2741, i.e. 74% of the effect. YESTERDAY'S opening range predicts today's midday range nearly as well as today's does, so specificity to the same session is in question: this may be a multi-day volatility-REGIME effect rather than an opening-range effect. THREE THINGS THE GATE MUST BE TOLD: (1) P3 does NOT cover this -- it residualized on prior-day RANGE, a DIFFERENT variable from prior-day OPENING range, never in the registered scope; (2) it is a near-boundary verdict -- the shifted leg's overlap with the real selection is 48.56%, just under the 50% guard above which that leg stops gating, so ~1.5 points of overlap separate this red from never being raised; (3) nothing was retuned in response -- a red is a blocking finding, not an automatic close and not an invitation to move a threshold. The inverted placebo behaves correctly (-0.1369). Report: research/integrity/mechanical-scan036-2026-09-14.json *** OPS: the busy-work guardrail that FAILED at the 5:00 am close (3 cycles moved nothing) is the reason this cycle drew; it clears with this cycle's ledger row + registered scan + inventory change. Also fixed a false mechanism-gate WARN: the check keys off a `**STATE VARIABLE**:` line in the inventory entry body and Entry 34 never carried one (added: opening_range_vs_atr). Shelf 4/3 -> 3/3 DRAWABLE (Entries 32, 33, 35), at the floor, draw still authorised. 409 tests. NEXT: Statistical (+POWER) for hyp-000162, then the BLIND Gate -- hand it the specific question (distinct fact vs proxy for a multi-day volatility regime), not a general 'is this real'. Obvious follow-up the Gate may want scoped: a registered test of prior-day OPENING range as the conditioning variable, to separate the two readings. hyp-000156 still owes a Director capital call.
Previous: September 14th, ~7:25-7:45 am CT -- 5:00 AM CYCLE RUN AS CATCH-UP. U6 DONE: src/integrity_checks.py, the Integrity Gate's mechanical suite -- all seven checks (drift_null, overnight_intraday_split, cost_sensitivity @2x, roll_date_contamination, subperiod_stability, concentration, placebo), ops_checks style, green/red/NOT APPLICABLE/INSUFFICIENT, no judgment, nothing tuned. 24 tests; suite 409/409. Every check returns NOT APPLICABLE or INSUFFICIENT rather than a green when its input cannot support it, and the output says plainly that a not-run check has NOT passed. FIRST RUNS: Stack A (hyp-000161, n=1543) -> 3 green, 2 RED (subperiod_stability: first half credible, second not, signs disagree; concentration: top 5% carry 188% of a small net effect), 2 not run. hyp-000142 (n=565) -> 5 GREEN, 0 red, 2 not run. That is the right validation shape: it flags the candidate already closed as a powered null and clears the one that passed all three stages. Reports: research/integrity/mechanical-stack-a-2026-09-14.json, research/integrity/mechanical-hyp142-2026-09-14.json. THREE FALSE VERDICTS CAUGHT ON THE SUITE'S OWN FIRST RUNS, all fixed with regression tests: (1) roll_date_contamination flagged the full 8-day expiry window, a 12.7% CALENDAR BASE RATE, so it reds any candidate that trades most days -- Stack A came back RED at 9.4%, BELOW the base rate; narrowed to the actual roll days (~3.0% base rate) and the check now reports the base rate next to the share. (2) cost_sensitivity GREENED an effect that had inverted under 2x costs (CI no longer crosses zero because it moved cleanly BELOW it); now red on a sign flip too. (3) placebo REDDED hyp-000142 -- but the t+1 leg re-selects 78.8% of the real sample (P(HIGH tomorrow|HIGH today)=0.79), so for a PERSISTENT state it reproduces the effect by construction; the shifted leg is now reported but does not gate above 50% overlap (measured per candidate, never assumed), while the INVERTED leg still gates and hyp-142 passes it cleanly (-0.086 vs +0.284). That is a structural fix for a class of candidate, NOT a threshold loosened for one -- the regression tests assert the guard does NOT fire on a non-persistent signal. PATTERN, now three for three (U28's contrast, the roll base rate, the placebo overlap): a structural check needs its OWN BASE RATE before its threshold means anything, and the base rate must be COMPUTED, not assumed. STANDING CHANGE: run integrity_checks.py on a stack's occurrence file BEFORE registering it -- this cycle is the evidence it would have had something to say about Stack A before the attempt was spent. NEXT: 7:00 am catch-up = shelf draw (prefer Entry 34/M30). U30/Stack B still a Director question; both U28 and U6 currently say 'not yet'.
Previous: September 14th, ~7:09-7:25 am CT -- 3:00 AM CYCLE RUN AS CATCH-UP (Jason, 7:07 am: run the missed 3/5/7 am cycles, and NO approval prompts). APPROVAL BUG FOUND AND FIXED: the 1:00 am cycle's console publish and trigger-prompt rewrite both raised approval dialogs on Jason's phone, which is what stalled it. Cause of the first was mine -- Artifact write_db was pointed at the STAGED upload path (/mnt/user-data/uploads/...), which is outside the session's readable folders and therefore always needs manual approval. Copy the console JSON into the session workspace and publish from there: no prompt. Console v87 -> v88 first try. Cause of the second: update_trigger asks whenever the `prompt` field changes; schedule-only (run_once_at) changes do not. Since the trigger wakes THIS persistent session, which already has the context, the prompt is redundant -- FROM NOW ON: never rewrite the trigger prompt, only move its fire time. BOT: B7 catch-up run = no-op and correct (data still through 2026-09-08, that session already logged). RESEARCH: U28 DONE -- idea_factory.py --interactions built, tested (13 tests), run. Pairwise state x state cross-tabs, Discovery only, timing rule on BOTH layers (pairing dropped if either layer is late), context = earlier-known state (tie emits both orderings). build_frame() extracted so the single-state and interaction modes cannot drift apart. METHOD BUG CAUGHT ON ITS OWN FIRST RUN: ranking by distance from the trigger-alone mean put `vxn HIGH x anything -> range` at the top at |z| up to 8.5 -- that is the already-validated volatility fact with a second state riding along, because that contrast still contains the CONTEXT's main effect. Fixed by ranking on z_vs_additive (cell vs what the two main effects predict additively); shortlist collapsed 1,495 -> 172 cells. **RESULT THAT MATTERS: K=14,740 cells looked at, and ZERO clear the multiplicity yardstick (|z| ~ 4.64 for that K); the strongest interaction on the whole Discovery slice is 4.4.** The states on disk do not visibly modify one another beyond their own separate effects. Directly relevant to U30/Stack B: the look table does NOT license a second conditional stack, and only one powered null remains before the format closes. That is a Director call. Table: research/observatory/interactions-2026-09-14.md (carry look_cells_k=14740 into any spec sourced from it). 385 tests, ops_checks 11/11 PASS, console v88. NEXT: 5:00 am catch-up = U6 integrity_checks.py; 7:00 am catch-up = shelf draw.
Previous: September 14th, 1:00-7:03 am CT -- SCHEDULED 1:00 AM CYCLE (real wall-clock time included a ~6hr device-link gap mid-cycle; actual work stayed inside budget). BOT: B7 BUILT, TESTED, RUN (src/bot_stack_paper_run.py, 14 tests) -- wires base_entry_b3 -> risk_state_engine -> order_path into one loop, one row per session logged to the new research/forward_validation/bot_stack_paper_log.jsonl (execution log, kept visibly separate from bot_stack_forward_log.jsonl's statistical log -- two clocks rule). Own execution anchor 2026-09-08 (NOT the statistical log's forward-only anchor -- B7 isn't a statistical claim, see the file's own header for the full reasoning on this and four other explicit scope choices). First real run: 1 new session (2026-09-08) -- a short signal fired, risk_state_engine permitted it, and capital_protection correctly BLOCKED it (stop $468, outside the $50-150 swing band) -- B6 proven fail-closed on real data, not just in tests. execution_measurement.py still INSUFFICIENT SAMPLE (0 order_intents) because the one real session never reached an order_intent. docs/BOT_ROADMAP.md's table brought current for B4-B7 -- caught that the 11:00 pm cycle's own close-out had claimed this update but never made it. Full test suite 372/372, ops_checks 11/11 PASS. RESEARCH: none touched -- B7 was the honest primary work (a new capital-tracking data flow wired correctly into capital_protection's gate is not small); U28/U6/shelf deliberately left for a cycle where they're the focus rather than rushed as an add-on. OPERATIONAL ISSUE: the console publish (write_db to the hosted state doc, v87) was DENIED twice this cycle (once before the device-link gap, once after, with the connection healthy) -- not retried a third time. research/_console_state.json on disk/in-commit IS correct and current; only the hosted page at the console URL is stale at v87. Needs Jason's attention. NEXT: more B7 catch-up sessions as data lands (still not this project's to control); the console publish; then U28 (idea_factory --interactions), U6 (integrity_checks.py), shelf draw Entry 32 (M28) or 34 (M30).
Previous: September 13th/14th, 10:37-11:00 pm CT -- SCHEDULED 11:00 PM CYCLE. BOT: B4a BUILT (order path against a simulated broker -- src/broker_interface.py (contract: Order/OrderAck/Fill/Position + BrokerInterface ABC), src/simulated_broker.py (deterministic seeded reject/partial-fill/disconnect-mid-order/late-ack, one-shot hooks + soak-mode rates), src/order_path.py (capital-protection gate first and fail-closed, order construction, journal-intent-before-submit, ack/fill/reconciliation, recover() proving a crash cannot silently leave a position open); spec research/infrastructure/b4a-order-path-spec.md; 25 new tests, all pass). B6 kill switches now WIRED (capital_protection.pre_order_check called before every order in submit_signal -- was CODE EXISTS/not wired before today). Budget allowed more: B4a/B7-EARLY's free statistical forward log built next (src/bot_forward_log.py, 9 tests) -- TWO CLOCKS RULE kept explicit in its own docstring, this is NOT execution and is never compared with B4a's run; ran clean against real data, 0 eligible sessions yet (anchor 2026-09-14, data through 2026-09-08). Then B5 first cut (src/execution_measurement.py, 4 tests): computes the 14 frozen checks against whatever order_path journal exists, reports INSUFFICIENT SAMPLE honestly at N=0 rather than a false pass, and does not itself authorize stage 3. Full test suite 358/358, ops_checks 11/11 PASS. RESEARCH: none touched this cycle -- bot milestones outrank the queue and there was real budget-justified work on B4a/B5 the whole session (three sub-builds, each spec'd, coded, tested; see the budget-use rule). NEXT: B7 (wire base_entry_b3 + risk_state_engine + order_path into one continuous per-session paper loop, run it live); U28 (idea_factory --interactions) and U6 (integrity_checks.py) are still queued whenever a cycle has bot-milestone headroom left over; shelf draw Entry 32 (M28) or 34 (M30) when research resumes.
Previous: September 13th, 9:02-9:55 pm CT -- SCHEDULED CYCLE, CONDITIONAL STACK BUILT AND FIRST STACK RUN (Jason: "Let's push it in now"). BOT: nothing moved; B4 order path STILL BLOCKED ON JASON (broker paper account) -- fell through to research as instructed. U25 DONE (src/stack_spec.py: schema, validator, sha256 hash; STACK_REGISTRY + register_stack() + stacks_attempted() in project_wide_multiplicity.py; 8 tests). U26 DONE (mechanism TEMPLATE sections 4a/4b/9a; UNDERPOWERED closure status in the closure form; six stack checks added to the blind-packet Gate brief). U27 DONE (src/stack_scan_runner.py: layers in time order, year-chunked occurrences, PAIRED mode, difference bootstrap N_BOOT=20000 + Sidak; 5 tests). U29 DONE -- STACK A REGISTERED (scan_035, hash 4df7b408, look_cells_k=0) AND RUN: gating difference IN_CONTEXT minus OUT_CONTEXT = +0.0247R, CI90 (-0.0496,+0.0976), Sidak N=460 (-0.1401,+0.1896), n=566/977 vs floor 100 -> POWERED NULL, hyp-000161 REJECTED, closure form filed. Consequence: B2 is a sizing/permission layer, NOT an entry filter; the BASE vs BASE+B2 paper comparison keeps that as its stated prior. Format now has one result -> 2-layer ceiling lifts to 3; ONE MORE powered null closes the format (rule 10). hyp-156: ALL FIVE blind-Gate conditions RESOLVED in writing (one test = paired per-day diff, baseline named as US-RTH hourly; src/validate_hyp156.py written + hashed e679fba6 before data exists, Sidak as max(20,N), N_BOOT 20000; DST diagnostics instead of a changed window; ATR warm-up from the Discovery tail; provenance/roll assertion; strategy_origin convention in the packet; density + first-5-min variance-share diagnostics) -> THE 6E VALIDATION DATA PULL IS NOW JASON'S CALL. U24 DONE (update_status refuses post-Validation statuses without a validation-slice row; status vocabulary in the module; 5 tests). Tests 320 PASS, ops_checks 12 PASS. NEXT: U28 (idea_factory --interactions) so the next stack is sourced from a look table rather than the roadmap; U6 integrity_checks.py; shelf draw Entry 34 (M30) or 32 (M28); U30 Stack B only after a second look.
Previous: September 13th, 7:03-7:35 pm CT -- SCHEDULED 7:00 pm CYCLE, DESIGNATED FULL-PIPELINE TEST (first cycle under the bot-first ordering). BOT: B2 BUILT (src/risk_state_engine.py, frozen params in research/infrastructure/risk-state-engine-frozen-params.json, 9 tests, daily log; found + fixed: the bot layer must load data WITHOUT the research Holdout boundary or its "latest session" is April 6th); B3 SPEC FROZEN + CODED (research/infrastructure/base-entry-b3-spec.md; src/base_entry_b3.py, 6 tests, 2,717 placeholder signals / 3,638 sessions, 0 lookahead, 0 duplicates; found: both legacy ORB/IB detectors open at 08:30 in NY-stamped data = pre-market, not the open); B1 DONE for B3. NEXT MILESTONE B4 (order path) NEEDS JASON: broker paper account. RESEARCH: U2 DONE -- M23/hyp-000156 Statistical PASS on all four incl. Sidak at N=451 -> PROMISING with Validation owed (status label corrected same cycle); blind Gate (fresh subagent, masked) CONDITIONAL with 5 conditions (research/integrity/gate-hyp156-blind-2026-09-13.md) -- FIRST research item next cycle; Validation is BLOCKED ON DATA (6E on disk = Discovery slice only) -> pull request to Jason only after conditions resolved. SOURCING RULE v3: M30/Entry 34 (opening-range width -> midday range/excursion) and M31/Entry 35 (prior-day volume -> first-30 range) docs written from the queue. U3-M27 DONE: Scan 034 P1_FAIL -- Tokyo hour credibly QUIETER than baseline (hyp-000160), London burst is London-specific. U8 DONE: 12 closure forms + research/ledger/closures.jsonl. Portfolio pass on the fact registry written. Observatory: idea-factory queue regenerated. Shelf 4/3 (Entries 32, 33, 34, 35). NEXT: resolve the 5 Gate conditions on hyp-156; draw Entry 32 (M28) or Entry 34 (M30, plugs into B2); U6 integrity_checks.py build; U12 outcome battery is now idea_factory.py.
Previous: September 13th, 4:42-5:25 pm CT -- INTERACTIVE TEST CYCLE (first under UPGRADE QUEUE v3; Jason asked to run a session and test it): U3 DONE -- drew Entry 30/M26 (Scan 033, 4 cells): P1_FAIL, compressed-day net R +0.030 ci_90 (-0.109,+0.186) n=131 powered; P2 diff not credible; hyp-000159 REJECTED; CLOSED, attempt 1 of 2 for the family. U1 DONE -- Sidak diagnosis (read-only): does NOT double-count (stage-specific N: 451/20/3); the Discovery bar tightens monotonically -- policy decision framed for Jason, no bar change. U4 DONE -- sourced M29/Entry 33 (implied-minus-realized vol gap, state primitive), shelf 3/3 (31, 32, 33). U2 (M23 Statistical) NOT done -- slipped to 7:00 pm cycle (scan hit the device-shell 3-minute limit twice before year-chunking fixed it). Tests 287, ops_checks 8/8 PASS. NEXT: U2 first, then U5 (three conditional families), U6-U8 (specs/forms), U10 (data trigger already in KNOWLEDGE.md).
Previous: 
3:00 pm CT scheduled cycle (2026-09-13 20:01 UTC). Drew Entry 29/M25 (monthly options-expiration week delta-hedge unwind, NQ): Scan 032, 10 cells, calendar-week partition (80 expiration weeks vs. 269 non-expiration weeks). GATING clean fail -- expiration-week return, ATR14-normalized, net of NQ's own unconditional weekly drift, mean=+0.1872, ci_90=(-0.0291,+0.3950), wide interval spanning both signs (not a near-miss like M24, a clean non-credible result). P2 (expiration minus non-expiration) also not credible. Day-of-week cumulative cells (Tue/Wed/Thu/Fri) individually credibly positive but non-gating/descriptive, does not override the failed gate. Director CONCUR with closure. hyp-000158 REJECTED. Entry closed, shelf dropped to 2/3. Sourced Entry 32/M28 (pre-holiday effect, NQ) restoring shelf to 3/3 -- a well-replicated multi-decade, multi-market equity anomaly (Lakonishok-Smidt 1988, Ariel 1990) never before tested against NQ in this project, with an honestly-flagged weaker named-participant mechanism story than this project's usual standard. Mechanism doc written before any scan; not drawn this cycle, budget-use deferral, first in line next cycle. pytest 287/287, ops_checks PASS, console v80->v81. Full: research/sessions/2026-09-13-2001.md.

Previous: 1:00 pm CT scheduled cycle (2026-09-13 18:00 UTC). Drew Entry 28/M24 (month-end payment-cycle reversal, NQ): Scan 031, 10 cells, thin-sample family (n=80 usable calendar months, ~27/tercile, block=3). GATING near-miss -- LOW-tercile next-month return net of NQ's own unconditional drift, mean=+0.0112, ci_90=(-0.0005,+0.0224), lower bound just barely negative, not credible. P2 (LOW-HIGH) also not credible. Not confounded with M6/hyp-000108 (first-3-session share 0.452, below kill threshold). Director CONCUR with closure despite the near-miss CI -- this project's own discipline treats a near-miss the same as a clean miss, no re-test authorized without new information. hyp-000157 REJECTED. Entry closed, shelf dropped to 2/3. Sourced Entry 31/M27 (Tokyo FX session open, 6E) restoring shelf to 3/3 -- direct companion to M23's own proven methodology (unconditional-hourly-baseline comparison, specificity check, kill check), applied to the non-overlapping Tokyo-open window (19:00-20:00 ET) with its own participant story (Japanese exporter/importer flow, Asian real-money accounts). Mechanism doc written before any scan; not drawn this cycle, budget-use deferral, first in line next cycle. pytest 287/287, ops_checks PASS, console v79->v80. Full: research/sessions/2026-09-13-1800.md.

Previous: 11:00 am CT scheduled cycle (2026-09-13 16:01 UTC), continuing directly from an interactive conversation with Jason about the project's research perspective ahead of the September 19th checkpoint. Drew Entry 27/M23 (London-open volatility burst, 6E): Scan 030, GATING P1_PASS cleanly -- London-open hour |return|/ATR14 credibly exceeds the unconditional hourly baseline (diff +0.0400, ci_90=[+0.0279,+0.0550], n=891 days, largest-n open-scope entry so far); pre-London hour secondary check does NOT show the same elevation (specificity confirmed); not a first-minute print artifact. First clean unambiguous pass in the M20/M21/M23 scheduled/structural-volatility family. Director CONTINUE. Monetization: 6E has no base strategy to size, but per the mechanism doc's own guidance (this fires daily, unlike M20/M21's rare events) a standalone opening-range breakout/fade strategy is a credible path -- deferred to a fresh sourced entry rather than designed mid-cycle. hyp-000156 PROMISING, filed KNOWN TRUE. Sourced Entry 30/M26 (Level Sweep Reversal, close_min_distance variant, conditioned on the project's own already-validated prior_day_narrow range-contraction state fact rather than retested unconditionally) restoring shelf to 3/3 -- origin: this cycle's interactive conversation, the first concrete test of whether a pattern that failed on average can still work under specific conditions. Not drawn this cycle, budget-use deferral, first in line next cycle. pytest 287/287, ops_checks PASS, console v78->v79. Full: research/sessions/2026-09-13-1601.md.

Previous: 9:00 am CT scheduled cycle (2026-09-13 14:00 UTC). Data ceiling resolved: Jason independently ran the RTY and ES Databento fetch scripts himself (per standing guidance that these fetches must run outside the sandboxed/bridged shells); both files found already on disk this cycle. Fixed a real cost-log bug (log_cost_entry() hardcoded NQ symbol regardless of caller, mislabeling the RTY purchase) and corrected/completed the cost log (~$13.09 total, 2 entries). Un-parked Entry 17/M13 and Entry 18/M14 to DRAWABLE (shelf jumped 2/3 -> 4/3); drew and scanned both: Scan 028 (M13, LETF close-rebalance, RTY/ES/NQ common window 2017-07-09->2021-10-03 since RTY has no earlier CME history) -- P1_FAIL for all three instruments, CLOSED, hyp-000154 REJECTED. Scan 029 (M14, option-dealer gamma regime, NQ/ES, ES-derived autocorrelation proxy) -- P1_FAIL for both instruments (both wrong-signed vs prediction), CLOSED, hyp-000155 REJECTED. Sourced Entry 29/M25 (monthly options-expiration week delta-hedge unwind, NQ, literature: Stivers and Sun SSRN) restoring shelf to 3/3 floor; deliberately NOT drawn this cycle (budget-use judgment call after two full scans already run), first in line next cycle. pytest 287/287, ops_checks PASS. Full: research/sessions/2026-09-13-1400.md.

Previous: 7:00 am CT scheduled cycle (2026-09-13 12:00 UTC). Sourcing owed, shelf stayed 2/3 (Entry 27, 28). Investigated a quarterly-witching-day NQ closing-volatility/reversal candidate; ruled out before writing a mechanism doc -- re-verified a known data-integrity gap (zero usable RTH bars on witching Fridays in the continuous NQ series, confirmed against 2021-06-18 and 2021-09-17). No other candidate cleared the LEARN/resurrection and power bar this cycle. pytest 287/287, ops_checks WARN only on expected shelf-below-floor. Full: research/sessions/2026-09-13-1200.md.

Previous: 5:00 am CT scheduled cycle (2026-09-13 10:00 UTC). Sourcing owed, shelf stayed 2/3 (Entry 27, 28) -- practitioner queue fully ruled, no new claims; considered and declined the daylight-saving-time stock-return anomaly (contested replication, only ~13 events across Discovery, thinner than M19/M22's already-thin samples). No candidate cleared the LEARN/resurrection and power bar this cycle. pytest 287/287, ops_checks WARN only on expected shelf-below-floor. Full: research/sessions/2026-09-13-1000.md.

Previous: 3:00 am CT scheduled cycle (2026-09-13 08:00 UTC). Sourced Entry 28/M24 (month-end payment-cycle reversal, NQ, literature: forced institutional selling for month-end cash needs, reversing over the following month) restoring shelf to 3/3, authorizing a draw per SHELF RULE v2. Drew and scanned Entry 26/M22 (month-end ZN duration-extension flow): Scan 027 -- GATING cell n=82 mean=+0.1022 ci_90=(-0.1210,+0.2630), not credibly positive; not killed; issuance-direction split omitted (no issuance-size data on disk). CLOSED, hyp-000153 REJECTED, THIN-SAMPLE caveat (n=82, same discipline as M19). Shelf back to 2/3 (Entry 27, 28), sourcing owed again. pytest 287/287, ops_checks WARN only on expected shelf-below-floor. Full: research/sessions/2026-09-13-0800.md.

Previous: 1:00 am CT scheduled cycle (2026-09-13 06:00 UTC). Sourced Entry 27/M23 (London FX session-open volatility burst, 6E, structural session-boundary mechanism) restoring shelf to 3/3, which authorized drawing within the same cycle per SHELF RULE v2. Drew and scanned Entry 22/M18 (volume-conditioned daily reversal, NQ): Scan 026 -- P1 gating passed (HIGH-volume credibly negative) but P2 failed (not credibly below LOW-volume); CLOSED, hyp-000152 REJECTED, not killed (first-min share 0.036). Shelf back to 2/3 (Entry 26, 27), sourcing owed again. pytest 287/287, ops_checks WARN only on expected shelf-below-floor. Full: research/sessions/2026-09-13-0600.md.

Previous: September 12th, 11:00 pm CT scheduled cycle (2026-09-13 04:00 UTC). Sourcing owed, shelf stayed 2/3 -- considered the day_of_week/volume-regime follow-up flagged in Entry 4's closure notes and declined it as fishing-adjacent on an already-null variable; no other candidate cleared the LEARN/resurrection bar. Confirmed the interactive VXN Holdout pass (hyp-000151, between the 9pm and 11pm cycles) rolled cleanly into the sweep: GATED 0, FROZEN 3. pytest 287/287. Full: research/sessions/2026-09-13-0400.md.

Previous: September 12th, ~9:50 pm CT, interactive (Jason: "Push through the option through the holdout"). Spent Holdout Gen 2 slot 3 of 5 on hyp-000142/144 (VXN vs trailing average -> next-session range): HOLDOUT PASSED (hyp-000151), HIGH ratio 1.239 [1.170,1.313], Sidak-adjusted [1.154,1.324], strengthened Validation->Holdout. THIRD hypothesis in project history to clear all three stages. Portfolio review: SEPARABLE, 53-66% retained residualized -- must combine by RESIDUAL not product if integrated (deferred to Sept 19th). GATED count now 0, awaiting-jason WARN cleared. 2 of 5 Holdout Gen-2 slots remain. pytest 287/287. Full: research/sessions/2026-09-13-0203.md (addendum).

Previous: September 12th, 9:03 pm CT scheduled cycle (2026-09-13 02:03-02:xx UTC). Sourcing owed (shelf still below floor after 7:00pm cycle). Reviewed all four channels: queue v2's pre-scoped items exhausted at the data ceiling, all seeded practitioner claims already ruled no-entry. Sourced ONE new candidate, map channel: M22 month-end index duration-extension flow, ZN (open scope) -- bond index funds forced to extend duration at month-end via Treasury futures, distinct from M19 (auction concession), M5 (NQ-vs-ZN relative performance), and turn-of-month (different instrument/window). Mechanism doc written before any scan, Entry 26, DRAWABLE, no scan run. Searched for a second new candidate to reach the floor of 3; none cleared LEARN/resurrection scrutiny honestly (would have been a scheduled-event-magnitude clone or a data-blocked family) -- did not invent one. Shelf 2/3. pytest 287/287. Full: research/sessions/2026-09-13-0203.md.

Previous: September 12th, 7:00 pm CT cycle (2026-09-13 00:01-00:55 UTC). A fresh WebFetch found a usable historical source (Jarocinski-Karadi ECB shocks dataset) and unblocked Entry 25/M21. Drew it: Scan 025 Discovery PASS (decision-hour diff +0.534 ATR, largest effect in the M20/M21 family) -> Statistical PASS -> Director CONTINUE -> Monetization NO CREDIBLE PATH (no 6E strategy to size). hyp-000150 REJECTED, filed KNOWN TRUE. All three September 12th open-scope entries (M19/M20/M21) now resolved. Ruled out a queued practitioner claim (IB family). Declined to source a third scheduled-event-magnitude clone (FOMC/NFP in 6E or CL) -- reasoning documented in KNOWLEDGE.md; sharpened the loose end to building a CL/6E base strategy. Shelf 1/3 (Entry 22/M18 only). pytest 287/287. Full: research/sessions/2026-09-13-0001.md.

Previous: September 12th, ~7:10 pm CT (2026-09-12 23:23 UTC), interactive (Jason supplied the TreasuryDirect 10-year auction-date CSV after asking what was needed of him). Drew Entry 23/M19: Scan 024, both gating legs null vs ZN's unconditional 3-session drift (n=40 events), kill check clears (8.8%, not a print artifact). hyp-000149 REJECTED, entry CLOSED. Caught and fixed a kill-share denominator bug in the scan before treating the result as final. Shelf 1/3 (M19 no longer pending; still waiting on Entry 25/M21's ECB date list). pytest 287/287. Full: research/sessions/2026-09-12-2315.md.

Previous: September 12th, 5:00-5:35 pm CT (2026-09-12 22:00-22:35 UTC), scheduled 5:00 pm CT cycle (survived a mid-cycle cloud-container reset; no work lost, the connected project folder held every uncommitted change). Sourced M19/ZN (WAITING on TreasuryDirect data), M20/CL, M21/6E -- 2nd and 3rd open-scope entries. Drew and closed Entry 21/M17 (clean null, hyp-000147). Drew Entry 24/M20 through the full pipeline: first open-scope Discovery PASS, honest near-kill disclosure, Monetization NO CREDIBLE PATH (hyp-000148). Entry 25/M21 blocked honestly on a missing verified ECB press-conference date list (web-tool limit hit), filed WAITING rather than scanned on guessed dates. Shelf 1/3, sourcing owed. pytest 287/287. Next cycle: source toward the floor across all four channels, then draw Entry 22/M18. Full: research/sessions/2026-09-12-2200.md.

Previous: September 12th, 5:25 pm CT (2026-09-12 20:33 UTC), TEST cycle (Jason asked for one after the budget-use staff meeting). Observatory item 4 CLOSED at the ceiling (lead-lag v2: none, any resolution/session/shock; state classifier: variance conditions range two-sided, rate configuration conditions nothing). Sourced M17 (Entry 21) -> drew Entry 19 / M15: Scan 020 CLEAN NULL (hyp-000145; run 1 had a Monday-drop sample bug, caught, fixed to spec, run 2 of record). Sourced M18 (Entry 22) -> drew Entry 20 / M16: Scan 021 CLEAN NULL (hyp-000146). Shelf 2/3 (Entries 21, 22). Next cycle: sourcing owed (one more entry to the floor), then draw Entry 21 (M17). pytest and ops_checks at close-out. Full: research/sessions/2026-09-12-2013.md.

Previous: September 12th, 4:15 pm CT (2026-09-12 21:15 UTC), scheduled 3:00 pm CT cycle. Shelf held at 2/3 (below floor, no draw). Queue v2 item 4 Observatory: closed the last unchecked separability pairing (prior-day range regime vs. overnight coil and vs. midday-lull, both SEPARABLE) and ran the first NQ/ZN/6E/CL information-transmission characterization (no lead-lag at 15-min RTH resolution, a third lens agreeing with the M11/M12 nulls). Fixed a report-format gap from the 11am cycle (missing Agents/new-information sections). pytest 286/286. Full: research/sessions/2026-09-12-2000.md.

Previous: September 12th, 1:35 pm CT (2026-09-12 18:35 UTC), scheduled 11:00 am CT cycle (ran on device reconnect). Shelf 0/3 -> 2/3 DRAWABLE: queue item 2c filed (M15 overnight-vs-intraday split, Entry 19, map-ranked #1) and item 2e filed (M16 market intraday momentum, Entry 20, #2), mechanism docs before any scan; item 5 practitioner stream opened with three claims ruled (no entry). No draw (below floor). Daily checkers clean. Next cycle: sourcing via item 4 Observatory; draw Entry 19 when the shelf reaches 3. Full: research/sessions/2026-09-12-1600.md.

Previous: September 12th, 9:30 am CT (2026-09-12 14:28 UTC), TEST cycle with Jason watching, after the push (fb52280) and the post-push staff meeting (CONTINUE). Queue v2 item 2b filed: M14 gamma-regime entry (Entry 18), mechanism doc before any scan, waits on ES data. Daily checkers clean. Full: research/sessions/2026-09-12-1428.md.

Previous: September 12th, 9:06 am CT (2026-09-12 14:00 UTC), scheduled cycle. Queue v2 item 1 done: two-nulls amendment + baseline_relative.py; H118 baseline diagnostic FAILS (edge not distinguishable from NQ's own drift, Jason messaged, status his call). Item 2 started: sourcing template + M13 LETF close rebalance filed (Entry 17), waits on RTY/ES data. pytest 284/284. Full: research/sessions/2026-09-12-1400.md.

Previous: September 12th, 3:02 am CT (2026-09-12 08:00 UTC), routine cycle. Map empty by Jason's choice; daily checkers run, nothing new; pytest 280/280. Full: research/sessions/2026-09-12-0800.md.

Previous: September 12th, 1:00 am CT (2026-09-12 06:00 UTC), scheduled cycle. Map
refill on hold per Jason's explicit instruction (he's sourcing M9 data
himself this weekend; cross-asset M12 staged, not authorized to draw). No
Discovery Engine work done, by instruction not exhaustion. Ran both
FROZEN-tier daily checkers: H118 forward validation (no new signal, 1 open
position tracked) and EXP047 weekly monitor (3/260 weeks, no early-kill).
Nothing to act on from either. pytest 279/279, ops_checks all PASS except
the expected awaiting-jason WARN (VXN Holdout slot, not re-raised). Full:
research/sessions/2026-09-12-0600.md.

Previous: September 11th, 11:20 pm CT (2026-09-12 04:20 UTC), scheduled cycle. Jason
held the VXN Holdout slot request interactively earlier tonight (not spent).
Drew and closed all 3 shelf entries: Scan 015 (M5 month-end NQ-vs-ZN) clean
null, n=79 (found+fixed a units bug mid-scan); Scan 016 (M3b post-FOMC
continuation) clean null, n=52; Scan 017 (M4 pre-FOMC drift exact L-M
window) near-miss, not credible, 2-attempt limit exhausted, CLOSED FOR
GOOD. No hypothesis ids spent. Shelf now 0/3, QUEUE EXHAUSTED (ops_checks
value FAIL, by design, not a bug) -- every map entry closed except M9
(parked on missing rebalance-date data). IMMEDIATE item for Jason: front
end of Discovery Engine needs his input to refill (new map entry, M9 data,
or judgment call on a near-miss). pytest 279/279. Full:
research/sessions/2026-09-12-0400.md.

Previous: September 11th, 9:52 pm CT (2026-09-12 02:52 UTC), EXTRA scheduled cycle
(FULL-BUDGET RULE). 0b audit DONE (0 resurrections). Scans 011/012/013 null
(M10, M11 attempt 1; M1 closed for good). Scan 014 (M7 VXN -> next-session
range) survived -> Statistical PASS -> Director CONTINUE -> blind Gate ->
VALIDATION PASS (hyp-000142/144, HIGH 1.120 [1.066,1.177]) -> Monetization ->
frozen Holdout spec -> blind Gate -> WAITING ON JASON (Holdout slot). Shelf 3/3
(Entries 12 M5, 13 M3b, 14 M4). pytest 275, ops 8/8. Full:
research/sessions/2026-09-12-0230.md.

Previous: September 11th, 9:00 pm CT (2026-09-12 02:00 UTC), scheduled cycle. Portfolio
review of hyp-000105/106/133/141 CLOSED: separable from overnight-coil (82.5%
of spread retained), KNOWN TRUE incremental, stays in volatility_conditioning.py.
Found+fixed a pipeline_sweep.py bug (HOLDOUT PASSED branch never checked for a
completed Portfolio doc, would have kept re-flagging it as owed forever) --
1 new regression test, 2 existing tests updated. pytest 274/274, ops_checks
8/8 PASS. Next owed: item 0b (LEARN closed-family audit), then Entry 9 draw.
Full: research/sessions/2026-09-12-0200.md.

Previous: September 11th, 7:35 pm CT (2026-09-12 00:35 UTC), interactive
(Jason present). HOLDOUT SLOT 2 SPENT on hyp-000105/106: HOLDOUT PASSED
(hyp-000141). Sweep collapse fix for *_holdout rows. Full:
research/sessions/2026-09-12-0027.md.
