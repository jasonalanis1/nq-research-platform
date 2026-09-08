"""
study_intraday_behavior_batch3.py
=====================================

exp-083/084 -- frozen spec: research/studies/intraday-behavior-batch3-spec.md.
The remaining 2 of the Market Behavior Advisor's 5 original candidates
from the batch-2 sourcing round.

STEP 1 ONLY. Search batch ID: batch-2026-09-08-intraday-behavior-3.

HOW TO RUN:
    python3 src/study_intraday_behavior_batch3.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_overnight_gap import get_reference_close
from study_intraday_behavior_batch1 import bootstrap_mean_ci, build_daily_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

LULL_START, LULL_END = "12:00", "13:00"
AFTERNOON_START = "13:00"
COIL_PCTL = 20
LOOKBACK_DAYS = 20


def analyze_lull_reengagement(df: pd.DataFrame) -> dict:
    """exp-083: midday lull's own net direction -> afternoon (13:00-close)
    return, signed WITH the lull's own direction."""
    signed_rets = []
    for day, day_df in df.groupby(df.index.date):
        lull = day_df.between_time(LULL_START, LULL_END)
        afternoon = day_df.between_time(AFTERNOON_START, "16:00")
        if len(lull) < 30 or afternoon.empty:
            continue
        lull_open = lull["Open"].iloc[0]
        lull_close = lull["Close"].iloc[-1]
        lull_ret = np.log(lull_close / lull_open)
        if lull_ret == 0:
            continue
        direction = np.sign(lull_ret)
        afternoon_close = afternoon["Close"].iloc[-1]
        afternoon_ret = np.log(afternoon_close / lull_close)
        signed_rets.append(direction * afternoon_ret)

    mean = float(np.mean(signed_rets)) if signed_rets else float("nan")
    ci = bootstrap_mean_ci(signed_rets) if signed_rets else (float("nan"), float("nan"))
    credible = bool(signed_rets) and (ci[0] > 0 or ci[1] < 0)
    return {"n": len(signed_rets), "mean_signed_afternoon_return": mean, "ci_90": ci, "statistically_credible": credible}


def build_overnight_and_rth_frame(df: pd.DataFrame) -> pd.DataFrame:
    """One row per day: overnight (prior 16:00 ET -> this day's 09:30 ET)
    range, and this day's own RTH (09:30-16:00) range.

    NOTE: implemented via a single groupby + index.searchsorted rather than
    per-day full-frame boolean masks -- the naive version is O(n_days *
    n_rows) and does not finish in reasonable time on a multi-year 1-min
    dataset. This is a performance-only change; the definitions themselves
    are unchanged from the frozen spec.
    """
    tz = df.index.tz
    idx = df.index
    grouped = {d: g for d, g in df.groupby(idx.date)}
    days = sorted(grouped.keys())
    rows = []
    for i in range(1, len(days)):
        day = days[i]
        prior_day = days[i - 1]
        day_df = grouped[day]
        prior_df = grouped[prior_day]
        if day_df.empty or prior_df.empty:
            continue
        ref_close = get_reference_close(prior_df, prior_day, tz)
        if ref_close is None:
            continue
        overnight_start = pd.Timestamp(prior_day, tz=tz).replace(hour=16, minute=0)
        open_time = pd.Timestamp(day, tz=tz).replace(hour=9, minute=30)
        lo = idx.searchsorted(overnight_start, side="left")
        hi = idx.searchsorted(open_time, side="left")
        overnight = df.iloc[lo:hi]
        rth = day_df.between_time("09:30", "16:00")
        if overnight.empty or rth.empty:
            continue
        overnight_range = float(overnight["High"].max() - overnight["Low"].min())
        rth_range = float(rth["High"].max() - rth["Low"].min())
        rows.append({"date": day, "overnight_range": overnight_range, "rth_range": rth_range})
    out = pd.DataFrame(rows).set_index("date").sort_index()
    out["trailing_avg_overnight_range"] = out["overnight_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    out["trailing_avg_rth_range"] = out["rth_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    return out


def analyze_overnight_coil(frame: pd.DataFrame) -> dict:
    """exp-084: coiled overnight range (bottom 20th pctl of own trailing
    20-day overnight-range distribution) -> that day's own RTH range ratio."""
    coil_thresh = frame["overnight_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, COIL_PCTL), raw=True).shift(1)
    valid = frame.dropna(subset=["trailing_avg_rth_range"]).copy()
    valid["rth_range_ratio"] = valid["rth_range"] / valid["trailing_avg_rth_range"]
    is_coiled = valid["overnight_range"] <= coil_thresh.reindex(valid.index)
    ratios = valid.loc[is_coiled.fillna(False), "rth_range_ratio"].dropna().tolist()

    mean = float(np.mean(ratios)) if ratios else float("nan")
    ci = bootstrap_mean_ci(ratios) if ratios else (float("nan"), float("nan"))
    credible = bool(ratios) and (ci[0] > 1.0 or ci[1] < 1.0)
    return {"n": len(ratios), "mean_rth_range_ratio": mean, "ci_90": ci, "statistically_credible": credible}


def main():
    print("=" * 78)
    print("INTRADAY BEHAVIOR BATCH 3: exp-083 (lull re-engagement), exp-084")
    print("(overnight coiling) -- Step 1 only")
    print("=" * 78)
    print("\nFrozen spec: research/studies/intraday-behavior-batch3-spec.md")
    print("search_batch_id: batch-2026-09-08-intraday-behavior-3\n")

    df, is_synthetic = load_price_data(context="study_intraday_behavior_batch3.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)

    print("--- exp-083: Midday lull character / afternoon re-engagement ---")
    lull = analyze_lull_reengagement(discovery)
    print(f"  n={lull['n']} mean_signed_afternoon_return={lull['mean_signed_afternoon_return']:.6f} "
          f"ci_90={lull['ci_90']} credible={lull['statistically_credible']}")

    print("\n--- exp-084: Overnight range compression (pre-open coiling) ---")
    frame = build_overnight_and_rth_frame(discovery)
    coil = analyze_overnight_coil(frame)
    print(f"  n={coil['n']} mean_rth_range_ratio={coil['mean_rth_range_ratio']:.6f} "
          f"ci_90={coil['ci_90']} credible={coil['statistically_credible']}")

    print("\n" + "=" * 78)
    verdicts = {
        "lull_reengagement": "STEP_1_PASS" if lull["statistically_credible"] else "STEP_1_FAIL",
        "overnight_coil": "STEP_1_PASS" if coil["statistically_credible"] else "STEP_1_FAIL",
    }
    for k, v in verdicts.items():
        print(f"  {k}: {v}")

    out = {
        "search_batch_id": "batch-2026-09-08-intraday-behavior-3",
        "lull_reengagement": lull,
        "overnight_coil": coil,
        "verdicts": verdicts,
    }
    out_path = DATA_DIR / "study_intraday_behavior_batch3_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
