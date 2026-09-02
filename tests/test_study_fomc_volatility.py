"""
Tests for study_fomc_volatility.py -- the frozen FOMC scheduled-release
volatility study (research/studies/fomc-release-volatility.md).
"""
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from study_fomc_volatility import (  # noqa: E402
    FOMC_DATES,
    FOMC_SET,
    FOMC_CPI_OVERLAP_DATES,
    FOMC_NFP_OVERLAP_DATES,
    FOMC_PRIMARY_DATES,
    classify_day,
    compute_forward_return_at,
    scan_all_days,
    analyze_horizon,
    robustness_drop_largest_abs_return_day,
    robustness_split_half,
    PRIMARY_HORIZON_MINUTES,
    FOMC_ANCHOR_HOUR,
    FOMC_ANCHOR_MINUTE,
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

def test_fomc_dates_count():
    assert len(FOMC_DATES) == 53


def test_fomc_dates_sorted_and_unique():
    assert FOMC_DATES == sorted(set(FOMC_DATES))


def test_fomc_dates_within_discovery_range():
    for d in FOMC_DATES:
        assert date(2015, 1, 1) <= d <= date(2021, 10, 3)


def test_fomc_cpi_overlap_count():
    assert len(FOMC_CPI_OVERLAP_DATES) == 6


def test_fomc_nfp_overlap_count():
    assert len(FOMC_NFP_OVERLAP_DATES) == 0


def test_fomc_primary_dates_excludes_cpi_overlap():
    assert len(FOMC_PRIMARY_DATES) == 47
    assert FOMC_PRIMARY_DATES == FOMC_SET - FOMC_CPI_OVERLAP_DATES


# ---------------------------------------------------------------------------
# classify_day
# ---------------------------------------------------------------------------

def test_classify_day_fomc():
    non_overlap_fomc = next(d for d in FOMC_DATES if d not in FOMC_CPI_OVERLAP_DATES)
    assert classify_day(non_overlap_fomc) == "fomc"


def test_classify_day_fomc_cpi_overlap_excluded():
    overlap_date = next(iter(FOMC_CPI_OVERLAP_DATES))
    assert classify_day(overlap_date) == "fomc_cpi_overlap_excluded"


def test_classify_day_normal():
    assert classify_day(date(2015, 1, 15)) == "normal"


# ---------------------------------------------------------------------------
# compute_forward_return_at
# ---------------------------------------------------------------------------

def test_compute_forward_return_at_basic():
    day = date(2015, 6, 17)  # an FOMC date
    # window is [anchor, anchor+horizon) -- the probe bar must land
    # strictly before the horizon boundary, same convention as
    # compute_forward_return().
    df = make_bars(day, [
        (14, 0, 100.0, 100.0, 100.0, 100.0),
        (14, 29, 108.0, 108.0, 108.0, 108.0),
    ])
    ret = compute_forward_return_at(df, day, 14, 0, 30)
    assert ret == pytest.approx(8.0)


def test_compute_forward_return_at_none_when_no_anchor_bar():
    day = date(2015, 6, 17)
    df = make_bars(day, [(9, 0, 100.0, 100.0, 100.0, 100.0)])  # before 2:00 PM
    ret = compute_forward_return_at(df, day, 14, 0, 30)
    assert ret is None


def test_compute_forward_return_at_none_when_horizon_unavailable():
    day = date(2015, 6, 17)
    df = make_bars(day, [(14, 0, 100.0, 100.0, 100.0, 100.0)])
    ret = compute_forward_return_at(df, day, 14, 0, 30)
    assert ret is None


def test_compute_forward_return_at_matches_fomc_anchor_constants():
    # sanity check the module's own constants are wired the way main()
    # calls compute_forward_return_at
    assert FOMC_ANCHOR_HOUR == 14
    assert FOMC_ANCHOR_MINUTE == 0


# ---------------------------------------------------------------------------
# scan_all_days
# ---------------------------------------------------------------------------

def test_scan_all_days_classifies_and_computes_abs_return():
    fomc_day = next(d for d in FOMC_DATES if d not in FOMC_CPI_OVERLAP_DATES)
    normal_day = date(2015, 1, 15)
    assert normal_day not in FOMC_SET

    df = pd.concat([
        make_bars(fomc_day, [
            (14, 0, 100.0, 100.0, 100.0, 100.0),
            (14, 29, 93.0, 93.0, 93.0, 93.0),   # -7 pt move by 30min
        ]),
        make_bars(normal_day, [
            (14, 0, 100.0, 100.0, 100.0, 100.0),
            (14, 29, 101.0, 101.0, 101.0, 101.0),  # +1 pt move by 30min
        ]),
    ])

    result = scan_all_days(df).set_index("date")
    assert result.loc[fomc_day, "release_type"] == "fomc"
    assert result.loc[fomc_day, "abs_return_30m"] == pytest.approx(7.0)
    assert result.loc[normal_day, "release_type"] == "normal"
    assert result.loc[normal_day, "abs_return_30m"] == pytest.approx(1.0)


def test_scan_all_days_marks_cpi_overlap_day_excluded():
    overlap_date = next(iter(FOMC_CPI_OVERLAP_DATES))
    df = make_bars(overlap_date, [
        (14, 0, 100.0, 100.0, 100.0, 100.0),
        (14, 29, 105.0, 105.0, 105.0, 105.0),
    ])
    result = scan_all_days(df).set_index("date")
    assert result.loc[overlap_date, "release_type"] == "fomc_cpi_overlap_excluded"


# ---------------------------------------------------------------------------
# analyze_horizon -- excluded rows must not appear in either bucket
# ---------------------------------------------------------------------------

def _synthetic_results_df():
    rows = []
    for i in range(8):
        rows.append({"date": date(2015, 1, 1 + i), "release_type": "fomc", "abs_return_30m": 6.0 + i * 0.1})
    for i in range(8):
        rows.append({"date": date(2015, 2, 1 + i), "release_type": "normal", "abs_return_30m": 1.0 + i * 0.1})
    return pd.DataFrame(rows)


def test_analyze_horizon_basic_stats():
    df = _synthetic_results_df()
    result = analyze_horizon(df, 30, {"fomc"})
    assert result["n_release"] == 8
    assert result["n_normal"] == 8
    assert result["mean_abs_return_release"] > result["mean_abs_return_normal"]


def test_analyze_horizon_excludes_cpi_overlap_rows_from_both_buckets():
    df = _synthetic_results_df()
    excluded = pd.DataFrame([{"date": date(2015, 3, 1), "release_type": "fomc_cpi_overlap_excluded", "abs_return_30m": 999.0}])
    df = pd.concat([df, excluded], ignore_index=True)
    result = analyze_horizon(df, 30, {"fomc"})
    assert result["n_release"] == 8  # the excluded row must not be counted as fomc
    assert result["n_normal"] == 8   # nor as normal


# ---------------------------------------------------------------------------
# Robustness checks
# ---------------------------------------------------------------------------

def test_robustness_drop_largest_removes_the_max_abs_return_row():
    df = _synthetic_results_df()
    result = robustness_drop_largest_abs_return_day(df)
    assert result["dropped_date"] == str(date(2015, 1, 8))
    assert result["n_release"] == 7


def test_robustness_split_half_returns_both_halves():
    df = _synthetic_results_df()
    result = robustness_split_half(df)
    assert "first_half" in result and "second_half" in result


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
