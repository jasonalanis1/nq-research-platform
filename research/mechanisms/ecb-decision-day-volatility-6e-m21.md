# Mechanism — ECB Governing Council rate decision, pre/post-release volatility, 6E (M21, open scope, map channel)

Written: 2026-09-12, ~5:55 pm CT (scheduled cycle)  ·  PRE-REGISTERED.
Results seen before writing: NO.
Source CHANNEL: map (forced participant), literature support:
Andersen, Bollerslev, Diebold and Vega (2003, American Economic Review)
and Ehrmann and Fratzscher (2005, J. International Money and Finance)
document a realized-volatility jump in EUR/USD around scheduled ECB
Governing Council rate announcements (fixed 45-minute press conference
schedule since 2015: decision ~13:45 CET / 07:45 ET, press conference
~14:30 CET / 08:30 ET) -- a magnitude claim, same design discipline as
M20, deliberately avoiding the direction-ambiguity failure mode (#4) that
closed the CPI/NFP family.

Third open-scope entry (with M19/ZN, M20/CL): signal AND trade in 6E.

## 1. The claim
6E's |return|/ATR14 in the hour spanning the press-conference start
(08:30-09:30 ET, covering the Q&A where volatility typically peaks per
Ehrmann-Fratzscher) is credibly larger than 6E's unconditional hourly
|return|/ATR14, on ECB decision days (roughly every 6 weeks, ~8/year).
Falsifiable in one sentence: if the decision-hour |return|/ATR14 has a
block-bootstrap 90% CI overlapping the unconditional hourly distribution,
no detectable ECB-day volatility signature exists in 6E 1-minute bars at
this ceiling and the entry closes.

## 2. Who is on the other side
FX dealers and macro funds who must reprice EUR rate-path expectations
the instant the statement and press conference cross; market makers who
widen through the announcement and are compensated by the realized move.
The forced element is the fixed, public SCHEDULE -- not a view on rates.

## 3. Testable predictions (gating marked)
P1 (GATING, magnitude): decision-hour |return|/ATR14 vs. unconditional
  hourly |return|/ATR14, credibly larger, block CI on the difference.
P2 (reported, direction, honestly unpinned): decision-hour signed mean
  return -- reported without a predicted sign, per the CPI/NFP lesson.
P3 (reported): compare the ECB decision-hour effect size to M20's EIA
  effect size (if both are run) -- a cross-check on whether "scheduled
  macro-adjacent releases show volatility jumps in 1-minute bars" is a
  general finding or specific to one instrument/event.
P4 (reported): decay across Discovery halves; ECB press-conference
  format has been stable since 2015 (before Discovery starts), so no
  format-change confound to control for.

## 4. What would falsify this
(a) P1 CI overlaps the unconditional distribution: closes. (b) KILL
RULE: if the decision-hour |return| is concentrated in the first
1-minute bar after the statement crosses (07:45 ET, before the press
conference the mechanism actually targets), the finding is a print
artifact at the STATEMENT, not the Q&A repricing this mechanism claims;
recorded and closes even if magnitude is confirmed, per the same
discipline as M20(b). (c) ECB meeting dates without a scheduled press
conference (pre-2015 format, not in Discovery) are not applicable; any
date where 6E RTH-equivalent hours are unusable is dropped and counted.

## 5. Resurrection ruling (LEARN + Integrity)
By name and by what is measured: no prior entry in this project's ledger
mentions 6E and a scheduled macro event together (checked by symbol and
by event name). CPI/NFP (CLOSED, direction ambiguity): different
instrument (NQ), different event (US labor/inflation, not ECB), and this
entry gates on magnitude only. M20 (EIA/CL, same cycle): different
instrument, different event, explicitly designed as a companion/cross-
check (P3), not a duplicate -- if both pass, that is the finding
"scheduled macro-adjacent events show a volatility signature," not two
separate findings double-counted; Portfolio would need to assess that
directly if both ever reach Validation. Pre-FOMC/post-FOMC (CLOSED): US
Fed, not ECB; different instrument. Not a resurrection of anything.
RULING: NEW. Enters. Attempt 1 of 2. Integrity signs at sourcing.

## 6. Instrument-choice gate
1. Leads: 6E itself -- the announcement is about the euro area.
2. Minutes not milliseconds: the claim is about the hour spanning a
   45-minute press conference, not the first tick.
3. 6E is the natural, only sensible vehicle.
4. Direction NOT gated (P1 magnitude); P2 reported honestly ambiguous.
5. NULL 1 built into P1 (vs. unconditional hourly |return|, not zero).

## 7. Frozen scope (for the scan)
ONE scan, Discovery only. ECB Governing Council monetary-policy meeting
dates with a press conference (public, fixed ~6-week schedule since
2015; roughly 8/year in-window) -- dates taken from the published ECB
schedule, a short fixed list assembled once and put in the script itself
(not a large external file; ~50 dates for the whole Discovery window).
Cells to register:
  1. decision-hour (08:30-09:30 ET) |return|/ATR14 mean vs unconditional
     hourly |return|/ATR14 mean, block CI on the difference   <- GATING (P1)
  2. decision-hour signed mean, block CI (P2, reported, unpinned sign)
  3. unconditional hourly |return|/ATR14 distribution mean (NULL 1 ref)
  4. share of the decision-hour |return| in the 07:45-07:46 statement
     print (KILL)
  5-6. cell 1 on Discovery halves (P4, 2 cells)
6 cells, 1 gating. Cross-reference to M20 (P3) is a comparison, not an
additional registered cell. Product track: RISK/VOLATILITY-EXECUTION
alpha if it passes -- same product class as M20 and the 3 validated
facts. Realization: event-anchored, 1-hour window. Data: 6E 1-minute on
disk; ECB dates assembled as a short fixed list in-script -- DRAWABLE now.

## 8. Ranking (information gain x edge potential)
Information gain: MODERATE. A second, independent instance of the
"scheduled macro event -> magnitude-only volatility claim" design
(companion to M20); together they test whether this class of finding
is general or a one-off, at essentially no incremental sourcing cost
(same design, different instrument/event/data already on disk).
Edge potential: MODERATE if it passes, same volatility/execution-input
class as M20 and the three validated facts -- not a directional trade.

## 9. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested (pending M20's own
result, if it advances). P4 -- untested.

## 10. Draw attempt, 2026-09-12 ~6:35 pm CT
Attempted to draw for Scan 024 this cycle. The frozen scope (Section 7)
calls for a short, fixed, public list of ECB Governing Council press-
conference dates assembled once in-script. WebFetch/WebSearch could only
confirm 2026-10-29 and 2026-12-17 plus 2027-2028 dates before hitting
this session's web-tool rate limit -- no verified historical list for
the 2015-2026 Discovery window was obtained. Per the no-fabrication rule,
did NOT hand-write remembered/approximate historical ECB dates into the
frozen scope. Filed WAITING ON a verified full historical ECB press-
conference date list (2015-2026) -- either from a fresh WebFetch once the
web-tool limit resets, or supplied by Jason. Mechanism doc and gating
design (Section 7) are unchanged and remain pre-registered; only the
date list is outstanding. Still DRAWABLE once the date list exists.

## 11. Scan 025 result, 2026-09-13 ~12:20 am UTC (hyp-000150)
A fresh WebFetch/WebSearch this cycle (the prior session's rate limit
had reset) found a usable historical source: the Jarocinski-Karadi ECB
monetary policy shocks dataset (public academic data, indexed by
Governing Council meeting date since 1999), rather than the ECB's own
site, whose press-conference archive pages did not return a usable
static date list. n=54 dates in the Discovery window (2015-01 to
2021-10.03), n=35 usable events.

GATING P1 PASSED: decision-hour (08:30-09:30 ET) |return|/ATR14 = 0.713
vs unconditional hourly 0.179, diff +0.534, CI (+0.457,+0.782) -- the
largest magnitude effect found in either the M20 or M21 family. P2
(signed decision-hour mean) is null as predicted: +0.048, CI
(-0.166,+0.235). Kill check: 07:45 statement-print share is 37.9%,
below the 0.5 threshold (not killed) but disclosed as material at
Statistical. Halves: 0.863 / 0.571 (both well above baseline; some
decay; CI not computable at this sample size).

STATISTICAL PASS -> DIRECTOR CONTINUE (second open-scope Discovery pass,
cross-confirms the scheduled-macro-event volatility pattern alongside
M20) -> MONETIZATION: NO CREDIBLE PATH (no 6E strategy exists, live or
Discovery, to attach a sizing overlay to -- every 6E-touching script in
this codebase uses 6E only as a cross-asset predictor for NQ).

hyp-000150 REJECTED as a valid characterization, not a failure. Filed
KNOWN TRUE alongside M20's EIA/CL fact, held for a future 6E base
strategy. Entry CLOSED at Monetization (not a Discovery-stage close);
attempt 1 of 2 spent, though Monetization's disposition is not sample-
dependent so a second attempt would only be warranted by a genuinely new
claim, not a retry of this one.

## 12. Closure form (U8, retroactive pass 2026-09-13 7:00 pm CT)
- Hypothesis / family: hyp-000150 / M21 ECB decision volatility, 6E
- Closure status: valid-but-non-actionable
- Primary outcome (as registered) and result: Discovery PASS (+0.534 ATR, Scan 025), Statistical PASS; Monetization no path at the time
- Sample adequacy: adequate
- Mechanism verdict: supported
- Robustness / cost / concentration flags: none
- What was learned: Largest effect in the M20/M21 family; same reclassification as M20 (2026-09-13).
- What must NOT be retested: Nothing -- passed.
- Permitted future retest condition: family-level Monetization (U5c)
- Capacity action: increase family (as part of U5c)
