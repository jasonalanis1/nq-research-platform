"""
test_study_open_return_persistence.py
========================================
Automated tests for the Open Return Persistence characterization study
(research/studies/open-return-persistence.md).

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date
import numpy as np
import pandas as pd
import study_open_return_persistence as st


def make_bars(day, tz, bars):
    rows = []
    index = []
    for hour, minute, o, h, l, c in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 100})
    return pd.DataFrame(rows, index=index)


def ib_bars_moving(day, tz, ib_open=100.0, ib_close=102.0):
    """30 minutes of bars (8:30-8:59) that move linearly from ib_open to
    ib_close -- the first bar's Open is ib_open, the last bar's Close is
    ib_close."""
    bars = []
    n = 30
    for i, minute in enumerate(range(30, 60)):
        frac_start = i / n
        frac_end = (i + 1) / n
        o = ib_open + frac_start * (ib_close - ib_open)
        c = ib_open + frac_end * (ib_close - ib_open)
        bars.append((8, minute, o, max(o, c), min(o, c), c))
    return make_bars(day, tz, bars)


def flat_bars(day, tz, hour_start, minute_start, n_minutes, price):
    bars = []
    for m in range(n_minutes):
        hour, minute = divmod(minute_start + m, 60)
        bars.append((hour_start + hour, minute, price, price, price, price))
    return make_bars(day, tz, bars)


def test_compute_day_returns_basic_values():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df_ib = ib_bars_moving(day, tz, ib_open=100.0, ib_close=102.0)
    # 9:00-12:00, flat at 105 (a fixed +3 move from ib_close for every horizon)
    df_after = flat_bars(day, tz, 9, 0, 180, price=105.0)
    day_df = pd.concat([df_ib, df_after])

    row = st.compute_day_returns(day_df, day)

    assert row is not None
    assert row["ib_open"] == 100.0
    assert row["ib_close"] == 102.0
    assert row["ib_return"] == 2.0
    for h in st.HORIZON_MINUTES:
        assert row[f"fwd_return_{h}m"] == 3.0  # 105 - 102


def test_missing_ib_data_returns_none():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    day_df = flat_bars(day, tz, 9, 0, 60, price=101.0)  # starts after the IB window

    row = st.compute_day_returns(day_df, day)

    assert row is None


def test_missing_horizon_data_is_none_but_day_still_included():
    """A day that ends early (e.g. a half session) should still produce
    a row -- just with None for horizons that ran out of data, not a
    dropped day."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df_ib = ib_bars_moving(day, tz, ib_open=100.0, ib_close=101.0)
    df_after = flat_bars(day, tz, 9, 0, 35, price=103.0)  # 35 min of post-IB data -- covers the 30m horizon, not 60m+
    day_df = pd.concat([df_ib, df_after])

    row = st.compute_day_returns(day_df, day)

    assert row is not None
    assert row["fwd_return_30m"] == 2.0  # 103 - 101, data available within 30 min
    assert row["fwd_return_60m"] is None  # no data reaches 60 minutes out
    assert row["fwd_return_180m"] is None


def test_analyze_horizon_detects_perfect_positive_correlation():
    """Construct data where fwd_return is EXACTLY 2x ib_return every day
    -- a perfect, unambiguous continuation relationship the analysis
    must detect as significant and positive."""
    rows = []
    for i in range(30):
        ib_ret = (i - 15) * 1.0  # varies from -15 to +14
        rows.append({
            "date": date(2024, 1, 1),
            "ib_open": 100.0,
            "ib_close": 100.0 + ib_ret,
            "ib_return": ib_ret,
            "fwd_return_30m": ib_ret * 2.0,
        })
    returns_df = pd.DataFrame(rows)

    result = st.analyze_horizon(returns_df, 30)

    assert result["n_days"] == 30
    assert result["correlation"] > 0.99
    assert result["correlation_significant"] is True
    assert result["mean_fwd_return_after_ib_up"] > result["mean_fwd_return_after_ib_down"]
    assert result["mean_diff_significant"] is True


def test_analyze_horizon_no_relationship_is_not_significant():
    """Construct data with NO relationship between ib_return and
    fwd_return (fwd_return is the same constant regardless of ib_return)
    -- correlation should be near zero / undefined-but-not-flagged
    significant, and the conditional means should be indistinguishable."""
    rng = np.random.default_rng(0)
    rows = []
    for i in range(200):
        ib_ret = rng.normal(0, 5)
        rows.append({
            "date": date(2024, 1, 1),
            "ib_open": 100.0,
            "ib_close": 100.0 + ib_ret,
            "ib_return": ib_ret,
            "fwd_return_30m": rng.normal(0, 5),  # independent of ib_return
        })
    returns_df = pd.DataFrame(rows)

    result = st.analyze_horizon(returns_df, 30)

    assert result["n_days"] == 200
    assert abs(result["correlation"]) < 0.3
    assert result["correlation_significant"] is False


def test_scan_all_days_skips_only_the_missing_day():
    day1 = date(2024, 1, 2)
    day2 = date(2024, 1, 3)
    tz = "America/New_York"

    day1_df = flat_bars(day1, tz, 9, 0, 60, price=101.0)  # no IB window at all
    day2_df = pd.concat([
        ib_bars_moving(day2, tz, ib_open=100.0, ib_close=101.0),
        flat_bars(day2, tz, 9, 0, 200, price=103.0),
    ])
    df = pd.concat([day1_df, day2_df])

    returns_df = st.scan_all_days(df)

    assert len(returns_df) == 1
    assert returns_df.iloc[0]["date"] == day2
