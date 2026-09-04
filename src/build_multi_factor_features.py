"""
build_multi_factor_features.py
================================

Pure data assembly -- NOT a hypothesis test, NOT a study, and NOT the
multi-factor model itself. This script does not fit anything, evaluate
anything, or produce a verdict. It exists solely to pull the individual
features already computed across past studies into one joined table,
one row per Discovery-slice trading day, so that whichever version of
the multi-factor model gets frozen (per
`research/studies/multi-factor-combination-scoping.md`, still a draft
awaiting Jason's and the Advisor's sign-off) has its raw ingredients
ready rather than needing to re-derive them from scratch.

Every column below reuses an existing, unmodified function or constant
from an existing study file -- nothing new is computed except the
mechanical joins needed to line everything up on a single per-day
index. See each column's source noted inline.

Two target-variable candidates (next-day return in points, and its
sign) are included as descriptive data only -- this script does not
decide which target the eventual model will use; that choice is still
open per the scoping document.

Discovery slice only (`data_split.get_discovery_data`), matching every
other search-stage artifact in this project.

HOW TO RUN:
    python3 src/build_multi_factor_features.py
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
from study_nq_trend_following import compute_momentum_signal
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
OUT_CSV = DATA_DIR / "multi_factor_features_discovery.csv"


def combine_event_type(day) -> str:
    """Reuses study_economic_calendar.classify_day() and
    study_fomc_volatility.classify_day() unmodified, combined with the
    exact same precedence already used in
    study_post_release_continuation.scan_all_days(): a CPI/NFP day is
    reported as such even on the 6 known FOMC/CPI overlap dates (their
    8:30 AM classification is unaffected by the 2:00 PM FOMC event)."""
    cpi_nfp_type = classify_cpi_nfp_day(day)   # 'cpi' / 'nfp' / 'normal'
    fomc_type = classify_fomc_day(day)         # 'fomc' / 'fomc_cpi_overlap_excluded' / 'normal'
    if cpi_nfp_type in ("cpi", "nfp"):
        return cpi_nfp_type
    if fomc_type == "fomc":
        return "fomc"
    if fomc_type == "fomc_cpi_overlap_excluded":
        return "fomc_cpi_overlap"
    return "normal"


def main():
    full_df, is_synthetic = load_price_data(context="build_multi_factor_features.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    all_days = sorted(day_groups.keys())

    # --- Reused, unmodified machinery from past studies ---
    ref_closes = compute_daily_ref_closes(day_groups)                  # study_volatility_regime
    returns = compute_daily_log_returns(ref_closes)                    # study_volatility_regime
    vol_by_day = compute_trailing_volatility(returns, all_days)        # study_volatility_regime
    regime_by_day = classify_regimes(vol_by_day)                       # study_volatility_regime
    mom_by_day = compute_momentum_signal(returns, all_days)            # study_nq_trend_following
    turn_flags = classify_turn_of_month(all_days)                      # study_turn_of_month
    is_exp_week = make_is_expiration_week(all_days[0].year, all_days[-1].year)  # study_futures_expiration

    cot_df = load_cot_signal()                                         # study_cot_positioning
    cot_df = resolve_availability_dates(cot_df, ref_closes)            # study_cot_positioning
    cot_signal_by_avail_date = {
        row["availability_date"]: row["signal"]
        for _, row in cot_df.iterrows()
        if row["availability_date"] is not None and not pd.isna(row["signal"])
    }

    # IMPORTANT: the raw per-calendar-day grouping includes spurious
    # "Sunday" entries -- NQ's Sunday-evening reopen bars get grouped
    # under Sunday's own date, which has no 8:30 AM-4:00 PM ET session
    # and therefore no valid reference close. Left unfiltered, that
    # silently breaks Monday's "prior day" and Friday's "next day"
    # lookups below (Monday would pair with a null-close Sunday instead
    # of the true prior Friday, and vice versa) -- the same class of
    # issue already documented elsewhere in this project (the Sunday
    # overnight-gap edge case fixed in fade-the-gap). Fixed here by
    # walking only the FILTERED list of days that actually have a valid
    # reference close, so consecutive entries are true consecutive
    # trading days -- the same "filter to valid days first, then walk
    # consecutive pairs" convention already used elsewhere in this
    # project (e.g. study_es_gap_incremental_info.build_joint_dataset).
    valid_days = [d for d in all_days if ref_closes.get(d) is not None]

    rows = []
    for i, day in enumerate(valid_days):
        row = {"date": day}

        # --- Candidate features (all reused, unmodified sources) ---
        row["day_of_week"] = day.weekday()  # 0=Monday .. 4=Friday
        row["turn_of_month"] = bool(turn_flags.get(day, False))
        row["is_expiration_week"] = bool(is_exp_week(day))
        row["event_type"] = combine_event_type(day)
        row["vol_regime"] = regime_by_day.get(day)  # 'high' / 'mid' / 'low' / None (insufficient history)
        row["momentum_sign"] = mom_by_day.get(day)  # +1 / -1 / None (insufficient history)

        # Overnight gap -- needs the prior VALID day's own intraday data
        if i > 0:
            prior_day = valid_days[i - 1]
            gap_result = compute_day_gap_and_returns(
                day_groups[prior_day], day_groups[day], day, prior_day
            )
            row["overnight_gap_pts"] = gap_result["gap"] if gap_result else None
        else:
            row["overnight_gap_pts"] = None

        # CFTC Leveraged Money weekly signal -- only non-missing on an
        # actual report-availability date (see resolve_availability_dates);
        # all other days get an explicit availability flag rather than an
        # imputed value, per the scoping document's Gap 2 fix.
        cftc_raw = cot_signal_by_avail_date.get(day)
        row["cftc_signal_available"] = cftc_raw is not None
        row["cftc_signal"] = float(cftc_raw) if cftc_raw is not None else 0.0

        # --- Candidate target variables (descriptive only -- not a decision) ---
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
    print("MULTI-FACTOR FEATURE TABLE -- pure data assembly, no test run")
    print("=" * 78)
    print(f"\nRows (classifiable Discovery trading days): {len(out_df)}")
    print(f"Date range: {out_df.index.min()} .. {out_df.index.max()}")
    print(f"\nColumns: {list(out_df.columns)}")
    print("\nMissingness by column (rows with no value):")
    print(out_df.isna().sum().to_string())
    print(f"\nCFTC signal available on {int(out_df['cftc_signal_available'].sum())} of {len(out_df)} rows "
          f"({out_df['cftc_signal_available'].mean():.1%}) -- expected, this feature's source data only "
          f"covers 2015-2018.")
    print(f"\nEvent-type breakdown:\n{out_df['event_type'].value_counts().to_string()}")
    print(f"\nSaved to {OUT_CSV}.")
    print("\nThis file is raw material only. No model has been fit, no target")
    print("variable has been chosen, and nothing here constitutes a result.")


if __name__ == "__main__":
    main()
