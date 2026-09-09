# VWAP-Distance-Low, 10-Day Drift -- H118 Monetization Spec

Frozen 2026-09-09. Live candidate from Scan 002. Survived chronological
split-sample AND both independent regime cuts (volatility-regime split,
trend-regime split -- src/scan_002_regime_split_check.py: consistent
direction and cost-floor pass in low-vol, high-vol, uptrend, AND
downtrend slices, the cleanest regime result of any candidate this
project's Discovery Engine has produced so far). Rediscovery check:
correlation with location_in_range, overnight_range_vs_atr, range_vs_atr,
and gap_vs_atr all near zero (|r| < 0.03); "low" bucket overlap with
location_in_range's "low" bucket is 36%, essentially the ~33% expected
under independence -- this is a genuinely novel predictor, not a
restatement of an existing finding.

## Mechanism (testable prediction, not post-hoc story)
vwap_dist_vs_atr = (RTH reference close - session VWAP) / ATR14. A day
in the LOW bucket closed well below its own session's volume-weighted
average price -- i.e. more volume traded at higher prices than the
day's eventual close, consistent with late-session selling pressure (or
an early rally that faded) leaving the close "cheap" relative to where
the day's volume actually transacted. Mechanism hypothesis: this is a
value/absorption signal -- a close that undershoots the day's own
volume-weighted fair value attracts follow-through buying over the next
several sessions as the imbalance is worked off, similar in spirit to
(but mechanically distinct from, per the near-zero correlation above)
the validated dip-buying pattern. Testable prediction: the effect should
NOT depend on the broader trend or volatility regime (a value/absorption
mechanism is about that day's own volume profile, not the market's
overall direction) -- already confirmed in the regime-split check above,
which is why this candidate is being taken to a frozen spec.

## Natural realization path
Measured as a fixed 10-trading-day forward return, same convention as
H116/H117. No excursion data characterized. Chosen exposure: TIME-BASED
EXIT, directional LONG, no stop/target -- same convention, avoids the
exit-design-mismatch trap.

## Definition (direction pre-registered BEFORE this test runs)
Event: a trading day whose vwap_dist_vs_atr falls in the LOW tercile of
its own full-Discovery-sample distribution (frozen bucket edges:
[-inf, -0.0460, 0.1471, inf] -- not refit here).
Position: enter LONG at that day's RTH reference close. Exit at the RTH
reference close 10 trading days later (skip if the exit day falls
outside available data).
Pre-specified direction: POSITIVE net return (matches the sign observed
in every exploratory pass: full sample, both split-sample halves, both
volatility regimes, both trend regimes).
Cost: one round-trip transaction cost, applied once per trade.
Risk unit for R-multiple: entry-day ATR(14), same convention as
H116/H117 (units only, not a stop distance).

## Method
Discovery-slice only for this pass. Bootstrap 90% CI on net points and
R-multiples (N_BOOTSTRAP=3000, seed=7). Promotion-bar fields reported,
not applied -- Discovery pass requires a separate Validation-slice
prospective test.

## Per protocol
Hypothesis #1 (attempt 1 of 2) for this candidate. Its own attempt
count, independent of H116/H117 (both closed, 1 attempt used each). No
retuning of the tercile definition, the 10-day horizon, or the
entry/exit convention after seeing the Discovery-slice result. A pass
here does NOT mean promotion -- it proceeds to a genuine Validation-
slice prospective test, unmodified. Given Scan 001's 0-for-2 Validation
record, a Discovery-slice pass alone is treated with the same
skepticism applied there -- no interim reporting to Jason unless this
candidate clears the full 90% promotion bar (Discovery pass AND a
genuine Validation-slice pass), per standing protocol.
