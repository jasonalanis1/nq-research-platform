# Mechanism — Midday directional retrace of the morning move (Entry 9, map anchor M10)

Written: September 11th, 7:10 pm CT (2026-09-12 00:10 UTC), scheduled cycle  ·  PRE-REGISTERED
Results seen before writing: NO. No scan has been scoped or run on this state variable. Under AMENDMENT v2.5 this doc precedes the scan; after the scan it may only ADD predictions, never rewrite the claim.

## 1. The claim
Between ~11:30 ET (European cash close) and ~13:30 ET, NQ liquidity thins: market makers widen, the European and cross-asset flow that fed the morning is gone, and the remaining participants are disproportionately intraday momentum takers. A large morning move (9:30-11:30) is therefore carried into the lull by a shallower book than the one that started it. When depth returns at ~13:30-14:00 (US afternoon desks, MOC pre-positioning), the part of the morning move that was liquidity-thinning rather than information partially retraces. Prediction direction: the 11:30->13:30 return is NEGATIVELY related to the 9:30->11:30 return, and the relationship is stronger for larger morning moves (top |magnitude| tercile).

## 2. Who is on the other side
The counterparty is whoever chased the morning move into the 11:30 lull -- intraday momentum takers and late trend-followers paying for immediacy in a thinning book. They keep taking the trade because the morning move LOOKS like information and the lull hides the fact that it is being extended on shallow depth. Not unknown; but note the counterparty is small and intraday, which caps the size of any edge (Monetization will have to show it survives a measured round-trip cost at a 2-hour hold).

## 3. Testable predictions
P1. The retrace is CONCENTRATED in the lull window: 11:30->13:30 shows the negative relation; 13:30->16:00 does not (or shows a weaker one). If the effect is just generic intraday mean reversion it should be spread across the afternoon, not localized to the lull.
P2. The effect scales with thinning: on days where 11:30-13:30 volume is in the LOW tercile of its trailing-20-day norm, the retrace is larger than on high-lull-volume days. A liquidity mechanism must respond to liquidity; an information-reversal mechanism would not.
P3. Separability: conditioning on the validated midday-lull RANGE finding (narrow midday, hyp-000106) must NOT explain the directional effect -- the retrace must hold on both narrow- and not-narrow-midday days. If it only appears on narrow-midday days it is the range finding restated (Portfolio double-count).

## 4. What would falsify this
No negative relation between morning move and lull return in the top |morning-move| tercile; or a relation of the same size in the bottom tercile (then it is not about move size); or P2 reversed (larger retrace on HIGH lull volume -- then it is information, not liquidity); or P1 failing with the effect living in 13:30-16:00 instead.

## 5. Prediction status (updated September 11th, 9:33 pm CT, Scan 011 -- claim above unchanged)
P1 — REFUTED. HIGH |morning-move| tercile, lull 11:30->13:30: n=558, mean sign-adjusted return -0.0006 ATR, ci_90 [-0.026, +0.026] -- null. No retrace in the lull; nothing to be "concentrated". All six pre-registered cells (3 terciles x 2 horizons) null; LOW and MID terciles indistinguishable from HIGH.
P2 — not credible either way (reported, not gated). Within HIGH: low-lull-volume n=274 mean +0.021 (null), high-lull-volume n=274 mean -0.016 (null). Sign pattern matches the liquidity story but neither half clears zero, so it is not evidence.
P3 — separability could not be tested because there is no effect to separate. Exploratory note only: the narrow-midday sub-cell (n=77) showed credible CONTINUATION (mean -0.030, ci_90 below zero), the opposite of a retrace; not-narrow n=481 null. Unpredicted sub-cell, not promoted, logged to LEARN as an observation for a future freshly pre-registered generation meeting only.

## 6. Verdict
CLOSED on its own pre-registered terms (Scan 011, src/market_behavior_discovery_scan_011.py, data/market_behavior_discovery_scan_011_results.json). The falsifier in Section 4 fired: no negative relation between morning move and lull return in the top tercile. Attempt 1 of 2 on the M10 directional claim spent; a second attempt needs a claim that is not "morning move retraces in the lull". No hypothesis ID spent (null-closure convention, as Scan 006/009). State variable for the scan: `morning_move_vs_atr` = (11:30 close - 9:30 open) / ATR14, signed, terciles by |value| on the Discovery sample; outcomes: 11:30->13:30 return and 11:30->16:00 return in ATR units, sign-adjusted so a retrace is positive. Horizon resolves daily. LEARN: not the IB-breakout family, not a gap fade, not the closed opening-hour fade (hyp-000081/082 traded the first hour, this trades the lull). Integrity ruling at insertion: NEW.
