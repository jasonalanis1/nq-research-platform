# Cross-Asset Short-Term Weekly Reversal -- Scoping (exp-052)

## Provenance

Jason asked (2026-09-07, after exp-051's kill) whether the project
should test multiple genuinely different signal types across the same
diversified basket, rather than one signal at a time, matching how
real multi-strategy operations work. Claude and the Path-to-
Profitability Advisor agreed this is sound in principle (see the
2026-09-07 "against the grain" brainstorm) but flagged a real risk:
testing several ideas loosely and keeping whichever looks best is the
exact multiple-comparisons trap this project exists to prevent. This
spec is the first of that batch, built with that risk explicit.

Before drafting this, the project's own history was checked for prior
art. Two categories initially proposed by Jason turned out to already
be dead ends on NQ: three separate calendar-timing hypotheses
(day-of-week, exp-031; options-expiration week, exp-035; turn-of-month,
exp-043) all came back clean nulls, and VWAP-based intraday mean
reversion (exp-034) was this project's single most decisive rejection
to date. Re-running any of those across more markets would not be a
fresh idea -- diversifying a signal that showed literally nothing on
NQ is a much weaker bet than diversifying exp-047's near-miss was.
Dropped from this batch rather than rebuilt.

What has genuinely never been tested: short-term (weekly-horizon)
return reversal -- betting AGAINST last week's move, distinct in both
mechanism and time horizon from exp-047's family (52-week trailing
momentum, betting WITH the trend) and from exp-034's VWAP reversion
(intraday, session-based, a completely different mechanism).
Short-term reversal at roughly this horizon is a real, separately
published academic phenomenon (distinct from the long-horizon
momentum literature exp-047 drew on), so this is not invented for the
occasion.

## Signal-family lineage disclosure (same discipline as exp-051 Section 3)

This is a NEW signal family, not a derivative of exp-047's. It has
never been tested on any instrument in this project before, in any
form. A pass here would be this family's FIRST test, not its Nth --
so, unlike exp-051, a clean pass here is NOT automatically downgraded
to "eligibility only." It would still need the same Validation/Holdout
corroboration before anything is promoted, but it does not carry
exp-047's inherited selection-bias discount.

## Exact signal definition (frozen before any result is looked at)

Per instrument, using the SAME weekly-return machinery exp-047/051
already built (`resample_to_weekly_closes`, `compute_weekly_log_returns`
from `study_nq_weekly_trend_following.py`, reused unmodified):

    reversal_signal[week_t] = -weekly_return[week_t - 1]

(the negative of the immediately preceding week's own log return --
NOT a multi-week window/sum, deliberately a different, shorter
mechanism than exp-047's 52-week trailing momentum, matching the
distinct academic literature this draws on)

    position[week_t] = +1 if reversal_signal[week_t] > 0
                        -1 if reversal_signal[week_t] < 0
                        (else: hold previous position, or +1 if first
                        classifiable week -- exp-047's own tie rule)

This reuses `compute_positions()` from `study_nq_trend_following.py`
completely UNMODIFIED -- it already implements exactly this
sign/tie-break rule; only the signal fed into it differs from exp-047
(single prior week, negated, instead of a 52-week trailing sum).

## Portfolio construction

Identical to exp-051's (frozen spec
`cross-asset-weekly-trend-scoping.md` Section 5), reused, not
reinvented: inverse-20-day-volatility weighting across the same 4
instruments (NQ/ZN/6E/CL), weekly log-return space, 5-bps-of-notional
per-instrument-per-flip cost (`FLIP_COST_BPS = 5.0`, same derivation).
`compute_portfolio_pnl()` from `study_cross_asset_weekly_trend.py` is
generic over the `positions` dict passed in -- reused completely
unmodified, just fed this signal's positions instead of exp-047's.
Same 2020-04-20/21 negative-WTI-price guard already fixed in
`study_volatility_regime.py`'s `compute_daily_ref_closes()` applies
here automatically (shared code, already fixed).

## Confirmation-filter layer (per Jason's second request, 2026-09-07)

Jason also asked whether a signal should need a second indicator to
agree before being trusted, rather than testing every possible
filter combination (which would multiply the number of things tried
and reopen the multiple-comparisons risk this whole batch is trying to
avoid). Resolution: filtering is applied ONLY as a Step 2, gated
behind this signal clearing Step 1 on its own -- same two-step gating
convention already used elsewhere in this project (exp-029/030,
exp-032/033, exp-043). If the raw reversal signal does not clear the
Step 1 promotion bar, Step 2 (the filter) is never run -- consistent
with "don't chase a filtered version of something that already failed
unfiltered," the same logic that closed out the exp-047 family after
two failed overlay attempts.

If Step 2 does run, the filter is: only take the reversal position in
a week where the SAME week's trailing-volatility PERCENTILE RANK is in
the bottom half of its own instrument's history -- i.e., only bet on
reversal in relatively calm weeks, skip it in high-volatility weeks.
This is a single, pre-specified filter choice (not tuned against
results), chosen because short-term reversal effects are commonly
documented to be weaker/noisier during high-volatility regimes -- a
real, stated mechanism, not a knob turned until something passed.

**No-lookahead, made explicit (Advisor-required, v2):** the percentile
rank for week_t's volatility is computed against only the trailing
volatility VALUES ALREADY KNOWN before week_t (an expanding,
point-in-time distribution built from `vol_by_day` entries strictly
before week_t's first trading day) -- never against the full-sample
distribution, which would leak future information into a week-t
decision. A week with fewer than 20 prior volatility observations
(the filter's own warm-up period, on top of `compute_trailing_volatility`'s
own 20-day warm-up) has no percentile rank; that week's raw Step-1
position is used unfiltered rather than silently excluded, since
excluding it would let this Step-2 warm-up quietly change the sample
Step 1 was already scored on.

**Sample period (Advisor-required, v2):** identical to exp-051 --
Discovery slice only (2015-01-01 to 2021-10-03), same 4-instrument
basket, same holdout boundary already applied by the shared loader.
No new data acquisition.

## Overfitting correction across this batch

Both this hypothesis (raw) and its Step-2 filtered variant, if run,
share a `search_batch_id` in the ledger (the new field added
2026-09-07) so `larry_validate.py`'s trial-counting reflects the true
batch size rather than undercounting them as unrelated single tests.

**Batch scope (Advisor-required, v2):** this `search_batch_id` covers
Step 1 and Step 2 of THIS signal family only. Jason's original request
was to test several genuinely different signal families in this same
round -- if and when another family (beyond this one) is scoped and
run as part of the same initiative, its hypotheses must reference this
same round via a shared PARENT reference (noted in each hypothesis's
`notes` field: "part of the 2026-09-07 multi-signal-family round,
alongside hyp-000021 [exp-051] and this family") so a future trial
count across the whole round can be reconstructed by reading `notes`,
even though `search_batch_id` itself only groups one family's own
internal variants. Not solved by widening `search_batch_id` itself,
since Step-1/Step-2 within a family and family-vs-family across a
round are genuinely different groupings.

## Promotion bar

Identical two-part bar as every other hypothesis in this project (90%
CI entirely above zero AND economically meaningful vs. realized cost),
applied to the combined portfolio's weekly return series.

## What this is NOT

- Not a re-test of any already-killed calendar-timing or VWAP-reversion
  idea -- see Provenance above for why those were dropped, not reused.
- Not a search across multiple filter definitions -- exactly one filter
  is pre-specified, gated behind Step 1, never run at all if Step 1
  fails.
- Not a promotion or live-authorization step even on a clean pass --
  same corroboration requirement as everything else in this project.

## ASCII-only

Confirmed.

## Advisor review (2026-09-07)

v1 returned "cleared with changes, not cleared as-is." Required
changes, all incorporated above: (1) explicit no-lookahead statement
for the filter's volatility-percentile calculation (point-in-time,
never full-sample) plus a stated rule for its own warm-up weeks; (2)
explicit sample period declared (Discovery slice, same as exp-051);
(3) filter warm-up edge case resolved (unfiltered Step-1 position
used, not silently excluded); (4) batch-scope note added so a future
trial count across this whole multi-signal-family round can be
reconstructed via each hypothesis's `notes` field, since a single
`search_batch_id` can only group one family's own Step-1/Step-2
variants. On concept: Advisor confirmed short-term reversal is a
genuinely distinct, real test (different horizon/mechanism from both
prior families), and gating the filter behind a Step-1 pass rather
than grid-searching filter variants correctly avoids the within-family
multiple-comparisons trap.
