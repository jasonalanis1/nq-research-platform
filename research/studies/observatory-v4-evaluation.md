# Observatory v4 Evaluation (multi-day reference levels + cost-aware screening)

Ran 2026-09-09. Frozen spec: research/studies/observatory-v4-design-spec.md.
276 combinations scanned (prior-week/prior-month high/low x regime x time
bucket x horizon), Discovery data only.

## Result

Label breakdown: 1 Promising, 7 Interesting, 201 Weak, 1 No-meaningful-
difference.

The single Promising candidate (prior_week_high, normal regime, open
bucket, 3min horizon, n=123, effect=-1.32pts, ci_90 entirely below
zero) is exactly the case the new cost-aware screen exists to catch:
ATR-normalized effect = 0.0103 -- about 1% of a typical day's range --
flagged LOW-PRIORITY_COST_DOMINATED before any hypothesis spec was
written. For comparison, H87/H89's near-miss (the closest result this
project has produced) had a materially larger relative effect and
still narrowly failed net of cost. Writing a monetization hypothesis
for an effect an order of magnitude smaller than the closest-ever near
miss would very likely repeat the same cost-dominated failure pattern
already diagnosed twice. Screen worked as intended.

Three candidates clear the ATR-normalized floor (0.05) and are
statistically "Interesting" (not "Promising" -- each falls short of
the n>=40 bar): prior_month_high/wide/open/30min (n=20, effect=+8.05,
atr_norm=0.063), prior_week_high/normal/afternoon/30min (n=18,
effect=+7.17, atr_norm=0.056), prior_week_low/normal/afternoon/10min
(n=15, effect=+6.86, atr_norm=0.054). All three are too thin to write
a Behavioral Finding at real confidence (same reasoning that flagged
hyp-000051's n=9 as untrustworthy) -- multi-day reference levels are
inherently low-frequency events (roughly one prior-week-high touch per
week, one prior-month-high touch per month), so getting n>=40 in this
family requires either a much longer lookback or coarser bucketing,
both of which would change the event definition rather than just
waiting for more Discovery data (none is coming -- Discovery is
capped).

## Verdict

No candidate is both statistically Promising and cost-viable in this
scan. Per protocol, no Behavioral Finding or hypothesis spec is
written from a thin/cost-dominated candidate -- writing one would set
up a doomed monetization attempt or an untrustworthy finding, either
one a waste of a research cycle. This scan is closed as a clean,
informative null: the multi-day reference-level family does not
appear to offer a materially exploitable behavior at the sample sizes
Discovery makes available, and the new cost-aware screen correctly
pre-empted spending a monetization cycle on the one statistically
Promising-but-tiny-effect candidate it did find.

## Combined with the rest of this week's work

Both live threads from the 2026-09-09 audit are now closed:
overlay-screen 3 (volatility findings on H87/H89) came back null;
Observatory v4 (multi-day levels) came back with nothing both credible
and cost-viable at adequate sample size. No open leads remain in the
project as of this writing. Per the methodology, the default next step
is a further Observatory scan generation with a new event family --
not yet scoped.
