# H118 — one-shot Integrity Gate review of the multiplicity finding (2026-09-09)

PRE-REGISTERED AS ONE-SHOT before it was run, on Jason's explicit
authorization. This review happens ONCE for this finding and is recorded
here. It is not reopened. Automated work sessions may not revisit it
(see the scope boundary in research/NEXT_UP.md).

## What prompted it
research/studies/project-wide-multiplicity-2026-09-09.md applied a Sidak
family-wise correction with stage-specific N. H118's Discovery
([0.270, 0.963]) and Holdout ([0.139, 0.653]) intervals survive; its
Validation interval ([-0.111, 0.679]) does not.

## VERDICT: CONDITIONAL PASS
Status unchanged: Forward Validation, paper only, no capital. No veto.

Reasoning: nothing was refit, tercile edges stayed frozen from Discovery
through Holdout, the Holdout is clean and needs no correction, and no
capital is at risk. But the corrected Validation failure is material new
information and the recorded effect size is optimistic, so an
unconditional pass would overstate what is established.

## Findings
1. The Sidak-by-N=18 lens is appropriate here. The 18 Validation tests are
   not independent shots at unrelated questions -- they are the survivor
   set of a Discovery search, and H118 reached Validation because it looked
   best. That is winner's-curse geometry, which is what family-wise
   correction exists for. Imperfect in both directions (the 18 tests are
   correlated, so Sidak is conservative; N_discovery=178 is a floor, so
   true search space is larger), but the corrected view is the honest one.
2. The surviving Holdout partially but not fully rescues it. It is the only
   never-touched data and the most informative number on file, but n=187
   with a lower bound of 0.139 sits uncomfortably near zero, and the point
   estimates decay monotonically (0.62 -> 0.28 -> 0.40) in the direction
   decay runs when Discovery is inflated. What survives is "plausibly real,
   magnitude likely near 0.2-0.3R, not 0.6R" -- above the 0.05R bar, with
   far less margin than the raw record implies.

## Conditions attached (all three required)
1. Re-baseline the working effect estimate for H118 to the Holdout figure
   (~0.40R, lower bound 0.14R). The 0.62R Discovery number is not to be
   quoted as the expected effect anywhere.
2. Record the corrected Validation interval alongside the original in the
   candidate's file.
3. Lock the forward review point below, in writing, before the next signal
   fires. Done by this document.

## Forward review point — PRE-REGISTERED, ONE LOOK
H118 gets exactly ONE Paper Verified evaluation, triggered when BOTH are
true (whichever comes later):
  - 40 resolved forward trades, AND
  - 12 elapsed calendar months of forward tracking.
Rationale: signals fire on ~26% of trading days with 10-day holds, so
consecutive trades share most of their window -- roughly one independent
10-day window per ~4 signals. 40 resolved trades is therefore only ~8-10
effectively independent observations. Thin, but honest. Non-overlapping-
only trades were rejected as a requirement (discards real signals, triples
elapsed time).
Compute the review CI on BLOCK-BOOTSTRAPPED 10-day blocks, never treating
the 40 trades as independent.
NO interim peeking. NO early promotion on a good run. One look.

Live-capital authorization remains a separate explicit decision by Jason
regardless of any statistical result, per standing project rule.
