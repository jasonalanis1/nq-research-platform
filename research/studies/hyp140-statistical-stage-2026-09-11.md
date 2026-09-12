# Statistical stage -- hyp-000140 (|gap_vs_atr| magnitude, same-day RTH range)

Run: 2026-09-11 (interactive session, Jason present), src/statistical_stage_hyp140.py.
Scope: Discovery-stage data only (2015-01-01 -> 2021-10-03), the same sample Scan 010
used. Frozen from Scan 010 / idea_inventory.md Entry 5, no retuning: state variable
`abs(gap_vs_atr)` terciled, outcome same-day RTH range vs its own trailing-20d average.
Candidate cells: LOW (compression) and HIGH (elevation), both credible in Scan 010.

## Baseline (reproduced, unchanged from Scan 010)

LOW: n=556, mean=0.9130, ci_90=[0.8806, 0.9454], credible.
HIGH: n=556, mean=1.1921, ci_90=[1.1468, 1.2372], credible.

## Q1 -- Stability (chronological split-sample)

LOW first half: n=313, mean=0.9123, ci_90=[0.8710, 0.9592], credible.
LOW second half: n=243, mean=0.9139, ci_90=[0.8644, 0.9652], credible.
HIGH first half: n=240, mean=1.1947, ci_90=[1.1221, 1.2731], credible.
HIGH second half: n=316, mean=1.1902, ci_90=[1.1357, 1.2468], credible.

Both cells: same sign in both halves, BOTH halves independently credible. PASSES
cleanly -- this is not a result that only holds in one part of the sample.

## Q2 -- Regime dependence (trailing-avg-RTH-range median split)

LOW low-range-regime: n=298, mean=0.9236, credible. LOW high-range-regime: n=258,
mean=0.9007, credible. HIGH low-range-regime: n=259, mean=1.2476, credible. HIGH
high-range-regime: n=297, mean=1.1438, credible.

Neither cell is concentrated in one volatility regime -- both hold in both. PASSES.

## Q3 -- Magnitude (project-wide multiplicity correction, binding constraint)

LOW: raw CI=[0.8806, 0.9454], Sidak-adjusted CI=[0.8430, 0.9830], SURVIVES. |deviation
from 1.0|=0.0870, clears the 0.05 economic-meaningfulness floor.
HIGH: raw CI=[1.1468, 1.2372], Sidak-adjusted CI=[1.0944, 1.2898], SURVIVES. |deviation
from 1.0|=0.1921, clears the 0.05 floor comfortably.

This is the binding constraint that closed hyp-000139 (Sidak-adjusted CI crossed zero
there). Here BOTH cells survive the same correction with room to spare -- this
candidate is materially stronger on the project's own strictest test than the prior
Triage candidate was.

## Q4 -- Selection sensitivity (bucket width around frozen terciles)

Quintile (20%): top mean=1.2702 credible, bottom mean=0.9183 credible.
Tercile (33.33%, frozen): top mean=1.1921 credible, bottom mean=0.9130 credible.
Quartile (25%): top mean=1.2498 credible, bottom mean=0.9131 credible.

Consistent, monotonic-with-width pattern across all three cuts -- not a knife-edge
property of the exact tercile boundary. PASSES.

## Same-data selection disclosure

The `abs(gap_vs_atr)` state variable, the RTH-range-vs-trailing-20d-avg outcome, and
the tercile cut were all fixed by Scan 010 / Entry 5 before this candidate's Discovery
result was seen. Q1-Q3 reuse that frozen construction unmodified. Q4 deliberately
varies the selection threshold but is diagnostic, not a retune -- the frozen tercile
result is what is being scored.

## Mechanism-doc predictions (P1-P3, from research/mechanisms/abs-gap-vs-atr-same-day-range-magnitude.md)

**P1 (validated-vs-faded split) -- NOT CONFIRMED, ran the OPPOSITE way.** The doc
predicted elevation concentrated in the "validated" subgroup (first-RTH-hour move
continues the gap's direction). Instead: validated n=276, mean=1.1249, credible;
faded n=280, mean=1.2585, credible -- the FADED subgroup shows the stronger elevation.
Per the doc's own Section 4 falsification condition, this means the "volume confirms
the gap is real" reframe FAILS, and the underlying P3 anomaly (from Scan 010) remains
genuinely unexplained rather than resolved by this document's reframe.

**P2 (full volume x gap-magnitude grid) -- ONE-SIDED, not symmetric.** HIGH-gap cell:
monotonic increasing with volume (low-vol mean=0.9992 not credible -> mid-vol
mean=1.0383 not credible -> high-vol mean=1.4306 credible) -- CONFIRMED. LOW-gap cell:
NOT monotonic decreasing with volume (low-vol mean=0.7753 credible -> mid-vol
mean=0.9387 not credible -> high-vol mean=1.0956 credible -- U-shaped, not a clean
decreasing trend). Per the doc's own Section 4, a one-sided relationship (volume
matters for elevation but not, in a clean monotonic way, for compression) points
toward something specific to large gaps rather than a general volume-amplifies-
repricing story.

**P3 (volume-tercile re-cut of the original median split) -- CONFIRMED, robust.**
low-vol n=86 mean=0.9992 not credible; mid-vol n=127 mean=1.0383 not credible;
high-vol n=181 mean=1.4306 credible. Monotonic increasing, preserved under a finer
cut -- NOT an artifact of the original median-split construction. The volume-
conditioning effect on HIGH-gap days is real and reproducible, just still without a
confirmed causal story for why.

## Verdict

**Q1-Q4 all PASS, including Q3 -- the binding multiplicity constraint that closed
hyp-000139.** Both cells (LOW compression, HIGH elevation) are stable across time,
regime-independent, robust to selection-boundary width, and survive project-wide
Sidak correction with meaningful economic magnitude. On the project's own strictest
tests, hyp-000140's core empirical finding is materially stronger than any other
Discovery-stage candidate this project has produced to date.

The mechanism doc's own reframe for the P3 anomaly (Section 3, "volume confirms the
gap is real") does NOT survive its own falsification test (P1 ran backwards) and its
secondary prediction (P2) only holds on one side. The P3 volume-conditioning effect
itself is real and robust (confirmed under a finer cut), but WHY it happens remains
unresolved -- the reframe was a coherent hypothesis, tested honestly, and it did not
hold up. This is not a reason to reject the candidate; the primary elevation/
compression finding does not depend on the P3 story being correct. It IS a reason to
flag the candidate's mechanism section as incomplete: hyp-000140 has strong empirical
support and a plausible but partially disconfirmed causal account.

Disposition: **PROMOTE to Director Re-Evaluation.** Unlike hyp-000139 (closed at this
exact stage on the Q3 multiplicity test), hyp-000140 clears every Statistical-stage
test on the primary cells. The unresolved P3 mechanism question does not block
Director Re-Evaluation or Monetization design under the MECHANISM GATE (a doc exists
and was tested in good faith); it is carried forward as an open research question, not
a blocker. Ledger status: PROMISING, unchanged (Statistical stage does not itself
promote to VALIDATED -- that requires Director Re-Evaluation + Monetization +
Integrity Gate in sequence, per AGENT PROTOCOL).
