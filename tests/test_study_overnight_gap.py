"""
test_study_overnight_gap.py
==============================
Automated tests for the Overnight Gap Behavior characterization study
(research/studies/overnight-gap-behavior.md).

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date
import numpy as np
import pandas as pd
import study_overnight_gap as gap


def make_bars(day, tz, bars):
    rows = []
    index = []
    for hour, minute, o, h, l, c in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 100})
    return pd.DataFrame(rows, index=index)


def flat_bars(day, tz, hour_start, minute_start, n_minutes, price):
    bars = []
    for m in range(n_minutes):
        hour, minute = divmod(minute_start + m, 60)
        bars.append((hour_start + hour, minute, price, price, price, price))
    return make_bars(day, tz, bars)


def test_get_reference_close_uses_last_bar_at_or_before_4pm():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = pd.concat([
        flat_bars(day, tz, 15, 55, 5, price=100.0),  # 15:55-15:59
        flat_bars(day, tz, 16, 0, 1, price=102.0),   # exactly 16:00 -- should be used
        flat_bars(day, tz, 16, 1, 5, price=999.0),   # after 16:00 -- must NOT be used
    ])

    ref = gap.get_reference_close(df, day, tz)

    assert ref == 102.0


def test_compute_day_gap_up_and_fill():
    day1 = date(2024, 1, 2)
    day2 = date(2024, 1, 3)
    tz = "America/New_York"
    day1_df = flat_bars(day1, tz, 15, 55, 10, price=100.0)  # prior_close = 100.0

    # Gap up: opens at 105, dips down to touch 100.0 (fills) within the watch window, then flat after.
    day2_df = pd.concat([
        make_bars(day2, tz, [(8, 30, 105.0, 105.0, 105.0, 105.0)]),
        make_bars(day2, tz, [(8, 31, 105.0, 105.0, 100.0, 101.0)]),  # low touches prior_close -- filled
        flat_bars(day2, tz, 8, 32, 400, price=103.0),  # enough bars to cover all horizons
    ])

    row = gap.compute_day_gap_and_returns(day1_df, day2_df, day2, day1)

    assert row is not None
    assert row["prior_close"] == 100.0
    assert row["today_open"] == 105.0
    assert row["gap"] == 5.0
    assert row["gap_filled_by_noon"] is True


def test_compute_day_gap_down_not_filled():
    day1 = date(2024, 1, 2)
    day2 = date(2024, 1, 3)
    tz = "America/New_York"
    day1_df = flat_bars(day1, tz, 15, 55, 10, price=100.0)

    # Gap down: opens at 95, stays well below 100 the whole watch window -- never fills.
    day2_df = pd.concat([
        make_bars(day2, tz, [(8, 30, 95.0, 95.0, 95.0, 95.0)]),
        flat_bars(day2, tz, 8, 31, 400, price=96.0),
    ])

    row = gap.compute_day_gap_and_returns(day1_df, day2_df, day2, day1)

    assert row["gap"] == -5.0
    assert row["gap_filled_by_noon"] is False


def test_missing_prior_close_returns_none():
    day1 = date(2024, 1, 2)
    day2 = date(2024, 1, 3)
    tz = "America/New_York"
    day1_df = flat_bars(day1, tz, 20, 0, 10, price=100.0)  # only bars AFTER 16:00 -- no reference close available
    day2_df = flat_bars(day2, tz, 8, 30, 400, price=105.0)

    row = gap.compute_day_gap_and_returns(day1_df, day2_df, day2, day1)

    assert row is None


def test_zero_gap_has_no_fill_verdict():
    day1 = date(2024, 1, 2)
    day2 = date(2024, 1, 3)
    tz = "America/New_York"
    day1_df = flat_bars(day1, tz, 15, 55, 10, price=100.0)
    day2_df = flat_bars(day2, tz, 8, 30, 400, price=100.0)  # opens exactly at prior_close

    row = gap.compute_day_gap_and_returns(day1_df, day2_df, day2, day1)

    assert row["gap"] == 0.0
    assert row["gap_filled_by_noon"] is None


def test_analyze_horizon_detects_perfect_correlation():
    rows = []
    for i in range(30):
        g = (i - 15) * 1.0
        rows.append({"date": date(2024, 1, 1), "gap": g, "fwd_return_30m": g * 3.0})
    gaps_df = pd.DataFrame(rows)

    result = gap.analyze_horizon(gaps_df, 30)

    assert result["n"] == 30
    assert result["correlation"] > 0.99
    assert result["significant"] is True


def test_analyze_gap_fill_rates():
    rows = [
        {"gap": 5.0, "gap_filled_by_noon": True},
        {"gap": 5.0, "gap_filled_by_noon": True},
        {"gap": 5.0, "gap_filled_by_noon": False},
        {"gap": -3.0, "gap_filled_by_noon": False},
        {"gap": -3.0, "gap_filled_by_noon": False},
    ]
    gaps_df = pd.DataFrame(rows)

    result = gap.analyze_gap_fill(gaps_df)

    assert result["gap_up"]["n"] == 3
    assert result["gap_up"]["filled"] == 2
    assert abs(result["gap_up"]["fill_rate"] - (2 / 3)) < 1e-9
    assert result["gap_down"]["n"] == 2
    assert result["gap_down"]["filled"] == 0
