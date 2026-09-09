# Overnight-Range-Moderate 10-Day Drift -- H116 Monetization Spec

Frozen 2026-09-09. First monetization attempt for the Discovery
Engine's first surviving candidate: overnight_range_vs_atr (mid
tercile) -> positive 10-trading-day forward return, discovered in
Scan 001 and surviving four independent exploratory checks
(chronological split-sample, volatility-regime split, trend-regime
split, and a separability check confirming this return effect is not
a byproduct of the already-validated overnight-coil RANGE finding on
the same predictor). Governed by
research/infrastructure/agent-governance-structure.md's Monetization
Agent standard and the existing Research Integrity Protocol
(chronological Discovery/Validation/Holdout, frozen specs, 2-attempt
limit, no retuning after a null).

## Natural realization path (asked before any exit structure, per the
exit-design-mismatch LEARN entry)

The behavior was discovered and measured AS a fixed-horizon return
(close-to-close over the next 10 trading days), not as an excursion
with a natural stop/target level -- unlike OBS-FINDING-012 (pre-NFP
drift), where MAE/MFE excursion data existed and a stop/target
structure was tried (and failed twice, H114/H115). No excursion data
has been characterized for this candidate. Forcing a stop/target here
would repeat exactly the mismatch the LEARN entry warns against.

Chosen exposure type: TIME-BASED EXIT, directional position. Enter
long at the RTH close of the signal day (the day whose overnight
range falls in the mid tercile), hold through 10 trading days, exit
at that day's RTH close. No stop, no target -- the exposure matches
how the effect was actually measured. This is the simplest exposure
type available in the Monetization Agent's menu and the one directly
implied by the discovery methodology itself.

## Definition (direction pre-registered BEFORE this test runs)

Event: a trading day whose overnight_range_vs_atr (overnight Globex
range / trailing ATR(14), same definitions as
src/market_state_primitives.py) falls in the MIDDLE tercile of its own
full-Discovery-sample distribution (frozen bucket edges, identical to
Scan 001 and every exploratory pass since -- not refit here).

Position: enter LONG at that day's RTH reference close. Exit at the
RTH reference close 10 trading days later (skip if the exit day falls
outside available data -- no partial trades).

Pre-specified direction: POSITIVE net return (matches the sign
observed in every exploratory pass to date: Scan 001 full sample,
both split-sample halves, both volatility regimes, both trend
regimes).

Cost: one round-trip transaction cost (ROUND_TRIP_COST_POINTS,
project-standard convention) applied once per trade.

Risk unit for R-multiple: entry-day ATR(14), consistent with this
project's existing ATR-normalized cost-aware convention used
everywhere else (not a stop-distance R, since there is no stop --
this is a magnitude-of-move-relative-to-typical-daily-range
convention, used here purely as the promotion bar's required units,
not as a risk-management level).

## Method

Discovery-slice only for this pass (per protocol: promotion requires
a SEPARATE Validation-slice prospective test after this). Bootstrap
90% CI on net return (points) and on R-multiples (N_BOOTSTRAP=3000,
seed=7, same convention as every other study in this project).
Promotion-bar fields reported (not applied yet -- this is a Discovery
pass, promotion requires the full pipeline): 90% CI entirely above
zero, and economically meaningful (>=0.05R mean).

## Per protocol

This is hypothesis #1 (attempt 1 of 2) for this candidate behavior.
No retuning of the tercile definition, the 10-day horizon, or the
entry/exit convention after seeing this Discovery-slice result -- a
null here means either (a) a second, differently-motivated attempt
per the 2-attempt limit, or (b) closing the line and logging the
failure mode to LEARN, exactly like every other line in this project's
history. A pass here does NOT mean promotion -- it means the
candidate proceeds to a genuine out-of-sample Validation-slice
prospective test, unmodified, per the existing pipeline.
