"""
study_intraday_behavior_batch3_prospective.py
=====================================

exp-085 -- frozen spec: research/studies/intraday-behavior-batch3-prospective-spec.md.
Single pre-registered Validation-slice prospective test of exp-084
(overnight coil -> RTH range ratio, hyp-000056), unmodified thresholds.

HOW TO RUN:
    python3 src/study_intraday_behavior_batch3_prospective.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import get_validation_data
from study_intraday_behavior_batch3 import build_overnight_and_rth_frame, analyze_overnight_coil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main():
    print("=" * 78)
    print("INTRADAY BEHAVIOR BATCH 3 PROSPECTIVE: exp-085 (overnight coil,")
    print("Validation slice)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/intraday-behavior-batch3-prospective-spec.md\n")

    df, is_synthetic = load_price_data(context="study_intraday_behavior_batch3_prospective.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    validation = get_validation_data(df)

    print("--- exp-085: Overnight range compression (pre-open coiling), Validation slice ---")
    frame = build_overnight_and_rth_frame(validation)
    coil = analyze_overnight_coil(frame)
    print(f"  n={coil['n']} mean_rth_range_ratio={coil['mean_rth_range_ratio']:.6f} "
          f"ci_90={coil['ci_90']} credible={coil['statistically_credible']}")

    verdict = "PROSPECTIVE_PASS" if coil["statistically_credible"] else "PROSPECTIVE_FAIL"
    print(f"\nVerdict: {verdict}")

    out = {
        "search_batch_id": "batch-2026-09-08-intraday-behavior-3-prospective",
        "overnight_coil_validation": coil,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_intraday_behavior_batch3_prospective_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
