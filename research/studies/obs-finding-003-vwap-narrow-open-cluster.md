# OBS-FINDING-003: VWAP Touch, Narrow-Regime, Open Bucket

Per the Behavioral Finding protocol. Measurement only -- no trade design.

## Definition

Event: first touch (09:30-10:30 ET, "open" bucket) of session VWAP,
"narrow" volatility regime day (prior day's range in the bottom
percentile band, per volatility_conditioning's existing classification).
Horizon 30min. n=295. Source: Observatory v1 scan.

## Why this is a distinct candidate, not a variant of #1

OBS-FINDING-001 (open-bucket cluster used for H81/H82) did not
condition on volatility regime -- it pooled all regimes. This cell is
regime-SPECIFIC (narrow days only) and was explicitly excluded from
H81/H82 for that reason. Testing it separately asks a different
question: does the VWAP-fade effect concentrate in narrow-range days
specifically (a "compressed range -> mean-reversion" story), or is it
regime-independent? That's a genuinely different mechanism hypothesis,
not a retune of the same one.

## Perspectives

- Path-to-Profitability Advisor: narrow-regime days are exactly the
  ones where this project's two CONFIRMED findings already say next-day
  range compresses further -- if VWAP-fade is also concentrated there,
  that's a coherent, mechanistically-connected story worth testing.
- Market Behavior Advisor: n=295 is a reasonable size, but this is the
  weakest-instrument cell of the two open-bucket candidates tried so far
  (single level, single regime, single horizon) -- treat a pass here
  with normal skepticism, not extra credit for the "coherent story."
- Claude: agree. Proceeding to a hypothesis spec, single reference
  level (VWAP), narrow regime filter, 30-min-informed target only
  (no MFE/MAE reuse -- same H81-style generic convention as H83, to
  keep results comparable across the pilot).

## Judgment

Plausible, narrower-scoped version of the fade mechanism, worth testing
as its own candidate given the mechanistic tie to the project's two
confirmed volatility findings. Not yet independently re-validated.

## Status

OPEN -- proceeding to hypothesis spec (H84).
