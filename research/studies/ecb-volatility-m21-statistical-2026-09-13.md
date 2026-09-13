# Statistical stage review — hyp-000150 (M21, ECB decision volatility, 6E)

Reviewed: September 13th, ~12:35 am UTC (7:00 pm CT cycle)

## Result under review
Scan 025, Discovery slice (2015-01 to 2021-10.03). GATING P1: decision-
hour (08:30-09:30 ET) |return|/ATR14 = 0.713 vs unconditional
RTH-equivalent hourly |return|/ATR14 = 0.179, diff +0.534, block-
bootstrap 90% CI (+0.457, +0.782), n=35 ECB press-conference dates.
Credibly positive; the mechanism's magnitude claim clears.

## Two-nulls check
NULL 1 (vs. 6E's own unconditional hourly |return|/ATR14, not zero) is
built into the gating cell by construction, per the project's standing
rule. There is no cross-index directional claim here (P2, the signed
decision-hour mean, is reported unpinned and is null: +0.048 ATR, CI
(-0.166,+0.235) -- consistent with the doc's own prediction that
direction would not be separable from noise), so the cross-index null
does not apply.

## Thin-sample / power check
n=35 events clears the project's informal floor for a magnitude claim
(compare M20's n=329 -- much larger because M20's release is weekly,
M21's is roughly every 6 weeks). The gating CI is comfortably away from
zero relative to its width (+0.457 to +0.782), so n=35 is not a
borderline call the way M19's n=40 directional legs were -- the effect
size here is large enough that even a smaller sample clears it cleanly.

## Kill-adjacent disclosure (required, per the M20 precedent)
First-minute (07:45-07:46, the STATEMENT print, not the 08:30 press-
conference start this mechanism targets) share of the decision-hour
magnitude: 37.9%. Below the 0.5 kill threshold -- not killed -- but
material enough to disclose plainly: a bit over a third of the
decision-hour's magnitude is attributable to the statement print itself,
not the Q&A repricing window the mechanism specifically claims. This
narrows (does not close) the honest interpretation: the finding is "the
hour spanning the ECB announcement and press conference is more volatile
than a typical hour," which is true and useful for sizing, but the
specific claim that Q&A-driven repricing (as opposed to the initial
statement print) drives the bulk of it is not as clean as the headline
number alone would suggest.

## Decay check
Discovery halves: first half mean 0.863, second half mean 0.571 -- both
well above the unconditional 0.179 baseline, so the effect is present in
both halves (not a fluke of one sub-period), though there is some
apparent decay. Block-bootstrap CI is not computable at this sample size
(n=17-18 per half, below the block=10 x 3 = 30 floor) -- reported as
descriptive only, not a formal robustness pass/fail.

## Verdict
STATISTICAL PASS. The magnitude finding is real and not simply a
combination of the print-share issue and thin sampling. Advance to
Director Re-Evaluation with both caveats (statement-print share, thin
half-samples) carried forward explicitly.
