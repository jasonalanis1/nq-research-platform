# Mechanism — NQ-ZN correlation breakdown -> 1-3 day NQ return (Entry 10, map anchor M11)

Written: September 11th, 9:35 pm CT (2026-09-12 02:35 UTC), extra cycle at Jason's direction  ·  PRE-REGISTERED
Results seen before writing: NO. No scan has been scoped or run on this state variable. Under AMENDMENT v2.5 this doc precedes the scan; after the scan it may only ADD predictions, never rewrite the claim.

## 1. The claim
Balanced (60/40) and risk-parity books hold NQ-type equity exposure against a Treasury hedge (ZN) and size the equity leg on the assumption the two move opposite. Their risk engines re-estimate that co-movement on rolling windows. When the rolling correlation flips from its usual negative toward positive -- the hedge stops hedging -- realized portfolio volatility jumps and the books must cut gross exposure over the next few sessions. Equity is the leg they cut. Prediction direction: when `nq_zn_corr_20d` is in its HIGH (most positive) tercile, NQ's forward 1-3 day return is NEGATIVE relative to the LOW-tercile state; the deleveraging is a flow, not a forecast, so it should show up as a drift over 1-3 days rather than a one-day jump.

## 2. Who is on the other side
Leveraged multi-asset books (risk-parity, vol-target balanced funds) de-risking on a schedule set by their own risk models, not on price -- they sell because their measured correlation rose, regardless of where NQ trades. Not unknown; the risk is that the footprint is small in NQ specifically (they cut broad equity, ES first) and slow, so Monetization will have to show it survives cost at a 1-3 day hold. Distinct from the closed lead-lag family (hyp-000031/034/035), which asked whether ZN's OWN move predicts NQ; this asks about the co-movement STATE.

## 3. Testable predictions
P1. State, not lag: HIGH corr-tercile forward NQ return (1d, 2d, 3d) is below the LOW-tercile return, credibly. As a placebo, ZN's own prior-day return added as a second conditioner should NOT change the result -- if it does, this is the lead-lag family in disguise.
P2. Drift shape: the effect grows from 1d to 3d (a deleveraging flow), not concentrated in day 1 (a repricing).
P3. Regime robustness: the effect holds within both halves of the Discovery slice chronologically AND within both VXN-level halves; a risk-model flow should not depend on the vol regime, though its size may.

## 4. What would falsify this
No difference between HIGH and LOW corr-tercile forward returns at any horizon; or an effect that disappears once ZN's prior-day return is controlled (lead-lag resurrection); or an effect concentrated entirely in day 1 with no 2-3 day drift; or sign that flips between chronological halves.

## 5. Prediction status (updated September 11th, 9:36 pm CT, Scan 012 -- claim above unchanged)
P1 — NOT CONFIRMED (fails the pre-registered bar). HIGH corr-tercile forward NQ return: 1d +0.032 [-0.034,+0.094], 2d +0.067 [-0.023,+0.154], 3d +0.085 [-0.021,+0.192] ATR -- null at every horizon. HIGH-minus-LOW: 1d -0.043 [-0.140,+0.047], 2d -0.081 [-0.214,+0.049], 3d -0.135 [-0.291,+0.019] -- never credibly negative. The 3d difference is a near-miss (upper bound +0.019); under this project's rules a near-miss is a fail and is not retuned. Placebo not run (no effect to protect).
P2 — direction and SHAPE matched (HIGH is the lowest tercile at every horizon and the gap widens 1d -> 3d), but with no credible P1 this is consistent-with, not evidence-for. Recorded so a future generation meeting knows the sign was right.
P3 — not run (no credible effect to test for robustness).
Context: LOW and MID terciles are credibly positive at all horizons -- that is the Discovery-slice equity drift (2015-2021), not a finding.

## 6. Verdict
CLOSED on its own pre-registered terms (Scan 012, src/market_behavior_discovery_scan_012.py, data/market_behavior_discovery_scan_012_results.json). Attempt 1 of 2 on the M11 co-movement claim spent. LEARN note: sign and drift shape agreed with the deleveraging story, magnitude did not clear; if a second attempt is ever made it needs a genuinely different claim (e.g. a forced-flow proxy rather than the correlation state itself), not a longer window or a finer bucket. No hypothesis ID spent (null-closure convention). State variable for the scan: `nq_zn_corr_20d` = rolling 20-day Pearson correlation of NQ and ZN daily RTH close-to-close returns (ZN from data/ZN_1min_databento_2026-09-07.csv, RTH session aligned to NQ's), terciles cut on the Discovery sample; outcomes: NQ forward 1d, 2d, 3d close-to-close return in ATR14 units. Cells: 3 terciles x 3 horizons = 9, gating claim HIGH-minus-LOW at each horizon (P1). Daily n. LEARN: not the lead-lag family (031/034/035, closed); not the cross-asset weekly trend/reversal baskets (021/022, closed) which used ZN as a traded leg, not as a state. Integrity ruling at insertion: NEW. Boundaries half-open per the KNOWN FAILURE MODE.
