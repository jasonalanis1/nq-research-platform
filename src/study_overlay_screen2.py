"""
study_overlay_screen2.py
=====================================

exp-086/087 -- frozen spec: research/studies/overlay-screen2-spec.md.
Same quick overlay-screen technique as exp-077 (vol-regime), applied to
two newer conditioning facts: the overnight-coil finding (hyp-000056/057)
and the CPI/NFP/FOMC release-day magnitude finding (exp-039/040).
Reuses the 4 Level Sweep Reversal per-trade CSVs already on disk.

HOW TO RUN:
    python3 src/study_overlay_screen2.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_intraday_behavior_batch1 import bootstrap_mean_ci
from study_intraday_behavior_batch3 import build_overnight_and_rth_frame, COIL_PCTL, LOOKBACK_DAYS
from study_economic_calendar import classify_day as classify_cpi_nfp
from study_fomc_volatility import classify_day as classify_fomc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

TRADE_FILES = {
    "level_sweep_close_min_distance_not_protected": "backtest_results_level_sweep_close_min_distance_not_protected_discovery.csv",
    "level_sweep_close_min_distance_protected": "backtest_results_level_sweep_close_min_distance_protected_discovery.csv",
    "level_sweep_full_bar_range_not_protected": "backtest_results_level_sweep_full_bar_range_not_protected_discovery.csv",
    "level_sweep_full_bar_range_protected": "backtest_results_level_sweep_full_bar_range_protected_discovery.csv",
}
MIN_BUCKET_TRADES = 10


def release_day_classification(day) -> str:
    """'release' if CPI, NFP, or FOMC; else 'normal'."""
    c = classify_cpi_nfp(day)
    if c in ("cpi", "nfp"):
        return "release"
    if classify_fomc(day) == "fomc":
        return "release"
    return "normal"


def build_coil_lookup(discovery: pd.DataFrame) -> dict:
    """date -> True (coiled) / False (not coiled), same definition as hyp-000056."""
    frame = build_overnight_and_rth_frame(discovery)
    coil_thresh = frame["overnight_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, COIL_PCTL), raw=True).shift(1)
    is_coiled = frame["overnight_range"] <= coil_thresh.reindex(frame.index)
    return {d: bool(v) for d, v in is_coiled.items() if pd.notna(v)}


def screen_condition(trades: pd.DataFrame, label_col: str, group_a: str, group_b: str) -> dict:
    a = trades.loc[trades[label_col] == group_a, "r_multiple_net"].dropna().tolist()
    b = trades.loc[trades[label_col] == group_b, "r_multiple_net"].dropna().tolist()
    if len(a) < MIN_BUCKET_TRADES or len(b) < MIN_BUCKET_TRADES:
        return {"n_a": len(a), "n_b": len(b), "note": "too few trades in one bucket, skipped"}
    rng = np.random.default_rng(7)
    a_arr, b_arr = np.array(a), np.array(b)
    diffs = np.empty(3000)
    for i in range(3000):
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
    print("OVERLAY SCREEN 2: exp-086 (overnight coil), exp-087 (release-day")
    print("magnitude) on the 4 Level Sweep Reversal variants")
    print("=" * 78)
    print("\nFrozen spec: research/studies/overlay-screen2-spec.md")
    print("search_batch_id: batch-2026-09-08-overlay-screen-2\n")

    df, is_synthetic = load_price_data(context="study_overlay_screen2.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return
    discovery = get_discovery_data(df)

    coil_lookup = build_coil_lookup(discovery)

    results = {"exp_086_overnight_coil": {}, "exp_087_release_day": {}}
    for name, fname in TRADE_FILES.items():
        trades = pd.read_csv(DATA_DIR / fname, parse_dates=["date"])
        trades["date_only"] = trades["date"].dt.date

        trades["coil_label"] = trades["date_only"].map(lambda d: "coiled" if coil_lookup.get(d) else ("not_coiled" if d in coil_lookup else None))
        trades["release_label"] = trades["date_only"].map(lambda d: release_day_classification(d))

        r_coil = screen_condition(trades.dropna(subset=["coil_label"]), "coil_label", "coiled", "not_coiled")
        r_release = screen_condition(trades, "release_label", "release", "normal")

        results["exp_086_overnight_coil"][name] = r_coil
        results["exp_087_release_day"][name] = r_release

        print(f"--- {name} ---")
        print(f"  coil:    {r_coil}")
        print(f"  release: {r_release}")

    out_path = DATA_DIR / "study_overlay_screen2_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
