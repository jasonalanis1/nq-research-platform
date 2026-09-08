"""
study_cot_positioning_prospective.py
=======================================

exp-092 -- frozen spec: research/studies/cot-positioning-prospective-spec.md.
Single pre-registered Validation-slice prospective test of exp-091
(hyp-000063), unmodified method and thresholds.

REUSED, UNMODIFIED: resolve_availability_dates, build_forward_returns,
run_step1, run_step2 from study_cot_positioning.py. long_group is fixed
at -1.0 (fade leveraged-money's own positioning change), determined by
exp-091's Discovery-stage result -- NOT re-derived here.

HOW TO RUN:
    python3 src/study_cot_positioning_prospective.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_validation_data
from study_volatility_regime import compute_daily_ref_closes
from study_cot_positioning import (
    resolve_availability_dates,
    run_step2,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
COT_FILES = [
    DATA_DIR / "cftc_tff_nq_mini_2015_2018.csv",
    DATA_DIR / "cftc_tff_nq_mini_2019_2021.csv",
    DATA_DIR / "cftc_tff_nq_mini_2022_2023.csv",
]
LONG_GROUP = -1.0  # fixed from exp-091's Discovery-stage result, not re-derived


def load_full_combined_cot_signal() -> pd.DataFrame:
    """Full 2015-2023 series, so the week-over-week delta is continuous
    across the Discovery/Validation boundary (no artificial NaN reset)."""
    frames = [pd.read_csv(f, parse_dates=["Report_Date_as_YYYY-MM-DD"]) for f in COT_FILES]
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset=["Report_Date_as_YYYY-MM-DD"])
    df = df.sort_values("Report_Date_as_YYYY-MM-DD").reset_index(drop=True)
    df["net_lev_money"] = df["Lev_Money_Positions_Long_All"] - df["Lev_Money_Positions_Short_All"]
    df["delta_net_lev_money"] = df["net_lev_money"].diff()
    df["signal"] = np.sign(df["delta_net_lev_money"])
    df["raw_availability_date"] = df["Report_Date_as_YYYY-MM-DD"] + pd.Timedelta(days=3)
    return df


def build_forward_returns_any_slice(cot_df: pd.DataFrame, ref_closes: dict) -> pd.DataFrame:
    """Same logic as study_cot_positioning.build_forward_returns, but
    over the full multi-year cot_df -- only rows whose availability_date
    AND next availability_date both resolve in the passed ref_closes
    (i.e. both fall in whatever slice ref_closes was built from) survive."""
    cot_df = cot_df.dropna(subset=["availability_date"]).reset_index(drop=True)
    rows = []
    for i in range(len(cot_df) - 1):
        this_row = cot_df.iloc[i]
        next_row = cot_df.iloc[i + 1]
        if pd.isna(this_row["signal"]):
            continue
        this_avail = this_row["availability_date"]
        next_avail = next_row["availability_date"]
        if ref_closes.get(this_avail) is None or ref_closes.get(next_avail) is None:
            continue
        fwd_return = float(ref_closes[next_avail] - ref_closes[this_avail])
        rows.append({
            "report_date": this_row["Report_Date_as_YYYY-MM-DD"],
            "availability_date": this_avail,
            "signal": float(this_row["signal"]),
            "forward_return": fwd_return,
        })
    return pd.DataFrame(rows)


def main():
    print("=" * 78)
    print("CFTC COT POSITIONING -- VALIDATION-SLICE PROSPECTIVE TEST (exp-092)")
    print("=" * 78)

    full_df, is_synthetic = load_price_data(context="study_cot_positioning_prospective.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    validation_df = get_validation_data(full_df)
    day_groups = {day: sub for day, sub in validation_df.groupby(validation_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)

    cot_df = load_full_combined_cot_signal()
    print(f"\nFull combined weekly reports (2015-2023): {len(cot_df)}")

    # IMPORTANT: resolve_availability_dates rolls a raw_availability_date
    # FORWARD to the nearest day present in the passed ref_closes. Since
    # ref_closes here is Validation-only, an unfiltered Discovery-era
    # report's raw_availability_date (e.g. 2018-05-01) would incorrectly
    # roll all the way forward to the Validation slice's first day
    # instead of being excluded -- corrupting the test with misdated
    # signal rows. Guard against this explicitly: only pass through
    # reports whose raw_availability_date already falls at or near the
    # Validation window (a small pre-window buffer covers the one
    # boundary-straddling report whose signal continuity we needed the
    # full series for, but whose OWN availability date must still be
    # genuinely in-or-adjacent-to Validation to be scored).
    validation_start = pd.Timestamp(min(d for d in ref_closes if ref_closes[d] is not None), tz=cot_df["raw_availability_date"].dt.tz)
    validation_end = pd.Timestamp(max(d for d in ref_closes if ref_closes[d] is not None), tz=cot_df["raw_availability_date"].dt.tz)
    pre_window_buffer = pd.Timedelta(days=10)
    in_window = (cot_df["raw_availability_date"] >= validation_start - pre_window_buffer) & \
                (cot_df["raw_availability_date"] <= validation_end)
    print(f"Reports with raw_availability_date near/in Validation window: {int(in_window.sum())} of {len(cot_df)}")
    cot_df = cot_df[in_window].reset_index(drop=True)

    cot_df = resolve_availability_dates(cot_df, ref_closes)
    fwd_df = build_forward_returns_any_slice(cot_df, ref_closes)
    print(f"Weeks with a usable Validation-slice forward return: {len(fwd_df)}")
    if len(fwd_df):
        print(f"Date range: {fwd_df['availability_date'].min()} to {fwd_df['availability_date'].max()}")

    step2 = run_step2(fwd_df, LONG_GROUP)
    print("\n--- STEP 2 (prospective, costed weekly rule, fixed long_group=-1.0) ---")
    for k, v in step2.items():
        print(f"  {k}: {v}")

    verdict = "PROSPECTIVE_PASS" if (step2["statistically_credible"] and step2["economically_meaningful"]) else "PROSPECTIVE_FAIL"
    print(f"\nVerdict: {verdict}")

    out = {"step2_prospective": step2, "verdict": verdict, "n_weeks": len(fwd_df)}
    out_path = DATA_DIR / "study_cot_positioning_prospective_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
