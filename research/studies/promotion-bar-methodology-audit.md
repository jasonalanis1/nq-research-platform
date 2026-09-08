# Promotion-Bar Methodology Audit (Option C)

Requested audit: is the 90-for-90 rejection rate a sign the promotion
bar itself is miscalibrated, or a sign the ideas tried are genuinely
not there? Two checks: cost-assumption realism, and statistical power.

## Cost assumption

`ROUND_TRIP_COST_POINTS` (src/backtest.py) is derived transparently
from full-size NQ contract economics ($20/point multiplier, stated
commission + slippage-in-ticks, both adjustable at the top of the
file) -- not an arbitrary or inflated number. No miscalibration found
here.

## Statistical power (the real finding)

Ran a power analysis across every saved positive-mean result this
session produced: for each, computed the implied standard deviation of
trade R-multiples from its 90% bootstrap CI width, then computed what
sample size WOULD have been needed for that same mean effect to clear
the CI-entirely-above-zero bar.

| Candidate | n (actual) | mean R | n needed | shortfall |
|---|---|---|---|---|
| H87/H89 gap-down fade | 128 | +0.068 | ~194 | 1.5x |
| H88 open-support (long leg) | 104 | +0.046 | ~220 | 2.1x |
| H91 gap-fade multi-day | 71 | +0.109 | ~304 | 4.3x |
| H86 round-number (long leg) | 245 | +0.058 | ~1143 | 4.7x |
| H81 overnight-low fade | 385 | +0.024 | ~6383 | 16.6x |

**This project's single closest near-miss (H87/H89) was only ~1.5x
short of the sample size it would need to clear the bar, assuming the
measured edge is real and holds at the same magnitude.** That is a
meaningfully different conclusion from "the bar is unreachable" -- for
at least one candidate, the bar is roughly in reach, just not with the
data currently available.

## Why we can't just get more data

The Discovery window is capped at 2021-10-03 by this project's frozen
chronological split (Discovery/Validation/Holdout) -- a foundational
integrity control, not a tunable parameter. The underlying price
history extends back to 2015-01-01, well before the current Discovery
start, but Discovery already uses effectively all pre-2021-10-03 data
available. Extending or moving the Discovery boundary to manufacture
more sample size would compromise the split's entire purpose (an
unseen-until-tested Validation slice) and is not something to do
without Jason's explicit sign-off -- flagging this rather than acting
on it.

## Conclusion

The bar itself checks out: cost assumptions are realistic, and the
statistical requirement (CI entirely above zero, not just a point
estimate) is doing its job -- it correctly rejected effects that, when
power-checked, mostly needed 5-15x more data than exists to be
distinguishable from noise. Those are appropriately rejected as
"can't tell," not wrongly rejected as "definitely fake." The one
exception (H87/H89) is close enough that its rejection is closer to
"underpowered" than "clearly false" -- worth remembering if a
materially larger, still-legitimate Discovery-equivalent sample ever
becomes available (e.g. a different instrument's history, or a
sufficiently long time gap before revisiting this project's own
boundary decisions), but not a reason to retest it now under the
current frozen split.
