# Volatility Conditioning Module — Design Note (2026-09-08)

## What this is

Not a new hypothesis test. This builds a reusable, documented tool out
of the project's two Validation-confirmed volatility-persistence facts
(the only two findings in the project's history to survive a
prospective test): range-contraction (hyp-000046/048) and overnight
coiling (hyp-000056/057). Per Jason's direction after the COT-
positioning line closed: stop generating new directional hypotheses for
now, and turn what's already confirmed into something usable.

## What it is NOT

Not itself a trading strategy, not subject to the 90%-CI promotion bar
(there's no P&L claim being made here), and not live-authorized for
anything. It is a conditioning/context module: given a date, tell you
whether today is expected to be quieter or louder than normal, using
only the two facts that have actually survived out-of-sample testing.
Any future strategy that wants to use this as a sizing/stop-width input
would need its OWN frozen spec and its OWN Discovery/Validation test of
whether using it that way actually helps -- this module only computes
the honest, already-confirmed numbers; it does not claim they improve
any particular strategy's economics.

## What it computes, and with which numbers

Uses VALIDATION-slice numbers throughout (not Discovery), since this
project's own effect-size-inflation diagnostic showed Discovery numbers
run larger than what survives -- the honest, load-bearing numbers are
the ones that were actually confirmed out-of-sample:

- **Prior-day range regime** (hyp-000048, reusing
  `study_intraday_behavior_batch1.build_daily_frame`'s narrow/wide
  classification unmodified): narrow prior day -> today's range ratio
  ~0.94 (Validation ci_90 0.888-0.998); wide prior day -> ~1.08
  (Validation ci_90 1.020-1.143); neither -> 1.0 (no adjustment, this
  case was never itself tested as a distinct bucket).
- **Overnight coil** (hyp-000057, reusing
  `study_intraday_behavior_batch3.build_overnight_and_rth_frame` /
  `analyze_overnight_coil`'s definition unmodified): coiled overnight
  session -> today's RTH range ratio ~0.89 (Validation ci_90
  0.830-0.960); not coiled -> 1.0 (no adjustment; only the coiled
  bucket was itself tested).
- **Combined multiplier**: when both signals fire the same day (both
  point toward "quieter than normal"), multiply the two ratios
  together as an approximation (disclosed as an approximation --  the
  interaction of the two conditions together has never itself been
  tested, only each alone). When they disagree or only one fires, use
  whichever ratio(s) actually apply; when neither fires, multiplier is
  1.0 (no information).

## Output

A single function, `get_volatility_conditioning(date, df)`, returns:
`{"narrow_prior_day": bool, "coiled_overnight": bool,
"expected_range_multiplier": float, "basis": [...]}` -- `basis` lists
which confirmed fact(s) contributed, so a caller always knows exactly
what the number is built from, never a black box.

## Honesty disclosures in the module's own docstring

1. Both underlying facts predict RANGE, not direction -- this cannot
   tell anyone which way to trade, only how big a move to expect.
2. Neither fact's economic value has been tested as an actual
   sizing/stop-width rule yet (the 3 overlay screens run earlier today
   found no conditioning effect on the specific dead signals tested --
   that doesn't mean this could never help a live signal, just that it
   hasn't been shown to yet).
3. Validation-slice numbers are used deliberately, not Discovery, to
   avoid repeating this project's most common mistake.
