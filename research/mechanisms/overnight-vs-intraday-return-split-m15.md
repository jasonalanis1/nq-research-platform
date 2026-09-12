# Mechanism — overnight vs intraday return split, NQ (M15, sourcing item 2c)

Written: 2026-09-12, 11:00 am CT cycle (unattended)  ·  PRE-REGISTERED
Results seen before writing: NO. No scan has been run on this scope. Written
BEFORE the scan per the v2.5 pipeline order.
Source CHANNEL: literature. Lou, Polk and Skouras (2019), "A tug of war:
Overnight versus intraday expected returns," Journal of Financial Economics
134(1), 192-213 (SSRN circulation from ~2015). Base finding for the index:
Cooper, Cliff and Gulen (2008), "Return differences between trading and
non-trading hours: Like night and day" (S&P 500 index products, 1993-2006).
Both papers say the same qualitative thing: the equity premium accrues
almost entirely in the CLOSE-TO-OPEN session; the OPEN-TO-CLOSE session
earns roughly zero or negative on average. Lou-Polk-Skouras add that the
split is a clientele effect (institutions trade intraday, other demand
arrives overnight) and that at the firm level overnight returns persist
while intraday returns reverse.

## 1. The claim
For NQ, the unconditional drift of the instrument is not spread evenly over
the day. Decompose each session day into R_night (prior RTH close 16:00 ET
-> today's 09:30 ET first RTH bar open) and R_day (09:30 open -> 16:00
close), both ATR14-normalized. CLAIM: mean(R_night) is credibly positive and
mean(R_day) is not -- the night leg carries the drift. The claim is about
the SPLIT of a known drift, not about a new state variable.

Falsifiable in one sentence: if the block-bootstrap 90% CI of
mean(R_night) - mean(R_day) includes zero on Discovery, the split is not
there in NQ and the entry closes.

## 2. Who is on the other side
Lou-Polk-Skouras: intraday demand is dominated by institutions that are
CONSTRAINED to trade in liquid hours and against a close benchmark; they
are net sellers of exposure they accumulated at the open/overnight
(and their intraday order flow reverses). Overnight demand is
news-driven and retail/foreign, arriving into an auction with thin
intermediary balance sheets -- intermediaries reluctant to carry inventory
through the overnight session require a premium to do so. The forced
participant here is the INTERMEDIARY: the constraint is overnight
inventory-holding capacity, and the footprint is a positive average
close-to-open return paid to whoever carries. Nobody is "leaving money" by
choice; the premium is compensation for a real overnight risk that daytime
books decline to hold.

## 3. Testable predictions (pre-registered, gating marked)
P1 (GATING): mean(R_night) - mean(R_day) > 0 on Discovery, block-bootstrap
  (block = 10 sessions) 90% CI excluding zero. NULL 1 is built into the
  statistic: the total drift is mean(R_night)+mean(R_day); the claim is
  that the night share is credibly larger than half. Report both legs
  and the share night/(night+day).
P2 (reported): the split is stable in the two halves of Discovery
  (2015-01 -> 2018-06 vs 2018-07 -> 2021-10). This is the DECAY check:
  the whole Discovery sample is post-Cooper (2008) and post-SSRN
  circulation of the tug-of-war paper; if the second half is flat while
  the first is not, record "decayed".
P3 (reported): the night premium is NOT concentrated in the 09:30 first
  1-minute bar. Report mean(R_night) split into 16:00 -> 09:29 (Globex)
  and the 09:29 -> 09:30 open print. See kill rule.
P4 (reported, the ONLY conditional cell): a rolling 20-session measure of
  R_night carries no information for the next R_night (lag-1 daily
  autocorrelation of R_night, CI). This is a diagnostic to confirm the
  ruling in Section 5 -- hyp-000139 already found the CONDITIONAL
  divergence claim reverts -- and is not a gating cell.

## 4. What would falsify this
(a) P1 CI includes zero: NQ has no night/day split at this ceiling -- the
    drift is diffuse. Entry closes; the learning is that the tug-of-war
    is an equity-cross-section effect, not an NQ-index effect.
(b) P1 holds but P2 shows the second half flat: recorded DECAYED. Closes.
    A second attempt would need a claim about WHEN the premium
    reappears, not a re-tune of the window.
(c) KILL RULE: if more than half of mean(R_night) sits in the 09:29->09:30
    open print (P3), the "premium" is an auction-print artifact that a
    futures holder cannot capture at the quoted bar; family terminates,
    no drift toward slower variants.
(d) The gap-day caveat: 27 quarterly roll Fridays are missing the RTH
    session in the continuous-contract file (M9 finding). Those sessions
    are EXCLUDED from both legs by construction (no 09:30 bar); the count
    is disclosed in the scan output. If the result depends on their
    exclusion it cannot -- they are ~2% of sessions -- but disclose.

## 5. Resurrection ruling (LEARN + Integrity)
Checked by NAME and by WHAT IS MEASURED:
- Gap-fade family (hyp-000012, 087, 089, 091/092, 101, 102/103/104):
  those used the SIGN of a gap as a predictor of intraday reversal.
  This measures the unconditional MEAN of each session leg. No
  conditioning on gap sign. Not a resurrection.
- hyp-000139 overnight-vs-RTH divergence, HIGH tercile (Scan 008,
  REJECTED): that was a CONDITIONAL claim -- a 20-day rolling divergence
  z-score predicting next-day divergence -- and it reverted. This entry
  makes NO conditional claim as its gate; P4 is a diagnostic that the
  unconditional split coexists with no persistence, which is exactly what
  139 found. Different measurement (level vs conditional state). Not a
  resurrection; and if P4 shows persistence, it is 139's P1 resurfacing
  and is reported, not traded.
- Overnight RANGE family (hyp-000056/057 coil; hyp-000117/118 "H116"
  range-mid drift): range magnitudes as state variables. This is a
  RETURN decomposition with no state variable. Not a resurrection.
- H118 (vwap_dist LOW drift, baseline confusion): the lesson applies
  directly -- this entry is BUILT as a comparison of two legs against
  each other, so the unconditional drift cannot masquerade as a signal.
  NULL 1 is the statistic itself.
- Turn-of-month / days-to-opex / day-of-week calendar entries: those
  conditioned on the calendar; this does not.
RULING: NEW. Enters. Attempt 1 of 2. Integrity signs at sourcing (this
document); the BLIND gate re-checks at the Statistical stage.

## 6. Instrument-choice gate
1. Leads: the instrument itself -- this is a session-level premium on
   the index. NQ (and ES) both carry it in the published record; NQ is
   the vehicle on disk.
2. Minutes not milliseconds: the effect is measured over ~17.5 hours and
   ~6.5 hours; it is a holding-period premium, not a race.
3. NQ is the cheapest liquid way to express "hold overnight, flat
   intraday" -- one contract, one round trip per day, no cash-market
   auction access needed.
4. Directional NQ. Not relative.
5. NULL 1: satisfied by construction (night vs day legs of the SAME
   drift). Not cross-index, NULL 2 does not apply.

## 7. Frozen scope (for the scan)
ONE scan, Discovery only (2015-01-01 -> 2021-10-03). Session day = the
09:30-16:00 ET RTH block; R_night = open(09:30 bar) - close(16:00 bar of
prior session), R_day = close(16:00) - open(09:30), both / ATR14 (daily
ATR from RTH bars, lagged). Sessions lacking either the 09:30 or the
16:00 bar are dropped and counted. Cells to register in SCAN_REGISTRY:
  1. mean(R_night), block-bootstrap CI (reported)
  2. mean(R_day), block-bootstrap CI (reported)
  3. mean(R_night - R_day), block-bootstrap CI  <- GATING (P1)
  4. cell 3 on the first half of Discovery (P2, reported)
  5. cell 3 on the second half of Discovery (P2, reported)
  6. share of mean(R_night) in the 09:29->09:30 open print (P3, kill)
  7. lag-1 autocorrelation of R_night with CI (P4, reported)
7 cells, one gating. Multiplicity: Sidak on the one gating cell is
trivially 1; the six reported cells are disclosed, not selected on.
Product track: DIRECTIONAL alpha (long-overnight / flat-intraday).
Realization path: TIME-BASED -- enter at the 16:00 close, exit at the
09:30 open. Holding period ~17.5 hours: passes the hours-to-days filter.
Monetization pre-check: the overnight premium in points per session must
clear 2x the round-trip cost (spread + commission) or Monetization will
close it regardless of P1 -- record the cost hurdle in the scan output.
Data: NQ 1-minute continuous file on disk. DRAWABLE.

## 8. Ranking (information gain x edge potential)
Information gain: HIGH. Either answer is a design principle for every
future directional entry -- if the drift lives overnight, any intraday
directional claim is fighting a zero- or negative-drift session and must
be measured against THAT baseline, not the daily drift; if the split is
absent, the tug-of-war literature does not transfer to NQ and the
literature channel gets re-weighted.
Edge potential: MODERATE. The published premium is a few basis points
per session; on NQ that is real money only at the contract level with
tight costs. Realistic best case is a low-Sharpe carry that the
Monetization cost hurdle may close. It is the cheapest test on the
shelf: no state variable, no thresholds, nothing to tune.

## 9. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. P4 -- untested.
