# Portfolio review — hyp-000142/144/151 (VXN level vs. trailing -> next-session range)

Hypothesis IDs covered (full family): hyp-000142 (Discovery), hyp-000144 (Validation),
hyp-000151 (Holdout, HOLDOUT PASSED September 12th, ~9:45 pm CT, Jason's sign-off).

Written: September 12th, ~9:50 pm CT (2026-09-13 UTC), same evening as the Holdout run.
Closes the FROZEN-tier item the pipeline sweep will carry from Holdout passed.

## Question
Per AMENDMENT v2 (Portfolio Agent's first job): does this finding add incremental
information, or is it the same latent volatility-persistence state already captured by
the overnight-coil finding (`overnight_range_vs_atr`, hyp-056/057) and/or prior-day range
regime (hyp-046/048), restated through the options market? The mechanism doc names this
exact risk directly (Section 3, P3), and the blind Integrity Gate made resolving it a
binding condition before Holdout could even be authorized.

## Method
This question was already run TWICE before Holdout, not just once at Portfolio review --
unusually thorough for this family because the Gate flagged it as unresolved:
- Discovery (P3, gating for advancement): residualized on `overnight_range_vs_atr`
  tercile alone. 66% of the HIGH-LOW spread retained, residual HIGH cell stays credible.
  corr(vxn_level_vs_trailing, overnight_range_vs_atr) = +0.41 -- real overlap, not identity.
- Statistical stage (P4 resolution, per the blind Gate's condition 1): residualized on
  BOTH prior-day realized range (`range_vs_atr`) AND overnight range together (the
  stricter, two-variable control). 53% of the HIGH-LOW spread survives.
- Holdout (this review): the P4 split (prior-day-quiet vs. prior-day-wild) reproduced its
  Validation-stage shape a third time on genuinely untouched data -- both cells credibly
  elevated (quiet 1.127, wild 1.351), confirming the "partly echo, partly genuine lead"
  reading held out of sample rather than being a Discovery-slice artifact.

## Result
Across three independent checks (Discovery single-variable residual, Statistical
two-variable residual, Holdout P4 reproduction), VXN's next-session range signal survives
controlling for both existing conditioning facts at 53-66% of its raw magnitude,
consistently on the elevated (informative) side, never collapsing to the null. This is a
weaker retention than midday-lull's 82.5% but still comfortably above the standing 50%
separability floor at every check, on three different slices of data (Discovery,
Statistical re-check, Holdout).

## Verdict
**SEPARABLE, with a disclosed caveat.** VXN carries genuinely incremental next-session
range information beyond both the overnight-coil and prior-day-range facts, not a
restatement of either -- but roughly half the raw effect (34-47%, depending on which
control set) IS shared with those facts, higher overlap than any of the project's other
three conditioning survivors. Disposition: **KNOWN TRUE, incremental but overlapping** --
per the blind Gate's binding condition, if and when this is integrated into
`src/volatility_conditioning.py`, it must be combined with the existing overnight-coil
input BY RESIDUAL (the shared component removed once, not applied twice), never by
simple product -- the current module's documented "combined = product of both ratios"
convention (see its own Disclosure 4) is explicitly NOT valid for this third fact and
should not be extended to it unmodified.

Not addressed here (out of scope for Portfolio's incremental-information question,
deliberately, and out of scope for tonight given the change freeze on structure through
September 19th): the actual code integration into volatility_conditioning.py, and the
residual-combination formula itself. This is a "how do we combine three facts, one of
which needs residual not product" build decision -- exactly the kind of "turn the banked
facts into a product" work already flagged for the September 19th checkpoint. Recording
the constraint here now so it is not lost or violated whenever that build happens.
