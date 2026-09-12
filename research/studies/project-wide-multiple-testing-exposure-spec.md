# Project-Wide Multiple-Testing Exposure -- Frozen Methodology Spec

Written 2026-09-09 (automated session), addressing the gap the H118
Integrity Gate itself flagged and docs/BACKLOG.md logged as a
LEARN/KNOWN UNEXPLORED infrastructure gap: "only Scan 002's own 44
cells accounted for; no project-wide (123-hypothesis) multiple-testing
/deflated-Sharpe adjustment has ever been computed." This is NEXT_UP
queue item 2. Per standing protocol, the counting method is decided and
frozen BEFORE using it to re-examine any currently-standing result
(H118, the two validated volatility-persistence findings, etc.) -- the
method is not to be adjusted afterward based on whether a favored
result survives it.

## What already exists and is reused, not rebuilt

`src/larry_validate.py` already wires Bailey & Lopez de Prado's
Deflated Sharpe Ratio (DSR) and Probability of Backtest Overfitting
(PBO) via the third-party `purgedcv` library, with decided thresholds
(DSR_PASS_THRESHOLD=0.90, PBO_FAIL_THRESHOLD=0.25, AND logic). It
already supports an explicit `n_trials_override`. What has never been
supplied is an honest, PROJECT-WIDE trial count -- every prior
application scoped `n_trials` to one family (e.g. the Level Sweep
Reversal liquidity-filter siblings) or, per the H118 gate note, to one
scan's own cell count (44). This spec defines how to compute the
project-wide count instead.

## Counting rule (decided, mechanical, reproducible)

Two components, summed:

1. **Scan-cell exposure** -- every combinatorial cell mechanically
   screened by a multi-candidate scan against Discovery-slice data.
   Counted directly from each scan's own saved results JSON, using its
   authoritative scanned-count field (`combinations_scanned` for
   Observatory v1-v6, `total_cells` for market_behavior_discovery_scan
   001/002) rather than the (sometimes smaller) list of candidates
   actually written to disk after internal pre-filtering -- the
   pre-filtered-out cells were still looks taken, and undercounting
   them would understate exposure, the unsafe direction.
2. **Standalone hypothesis exposure** -- every distinct ledger
   hypothesis (unique `hypothesis_id`, latest state) with
   `data_slice_used == "discovery"`, EXCLUDING pure ledger-hygiene
   rows (STATUS_CORRECTION / PROGRESSION_POINTER / no-new-test
   corrections), counted as 1 trial each. This captures every
   hypothesis tested one-at-a-time outside the big scan framework
   (the ~20 bar-pattern/candlestick hypotheses, the ~10 cross-asset
   standalone signals, the legacy strategy-first re-mines, the
   Observatory-derived monetization attempts such as H92/H93,
   H116-H118, etc.)

Total N = component 1 + component 2, with NO further attempt to
deduplicate the small number of hypotheses that are themselves
monetization follow-ups on an already-scanned cell (e.g. H92/H93
following OBS-FINDING-009; H116-H118 following Scan 002's cells).
This is a deliberate, disclosed simplification: it double-counts a
handful of cells (at most ~7 of ~1380, well under 1%) rather than
building a fragile cross-reference between heterogeneous scan and
ledger schemas. Overcounting trials makes DSR MORE conservative
(harder to pass) -- the safe direction for a correction whose whole
purpose is to guard against false-positive over-confidence. Undercounting
would be the dangerous direction, so where a choice must be made
between the two this spec always chooses the direction that counts a
trial rather than omits one.

## What this total is used for

- DSR is computable at the full project-wide N, using each
  candidate's own per-trade returns as `winner_returns` -- DSR only
  needs a scalar trial count, not a matching set of sibling return
series.
- PBO is NOT computable at the full project-wide level -- it requires
  a common (n_configs x n_obs) return matrix across every competing
  trial, which does not exist across ~1380 heterogeneous studies
  spanning different instruments, horizons, and methods. PBO stays
  scoped to homogeneous within-family applications only (as already
  done for the Level Sweep Reversal family); this spec does not claim
  otherwise.
- Applied first to H118 (hyp-000121, the only candidate that has
  consumed a Holdout Generation 2 slot and carries a live, if paper-only,
  forward position) as the highest-stakes case. May be applied to
  other standing candidates afterward using the same frozen N.

## Explicit limitations (disclosed, not hidden)

- This counts *saved, documented* looks. Any exploratory attempt that
  was tried and never written to a results file is invisible to this
  method and is a residual understatement risk -- the true exposure is
  at least this large, plausibly larger, never smaller. Read the
  resulting DSR as an upper bound on the candidate's trial-adjusted
  credibility, not a precise final number.
- This is a global, per-candidate DSR against total project search
  breadth. It is a stronger (more conservative) correction than the
  project's existing practice of scoping trial counts to a single
  hypothesis family, and is intentionally so.
