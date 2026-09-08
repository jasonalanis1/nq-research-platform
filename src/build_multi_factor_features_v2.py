"""
build_multi_factor_features_v2.py
====================================

Pure data assembly for the v2 ensemble attempt (see
research/studies/ensemble-v2-scoping.md for the frozen spec). Same as
build_multi_factor_features.py (exp-046's inputs), with exactly ONE
change: adds `event_day_realized_move_zscore`, a continuous magnitude
column populated only on CPI/NFP days (0 elsewhere), alongside the
existing `event_type` categorical column (kept unchanged) -- the
Advisor's fix for the "sparse dummy" risk flagged in review: the model
sees BOTH "is this an event day" (event_type) and, when it is one,
"how large was that day's realized move" (the new column), rather than
collapsing both into one sparse magnitude column filled with 0 for
~93% of rows.

event_day_realized_move_zscore = abs(daily log return) / trailing
20-day realized-move stdev (reuses compute_trailing_volatility()
unmodified, study_volatility_regime.py) -- computed from EXISTING NQ
price history for the full Discovery window, NOT from the small
67-row options-purchased subsample (data/study_options_vrp_check_rows.csv)
used in the just-closed options-VRP check (exp-063/hyp-000036). This
is a deliberate choice, per the ensemble-v2 scoping doc: full coverage,
zero new cost, at the price of using realized-move-alone rather than
options-implied-vs-realized (a different, more modest claim -- exp-063
already showed implied doesn't predict realized; this column doesn't
resurrect that claim, it just uses "how big was the actual move" as an
ordinary continuous feature, same epistemic status as overnight_gap_pts).

HOW TO RUN:
    python3 src/build_multi_factor_features_v2.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_economic_calendar import classify_day as classify_cpi_nfp_day
from study_fomc_volatility import classify_day as classify_fomc_day
from study_futures_expiration import make_is_expiration_week
from study_overnight_gap import compute_day_gap_and_returns
from study_nq_trend_following import compute_momentum_signal, compute_positions
from study_turn_of_month import classify_turn_of_month
from study_volatility_regime import (
    classify_regimes,
    compute_daily_log_returns,
    compute_daily_ref_closes,
    compute_trailing_volatility,
)
from study_cot_positioning import load_cot_signal, resolve_availability_dates

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUT_CSV = DATA_DIR / "multi_factor_features_v2_discovery.csv"


def combine_event_type(day) -> str:
    cpi_nfp_type = classify_cpi_nfp_day(day)
    fomc_type = classify_fomc_day(day)
    if cpi_nfp_type in ("cpi", "nfp"):
        return cpi_nfp_type
    if fomc_type == "fomc":
        return "fomc"
    if fomc_type == "fomc_cpi_overlap_excluded":
        return "fomc_cpi_overlap"
    return "normal"


def main():
    full_df, is_synthetic = load_price_data(context="build_multi_factor_features_v2.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    all_days = sorted(day_groups.keys())

    ref_closes = compute_daily_ref_closes(day_groups)
    returns = compute_daily_log_returns(ref_closes)
    vol_by_day = compute_trailing_volatility(returns, all_days)
    regime_by_day = classify_regimes(vol_by_day)
    mom_magnitude_by_day = compute_momentum_signal(returns, all_days)
    mom_by_day = compute_positions(mom_magnitude_by_day)
    turn_flags = classify_turn_of_month(all_days)
    is_exp_week = make_is_expiration_week(all_days[0].year, all_days[-1].year)

    cot_df = load_cot_signal()
    cot_df = resolve_availability_dates(cot_df, ref_closes)
    cot_signal_by_avail_date = {
        row["availability_date"]: row["signal"]
        for _, row in cot_df.iterrows()
        if row["availability_date"] is not None and not pd.isna(row["signal"])
    }

    valid_days = [d for d in all_days if ref_closes.get(d) is not None]

    rows = []
    for i, day in enumerate(valid_days):
        row = {"date": day}
        row["day_of_week"] = day.weekday()
        row["turn_of_month"] = bool(turn_flags.get(day, False))
        row["is_expiration_week"] = bool(is_exp_week(day))
        event_type = combine_event_type(day)
        row["event_type"] = event_type
        row["vol_regime"] = regime_by_day.get(day)
        row["momentum_sign"] = mom_by_day.get(day)

        # NEW (v2): realized-move z-score, event days only, 0 elsewhere
        day_return = returns.get(day)
        trailing_vol = vol_by_day.get(day)
        if event_type in ("cpi", "nfp") and day_return is not None and trailing_vol not in (None, 0):
            row["event_day_realized_move_zscore"] = abs(day_return) / trailing_vol
        else:
            row["event_day_realized_move_zscore"] = 0.0

        if i > 0:
            prior_day = valid_days[i - 1]
            gap_result = compute_day_gap_and_returns(
                day_groups[prior_day], day_groups[day], day, prior_day
            )
            row["overnight_gap_pts"] = gap_result["gap"] if gap_result else None
        else:
            row["overnight_gap_pts"] = None

        cftc_raw = cot_signal_by_avail_date.get(day)
        row["cftc_signal_available"] = cftc_raw is not None
        row["cftc_signal"] = float(cftc_raw) if cftc_raw is not None else 0.0

        if i + 1 < len(valid_days):
            next_day = valid_days[i + 1]
            fwd = ref_closes[next_day] - ref_closes[day]
            row["target_next_day_return_pts"] = fwd
            row["target_next_day_return_sign"] = int(np.sign(fwd)) if fwd != 0 else 0
        else:
            row["target_next_day_return_pts"] = None
            row["target_next_day_return_sign"] = None

        rows.append(row)

    out_df = pd.DataFrame(rows).set_index("date")
    out_df.to_csv(OUT_CSV)

    print("=" * 78)
    print("MULTI-FACTOR FEATURE TABLE v2 -- pure data assembly, no test run")
    print("=" * 78)
    print(f"\nRows: {len(out_df)}, date range {out_df.index.min()} .. {out_df.index.max()}")
    print(f"Columns: {list(out_df.columns)}")
    n_nonzero_zscore = int((out_df['event_day_realized_move_zscore'] != 0).sum())
    print(f"\nevent_day_realized_move_zscore nonzero on {n_nonzero_zscore} rows "
          f"(should roughly match CPI+NFP day count with sufficient trailing history)")
    print(f"\nSaved to {OUT_CSV}.")
    print("\nThis file is raw material only. No model has been fit, nothing here is a result.")


if __name__ == "__main__":
    main()
