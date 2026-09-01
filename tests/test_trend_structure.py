"""
test_trend_structure.py
==========================
Automated tests for the trend-structure-aware liquidity filter
(research/setups/trend-structure-liquidity-filter.md). Covers daily
resampling, swing-point detection (including that boundary days can
never be flagged), the no-lookahead confirmation lag (the single most
important property of this module -- see trend_structure.py's
docstring), trend classification, and the final protected/not_protected
signal classification.
"""
from datetime import date

import pandas as pd
import pytest

import trend_structure as ts


def make_minute_bars(day, tz, bars):
    """bars: list of (hour, minute, high, low) tuples."""
    rows, index = [], []
    for hour, minute, h, l in bars:
        index.append(pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute))
        rows.append({"Open": (h + l) / 2, "High": h, "Low": l, "Close": (h + l) / 2, "Volume": 100})
    return pd.DataFrame(rows, index=index)


def make_daily_swings(day_specs, k=ts.SWING_FRACTAL_K):
    """Builds a swings-shaped DataFrame directly (bypassing find_swing_points)
    so trend_context_as_of/classify_signal can be tested in isolation from
    swing DETECTION. day_specs: list of (day, high, low, swing_high, swing_low)."""
    rows, index = [], []
    for day, high, low, sh, sl in day_specs:
        index.append(pd.Timestamp(day))
        rows.append({"High": high, "Low": low, "swing_high": sh, "swing_low": sl})
    return pd.DataFrame(rows, index=index)


# --- to_daily_bars -----------------------------------------------------

def test_to_daily_bars_resamples_to_one_row_per_day():
    tz = "America/New_York"
    day1_bars = make_minute_bars(date(2024, 1, 1), tz, [(9, 0, 105, 100), (9, 1, 110, 103)])
    day2_bars = make_minute_bars(date(2024, 1, 2), tz, [(9, 0, 95, 90), (9, 1, 98, 92)])
    df = pd.concat([day1_bars, day2_bars])

    daily = ts.to_daily_bars(df)

    assert len(daily) == 2
    assert daily.iloc[0]["High"] == 110
    assert daily.iloc[0]["Low"] == 100
    assert daily.iloc[1]["High"] == 98
    assert daily.iloc[1]["Low"] == 90


# --- find_swing_points --------------------------------------------------

def test_find_swing_points_flags_a_real_swing_high():
    daily = pd.DataFrame(
        {"High": [10, 12, 20, 12, 10], "Low": [1, 1, 1, 1, 1]},
        index=pd.date_range("2024-01-01", periods=5),
    )
    result = ts.find_swing_points(daily, k=2)
    assert list(result["swing_high"]) == [False, False, True, False, False]
    assert not result["swing_low"].any()


def test_find_swing_points_flags_a_real_swing_low():
    daily = pd.DataFrame(
        {"High": [20, 20, 20, 20, 20], "Low": [10, 8, 2, 8, 10]},
        index=pd.date_range("2024-01-01", periods=5),
    )
    result = ts.find_swing_points(daily, k=2)
    assert list(result["swing_low"]) == [False, False, True, False, False]
    assert not result["swing_high"].any()


def test_find_swing_points_never_flags_boundary_days():
    # Position 0 is the highest value in the whole series, but it has no
    # "before" neighbors to compare against, so it can never be confirmed
    # as a swing high -- this must stay False, not True.
    daily = pd.DataFrame(
        {"High": [100, 1, 1, 1, 1], "Low": [1, 1, 1, 1, 1]},
        index=pd.date_range("2024-01-01", periods=5),
    )
    result = ts.find_swing_points(daily, k=2)
    assert not result["swing_high"].any()


# --- trend_context_as_of -------------------------------------------------

def test_no_trend_when_insufficient_swing_history():
    daily = pd.DataFrame(
        {"High": [10, 11, 12], "Low": [1, 2, 3], "swing_high": [False, False, False],
         "swing_low": [False, False, False]},
        index=pd.date_range("2024-01-01", periods=3),
    )
    ctx = ts.trend_context_as_of(daily, as_of_day=date(2024, 1, 3), k=2)
    assert ctx.trend == "NO_TREND"


def test_uptrend_detected_with_correct_protected_low():
    days = pd.date_range("2024-01-01", periods=12)
    specs = [
        (days[0], 100, 90, False, False),
        (days[1], 101, 90, False, True),    # swing low #1: Low=90
        (days[2], 102, 91, False, False),
        (days[3], 110, 92, True, False),    # swing high #1: High=110
        (days[4], 103, 93, False, False),
        (days[5], 104, 95, False, True),    # swing low #2: Low=95 (higher than 90)
        (days[6], 105, 96, False, False),
        (days[7], 120, 97, True, False),    # swing high #2: High=120 (higher than 110)
        (days[8], 106, 98, False, False),
        (days[9], 107, 99, False, False),
        (days[10], 108, 100, False, False),
        (days[11], 109, 101, False, False),
    ]
    swings = make_daily_swings(specs)

    # As of day 9 (index 9): day 7's swing high isn't confirmable yet
    # (needs days 8 and 9 to complete its 2-after window, and confirmation
    # requires that to have happened strictly BEFORE day 9) -- so only one
    # swing high is known, which isn't enough to call a trend.
    ctx_early = ts.trend_context_as_of(swings, as_of_day=days[9], k=2)
    assert ctx_early.trend == "NO_TREND", (
        "day 7's swing high must not be visible yet at day 9 -- if this fails, "
        "the no-lookahead guard is broken"
    )

    # As of day 10, day 7's swing high (position 7) IS confirmable
    # (7 + 2 <= 10 - 1), so now both highs and both lows are known.
    ctx_later = ts.trend_context_as_of(swings, as_of_day=days[10], k=2)
    assert ctx_later.trend == "UPTREND"
    assert ctx_later.protected_low == 95


def test_downtrend_detected_with_correct_protected_high():
    days = pd.date_range("2024-01-01", periods=11)
    specs = [
        (days[0], 120, 100, False, False),
        (days[1], 119, 99, True, False),    # swing high #1: High=119
        (days[2], 118, 98, False, False),
        (days[3], 117, 90, False, True),    # swing low #1: Low=90
        (days[4], 116, 91, False, False),
        (days[5], 110, 92, True, False),    # swing high #2: High=110 (lower than 119)
        (days[6], 109, 93, False, False),
        (days[7], 108, 80, False, True),    # swing low #2: Low=80 (lower than 90)
        (days[8], 107, 94, False, False),
        (days[9], 106, 95, False, False),
        (days[10], 105, 96, False, False),
    ]
    swings = make_daily_swings(specs)

    ctx = ts.trend_context_as_of(swings, as_of_day=days[10], k=2)
    assert ctx.trend == "DOWNTREND"
    assert ctx.protected_high == 110


# --- classify_signal ------------------------------------------------------

def test_classify_signal_protected_when_sweep_reaches_protected_low():
    days = pd.date_range("2024-01-01", periods=12)
    specs = [
        (days[0], 100, 90, False, False),
        (days[1], 101, 90, False, True),
        (days[2], 102, 91, False, False),
        (days[3], 110, 92, True, False),
        (days[4], 103, 93, False, False),
        (days[5], 104, 95, False, True),
        (days[6], 105, 96, False, False),
        (days[7], 120, 97, True, False),
        (days[8], 106, 98, False, False),
        (days[9], 107, 99, False, False),
        (days[10], 108, 100, False, False),
        (days[11], 109, 101, False, False),
    ]
    swings = make_daily_swings(specs)  # UPTREND as of day 10, protected_low=95

    # Swept level at or below the protected low (95) -- a genuine
    # structural-point sweep.
    result = ts.classify_signal(swings, days[10], direction="long", level_swept=95)
    assert result["classification"] == "protected"
    assert result["trend"] == "UPTREND"

    # Swept level shallower than the protected low -- an interior sweep.
    result = ts.classify_signal(swings, days[10], direction="long", level_swept=97)
    assert result["classification"] == "not_protected"


def test_classify_signal_not_protected_on_wrong_direction_for_trend():
    days = pd.date_range("2024-01-01", periods=12)
    specs = [
        (days[0], 100, 90, False, False),
        (days[1], 101, 90, False, True),
        (days[2], 102, 91, False, False),
        (days[3], 110, 92, True, False),
        (days[4], 103, 93, False, False),
        (days[5], 104, 95, False, True),
        (days[6], 105, 96, False, False),
        (days[7], 120, 97, True, False),
        (days[8], 106, 98, False, False),
        (days[9], 107, 99, False, False),
        (days[10], 108, 100, False, False),
        (days[11], 109, 101, False, False),
    ]
    swings = make_daily_swings(specs)  # UPTREND as of day 10

    # A short signal during an UPTREND day can never be "protected" --
    # protected shorts only make sense during a DOWNTREND.
    result = ts.classify_signal(swings, days[10], direction="short", level_swept=1000)
    assert result["classification"] == "not_protected"


def test_classify_signal_not_protected_when_no_trend():
    daily = pd.DataFrame(
        {"High": [10, 11, 12], "Low": [1, 2, 3], "swing_high": [False, False, False],
         "swing_low": [False, False, False]},
        index=pd.date_range("2024-01-01", periods=3),
    )
    result = ts.classify_signal(daily, date(2024, 1, 3), direction="long", level_swept=1)
    assert result["classification"] == "not_protected"
    assert result["trend"] == "NO_TREND"


def test_classify_signal_rejects_unknown_direction():
    daily = pd.DataFrame(
        {"High": [10], "Low": [1], "swing_high": [False], "swing_low": [False]},
        index=pd.date_range("2024-01-01", periods=1),
    )
    with pytest.raises(ValueError):
        ts.classify_signal(daily, date(2024, 1, 1), direction="sideways", level_swept=5)
