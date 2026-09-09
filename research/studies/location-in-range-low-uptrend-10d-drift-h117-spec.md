# Location-in-Range-Low, Uptrend-Conditioned, 10-Day Drift -- H117 Monetization Spec

Frozen 2026-09-09. Second live candidate from Scan 001 (Discovery Engine),
distinct from H116. Survived chronological split-sample and volatility-
regime-split checks (research/infrastructure/agent-governance-structure.md).
Mechanism Agent trend-regime test (src/mechanism_agent_trend_check.py)
found the effect REVERSES sign between trend regimes: outperforms baseline
by +74.66pts in uptrend (n=342, credible, clears cost floor), underperforms
baseline by -73.14pts in downtrend (n=193, credible, clears cost floor,
wrong direction). This is mechanistically a "buy-the-dip in an established
uptrend" story, not trend-independent mean-reversion -- so unlike H116,
this candidate is monetized as a genuinely TWO-VARIABLE conditioned spec
(location-in-range AND trend regime together), not a single-variable one.
Freezing this as its own hypothesis, not a retune of H116.

## Natural realization path
Behavior was discovered and measured as a fixed 10-trading-day forward
return, same as H116. No excursion/MAE-MFE data characterized for this
candidate. Chosen exposure: TIME-BASED EXIT, directional LONG, no stop/
target -- same convention as H116, avoids the exit-design-mismatch trap.

## Definition (direction pre-registered BEFORE this test runs)
Event: a trading day where BOTH conditions hold --
  (1) location_in_range (definition per src/market_state_primitives.py)
      falls in the LOW tercile of its own full-Discovery-sample
      distribution (frozen bucket edges, same convention as every prior
      pass -- not refit here).
  (2) trailing 60-trading-day return (close.pct_change(60).shift(1)) is
      POSITIVE (uptrend regime, frozen threshold at zero -- same
      convention as mechanism_agent_trend_check.py, not refit here).
Position: enter LONG at that day's RTH reference close. Exit at the RTH
reference close 10 trading days later (skip if the exit day falls outside
available data -- no partial trades).
Pre-specified direction: POSITIVE net return (matches the sign observed
in the uptrend-regime slice of the exploratory Mechanism Agent pass).
Cost: one round-trip transaction cost (ROUND_TRIP_COST_POINTS), applied
once per trade.
Risk unit for R-multiple: entry-day ATR(14), same convention as H116 and
the rest of this project (not a stop-distance R -- units only).

## Method
Discovery-slice only for this pass. Bootstrap 90% CI on net points and on
R-multiples (N_BOOTSTRAP=3000, seed=7). Promotion-bar fields reported, not
applied -- this is a Discovery pass, promotion requires a separate
Validation-slice prospective test after this, same pipeline as H116.

## Per protocol
This is hypothesis #1 (attempt 1 of 2) for this candidate behavior (the
two-variable location-in-range/uptrend conditioning). It is a DIFFERENT
hypothesis from H116 (which tested overnight_range_vs_atr, now closed as
a Validation-slice null) -- not a second attempt on H116's definition, and
not subject to H116's attempt count. No retuning of the tercile
definition, the trend threshold, the 10-day horizon, or the entry/exit
convention after seeing this Discovery-slice result. A pass here does NOT
mean promotion -- it proceeds to a genuine out-of-sample Validation-slice
prospective test, unmodified.
