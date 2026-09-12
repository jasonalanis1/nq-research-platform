# Director Re-Evaluation -- hyp-000140 (|gap_vs_atr| magnitude, same-day RTH range)

Run: September 11th, 1:03 pm CT, scheduled cycle (first under the 2026-09-11 handoff protocol),
src/director_reeval_hyp140.py. Discovery data only. Frozen Scan 010 construction.

## The question

Statistical passed everything (research/studies/hyp140-statistical-stage-2026-09-11.md).
The Re-Evaluation question is not "is it real" -- it is "is it NEW". The project already
holds a validated same-day-range fact from the same night: overnight_range_vs_atr (the
"overnight coil", hyp-056/057). A big opening gap and a big overnight range are plausibly
the same event. If the gap effect is the coil restated, spending a Monetization + Integrity
+ Validation cycle on it buys nothing the project does not already own. Same separability
discipline as H116 (2026-09-09, which retained 98% and advanced).

## Result (n=1310 Discovery RTH days with both variables; fewer than Scan 010's 1668
because overnight_range_vs_atr has a longer warm-up -- disclosed, not a selection)

- Correlation |gap| vs overnight range: Pearson 0.6854, Spearman 0.4679.
  57.0% of HIGH-gap days are also HIGH-overnight-range days (33% if independent).
- Raw HIGH-LOW gap spread in range ratio: 1.2129 vs 0.927 = 0.2859 (reproduces Scan 010).
- Within each overnight-range tercile, the gap spread is:
  low-overnight  0.0914  (HIGH-gap n=41 mean 0.8693; LOW-gap n=222 mean 0.7779)
  mid-overnight  0.0315  (neither cell credible)
  high-overnight 0.1848 (HIGH-gap n=249 mean 1.3668; LOW-gap n=84 mean 1.182)
- Residualised on overnight-range tercile: HIGH-gap 1.0955 ci_90=[1.0496, 1.1422] (credible);
  LOW-gap 1.0037 ci_90=[0.9683, 1.0411] (NOT credible). Spread 0.0918 =
  **32% of the raw effect retained** (H116 precedent: 98%).

## Reading

The COMPRESSION leg (small gap -> quiet day) is entirely the overnight-coil finding:
once overnight range is held fixed, LOW-gap days are at 1.00, and inside the
high-overnight-range tercile LOW-gap days are themselves elevated (1.18). The
ELEVATION leg keeps a residual: HIGH-gap days run about +10% above what overnight
range alone predicts, credible, n=437. That residual is the only genuinely
new information in hyp-000140, and it is a third of what Scan 010 appeared to find.

This also reframes the unexplained P3 volume anomaly: heavy-volume HIGH-gap days are
very likely the high-overnight-range subset; it was never a gap-specific effect.

## Staff meeting (disagreement forum -- Statistical and Director reached opposite dispositions)

- Statistical: the candidate is real and robust on every test; recommends PROMOTE.
- Director: real is not new. Two-thirds of it is a fact the project already validated
  and already carries as a sizing/conditioning input (src/volatility_conditioning.py).
  The residual +10% elevation is a modest, one-sided effect on a non-directional
  outcome, with no realization path the project does not already have for the coil.
  Diminishing returns: a fourth correlated volatility fact does not move the central
  research question (an executable edge). Recommends ABANDON Monetization.
- Integrity Gate: the check is clean (Discovery only, frozen cuts, no retuning) and the
  redundancy was exactly the double-counting risk the Gate's brief names. Concurs with
  Director. Notes the residual must NOT be turned into a new entry post hoc.
- LEARN: record as KNOWN TRUE, NOT INCREMENTAL: |gap| magnitude ~ overnight range
  (r=0.69); gap adds ~+0.10 range-ratio on HIGH-gap days beyond the coil; compression
  side adds nothing. A future entry on the residual is admissible only if it arrives
  with a mechanism DISTINCT from the coil, pre-registered before any further look.

Disposition: **ABANDON at Director Re-Evaluation. hyp-000140 -> REJECTED (redundant with
validated overnight-coil range finding; residual too small and unexplained to fund).**
Monetization not run (input condition not met). Entry 5 CLOSED. No hypothesis ID spent
on the separability check (diagnostic on an existing candidate). Multiplicity: no new
Discovery cells claimed.
