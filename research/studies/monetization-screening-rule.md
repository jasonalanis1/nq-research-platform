# Monetization Pre-Screening Rule (derived from diagnostic + H87/H89)

Not a hypothesis -- a methodology conclusion from this session's
diagnostic work, to be applied to future Observatory candidates before
a hypothesis spec is even written.

## What the data showed

Gross-vs-net decomposition (monetization-diagnostic-round1.md) on
H81-short and H86-combined: both had a real, small POSITIVE gross edge
(+0.010R, +0.031R) fully consumed by the fixed 0.75pt cost, because
their risk distances (15-21pts, from the 1-minute-buffer stop
convention) were too tight -- cost was 5.5-7.5% of risk per trade.

Switching to an ATR(14)-scaled stop (H87/H89) widened risk distance
substantially and produced this project's closest-ever near-miss
(gap-down fade, long-only: mean_r=+0.068, economically meaningful,
CI narrowly missing credibility) -- direct confirmation that widening
risk relative to fixed cost is the right lever, even though it wasn't
quite enough on its own this time.

## The rule

Before writing a hypothesis spec for a new Observatory candidate,
require its OWN measured effect size (in points, from the Observatory
scan output) to be checked against a minimum bar: the candidate's
measured effect at the chosen horizon must be large enough that, once
converted to a trade with a stop sized to reasonably contain that
horizon's typical noise (proxy: daily ATR(14), the new default), the
fixed 0.75pt cost is no more than ~5% of that stop distance. In
practice: candidates with ATR-scale stops around 40-90pts (typical NQ
range) need the underlying measured effect to be economically
non-trivial at that scale, not just statistically distinguishable from
baseline at a 1-point level. This filters out candidates whose
Observatory-measured effect, however statistically real, is too small
in POINTS to ever clear a cost-aware stop -- before spending a full
hypothesis-spec-and-test cycle on them.

This does not replace the existing promotion bar (90% CI, prospective
test) -- it's a cheaper pre-filter to apply at candidate-selection time,
using output the Observatory scan already produces.

## Status of the underlying research question

Applied retroactively: of this session's 9 hypotheses, only the
gap-fade candidates (whose Observatory effect sizes were 3.5+ points at
short horizons, largest of any candidate scanned) came close. This is
consistent with the rule -- worth formalizing as a required check
before the next Observatory scan is converted into hypotheses, rather
than running blind.
