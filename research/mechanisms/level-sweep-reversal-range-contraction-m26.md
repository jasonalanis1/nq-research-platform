# Mechanism — Level Sweep Reversal, conditioned on prior-day range contraction (M26, resurrection, practitioner/map channel)

Written: 2026-09-13, ~11:15 am CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO. No scan exists.
Origin: this cycle's earlier interactive conversation with Jason (2026-09-13)
-- he raised, in plain terms, whether a pattern that failed unconditionally
(the project's own closed Level Sweep Reversal family) could still be real
under a specific market condition, the way a discretionary trader would
only take a setup "when the tape looks a certain way," rather than every
time it appears. This is the first concrete test of that question.

## 1. The claim
Level Sweep Reversal (`close_min_distance` variant: price sweeps a prior-
day/pre-market reference level, then the confirming bar's CLOSE clears
back beyond the level by at least 5.0 points before entry) has a credibly
different expectancy on days that follow a COMPRESSED prior trading day
(bottom tercile of trailing prior-day range, the project's own
`prior_day_narrow` state variable from `src/volatility_conditioning.py`,
underlying hyp-000046/048, HOLDOUT PASSED) than on days that do not.
Mechanism reasoning: a level sweep during an already-compressed volatility
regime is more likely a genuine liquidity grab ahead of continued range-
bound trading (the setup's original reversal thesis), whereas the same
sweep during an already-expansive regime is more likely the first leg of
a breakout/trend day, where "reversal after a sweep" is the wrong bet by
construction. If real, this would explain why the unconditional test came
back flat: two opposite-sign sub-populations averaging to noise.

## 2. Who is on the other side
Same participants as the original Level Sweep Reversal thesis (stop-hunt
liquidity providers, momentum traders who get trapped past the level) --
this is NOT a new participant story, it is a claim about WHEN that
existing story's mechanics actually dominate versus when a competing
mechanic (trend/breakout continuation) dominates instead.

## 3. Why this is not the overfitting trap
This project's own discipline exists specifically to prevent "slice the
data until something looks good." What makes this different: the
conditioning variable (`prior_day_narrow`) was chosen and validated
BEFORE this hypothesis existed, for a completely unrelated purpose (a
volatility-conditioning sizing fact, HOLDOUT PASSED 2026-09-09, no
Level-Sweep-Reversal data or results were involved in defining it). This
is the ONLY conditioning variable being tried here -- not the first of a
search across many candidate slices. If this comes back null, the
question is treated as ANSWERED (no), not as a prompt to try the next
slice (coiled-overnight, volume regime, etc.) on the same dead pattern.

## 4. Testable predictions
P1 (GATING). On days following a `prior_day_narrow` (bottom-tercile
   compressed prior-day range) session, `close_min_distance` Level Sweep
   Reversal trades show expectancy credibly ABOVE zero (90% block-
   bootstrap CI on per-trade R entirely above zero).
P2 (reported, the actual "is this conditional and not just noise"
   question). The COMPRESSED-day expectancy is credibly HIGHER than the
   NON-compressed-day expectancy (difference CI excludes zero) -- this is
   the cell that actually answers Jason's question, distinct from P1
   alone (P1 could pass by chance on a subset even with no real gradient).

## 5. What would falsify this
(a) P1 fails (compressed-day expectancy not credibly positive) -- closes
    the conditional story outright, same standing as the unconditional
    closure.
(b) P1 passes but P2 fails (no credible gap vs. non-compressed days) --
    the compressed-day subset just got lucky; the pattern is still dead,
    same failure mode discipline as M13/M14/M18 this week (P1-passes-
    without-P2 is explicitly NOT a real finding in this project).
(c) THIN-SAMPLE kill: Level Sweep Reversal fires infrequently (150-220
    trades over the full 2015-2021 Discovery slice in the original
    tests); splitting by tercile could leave too few compressed-day
    trades for a meaningful CI. If the compressed-day cell has fewer than
    ~40 trades, disclose as underpowered rather than claim a null.

## 6. Information gain and edge potential
Information gain: HIGH if real -- this would be the project's first
directional (not merely conditioning) signal to survive Discovery in
months, and it would validate the whole "condition old dead ideas on
proven state facts" methodology Jason asked to prioritize ahead of the
September 19th checkpoint. Information gain is also real if null:
answers a specific, previously-untested version of "does it ever work"
plainly, closing one more branch of the original six-variant Level Sweep
Reversal family for good rather than leaving it as an open, recurring
question.
Edge potential if real: directly tradeable -- Level Sweep Reversal
already has a fully specified entry/exit (research/setups/level-sweep-
reversal.md), so a credible conditional pass here is close to
Monetization-ready without a new strategy design step, unlike M23 this
same cycle.

## 7. Resurrection ruling (LEARN + Integrity)
- NOT a re-run of the unconditional Level Sweep Reversal tests
  (exp-003 through exp-024, `close_min_distance` specifically: exp-007,
  011, 015, 019, 021, 023 -- all either thin-sample or non-credible on a
  properly holdout-respecting Discovery slice, most recently exp-023:
  -0.038R, 90% CI spans zero). Those tested the UNCONDITIONAL pattern.
  This tests one specific, pre-chosen CONDITIONAL claim -- structurally
  the same distinction the project already draws for its volatility
  facts (e.g. M13/M14's own instrument-conditioned tests).
- NOT the FVG entry trigger variant (exp-025, killed decisively,
  -0.208R, CI entirely below zero) -- different entry mechanic, not
  reused here; `close_min_distance` only.
- NOT the trend-structure-liquidity-filter idea from `docs/BACKLOG.md`
  (interior-liquidity vs. protected-high/low distinction) -- that filter
  was never precisely defined and was flagged as introducing new
  overfitting-prone parameter choices; `prior_day_narrow` is an existing,
  already-frozen, already-validated variable, not a new invented filter.
- NOT the event-conditioned-reference-level-fade thread (h81 recut,
  under separate LEARN/Mechanism/Director review) -- that conditions a
  DIFFERENT setup (exp-110 Opening-Hour Reference-Level Fade) on
  scheduled-event proximity, not on volatility state, and is not a
  Level-Sweep-Reversal test at all.
RULING: NEW. Attempt 1 of 2 (the family's overall 2-attempt budget is
tracked per-conditioning-variable, not per the whole Level Sweep Reversal
history, since the unconditional attempts are a structurally different
claim already closed on their own terms).

## 8. Instrument-choice gate
1. NQ only -- Level Sweep Reversal was designed and originally tested on
   NQ; `prior_day_narrow` is also computed on NQ's own daily range. No
   cross-instrument step needed.
2. Daily state variable (prior day), intraday trade horizon (same-day
   entry/exit per the existing setup spec) -- consistent time horizons,
   no lookahead (the state is known before the trading day begins).
3. Directional (per-trade R), not a magnitude/relative claim. NULL 1
   does not directly apply (this is an expectancy-vs-zero test on a
   conditioned trade subset, following the same convention as the
   original Level Sweep Reversal expectancy tests, not a drift-vs-
   baseline test).

## 9. Frozen scope (for the scan)
ONE scan. Re-run `close_min_distance` Level Sweep Reversal exactly as
specified in `research/setups/level-sweep-reversal.md` (5.0-point
confirm distance, existing entry/exit/stop/target, Discovery slice
2015-01-01 to 2021-10-03, holdout-respecting per `src/data_holdout.py`)
via `src/detect_level_sweep.py close_min_distance`, then split the
resulting trade list by whether the trade's OWN trading day was flagged
`prior_day_narrow` in `src/volatility_conditioning.py`'s existing,
frozen tercile definition (bottom tercile of trailing prior-day range,
computed once, never refit).
Cells: (1) compressed-day expectancy, block CI (GATING P1); (2)
non-compressed-day expectancy, block CI (reference); (3) difference,
block CI (P2, the real test); (4) trade-count check per cell (falsifier
c, thin-sample disclosure). Four cells total, registered exactly before
the scan is written, no retuning after seeing results.
Data: NQ 1-minute OHLCV, already on disk, full Discovery range. No
purchase needed.

## 10. Prediction status
P1 -- untested. P2 -- untested. NOT drawn this cycle: budget-use
judgment call -- this cycle already ran a full Discovery scan (Scan 030,
M23) plus its full disposition (Director, Monetization, ledger, four
document updates); sourcing this entry restores the shelf to the floor
of 3 as SHELF RULE v2 requires, but the draw itself is deferred to
preserve budget for a careful, unhurried close-out. DRAWABLE as of this
doc's completion; first in line next cycle (or sooner, given Jason's
explicit interest in this exact question ahead of September 19th).

## 11. Disposition (2026-09-13, Scan 033, hyp-000159) -- first sanctioned conditional retest
Drawn in the September 13th ~4:45 pm CT interactive test cycle (the first cycle
after the freeze was lifted), under the eight-condition conditional-retest protocol
adopted the same day. Four cells, registered in SCAN_REGISTRY before the scan ran.
GATING P1: compressed-day (prior_day_narrow) net R mean=+0.0300, ci_90=(-0.1093,
+0.1860), n=131 -- adequately powered (falsifier (c) threshold 40), NOT credible.
Reference: non-compressed mean=-0.0652, ci_90=(-0.1686,+0.0328), n=343.
P2 (the real question): compressed minus non-compressed = +0.0952, ci_90=(-0.0687,
+0.2736) -- not credible. The gap points the predicted way (compressed days are
better than non-compressed) but does not clear noise.
Counts: 474 trades on the Discovery slice (exp-023 had 461 on the 2026-08-20 data
file; this run used the 2026-09-09 file and a year-chunked scan with identical
detection math -- disclosed, not material). 98.5% of compressed-day trades resolved
(stop or target), so the result is not an artifact of unresolved end-of-day exits.
VERDICT: P1_FAIL. Closed per falsifier (a). Director Re-Evaluation: CONCUR -- a clean,
powered null, not a near-miss; attempt 1 of 2 for this conditioning family; no
re-test without a materially different, independently established condition.
Answer to Jason's question ("does a pattern that failed on average still work under
specific conditions") for THIS pattern and THIS condition: no. The methodology
itself worked as designed -- one pre-chosen condition, one shot, honest answer.
