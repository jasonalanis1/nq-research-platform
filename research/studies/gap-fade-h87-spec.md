# Overnight Gap Fade — Frozen Spec (H87 / exp-116)

Parent finding: OBS-FINDING-006. First hypothesis in this project
deliberately designed around the monetization diagnostic's finding
(research/studies/monetization-diagnostic-round1.md): prior attempts
had real but small positive GROSS edge, wiped out by fixed cost against
too-tight a stop. This design uses a wide, ATR-scaled stop instead of
the 1-minute-bar buffer convention used in every prior Observatory
hypothesis.

## Setup

**Signal:** at the 09:30 RTH open, if |gap| (open vs. prior RTH close)
>= 0.5x the prior day's RTH range: gap DOWN -> LONG (fade), gap UP ->
SHORT (fade). One signal per day, at the open bar.

**Entry:** open bar's close (09:30 bar). **Stop:** entry -/+ `1.0 *
daily ATR(14)` (14-day average of daily RTH High-Low range, computed
from `build_daily_bars`, unmodified daily-bar source) -- a deliberately
WIDE stop relative to every prior Observatory hypothesis's ~15-21pt
intraday-buffer stops, sized in daily terms rather than 1-minute-bar
terms, per the diagnostic's cost-ratio lesson. **Target:** entry +/-
`1.35 * risk` (TARGET_R_MULTIPLE, unmodified). Exit via
`backtest.simulate_trade` (unmodified, exits by end of day if neither
touched -- no overnight hold). Cost: `ROUND_TRIP_COST_POINTS`
(unmodified, 0.75).

## Method

Step 1+2, costed, per direction AND combined. Bootstrap mean-R-multiple
CI, N_BOOTSTRAP=3000, seed=7, 90% CI. Credible = CI entirely above zero
AND mean R-multiple net of cost >= 0.05R.

## Disclosed risk (from OBS-FINDING-006)

The Observatory measurement was only clearly Promising at the 1-minute
horizon; this trade needs the move to develop and hold through a
same-day exit, which the finding's own caveat says may not happen if
the effect decays fast. A null result here would be informative either
way: whether widening the stop (this hypothesis's whole point) still
isn't enough, or whether the effect just doesn't survive past 1 minute.

## Pre-commitment

One frozen attempt. Regardless of outcome, this is the last hypothesis
of this working session's Observatory effort -- next step either way
is deciding, with Jason, whether ATR-scaled (wide) stops should become
the new default convention for future Observatory hypotheses, replacing
the 1-minute-buffer convention used in H81-H86.
