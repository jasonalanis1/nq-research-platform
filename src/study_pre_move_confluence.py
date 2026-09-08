"""
study_pre_move_confluence.py
=================================

exp-107 -- frozen spec: research/studies/pre-move-behavior-confluence-spec.md.
Tests whether agreement between two mechanistically distinct, individually
edge-less signals (opening volume imbalance x multi-timeframe trend
alignment) carries information neither has alone.

STEP 1 + STEP 2 together. Search batch ID: batch-2026-09-08-pre-move-confluence.

REUSED, UNMODIFIED: detect_volume_imbalance_signal_for_day (batch3),
detect_alignment_signal_for_day (batch1), simulate_signal,
analyze_r_multiples (batch1).

HOW TO RUN:
    python3 src/study_pre_move_confluence.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
from study_pre_move_behavior_batch1 import (
    detect_alignment_signal_for_day,
    simulate_signal,
    analyze_r_multiples,
    MIN_PROSPECTIVE_N,
)
from study_pre_move_behavior_batch3 import detect_volume_imbalance_signal_for_day

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-pre-move-confluence"


def main():
    print("=" * 78)
    print("EXP-107: VOLUME-IMBALANCE x TREND-ALIGNMENT CONFLUENCE")
    print("=" * 78)
    print("\nFrozen spec: research/studies/pre-move-behavior-confluence-spec.md\n")

    df, is_synthetic = load_price_data(context="study_pre_move_confluence.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    session = discovery.between_time("09:30", "16:00")
    day_groups = {d: g for d, g in session.groupby(session.index.date)}
    print(f"Discovery RTH days: {len(day_groups)}")

    confluence_r = []
    days_with_both = 0
    days_agreeing = 0

    for day, day_df in day_groups.items():
        vol_sig = detect_volume_imbalance_signal_for_day(day_df)
        align_sig = detect_alignment_signal_for_day(day_df)
        if vol_sig is None or align_sig is None:
            continue
        days_with_both += 1
        if vol_sig["direction"] != align_sig["direction"]:
            continue
        days_agreeing += 1
        r = simulate_signal(day_df, align_sig)
        if r is not None:
            confluence_r.append(r)

    print(f"\nDays with both signals present: {days_with_both}")
    print(f"Days agreeing (confluence fired): {days_agreeing}")
    print(f"exp-107 confluence trades: {len(confluence_r)}")

    result = analyze_r_multiples(confluence_r)
    print(f"\nexp107_volume_alignment_confluence: {result}")

    n = result.get("n", 0)
    if n == 0:
        verdict = "NO_DATA"
    elif result["statistically_credible"] and result["economically_meaningful"]:
        verdict = "STEP_1+2_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN_FOR_PROSPECTIVE"
    else:
        verdict = "STEP_1+2_FAIL"
    print(f"  exp107_volume_alignment_confluence: {verdict}")

    out = {
        "search_batch_id": SEARCH_BATCH_ID,
        "days_with_both": days_with_both,
        "days_agreeing": days_agreeing,
        "result": result,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_pre_move_confluence_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
