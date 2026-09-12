# Mechanism — EIA weekly petroleum inventory report, pre/post-release drift, CL (M20, open scope, map channel)

Written: 2026-09-12, ~5:45 pm CT (scheduled cycle)  ·  PRE-REGISTERED.
Results seen before writing: NO.
Source CHANNEL: map (forced participant), literature support: the EIA
Weekly Petroleum Status Report (released Wednesdays ~10:30 ET, 52x/year,
occasionally shifted a day for a Monday holiday) is a scheduled, high-
attention data release; Linn and Zhu (2004, Energy Journal) and Gu, Kurov
and Wolfe (2018, J. Futures Markets) document a pre-release positioning
drift and a post-release volatility jump in crude futures around it,
distinct from FOMC/CPI/NFP (already closed families, different
instrument, different release type -- a physical-supply data release,
not a monetary or labor release).

Second open-scope entry (after M19/ZN): signal AND trade in CL.

## 1. The claim
CL's RTH return in the hour before the 10:30 ET release, and the hour
after, are each credibly non-zero (either sign, reported), and the
POST-release hour shows credibly larger |return| / ATR than an
unconditional RTH hour (a volatility-jump claim, not a directional one --
avoids the direction-ambiguity failure mode #4 that closed CPI/NFP).
Falsifiable in one sentence: if the post-release hour's |return|/ATR has
a block-bootstrap 90% CI overlapping the unconditional hourly |return|/ATR
distribution's CI, there is no detectable EIA-day volatility signature in
CL 1-minute bars and the entry closes.

## 2. Who is on the other side
Hedgers (producers, refiners, airlines) and speculators who must reprice
inventory-driven fair value the moment the report crosses; market makers
who widen ahead of the print and are paid via the post-release move for
having quoted through the uncertainty window. The forced element is the
SCHEDULE (everyone reprices at the same 10:30 print), not a directional
view.

## 3. Testable predictions (gating marked)
P1 (GATING, magnitude not direction): post-release hour (10:30-11:30)
  |return|/ATR14 vs. the unconditional distribution of |return|/ATR14
  over all RTH hours in Discovery, credibly larger (one-sided, block CI
  on the difference of means).
P2 (reported, direction, honestly labeled ambiguous per failure mode #4):
  pre-release hour (09:30-10:30) mean signed return -- reported without a
  pinned sign, exactly as the CPI/NFP lesson requires.
P3 (reported): the post-release |return| effect scales with the
  DEVIATION of the actual inventory change from the trailing 4-week
  average change (a proxy for "surprise size") -- REQUIRES the EIA
  inventory figures; if unavailable, not run and recorded as such.
P4 (reported): decay across Discovery halves.

## 4. What would falsify this
(a) P1 CI overlaps the unconditional distribution: no detectable EIA
signature at this ceiling. Closes. (b) KILL RULE: if the post-release
volatility is concentrated in the first 1-minute bar after 10:30, it is
a print-reaction artifact indistinguishable from any scheduled release
and not itself informative; the finding is recorded as "print effect
only," which still closes the ENTRY (nothing to trade at 1-min
resolution) even though it is a real, if trivial, confirmation. (c)
Roll-day and holiday-shifted release days handled per the Scan 020 rule
(a report day with unusable RTH data is dropped and counted, not forced).

## 5. Resurrection ruling (LEARN + Integrity)
By name and by what is measured:
- CPI/NFP reaction (CLOSED, direction ambiguity #4): pooled event
  reaction in NQ, unconditioned sign, closed for DIRECTION ambiguity.
  This entry explicitly measures MAGNITUDE only (P1 gating), with
  direction reported but never gated (P2) -- built to not repeat that
  failure. Different instrument (CL not NQ), different event class
  (supply data, not monetary/labor). Not a resurrection.
- Pre-FOMC / post-FOMC drift (CLOSED, 2 attempts each): different event,
  different instrument, different release cadence (52x/yr weekly vs 8x/yr).
  Not a resurrection.
- Days-to-opex, turn-of-month (SKIP LIST): calendar effects with no
  named participant. This names the participant (hedgers/market makers
  repricing at a scheduled release) and is instrument-specific to the
  underlying being reported on. Not a resurrection.
- No CL-specific event-day entry has been run in this project's history
  (LEARN check of the ledger by name and by instrument: no hyp row
  mentions CL or EIA). Genuinely new instrument and new event class.
RULING: NEW. Enters. Attempt 1 of 2. Integrity signs at sourcing.

## 6. Instrument-choice gate
1. Leads: CL itself -- the report is ABOUT crude oil inventories.
2. Minutes not milliseconds: the pre-release positioning window and the
   post-release repricing window are each an hour, not a race (though
   the kill rule checks the first minute specifically for a pure print
   artifact).
3. CL is the natural and only sensible vehicle -- this is not a
   cross-instrument question.
4. Direction is explicitly NOT gated (P1 is magnitude); P2 is reported
   honestly ambiguous.
5. NULL 1 is built into P1 by construction (compared to the
   unconditional hourly |return| distribution, not to zero).

## 7. Frozen scope (for the scan)
ONE scan, Discovery only. EIA Wednesday release dates: every Wednesday
in the Discovery window EXCEPT weeks with a Monday holiday (where EIA
shifts to Thursday) -- built from the NYSE holiday calendar already on
disk (used by the FOMC/CPI scans), not from an external EIA calendar
file (the release-day RULE is public and mechanical: Wednesday, or
Thursday if Monday was a holiday that week). Cells to register:
  1. post-release hour |return|/ATR14 mean vs unconditional-hour
     |return|/ATR14 mean, block CI on the difference        <- GATING (P1)
  2. pre-release hour signed mean, block CI (P2, reported, unpinned sign)
  3. unconditional RTH-hour |return|/ATR14 distribution mean (NULL 1
     reference, reported)
  4. share of the post-release |return| in the 10:30-10:31 bar (KILL)
  5-6. cell 1 on Discovery halves (P4, 2 cells)
6 cells (9 if the inventory-surprise file is available for P3), 1 gating.
Product track: RISK/VOLATILITY-EXECUTION alpha if P1 passes (a
volatility-conditioning input for options/straddle-style structures, NOT
a directional signal -- consistent with this project's only validated
facts being of this type). Realization: event-anchored, 1-hour window.
Data: CL 1-minute on disk; the NYSE holiday calendar used to compute
Wednesday/Thursday shifts is already in the codebase (FOMC scans). No
new external data needed -- DRAWABLE now, unlike M19.

## 8. Ranking (information gain x edge potential)
Information gain: MODERATE-HIGH. First CL-specific event-day entry ever
in this project; a magnitude-only design that should be immune to the
direction-ambiguity failure mode that closed CPI/NFP -- tests whether
that failure mode was about the STATISTIC (pooled direction) or the
INSTRUMENT/EVENT (macro releases in an equity index). If this also nulls,
it strengthens the case that EVENT-DAY volatility signatures are not
visible in 1-minute OHLCV either, a fourth failure-mode data point.
Edge potential: MODERATE if it passes (a volatility/execution input, not
a directional strategy -- same product class as the three validated
facts) -- consistent with and adding to that track rather than
competing with it.

## 9. Prediction status -- SCAN 023 RUN, September 12th, ~6:05 pm CT, PASSED DISCOVERY THEN CLOSED AT MONETIZATION
P1 -- PASS. Post-release hour |return| = 0.367 ATR vs unconditional
hourly 0.186 ATR, diff +0.181, CI (+0.155, +0.216), n=329 release dates.
Not killed (first-minute share 0.481, below the 0.5 line) but CLOSE to
it -- disclosed at Statistical: roughly half the excess volatility is
the print minute itself. P2 (direction, unpinned) -- null as expected
(+0.006 ATR). P3 -- not run (needs inventory-surprise figures, not
required for P1). P4 -- some decay (first half 0.415, second half 0.318)
but both far above baseline.
Ledger: hyp-000148. Discovery PROMISING -> Statistical PASSES (near-kill
disclosed as a hard constraint on Monetization) -> Director CONTINUE
(narrowly) -> **Monetization: NO CREDIBLE PATH** (this project has zero
CL strategies to attach a sizing overlay to) -> final status REJECTED
(closed, no product path -- the Discovery finding itself was NOT falsified).
Filed as KNOWN TRUE / characterization for future use if a CL strategy is
ever built. Full record: research/studies/eia-volatility-m20-statistical-
2026-09-12.md, -director-reeval-2026-09-12.md, -monetization-2026-09-12.md.
Attempt 1 of 2 spent (a second attempt would need a different claim, not
a re-test of magnitude).
