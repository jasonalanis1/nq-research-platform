# Gap-Down Fade, Multi-Day Hold — Frozen Spec (H91 / exp-120)

Different-angle pivot per the staff-meeting consensus: rather than
another same-day intraday variant, test whether the gap-fade behavior
(this project's only near-miss) needs more than a same-day exit to
develop. Materially different from H87/H89 (multi-day hold instead of
same-day-only exit) -- not a retune of either.

## Rationale

H87/H89's caveat (from OBS-FINDING-006) was that the Observatory's
measurement was only clearly Promising at very short (1-minute)
horizons -- consistent with a fast initial reaction that a same-day
trade structure may cut off too early relative to where the full
reversion plays out. This tests the opposite structural assumption:
give the trade multiple days to resolve, using this project's existing
multi-day walk-forward simulation mechanism (from exp-108/109) instead
of `backtest.simulate_trade`'s same-day-only exit.

## Setup

Signal: identical to H89 (gap-down open, >=0.5x prior-day RTH range) ->
LONG. **Entry:** open bar's close. **Stop:** entry - `1.0x daily
ATR(14)` (same convention). **Target:** entry + `1.35 * risk` (same
R-multiple). **Exit:** multi-day walk-forward (daily bars, matching
exp-108/109's mechanism) with a `MAX_HOLD_DAYS=10` timeout, exiting at
mark-to-market close if neither stop nor target is touched by then --
NOT same-day-only. Cost: `ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI, AND a block-bootstrap-by-segment robustness check
(reusing exp-109's technique) since multi-day trades from nearby gap
events could overlap/correlate. Credible = both CIs entirely above
zero AND mean R-multiple net of cost >= 0.05R.

## Pre-commitment

One frozen attempt. If this also fails, the gap-fade behavior is fully
closed (three attempts: H87, H89, H91) and this project moves to a
genuinely different behavior/angle next, not a fourth gap-fade variant.
