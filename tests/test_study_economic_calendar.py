"""
Tests for study_economic_calendar.py -- the frozen CPI/NFP scheduled-
release volatility study (research/studies/economic-release-volatility.md).
"""
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from study_economic_calendar import (  # noqa: E402
    CPI_DATES,
    NFP_DATES,
    CPI_SET,
    NFP_SET,
    classify_day,
    scan_all_days,
    analyze_horizon,
    robustness_drop_largest_abs_return_day,
    robustness_split_half,
    PRIMARY_HORIZON_MINUTES,
)


def make_bars(day, times_prices, tz="America/New_York"):
    """times_prices: list of (hour, minute, open, high, low, close)."""
    rows = []
    idx = []
    for h, m, o, hi, lo, c in times_prices:
        idx.append(pd.Timestamp(day.year, day.month, day.day, h, m, tz=tz))
        rows.append({"Open": o, "High": hi, "Low": lo, "Close": c})
    return pd.DataFrame(rows, index=pd.DatetimeIndex(idx))


# ---------------------------------------------------------------------------
# Frozen calendar-constant properties
# ---------------------------------------------------------------------------

def test_cpi_dates_count():
    # 81 original (Discovery, 2015-2021) + 27 extension (Validation,
    # 2021-2023), added 2026-09-02 when the first out-of-sample check
    # found the original list didn't cover the Validation window.
    assert len(CPI_DATES) == 108


def test_nfp_dates_count():
    assert len(NFP_DATES) == 108


def test_cpi_nfp_disjoint():
    assert CPI_SET.isdisjoint(NFP_SET)


def test_cpi_dates_within_discovery_plus_validation_range():
    for d in CPI_DATES:
        assert date(2015, 1, 1) <= d <= date(2024, 1, 3)


def test_nfp_dates_within_discovery_plus_validation_range():
    for d in NFP_DATES:
        assert date(2015, 1, 1) <= d <= date(2024, 1, 3)


def test_cpi_dates_cover_validation_window():
    # The whole point of the 2026-09-02 extension: at least one CPI date
    # must fall inside the Validation slice, or the out-of-sample check
    # silently finds nothing again.
    validation_cpi = [d for d in CPI_DATES if date(2021, 10, 4) <= d <= date(2024, 1, 3)]
    assert len(validation_cpi) == 27


def test_nfp_dates_cover_validation_window():
    validation_nfp = [d for d in NFP_DATES if date(2021, 10, 4) <= d <= date(2024, 1, 3)]
    assert len(validation_nfp) == 27


def test_nfp_validation_dates_all_fridays():
    for d in NFP_DATES:
        if date(2021, 10, 4) <= d <= date(2024, 1, 3):
            assert d.weekday() == 4, f"{d} is not a Friday"


def test_cpi_dates_sorted_and_unique():
    assert CPI_DATES == sorted(set(CPI_DATES))


def test_nfp_dates_sorted_and_unique():
    assert NFP_DATES == sorted(set(NFP_DATES))


# ---------------------------------------------------------------------------
# classify_day
# ---------------------------------------------------------------------------

def test_classify_day_cpi():
    assert classify_day(date(2015, 1, 16)) == "cpi"


def test_classify_day_nfp():
    assert classify_day(date(2015, 1, 9)) == "nfp"


def test_classify_day_normal():
    assert classify_day(date(2015, 1, 15)) == "normal"


# ---------------------------------------------------------------------------
# scan_all_days
# ---------------------------------------------------------------------------

def test_scan_all_days_classifies_and_computes_abs_return():
    cpi_day = CPI_DATES[0]
    normal_day = date(2015, 1, 15)
    assert normal_day not in CPI_SET and normal_day not in NFP_SET

    # compute_forward_return's window is [open, open+horizon) -- the last
    # bar strictly before the horizon boundary is what counts, so the
    # probe bar must land at 8:59, not exactly at 9:00.
    df = pd.concat([
        make_bars(cpi_day, [
            (8, 30, 100.0, 100.0, 100.0, 100.0),
            (8, 59, 95.0, 95.0, 95.0, 95.0),   # -5 pt move by 30min
        ]),
        make_bars(normal_day, [
            (8, 30, 100.0, 100.0, 100.0, 100.0),
            (8, 59, 101.0, 101.0, 101.0, 101.0),  # +1 pt move by 30min
        ]),
    ])

    result = scan_all_days(df)
    result = result.set_index("date")

    assert result.loc[cpi_day, "release_type"] == "cpi"
    assert result.loc[cpi_day, "abs_return_30m"] == pytest.approx(5.0)
    assert result.loc[normal_day, "release_type"] == "normal"
    assert result.loc[normal_day, "abs_return_30m"] == pytest.approx(1.0)


def test_scan_all_days_none_when_horizon_unavailable():
    day = date(2015, 1, 15)
    # Only one bar at the open -- no bar reaches the 30-minute horizon.
    df = make_bars(day, [(8, 30, 100.0, 100.0, 100.0, 100.0)])
    result = scan_all_days(df)
    assert result.iloc[0]["abs_return_30m"] is None


# ---------------------------------------------------------------------------
# analyze_horizon
# ---------------------------------------------------------------------------

def _synthetic_results_df():
    """8 release days with a larger |move|, 8 normal days with a
    smaller |move|, so the comparison has an obvious, hand-checkable
    direction and magnitude."""
    rows = []
    for i in range(8):
        rows.append({"date": date(2015, 1, 1 + i), "release_type": "cpi", "abs_return_30m": 6.0 + i * 0.1})
    for i in range(8):
        rows.append({"date": date(2015, 2, 1 + i), "release_type": "normal", "abs_return_30m": 1.0 + i * 0.1})
    return pd.DataFrame(rows)


def test_analyze_horizon_basic_stats():
    df = _synthetic_results_df()
    result = analyze_horizon(df, 30, {"cpi", "nfp"})
    assert result["n_release"] == 8
    assert result["n_normal"] == 8
    assert result["mean_abs_return_release"] > result["mean_abs_return_normal"]
    assert result["mean_diff_points"] > 0
    assert result["ci_90"][0] < result["ci_90"][1]


def test_analyze_horizon_release_types_filter_selects_only_matching_rows():
    df = _synthetic_results_df()
    # add an nfp row that should be excluded when release_types={"cpi"}
    extra = pd.DataFrame([{"date": date(2015, 3, 1), "release_type": "nfp", "abs_return_30m": 50.0}])
    df = pd.concat([df, extra], ignore_index=True)

    cpi_only = analyze_horizon(df, 30, {"cpi"})
    assert cpi_only["n_release"] == 8  # the nfp outlier row must not be counted

    pooled = analyze_horizon(df, 30, {"cpi", "nfp"})
    assert pooled["n_release"] == 9


def test_analyze_horizon_drops_rows_with_missing_horizon_value():
    df = _synthetic_results_df()
    df.loc[0, "abs_return_30m"] = None
    result = analyze_horizon(df, 30, {"cpi", "nfp"})
    assert result["n_release"] == 7


# ---------------------------------------------------------------------------
# Robustness checks
# ---------------------------------------------------------------------------

def test_robustness_drop_largest_removes_the_max_abs_return_row():
    df = _synthetic_results_df()
    result = robustness_drop_largest_abs_return_day(df)
    # The largest abs_return_30m row overall is the last cpi row (6.7).
    assert result["dropped_date"] == str(date(2015, 1, 8))
    assert result["n_release"] == 7  # one of the 8 release rows was the max and got dropped


def test_robustness_split_half_returns_both_halves():
    df = _synthetic_results_df()
    result = robustness_split_half(df)
    assert "first_half" in result and "second_half" in result
    assert result["first_half"]["n_release"] + result["first_half"]["n_normal"] == 8
    assert result["second_half"]["n_release"] + result["second_half"]["n_normal"] == 8


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
