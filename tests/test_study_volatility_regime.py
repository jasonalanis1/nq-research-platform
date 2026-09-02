"""
test_study_volatility_regime.py
==================================
Automated tests for the Volatility-Regime Conditioning characterization
study (research/studies/volatility-regime-post-open-behavior.md).

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

import study_volatility_regime as vr


def test_compute_daily_log_returns_basic_math():
    """Three consecutive valid ref closes -> two log returns, hand-checked."""
    ref_closes = {
        date(2024, 1, 1): 100.0,
        date(2024, 1, 2): 110.0,
        date(2024, 1, 3): 99.0,
    }
    returns = vr.compute_daily_log_returns(ref_closes)
    assert set(returns.keys()) == {date(2024, 1, 2), date(2024, 1, 3)}
    assert returns[date(2024, 1, 2)] == np.log(110.0 / 100.0)
    assert returns[date(2024, 1, 3)] == np.log(99.0 / 110.0)


def test_compute_daily_log_returns_skips_missing_ref_close():
    """A day with ref_close=None should not break the chain -- the next
    valid day should compare against the last VALID day before it, not
    the missing one, and the missing day itself produces no entry."""
    ref_closes = {
        date(2024, 1, 1): 100.0,
        date(2024, 1, 2): None,   # missing
        date(2024, 1, 3): 105.0,
    }
    returns = vr.compute_daily_log_returns(ref_closes)
    assert date(2024, 1, 2) not in returns
    assert returns[date(2024, 1, 3)] == np.log(105.0 / 100.0)


def test_compute_trailing_volatility_requires_full_lookback():
    """Fewer than VOL_LOOKBACK_DAYS (20) prior returns -> day is excluded
    entirely (not given a vol figure at all)."""
    base = date(2024, 1, 1)
    all_days = [base + timedelta(days=i) for i in range(25)]
    # Only 15 prior returns available for the 16th day onward.
    returns = {all_days[i]: 0.01 for i in range(15)}
    vol = vr.compute_trailing_volatility(returns, all_days)
    assert vol == {}  # no day has 20 prior returns yet


def test_compute_trailing_volatility_uses_exactly_the_last_20():
    """Once 20+ prior returns exist, vol[day_t] must be the stdev of
    exactly the 20 MOST RECENT ones, not all available history."""
    base = date(2024, 1, 1)
    all_days = [base + timedelta(days=i) for i in range(30)]
    # returns for days[0..24]: first 5 are huge (should be excluded from
    # the 20-day window once we're far enough along), rest are small.
    returns = {}
    for i in range(25):
        returns[all_days[i]] = 10.0 if i < 5 else 0.001
    day_t = all_days[26]  # has 25 prior returns available -- only the last 20 should be used
    vol = vr.compute_trailing_volatility(returns, all_days)
    expected = np.std([0.001] * 20, ddof=1)  # the 5 huge ones are outside the trailing-20 window
    assert vol[day_t] == pytest.approx(expected)


def test_classify_regimes_first_day_is_trivially_high():
    """No minimum-history floor (per the approved spec change): the
    first classifiable day is ranked against a pool of exactly itself,
    landing in the high tercile by construction."""
    vol_by_day = {date(2024, 1, 1): 0.5}
    regimes = vr.classify_regimes(vol_by_day)
    assert regimes[date(2024, 1, 1)] == "high"


def test_classify_regimes_expanding_causal_not_whole_sample():
    """A day's regime must depend only on days up to and including it --
    adding a later, more extreme day must NOT retroactively change an
    earlier day's classification."""
    vol_by_day = {
        date(2024, 1, 1): 1.0,
        date(2024, 1, 2): 2.0,
        date(2024, 1, 3): 3.0,
    }
    regimes_3days = vr.classify_regimes(vol_by_day)

    # Classify just the first two days on their own.
    vol_by_day_2 = {date(2024, 1, 1): 1.0, date(2024, 1, 2): 2.0}
    regimes_2days = vr.classify_regimes(vol_by_day_2)

    # Day 1 and day 2's labels must be identical whether or not day 3
    # (a later, more extreme value) is ever added.
    assert regimes_3days[date(2024, 1, 1)] == regimes_2days[date(2024, 1, 1)]
    assert regimes_3days[date(2024, 1, 2)] == regimes_2days[date(2024, 1, 2)]


def test_classify_regimes_new_all_time_low_is_low():
    """Three high values establish the pool, then a day far below
    everything seen so far must land in the low tercile -- hand-checked:
    pool after inserting day4's value 1 is [10,10,10,1] (sorted [1,10,10,10]),
    count(<=1)=1, rank=1/4=0.25 <= 1/3."""
    vol_by_day = {
        date(2024, 1, 1): 10.0,
        date(2024, 1, 2): 10.0,
        date(2024, 1, 3): 10.0,
        date(2024, 1, 4): 1.0,
    }
    regimes = vr.classify_regimes(vol_by_day)
    assert regimes[date(2024, 1, 4)] == "low"


def test_classify_regimes_middling_value_against_diverse_pool_is_mid():
    """Nine distinct values 1..9 establish a diverse pool, then a repeat
    of the middle value (5) must land in mid -- hand-checked: pool after
    inserting the second 5 is [1,2,3,4,5,5,6,7,8,9] (10 elements),
    count(<=5)=6, rank=6/10=0.6, which is between 1/3 and 2/3."""
    vol_by_day = {date(2024, 1, i + 1): float(i + 1) for i in range(9)}  # 1..9
    vol_by_day[date(2024, 1, 10)] = 5.0  # a second "5", after the diverse pool is established
    regimes = vr.classify_regimes(vol_by_day)
    assert regimes[date(2024, 1, 10)] == "mid"


def make_bars(day, tz, bars):
    rows = []
    index = []
    for hour, minute, o, h, l, c, v in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": v})
    return pd.DataFrame(rows, index=index)


def test_compute_forward_return_basic():
    """Open at 8:30 (Close=100), a later bar at 8:59 (Close=105) is the
    last bar strictly before the 30-minute horizon (9:00) -- return
    should be 105 - 100 = 5.0."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    bars = [(8, 30, 100.0, 100.0, 100.0, 100.0, 10.0)]
    bars += [(8, 59, 105.0, 105.0, 105.0, 105.0, 10.0)]
    day_df = make_bars(day, tz, bars)

    ret = vr.compute_forward_return(day_df, day, horizon_minutes=30)
    assert ret == 5.0


def test_compute_forward_return_none_when_horizon_not_reached():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    bars = [(8, 30, 100.0, 100.0, 100.0, 100.0, 10.0)]  # data ends right at the open, nowhere near 30min later
    day_df = make_bars(day, tz, bars)

    ret = vr.compute_forward_return(day_df, day, horizon_minutes=30)
    assert ret is None


def test_scan_all_days_integration_produces_expected_columns():
    """Small multi-day synthetic dataset -- just checks the pipeline
    wires together and produces the expected shape, not exact values
    (those are covered by the unit tests above)."""
    tz = "America/New_York"
    frames = []
    base = date(2024, 1, 1)
    for i in range(25):  # enough days to get at least one classifiable day (need 20 prior returns)
        day = base + timedelta(days=i)
        bars = [(16, 0, 100.0 + i, 100.0 + i, 100.0 + i, 100.0 + i, 10.0)]  # 4pm ref close
        bars += [(8, 30, 100.0 + i, 100.0 + i, 100.0 + i, 100.0 + i, 10.0)]
        bars += [(9, m, 100.0 + i, 100.0 + i, 100.0 + i, 100.0 + i, 10.0) for m in range(60)]
        bars += [(h, m, 100.0 + i, 100.0 + i, 100.0 + i, 100.0 + i, 10.0)
                 for h in range(10, 12) for m in range(60)]
        frames.append(make_bars(day, tz, bars))
    df = pd.concat(frames)

    result = vr.scan_all_days(df)
    assert "regime" in result.columns
    assert "return_30m" in result.columns
    assert set(result["regime"].unique()) <= {"high", "mid", "low"}
