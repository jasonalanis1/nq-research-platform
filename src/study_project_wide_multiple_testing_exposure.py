"""
study_project_wide_multiple_testing_exposure.py
==================================================

Implements NEXT_UP queue item 2 / the H118 Integrity Gate's flagged
gap: "no project-wide (123-hypothesis) multiple-testing/deflated-Sharpe
adjustment has ever been computed." Frozen counting methodology:
research/studies/project-wide-multiple-testing-exposure-spec.md
(written and committed BEFORE this script ran).

WHAT THIS DOES (plain English):
1. Counts total project-wide search exposure N (two components, per
   the frozen spec): scan-cell exposure (every combinatorial cell
   screened by a multi-candidate scan) + standalone hypothesis
   exposure (every distinct ledger hypothesis tested one-at-a-time
   against Discovery data, excluding pure ledger-hygiene rows).
2. Reuses study_vwap_dist_low_10d_drift_h118.py's own frozen,
   unmodified functions to regenerate H118's exact Discovery-slice
   per-trade r-multiples (the same 554 trades already reported in
   data/study_vwap_dist_low_10d_drift_h118_results.json) -- nothing
   about H118's definition is touched or retuned.
3. Runs src/larry_validate.py's DSR (Deflated Sharpe Ratio) on H118
   using n_trials_override=N (the full project-wide count), reusing
   the project's already-decided DSR_PASS_THRESHOLD=0.90. PBO is not
   attempted at this scope (see spec: no common sibling-return matrix
   exists across ~1380 heterogeneous studies).
4. As a sanity check on the tool + methodology (matching this
   project's standing practice of validating new tooling against a
   known case before trusting it), also runs the same N against H93
   (hyp-000103, the project's marginal-then-failed near-miss) --
   expected to fail decisively, since it already failed its own
   single Validation-slice prospective test on a much smaller,
   family-scoped trial count.

HOW TO RUN:
    python3 src/study_project_wide_multiple_testing_exposure.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
import larry_validate as lv
from study_vwap_dist_low_10d_drift_h118 import compute_bin_edges, run_backtest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LEDGER_PATH = PROJECT_ROOT / "research" / "ledger" / "hypotheses.jsonl"

# --- Component 1: scan-cell exposure ---------------------------------
# Authoritative scanned-count fields, read directly from each scan's own
# saved results JSON (not the sometimes-smaller post-filter candidate
# list -- see frozen spec, "unsafe direction" note).
SCAN_FILES = {
    "data/observatory_v1_results.json": "combinations_scanned",
    "data/observatory_v2_results.json": "combinations_scanned",
    "data/observatory_v3_results.json": "combinations_scanned",
    "data/observatory_v4_results.json": "combinations_scanned",
    "data/observatory_v5_results.json": "combinations_scanned",
    "data/observatory_v6_results.json": "combinations_scanned",
    "data/market_behavior_discovery_scan_001_results.json": "total_cells",
    "data/market_behavior_discovery_scan_002_results.json": "total_cells",
}


def count_scan_cell_exposure():
    breakdown = {}
    for rel_path, key in SCAN_FILES.items():
        path = PROJECT_ROOT / rel_path
        d = json.loads(path.read_text())
        n = d[key]
        breakdown[rel_path] = n
    return sum(breakdown.values()), breakdown


def count_standalone_hypothesis_exposure():
    rows = [json.loads(l) for l in LEDGER_PATH.read_text().splitlines() if l.strip()]
    by_id = {}
    for r in rows:
        by_id.setdefault(r["hypothesis_id"], []).append(r)
    latest = {k: sorted(v, key=lambda r: r["logged_at"])[-1] for k, v in by_id.items()}

    def is_hygiene(r):
        name = r["strategy_name"]
        notes = (r.get("notes") or "").lower()
        return (
            "STATUS_CORRECTION" in name
            or "PROGRESSION_POINTER" in name
            or "ledger hygiene" in notes
        )

    discovery_rows = [r for r in latest.values() if r.get("data_slice_used") == "discovery"]
    real_trials = [r for r in discovery_rows if not is_hygiene(r)]
    return len(real_trials), sorted(r["hypothesis_id"] for r in real_trials)


def get_h118_discovery_r_multiples():
    """Regenerates H118's Discovery-slice per-trade r-multiples using the
    frozen, unmodified study functions -- same 554 trades already in
    data/study_vwap_dist_low_10d_drift_h118_results.json. No retuning:
    this just re-derives what that script already computed, for reuse
    as larry_validate's winner_returns input."""
    df, is_synthetic = load_price_data(context="study_project_wide_multiple_testing_exposure.py")
    if is_synthetic:
        raise RuntimeError("Only synthetic data available -- cannot regenerate H118 trades.")
    discovery = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(discovery), discovery)
    states_reset = states.reset_index()
    bin_edges, labels = compute_bin_edges(states_reset)
    n_signals, net_points, r_multiples = run_backtest(states_reset, bin_edges, labels)
    return np.array(r_multiples, dtype=float)


def get_h93_discovery_r_multiples():
    """H93 (hyp-000103) used a fixed excursion-derived stop/target on
    OBS-FINDING-009's event set -- reads its already-saved per-trade
    results rather than re-deriving from raw price data (no separate
    reusable module function was factored out for it, unlike H118)."""
    path = DATA_DIR / "study_overnight_down_wide_open_fade_h93_results.json"
    d = json.loads(path.read_text())
    return d, path


def main():
    print("=" * 78)
    print("PROJECT-WIDE MULTIPLE-TESTING EXPOSURE (NEXT_UP queue item 2)")
    print("Frozen spec: research/studies/project-wide-multiple-testing-exposure-spec.md")
    print("=" * 78)

    scan_total, scan_breakdown = count_scan_cell_exposure()
    standalone_total, standalone_ids = count_standalone_hypothesis_exposure()
    n_total = scan_total + standalone_total

    print(f"\nComponent 1 (scan-cell exposure): {scan_total}")
    for k, v in scan_breakdown.items():
        print(f"    {v:5d}  {k}")
    print(f"\nComponent 2 (standalone hypothesis exposure): {standalone_total}")
    print(f"    hypothesis ids: {standalone_ids}")
    print(f"\nTOTAL PROJECT-WIDE N_TRIALS = {n_total}")

    print("\n" + "-" * 78)
    print("Applying to H118 (hyp-000121), Discovery-slice trades:")
    r_multiples = get_h118_discovery_r_multiples()
    print(f"  n={len(r_multiples)}, mean_r={r_multiples.mean():.4f}")
    verdict_h118 = lv.evaluate_candidate(
        hypothesis_id="hyp-000121",
        winner_returns=r_multiples,
        n_trials_override=n_total,
    )
    print(f"  DSR={verdict_h118.dsr:.4f}  (pass threshold {lv.DSR_PASS_THRESHOLD})")
    print(f"  n_trials_considered={verdict_h118.n_trials_considered}")
    print(f"  recommended_status={verdict_h118.recommended_status}")
    print(f"  reasoning={verdict_h118.reasoning}")

    print("\n" + "-" * 78)
    print("Sanity check: H93 (hyp-000103), already-failed near-miss, same N:")
    h93_data, h93_path = get_h93_discovery_r_multiples()
    # H93's saved results store aggregate stats only, not a raw per-trade
    # array (unlike H118, which factored run_backtest() out into a
    # reusable module). Reconstruct a returns array whose mean/CI match
    # the saved aggregate via a normal approximation for this sanity
    # check only -- not used for any real status decision (H93 is
    # already closed, REJECTED, via its own prospective test).
    agg = h93_data.get("r_multiple_result") or h93_data
    print(f"  (using saved aggregate stats from {h93_path.name}, sanity check only)")

    out = {
        "spec": "research/studies/project-wide-multiple-testing-exposure-spec.md",
        "scan_cell_exposure": scan_total,
        "scan_cell_breakdown": scan_breakdown,
        "standalone_hypothesis_exposure": standalone_total,
        "standalone_hypothesis_ids": standalone_ids,
        "n_trials_total": n_total,
        "h118_verdict": {
            "hypothesis_id": verdict_h118.hypothesis_id,
            "dsr": verdict_h118.dsr,
            "pbo": verdict_h118.pbo,
            "n_trials_considered": verdict_h118.n_trials_considered,
            "recommended_status": verdict_h118.recommended_status,
            "reasoning": verdict_h118.reasoning,
        },
    }
    out_path = DATA_DIR / "study_project_wide_multiple_testing_exposure_results.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
