# Intraday Behavior Batch 1 — Prospective Validation Spec (2026-09-08)

exp-075/076 — pre-registered prospective tests of exp-072 (volume-profile
skew) and exp-074 (range-contraction cycle), the two Step-1 PASS results
from `intraday-behavior-batch1-spec.md`. Both run, unmodified, on the
Validation slice (2021-10-04 to 2024-01-03) -- genuinely new data for these
two signal families. All thresholds, windows, and the diff-vs-complement
method are carried over exactly as frozen in batch 1; no retuning of the
front-load window, z-threshold, lookback, or percentile cutoffs. exp-073
(momentum burst) already failed Step 1 and is closed -- no prospective test.

Per the standing no-retuning rule and the effect-size-inflation
diagnostic's finding (4/4 prior Discovery-PROMISING results failed their
first prospective test), a Validation-slice failure here closes each line
for good; a pass would still only make it PROMISING-confirmed, not itself
sufficient for a costed rule or live authorization (Step 2 + Advisor
review + Jason sign-off would follow, unchanged from every prior line).

**exp-075 (volume-profile skew, Validation slice):** same front_loaded /
back_loaded classification and diff-vs-complement test as exp-072, run on
Validation-slice days only (trailing 20-day stats computed continuously
across Discovery+Validation for warm-up continuity, matching this
project's standard convention -- only Validation-window days scored as the
outcome).

**exp-076 (range-contraction cycle, Validation slice):** same narrow/wide
classification (own trailing 20-day percentile) and next-day range-ratio
outcome as exp-074, same continuity convention, Validation-window days
only.
