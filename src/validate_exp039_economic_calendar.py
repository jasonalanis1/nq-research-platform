"""
validate_exp039_economic_calendar.py
=====================================

Out-of-sample replication check for exp-039 (Scheduled Macro-Release
Volatility, CPI/NFP) on the Validation slice.

WHY THIS EXISTS AND WHY IT'S SEPARATE FROM study_economic_calendar.py:
exp-039 is this project's first non-null result across fourteen
hypotheses. Per docs/RESEARCH_INTEGRITY_PROTOCOL.md, Validation data is
normally reserved for a candidate that has already been formally
promoted out of Discovery -- this characterization study was never put
through that (trade-count-based) promotion bar, since it isn't a
trading setup. Jason explicitly approved this as a one-time, disclosed
exception (2026-09-02): given that exp-039 is the first result this
project would ever consider acting on, and given the honest
multiple-testing concern (roughly 1.4 false positives expected by
chance across 14 tests at a 90% CI, and this is 1 hit), an
out-of-sample check on the exact frozen spec -- before any further
Discovery-only testing (FOMC) or any structure design -- was the
Advisor's and Claude's shared top recommendation, and Jason approved
running it. See docs/ROADMAP.md's 2026-09-02 entries for the full
record of this decision.

DISCIPLINE: this script performs ZERO new fitting. It reuses
study_economic_calendar.py's CPI_DATES/NFP_DATES constants,
classify_day(), scan_all_days(), and analyze_horizon() completely
unmodified, and applies them to data_split.get_validation_data()
instead of get_discovery_data(). No parameter is touched, no threshold
adjusted, no horizon re-picked. If this were to fail, the honest
conclusion is that the Discovery result did not replicate -- not an
invitation to retune anything.

HOW TO RUN:
    python3 src/validate_exp039_economic_calendar.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import get_validation_data
from study_economic_calendar import (
    scan_all_days,
    analyze_horizon,
    robustness_drop_largest_abs_return_day,
    robustness_split_half,
    PRIMARY_HORIZON_MINUTES,
    SECONDARY_HORIZON_MINUTES,
    ECONOMIC_THRESHOLD_POINTS,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main():
    full_df, is_synthetic = load_price_data(context="validate_exp039_economic_calendar.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this check requires real data.")
        return

    validation_df = get_validation_data(full_df)
    results_df = scan_all_days(validation_df)
    out_path = DATA_DIR / "validate_exp039_economic_calendar_validation.csv"
    results_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("exp-039 OUT-OF-SAMPLE REPLICATION CHECK -- Validation slice")
    print("Same frozen spec as study_economic_calendar.py, zero new fitting.")
    print("=" * 78)
    counts = results_df["release_type"].value_counts()
    print(f"\nDay counts: {counts.to_dict()}")

    print(f"\n--- PRIMARY (same as Discovery): {PRIMARY_HORIZON_MINUTES}-minute |post-8:30 return|, "
          f"release (CPI+NFP) vs normal ---")
    primary = analyze_horizon(results_df, PRIMARY_HORIZON_MINUTES, {"cpi", "nfp"})
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['significant']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= {ECONOMIC_THRESHOLD_POINTS:.3f} pts): "
          f"{primary['economically_meaningful']}")

    print("\n--- Robustness (a): drop single largest-|return| day ---")
    drop_result = robustness_drop_largest_abs_return_day(results_df)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(results_df)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n--- Descriptive breakdown: CPI-only vs NFP-only ---")
    cpi_only = analyze_horizon(results_df, PRIMARY_HORIZON_MINUTES, {"cpi"})
    nfp_only = analyze_horizon(results_df, PRIMARY_HORIZON_MINUTES, {"nfp"})
    print("  CPI-only:", cpi_only)
    print("  NFP-only:", nfp_only)

    print("\n--- SECONDARY horizons (descriptive only) ---")
    secondary = {}
    for h in SECONDARY_HORIZON_MINUTES:
        r = analyze_horizon(results_df, h, {"cpi", "nfp"})
        secondary[h] = r
        print(f"  {h}min: mean_diff={r['mean_diff_points']:+.3f}pts  "
              f"90% CI=[{r['ci_90'][0]:+.3f}, {r['ci_90'][1]:+.3f}]  "
              f"{'SIGNIFICANT' if r['significant'] else 'not significant'}")

    # Discovery result, hardcoded from the already-committed exp-039 write-up,
    # for a direct side-by-side comparison in the printed output only (not
    # used in any computation above).
    discovery_primary = {
        "mean_diff_points": 11.332697276436392,
        "ci_90": (8.103014337342502, 14.939408477306364),
    }
    print("\n" + "=" * 78)
    print("SIDE-BY-SIDE: Discovery (exp-039) vs Validation (this check)")
    print(f"  Discovery:  mean_diff={discovery_primary['mean_diff_points']:+.3f}pts  "
          f"90% CI=[{discovery_primary['ci_90'][0]:+.3f}, {discovery_primary['ci_90'][1]:+.3f}]")
    print(f"  Validation: mean_diff={primary['mean_diff_points']:+.3f}pts  "
          f"90% CI=[{primary['ci_90'][0]:+.3f}, {primary['ci_90'][1]:+.3f}]")
    replicated = primary["significant"] and primary["economically_meaningful"]
    print(f"\n  REPLICATED on Validation (both statistically credible and economically meaningful): {replicated}")
    print("=" * 78)

    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "descriptive_cpi_only": cpi_only,
        "descriptive_nfp_only": nfp_only,
        "secondary": secondary,
        "discovery_primary_for_comparison": discovery_primary,
        "replicated": replicated,
    }
    json_path = DATA_DIR / "validate_exp039_economic_calendar_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
