# Monetization — hyp-000150 (M21, ECB decision volatility, 6E)

Reviewed: September 13th, ~12:45 am UTC (7:00 pm CT cycle)

## What was confirmed
6E's realized |return|/ATR14 in the hour spanning an ECB Governing
Council press conference (08:30-09:30 ET) is credibly ~3x the
unconditional hourly baseline (0.713 vs 0.179 ATR, diff +0.534, CI
+0.457 to +0.782, n=35 events). This is a genuine, confirmed volatility
fact about 6E -- the largest magnitude effect found in either the M20 or
M21 family.

## What Monetization needs to attach it to
A sizing overlay needs a BASE strategy already trading 6E, whose
position sizing or stop/target width the volatility fact would adjust.
Searched every script in this codebase that touches 6E: all of them
(study_currency_lead_signal.py, study_bond_lead_signal.py,
study_cross_asset_weekly_trend.py, study_cross_asset_short_term_reversal.py,
study_oil_lead_signal.py, study_volatility_regime.py,
observatory_information_transmission_v1.py) use 6E as a cross-asset
PREDICTOR feeding an NQ signal, or as one leg of a basket-level
characterization -- never as an instrument with its own standalone entry
logic. There is currently no 6E strategy, live or in Discovery, to size.

## Verdict
NO CREDIBLE PATH. Same disposition as M20 (EIA/CL), for the same
underlying reason: this project has not yet built a directional or
carry strategy IN 6E itself, so a volatility-sizing overlay has nothing
to attach to. This is not a failure of the finding -- it is a
characterization worth keeping. Filed as KNOWN TRUE (characterized, not
integrated), matching M20's disposition, not promoted to Validation or
Holdout (there is nothing there to validate against real capital yet).

## What would change this
If a 6E directional or carry strategy is ever built (open scope allows
it), this volatility fact becomes an immediately usable sizing input for
it, and for M20's CL fact, and for the three already-validated NQ
range-persistence facts -- four characterized volatility facts now sit
on the shelf waiting for base strategies to attach to, one per
instrument this project has data for (NQ x3, CL, 6E).
