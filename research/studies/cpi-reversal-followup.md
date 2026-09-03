# CPI-Only Reversal Follow-Up (frozen spec)

**Status: frozen, not yet run as of writing.** Drafted 2026-09-03, at
Jason's explicit direction ("let's just knock it out"), as item #2 of
the three-item agenda agreed after the "step back" conversation:
checkpoint review, this CPI-reversal follow-up, and an order-flow data
cost check.

## What this is following up on

exp-041 (`research/experiments/exp-041-post-release-directional-continuation.md`)
pre-registered ONE primary test -- pooled CPI+NFP+FOMC directional
continuation -- and it came back null. A descriptive breakdown by
release type, run AFTER seeing the pooled result (not pre-registered),
showed CPI days specifically had a statistically credible (90% CI
entirely below zero) tendency to REVERSE rather than continue: n=75,
mean -11.023 points, CI [-22.560, -0.436]. exp-041's own writeup
flagged this honestly as "a lead requiring its own fresh frozen spec,
not treated as a finding" -- exactly what this document is.

## Being honest about what this test can and can't prove

This uses the SAME Discovery-slice CPI days and the SAME
`directional_continuation` statistic already computed in exp-041 --
re-running that exact computation will reproduce the exact same
numbers above, because nothing about the underlying data or math
changes. This is NOT independent confirmation on fresh data. Two
reasons a fresh sample isn't used instead:

1. `data_split.get_validation_data()` is explicitly reserved, by this
   project's own rule (see its docstring and
   `docs/RESEARCH_INTEGRITY_PROTOCOL.md`), for testing a candidate that
   was already formally PROMOTED out of Discovery -- never for
   searching new leads. This lead hasn't been promoted (it isn't even
   a costed strategy yet), so pulling Validation data now would itself
   violate the project's own rule against using it to search.
2. There is no other independent NQ data available to this project
   (no live forward period has passed since exp-041 was written).

So the only genuinely NEW information this follow-up can add, without
breaking the Validation-slice rule, is: does the observed reversal
survive being treated as an actual, cost-inclusive trade -- something
exp-041's raw point-to-point statistic never tested. That is the one
and only thing this document commits to testing. If it's positive
after costs, the honest verdict is still "promising lead, needs
Validation-stage confirmation before being trusted with money" -- NOT
"promoted" -- both because it hasn't been independently confirmed and
because n=75 is nowhere near this project's 150-trade promotion-bar
minimum (see below).

## The one pre-registered test

Reuses `study_post_release_continuation.py`'s own
`directional_continuation` values for CPI-only rows, unmodified. No
new stop-loss or target parameters are introduced (each new parameter
choice would itself be a new researcher degree of freedom and a new
overfitting risk, which is exactly what Jason asked to avoid by not
wanting to "go down the rabbit hole" here) -- the trade this test
prices is simply "take the reversal side of the initial 30-minute
move, hold the position mechanically to the 180-minute mark," the
exact mirror image of exp-041's own continuation trade:

```
reversal_pnl_gross = -1 * directional_continuation      # betting AGAINST the initial move's direction
reversal_pnl_net   = reversal_pnl_gross - ROUND_TRIP_COST_POINTS   # one round-trip cost per trade, reused unmodified from backtest.py
```

**Primary test:** 90% one-sample bootstrap CI (2,000 resamples,
seed=11, `study_nq_trend_following.bootstrap_mean_ci()` reused
unmodified) on the mean of `reversal_pnl_net`, CPI-only rows.

**Step-2 gate, same bar as every prior study in this project:**
1. Statistically credible: CI entirely above zero.
2. Economically meaningful: mean >= 2 x ROUND_TRIP_COST_POINTS.

**Promotion-bar reminder, stated up front so a positive result isn't
overread:** this project's promotion bar
(`docs/RESEARCH_INTEGRITY_PROTOCOL.md`) requires a minimum of 150
trades. CPI-only Discovery days number at most 75 (fewer once the
usual small exclusions for missing data are applied). No outcome of
this test can result in a "promote" verdict -- at best, "promising,
underpowered, revisit if the sample grows or Validation-stage testing
becomes appropriate later"; at worst, a clean kill.

**Robustness (descriptive, does not override the primary verdict):**
drop the single largest-|reversal_pnl_net| day; first-half/second-half
chronological split -- both reused unmodified from
`study_post_release_continuation.py`'s existing helpers.

Implementation: `src/study_cpi_reversal_followup.py`.

## What this is NOT

Not a new detection method, not new calendar data, not a new stop/
target design, not a Validation-stage test, not eligible for
promotion regardless of outcome (see above). A single, narrowly
scoped, cost-inclusive check of one already-disclosed lead.
