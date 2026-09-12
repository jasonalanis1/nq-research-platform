"""
project_wide_multiplicity.py
=============================

WHAT THIS FILE DOES (plain English):
Closes the one open item the mandatory Integrity Gate flagged on H118
(2026-09-09, docs/BACKLOG.md "Agent governance v2 + mandatory Integrity
Gate on H118"): "project-wide multiple-testing exposure across all
[the ledger's] hypotheses has never been formally quantified." Logged
there as a LEARN/KNOWN UNEXPLORED infrastructure gap, not an H118
blocker, and picked up here per research/NEXT_UP.md queue item 2.

WHY THIS IS A DIFFERENT TOOL FROM src/larry_validate.py, NOT A DUPLICATE:
larry_validate.py answers "was THIS candidate's own winning result
picked from among its own close relatives (parameter neighbors / joint
search siblings), and does it survive Deflated Sharpe / PBO against
THAT family?" -- a per-candidate, lineage- or search-batch-scoped
question, using the `purgedcv` library on raw per-trade return series.
It has always undercounted the true project-wide exposure by design
(its own docstring says so): it only ever looks at one candidate's
immediate family, never the whole ledger, and it needs raw per-trade
returns, which most post-2026-09-08 Observatory-sourced candidates
don't have saved to disk (only summary n/mean/CI per stage).

This module answers the different question the Integrity Gate actually
asked: "across the WHOLE PROJECT's history, how many chances has this
research program given itself to find something that looks real by pure
chance, and do this project's live claims survive an honest correction
for that?" It works directly off the summary statistics (n, mean, 90%
CI) every ledger stage already stores, with no raw-return-series
dependency -- deliberately, so it can be applied uniformly across every
candidate this project has ever produced, old and new alike, not just
the handful with per-trade CSVs on disk.

METHOD -- CHOSEN, WITH REASONING (2026-09-09):
A true Deflated Sharpe Ratio needs a return series (or at least its
estimated skew/kurtosis) to compute Var[SR_hat] correctly; most rows in
this ledger only ever stored the summary CI. Rather than force a
normal-returns assumption onto a DSR formula and call it precise, this
module uses the "or equivalent adjustment" language NEXT_UP.md's queue
item 2 explicitly allows: a Sidak family-wise correction applied to the
ALREADY-COMPUTED 90% bootstrap/analytic CI. Sidak (not the more common
Bonferroni) is used because it is the exact, non-conservative-beyond-
what's-needed answer for independent tests (Bonferroni is a slightly
more conservative approximation to it) -- and because this project's own
docstrings elsewhere favor being precise about which correction is being
applied and why, not defaulting to the roughest available one.

Given n, mean, and an existing single-test 90% CI [lo, hi], the
implied standard error is backed out assuming approximate normality of
the sampling distribution (SE = (hi - lo) / (2 * z_0.90), z_0.90 =
1.6449) -- exactly the same normal-approximation the project's own
confidence_analysis.py bootstrap CIs are reported alongside elsewhere.
The adjusted CI is then mean +/- z_adjusted * SE, where z_adjusted comes
from the Sidak-corrected alpha for N_trials. A candidate whose adjusted
CI still excludes the null value (0 for R-multiple/point return
effects, 1.0 for the volatility/range RATIO effects like the overnight-
coil and range-contraction/midday-lull families) survives; otherwise it
doesn't.

THE STAGE-SPECIFIC N DECISION -- THE MOST IMPORTANT DESIGN CHOICE HERE,
GET THIS WRONG AND THE WHOLE ADJUSTMENT MISLEADS RATHER THAN HELPS:
An earlier draft of this script (2026-09-09, this same session) applied
ONE project-wide N to every stage of every candidate uniformly. That is
WRONG and was caught before being logged as a real result: Discovery is
where the actual data-mining happens (many cells/hypotheses screened,
best ones kept) -- that is exactly what a multiple-testing correction
exists to discipline. Validation and Holdout are, by this project's own
frozen protocol, each a SINGLE pre-registered test per candidate on
data that specific candidate never touched before -- there is no
re-selection, no re-running, no picking the best of several tries at
that stage for a given candidate. Applying the full Discovery-stage
search-space N to a Validation or Holdout result double-penalizes it
for a search it was never part of, and would make the Discovery ->
Validation -> Holdout pipeline's whole reason for existing (converting
an uncontrolled multiplicity problem into a controlled one via fresh
unsearched data) statistically pointless.

The correct family size for a stage is "how many chances did THAT
STAGE have to produce a false positive project-wide", which is:
  - Discovery: every cell/hypothesis ever screened at the Discovery
    step, INCLUDING Discovery-Engine scan cells that were screened but
    never promoted to their own ledger hypothesis_id (most of a scan's
    cells don't get promoted -- only the survivors do, but all of them
    were "asked the question").
  - Validation: every DISTINCT candidate that has ever been sent to its
    own one-shot Validation-slice prospective test, project-wide (each
    such candidate is one chance for a false positive to slip through
    the Validation gate; the fact that any one candidate only gets ONE
    Validation attempt is what keeps this number from being much larger
    than the Discovery-stage figure, not what excuses ignoring it).
  - Holdout: every DISTINCT candidate that has ever consumed a Holdout
    Generation 2 slot. As of 2026-09-09 that is exactly 1 (H118) -- with
    N=1 there is, correctly, no adjustment: a single test's own 90% CI
    already is the honest answer when nothing else has ever competed
    for that same scarce resource. This matches the project's explicit
    5-slot Holdout budget by design, not a coincidence to paper over.

Counting rule for "how many distinct hypotheses has this project ever
logged": a ledger row is EXCLUDED from the count (does not represent an
independent trial) if it is a pure post-hoc bookkeeping correction that
adds no new empirical test of its own -- identified structurally as:
strategy_name ending in "_STATUS_CORRECTION", "_PROGRESSION_POINTER", or
"_MULTIPLICITY_REEXPRESSION", OR parameters containing a "corrects" or
"reexpresses" key, OR (for the small number of corrections logged
before that naming convention existed, 2026-09-08 night) notes
containing "ledger hygiene correction" with no trade_count of its own.
This module's own re-expression rows (hyp-000130 through hyp-000133,
2026-09-09) are themselves excluded by this same rule -- they carry no
independent trial of their own, so a future re-run must not count them
as new Discovery/Validation/Holdout trials, which would otherwise
silently inflate every N by re-counting the same underlying candidates
this module already re-expressed. A correction row that DOES carry its own trade_count (e.g.
hyp-000091's independent n=85 re-test) is kept -- it is a genuine second
trial, not paperwork.

DISCOVERY-ENGINE SCAN REGISTRY: the "cells screened but never promoted"
count can't be recovered from the ledger alone (most cells never get a
hypothesis_id at all) -- it has to be read from each scan's own writeup.
Sourced from docs/BACKLOG.md:
  - Scan 001 (2026-09-09): 48 cells scanned, 2 promoted to hypothesis
    rows (H116 = hyp-000117, H117 = hyp-000119) -> 46 unpromoted.
  - Scan 002 (2026-09-09): 44 cells scanned, 1 promoted (H118 =
    hyp-000121) -> 43 unpromoted.
Update SCAN_REGISTRY below whenever a new Discovery Engine scan runs --
that is the one number this module cannot derive automatically, because
the ledger schema has no field for "cells screened but rejected before
ever being written down." Flagged as a real, disclosed limitation, not
silently assumed away: any earlier (pre-2026-09-09, pre-"Scan 00N"
naming) exploratory work that also screened multiple related
configurations without a documented per-cell count is NOT included in
N_DISCOVERY, meaning this module's N is a FLOOR on true Discovery-stage
exposure, not a ceiling -- the true correction, if anything, should be
at least this harsh, possibly harsher.

STATUS: first real application, 2026-09-09 (this session). Applied to
every "still-in-flight" candidate identified by the same session's
ledger triage sweep (research/studies/project-wide-multiplicity-2026-09-09.md
carries the full results table and narrative). Not re-run automatically
by any daily checker yet -- re-run by hand (from the repo root:
`PYTHONPATH=src python3 src/project_wide_multiplicity.py`) whenever a new candidate needs checking
or the ledger has grown meaningfully, and update SCAN_REGISTRY when a
new Discovery Engine scan runs.
"""

from dataclasses import dataclass
from typing import Optional
import math

try:
    from scipy.stats import norm
    def _z_for_two_sided_alpha(alpha: float) -> float:
        return float(norm.ppf(1 - alpha / 2))
except ImportError:  # pragma: no cover - scipy is expected to be present in this project
    def _z_for_two_sided_alpha(alpha: float) -> float:
        # Beasley-Springer-Moro rational approximation to the inverse normal CDF.
        p = 1 - alpha / 2
        a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
             1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
        b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
             6.680131188771972e+01, -1.328068155288572e+01]
        c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
             -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
        d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
             3.754408661907416e+00]
        plow, phigh = 0.02425, 1 - 0.02425
        if p < plow:
            q = math.sqrt(-2 * math.log(p))
            return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                   ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
        elif p <= phigh:
            q = p - 0.5
            r = q * q
            return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
                   (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
        else:
            q = math.sqrt(-2 * math.log(1 - p))
            return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                    ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

import research_ledger as rl

FAMILYWISE_ALPHA = 0.10          # matches this project's existing 90%-CI single-test convention
Z_90_SINGLE = 1.6448536269514722  # two-sided z for a single-test 90% CI

# Discovery-Engine scan registry -- see module docstring. (scanned_cells, promoted_hypothesis_ids)
SCAN_REGISTRY = {
    "scan_001_2026-09-09": {"cells_scanned": 48, "promoted_hypothesis_ids": ["hyp-000117", "hyp-000119"]},
    "scan_002_2026-09-09": {"cells_scanned": 44, "promoted_hypothesis_ids": ["hyp-000121"]},
    "scan_003_2026-09-09": {"cells_scanned": 24, "promoted_hypothesis_ids": []},
    # Scan 003 (opening_range_vs_atr, zn_level_vs_trailing): 4 of 24 cells cleared
    # the unusual+cost gate; the split-sample robustness screen
    # (discovery_scan_003_split_sample_robustness.py) then killed 2 of those 3
    # unique (var,bucket) candidates (zn_level_vs_trailing/mid/h10d,
    # opening_range_vs_atr/mid/h1d). The 3rd (zn_level_vs_trailing/low/h10d)
    # then FAILED an independent volatility-regime split
    # (research_director_regime_check_scan003.py) -- effect concentrated
    # entirely in the high-vol regime subset. ABANDONED, no hypothesis_id
    # spent. Scan 003 is fully closed (0/3 survived).
    "scan_004_2026-09-10": {"cells_scanned": 36, "promoted_hypothesis_ids": []},
    "scan_005_2026-09-10": {"cells_scanned": 24, "promoted_hypothesis_ids": []},
    "scan_006_2026-09-10": {"cells_scanned": 3, "promoted_hypothesis_ids": []},
    # Scan 006 (overnight_range_vs_atr, first-RTH-hour reaction -- Idea
    # Inventory Entry 1, drawn 2026-09-10 20:15 UTC session): 0/3 cells
    # cleared the credible+cost-floor screen (all three atr_norm <0.02,
    # nowhere near the 0.05 floor, no monotonic gradient). CLOSED, zero
    # survivors. 2-attempt limit on overnight_range_vs_atr now exhausted
    # (H116's 10-day drift = attempt 1, closed at Validation; this =
    # attempt 2, closed at Discovery). See
    # research/sessions/2026-09-10-2015.md.
    "scan_007_2026-09-11": {"cells_scanned": 4, "promoted_hypothesis_ids": []},
    "scan_008_2026-09-11": {"cells_scanned": 3, "promoted_hypothesis_ids": ["hyp-000139"]},
    "scan_009_2026-09-11": {"cells_scanned": 1, "promoted_hypothesis_ids": []},
    "scan_010_2026-09-11": {"cells_scanned": 3, "promoted_hypothesis_ids": ["hyp-000140"]},
    "scan_011_2026-09-12": {"cells_scanned": 6, "promoted_hypothesis_ids": []},
    "scan_012_2026-09-12": {"cells_scanned": 9, "promoted_hypothesis_ids": []},
    "scan_013_2026-09-12": {"cells_scanned": 6, "promoted_hypothesis_ids": []},
    "scan_014_2026-09-12": {"cells_scanned": 2, "promoted_hypothesis_ids": ["hyp-000142", "hyp-000144"]},
    "scan_015_2026-09-12": {"cells_scanned": 2, "promoted_hypothesis_ids": []},
    # Scan 015 (Entry 12 / map M5: nq_minus_zn_mtd terciles -> last-2-session
    # gating return, first-2-session reported window). Attempt 1 of 2.
    # Mechanism doc research/mechanisms/nq-zn-month-end-relative-performance-m5.md
    # written BEFORE this scan. Registered September 11th, 11:00 pm CT.
    "scan_016_2026-09-12": {"cells_scanned": 1, "promoted_hypothesis_ids": []},
    # Scan 016 (Entry 13 / map M3b: fomc_initial_move_vs_atr sign-adjusted
    # continuation, single pre-registered gating cell 14:30->16:00). Attempt
    # 1 of 2. Mechanism doc research/mechanisms/post-fomc-continuation-m3b.md
    # written BEFORE this scan. Registered September 11th, 11:10 pm CT.
    "scan_017_2026-09-12": {"cells_scanned": 1, "promoted_hypothesis_ids": []},
    "scan_018_2026-09-12": {"cells_scanned": 2, "promoted_hypothesis_ids": []},
    "scan_019_2026-09-12": {"cells_scanned": 9, "promoted_hypothesis_ids": []},
    # Scan 019 (Entry 16 / map M12: 5-day change in 20-day average pairwise
    # correlation across the NQ/ZN/6E/CL basket, terciles x NQ forward 1/2/3
    # day return in ATR units. GATING = HIGH tercile at h=3, credibly
    # NEGATIVE; the other 8 cells reported). Attempt 1 of 2. Drawn on
    # Jason's explicit go-ahead September 12th, ~1:35 am CT ("Run cross-asset
    # first"). Mechanism doc research/mechanisms/cross-asset-correlation-
    # convergence-m12.md written BEFORE this scan, and it pre-registers a
    # BINDING confound check (trailing 5-day NQ return by tercile + the
    # gating cell split by that sign) -- a credible result that survives
    # only in the already-falling subset closes as the known momentum
    # family, not a finding. Registered September 12th, 1:45 am CT.
    # Scan 018 (Entry 15 / map M9: Nasdaq-100 quarterly rebalance close-
    # window |move| and volume vs normal days, 2 pre-registered gating
    # cells, next-session sign-adjusted reversal reported if P1 passes).
    # M9 UNPARKED 2026-09-11 11:37 pm CT after Jason authorized sourcing
    # the rebalance calendar ("do what you gotta do, don't wait for me").
    # Calendar: src/nasdaq_rebalance_calendar.py (3rd Friday of Mar/Jun/
    # Sep/Dec, verified against Nasdaq's own Dec-2025 press release).
    # Mechanism doc research/mechanisms/nasdaq-rebalance-close-window-m9.md
    # written BEFORE this scan. Registered September 12th, 12:05 am CT.
    # OUTCOME: INDETERMINATE, not a null -- n_rebalance_days=0. Every one
    # of the 27 in-range rebalance Fridays has a data gap in the
    # continuous-contract file (same day as the NQ futures quarterly
    # roll). Not a spent attempt (no real test occurred). M9 re-PARKED.
    # See mechanism doc Section 6 for full root-cause detail.
    # Scan 017 (Entry 14 / map M4: pre-FOMC drift, exact Lucca-Moench window
    # prior-day 14:00 -> FOMC-day 14:00, single pre-registered gating cell).
    # Attempt 2 of 2 (LAST) on pre-FOMC drift (hyp-000111 = attempt 1).
    # Mechanism doc research/mechanisms/pre-fomc-drift-exact-lm-window-m4.md
    # written BEFORE this scan. Registered September 11th, 11:14 pm CT.
    # Scan 014 (Entry 8 / map M7 range footprint: vxn_level_vs_trailing HIGH
    # -> next-day RTH range vs trailing-20d avg; LOW reported). Attempt 2 of
    # 2 on vxn_level_vs_trailing (Scan 002 returns = attempt 1). Mechanism
    # doc research/mechanisms/vxn-implied-leads-realized-range-m7.md
    # written BEFORE this scan. Registered September 11th, 9:45 pm CT.
    # Scan 013 outcome: clean null, closing-move family closed for good.
    # Scan 013 (Entry 11 / map M1: close_volume_vs_norm terciles x next-
    # morning sign-adjusted reversal at 09:30 open and 10:00). Attempt 2 of 2
    # on the closing-move family (hyp-000110). Mechanism doc research/
    # mechanisms/cash-close-imbalance-volume-conditioned-m1.md written
    # BEFORE this scan. Registered September 11th, 9:39 pm CT, before the
    # scan ran. Scan 012 outcome: P1 not confirmed, 0 promoted.
    # Scan 012 (Entry 10 / map M11: nq_zn_corr_20d terciles x NQ forward
    # 1/2/3-day return in ATR units, gating claim HIGH-minus-LOW per
    # horizon). Mechanism doc research/mechanisms/nq-zn-correlation-
    # breakdown-m11.md written BEFORE this scan. Registered September 11th,
    # 9:37 pm CT, extra cycle, before the scan ran. Outcome of Scan 011
    # (Entry 9 / M10): clean null, 6/6 cells, no promotion.
    # Scan 011 (Entry 9 / map M10: morning_move_vs_atr |magnitude| terciles
    # x two horizons -- lull 11:30->13:30 and 11:30->16:00 -- sign-adjusted
    # retrace in ATR units. Mechanism doc research/mechanisms/
    # midday-directional-retrace-m10.md written BEFORE this scan (AMENDMENT
    # v2.5). Six pre-registered cells; the GATING claim is the HIGH tercile
    # at the lull horizon (P1 concentration). Registered September 11th,
    # 9:33 pm CT, extra cycle at Jason's direction, before the scan ran.
    # Scan 010 (|gap_vs_atr| magnitude terciles, same-day RTH range vs
    # trailing-20d average -- Idea Inventory Entry 5, drawn 2026-09-11
    # 16:3X UTC interactive session with Jason present, per the DRAW
    # rule immediately following this session's own TOP-UP meeting
    # (Entry 7 added, floor restored). Three pre-registered cells
    # (low/mid/high). Registered here BEFORE the scan is run, per this
    # module's standing maintenance note -- outcome to be updated once
    # the scan completes.
    # Scan 009 (day_of_week==Friday, same-day RTH range vs trailing-20d
    # average -- Idea Inventory Entry 4, drawn 2026-09-11 14:2X UTC
    # autonomous overnight cycle, DRAW rule per Entry 4's own Cadence
    # note, floor already met, no TOP-UP owed). ONE pre-registered cell
    # (Friday only; Monday deferred pending this result). Registered
    # here BEFORE the scan is run, per this module's standing
    # maintenance note -- promoted_hypothesis_ids and outcome to be
    # updated once the scan completes.
    # Scan 008 (trailing 20d overnight-vs-RTH return divergence, today's own
    # divergence outcome -- Idea Inventory Entry 3, drawn 2026-09-11 03:2X
    # UTC session immediately after that session's TOP-UP meeting restored
    # the floor): 1/3 cells credible (HIGH tercile, n=364, mean=-0.0746,
    # ci_90=[-0.1371,-0.0099]) -- but it confirms P2 (the falsifying,
    # mean-reversion alternative), not P1 (the entry's primary persistence
    # mechanism). Routed to Candidate Triage, not closed -- see
    # research/sessions/2026-09-11-0329.md and hyp-000139. Mechanism doc for
    # the reversion story still owed before this can advance past Triage
    # (MECHANISM GATE).
    # UPDATE 2026-09-11: hyp-000139 REJECTED at Statistical stage
    # (research/studies/hyp139-statistical-stage-2026-09-11.md) -- fails
    # the project-wide multiplicity-corrected magnitude check (Q3),
    # adjusted CI crosses zero. promoted_hypothesis_ids left as-is (this
    # registry tracks scan-cell counts, not final ledger status; see
    # research/ledger/hypotheses.jsonl for the current REJECTED status).
    # Scan 007 (days_to_monthly_opex, RTH-range compression/release around
    # monthly opex -- Idea Inventory Entry 2, drawn 2026-09-11 02:40 UTC
    # session): 4 cells (before/after-opex x witching/non-witching). Both
    # PRIMARY (non-witching) cells null -- CI_90 spans 1.0, neither
    # pre-registered direction (compress before, release after) confirmed.
    # Witching-month cells (n=27 each) also null. CLOSED, zero survivors.
    # 2-attempt limit on days_to_monthly_opex now exhausted (Scan 004
    # return-direction test = attempt 1, closed 0/36; this = attempt 2,
    # closed at Discovery). hyp-000138. See research/sessions/2026-09-11-0240.md.
    # Scan 005 (nq_zn_divergence, nq_vxn_divergence -- cross-instrument
    # relative-value/divergence state, direction B per the Idea Inventory
    # framework, AMENDMENT v2.3): 5 of 24 cells cleared the raw credible+
    # cost-floor screen, but NONE confirmed the pre-registered falsifiable
    # monotonic-reversion shape (LOW positive AND HIGH negative) that
    # justified scanning in the first place -- D1 complete null (0/12),
    # D2 thin/one-sided (HIGH-at-5d only, LOW never confirms). CLOSED,
    # zero survivors on pre-registered terms. See
    # research/studies/scan-005-closure-and-staff-meeting-2026-09-10.md.
    # An unpredicted MID-bucket continuation pattern was found and
    # deliberately NOT chased (no pre-registered mechanism) -- logged to
    # LEARN/KNOWN UNEXPLORED for a future, freshly pre-registered attempt.
    # Scan 004 (days_to_monthly_opex, prior_close_location_in_range,
    # dist_to_multiday_reference_level_vs_atr; short horizons per the
    # Standing Research Priority -- intraday/overnight/1d/2d, not h10d):
    # 1 of 36 cells cleared BOTH the ATR floor and the new additive
    # absolute-cost floor -- prior_close_location_in_range/low/intraday,
    # n=552, atr_norm=0.055 (barely above the 0.05 floor -- flagged as a
    # caution, not disqualifying on its own). NOT yet promoted -- pending
    # split-sample robustness + regime check
    # (research/studies/scan-004-scoping-2026-09-10.md; see
    # research/NEXT_UP.md queue for the in-progress triage). Update
    # promoted_hypothesis_ids here if/when it survives and is logged.
}


def _is_meta_row(record: dict) -> bool:
    """True if this ledger row is a pure post-hoc bookkeeping correction /
    progression pointer with no independent empirical trial of its own --
    see module docstring's counting rule."""
    name = record.get("strategy_name", "")
    params = record.get("parameters") or {}
    notes = (record.get("notes") or "").lower()
    if name.endswith("_STATUS_CORRECTION") or name.endswith("_PROGRESSION_POINTER") \
            or name.endswith("_MULTIPLICITY_REEXPRESSION"):
        return True
    if "corrects" in params or "reexpresses" in params:
        return True
    if "ledger hygiene correction" in notes and record.get("trade_count") is None:
        return True
    return False


def compute_stage_trial_counts(ledger_path=rl.LEDGER_PATH) -> dict:
    """Returns {"discovery": N, "validation": N, "holdout": N} -- the
    honest, current, stage-specific family sizes described in the module
    docstring. Recomputed from the live ledger every call (never a
    hand-maintained number that can silently drift), except for the
    Discovery-stage "unpromoted scan cells" addend, which is read from
    SCAN_REGISTRY above (the one figure the ledger schema cannot recover
    on its own -- see docstring)."""
    current = rl.get_current_state(ledger_path)
    real = {r["hypothesis_id"]: r for r in current if not _is_meta_row(r)}

    n_discovery_logged = sum(1 for r in real.values() if r.get("data_slice_used") == "discovery")
    n_validation = sum(1 for r in real.values() if r.get("data_slice_used") == "validation")
    n_holdout = sum(1 for r in real.values() if (r.get("data_slice_used") or "").startswith("holdout"))

    n_unpromoted_scan_cells = sum(
        scan["cells_scanned"] - len(scan["promoted_hypothesis_ids"])
        for scan in SCAN_REGISTRY.values()
    )

    return {
        "discovery": n_discovery_logged + n_unpromoted_scan_cells,
        "validation": max(1, n_validation),
        "holdout": max(1, n_holdout),
        "_detail": {
            "n_discovery_logged": n_discovery_logged,
            "n_unpromoted_scan_cells": n_unpromoted_scan_cells,
            "n_validation_logged": n_validation,
            "n_holdout_logged": n_holdout,
        },
    }


@dataclass
class MultiplicityVerdict:
    label: str
    stage: str
    n_trials: int
    n_obs: int
    mean: float
    single_test_ci_90: tuple
    adjusted_ci: tuple
    null_value: float
    survives_adjustment: bool


def sidak_z(n_trials: int, familywise_alpha: float = FAMILYWISE_ALPHA) -> float:
    n_trials = max(1, n_trials)
    alpha_sidak = 1 - (1 - familywise_alpha) ** (1 / n_trials)
    return _z_for_two_sided_alpha(alpha_sidak)


def evaluate(label: str, stage: str, n_obs: int, mean: float, ci_90: tuple,
             null_value: float, stage_trial_counts: dict) -> MultiplicityVerdict:
    """Applies the stage-appropriate Sidak correction to one already-computed
    single-test 90% CI. stage must be one of "discovery", "validation",
    "holdout" -- the trial count used is stage_trial_counts[stage], NOT a
    single blanket project-wide number (see module docstring)."""
    lo, hi = ci_90
    se = (hi - lo) / (2 * Z_90_SINGLE)
    z_adj = sidak_z(stage_trial_counts[stage])
    adj_lo, adj_hi = mean - z_adj * se, mean + z_adj * se
    survives = (adj_lo > null_value) or (adj_hi < null_value)
    return MultiplicityVerdict(
        label=label, stage=stage, n_trials=stage_trial_counts[stage], n_obs=n_obs,
        mean=mean, single_test_ci_90=(lo, hi), adjusted_ci=(adj_lo, adj_hi),
        null_value=null_value, survives_adjustment=survives,
    )


def _print_report():
    counts = compute_stage_trial_counts()
    print("Stage-specific project-wide trial counts (2026-09-09 first run):")
    print(f"  discovery : N={counts['discovery']}  ({counts['_detail']})")
    print(f"  validation: N={counts['validation']}")
    print(f"  holdout   : N={counts['holdout']}")
    print()

    # (label, stage, n, mean, ci_lo, ci_hi, null_value)
    candidates = [
        ("H118 Discovery (hyp-000121)", "discovery", 554, 0.6166127225439121, 0.4533269265357841, 0.7849286122846664, 0.0),
        ("H118 Validation (hyp-000122)", "validation", 213, 0.2839896940801262, 0.047924667873678724, 0.5192995801763663, 0.0),
        ("H118 Holdout (hyp-000123)", "holdout", 187, 0.39594291085440664, 0.13649436895644734, 0.6503324231137323, 0.0),
        ("Range-contraction narrow (hyp-000046 Discovery)", "discovery", 412, 0.836, 0.802, 0.869, 1.0),
        ("Range-contraction wide (hyp-000046 Discovery)", "discovery", 389, 1.372, 1.313, 1.434, 1.0),
        ("Range-contraction narrow (hyp-000048 Validation)", "validation", 141, 0.9438, 0.8884, 0.9982, 1.0),
        ("Range-contraction wide (hyp-000048 Validation)", "validation", 130, 1.0809, 1.0204, 1.1430, 1.0),
        ("Overnight coil (hyp-000056 Discovery)", "discovery", 332, 0.7827, 0.7471, 0.8176, 1.0),
        ("Overnight coil (hyp-000057 Validation)", "validation", 103, 0.8944, 0.8300, 0.9595, 1.0),
        ("Midday lull narrow (hyp-000105 Discovery)", "discovery", 411, 0.7127, 0.6864, 0.7431, 1.0),
        ("Midday lull not-narrow (hyp-000105 Discovery)", "discovery", 1201, 1.1602, 1.1261, 1.1939, 1.0),
        ("Midday lull narrow (hyp-000106 Validation)", "validation", 142, 0.8161, 0.7615, 0.8784, 1.0),
        ("Midday lull not-narrow (hyp-000106 Validation)", "validation", 404, 1.091, 1.0372, 1.1473, 1.0),
    ]
    for label, stage, n, mean, lo, hi, null in candidates:
        v = evaluate(label, stage, n, mean, (lo, hi), null, counts)
        tag = "SURVIVES" if v.survives_adjustment else "fails"
        print(f"[{v.stage:10}] {v.label:<50} n={v.n_obs:>5} mean={v.mean:>8.4f} "
              f"single90={v.single_test_ci_90} adj={tuple(round(x,4) for x in v.adjusted_ci)} {tag}")


if __name__ == "__main__":
    _print_report()
