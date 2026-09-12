# NEXT UP — session handoff baton

The ONE file every work session reads FIRST and rewrites LAST. Sessions are
stateless; this exists so no run re-derives context from the 14k-word
docs/BACKLOG.md or the 137-row ledger. Keep it under ~400 words — prune,
don't grow. Permanent record stays in research/ledger/, research/experiments/,
docs/BACKLOG.md. Do NOT read BACKLOG.md unless choosing a genuinely new
research direction. Jason also works this project ad hoc — if "Last updated
by" says an interactive session, that work is done; continue, don't redo.

## In forward validation (paper only, no capital) — DO NOT TOUCH, see scope boundary below

- **H118** vwap_dist_vs_atr LOW tercile, 10-day drift. Holdout passed, one
  open paper position (opened 2026-09-08 at 29538.00, exits ~2026-09-22).
  Frozen, no retuning. Daily checker handles it. A project-wide multiplicity
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

(auto-built by src/pipeline_sweep.py -- do not hand-edit; rebuilt every cycle. Counts: OPEN 0, GATED 1, FROZEN 3.)

- SHELF: Shelf 2/3 live (Entry 15, 17) -> TOP-UP OWED before any draw
- GATED hyp-000142 vxn_level_vs_trailing_high_next_day_range (re-expressions: hyp-000143, hyp-000144): reached Integrity Gate checkpoint cleared -> OWED: nothing further automated -- frozen Holdout spec ready; Waiting on Jason to spend a Holdout slot
- FROZEN EXP047 prospective_validation_weekly_trend_exp047: reached FORWARD VALIDATION -> OWED: nothing -- evidence window open (H118: 40 trades AND 12 months); daily checker only
- FROZEN H118 vwap_dist_low_10d_drift_h118_INTEGRITY_REVIEW_MULTIPLICITY (re-expressions: hyp-000126, hyp-000130): reached FORWARD VALIDATION -> OWED: nothing -- evidence window open (H118: 40 trades AND 12 months); daily checker only
- FROZEN hyp-000105 midday_lull_afternoon_expansion (re-expressions: hyp-000106, hyp-000133, hyp-000141): reached HOLDOUT PASSED -> OWED: nothing -- Portfolio review complete (see research/studies/, KNOWN TRUE); daily checker only

## SESSION HANDOFF RULES (set by Jason 2026-09-11) — binding for every session, interactive or scheduled

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

## Queue

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

QUEUE v2 (Jason, September 12th ~9:10 am CT, after three outside-AI responses
were folded in -- research/infrastructure/outside-ai-synthesis-2026-09-12.md
is the reasoning; this block is the work). Cycles work it front to back under
the normal budget clock. PREPARATION items run unattended. The first
Discovery SCAN on any new entry waits for Jason's go. Active slate is capped
at 5 families at any time; everything else sits in research/sourcing/.

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
   a. LETF close rebalancing, instrument as a factor (RTY/ES/NQ), flow
      measured from AUM. DONE (Entry 17 / M13). Either outcome is decisive
      about whether "search where the forcing is largest" is a principle.
   b. Hedging-demand intraday momentum (Baltussen et al. 2021 JFE), price-
      only base with gamma regime computed from ES. Low pass odds, highest
      strategic information: it is the gate on buying options data.
   c. Overnight-vs-intraday tug-of-war (Lou, Polk, Skouras 2019 JFE).
      Probably true; explains H118; tells us where NQ's return lives; also
      a fast trade in its own right (hold overnight, flat by the open).
      Ruling vs gap-fade family and H116.
   d. Cash-open acceptance/rejection of the pre-open NQ/ES residual --
      the cheapest test of whether ANY cross-index relative-value effect
      survives at minute resolution; a kill-rule outcome settles the tick-
      data question for the whole track. Needs SPY/QQQ bars.
   e. Intraday momentum (Gao, Han, Li, Zhou 2018 JFE). Ruling vs hyp-000076
      and the IB family. Mostly informative about literature decay; also
      the confound for (a).
   f. Curve-conditioned NQ/ES rotation (needs ZT or SR3).
   Mechanism doc BEFORE any scan. One shot at the exact published spec.
3. DATA, in order, each via metadata.get_cost FIRST; any single pull at
   $5.00 or more stops and lists the number under "needs Jason" unless he
   has set a cap (see PARKED below): (i) ES, RTY, YM 1-min OHLCV, outright
   contracts where the feed allows; (ii) NQ outright contract months for the
   witching weeks only -- revives M9; (iii) SPY, QQQ, IWM, DIA 1-min;
   (iv) ZT or SR3; (v) free: VIX/VXN futures settlements from CBOE, LETF
   AUM/shares outstanding from issuer files (manual assembly). Register each
   file in data_loader with a coverage test. If no API key is available to
   the cycle, stop and say so under needs Jason.
4. OBSERVATORY PROGRAM (characterize, do not claim): an information-
   transmission map across ES/NQ/RTY/YM/ZN/6E/CL at 5/15/30/60-minute bars
   built from the 1-min data: shock -> first responder -> lag -> decay ->
   reversal, conditioned on the three validated vol states + semivariance.
   Plus a FIXED, interpretable state classifier (broad-equity agreement /
   NQ-only residual / rate-confirmed / rate-conflicted / high vs low
   overnight and cash-session variance) reporting forecast return, range and
   MAE per state. No ML. Portfolio's separability check of the range-
   contraction fact vs the other two comes first. Output = map-ready
   entries, not trades. This absorbs the day-type program.
5. PRACTITIONER STREAM: research/sourcing/practitioner.md -- claims enter
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
- H118 STATUS (raised September 12th, 9:03 am CT, IMMEDIATE, awaiting his call): baseline
  diagnostic shows the edge is not distinguishable from NQ's own drift.
  Nothing frozen touched. Ledger status change is his decision.
- DATA CAP: Jason has not yet set a dollar cap for the ES/RTY/YM (and later
  SPY/QQQ/IWM/DIA, ZT) pulls. Until he does, each pull quoted at $5.00+
  stops and waits. Asked September 12th ~9:10 am CT.
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

September 12th, 9:06 am CT (2026-09-12 14:00 UTC), scheduled cycle. Queue v2 item 1 done: two-nulls amendment + baseline_relative.py; H118 baseline diagnostic FAILS (edge not distinguishable from NQ's own drift, Jason messaged, status his call). Item 2 started: sourcing template + M13 LETF close rebalance filed (Entry 17), waits on RTY/ES data. pytest 284/284. Full: research/sessions/2026-09-12-1400.md.

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
