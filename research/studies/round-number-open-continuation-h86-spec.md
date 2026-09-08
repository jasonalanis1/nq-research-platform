# Round-Number Open Continuation — Frozen Spec (H86 / exp-115)

Parent finding: OBS-FINDING-005. First continuation-style (not fade)
candidate tried in this project, from either the Observatory or the
historical hypothesis set.

## Setup (directional, per the drift-artifact caveat in the finding)

During 09:30-10:30 ET, "normal" volatility regime days only, the FIRST
bar whose High/Low range touches the nearest 50-point round level
(recomputed at each bar from price already seen, no lookahead):
- If price in the preceding 5 bars was net UP (close[i] > close[i-5]) ->
  LONG (continuation of the up-move through the round level).
- If price in the preceding 5 bars was net DOWN (close[i] < close[i-5])
  -> SHORT (continuation of the down-move through the round level).
- No signal if flat (close[i] == close[i-5]).

This directly tests whether the effect is a genuine momentum-through-
round-number interaction (should work in both directions) or a
same-period upward-drift artifact (would only work long).

**Entry:** touch bar's close. **Stop:** touch bar's extreme against the
trade direction +/- `1.5 * average 1-minute bar range over the trailing
20 bars` (same buffer convention as every other Observatory hypothesis
this project has run). **Target:** entry +/- `1.35 * risk`
(TARGET_R_MULTIPLE, unmodified). Exit via `backtest.simulate_trade`
(unmodified). Cost: `ROUND_TRIP_COST_POINTS` (unmodified, 0.75).

## Method

Step 1+2, costed, per direction AND combined. Bootstrap mean-R-multiple
CI, N_BOOTSTRAP=3000, seed=7, 90% CI. Credible = CI entirely above zero
AND mean R-multiple net of cost >= 0.05R.

## Pre-commitment

If only the long side passes and the short side fails/is thin, that is
read as evidence FOR the drift-artifact concern, not a reason to keep
only the long side and call it a win -- the finding's own caveat
requires both directions to hold up for this to be treated as a real
round-number effect. One frozen attempt; regardless of outcome this
closes candidate #5 of the (now extended) Observatory pilot.
