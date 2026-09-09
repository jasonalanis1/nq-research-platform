# Observatory v4 Design Spec

Frozen 2026-09-09. Continues the Observatory as the project's default
hypothesis-generation mechanism (research/studies/two-layer-methodology.md).

## What's new vs. v1/v2/v3

1. **New event family: multi-day reference levels.** v1-v3 all used
   single-prior-day or intraday-occurrence event definitions. v4 adds
   first-touch of the prior CALENDAR WEEK's high/low and the prior
   CALENDAR MONTH's high/low -- a genuinely different time scale,
   structurally distinct from anything scanned before. (Options/futures
   expiration and CPI/NFP/FOMC release-day effects were checked earlier
   in the project -- research/studies/futures-expiration-effects.md,
   economic-release-volatility.md -- both clean nulls, not re-tested
   here.)
2. **Cost-aware candidate screening, applied at ranking time, not
   signal-design time.** Per the 2026-09-08 diagnostic (cost-dominance:
   real gross effects wiped out by fixed cost against typical risk
   distances) and H90's disproof of a naive raw-point screening rule,
   v4 reports each candidate's effect size BOTH in raw points and
   normalized by that day's ATR(14) (effect_size / atr14_avg_over_
   window), and flags candidates whose ATR-normalized effect is below
   a fixed, pre-registered floor (0.05, i.e. the effect is under 5% of
   a typical day's range) as LOW-PRIORITY regardless of statistical
   credibility -- these are not discarded, just deprioritized for
   hypothesis-spec-writing, since H87/H89's own near-miss had an
   ATR-normalized effect near this order of magnitude and still nearly
   failed on cost alone. This is a new screening rule applied fresh to
   v4's own output, not a retune of H90 (H90's specific raw-point rule
   stays disproven and unused).
3. Baseline/ranking machinery otherwise unchanged from v1 (same
   bootstrap-diff-CI technique, same regime/time-bucket conditioning,
   same Promising/Interesting/Weak/No-meaningful-difference labels).

## Event definitions

- `prior_week_high` / `prior_week_low`: high/low of the most recently
  fully-completed calendar week (Mon-Fri), first RTH touch.
- `prior_month_high` / `prior_month_low`: high/low of the most recently
  fully-completed calendar month, first RTH touch.

Same 4 time buckets, same 6 horizons (1,3,5,10,15,30 min), same
volatility-regime conditioning (narrow/normal/wide via
volatility_conditioning.build_conditioning_frame, unchanged) as v1-v3.

## Per protocol

Any Promising/Interesting candidate gets its own Behavioral Finding
(OBS-FINDING-NNN) before any hypothesis spec is written -- no
exceptions, per observatory-finding-protocol-addendum.md.
