"""
study_pre_move_target_sensitivity.py
=====================================

exp-106 -- frozen spec: research/studies/pre-move-behavior-target-sensitivity-spec.md.
Diagnostic: re-simulates all 6 already-detected fresh-behavior signals
(exp-100/101/102/103/104/105) at smaller R-multiple targets (0.5, 0.75)
instead of the project's default 1.35, holding the same stop/detection
logic, to check whether the fixed 1.35R target (not the trigger idea
itself) explains today's uniform losses.

REUSED, UNMODIFIED: detect_vacuum_signals_for_day,
detect_alignment_signal_for_day (batch1); fade_signal (batch2);
detect_volume_imbalance_signal_for_day,
detect_prior_close_rejection_signal_for_day (batch3);
backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS;
bootstrap_mean_ci, analyze_r_multiples (batch1).

HOW TO RUN:
    python3 src/study_pre_move_target_sensitivity.py
"""

import json
from pathlib import Path

import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from study_pre_move_behavior_batch1 import (
    detect_vacuum_signals_for_day,
    detect_alignment_signal_for_day,
    analyze_r_multiples,
)
from study_pre_move_behavior_batch2_fade import fade_signal
from study_pre_move_behavior_batch3 import (
    detect_volume_imbalance_signal_for_day,
    detect_prior_close_rejection_signal_for_day,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-pre-move-target-sensitivity"
TARGET_R_MULTIPLE_GRID = [0.5, 0.75]


def retarget(sig, target_r):
    entry = sig["entry"]
    risk = abs(entry - sig["stop"])
    new_sig = dict(sig)
    if sig["direction"] == "long":
        new_sig["target"] = entry + target_r * risk
    else:
        new_sig["target"] = entry - target_r * risk
    return new_sig


def simulate_at_target(day_df, sig, target_r):
    retargeted = retarget(sig, target_r)
    sig_series = pd.Series(retargeted)
    outcome = simulate_trade(day_df, sig_series, "signal_time")
    risk_points = abs(retargeted["entry"] - retargeted["stop"])
    if risk_points <= 0:
        return None
    if retargeted["direction"] == "long":
        pnl_gross = outcome["exit_price"] - retargeted["entry"]
    else:
        pnl_gross = retargeted["entry"] - outcome["exit_price"]
    is_resolved = not outcome["exit_reason"].startswith("unresolved")
    pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
    return pnl_net / risk_points


def main():
    print("=" * 78)
    print("EXP-106: TARGET SENSITIVITY CHECK ON 6 FRESH-BEHAVIOR SIGNALS")
    print("=" * 78)
    print("\nFrozen spec: research/studies/pre-move-behavior-target-sensitivity-spec.md\n")

    df, is_synthetic = load_price_data(context="study_pre_move_target_sensitivity.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    session = discovery.between_time("09:30", "16:00")
    day_groups = {d: g for d, g in session.groupby(session.index.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery RTH days: {len(day_groups)}")

    prior_close_map = {}
    prev_close = None
    for day in days_sorted:
        prior_close_map[day] = prev_close
        prev_close = float(day_groups[day]["Close"].iloc[-1])

    streams = {
        "vacuum_continuation": [], "vacuum_fade": [],
        "alignment_continuation": [], "alignment_fade": [],
        "volume_imbalance": [], "prior_close_rejection": [],
    }
    all_signals = {k: [] for k in streams}

    for day in days_sorted:
        day_df = day_groups[day]

        for sig in detect_vacuum_signals_for_day(day_df):
            all_signals["vacuum_continuation"].append((day_df, sig))
            all_signals["vacuum_fade"].append((day_df, fade_signal(sig)))

        align_sig = detect_alignment_signal_for_day(day_df)
        if align_sig is not None:
            all_signals["alignment_continuation"].append((day_df, align_sig))
            all_signals["alignment_fade"].append((day_df, fade_signal(align_sig)))

        vol_sig = detect_volume_imbalance_signal_for_day(day_df)
        if vol_sig is not None:
            all_signals["volume_imbalance"].append((day_df, vol_sig))

        rej_sig = detect_prior_close_rejection_signal_for_day(day_df, prior_close_map[day])
        if rej_sig is not None:
            all_signals["prior_close_rejection"].append((day_df, rej_sig))

    results = {}
    for stream_name, sig_list in all_signals.items():
        results[stream_name] = {}
        for target_r in TARGET_R_MULTIPLE_GRID:
            r_multiples = []
            for day_df, sig in sig_list:
                r = simulate_at_target(day_df, sig, target_r)
                if r is not None:
                    r_multiples.append(r)
            results[stream_name][f"target_{target_r}R"] = analyze_r_multiples(r_multiples)

    verdicts = {}
    any_pass = False
    for stream_name, by_target in results.items():
        for target_key, r in by_target.items():
            key = f"{stream_name}_{target_key}"
            n = r.get("n", 0)
            if n == 0:
                verdicts[key] = "NO_DATA"
            elif r["statistically_credible"] and r["economically_meaningful"]:
                verdicts[key] = "CREDIBLE_PASS"
                any_pass = True
            else:
                verdicts[key] = "FAIL"

    print()
    for stream_name, by_target in results.items():
        for target_key, r in by_target.items():
            print(f"{stream_name} @ {target_key}: {r}")
    print()
    for key, v in verdicts.items():
        print(f"  {key}: {v}")
    print(f"\nAny credible pass found: {any_pass}")

    out = {"search_batch_id": SEARCH_BATCH_ID, "results": results, "verdicts": verdicts, "any_credible_pass": any_pass}
    out_path = DATA_DIR / "study_pre_move_target_sensitivity_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
