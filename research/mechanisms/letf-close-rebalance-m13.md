# Mechanism — Leveraged-ETF close rebalancing (M13)

Written: September 12th, ~9:25 am CT  ·  Pre-registered  ·  Sourcing entry, queue v2 item 2a
Results seen before writing: no. No scan exists. Scan waits for RTY and ES data (see Section 7) and Jason's go.

## 1. The claim
Leveraged and inverse ETFs must rebalance their exposure at the close, every
day, in the DIRECTION of that day's index return. For a fund with leverage L
and assets A, the end-of-day trade in underlying-dollar terms is
(L^2 - L) * A * r, where r is the day's return (Cheng and Madhavan 2009).
For L = +3 that is 6*A*r; for L = -3 it is 12*A*r; even L = -1 gives
2*A*r. Every leveraged AND every inverse fund buys into the close on an up
day and sells into the close on a down day. This is not a view; it is the
product's prospectus. The flow is positive feedback, concentrated in the
last minutes of the session, and its size is computable in advance from
public AUM and the day-so-far return.

Prediction: the last 30 minutes of the session continue the day-so-far
direction, more so when the day-so-far move is large and when the fund
complex tracking that index is large relative to the index future's close-
window liquidity.

## 2. Who is on the other side
Liquidity providers and closing-auction participants who take the other
side of a mechanical, informationless order and are paid by the partial
reversal that follows once the flow clears (that reversal is the next-
session claim, reported not gating). The LETF sponsor cannot wait, cannot
work the order over the next day, and cannot choose the direction.

## 3. Testable predictions
P1 (GATING). Sign-adjusted close-window return, in ATR units --
   sign(r_day) * (close_16:00 - close_15:30) / ATR14, where r_day is the
   9:30-15:30 return -- is credibly positive in the TOP tercile of
   |r_day|, measured against NULL 1 (minus the all-days sign-adjusted
   close-window mean, which for a sign-adjusted measure is near zero but
   is reported anyway).
P2 (reported, the mechanism's fingerprint). The effect is ORDERED across
   instruments by rebalance flow as a share of close-window liquidity:
   RTY > ES >= NQ. It is also larger in the second half of the Discovery
   slice than the first, because LETF AUM grew several-fold 2015-2021.
   Neither ordering is predicted by generic intraday momentum.

## 4. What would falsify this
(a) P1 not credible after NULL 1.
(b) P1 credible but FLAT across instruments and flat across the AUM growth
    -- then what was measured is generic intraday momentum (Gao et al.,
    queue item 2b), not LETF flow, and this entry closes in favor of that
    one. This is the pre-registered discriminator between two claims that
    predict the same late-day continuation.
(c) The effect lives only in the 15:59-16:00 bar: untradeable from these
    bars, family terminates under the kill rule.

## 5. Resurrection ruling (LEARN + Integrity)
Adjacent closed families, checked by name and by what is measured:
- hyp-000110 closing_pressure_reversal and M1 / Scan 013 (close-window move
  conditioned on close volume -> next-morning reversal): those used the
  close-window move as the PREDICTOR of what follows. This uses the DAY-SO-
  FAR return to predict the close-window move itself. Different direction of
  inference, different participant (index funds at MOC vs leveraged-fund
  sponsors). Not a resurrection.
- hyp-000076 opening_volume_imbalance (9:30-10:00 -> rest of day): opening
  window, unrelated mechanism.
- Intraday momentum (queue 2b): NOT closed, and it is the confound -- see
  Section 4(b). Both may be true; the instrument/AUM ordering separates them.
RULING: NEW. Enters. Attempt 1 of 2.

## 6. Instrument-choice gate
1. Leads: the index future whose LETF complex is largest relative to its own
   close liquidity -- RTY (TNA/TZA/UWM/TWM/RWM vs a thin future).
2. Minutes not milliseconds: the flow is executed over the closing window
   and the auction, by sponsors who must finish by the print; it is not a
   race, it is a schedule.
3. NQ is NOT necessarily the vehicle. If the effect lives in RTY, trade
   M2K/RTY. That is the point of open scope.
4. Directional, in the day's direction, per instrument. Not relative.
5. Survives NULL 1 by construction (sign-adjusted); reported anyway.

## 7. Frozen scope (for the scan, once data is on disk)
ONE scan, instrument as a factor: RTY, ES, NQ. Per instrument: terciles of
|r_day| frozen on Discovery; outcome = sign-adjusted 15:30-16:00 return /
ATR14; reported: 1st-half vs 2nd-half Discovery split (AUM growth), and
next-session sign-adjusted open-to-close (reversal, P2-type). 3 instruments
x 3 terciles = 9 gating-side cells + 3 x 2 reported = 15 cells to register.
Data: NQ on disk. RTY and ES 1-minute bars NOT on disk -- queue v2 item 3.
Do not run NQ alone first: that would spend the family's one shot on the
instrument where the mechanism predicts the WEAKEST effect. LETF AUM
history (issuer NAV files + shares outstanding) is needed only for the
flow-size gradient, not for P1; assemble it before the scan if cheap,
otherwise P2's AUM test uses the time split as the proxy.
Kill rule per Section 4(c). Publication: Cheng and Madhavan 2009 (J. of
Investment Management); widely known since ~2010-2012 -- expect decay in ES
and NQ; that is why RTY is the first-order test.

## 8. Prediction status
P1 -- untested. P2 -- untested. Waiting on RTY/ES data and Jason's go.
