"""
study_overlay_screen3_gap_fade.py
==================================

exp-119 -- frozen spec: research/studies/overlay-screen3-gap-fade-spec.md.
Overlay screen: do the 2 validated volatility findings (range-contraction,
hyp-000046/048; overnight coil, hyp-000056/057) condition the economics
of H89 (gap-down fade, long-only, ATR-scaled stop) -- the project's
closest-ever near-miss? Never tried before. Reuses H89's exact signal
logic unchanged, and both classifiers unchanged from their own hypotheses.

HOW TO RUN:
    python3 src/study_overlay_screen3_gap_fade.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_level_sweep import TARGET_R_MULTIPLE
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from study_bar_behavior_batch1 import build_daily_bars
from study_intraday_behavior_batch1 import RANGE_NARROW_PCTL, LOOKBACK_DAYS as RC_LOOKBACK
from study_intraday_behavior_batch3 import build_overnight_and_rth_frame, COIL_PCTL, LOOKBACK_DAYS as COIL_LOOKBACK

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-09-overlay-screen-3-h89"
GAP_THRESH_MULT = 0.5
ATR_WINDOW = 14
MIN_BUCKET_TRADES = 10
N_BOOTSTRAP = 3000


def simulate_signal(day_df, sig):
    sig_series = pd.Series(sig)
    outcome = simulate_trade(day_df, sig_series, "signal_time")
    risk_points = abs(sig["entry"] - sig["stop"])
    if risk_points <= 0:
        return None
    pnl_gross = outcome["exit_price"] - sig["entry"]
    is_resolved = not outcome["exit_reason"].startswith("unresolved")
    pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
    return pnl_net / risk_points


def build_narrow_lookup(daily_bars: pd.DataFrame) -> dict:
    """date -> True (narrow prior day) / False, RANGE_NARROW_PCTL of
    trailing RC_LOOKBACK-day range distribution. Unchanged from
    hyp-000046/048's analyze_range_contraction()."""
    rng_series = daily_bars["range"]
    narrow_thresh = rng_series.rolling(RC_LOOKBACK, min_periods=RC_LOOKBACK).apply(
        lambda w: np.percentile(w, RANGE_NARROW_PCTL), raw=True)
    is_narrow = rng_series <= narrow_thresh.reindex(rng_series.index)
    return {d: bool(v) for d, v in is_narrow.items() if pd.notna(narrow_thresh.get(d))}


def build_coil_lookup(discovery: pd.DataFrame) -> dict:
    """date -> True (coiled) / False. Unchanged from hyp-000056/057 /
    study_overlay_screen2.py's build_coil_lookup."""
    frame = build_overnight_and_rth_frame(discovery)
    coil_thresh = frame["overnight_range"].rolling(COIL_LOOKBACK, min_periods=COIL_LOOKBACK).apply(
        lambda w: np.percentile(w, COIL_PCTL), raw=True).shift(1)
    is_coiled = frame["overnight_range"] <= coil_thresh.reindex(frame.index)
    return {d: bool(v) for d, v in is_coiled.items() if pd.notna(v)}


def screen_condition(trades: pd.DataFrame, label_col: str, group_a, group_b: object) -> dict:
    a = trades.loc[trades[label_col] == group_a, "r_multiple"].dropna().tolist()
    b = trades.loc[trades[label_col] == group_b, "r_multiple"].dropna().tolist()
    if len(a) < MIN_BUCKET_TRADES or len(b) < MIN_BUCKET_TRADES:
        return {"n_a": len(a), "n_b": len(b), "note": "too few trades in one bucket, skipped"}
    rng = np.random.default_rng(7)
    a_arr, b_arr = np.array(a), np.array(b)
    diffs = np.empty(N_BOOTSTRAP)
    for i in range(N_BOOTSTRAP):
        diffs[i] = rng.choice(a_arr, size=len(a_arr), replace=True).mean() - rng.choice(b_arr, size=len(b_arr), replace=True).mean()
    ci = (float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95)))
    credible = ci[0] > 0 or ci[1] < 0
    return {
        "n_a": len(a), "n_b": len(b),
        "mean_a": float(np.mean(a_arr)), "mean_b": float(np.mean(b_arr)),
        "diff": float(np.mean(a_arr) - np.mean(b_arr)),
        "ci_90": ci, "credible": credible,
    }


def main():
    print("=" * 78)
    print("OVERLAY SCREEN 3: range-contraction + overnight-coil on H89 gap-fade")
    print("=" * 78)
    print("\nFrozen spec: research/studies/overlay-screen3-gap-fade-spec.md\n")

    df, is_synthetic = load_price_data(context="study_overlay_screen3_gap_fade.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    narrow_lookup = build_narrow_lookup(daily_bars)
    coil_lookup = build_coil_lookup(discovery)

    trade_rows = []
    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index or day not in daily_bars.index:
            continue
        prior_close = float(daily_bars.loc[prior_day, "Close"])
        prior_range = float(daily_bars.loc[prior_day, "range"])
        atr = daily_bars.loc[prior_day, "atr14"]
        if pd.isna(atr) or atr <= 0 or prior_range <= 0:
            continue
        atr = float(atr)
        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty:
            continue
        open_price = float(rth["Close"].iloc[0])
        gap = open_price - prior_close
        if gap >= 0 or abs(gap) < GAP_THRESH_MULT * prior_range:
            continue
        entry = open_price
        stop = entry - atr
        target = entry + TARGET_R_MULTIPLE * atr
        sig = {"signal_time": rth.index[0], "direction": "long", "entry": entry, "stop": stop, "target": target}
        r = simulate_signal(rth, sig)
        if r is not None:
            trade_rows.append({
                "date": day,
                "r_multiple": r,
                "narrow_prior_day": narrow_lookup.get(prior_day),
                "coiled": coil_lookup.get(prior_day),
            })

    trades = pd.DataFrame(trade_rows)
    print(f"\nTotal H89 long gap-down-fade trades regenerated: {len(trades)}")

    trades["narrow_label"] = trades["narrow_prior_day"].map(lambda v: "narrow" if v is True else ("not_narrow" if v is False else None))
    trades["coil_label"] = trades["coiled"].map(lambda v: "coiled" if v is True else ("not_coiled" if v is False else None))

    r_range_contraction = screen_condition(trades.dropna(subset=["narrow_label"]), "narrow_label", "narrow", "not_narrow")
    r_coil = screen_condition(trades.dropna(subset=["coil_label"]), "coil_label", "coiled", "not_coiled")

    print("\n--- range-contraction (narrow prior day vs not) ---")
    print(f"  {r_range_contraction}")
    print("\n--- overnight coil (coiled prior night vs not) ---")
    print(f"  {r_coil}")

    results = {
        "exp_119_range_contraction_on_h89": r_range_contraction,
        "exp_119_overnight_coil_on_h89": r_coil,
    }
    out = {"search_batch_id": SEARCH_BATCH_ID, "total_trades": len(trades), "results": results}
    out_path = DATA_DIR / "study_overlay_screen3_gap_fade_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
