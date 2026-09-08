# Volatility-Conditioned Position Sizing — Spec

## Why this, not another hypothesis search

Per the 2026-09-08 staff-meeting conclusion (all three views converged):
stop searching for new directional bar patterns for now (65+ tested, 0
survivors, confirmed exhausted at both daily and 60-min resolution this
session); instead make the two confirmed volatility facts
(range-contraction, overnight coil) into something actually usable. This
is that next deliverable, scoped narrowly to avoid the $-spend and
account-setup decisions that come with real execution infrastructure
(Tradovate) — those stay a separate, later ask.

## What this is

A pure risk-management transform, not a new strategy and not a
hypothesis subject to the 90%-CI promotion bar — it makes no return
claim, only a sizing recommendation conditional on the already-confirmed
range prediction. Standard, well-established practice (inverse
volatility sizing): trade smaller on days expected to have a wider
range, trade larger on days expected to have a narrower range, so that
expected dollar risk per trade stays roughly constant regardless of the
day's volatility regime.

## Method

`position_size_multiplier(expected_range_multiplier) = 1 / expected_range_multiplier`,
clipped to `[MIN_SIZE_MULT, MAX_SIZE_MULT] = [0.5, 1.5]` so a single
stacked condition (e.g. both prior_day_wide and coiled_overnight firing
at once) can't push size to an extreme on a fact whose own Validation CI
is not infinitely tight. Fed directly from
`volatility_conditioning.get_volatility_conditioning()`'s
`expected_range_multiplier` output — no new statistical test needed
since it's an algebraic transform of an already-Validation-confirmed
number, not a new claim about returns.

## Honest disclosures

- This does NOT create or resurrect a directional strategy. It only
  answers "given a signal from elsewhere, how many contracts," never
  "should I take this trade."
- The 0.5–1.5x clip is a judgment call (documented, not tuned against
  any backtest) meant to keep the tool from ever silently taking a huge
  size bet on a fact whose Validation-slice CI, while credible, is not
  perfectly tight (coil: 0.83–0.96; narrow: 0.89–1.00; wide: 1.02–1.14).
- Its real economic value — does risk-normalized sizing actually improve
  a live strategy's risk-adjusted return, net of the fact that NQ
  contracts aren't fractionally sizable in practice below 1 — is
  UNTESTED and cannot be tested against a strategy this project doesn't
  have (no promoted directional signal exists yet to size).
- Wiring this into real order sizing requires the execution-infrastructure
  decision (Tradovate account, webhook bridge) already parked as a
  separate, not-yet-started track — this spec stops at the sizing
  function itself.
