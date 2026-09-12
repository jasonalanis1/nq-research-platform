# Statistical stage — hyp-000139 (overnight-vs-RTH divergence, HIGH tercile, reversion)

Automated session, 2026-09-11 (~07:51-08:xx UTC). NEXT_UP.md queue item 0.
Code: src/statistical_stage_hyp139.py. Raw output: data/statistical_stage_hyp139_results.json.

## Scope and method

Discovery-slice data only (2015-01-01 -> 2021-10-03), the same sample Scan 008
used — hyp-000139 has no Validation result yet, so this stays Discovery-only
rather than pulling in Validation before the candidate has cleared Triage/
Statistical/Director Re-Eval/Monetization/Integrity in order. Frozen from
Scan 008 / idea_inventory.md Entry 3, unmodified: 20-day trailing
overnight-minus-RTH divergence, ATR-normalized, terciled; outcome is today's
own overnight-minus-RTH divergence; HIGH tercile only (the one credible cell).
Bootstrap CIs: 3000 resamples, seed=8 (Scan 008's own seed, reused), 90%.

Baseline reproduced exactly: n=364, mean=-0.0746, ci_90=[-0.1371, -0.0099],
credible. Matches data/market_behavior_discovery_scan_008_results.json exactly.

## Q1 — Stability (chronological split-sample)

| Leg | n | mean | ci_90 | credible |
|---|---|---|---|---|
| first_half (to 2018-06-29) | 187 | -0.0484 | [-0.1387, 0.0415] | NO |
| second_half (2018-06-29 on) | 177 | -0.1023 | [-0.1981, -0.0093] | yes |

Same sign both halves, but only the second half is independently credible —
the full-sample credibility is not evenly distributed across time. Not a
sign flip (the Scan-003 failure mode), but a real power/consistency caution:
half the sample alone does not clear the bar.

## Q2 — Regime dependence (trailing ATR14 median split)

| Leg | n | mean | ci_90 | credible |
|---|---|---|---|---|
| low_vol | 151 | -0.0853 | [-0.1991, 0.0210] | NO |
| high_vol | 213 | -0.0670 | [-0.1469, 0.0083] | NO |

Neither volatility-regime half is independently credible — the full-sample
result is not concentrated in one regime (no red flag of that specific
shape), but it also does not survive being cut in half by ANY of the three
splits tried so far (Q1 first-half, Q2 low-vol, Q2 high-vol). That is a
genuine power/fragility concern distinct from regime-concentration.

## Q3 — Magnitude (project-wide multiplicity correction)

Discovery-stage trial count (src/project_wide_multiplicity.py,
compute_stage_trial_counts(), live at run time): 275.

Raw CI: [-0.1371, -0.0099]. Sidak-adjusted CI (discovery, N=275):
[-0.2119, 0.0626] — **crosses zero, does NOT survive adjustment.**

|mean| = 0.0746 ATR units, clears the project's 0.05 economic-meaningfulness
floor on its own — but the adjusted CI is the binding constraint, same
convention this project has applied to every prior candidate (range-
contraction, overnight-coil all failed this same check 2026-09-10 despite
clearing the raw CI and the floor).

## Q4 — Selection sensitivity (bucket width around frozen tercile)

| Cut | n | mean | ci_90 | credible |
|---|---|---|---|---|
| top 20% | 219 | -0.0843 | [-0.1605, -0.0065] | yes |
| top 33.33% (frozen) | 364 | -0.0746 | [-0.1371, -0.0099] | yes |
| top 25% | 273 | -0.0612 | [-0.1280, 0.0066] | NO |

Not a fragile knife-edge in one direction (20% still credible), but the
25% cut alone loses credibility — a real, if modest, selection-sensitivity
flag, not the clean insensitivity range-contraction/overnight-coil/
midday-lull showed on 2026-09-10.

## Same-data selection disclosure

The 20-day window, tercile cut, and HIGH-tercile focus were fixed by Scan
008/Entry 3 before any Discovery result was seen (single pre-registered
shot). Q1-Q3 reuse that frozen construction unmodified. Q4 varies the
threshold diagnostically; the frozen 33.33% result is what is scored, never
the best-looking alternative.

## Mechanism-doc predictions (P1-P3, research/mechanisms/overnight-rth-divergence-reversion-high-tercile.md)

**P1 — overnight-driven vs RTH-driven subgroup split.** Mechanical story
predicts same sign/magnitude in both subgroups; entry's own P1 (real
overnight-specific flow) predicts concentration in overnight-driven only.

| Subgroup | n | mean | ci_90 | credible |
|---|---|---|---|---|
| overnight-driven | 147 | -0.0758 | [-0.1793, 0.0163] | NO |
| RTH-driven | 217 | -0.0738 | [-0.1552, 0.0125] | NO |

Same sign, similar magnitude — consistent with the mechanical story's shape
(not concentrated in the overnight-driven subgroup as the entry's original
persistence story would require) — but **neither subgroup is independently
credible**, so this is a directionally-consistent-but-underpowered result,
not a clean confirmation.

**P2 — window-length generalization (10d, 30d).**

| Window | n | mean | ci_90 | credible |
|---|---|---|---|---|
| 10d | 451 | -0.0609 | [-0.1178, -0.0038] | yes |
| 30d | 279 | -0.0886 | [-0.1603, -0.0210] | yes |

**Confirmed** — both neighboring windows show the same-signed, credible
reversion. Not a 20-day-only knife-edge. This is the one prediction that
comes back clean and does genuinely support the mechanical-reversion
reading over a pure Discovery-stage artifact of the specific window chosen.

**P3 — volume-conditioned reversion strength.**

| Subset | n | mean | ci_90 | credible |
|---|---|---|---|---|
| low-volume | 182 | 0.0130 | [-0.0581, 0.0867] | NO |
| high-volume | 182 | -0.1622 | [-0.2718, -0.0646] | yes |

**Not confirmed — and the result is the opposite of what the mechanical
story predicts.** The mechanical/stretched-statistic story (mechanism doc
Section 2/3) explicitly predicts volume-INDEPENDENCE: a pure
autocorrelation-of-noisy-sums effect should not care about participation.
Instead the reversion is essentially ALL in the high-volume subset (credible,
more than 2x the full-sample magnitude) and ABSENT in the low-volume subset
(not credible, wrong-signed point estimate). This is the mechanism doc's own
falsification condition (Section 4): "if P3 shows the reversion is equally
strong or stronger in low-volume subperiods, that weakens the mechanical
reading" — this ran the other way (stronger in HIGH volume), which still
weakens the mechanical-artifact reading, just not via the specific path the
doc anticipated. It is, however, consistent with a real, volume-participation
-linked flow effect — which is exactly the entry's own original P1 story
the Discovery result was supposed to have disfavored. The picture is now
genuinely mixed, not merely "mechanical, weak counterparty."

## Verdict

Q3 (magnitude) is the binding constraint and this candidate **fails it**:
the Sidak-adjusted 90% CI at the current Discovery-stage trial count (275)
crosses zero. That alone is normally sufficient to close a candidate at
Statistical per this project's established convention (range-contraction
and overnight-coil both closed on exactly this basis 2026-09-10 despite
otherwise-clean stability and regime checks). hyp-000139 additionally fails
Q1 (only one of two chronological halves independently credible) and shows
a real Q4 selection-sensitivity flag (25% cut loses credibility) — this
candidate is weaker on the 4 questions than any of the three candidates
Statistical closed favorably in the 2026-09-10 pass.

The mechanism predictions are genuinely mixed rather than uniformly
unfavorable: P2 (window generalization) confirms cleanly, and P1's
directional shape (same sign both subgroups) is consistent with the
mechanical story even though underpowered. But P3 directly contradicts the
mechanical story's own volume-independence prediction, undercutting the
"stretched z-score, no real counterparty" reading the mechanism doc used as
its most-defensible position — and does so without replacing it with a
credible alternative (the entry's own original P1/persistence story
predicted the OPPOSITE sign from what Scan 008 found).

**RECOMMENDATION: REJECT at Statistical.** Primary reason: fails the
project-wide multiplicity-corrected magnitude check (Q3), this project's
established binding constraint. Secondary: fails Q1 split-sample robustness
(one half not independently credible) and shows a genuine, if mild,
selection-sensitivity flag (Q4). The mechanism-doc predictions do not save
it — they resolve to a mixed, partially self-contradicting picture (P2
supports, P3 actively undercuts the doc's own stated mechanism) rather than
a clear confirmation that would argue for spending further research capital
regardless of the magnitude failure.

Per AGENT PROTOCOL, Director Re-Evaluation's question ("does this evidence
justify spending a Monetization + Integrity + confirmation-pipeline cycle?")
is answered NO by this Statistical result on its own terms — not deferred to
a separate Director session, since the 4-question result is unambiguous on
the binding constraint (Q3) and the session already has the full picture in
hand. No staff meeting trigger is met (not a zero-survivor scan, no second
RETURN, no conflicting agent recommendations, not requested) — this is an
ordinary single-candidate Statistical-stage closure, the normal path.
