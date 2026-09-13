# Šidák stacking diagnosis (UPGRADE QUEUE v3, U1) — READ-ONLY

Written: September 13th, ~5:15 pm CT, interactive test cycle. No code changed, no
bar changed. Question from outside review A: "project-wide Šidák at ~275 trials,
stacked on two out-of-sample confirmations, double-counts and is why nothing
clears." Does it?

## What the code actually does (`src/project_wide_multiplicity.py`)
The correction is **stage-specific by design**, not one project-wide N applied
everywhere. `compute_stage_trial_counts()` returns three separate family sizes,
recomputed live from the ledger every call:

| Stage | N today | How N is built | Šidák z (vs 1.645 single-test) | Per-test alpha |
|---|---:|---|---:|---:|
| Discovery | **451** | 110 logged Discovery rows + 341 unpromoted scan cells (SCAN_REGISTRY) | 3.680 | 0.00023 |
| Validation | **20** | number of Validation-slice tests ever logged | 2.791 | 0.00525 |
| Holdout | **3** | number of Holdout tests ever logged | 2.114 | 0.03451 |

The module docstring explicitly records that an earlier draft applied one
project-wide N to every stage, calls that WRONG, and explains why: Validation and
Holdout are single pre-registered tests per candidate on data the candidate never
touched, so applying the Discovery search-space N to them "double-penalizes it for a
search it was never part of."

## Verified against the two Holdout-passed cases
- **hyp-000142/144/151 (VXN level → next-day range):** Statistical stage used
  N_discovery=302 (Sept 12th). Validation used N_validation=19 ("Sidak count computed
  live (validation=19)" in the blind Gate record). Holdout used N_holdout at the time.
  Three different N's, each counting only its own stage's tests.
- **hyp-000105/106/141 (midday-lull → afternoon range):** same construction.
"Šidák is cumulative across attempts" in the Gate record means cumulative *within a
stage* (every Validation test ever run counts toward N_validation), not Discovery
trials carried into Validation.

## Verdict on review A's claim
**Does NOT double-count.** Discovery trials are never re-counted at Validation or
Holdout. The "~275" figure was N_discovery at the time hyp-000139 closed (Sept 11th);
it is 451 today.

## What IS true, and worth a decision (not made here)
1. **The Discovery bar rises monotonically for the life of the project.** Every scan
   cell ever run is added to N_discovery forever (275 → 302 → 451 in three days).
   A Discovery effect today must clear a CI 2.24× wider than a single test
   (z 3.68 vs 1.645). That is what review A is really pointing at: a strict
   Discovery-stage correction *and* a mandatory out-of-sample confirmation. The two
   are not double-counting each other, but they are two independent controls on
   the same false-discovery risk, and the first one keeps tightening.
2. **Concrete cost so far:** hyp-000139 (Sept 11th) closed on Q3 alone — raw
   Discovery CI [-0.137, -0.010] excluded zero; Šidák-adjusted at N=275 did not. It
   never reached Validation, which is the stage designed to catch exactly that.
3. **Review A's alternative** — control multiplicity *within a scan* (false discovery
   rate over the registered cells), and let Validation/Holdout be the project-wide
   control — is a coherent policy. It would have sent hyp-000139 to a one-shot
   Validation instead of closing it. It would also let more Discovery-stage
   candidates through to consume Validation attempts, which are themselves counted
   (N_validation would grow faster).
4. Either policy is defensible. Switching is a **bar change** and Jason's call. This
   diagnosis makes no recommendation beyond: the double-counting claim is false; the
   "Discovery bar tightens forever" observation is true and has already closed one
   candidate that Validation could have judged.
