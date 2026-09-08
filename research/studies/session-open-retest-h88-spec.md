# Session-Open Retest — Frozen Spec (H88 / exp-117)

Parent finding: OBS-FINDING-007. Second test of the ATR-scaled-stop
convention adopted after H87 (research/studies/observatory-exit-convention-update.md).

## Setup

During 10:30-12:00 ET, "normal" regime days, the FIRST bar that
re-touches today's own 09:30 RTH open price after price moved >= 1x
the trailing-20-bar average range away from it:
- If close 5 bars earlier was ABOVE the open -> LONG (open as support
  in an uptrend pullback).
- If close 5 bars earlier was BELOW the open -> SHORT (open as
  resistance in a downtrend rally).

**Entry:** touch bar's close. **Stop:** entry -/+ `1.0 * daily
ATR(14)` (the new default convention). **Target:** entry +/- `1.35 *
risk`. Exit via `backtest.simulate_trade` (unmodified, same-day only).
Cost: `ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2, costed, per direction AND combined. Bootstrap mean-R-multiple
CI, N_BOOTSTRAP=3000, seed=7, 90% CI. Credible = CI entirely above zero
AND mean R-multiple net of cost >= 0.05R.

## Pre-commitment

One frozen attempt. This closes out this working session's Observatory
effort at 8 hypotheses (81-88) across 3 scans -- whatever the result,
next step is a full-session wrap-up for Jason, not a 9th candidate.
