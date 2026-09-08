# IB Breakout, Conditioned on the Volatility Conditioning Module — Frozen Spec (exp-093)

## Why this is different from the 3 earlier overlay screens

exp-077, exp-086, and exp-087 all conditioned already-REJECTED Level
Sweep Reversal (a MEAN-REVERSION thesis) trades on a volatility fact and
found nothing. This is a mechanistically different pairing: Initial
Balance Breakout (`detect_ib_breakout.py`, hyp-000011, also REJECTED
standalone) is a CONTINUATION thesis -- it needs the day to actually
have room to run past the IB range to reach its 1.35R target before
reversing. "Today is expected to have an above-average range" (the
`prior_day_wide` flag from `volatility_conditioning.py`, itself built
from hyp-000048's Validation-confirmed finding) is a plausible,
motivated condition for a continuation setup specifically, in a way it
was never plausible for a reversal setup. This is the Market Behavior
Advisor's suggested next step: not more hypothesis origination, a
purpose-built pairing of an already-confirmed fact with a setup whose
own mechanism plausibly benefits from it.

## What this is NOT

IB Breakout is closed standalone (hyp-000011, REJECTED, Discovery
n=1654) -- the no-retuning rule means this cannot resurrect IB Breakout
as a whole. This tests whether the WIDE-DAY SUBSET specifically has
different economics than the rest -- a legitimately separate question,
same logic as this project's own precedent of testing subgroups as
their own universe (e.g. hyp-000052's choppy/trend_like split). If the
wide-day subset shows a credible, well-powered, economically meaningful
edge, that becomes its OWN new, separately pre-registered hypothesis
(a "wide-day-conditioned IB breakout") subject to its own Discovery ->
Validation-prospective-test pipeline before any promotion consideration
-- this spec's result alone, however it comes out, is not itself a
promotion event.

## Method

1. Generate IB Breakout signals on Discovery data only, reusing
   `detect_ib_breakout.scan_all_days()` and `backtest.simulate_trade()`
   unmodified -- same detection logic, same 1.35R target, same cost
   model (`ROUND_TRIP_COST_POINTS`) as hyp-000011's original test.
2. Classify each trade's date using `volatility_conditioning.
   build_conditioning_frame()` (Discovery data), unmodified.
3. Split trades into `wide_prior_day == True` vs. everything else
   (narrow or neither -- narrow is excluded from its own bucket here
   since the mechanistic argument is specifically about a continuation
   setup wanting room to run, not about narrow days being bad for it in
   a specific, motivated way).
4. Bootstrap difference-in-means CI on `r_multiple_net` between the two
   groups, N_BOOTSTRAP=3000, seed=7, 90% CI, this project's standard
   method. A bucket with fewer than 30 trades is flagged as too thin to
   trust, not forced into a verdict.

## Decision rule

Diagnostic, same tier as exp-077's screen -- but unlike exp-077, a
credible result here (unlike a mean-reversion setup with no
mechanistic story) is the trigger to formalize a genuinely new,
separately pre-registered hypothesis, not just informational. A null
result closes this specific pairing (breakout continuation x range-
expectation) for good, no further variants without a new independently
motivated reason.
