# Statistical-stage pass — hyp-000048, hyp-000057, hyp-000106

Automated session, 2026-09-10 (08:15-~10:xx UTC). NEXT_UP.md queue item
0. Full detail behind research/sessions/2026-09-10-0815.md and the
updated Prediction-status/Verdict sections of the three mechanism docs
(research/mechanisms/range-contraction-expansion-cycle.md,
overnight-coil-rth-range.md, midday-lull-afternoon-persistence.md).

## Scope and method

Per queue item 0: the 4 Statistical-stage questions (stability, regime
dependence, magnitude, selection sensitivity) plus same-data selection
disclosure, using the multiplicity-corrected numbers already computed
2026-09-10 (src/project_wide_multiplicity.py), plus each mechanism
doc's cheap already-scoped predictions (P1-P3).

Data: Discovery+Validation slices only (2015-01-01 -> 2024-01-03),
concatenated chronologically so trailing statistics run continuously
across the boundary — consistent with how each candidate's original
prospective test computed trailing stats. Holdout and live data
untouched (scope boundary). All bootstrap CIs: 3000 resamples, seed=7,
90% (5th/95th percentile), same convention as every prior script in
this project.

Code: research/_scratch_worksession/stage_a_build_cache.py (builds and
caches the three candidates' daily frames plus the state-primitives
frame used for VXN/volume/OPEX descriptors),
research/_scratch_worksession/stage_b_statistical_pass.py (the actual
4-question + predictions battery). Both are scratch, not committed to
src/ — the numbers below are the permanent record; promote the scripts
to src/ in a future session only if this becomes a recurring check.

## The 4 questions, per candidate

### 1. Stability (chronological split-sample)

Full Discovery+Validation sample split at its chronological midpoint;
same threshold definitions (rolling trailing-20-day percentile, no
refitting) applied to each half independently.

| Candidate | Leg | First half | Second half | Same sign/magnitude? |
|---|---|---|---|---|
| range-contraction | narrow | n=274, mean=0.837, credible | n=283, mean=0.886, credible | yes |
| range-contraction | wide | n=267, mean=1.339, credible | n=255, mean=1.272, credible | yes |
| overnight-coil | coiled | n=213, mean=0.783, credible | n=231, mean=0.826, credible | yes |
| midday-lull | narrow | n=270, mean=0.710, credible | n=287, mean=0.764, credible | yes |

All four clean. No candidate shows a sign flip or a magnitude collapse
across the chronological halves.

### 2. Regime dependence (volatility regime, trailing ATR(14) median split)

Same ATR(14) median threshold (141.2 pts) used for all three, computed
once on the full state frame.

| Candidate | Leg | Low-vol regime | High-vol regime | Concentrated in one regime? |
|---|---|---|---|---|
| range-contraction | narrow | n=272, mean=0.865, credible | n=285, mean=0.859, credible | no |
| range-contraction | wide | n=269, mean=1.338, credible | n=253, mean=1.272, credible | no |
| overnight-coil | coiled | n=219, mean=0.797, credible | n=225, mean=0.813, credible | no |
| midday-lull | narrow | n=267, mean=0.722, credible | n=290, mean=0.752, credible | no |

None of the three shows the Scan-003 failure pattern (effect
concentrated in one ATR-defined volatility regime) on this cut. Note:
overnight-coil's mechanism-doc P3 uses a DIFFERENT regime variable
(VXN-level, not ATR) and DOES show concentration there — see below and
the doc itself. Which regime variable is used matters; ATR-clean is not
the same claim as VXN-clean.

### 3. Magnitude (multiplicity-corrected, from src/project_wide_multiplicity.py, N_validation=18)

| Candidate | Leg | Raw Validation CI | Corrected 90% CI | Survives? |
|---|---|---|---|---|
| range-contraction | narrow | (0.888, 0.998) | (0.852, 1.036) | **NO — crosses 1.0** |
| range-contraction | wide | (1.020, 1.143) | (0.978, 1.184) | **NO — crosses 1.0** |
| overnight-coil | coiled | (0.830, 0.960) | (0.786, 1.003) | **NO — crosses 1.0** |
| midday-lull | narrow | (0.762, 0.878) | (0.718, 0.914) | **YES** |
| midday-lull | not-narrow | (1.037, 1.147) | (0.999, 1.183) | NO — crosses 1.0 |

This table is unchanged from the mechanism docs (re-quoted here for a
single reference point) — it is the binding constraint for range-
contraction and overnight-coil regardless of how the other 3 questions
score.

Economic-meaningfulness convention for a range-RATIO characterization
(this project has no prior convention for this — stated explicitly so
a future session doesn't have to re-derive it): distance of the mean
from the 1.0 null. All four surviving-raw-CI legs clear a 5%
deviation from 1.0 (the same ATR-normalized-effect floor this project
already uses for point-return effects), before correction. Only
midday-lull/narrow clears it AFTER correction (mean 0.816, 18.4% below
null).

### 4. Selection sensitivity (percentile threshold varied around the frozen 20/80)

| Candidate | Leg | pctl 15/85 (or 15) | pctl 20/80 (frozen) | pctl 25/75 (or 25) |
|---|---|---|---|---|
| range-contraction | narrow | n=467, mean=0.847 | n=557, mean=0.862 | n=647, mean=0.861 |
| range-contraction | wide | n=425, mean=1.343 | n=522, mean=1.306 | n=612, mean=1.277 |
| overnight-coil | coiled | n=370, mean=0.796 | n=444, mean=0.805 | n=531, mean=0.816 |
| midday-lull | narrow | n=465, mean=0.732 | n=557, mean=0.737 | n=635, mean=0.745 |

All three candidates are insensitive to the exact threshold choice —
means move by low single-digit percent as the cutoff moves 5 points
either side of the frozen value, in the direction sample size would
predict (wider bucket -> mean drifts toward 1.0), not a fragile cliff
at exactly 20/80. No selection-sensitivity red flag on any candidate.

### Same-data selection disclosure

All three candidates' narrow/wide/coiled percentile thresholds (20/80,
or 20 alone) were fixed BEFORE any of these three candidates was
tested — inherited from study_intraday_behavior_batch1.py's original
RANGE_NARROW_PCTL/RANGE_WIDE_PCTL constants (2026-09-08), reused
unmodified by batch3 (overnight-coil) and the midday-lull study. No
threshold was tuned specifically to any of these three results, and
none of today's re-analysis retunes them either — question 4 above
varies them only to test robustness, not to pick a better-looking
value; the frozen 20/80 (or 20) result is what is being scored against
the corrected CI, never the best of the three.

## Mechanism-doc predictions (P1-P3), summary

Full numbers and interpretation are now in each mechanism doc directly
(Prediction status / Verdict sections, updated this session). Headline:

- **range-contraction P1** (lag decay): partial confirm — magnitude
  decays toward null each day but doesn't vanish by day 3.
- **range-contraction P2** (opex clustering): not confirmed — no
  clustering found (base rate ~= bucket rate).
- **range-contraction P3** (VXN coherence): confirmed cleanly, both
  buckets, predicted direction — the strongest mechanism evidence any
  of the three candidates has.
- **overnight-coil P1** (volume co-movement): confirmed.
- **overnight-coil P2** (opex de-clustering): not confirmed — no
  effect found.
- **overnight-coil P3** (VXN-regime robustness): NOT robust — credible
  in low-VXN, not credible in high-VXN (n=88, thin) — a genuine
  caution matching the project's known regime-concentration failure
  mode.
- **midday-lull P2** (opening->midday persistence): confirmed cleanly
  and symmetrically — general same-day persistence, not midday/
  afternoon-specific.
- **midday-lull P3** (overlap with overnight-coil): ~38% two-way
  overlap, ~1.9x the rate expected under independence — real
  association, not identity. Material for Portfolio's future
  double-counting question, not disqualifying now.

## Verdicts

**range-contraction (hyp-000046/048): ABANDON at Statistical stage.**
Passes all 4 stability/regime/selection checks and gains genuine
mechanism support (P3 especially), but both Validation legs fail the
project's own multiplicity correction — the binding constraint. Ledger
updated (hyp-000048 -> REJECTED, in place, no new id spent).

**overnight-coil (hyp-000056/057): ABANDON at Statistical stage.**
Passes stability and selection-sensitivity; P1 confirmed. But the
Validation leg fails multiplicity correction AND P3 surfaces a genuine
(if thin-sample) regime-concentration caution — two independent reasons
not to advance. Ledger updated (hyp-000057 -> REJECTED, in place, no
new id spent).

**midday-lull narrow leg (hyp-000105/106): ADVANCES to Director
Re-Evaluation.** The only Validation leg, of five checked across all
three candidates, to survive multiplicity correction — and the only
one to also pass every Statistical-stage question cleanly plus gain
two independently-confirmed mechanism predictions. See Director
Re-Evaluation and Monetization positions in
research/sessions/2026-09-10-0815.md. No ledger status change (stays
VALIDATION CANDIDATE — full promotion bar not cleared).
