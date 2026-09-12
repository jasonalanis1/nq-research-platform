# Mechanism — fomc_initial_move_vs_atr (M3b, post-FOMC-statement continuation)

Written: September 11th, 11:10 pm CT (2026-09-12 04:10 UTC)  ·  Pre-registered
Results seen before writing: no — this doc precedes Scan 016 (not yet written or run).

## 1. The claim
When the FOMC statement (14:00 ET) surprises the market, dealers and
systematic books must re-hedge and re-position — this takes longer than the
30 minutes between the statement and the 14:30 press conference to fully
complete. The 14:30 presser more often confirms the statement's tone than
reverses it, so the initial sign-adjusted 30-minute move (14:00->14:30)
should continue, on average, through the rest of the session (14:30->16:00).
This is a statement-day-specific claim, distinct from the already-closed
CPI/NFP release-reaction family (different event, different actors) and from
the already-tested pre-FOMC drift (hyp-000111, a different 24-hour window
entirely before the statement).

## 2. Who is on the other side
Counterparty: discretionary fade traders who read the initial move as an
overreaction and position for the 14:30 presser to "walk it back" — they are
wrong on average if the continuation claim holds, providing the liquidity
dealers need to complete their re-hedging without the move stalling out.

## 3. Testable predictions
P1. Sign-adjusted (initial-move-direction-adjusted) return from 14:30 to
16:00 is credibly positive (continuation, not reversal) across all FOMC
days in the Discovery slice — this is the single pre-registered gating cell.
P2 (reported, not gating). Splitting by whether the initial 14:00->14:30
move was large (above median |move|/ATR) or small: the continuation effect
should be stronger following a larger initial move (more re-hedging left to
do), not weaker.

## 4. What would falsify this
Sign-adjusted 14:30->16:00 return not credibly positive (null), or credibly
negative (a true reversal pattern — the presser walks back the statement
more often than it confirms it).

## 5. Prediction status
P1 — REFUTED (clean null, adequately powered per the pre-registered scope)
— Scan 016: n=52 usable FOMC days (of 53 registered), sign-adjusted
14:30->16:00 continuation mean -0.0126 ATR, ci_90 [-0.1381,+0.1076] — not
credibly positive, and if anything trivially negative (not credibly so
either). P1_FAIL.
P2 — not tested — pre-registered scope: read only if P1 passes; it did not.

## 6. Verdict
REFUTED at Discovery, clean null. n=52 essentially matches the ~55
estimated at scoping (this was NOT an underpowered sample the way the
detectable-effect caveat anticipated it might be) — the pre-statement
continuation story does not hold up: the 14:30 presser does not reliably
extend the initial 30-minute move through the close. Attempt 1 of 2 on
this mechanism closed. No hypothesis id spent (Discovery-stage scan did not
clear the credible+cost-floor screen). LEARN entry filed under FAILED
(clean null).
