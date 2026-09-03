"""
Tests for study_post_release_continuation.py -- the frozen post-release
directional continuation study
(research/studies/post-release-directional-continuation.md).
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from study_economic_calendar import CPI_SET, NFP_SET  # noqa: E402
from study_fomc_volatility import FOMC_CPI_OVERLAP_DATES, FOMC_PRIMARY_DATES  # noqa: E402
from study_post_release_continuation import (  # noqa: E402
    compute_directional_continuation,
    normal_day_baseline,
    one_sample_test,
    robustness_drop_largest,
    robustness_split_half,
    scan_all_days,
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
# Disjointness (re-asserted at import time in the module itself; these
# tests just confirm the underlying sets still have the expected shape)
# ---------------------------------------------------------------------------

def test_fomc_primary_disjoint_from_cpi_and_nfp():
    assert CPI_SET.isdisjoint(FOMC_PRIMARY_DATES)
    assert NFP_SET.isdisjoint(FOMC_PRIMARY_DATES)
    assert CPI_SET.isdisjoint(NFP_SET)


def test_fomc_cpi_overlap_dates_are_in_cpi_set():
    # the 6 overlap days must still be ordinary CPI days for the 8:30 pass
    for d in FOMC_CPI_OVERLAP_DATES:
        assert d in CPI_SET


# ---------------------------------------------------------------------------
# scan_all_days -- correct anchors, correct row construction
# ---------------------------------------------------------------------------

def test_scan_all_days_cpi_day_gets_one_0830_row():
    # A CPI day is NOT a "true normal" day (it's 'cpi' in the CPI/NFP
    # pass), so it must NOT contribute a 1400-anchor baseline row --
    # exactly one row total, at the 0830 anchor.
    cpi_day = next(iter(CPI_SET - FOMC_CPI_OVERLAP_DATES))
    df = make_bars(cpi_day, [
        (8, 30, 100.0, 100.0, 100.0, 100.0),
        (8, 59, 105.0, 105.0, 105.0, 105.0),
        (11, 29, 110.0, 110.0, 110.0, 110.0),
    ])
    result = scan_all_days(df)
    assert len(result) == 1
    row = result.iloc[0]
    assert row["anchor"] == "0830"
    assert row["release_type"] == "cpi"
    assert row["initial_return"] == pytest.approx(5.0)
    assert row["total_return"] == pytest.approx(10.0)


def test_scan_all_days_fomc_overlap_day_gets_only_0830_row_classified_cpi():
    overlap_day = next(iter(FOMC_CPI_OVERLAP_DATES))
    df = make_bars(overlap_day, [
        (8, 30, 100.0, 100.0, 100.0, 100.0),
        (8, 59, 104.0, 104.0, 104.0, 104.0),
        (11, 29, 108.0, 108.0, 108.0, 108.0),
        (14, 0, 200.0, 200.0, 200.0, 200.0),
        (14, 29, 210.0, 210.0, 210.0, 210.0),
        (16, 59, 220.0, 220.0, 220.0, 220.0),
    ])
    result = scan_all_days(df)
    # exactly one row: the 0830 CPI row. No 1400 row, since this day is
    # 'fomc_cpi_overlap_excluded' in the FOMC pass, not 'fomc' or 'normal'.
    assert len(result) == 1
    row = result.iloc[0]
    assert row["anchor"] == "0830"
    assert row["release_type"] == "cpi"


def test_scan_all_days_fomc_day_gets_one_1400_row():
    # An FOMC day is not a "true normal" day (it's 'fomc' in the FOMC
    # pass), so it must NOT contribute an 0830-anchor baseline row --
    # exactly one row total, at the 1400 anchor.
    fomc_day = next(iter(FOMC_PRIMARY_DATES))
    df = make_bars(fomc_day, [
        (14, 0, 100.0, 100.0, 100.0, 100.0),
        (14, 29, 106.0, 106.0, 106.0, 106.0),
        (16, 59, 112.0, 112.0, 112.0, 112.0),
    ])
    result = scan_all_days(df)
    assert len(result) == 1
    row = result.iloc[0]
    assert row["anchor"] == "1400"
    assert row["release_type"] == "fomc"
    assert row["initial_return"] == pytest.approx(6.0)
    assert row["total_return"] == pytest.approx(12.0)


def test_scan_all_days_normal_day_gets_both_anchor_rows():
    normal_day = date(2015, 1, 15)
    assert normal_day not in CPI_SET and normal_day not in NFP_SET and normal_day not in FOMC_PRIMARY_DATES
    df = make_bars(normal_day, [
        (8, 30, 100.0, 100.0, 100.0, 100.0),
        (8, 59, 101.0, 101.0, 101.0, 101.0),
        (11, 29, 102.0, 102.0, 102.0, 102.0),
        (14, 0, 200.0, 200.0, 200.0, 200.0),
        (14, 29, 199.0, 199.0, 199.0, 199.0),
        (16, 59, 198.0, 198.0, 198.0, 198.0),
    ])
    result = scan_all_days(df)
    assert len(result) == 2
    anchors = set(result["anchor"])
    assert anchors == {"0830", "1400"}
    assert all(result["release_type"] == "normal")


# ---------------------------------------------------------------------------
# compute_directional_continuation
# ---------------------------------------------------------------------------

def _rows(*records):
    return pd.DataFrame(records)


def test_continuation_sign_math_positive_move_continues():
    df = _rows(
        {"date": date(2015, 1, 1), "anchor": "0830", "release_type": "cpi",
         "initial_return": 5.0, "total_return": 10.0},  # continuation +5, same sign -> +5
    )
    sub, counts = compute_directional_continuation(df)
    assert counts == {"n_missing_data": 0, "n_zero_initial_excluded": 0}
    assert sub.iloc[0]["continuation_return"] == pytest.approx(5.0)
    assert sub.iloc[0]["directional_continuation"] == pytest.approx(5.0)


def test_continuation_sign_math_negative_move_reverses():
    df = _rows(
        {"date": date(2015, 1, 1), "anchor": "0830", "release_type": "cpi",
         "initial_return": -5.0, "total_return": -10.0},  # continuation -5, sign(-5)=-1 -> +5 (kept going down = "continuation" positive)
    )
    sub, _ = compute_directional_continuation(df)
    assert sub.iloc[0]["continuation_return"] == pytest.approx(-5.0)
    assert sub.iloc[0]["directional_continuation"] == pytest.approx(5.0)


def test_continuation_sign_math_reversal_gives_negative_directional_continuation():
    df = _rows(
        {"date": date(2015, 1, 1), "anchor": "0830", "release_type": "cpi",
         "initial_return": 5.0, "total_return": 2.0},  # continuation_return = -3, sign(+5)=+1 -> -3
    )
    sub, _ = compute_directional_continuation(df)
    assert sub.iloc[0]["continuation_return"] == pytest.approx(-3.0)
    assert sub.iloc[0]["directional_continuation"] == pytest.approx(-3.0)


def test_continuation_excludes_missing_data():
    df = _rows(
        {"date": date(2015, 1, 1), "anchor": "0830", "release_type": "cpi",
         "initial_return": None, "total_return": 10.0},
        {"date": date(2015, 1, 2), "anchor": "0830", "release_type": "cpi",
         "initial_return": 5.0, "total_return": 10.0},
    )
    sub, counts = compute_directional_continuation(df)
    assert len(sub) == 1
    assert counts["n_missing_data"] == 1


def test_continuation_excludes_zero_initial_return():
    df = _rows(
        {"date": date(2015, 1, 1), "anchor": "0830", "release_type": "cpi",
         "initial_return": 0.0, "total_return": 10.0},
        {"date": date(2015, 1, 2), "anchor": "0830", "release_type": "cpi",
         "initial_return": 5.0, "total_return": 10.0},
    )
    sub, counts = compute_directional_continuation(df)
    assert len(sub) == 1
    assert counts["n_zero_initial_excluded"] == 1


# ---------------------------------------------------------------------------
# one_sample_test
# ---------------------------------------------------------------------------

def test_one_sample_test_clearly_positive():
    values = [5.0] * 20  # constant, so CI collapses tightly around 5.0
    result = one_sample_test(values)
    assert result["n"] == 20
    assert result["mean"] == pytest.approx(5.0)
    assert result["significant"] is True
    assert result["ci_90"][0] > 0


def test_one_sample_test_too_few_points():
    result = one_sample_test([1.0])
    assert result["n"] == 1
    assert result["significant"] is False


# ---------------------------------------------------------------------------
# Robustness checks
# ---------------------------------------------------------------------------

def _synthetic_continuation_df():
    rows = []
    for i in range(10):
        rows.append({
            "date": date(2015, 1, 1 + i), "anchor": "0830", "release_type": "cpi",
            "initial_return": 5.0, "total_return": 5.0 + (2.0 + i * 0.1),
        })
    sub, _ = compute_directional_continuation(pd.DataFrame(rows))
    return sub


def test_robustness_drop_largest_removes_max_abs_row():
    sub = _synthetic_continuation_df()
    mask = sub["release_type"].isin(["cpi", "nfp", "fomc"])
    result = robustness_drop_largest(sub, mask)
    assert result["dropped_date"] == str(date(2015, 1, 10))  # largest i=9 -> largest directional_continuation
    assert result["n"] == 9


def test_robustness_split_half_returns_both_halves():
    sub = _synthetic_continuation_df()
    mask = sub["release_type"].isin(["cpi", "nfp", "fomc"])
    result = robustness_split_half(sub, mask)
    assert "first_half" in result and "second_half" in result
    assert result["first_half"]["n"] == 5
    assert result["second_half"]["n"] == 5


# ---------------------------------------------------------------------------
# normal_day_baseline
# ---------------------------------------------------------------------------

def test_normal_day_baseline_structure():
    rows = []
    for i in range(10):
        rows.append({"date": date(2015, 1, 1 + i), "anchor": "0830", "release_type": "cpi",
                      "initial_return": 5.0, "total_return": 10.0})
        rows.append({"date": date(2015, 1, 1 + i), "anchor": "0830", "release_type": "normal",
                      "initial_return": 5.0, "total_return": 6.0})
        rows.append({"date": date(2015, 2, 1 + i), "anchor": "1400", "release_type": "fomc",
                      "initial_return": 5.0, "total_return": 10.0})
        rows.append({"date": date(2015, 2, 1 + i), "anchor": "1400", "release_type": "normal",
                      "initial_return": 5.0, "total_return": 6.0})
    sub, _ = compute_directional_continuation(pd.DataFrame(rows))
    result = normal_day_baseline(sub)
    assert "cpi_nfp_vs_normal_0830" in result
    assert "fomc_vs_normal_1400" in result
    assert result["cpi_nfp_vs_normal_0830"]["normal"]["n"] == 10


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
