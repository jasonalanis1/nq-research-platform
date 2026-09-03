"""
study_cpi_reversal_followup.py
==================================

Implements the frozen spec in
`research/studies/cpi-reversal-followup.md`. Follow-up to exp-041's
disclosed-but-unregistered CPI-only reversal side-observation. Reuses
`study_post_release_continuation.py`'s scan/compute functions and
`directional_continuation` statistic UNMODIFIED -- this script adds
exactly one new thing: pricing that same statistic as an actual
cost-inclusive trade (the mirror-image "bet on reversal, not
continuation" side), which exp-041 never tested since it only measured
raw point-to-point drift.

Read `research/studies/cpi-reversal-followup.md` first for why this is
explicitly NOT independent confirmation (same Discovery data, same
underlying statistic) and why no outcome here can result in a
"promote" verdict (n=75 max, far under the 150-trade promotion-bar
minimum).

HOW TO RUN:
    python3 src/study_cpi_reversal_followup.py
"""

import json
from pathlib import Path

import numpy as np

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from study_nq_trend_following import bootstrap_mean_ci  # reused unmodified
from study_post_release_continuation import (
    compute_directional_continuation,
    robustness_drop_largest,
    robustness_split_half,
    scan_all_days,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 2000       # matches study_post_release_continuation.py
RANDOM_SEED = 11         # matches study_post_release_continuation.py
ECONOMIC_THRESHOLD_POINTS = 2 * ROUND_TRIP_COST_POINTS  # frozen Step-2-gate #2, same bar as every prior study
PROMOTION_BAR_MIN_TRADES = 150  # docs/RESEARCH_INTEGRITY_PROTOCOL.md


def one_sample_test(values) -> dict:
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": (float("nan"), float("nan")), "significant": False,
                "economically_meaningful": False}
    mean_val = float(arr.mean())
    ci_low, ci_high = bootstrap_mean_ci(arr, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED)
    significant = ci_low > 0
    return {
        "n": n,
        "mean": mean_val,
        "mean_dollars": mean_val * 20.0,  # CONTRACT_MULTIPLIER, matches backtest.py
        "ci_90": (ci_low, ci_high),
        "significant": bool(significant),
        "economically_meaningful": bool(mean_val >= ECONOMIC_THRESHOLD_POINTS),
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_cpi_reversal_followup.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    scanned = scan_all_days(discovery_df)                       # reused unmodified
    sub, exclusion_counts = compute_directional_continuation(scanned)  # reused unmodified

    cpi_mask = sub["release_type"] == "cpi"
    cpi_rows = sub[cpi_mask].copy()

    # The one new computation this script adds: price the reversal
    # (mirror-image) trade, gross and net of the standard round-trip
    # cost, reused unmodified from backtest.py.
    cpi_rows["reversal_pnl_gross"] = -1.0 * cpi_rows["directional_continuation"]
    cpi_rows["reversal_pnl_net"] = cpi_rows["reversal_pnl_gross"] - ROUND_TRIP_COST_POINTS

    print("=" * 78)
    print("CPI-ONLY REVERSAL FOLLOW-UP -- Discovery slice")
    print("=" * 78)
    print(f"\nExclusions (from the shared scan/compute step): {exclusion_counts}")
    print(f"CPI-only rows available: {len(cpi_rows)}")
    print(f"\n** Promotion-bar reminder: this project's minimum is "
          f"{PROMOTION_BAR_MIN_TRADES} trades. n={len(cpi_rows)} here cannot reach that "
          f"regardless of outcome -- no verdict below can be 'promote'. **")

    print(f"\n--- PRIMARY: CPI-only reversal trade, net of round-trip cost "
          f"({ROUND_TRIP_COST_POINTS:.3f} pts) ---")
    primary = one_sample_test(cpi_rows["reversal_pnl_net"])
    for k, v in primary.items():
        print(f"  {k}: {v}")
    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['significant']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= {ECONOMIC_THRESHOLD_POINTS:.3f} pts): "
          f"{primary['economically_meaningful']}")

    print("\n--- Descriptive: gross (pre-cost) reversal, for comparison to exp-041's raw number ---")
    gross = one_sample_test(cpi_rows["reversal_pnl_gross"])
    print(f"  n={gross['n']} mean={gross['mean']:+.3f}pts  90% CI=[{gross['ci_90'][0]:+.3f}, {gross['ci_90'][1]:+.3f}]  "
          f"(should mirror exp-041's cpi-only -11.023pts / [-22.560, -0.436] with the sign flipped)")

    cpi_release_mask = cpi_rows.index  # already filtered to cpi-only
    print("\n--- Robustness (a): drop single largest-|reversal_pnl_net| day ---")
    # robustness_drop_largest expects a full df + a boolean mask on release rows;
    # build a compatible mask-and-column view without modifying the reused helper.
    drop_input = sub.copy()
    drop_input.loc[cpi_mask, "directional_continuation"] = -1.0 * (
        sub.loc[cpi_mask, "directional_continuation"]
    ) - ROUND_TRIP_COST_POINTS  # so the reused helper's drop-largest logic operates on reversal_pnl_net values
    drop_result = robustness_drop_largest(drop_input, cpi_mask)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(drop_input, cpi_mask)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n" + "=" * 78)
    verdict = "retest -- promising, underpowered (n < 150-trade promotion bar)" if primary["significant"] and primary["economically_meaningful"] \
        else "kill -- not statistically credible and/or not economically meaningful after cost"
    print(f"Verdict: {verdict}")

    out = {
        "exclusion_counts": exclusion_counts,
        "n_cpi_rows": len(cpi_rows),
        "primary_net": primary,
        "descriptive_gross": gross,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "verdict": verdict,
    }
    json_path = DATA_DIR / "study_cpi_reversal_followup_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
