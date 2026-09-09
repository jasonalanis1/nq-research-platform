"""
study_midday_lull_afternoon_expansion.py
=========================================

exp-125 -- frozen spec: research/studies/observatory-v7-design-spec.md.
Does an unusually narrow midday (12:00-14:00, lowest-participation
window) predict an unusually wide afternoon (14:00-16:00, participation
resumes)? Magnitude-based (range ratio), same measurement convention as
hyp-000046/048 (range-contraction persistence), applied to a session
transition instead of a day-to-day transition.

HOW TO RUN:
    python3 src/study_midday_lull_afternoon_expansion.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOOKBACK_DAYS = 20
NARROW_PCTL = 20
N_BOOTSTRAP = 3000
MIN_N = 40


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=7):
    if len(values) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    means = rng.choice(arr, size=(n_bootstrap, len(arr)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def main():
    print("=" * 78)
    print("MIDDAY LULL -> AFTERNOON EXPANSION (exp-125)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/observatory-v7-design-spec.md\n")

    df, is_synthetic = load_price_data(context="study_midday_lull_afternoon_expansion.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    rows = []
    for day in days_sorted:
        day_df = day_groups[day]
        midday = day_df.between_time("12:00", "14:00")
        afternoon = day_df.between_time("14:00", "16:00")
        if midday.empty or afternoon.empty:
            continue
        midday_range = float(midday["High"].max() - midday["Low"].min())
        afternoon_range = float(afternoon["High"].max() - afternoon["Low"].min())
        rows.append({"date": day, "midday_range": midday_range, "afternoon_range": afternoon_range})

    daily = pd.DataFrame(rows).set_index("date").sort_index()
    daily["trailing_avg_midday_range"] = daily["midday_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    daily["trailing_avg_afternoon_range"] = daily["afternoon_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    narrow_thresh = daily["midday_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, NARROW_PCTL), raw=True).shift(1)

    valid = daily.dropna(subset=["trailing_avg_midday_range", "trailing_avg_afternoon_range"]).copy()
    valid["afternoon_range_ratio"] = valid["afternoon_range"] / valid["trailing_avg_afternoon_range"]
    valid["is_narrow_midday"] = valid["midday_range"] <= narrow_thresh.reindex(valid.index)

    narrow = valid.loc[valid["is_narrow_midday"], "afternoon_range_ratio"].dropna().tolist()
    not_narrow = valid.loc[~valid["is_narrow_midday"], "afternoon_range_ratio"].dropna().tolist()

    print(f"\nTotal usable days: {len(valid)}")
    print(f"Narrow-midday days: {len(narrow)}, not-narrow days: {len(not_narrow)}")

    result = {}
    for label, vals in (("narrow_midday", narrow), ("not_narrow_midday", not_narrow)):
        if len(vals) < 10:
            continue
        ci = bootstrap_mean_ci(vals)
        credible = bool(vals) and (ci[0] > 1.0 or ci[1] < 1.0)
        result[label] = {"n": len(vals), "mean_afternoon_range_ratio": float(np.mean(vals)), "ci_90": ci, "statistically_credible": credible}
        print(f"{label}: {result[label]}")

    verdict = "NO_DATA"
    if "narrow_midday" in result:
        n = result["narrow_midday"]["n"]
        cred = result["narrow_midday"]["statistically_credible"]
        mean_ratio = result["narrow_midday"]["mean_afternoon_range_ratio"]
        if cred and mean_ratio > 1.0 and n >= MIN_N:
            verdict = "STEP_1_PASS"
        elif cred and n >= MIN_N:
            verdict = "STEP_1_PASS_WRONG_DIRECTION"
        else:
            verdict = "STEP_1_FAIL"
    print(f"\nVerdict: {verdict}")

    out = {"search_batch_id": "batch-2026-09-09-observatory-v7-midday-lull", "result": result, "verdict": verdict}
    out_path = DATA_DIR / "study_midday_lull_afternoon_expansion_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
