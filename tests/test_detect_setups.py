"""
test_detect_setups.py
=======================
Automated tests for the Opening Range Breakout detection logic.

WHAT A "TEST" IS, IF YOU'RE NEW TO THIS: instead of eyeballing a chart to
see "does this look right," we build a tiny, fake, fully-known dataset
where WE decide exactly what should happen, run the real code against it,
and have the computer check the answer matches. This catches bugs
immediately if someone (including future-Claude) changes the logic in a
way that breaks it, without needing to re-run the whole pipeline and
squint at a chart every time.

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date
import pandas as pd
import detect_setups as ds


def make_bars(day, tz, bars):
    """
    Helper: builds a small DataFrame of price bars from a simple list of
    (hour, minute, open, high, low, close) tuples, so each test can spell
    out exactly the prices it needs without repeating boilerplate.
    """
    rows = []
    index = []
    for hour, minute, o, h, l, c in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 100})
    return pd.DataFrame(rows, index=index)


def range_bars(day, tz, low=100.0, high=102.0):
    """15 minutes of bars (8:30-8:44) that stay between `low` and `high`,
    i.e. a clean, boring opening range with no drama."""
    bars = []
    for minute in range(30, 45):
        bars.append((8, minute, 101, high, low, 101))
    return make_bars(day, tz, bars)


def test_long_breakout_is_detected():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = range_bars(day, tz, low=100.0, high=102.0)
    # One bar right after the range window closes, breaking above the high.
    breakout = make_bars(day, tz, [(8, 45, 102, 103.5, 102, 103.2)])
    day_df = pd.concat([df, breakout])

    signal = ds.detect_orb_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "long"
    assert signal["range_high"] == 102.0
    assert signal["range_low"] == 100.0
    assert signal["entry"] == 103.2
    assert signal["stop"] == 100.0  # opposite side of the range


def test_short_breakout_is_detected():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = range_bars(day, tz, low=100.0, high=102.0)
    breakout = make_bars(day, tz, [(8, 45, 100, 100, 98.5, 99.0)])
    day_df = pd.concat([df, breakout])

    signal = ds.detect_orb_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "short"
    assert signal["entry"] == 99.0
    assert signal["stop"] == 102.0  # opposite side of the range


def test_no_breakout_returns_none():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = range_bars(day, tz, low=100.0, high=102.0)
    # Watch-window bars that never leave the range (8:45 through 9:14).
    calm_bars = []
    for m in range(0, 30):
        hour, minute = divmod(45 + m, 60)
        calm_bars.append((8 + hour, minute, 101, 101.5, 100.5, 101))
    calm = make_bars(day, tz, calm_bars)
    day_df = pd.concat([df, calm])

    signal = ds.detect_orb_for_day(day_df, day)

    assert signal is None


def test_missing_range_data_returns_none():
    """If a day has no bars during the range window at all (e.g. a data
    gap), we should skip it cleanly rather than crash or fake a range."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    day_df = make_bars(day, tz, [(9, 0, 101, 101.5, 100.5, 101)])  # starts after the range window

    signal = ds.detect_orb_for_day(day_df, day)

    assert signal is None
