# H118 execution approximation — FROZEN SPEC

Frozen 2026-09-10 by Jason's decision. Queue item 0a, previously
BLOCKED pending this answer, is now unblocked.

This document freezes HOW H118's signal is transacted. It changes
nothing about what H118 is, what it predicts, or when it is judged.

## The problem being solved

H118's research measures entry AND exit at the RTH reference close.
That price cannot be transacted: by the time the close exists, the
opportunity to trade at it has passed. Every implementation is
therefore an APPROXIMATION of the research assumption, and the
distance between the two is a real cost that must be measured rather
than assumed away.

## The decision

Two options were put to Jason on 2026-09-10:

  A. Market-on-close order. Submitted before the exchange cutoff,
     filled at the official close. Tracks the research assumption most
     closely. Costs: commits before the price is known, a hard cutoff
     that cannot be missed, and broker support for MOC on micro
     futures is not confirmed for this account.

  B. Market order shortly before the close. Simple, always available,
     no cutoff to miss. Cost: fills NEAR the close, not AT it, by an
     amount that varies day to day.

JASON CHOSE B.

Rationale as put to him and accepted: B is simpler to build, works
with any broker, and cannot fail silently. Option A would require the
same deviation measurement anyway, so A's closer tracking does not
remove the measurement obligation — it only shrinks the number being
measured, and it does so at the price of a dependency this account has
not confirmed.

## Frozen rule

    ENTRY: single market order at 15:58:00 America/New_York on the
           signal date.
    EXIT:  single market order at 15:58:00 America/New_York on the
           exit date (signal date + 10 trading days, per the frozen
           H118 spec — unchanged).
    SIZE:  1 MNQ. Unchanged.

A single deterministic timestamp, not a window. A window invites
discretion, and discretion is unmeasurable. 15:58:00 is two minutes
before the 16:00 RTH close, chosen to be far enough inside the session
that liquidity is normal and near enough that the fill tracks the
reference.

## Mandatory measurement — the point of this document

Every fill records, at the time of the fill and never reconstructed
later:

  - intended reference price  (that day's official RTH close)
  - actual fill price
  - deviation in points       (fill - reference, signed)
  - deviation in R            (deviation / ATR14 at signal)
  - side                      (entry or exit)
  - timestamp of order submission and of fill

The deviation is reported per trade and as a distribution at the
review point. It is NEVER assumed to be zero, and never silently
folded into the result.

WHY THIS MATTERS FOR THE VERDICT. H118's working effect is ~0.40R,
about 147 points. If the approximation costs an average of 2 points
per side, that is 4 points round trip — under 3% of the effect, and
tolerable. If it costs 15 points per side, that is 30 points round
trip, a fifth of the effect, and the economics change materially. We
do not currently know which of those worlds we are in. That is
precisely why it is measured rather than assumed.

## What this does NOT change

  - The pre-registered review point stays 40 resolved trades AND 12
    months. It does not move, tighter or looser, for this or any other
    reason.
  - H118's working effect stays re-baselined at Holdout ~0.40R
    (floor 0.14R). The 0.62R Discovery figure is never quoted.
  - H118 remains at Forward Validation and remains OUTSIDE automated
    session scope. Sessions flag, they do not act.
  - No broker account, no capital, no live authorization is implied by
    this document. This freezes a rule for the signal engine and the
    later paper-trading stage; nothing here authorizes a trade.

## Next

Queue item 0a is unblocked and this spec is its input. The signal
engine (item 0b) generates the order intent at the frozen timestamp;
the execution-qualification stage later measures whether the fills
behave as this document assumes. Building the engine is in scope for
automated sessions ONLY insofar as it does not touch H118's ledger
rows or its forward-validation log — the SCOPE BOUNDARY is unchanged.
