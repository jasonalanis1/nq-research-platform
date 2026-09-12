# Mechanism — market intraday momentum, first 30 min -> last 30 min, NQ (M16, sourcing item 2e)

Written: 2026-09-12, 11:00 am CT cycle (unattended)  ·  PRE-REGISTERED
Results seen before writing: NO.
Source CHANNEL: literature. Gao, Han, Li and Zhou (2018), "Market intraday
momentum," Journal of Financial Economics 129(2), 394-414 (SSRN ~2015).
Finding on SPY 1993-2013: the first half-hour return (measured from the
prior close to 10:00 ET) positively predicts the LAST half-hour return
(15:30-16:00), with the middle of the day carrying little predictive
content; the effect is stronger on high-volatility, high-volume and
macro-news days and survives transaction costs in their sample.

## 1. The claim
For NQ, sign(R_first30) predicts sign(R_last30) on the same session, where
R_first30 = prior 16:00 close -> 10:00 ET and R_last30 = 15:30 -> 16:00,
both / ATR14. CLAIM: mean(sign-adjusted R_last30 | R_first30 in the top or
bottom tercile) is credibly positive, and the effect is specifically
first-30 -> last-30, NOT a generic "day so far -> close" continuation.

Falsifiable in one sentence: if sign-adjusted last-30 given an extreme
first-30 has a block-bootstrap 90% CI including zero on Discovery, or if
the first-30 coefficient is not credibly different from zero once the
10:00 -> 15:30 return is included, the claim is not there and the entry
closes.

## 2. Who is on the other side
Two constrained groups per Gao et al.: (a) LATE-INFORMED traders who see
the morning move/news but only act at the close (end-of-day rebalancers,
mutual funds executing at NAV, ETF creation/redemption flows) -- their
constraint is a schedule; (b) INFREQUENT REBALANCERS (vol-targeters,
risk-parity) who reset at the close in the direction the day's realized
variance and drift imply. Both deliver flow into the last half-hour that
is CORRELATED with the morning's information, and the intermediaries
absorbing it are paid a small continuation. The footprint is a same-sign
last-30 return, resolved at minute scale because the flow is executed on
a closing schedule, not a race.

## 3. Testable predictions (pre-registered, gating marked)
P1 (GATING): sign-adjusted R_last30 given R_first30 in the TOP or BOTTOM
  tercile (terciles frozen on Discovery) has a block-bootstrap 90% CI
  excluding zero and positive. Reported alongside: NULL 1 -- the same
  statistic on the MIDDLE tercile and unconditional mean(R_last30).
P2 (reported, separation from M13 / generic momentum): OLS of R_last30 on
  R_first30 AND R_mid (10:00 -> 15:30). Claim: the first-30 coefficient
  is credibly positive WITH R_mid in the regression. If only R_mid
  carries the sign, the effect is day-so-far continuation (M13's
  territory, or generic momentum), not Gao et al., and the entry is
  recorded as "confounded, not confirmed".
P3 (reported): stronger on high trailing-volatility sessions (ATR14 in
  its top Discovery tercile) than low -- the paper's own conditioning.
P4 (reported): stable across Discovery halves (decay check; the whole
  sample is post-SSRN circulation).

## 4. What would falsify this
(a) P1 CI includes zero: no first-to-last continuation in NQ. Closes.
(b) P1 holds, P2 fails: the signal is the day's momentum, not the first
    half-hour's information; this is a confound, not a pass. Closes as
    "confounded"; a second attempt would need to isolate a flow the
    morning move triggers that the mid-day move does not.
(c) KILL RULE: if more than half of the sign-adjusted last-30 response
    sits in the 15:59 -> 16:00 bar (the closing print), the effect is an
    auction artifact; family terminates.
(d) 27 roll-Friday sessions lack RTH bars and are dropped, count disclosed.

## 5. Resurrection ruling (LEARN + Integrity)
Checked by NAME and by WHAT IS MEASURED:
- IB / opening-range breakout family (hyp-000011, 028, 065, 135, all
  REJECTED; closed): entered on a RANGE BREAK of the first hour, held
  through the day. This conditions on a RETURN tercile and measures ONLY
  the last 30 minutes, skipping the middle. Different predictor
  construction, different outcome window. Not a resurrection.
- hyp-000045 intraday_momentum_burst_15min_continuation (REJECTED):
  immediate 15-minute continuation after a burst, any time of day. This
  is a fixed-window, session-anchored claim with a five-hour gap between
  predictor and outcome. Not a resurrection.
- hyp-000076 opening_volume_imbalance (REJECTED): 9:30-10:00 VOLUME
  imbalance -> rest of day. Different predictor (volume, not return) and
  different outcome (rest of day, not last 30). Adjacent; not a
  resurrection.
- hyp-000052 intraday_trend_day_shape_first_hour_mae (PROMISING, not
  closed): trend-day shape diagnostic; not a claim on the last 30 min.
  Noted, no conflict.
- M13 LETF close rebalance (PARKED): the CONFOUND, by design. Separated
  by P2 (first-30 vs mid-day coefficients). Both may be true.
- M1 / hyp-000110 closing-pressure (CLOSED FOR GOOD): used the close move
  as a PREDICTOR of the next morning. This predicts the close move.
RULING: NEW. Enters. Attempt 1 of 2. Integrity signs at sourcing.

## 6. Instrument-choice gate
1. Leads: the index future carrying the largest close-scheduled flow
   relative to its liquidity -- ES/SPY in the paper; NQ carries the same
   flow classes (QQQ NAV/creation, vol-targeters).
2. Minutes not milliseconds: the flow is scheduled into a 30-minute
   window, not raced.
3. NQ is a fine vehicle; ES would be the paper's own. NQ-only is
   acceptable because the claim is not instrument-ordered (unlike M13).
4. Directional NQ. Not relative.
5. NULL 1: middle-tercile and unconditional last-30 mean reported
   beside the gating cell. Not cross-index.

## 7. Frozen scope (for the scan)
ONE scan, Discovery only. R_first30 = open(09:30 bar)... no: prior 16:00
close -> 10:00 ET close, per Gao et al.; R_mid = 10:00 -> 15:30; R_last30
= 15:30 -> 16:00; all / ATR14 (lagged). Terciles of R_first30 frozen on
Discovery. Cells to register in SCAN_REGISTRY:
  1. sign-adjusted mean(R_last30 | first30 top OR bottom tercile), block
     bootstrap CI  <- GATING (P1)
  2. mean(R_last30 | middle tercile) (NULL 1, reported)
  3. unconditional mean(R_last30) (NULL 1, reported)
  4. OLS coefficient on R_first30 with R_mid included, CI (P2, reported)
  5. OLS coefficient on R_mid, CI (P2, reported)
  6. cell 1 on high- vs low-ATR14 tercile sessions (P3, reported, 2 cells)
  7. cell 1 on Discovery halves (P4, reported, 2 cells)
  8. share of cell 1 in the 15:59->16:00 bar (kill rule)
10 cells, one gating. Product track: DIRECTIONAL alpha. Realization:
TIME-BASED (15:30 in, 16:00 out, ~30 min hold; passes the filter).
Monetization pre-check: the sign-adjusted last-30 premium in points must
clear 2x round-trip cost. Data: NQ 1-minute file on disk. DRAWABLE.

## 8. Ranking (information gain x edge potential)
Information gain: MODERATE-HIGH. Together with M15 it maps WHERE in the
session NQ's predictable return lives (overnight leg, morning
information -> close). A null closes the last open "session-anchored
continuation" claim in the literature channel; P2 either way tells us
whether close-window flow is information-driven or momentum-driven,
which is the design fact M13/M14 depend on.
Edge potential: MODERATE. Gao et al. report the effect survives costs on
SPY; on NQ a 30-minute hold with tight costs is realistic, but the
paper's sample ends 2013 and decay is the base case.

## 9. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. P4 -- untested.
