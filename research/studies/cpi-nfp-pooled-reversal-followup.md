# Pooled CPI+NFP Reversal Follow-Up (exp-045)

## What this document is

A frozen spec, written before running anything, for the "pooled
CPI+NFP" version of exp-042's CPI-only reversal follow-up. This is the
concrete next step the Path-to-Profitability Advisor recommended
(2026-09-03) and that this document verifies was genuinely
pre-planned, not reverse-engineered from a good-looking number:
`research/studies/post-release-directional-continuation.md` (exp-041's
own frozen spec, written before any result existed) already treats
NFP as a first-class member of the "CPI/NFP pass" population --
"every day `classify_day()` returns 'cpi' or 'nfp' for" -- and exp-041's
own results file already computed the nfp-only descriptive statistic
(see below). Pooling them now uses only machinery and data already
built; nothing new is invented.

## Why this, and an honest disclosure before running it

exp-042 tested CPI-only reversal and came back a close-but-real kill:
n=75, net mean +10.273 pts, 90% CI [-0.314, +21.810] -- the lower bound
sits just barely below zero. n=75 is also half this project's 150-trade
promotion-bar minimum, so no outcome there could ever have reached
"promote" regardless of the result.

**Disclosed risk, stated before running anything**: exp-041's own
descriptive breakdown already shows CPI-only and NFP-only do NOT point
the same direction. CPI-only directional continuation: -11.023 pts
(n=75) -- the basis for exp-042's reversal bet. NFP-only directional
continuation: **+1.805 pts (n=77), CI [-12.762, +15.608]** -- near zero,
and the OPPOSITE sign from CPI. exp-041's own write-up already flagged
this: "nfp and fomc disagree in sign with the pooled (negative)
result," and separately notes pooling CPI with NFP "dilutes" the
effect. This means pooling CPI+NFP is a genuine, honest question with
a real chance of making the result WORSE (more diluted, wider CI, less
credible), not a guaranteed improvement just because the sample gets
bigger. This is being run anyway because a bigger, real-sized sample
answering the question honestly either way is more useful than a
half-sized near-miss that can never be trusted on its own -- not
because a positive outcome is expected.

## Methodology (identical to exp-042, one change only)

Reuses `study_post_release_continuation.py`'s `scan_all_days()` and
`compute_directional_continuation()` unmodified (same as exp-042).
The ONE change from exp-042: the population mask is
`sub["release_type"].isin(["cpi", "nfp"])` instead of
`sub["release_type"] == "cpi"` only. Everything downstream -- the
mirror-image reversal pricing (`reversal_pnl_gross = -1 *
directional_continuation`, `reversal_pnl_net = reversal_pnl_gross -
ROUND_TRIP_COST_POINTS`), the bootstrap CI, the two robustness checks
(drop-largest, split-half) -- is exp-042's exact code, unmodified,
applied to the larger pooled population.

Expected pooled n: 75 (cpi) + 77 (nfp) = 152 -- for the first time in
this specific lead's history, at or above the 150-trade minimum.

## What counts as a real outcome here (pre-registered, before running)

- **Statistically credible AND economically meaningful** (same gates as
  exp-042: 90% CI entirely above zero, mean net >= 2x round-trip cost)
  **AND n >= 150**: this would be the first result in this project's
  22-hypothesis history to clear the full, un-adapted promotion bar.
  Still would need Validation-slice confirmation before "promote" is
  used for real (per `data_split.get_validation_data()`'s own
  restriction), but would be a genuinely different moment than
  anything so far.
- **Fails either statistical or economic gate**: kill, same as exp-042,
  and this specific lead (CPI/NFP reversal) is closed out for good --
  no third look, no further re-slicing of this same event-day data.
- **Passes with n still under 150** (should not happen given the
  expected pooled size, but disclosed in case of unexpected
  exclusions): same "retest -- promising, underpowered" holding
  pattern as exp-042.

## What this is NOT

- Not a new search for the best-looking release-type combination --
  CPI+NFP pooled is the one and only population tested here, chosen
  because it was pre-planned in exp-041's original design, not because
  it was picked after seeing which combination looks best.
- Not independent confirmation of exp-042 -- same underlying Discovery
  data and statistic, just a larger slice of the same population
  (CPI+NFP instead of CPI-only). `data_split.get_validation_data()`
  remains untouched, same restriction as every prior hypothesis.
- Not a change to the promotion bar itself -- if this reaches n>=150
  and clears both gates, it clears the SAME bar every other hypothesis
  has been held to, no adaptation needed here (unlike exp-038's
  daily-momentum study, this event-driven mechanism was always
  expected to be able to reach 150 trades once CPI and NFP were
  pooled, so no bar adaptation is being requested).
