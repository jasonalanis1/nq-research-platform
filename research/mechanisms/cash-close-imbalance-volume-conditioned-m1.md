# Mechanism — Cash-close move conditioned on close-window volume -> next-morning reversal (Entry 11, map anchor M1)

Written: September 11th, 9:38 pm CT (2026-09-12 02:38 UTC), extra cycle at Jason's direction  ·  PRE-REGISTERED
Results seen before writing: NO. hyp-000110 (closing_pressure_reversal, unconditioned last-15-min reversal) was a null; its result is known and is the reason this attempt is conditioned. This is attempt 2 of 2 on the closing-move family and the LAST. Under AMENDMENT v2.5 this doc precedes the scan; after the scan it may only ADD predictions, never rewrite the claim.

## 1. The claim
Index funds, ETFs and end-of-day rebalancers must execute market-on-close; the 15:50-16:00 ET window is where their imbalance prints, and NQ futures absorb it. An abnormally HEAVY close window (volume well above its own 20-day norm for that window) marks a forced imbalance rather than ordinary two-sided trading; the price impact of a forced imbalance is partly liquidity cost, not information, so it partially reverts by the next open once the overnight session and the next morning's deep pool re-price it. hyp-000110 found no unconditioned reversal -- consistent with this claim: on ordinary closes the last-10-minute move IS information and does not revert. Prediction direction: on HIGH close-volume days, the next-morning return (16:00 -> 09:30 open, and -> 10:00) is NEGATIVELY related to the 15:50-16:00 move; on LOW close-volume days it is not.

## 2. Who is on the other side
MOC-constrained funds paying for immediacy at the one moment they are not allowed to wait. They keep doing it because their mandate is to track the close, not to minimize impact. Not unknown; the footprint is modest per day and the overnight session is thin, so Monetization must show it survives cost on an overnight hold with a measured open fill.

## 3. Testable predictions
P1. Conditioning is the claim: within the HIGH close-volume tercile, the sign-adjusted next-open return (positive = reversal of the close move) is credibly > 0; within the LOW tercile it is not. If the effect appears equally in the LOW tercile, this is hyp-000110 again and the volume story is wrong.
P2. Size dependence: within HIGH volume, the reversal is larger for large |close moves| (top half by |close_move_vs_atr|) than small -- impact scales with the imbalance.
P3. Timing: the reversal is present at the 09:30 open and does not grow materially by 10:00 -- a liquidity-cost reversal is already priced by the time the deep pool trades; if it keeps growing into 10:00 it is a slower re-pricing story.

## 4. What would falsify this
No credible sign-adjusted reversal in the HIGH close-volume tercile; or an equal reversal in the LOW tercile; or P2 reversed (small close moves revert more). Any of these closes the closing-move family for good (attempt 2 of 2).

## 5. Prediction status (updated September 11th, 9:42 pm CT, Scan 013 -- claim above unchanged)
P1 — REFUTED. HIGH close-volume tercile, next-open sign-adjusted return: n=537, mean +0.017 ATR, ci_90 [-0.031, +0.065] -- null. LOW tercile also null (-0.008). All six cells null (3 volume terciles x open / 10:00). Volume conditioning did not surface a reversal that the unconditioned test (hyp-000110) missed.
P2 — no size dependence: within HIGH, large |close move| +0.016 (null) vs small +0.018 (null).
P3 — moot (no reversal at the open to track to 10:00; 10:00 cell also null).

## 6. Verdict
CLOSED on its own pre-registered terms (Scan 013, src/market_behavior_discovery_scan_013.py, data/market_behavior_discovery_scan_013_results.json). This was attempt 2 of 2 on the closing-move family (hyp-000110 + this): the family is CLOSED FOR GOOD. LEARN: the cash-close imbalance either has no next-morning footprint in NQ at 1-minute resolution, or the proxy (close-window volume vs. norm) does not isolate forced flow from ordinary two-sided closing activity. No hypothesis ID spent (null-closure convention). State variables for the scan: `close_move_vs_atr` = (16:00 RTH close - 15:50 close) / ATR14, signed; `close_volume_vs_norm` = 15:50-16:00 volume / its trailing-20-day mean for that window; terciles of close_volume_vs_norm cut on the Discovery sample. Outcomes: next-morning return 16:00 close -> 09:30 open, and -> 10:00 close, in ATR14 units, SIGN-ADJUSTED so a reversal of the close move is positive. Cells: 3 volume terciles x 2 horizons = 6, gating = HIGH tercile at the open horizon. Windows half-open per the KNOWN FAILURE MODE. LEARN: attempt 2 of 2 on the closing-move family (hyp-000110); distinct from the gap-fade family (which conditions on the GAP, not the prior close's own imbalance). Integrity ruling at insertion: SECOND AND LAST ATTEMPT, enters only on the volume-conditioned claim.
