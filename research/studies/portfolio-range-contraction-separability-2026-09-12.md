# Portfolio review — hyp-000046/048 (prior-day range regime) vs. the other two validated volatility facts

Hypothesis IDs covered: hyp-000046 (Discovery), hyp-000048 (Validation-confirmed).

Written: September 12th, 3:xx pm CT (scheduled cycle, queue v2 item 4, Observatory
sourcing). This is the pairing the project had never explicitly checked: H105's
own separability check (September 12th) tested itself against the overnight
coil; nothing had tested the FIRST validated fact (prior-day range regime)
against the other two. All three have been used together in
`volatility_conditioning.py` since September 8th without a pairwise redundancy
check on this specific pairing.

## Question
Same as every prior separability check in this project (H116 2026-09-09, H140
director re-eval 2026-09-11, H105 2026-09-12): does prior-day range regime add
incremental information about same-day range, or is it the overnight-coil fact
or the midday-lull fact restated at a coarser (daily) grain?

## Method
Same discipline: correlation, within-other-fact-level spread survival, and
residualized (partial) spread after subtracting the other fact's group mean.
Script: `src/portfolio_range_contraction_separability.py`. Discovery-slice data
only (n=1,667 days with all three classifications available), all three
classifications reused UNMODIFIED from `volatility_conditioning.py`
(`prior_day_narrow`, `coiled_overnight`, `narrow_midday`) — nothing retuned.

## Result

**vs. overnight coil (coiled_overnight):**
- Correlation: 0.16 (mild).
- Overlap: 7.7% of days both true (vs. 4.9% expected under independence).
- Raw spread (not-narrow minus narrow) in same-day range ratio: 0.234.
- Spread survives within both overnight-coil levels: 0.225 (not coiled),
  0.126 (coiled) — weaker inside the coiled bucket but the same sign, same
  order of magnitude.
- Residualized spread: 0.194, **82.8% of raw retained**.

**vs. midday-lull (narrow_midday):**
- Correlation: 0.16 (mild — same order as the coil pairing).
- Overlap: 8.6% of days both true (vs. 5.7% expected under independence).
- Raw spread: 0.234 (same as above; same signal, different partner).
- Spread survives within both midday-narrow levels: 0.207 (not narrow
  midday), 0.046 (narrow midday) — much weaker inside the narrow-midday
  bucket, but still the same sign, not flipped or nulled.
- Residualized spread: 0.155, **66.1% of raw retained**.

## Verdict
**SEPARABLE from both**, using the project's own precedent thresholds (H116's
98% and H105's 82.5% called separable; H140's 32% called ABANDON). 82.8%
against the coil and 66.1% against the midday fact both clear that bar with
room, and in neither case does the spread flip sign or vanish inside any
level of the other fact — it only compresses, most notably inside the
narrow-midday bucket (0.046), which is the one place worth a plain caveat:
prior-day range regime and midday-lull are closer to double-counting each
other on days when BOTH are narrow than on any other day-type combination,
even though neither subsumes the other overall.

Disposition: **KNOWN TRUE, incremental, all three facts distinct.** No change
to `volatility_conditioning.py` (all three conditioning inputs stay as
independent signals; combination/sizing logic remains explicitly out of
scope for this Portfolio question, per the project's standing convention).
This closes the last unchecked pairing among the three validated
volatility-persistence facts — Portfolio has now run the pairwise check on
all three combinations (contraction-vs-coil, contraction-vs-midday,
coil-vs-midday via H105's own check).

## Caveat for the record (not acted on — change freeze in effect until Sept 19)
The weakest surviving pairing (66.1%, narrow-midday) is the one place a
future combination rule should NOT simply multiply all three multipliers
together when more than one fires the same day — the existing
`volatility_conditioning.py` docstring already discloses the "combined"
multiplier as an unverified approximation; this result is a mild reason to
take that disclosure seriously rather than a reason to change anything now.
