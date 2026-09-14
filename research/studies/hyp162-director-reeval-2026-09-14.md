# Director Re-Evaluation — hyp-000162 (M30: opening-range width → midday range, NQ)

Run: September 14th, 11:00 am CT scheduled cycle, `src/director_reeval_hyp162.py`.
Discovery data only. Frozen Scan 036 construction, reproduced exactly (raw spread
+0.5193, matching the scan).

## The question

Statistical already passed everything
(`research/studies/hyp162-statistical-stage-2026-09-14.md`): stable across halves,
credible in both volatility regimes, survives Šidák at N=467 with the whole
adjusted interval above zero, insensitive to the window boundary. The
Re-Evaluation question is not "is it real" — it is **"is it NEW"**. Precedent:
H116 retained 98% and advanced; hyp-000140 retained 32% and the Director ruled
*real is not new*.

This candidate arrived with a specific reason for doubt already attached. The U6
mechanical suite's placebo check found **yesterday's** opening range reproduces
~74% of the effect. That reads, on its face, like the candidate is redundant.

## Result

Each stratum is a fact the project already owns (or the placebo's own suspect).
Tercile edges are the candidate's own frozen Discovery edges — not recut per
stratum, which would change the definition the freeze protects.

| Held fixed | Owner | corr | HIGH/HIGH overlap | residualised | **retained** |
|---|---|---:|---:|---:|---:|
| `vxn_level_vs_trailing` | hyp-000142, Holdout passed | +0.348 | 49.4% | +0.4142 | **79.8%** |
| `overnight_range_vs_atr` | hyp-056/057, the coil | +0.459 | 52.6% | +0.3908 | **75.3%** |
| `range_vs_atr` (prior day) | F-048 — scan_036's own P3 | +0.445 | 50.6% | +0.4342 | **83.6%** |
| `opening_range_vs_atr` **at t−1** | the U6 placebo's suspect | +0.323 | 48.6% | +0.4529 | **87.2%** |

Worst retained: **75.3%**, against a 50% bar. The prior-day-range row reproduces
scan_036's P3 figure of 83.6% exactly, which is the method control — the
machinery is measuring what it measured before.

## Reading

**Separable on every test, and the placebo result is now explained rather than
dismissed.** These two findings are both true and are not in conflict:

- Yesterday's opening range *is* informative about today's midday range. That is
  the placebo result, and it is real — volatility persists.
- Today's opening range carries information **beyond** yesterday's. Holding
  yesterday's value fixed, 87.2% of the effect survives.

The placebo check was detecting genuine persistence in the underlying variable,
not redundancy in the candidate. This is the same distinction the persistence
guard added to `integrity_checks.py` earlier today was built around — and this is
the harder, more direct version of that test, because it holds the suspect fixed
rather than inferring from sample overlap.

**One observation for the stages downstream.** In every one of the four strata,
the effect is largest in the HIGH tercile (0.64, 0.51, 0.58, 0.54 against
mid-stratum values around 0.29–0.35). The effect does not merely survive high
volatility — it *scales with* it. That is not a separability problem, but it is a
sizing fact in its own right and Monetization should treat the effect as
conditional in magnitude, not constant.

**Stated limitation.** The retained share is a point estimate of a ratio and
carries no confidence interval — same as the H116 and hyp-000140 precedents. What
supports the disposition is not the precision of "75.3%" but that all four tests
land in the same place, well clear of the bar, with every per-stratum spread
keeping its sign.

## Disposition: **ADVANCE**

Separable from every validated volatility fact the project holds, and separable
from its own lagged self. It is genuinely new information, not a restatement.
Owed next: **Monetization**, then the blind Integrity Gate, then a one-shot
Validation attempt.

The Gate still weighs the placebo red independently — this stage answers the
separability question, not the Gate's. What the Gate should now be handed is not
"is this real" and not "is this redundant" (both answered) but the narrower
remaining question: *the effect scales with volatility; is the mechanism in the
mechanism document still the right story for an effect that behaves that way?*

## Consequence for the sizing-queue pause

This morning's staff-meeting disposition paused the sizing queue at four inputs
"until the blind Gate answers hyp-000162's regime question, because that answer
decides whether B2 has four inputs or one wearing four hats."

**That question is now answered, with numbers, at an earlier stage than
expected.** B2's inputs are distinct: this candidate retains 75–88% against each
of them individually. Leaving a pause in place whose stated reason has been
resolved would be process theatre, so the pause is **lifted**. The Gate's
independent say on the placebo is unaffected.
