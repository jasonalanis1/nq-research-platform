# Opening-Hour Reference-Level Fade, Excursion-Derived Exits — Frozen Spec (H82 / exp-111)

## Relationship to H81 (exp-110, hyp-000081)

H81 tested the SAME behavior (opening-hour touches of upper reference
levels / overnight low) with a generic entry/stop/target convention
(buffer stop, 1.35R target) inherited from unrelated setups. It failed.
This is a genuinely different monetization design for the SAME
behavioral observation, not a retune of H81's thresholds -- per Jason's
explicit authorization: "one re-shaped monetization hypothesis,"
frozen before looking at its own result.

## Disclosure: parameters ARE informed by the Discovery sample

Per Jason's explicit guidance, this is legitimate provided it is
disclosed and the parameters are frozen BEFORE this hypothesis's own
trade-level test is run (not adjusted afterward based on its result,
and never adjusted based on Validation). The stop/target distances
below were computed from the same Discovery-slice event set as H81/the
Observatory scan, using the median 15-minute maximum adverse/favorable
excursion (MAE/MFE) -- NOT from looking at H81's trade outcomes, and
NOT re-derived after seeing this hypothesis's own result.

Computed once, frozen here:
- SHORT (upper-level touch): median 15-min MAE = 9.12 points (adverse,
  price moving up), median 15-min MFE = 10.00 points (favorable, price
  moving down). n=1282 events.
- LONG (overnight-low touch): median 15-min MAE = 8.75 points (adverse,
  price moving down), median 15-min MFE = 8.50 points (favorable,
  price moving up). n=474 events.

## Setup

Identical event detection to H81 (unchanged): first touch, 09:30-10:30,
of prior-day high / overnight high / VWAP -> SHORT; first touch of
overnight low -> LONG. Entry: touch bar's close (unchanged).

**Stop/target (the change from H81):** fixed POINT distances, not an
R-multiple of a buffer-based stop:
- SHORT: stop = entry + 9.12, target = entry - 10.00.
- LONG: stop = entry - 8.75, target = entry + 8.50.

No max-hold/timeout beyond the existing intraday exit convention
(`backtest.simulate_trade`, unmodified, exits by end of day if neither
touched). Cost: `ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2 together, costed, bootstrap mean-R-multiple CI (R defined here
as pnl_net / stop_distance, consistent with this project's R-multiple
convention elsewhere), N_BOOTSTRAP=3000, seed=7, 90% CI. Credible = CI
entirely above zero AND mean R-multiple net of cost >= 0.05R.

## Pre-commitment (binding regardless of outcome)

This is the ONE re-shaped monetization attempt this behavior earns.
Whatever the result -- pass, thin pass, or fail -- work moves to a
DIFFERENT Observatory candidate next, not a third variant of this
behavior. If this also fails, the documented conclusion is: "interesting
behavior, but not (yet) economically monetizable with a straightforward
excursion-sized rule -- closed, not further chased." This is one data
point in a planned 3-5-candidate pilot comparing Observatory-sourced
hypotheses against this project's historical intuition-sourced ones; no
single candidate's outcome should be over-interpreted before the pilot
completes.
