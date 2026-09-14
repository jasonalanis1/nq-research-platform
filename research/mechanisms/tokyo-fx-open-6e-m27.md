# Mechanism — Tokyo FX session open, 6E (M27, map/practitioner channel, open scope)

Written: 2026-09-13, ~2:00 pm CT (scheduled cycle) · PRE-REGISTERED.
Results seen before writing: NO. No scan exists.
Origin: sourcing owed this cycle after M24 (Entry 28) closed and dropped
the shelf below the SHELF RULE v2 floor of 3. Companion entry to M23
(London-open volatility, 6E, P1_PASS this same day) -- same methodology
family (structural session-boundary volatility, magnitude not
direction), applied to the OTHER major FX session-open boundary that
6E's 24-hour data already covers.

## 1. The claim
The hour following the Tokyo FX session's opening (19:00-20:00 ET, when
Tokyo desks return from their daily break and begin quoting for the
Asian session) shows |return|/ATR14 in 6E (Euro futures) credibly
elevated versus the unconditional hourly |return|/ATR14 baseline
computed across ordinary RTH-equivalent hours. Mechanism: Japanese
exporters/importers, Asian real-money accounts, and Tokyo-based bank
desks clear a backlog of orders accumulated since the prior session's
close, against comparatively thin liquidity at the seam between the
US afternoon lull and the Asian session's own ramp-up -- structurally
the same forcing mechanism as M23's London open, but a distinct venue,
distinct participant base (Asian real-money and corporate flow, not
European dealers), and a distinct time of day with no session overlap
with M23's own window.

## 2. Who is on the other side
Tokyo-based bank FX desks providing liquidity into a session open;
Japanese corporate treasury (exporter/importer hedging flow) and Asian
real-money accounts placing orders that accumulated since the US
afternoon; no scheduled news event required -- purely session-structure
liquidity, the same class as M1/M2 (NQ cash close/RTH open) and M23
(London open), not a calendar-event entry.

## 3. Why this is not the overfitting trap
This is not a slice of M23's own result -- it is a distinct, non-
overlapping time window (19:00-20:00 ET vs. M23's 03:00-04:00 ET, no
shared hours) tested on the SAME pre-existing, already-frozen
methodology (unconditional-hourly-baseline comparison, pre-window
specificity check, first-minute kill check) that M23 itself used, not a
new statistic invented after seeing M23's result. The Tokyo-open
hypothesis was an obvious candidate the moment M23 was sourced (6E's
24-hour data trivially supports checking every major session boundary),
not something searched for after M23 passed. Attempt 1 of 2 for this
specific session boundary.

## 4. Testable predictions
P1 (GATING). Tokyo-open hour (19:00-20:00 ET) |return|/ATR14 in 6E is
   credibly ABOVE the unconditional hourly |return|/ATR14 baseline (90%
   block-bootstrap CI entirely positive).
P2 (specificity, reported). The hour immediately BEFORE the Tokyo open
   (18:00-19:00 ET) does NOT show the same elevation -- distinguishes a
   genuine session-boundary effect from "the whole evening is noisy."
P3 (kill check). Share of the Tokyo-open hour's total |return| coming
   from the single first 1-minute bar is NOT more than half -- rules out
   a thin-liquidity single-print artifact rather than a genuine hour-long
   effect.

## 5. What would falsify this
(a) P1 fails (CI does not clear zero, or clears on the wrong side) --
    closes this session boundary; the London-open finding (M23) does not
    generalize to every session open in 6E.
(b) P1 passes but P2 fails (pre-Tokyo hour equally elevated) -- not
    specific to the session boundary, more likely a generic
    evening-liquidity-thinness artifact; not a genuine structural finding
    on its own terms, same standard M23 itself was held to.
(c) KILL: first-minute share of the Tokyo-open hour's |return| exceeds
    0.5 -- a print artifact, not an hour-long liquidity-clearing effect.

## 6. Information gain and edge potential
Information gain: HIGH if real -- would be the SECOND clean pass in the
"structural session-boundary volatility" family (after M23), starting to
establish whether this is a general property of FX session opens or
specific to London's outsized share of global FX volume. Also real if
null: tells us the effect is London-specific (a liquidity-concentration
story tied to London's dominant FX market share) rather than a generic
property of any session open, which is itself a useful characterization
fact either way.
Edge potential if real: same open question M23 left -- 6E has zero
existing base strategies to size against a volatility fact, so a P1
pass here would again defer to a fresh sourced entry for standalone
strategy design, not be monetization-ready on its own (unlike M24/NQ,
which already has a base strategy -- this is the structural-volatility
family's usual limitation, flagged in advance).

## 7. Resurrection ruling (LEARN + Integrity)
- NOT a re-run of M23 (different, non-overlapping window: Tokyo open
  19:00-20:00 ET vs. London open 03:00-04:00 ET; different participant
  story -- Asian real-money/corporate flow vs. European dealer backlog
  clearing).
- NOT a re-run of M20 (EIA/CL, scheduled news event, different
  instrument and mechanism class entirely) or M21 (ECB/6E, scheduled
  news event -- this entry has NO news event, purely session-structure,
  the same distinction M23 itself drew against M21).
- NOT M15 (overnight-vs-intraday session-level premium, NQ, unconditional
  decomposition with no state variable, already closed) -- different
  instrument, different claim shape (this is an hour-specific magnitude
  claim, not a full-session-split decomposition).
RULING: NEW. Attempt 1 of 2.

## 8. Instrument-choice gate
1. 6E only -- mirrors M23's own instrument choice; full 24-hour 6E
   coverage already confirmed on disk (used by Scan 030/M23 this same
   day). No cross-instrument step needed for a single open-scope
   characterization entry.
2. Hourly state window, same-hour horizon -- consistent time horizon, no
   lookahead (the hour boundary is known in advance from the clock, not
   estimated from data).
3. Magnitude claim (|return|/ATR14), not directional -- NULL 1 is the
   unconditional hourly |return|/ATR14 baseline, same convention as M20/
   M21/M23.

## 9. Frozen scope (for the scan)
ONE scan, full Discovery range (2015-01-01 to Discovery-slice cutoff),
6E 1-minute OHLCV (already on disk, confirmed this same cycle). Four
cells, mirroring M23's own Scan 030 exactly:
  1. Tokyo-open hour (19:00-20:00 ET) mean |return|/ATR14 minus
     unconditional hourly baseline, block bootstrap CI       <== GATING (P1)
  2. Pre-Tokyo hour (18:00-19:00 ET) minus unconditional, specificity
     check, reported (P2)
  3. Unconditional hourly |return|/ATR14 distribution mean (NULL 1
     reference)
  4. KILL: share of the Tokyo-open hour's total |return| from its first
     1-minute bar (P3)
Statistical convention: block bootstrap, block=10 (matches the M20/M21/
M23 family's own daily/hourly-frequency convention), N_BOOT=3000,
SEED=20260913, 90% CI, "credible" = CI entirely on one side of zero.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. NOT drawn this cycle:
sourced to restore the shelf floor per SHELF RULE v2 after M24/Entry 28
closed; drawing deferred to preserve budget for a careful, unhurried
close-out on top of the M24 disposition already completed this cycle.
DRAWABLE as of this doc's completion; first in line next cycle.

## 11. Disposition (2026-09-13, Scan 034, hyp-000160) -- 7:00 pm CT test cycle
GATING P1 FAIL, and informatively so: the Tokyo-open hour is credibly QUIETER than the US-session
hourly baseline (diff -0.0968 ATR, ci_90 (-0.1056,-0.0861), n=644 days), as is
the pre-Tokyo hour (-0.1101). Not a print artefact (first-minute share 0.192). 247 Discovery days
lacked 18:00/19:00 bars and were skipped -- disclosed. VERDICT: P1_FAIL, closed per falsifier (a).
Director: CONCUR. What this teaches the family: the London-open burst (M23, +0.0537, all four Statistical
questions passed the same evening) is specific to the London open, not a generic "any session boundary
gets a burst" effect -- the Tokyo boundary in the euro future is a quiet hour. That sharpens M23's
mechanism (European real-money flow at THEIR open) rather than weakening it. Attempt 1 of 2; no re-test
without a materially different construction. Closure form owed (U8).

## 12. Closure form (U8, retroactive pass 2026-09-13 7:00 pm CT)
- Hypothesis / family: hyp-000160 / M27 Tokyo FX open, 6E
- Closure status: clean null (informative)
- Primary outcome (as registered) and result: P1 credibly NEGATIVE: Tokyo hour quieter than baseline (Scan 034, n=644)
- Sample adequacy: adequate
- Mechanism verdict: falsified; sharpens M23
- Robustness / cost / concentration flags: 247 days skipped for missing bars
- What was learned: Session-open volatility bursts in 6E are London-specific, not generic to session boundaries; the Tokyo hour is a quiet hour.
- What must NOT be retested: Tokyo-open magnitude claims on 6E.
- Permitted future retest condition: none
- Capacity action: hold (M23 family continues)
