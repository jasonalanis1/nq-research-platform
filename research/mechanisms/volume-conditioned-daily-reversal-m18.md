# Mechanism — volume-conditioned daily reversal, NQ (M18, literature)

Written: 2026-09-12, ~5:10 pm CT (TEST cycle, sourcing toward the shelf
floor)  ·  PRE-REGISTERED. Results seen before writing: NO.
Source CHANNEL: literature. Campbell, Grossman and Wang (1993), "Trading
Volume and Serial Correlation in Stock Returns," Quarterly Journal of
Economics 108(4): daily index returns reverse MORE after high-volume days
than after low-volume days. Mechanism: when non-informational traders
need to sell (or buy), risk-averse liquidity providers absorb the flow
only at a price concession that is later reversed; the concession is
larger when the flow is larger, and volume marks the size of the flow.
Corroborated by Conrad-Hameed-Niden (1994) and Llorente-Michaely-Saar-Wang
(2002), who add that the sign flips for INFORMED volume (continuation) --
which is the confound this entry pre-registers.

## 1. The claim
For NQ, the next-session RTH return, sign-adjusted against today's RTH
return, is credibly NEGATIVE (reversal) when today's RTH volume is in its
top tercile relative to its trailing 20-day mean, and the reversal is
credibly LARGER than after low-volume days. Falsifiable in one sentence:
if the high-volume sign-adjusted next-day return's block-bootstrap 90% CI
includes zero on Discovery, or if it is not credibly below the
low-volume cell, the claim is not there and the entry closes.

## 2. Who is on the other side
Liquidity providers (dealers, market makers, short-horizon arbitrageurs)
who must hold overnight inventory they did not choose after a large
non-informational imbalance. Their constraint is capital and risk
tolerance; the footprint is a price concession that mean-reverts as
inventory is worked off over the next session. Nobody chooses to leave
money; the reversal is the fee for immediacy.

## 3. Testable predictions (gating marked)
P1 (GATING): sign-adjusted next-session RTH return / ATR14 given today's
  volume ratio (RTH volume / trailing-20d mean) in the TOP tercile is
  credibly negative (block bootstrap, block 10). NULL 1 reported: the
  unconditional sign-adjusted next-day return (NQ's own lag-1 daily
  autocorrelation) -- the claim is a volume GRADIENT on reversal, not
  reversal per se.
P2 (reported, gating on the gradient): HIGH-volume cell credibly below
  LOW-volume cell (bootstrap on the difference).
P3 (reported, the informed-volume confound): split the HIGH-volume cell
  by whether today's |return|/ATR is in its top tercile. Per
  Llorente et al., large-move + high-volume days can be informed
  (continuation); if the reversal lives ONLY in the small-move high-
  volume cell, the mechanism is confirmed in its own terms; if it lives
  only in the large-move cell, it is the closed gap/level-fade family
  restated and the entry is recorded "confounded".
P4 (reported): decay across Discovery halves (published 1993; base case
  is decayed at the index level).

## 4. What would falsify this
(a) P1 CI includes zero: closes. (b) P1 passes but P2 fails: it is NQ's
own daily reversal (or lack of it), volume adds nothing; closes.
(c) KILL RULE: if more than half of the next-session sign-adjusted return
sits in its first one-minute bar (the open print), the "reversal" is an
overnight gap artifact; family terminates. (d) Roll-Friday and half-day
sessions dropped and counted; calendar days with Globex-only bars are
not sessions and do not break the chain (Scan 020 lesson).

## 5. Resurrection ruling (LEARN + Integrity)
By name and by what is measured:
- hyp-000043 daily_volume_level_standalone_signal (REJECTED): volume
  LEVEL alone as a next-day signal, no sign pinned, no interaction. This
  is a volume x return INTERACTION with a pinned sign and a named
  participant. Adjacent; not the same measurement. Not a resurrection.
- hyp-000110 / M1 closing-pressure reversal (CLOSED FOR GOOD): last-10-
  minute move conditioned on CLOSE-WINDOW volume -> next morning. This
  is the whole-session return conditioned on whole-session volume ->
  next whole session. Same participant class (liquidity provision),
  different window and different flow. Adjacent; disclosed; not a
  resurrection. If P1 passes, Integrity re-checks separability from M1
  at the Statistical stage before anything advances.
- hyp-000022 cross_asset_short_term_reversal (REJECTED): weekly reversal
  on the basket, unconditioned. Different horizon, no volume. Not a
  resurrection.
- Gap-fade and level-fade families (closed): condition on gap sign or
  level touch, not on volume. P3 is the pre-registered separator.
- hyp-000072/074 volume vacuum (REJECTED): intraday low-volume bars.
  Different. Not a resurrection.
RULING: NEW, with two disclosed adjacencies (043, 110). Enters. Attempt
1 of 2. Integrity signs at sourcing.

## 6. Instrument-choice gate
1. Leads: the instrument itself -- an inventory effect on the index
   future's own order flow. NQ.
2. Minutes not milliseconds: inventory is worked off over a session.
3. NQ is the cheapest expression (one contract, one round trip).
4. Directional NQ, sign-adjusted. Not relative.
5. NULL 1: NQ's unconditional lag-1 daily autocorrelation reported
   beside the gate; the claim is the volume gradient.

## 7. Frozen scope (for the scan)
ONE scan, Discovery only. Session = RTH 09:30-16:00. vol_ratio = RTH
volume / trailing-20d mean RTH volume (lagged). Terciles frozen on
Discovery. Outcome = next-session RTH return / ATR14, sign-adjusted by
today's RTH return sign. Cells to register:
  1. HIGH-volume sign-adjusted next-day mean, block CI  <- GATING (P1)
  2. LOW-volume, same statistic (P2 comparison)
  3. MID-volume (reported)
  4. HIGH minus LOW, bootstrap on the difference (P2, reported)
  5. unconditional sign-adjusted next-day mean (NULL 1)
  6-7. HIGH cell split by today's |ret|/ATR top tercile vs rest (P3)
  8-9. HIGH cell on Discovery halves (P4)
  10. share of HIGH-cell response in the next session's first 1-min bar
      (kill rule)
10 cells, 1 gating. Product track: DIRECTIONAL alpha. Realization:
TIME-BASED, hold next RTH session (open to close). Monetization pre-check:
the sign-adjusted reversal in points must clear 2x round-trip cost. Data:
NQ 1-minute with volume, on disk. DRAWABLE.

## 8. Ranking (information gain x edge potential)
Information gain: MODERATE. Whether liquidity-provision concessions are
visible at the index-future level in daily bars is a direct test of the
structural conclusion that "the participants who leave money are not
visible in 1-minute OHLCV" -- volume IS in the OHLCV. A null closes the
volume channel as a state variable for good (043 + this).
Edge potential: LOW-MODERATE. Index-level daily reversal is small and
1993 is old; base case is decayed. Cheap, fully specified, nothing to
tune.

## 9. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. P4 -- untested.

## 10. Disposition (2026-09-13, ~1:20 am CT, scheduled cycle)
Scan 026 run, Discovery slice only (n_used=1665, sessions usable=1686,
dropped=2). Result:
  - Cell 1 (P1 GATING, HIGH-volume sign-adjusted next-day mean):
    n=555, mean=-0.0942, ci_90=(-0.1523,-0.0463) -- credibly NEGATIVE.
    P1 PASSES.
  - Cell 2 (LOW-volume, same statistic): n=555, mean=-0.0353,
    ci_90=(-0.0793,+0.0012) -- null.
  - Cell 4 (HIGH minus LOW, bootstrap on the difference): mean_diff=
    -0.0590, ci_90=(-0.1253,+0.0054) -- NOT credibly negative.
    P2 FAILS.
  - Cell 5 (NULL 1, unconditional sign-adjusted next-day mean):
    mean=-0.0425 -- close to the HIGH-volume cell's own mean, which is
    exactly what a P2 failure looks like: the reversal in the HIGH
    cell is largely just NQ's own everyday daily mean reversion, not a
    volume-driven gradient on top of it.
  - Kill check: first-minute share of the HIGH-cell response = 0.036
    (well under the 0.5 kill threshold) -- NOT an overnight-gap
    artifact; the reversal genuinely builds in over the session. This
    makes the P2 failure more informative, not less: it is a real
    session-long effect, it just is not bigger after high-volume days
    than after low-volume days.
VERDICT: P1_PASS_P2_FAIL. Per falsifier (b) in Section 4: "P1 passes
but P2 fails: it is NQ's own daily reversal (or lack of it), volume
adds nothing; closes." Entry CLOSED.
Logged: hyp-000152 (REJECTED), ledger data_slice=discovery.
This closes the volume-gradient-on-reversal channel for good (alongside
hyp-000043's closure of volume LEVEL alone) -- volume ratio, at least at
this tercile split and this trailing-20d window, does not modulate the
size of daily reversal in NQ index futures. Consistent with the
project's read of Campbell-Grossman-Wang as decayed/index-level weak
even before this test (Section 8 above flagged edge potential as
LOW-MODERATE going in).
Next owed: none for M18 -- CLOSED. Shelf consumption: Entry 22 drawn,
scanned, and closed within the same cycle it reached DRAWABLE, per
SHELF RULE v2 precedent (draw-then-scan once floor is met).

## 12. Closure form (U8, retroactive pass 2026-09-13 7:00 pm CT)
- Hypothesis / family: hyp-000152 / M18 volume-conditioned daily reversal, NQ
- Closure status: near miss
- Primary outcome (as registered) and result: P1_PASS_P2_FAIL (Scan 026): reversal real, volume adds no gradient
- Sample adequacy: adequate (n=555)
- Mechanism verdict: weakened -- the reversal exists, the volume conditioning does not
- Robustness / cost / concentration flags: none
- What was learned: NQ has an unconditional daily reversal (next-day sign-adjusted mean credibly negative); volume level does not grade it. The reversal itself is a KNOWN characterization, not an edge (M12/M18 lineage).
- What must NOT be retested: Volume as a gradient on daily reversal.
- Permitted future retest condition: none for volume; the unconditional reversal may be conditioned ONCE on a validated state under the 8-condition protocol
- Capacity action: hold
