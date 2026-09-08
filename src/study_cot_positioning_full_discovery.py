"""
study_cot_positioning_full_discovery.py
=========================================

exp-091 -- frozen spec: research/studies/cot-positioning-full-discovery-spec.md.
Follow-up to exp-044 (study_cot_positioning.py), extending the same
frozen method, unmodified, to the full Discovery window (2015-2018 +
newly-provided 2019-2021 CFTC TFF data) instead of just 2015-2018.

REUSED, UNMODIFIED: everything from study_cot_positioning.py --
load_cot_signal, resolve_availability_dates, build_forward_returns,
bootstrap_diff_ci, run_step1, run_step2.

HOW TO RUN:
    python3 src/study_cot_positioning_full_discovery.py
"""

from pathlib import Path

import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS  # noqa: F401 (used inside study_cot_positioning)
from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes
from study_cot_positioning import (
    resolve_availability_dates,
    build_forward_returns,
    run_step1,
    run_step2,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
COT_CSV_2015_2018 = DATA_DIR / "cftc_tff_nq_mini_2015_2018.csv"
COT_CSV_2019_2021 = DATA_DIR / "cftc_tff_nq_mini_2019_2021.csv"


def load_combined_cot_signal() -> pd.DataFrame:
    """Same construction as study_cot_positioning.load_cot_signal, but
    over the concatenation of both CSVs instead of just 2015-2018."""
    a = pd.read_csv(COT_CSV_2015_2018, parse_dates=["Report_Date_as_YYYY-MM-DD"])
    b = pd.read_csv(COT_CSV_2019_2021, parse_dates=["Report_Date_as_YYYY-MM-DD"])
    df = pd.concat([a, b], ignore_index=True)
    df = df.drop_duplicates(subset=["Report_Date_as_YYYY-MM-DD"])
    df = df.sort_values("Report_Date_as_YYYY-MM-DD").reset_index(drop=True)
    df["net_lev_money"] = df["Lev_Money_Positions_Long_All"] - df["Lev_Money_Positions_Short_All"]
    df["delta_net_lev_money"] = df["net_lev_money"].diff()
    import numpy as np
    df["signal"] = np.sign(df["delta_net_lev_money"])
    df["raw_availability_date"] = df["Report_Date_as_YYYY-MM-DD"] + pd.Timedelta(days=3)
    return df


def main():
    print("=" * 78)
    print("CFTC COMMITMENT-OF-TRADERS POSITIONING -- FULL DISCOVERY WINDOW (exp-091)")
    print("Leveraged Money category, NASDAQ-100 E-mini, 2015-2021 (full Discovery)")
    print("=" * 78)

    full_df, is_synthetic = load_price_data(context="study_cot_positioning_full_discovery.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return
    if not COT_CSV_2019_2021.exists():
        print(f"ABORT: {COT_CSV_2019_2021} not found.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)

    cot_df = load_combined_cot_signal()
    print(f"\nCombined weekly reports loaded: {len(cot_df)} "
          f"({cot_df['Report_Date_as_YYYY-MM-DD'].min().date()} to "
          f"{cot_df['Report_Date_as_YYYY-MM-DD'].max().date()})")

    cot_df = resolve_availability_dates(cot_df, ref_closes)
    fwd_df = build_forward_returns(cot_df, ref_closes)
    print(f"Weeks with a usable forward return: {len(fwd_df)}")

    step1 = run_step1(fwd_df)
    print("\n--- STEP 1: descriptive, difference-of-means (drift-controlled) ---")
    for k, v in step1.items():
        print(f"  {k}: {v}")
    print(f"\n  Step 1 pass (90% CI on the difference entirely on one side of zero)? "
          f"{step1['step1_pass']}")

    result = {"step1": step1, "step2": None}
    if step1["step1_pass"]:
        step2 = run_step2(fwd_df, step1["long_group_if_pass"])
        print("\n--- STEP 2: costed weekly rule ---")
        for k, v in step2.items():
            print(f"  {k}: {v}")
        result["step2"] = step2

    import json
    out_path = DATA_DIR / "study_cot_positioning_full_discovery_results.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
