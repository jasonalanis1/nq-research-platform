# Project-wide multiple-testing exposure -- scoping, method, and first results (2026-09-09)

Status: closes the one open item the mandatory Integrity Gate flagged on H118
(docs/BACKLOG.md, "Agent governance v2 + mandatory Integrity Gate on H118",
2026-09-09): *"project-wide multiple-testing exposure across all [the
ledger's] hypotheses has never been formally quantified."* Logged there as a
LEARN/KNOWN UNEXPLORED infrastructure gap, not an H118 blocker. Picked up per
research/NEXT_UP.md queue item 2 (2026-09-09 automated background session).

Implementation: `src/project_wide_multiplicity.py` (run: from the repo root,
`PYTHONPATH=src python3 src/project_wide_multiplicity.py`). Tests:
`tests/test_project_wide_multiplicity.py` (14 tests, all passing; full suite
202/202 passing after this addition).

## Why this is a different tool from `src/larry_validate.py`, not a duplicate

`larry_validate.py` answers a per-candidate question: was *this* candidate's
winning result picked from among its own close relatives (parameter
neighbors / joint search siblings), and does it survive Deflated Sharpe
Ratio / Probability of Backtest Overfitting against *that* family? It needs
raw per-trade return series (via `purgedcv`), which most post-2026-09-08
Observatory-sourced candidates never saved to disk (only summary n/mean/CI
per stage survive in `data/study_*.json`). It has always undercounted true
project-wide exposure by design -- its own docstring says so.

This module answers the question the Integrity Gate actually asked: across
the *whole project's* history, how many chances has this research program
given itself to find something that looks real by pure chance, and do this
project's live claims survive an honest correction for that? It works
directly off the summary statistics every ledger stage already stores, with
no raw-return dependency, so it applies uniformly to every candidate this
project has ever produced -- old strategy-first hypotheses and new
Observatory-sourced findings alike.

## Method

A true Deflated Sharpe Ratio needs a return series (or at least its skew and
kurtosis) to compute `Var[SR_hat]` correctly; most ledger rows only ever
stored a summary 90% CI. Rather than force a normal-returns assumption onto
a DSR formula and call it precise, this uses the "or equivalent adjustment"
language NEXT_UP's queue item 2 explicitly allows: a **Sidak family-wise
correction** applied to the already-computed 90% CI. Sidak (not the more
common Bonferroni) is the exact answer for independent tests; Bonferroni is
a slightly more conservative approximation to it.

Given n, mean, and an existing single-test 90% CI `[lo, hi]`, the implied
standard error is backed out assuming approximate normality of the sampling
distribution: `SE = (hi - lo) / (2 * z_0.90)`, `z_0.90 = 1.6449`. The
adjusted CI is `mean +/- z_adjusted * SE`, where `z_adjusted` comes from the
Sidak-corrected alpha for `N_trials`. A candidate survives if its adjusted CI
still excludes the null value (0 for R-multiple/point-return effects, 1.0
for the volatility/range RATIO effects -- overnight-coil,
range-contraction, midday-lull).

**Disclosed limitation:** this normal-approximation round-trip only exactly
reproduces an input CI that was already symmetric around the mean. Most of
this project's CIs are bootstrap percentile intervals and are only mildly
asymmetric, so the approximation error is small (a few percent of the
half-width, confirmed in `tests/test_project_wide_multiplicity.py`), but it
is an approximation, not an exact recomputation from raw data.

## The stage-specific N decision -- the most important design choice here

**An earlier draft of this analysis (this same session) applied one
project-wide N to every stage of every candidate uniformly. That is wrong,
and was caught before being logged as a real result.** Discovery is where
the actual data-mining happens (many cells/hypotheses screened, best ones
kept) -- exactly what a multiple-testing correction exists to discipline.
Validation and Holdout are each, by this project's own frozen protocol, a
**single pre-registered test per candidate** on data that candidate never
touched before -- no re-selection, no re-running. Applying the full
Discovery-stage search-space N to a Validation or Holdout result
double-penalizes it for a search it was never part of, and would make the
whole reason the Discovery -> Validation -> Holdout pipeline exists
(converting an uncontrolled multiplicity problem into a controlled one via
fresh, unsearched data) statistically pointless.

The correct family size for a stage is "how many chances did *that stage*
have to produce a false positive, project-wide":

- **Discovery**: every hypothesis ever logged with `data_slice_used ==
  "discovery"`, **plus** every Discovery-Engine scan cell that was screened
  but never promoted to its own ledger row (most of a scan's cells don't
  get promoted -- only survivors do, but all of them were "asked the
  question"). Scan cell counts, sourced from docs/BACKLOG.md (the ledger
  schema has no field for this -- see Limitations below): Scan 001 (48
  cells, 2 promoted: H116, H117 -> 46 unpromoted), Scan 002 (44 cells, 1
  promoted: H118 -> 43 unpromoted).
- **Validation**: every distinct candidate ever sent to its own one-shot
  Validation-slice prospective test, project-wide.
- **Holdout**: every distinct candidate that has ever consumed a Holdout
  Generation 2 slot. As of this analysis: exactly 1 (H118) -- correctly, no
  adjustment applies with N=1; a single test's own 90% CI already is the
  honest answer when nothing else has ever competed for that scarce,
  budgeted resource.

**Counting rule** (what counts as an independent trial vs. paperwork): a
ledger row is excluded if it is a pure post-hoc bookkeeping correction with
no new empirical test of its own -- `strategy_name` ending in
`_STATUS_CORRECTION` / `_PROGRESSION_POINTER`, or `parameters` containing a
`corrects` key, or (for corrections predating that naming convention) notes
containing "ledger hygiene correction" with no `trade_count` of its own. A
correction that *does* carry its own `trade_count` (e.g. hyp-000091's
independent n=85 re-test) is kept -- a genuine second trial, not paperwork.

## Results (computed live from the ledger, 2026-09-09)

Trial counts at time of this analysis: **Discovery N=178** (89 logged +
89 unpromoted scan cells), **Validation N=18**, **Holdout N=1**.

| Candidate | Stage | n | mean | Single-test 90% CI | Sidak-adjusted CI | Survives? |
|---|---|---|---|---|---|---|
| H118 (hyp-000121) | Discovery | 554 | 0.617 | [0.453, 0.785] | [0.270, 0.963] | **YES** |
| H118 (hyp-000122) | Validation | 213 | 0.284 | [0.048, 0.519] | [-0.111, 0.679] | **no** |
| H118 (hyp-000123) | Holdout | 187 | 0.396 | [0.136, 0.650] | [0.139, 0.653] | **YES** |
| Range-contraction narrow (hyp-000046) | Discovery | 412 | 0.836 | [0.802, 0.869] | [0.766, 0.906] | YES |
| Range-contraction wide (hyp-000046) | Discovery | 389 | 1.372 | [1.313, 1.434] | [1.246, 1.498] | YES |
| Range-contraction narrow (hyp-000048) | Validation | 141 | 0.944 | [0.888, 0.998] | [0.852, 1.036] | no |
| Range-contraction wide (hyp-000048) | Validation | 130 | 1.081 | [1.020, 1.143] | [0.978, 1.184] | no |
| Overnight coil (hyp-000056) | Discovery | 332 | 0.783 | [0.747, 0.818] | [0.709, 0.856] | YES |
| Overnight coil (hyp-000057) | Validation | 103 | 0.894 | [0.830, 0.960] | [0.786, 1.003] | no |
| Midday lull narrow (hyp-000105) | Discovery | 411 | 0.713 | [0.686, 0.743] | [0.654, 0.772] | YES |
| Midday lull not-narrow (hyp-00105) | Discovery | 1201 | 1.160 | [1.126, 1.194] | [1.089, 1.231] | YES |
| Midday lull narrow (hyp-00106) | Validation | 142 | 0.816 | [0.762, 0.878] | [0.718, 0.914] | YES |
| Midday lull not-narrow (hyp-00106) | Validation | 404 | 1.091 | [1.037, 1.147] | [0.999, 1.183] | no |

## Interpretation -- read this carefully, it is not a simple pass/fail

Every Discovery-stage result checked here survives even the harsh N=178
correction -- these are large-sample, strong-effect results, which is
expected precisely because Discovery-stage "PROMISING" already selects for
the strongest-looking cells out of everything screened.

The more informative result is at the Validation stage: of the four
distinct findings that have ever cleared their single pre-registered
Validation test at the project's standard (unadjusted) 90% bar --
H118, range-contraction, overnight-coil, and midday-lull -- **only
midday-lull's narrow-bucket sub-test clears an honest N=18 Validation-family
correction.** H118's own Validation result (hyp-000122), the one already
flagged in its own ledger note as "CI lower bound is marginal, essentially
touching zero," does not survive this correction. Neither does either
sub-bucket of range-contraction's Validation test or overnight-coil's.

This does **not** mean these findings are false, and it does not change any
live status on its own (matches the Integrity Gate's original framing:
this is disclosure, not a blocker). What it means concretely:

- **H118's Holdout result is the load-bearing piece of evidence**, and it
  is genuinely strong on its own terms: N=1 at that stage means it faces no
  project-wide multiplicity discount at all, by design (only one candidate
  has ever competed for a Holdout Gen2 slot). H118's ongoing paper-only
  Forward Validation (research/forward_validation/h118_forward_log.jsonl) is
  now the single most information-dense test available -- every new
  forward week is out-of-sample data that was never part of Discovery,
  Validation, *or* this multiplicity accounting, which only weighs
  already-searched slices.
- H118's own Validation-stage result should be read as weaker corroboration
  than its raw "PROSPECTIVE_PASS" label implies, once you account for the
  fact that 17 *other* candidates have also each had one shot at the same
  gate. This is exactly why the Holdout stage exists as a further, scarcer
  check rather than stopping at Validation.
- Range-contraction, overnight-coil, and midday-lull (the three
  already-built-into-`src/volatility_conditioning.py` volatility/range
  characterizations, per hyp-000129) should be treated as **plausible,
  useful risk-sizing inputs, not as independently-confirmed standalone
  findings** at the Validation-stage confidence level their raw CIs imply.
  Their Discovery-stage evidence remains strong; nothing here says these
  characterizations are wrong, only that the Validation-stage confirmation
  specifically is less conclusive, project-wide, than a single 90% CI
  suggests.

## Limitations, disclosed rather than hidden

1. `N_DISCOVERY`'s "unpromoted scan cells" addend (89) is a **floor**, not a
   ceiling. It only counts cells from the two named, formally-documented
   Discovery Engine scans (Scan 001, Scan 002). Earlier exploratory work
   (the 2026-08-24 - 09-01 strategy-first hypotheses, the 2026-09-08
   intraday-behavior batch 1/2/3 studies, Observatory v1-v6) also screened
   multiple related configurations without a per-cell count ever being
   written down, and is NOT included here. If anything, the true Discovery-
   stage correction should be at least this harsh, possibly harsher.
2. The Sidak/normal-approximation method is a documented substitute for a
   true Deflated Sharpe Ratio, chosen because most candidates lack a saved
   raw per-trade return series. Where a raw return series IS available
   (the level_sweep liquidity-filter family), `src/larry_validate.py`'s
   DSR/PBO path remains the more precise tool and should be preferred.
3. This is a first application, not a continuously-running gate. Re-run by
   hand as new candidates reach Validation/Holdout, and update
   `SCAN_REGISTRY` in `src/project_wide_multiplicity.py` whenever a new
   Discovery Engine scan runs -- both are currently manual steps.

## Recommendation

No status change to any existing hypothesis follows automatically from this
analysis (per the Integrity Gate's own framing: an open infrastructure gap,
not a blocker). Recorded here, in the ledger (see hyp referencing this
study), and in docs/BACKLOG.md so future sessions read H118's Validation
"PROSPECTIVE_PASS" and the three volatility-characterization Validation
passes with this context attached, rather than at face value.
