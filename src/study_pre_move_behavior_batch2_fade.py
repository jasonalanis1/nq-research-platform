"""
study_pre_move_behavior_batch2_fade.py
=======================================

exp-102/103 -- frozen spec: research/studies/pre-move-behavior-batch2-spec.md.
Fade (reversed-direction) variants of exp-100/101, which came back
CREDIBLY LOSING (not just null) in batch 1 -- testing the opposite
direction of the same, unmodified detection logic.

STEP 1 + STEP 2 together. Search batch ID:
batch-2026-09-08-pre-move-behavior-2-fade.

REUSED, UNMODIFIED from study_pre_move_behavior_batch1.py: all detection
logic (detect_vacuum_signals_for_day, detect_alignment_signal_for_day,
build_15min_bars, build_60min_bars_simple), simulate_signal,
bootstrap_mean_ci, analyze_r_multiples.

HOW TO RUN:
    python3 src/study_pre_move_behavior_batch2_fade.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
from study_pre_move_behavior_batch1 import (
    detect_vacuum_signals_for_day,
    detect_alignment_signal_for_day,
    simulate_signal,
    analyze_r_multiples,
    SEARCH_BATCH_ID as _UNUSED,
    MIN_PROSPECTIVE_N,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-pre-move-behavior-2-fade"


def fade_signal(sig):
    """Mirror a signal's direction across its own entry price, keeping
    |risk| and the 1.35R target distance identical in magnitude."""
    entry = sig["entry"]
    risk = abs(sig["entry"] - sig["stop"])
    target_dist = abs(sig["target"] - sig["entry"])
    if sig["direction"] == "long":
        new_direction = "short"
        new_stop = entry + risk
        new_target = entry - target_dist
    else:
        new_direction = "long"
        new_stop = entry - risk
        new_target = entry + target_dist
    faded = dict(sig)
    faded["direction"] = new_direction
    faded["stop"] = new_stop
    faded["target"] = new_target
    return faded


def main():
    print("=" * 78)
    print("EXP-102/103: FADE VARIANTS OF VOLUME VACUUM / TREND ALIGNMENT")
    print("=" * 78)
    print("\nFrozen spec: research/studies/pre-move-behavior-batch2-spec.md\n")

    df, is_synthetic = load_price_data(context="study_pre_move_behavior_batch2_fade.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    session = discovery.between_time("09:30", "16:00")
    day_groups = {d: g for d, g in session.groupby(session.index.date)}
    print(f"Discovery RTH days: {len(day_groups)}")

    vacuum_fade_r = []
    alignment_fade_r = []

    for day, day_df in day_groups.items():
        vac_signals = detect_vacuum_signals_for_day(day_df)
        for sig in vac_signals:
            faded = fade_signal(sig)
            r = simulate_signal(day_df, faded)
            if r is not None:
                vacuum_fade_r.append(r)

        align_sig = detect_alignment_signal_for_day(day_df)
        if align_sig is not None:
            faded = fade_signal(align_sig)
            r = simulate_signal(day_df, faded)
            if r is not None:
                alignment_fade_r.append(r)

    print(f"\nexp-102 volume vacuum FADE: {len(vacuum_fade_r)} signals")
    print(f"exp-103 trend alignment FADE: {len(alignment_fade_r)} signals")

    results = {
        "exp102_volume_vacuum_fade": analyze_r_multiples(vacuum_fade_r),
        "exp103_multi_timeframe_alignment_fade": analyze_r_multiples(alignment_fade_r),
    }

    verdicts = {}
    for key, r in results.items():
        n = r.get("n", 0)
        if n == 0:
            verdicts[key] = "NO_DATA"
        elif r["statistically_credible"] and r["economically_meaningful"]:
            verdicts[key] = "STEP_1+2_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN_FOR_PROSPECTIVE"
        else:
            verdicts[key] = "STEP_1+2_FAIL"

    print()
    for key, r in results.items():
        print(f"{key}: {r}")
    print()
    for key, v in verdicts.items():
        print(f"  {key}: {v}")

    out = {"search_batch_id": SEARCH_BATCH_ID, "results": results, "verdicts": verdicts}
    out_path = DATA_DIR / "study_pre_move_behavior_batch2_fade_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
