"""
study_gap_fade_multiday.py
=============================

H91 / exp-120 -- frozen spec: research/studies/gap-fade-multiday-h91-spec.md.
Multi-day-hold pivot on the gap-down fade (this project's sole
near-miss, H87/H89). Reuses exp-108/109's daily walk-forward exit
mechanism instead of same-day-only intraday exit.

REUSED, UNMODIFIED: TARGET_R_MULTIPLE, ROUND_TRIP_COST_POINTS,
build_daily_bars, block_bootstrap_ci (from
study_multiday_pullback_continuation_v2.py).

HOW TO RUN:
    python3 src/study_gap_fade_multiday.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_level_sweep import TARGET_R_MULTIPLE
from backtest import ROUND_TRIP_COST_POINTS
from study_bar_behavior_batch1 import build_daily_bars
from study_multiday_pullback_continuation_v2 import block_bootstrap_ci
from study_pre_move_behavior_batch1 import analyze_r_multiples, MIN_PROSPECTIVE_N

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-08-observatory-hyp-006c-h91"
GAP_THRESH_MULT = 0.5
ATR_WINDOW = 14
MAX_HOLD_DAYS = 10


def main():
    print("=" * 78)
    print("H91/EXP-120: GAP-DOWN FADE, MULTI-DAY HOLD")
    print("=" * 78)
    print("\nFrozen spec: research/studies/gap-fade-multiday-h91-spec.md\n")

    df, is_synthetic = load_price_data(context="study_gap_fade_multiday.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    daily = build_daily_bars(discovery).copy()
    daily["range"] = daily["High"] - daily["Low"]
    daily["atr14"] = daily["range"].rolling(ATR_WINDOW).mean()
    daily = daily.reset_index()
    date_col = daily.columns[0]
    n_days = len(daily)

    r_list = []
    segment_r_lists = []  # each gap event is its own "segment" (non-overlapping by construction: one signal per day)

    for i in range(1, n_days):
        prior_close = float(daily.iloc[i - 1]["Close"])
        prior_range = float(daily.iloc[i - 1]["range"])
        atr = daily.iloc[i - 1]["atr14"]
        if pd.isna(atr) or atr <= 0 or prior_range <= 0:
            continue
        atr = float(atr)
        day_open = float(daily.iloc[i]["Open"]) if "Open" in daily.columns else None
        if day_open is None:
            continue
        gap = day_open - prior_close
        if gap >= 0 or abs(gap) < GAP_THRESH_MULT * prior_range:
            continue  # long (gap-down fade) only, matching H89

        entry_price = day_open
        entry_idx = i
        stop = entry_price - atr
        target = entry_price + TARGET_R_MULTIPLE * atr
        risk = atr

        exit_price = None
        for j in range(entry_idx, min(entry_idx + MAX_HOLD_DAYS, n_days)):
            bar = daily.iloc[j]
            stop_hit = bar["Low"] <= stop
            target_hit = bar["High"] >= target
            if stop_hit:
                exit_price = stop
                break
            if target_hit:
                exit_price = target
                break
        if exit_price is None:
            timeout_idx = min(entry_idx + MAX_HOLD_DAYS - 1, n_days - 1)
            exit_price = float(daily.iloc[timeout_idx]["Close"])

        pnl_gross = exit_price - entry_price
        pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS
        r = pnl_net / risk
        r_list.append(r)
        segment_r_lists.append([r])  # one trade per segment; overlap is possible if gaps cluster within MAX_HOLD_DAYS

    print(f"\nGap-down fade (multi-day hold) signals: {len(r_list)}")
    result = analyze_r_multiples(r_list)
    block_ci = block_bootstrap_ci(segment_r_lists) if segment_r_lists else (float("nan"), float("nan"))

    print(f"h91_gap_down_fade_multiday: {result}")
    print(f"  block-bootstrap ci_90 (per-event, accounts for possible overlap): {block_ci}")

    n = result.get("n", 0)
    standard_credible = result["statistically_credible"] and result["economically_meaningful"]
    block_credible = block_ci[0] > 0
    if n == 0:
        verdict = "NO_DATA"
    elif standard_credible and block_credible:
        verdict = "STEP_1+2_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN_FOR_PROSPECTIVE"
    else:
        verdict = "STEP_1+2_FAIL"
    print(f"  verdict: {verdict}")

    out = {
        "search_batch_id": SEARCH_BATCH_ID,
        "result": result,
        "block_bootstrap_ci_90": block_ci,
        "verdict": verdict,
    }
    with open(DATA_DIR / "study_gap_fade_multiday_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {DATA_DIR / 'study_gap_fade_multiday_results.json'}")


if __name__ == "__main__":
    main()
