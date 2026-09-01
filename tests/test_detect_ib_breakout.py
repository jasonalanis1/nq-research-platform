"""
test_detect_ib_breakout.py
=============================
Automated tests for the Initial Balance Breakout detection logic
(research/setups/initial-balance-breakout.md).

Same tiny-fake-dataset approach as test_detect_setups.py -- build a
DataFrame where we know exactly what should happen, run the real code,
check the answer.

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date
import pandas as pd
import detect_ib_breakout as ib


def make_bars(day, tz, bars):
    """Helper: builds a small DataFrame of price bars from a simple list
    of (hour, minute, open, high, low, close) tuples."""
    rows = []
    index = []
    for hour, minute, o, h, l, c in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 100})
    return pd.DataFrame(rows, index=index)


def ib_bars(day, tz, low=100.0, high=102.0):
    """30 minutes of bars (8:30-8:59) that stay between `low` and `high`
    -- a clean Initial Balance range with no drama."""
    bars = []
    for minute in range(30, 60):
        bars.append((8, minute, 101, high, low, 101))
    return make_bars(day, tz, bars)


def test_long_breakout_is_detected():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = ib_bars(day, tz, low=100.0, high=102.0)
    breakout = make_bars(day, tz, [(9, 0, 102, 103.5, 102, 103.2)])
    day_df = pd.concat([df, breakout])

    signal = ib.detect_ib_breakout_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "long"
    assert signal["ib_high"] == 102.0
    assert signal["ib_low"] == 100.0
    assert signal["entry"] == 103.2
    assert signal["stop"] == 100.0  # opposite side of the IB range
    # target = entry + 1.35 * risk, risk = entry - stop = 3.2
    assert signal["target"] == round(103.2 + ib.TARGET_R_MULTIPLE * 3.2, 2)


def test_short_breakout_is_detected():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = ib_bars(day, tz, low=100.0, high=102.0)
    breakout = make_bars(day, tz, [(9, 0, 100, 100, 98.5, 99.0)])
    day_df = pd.concat([df, breakout])

    signal = ib.detect_ib_breakout_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "short"
    assert signal["entry"] == 99.0
    assert signal["stop"] == 102.0  # opposite side of the IB range
    risk = 102.0 - 99.0
    assert signal["target"] == round(99.0 - ib.TARGET_R_MULTIPLE * risk, 2)


def test_no_breakout_returns_none():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = ib_bars(day, tz, low=100.0, high=102.0)
    # Watch-window bars (9:00 through 11:59) that never leave the range.
    calm_bars = []
    for m in range(0, 180):
        hour, minute = divmod(m, 60)
        calm_bars.append((9 + hour, minute, 101, 101.5, 100.5, 101))
    calm = make_bars(day, tz, calm_bars)
    day_df = pd.concat([df, calm])

    signal = ib.detect_ib_breakout_for_day(day_df, day)

    assert signal is None


def test_missing_ib_data_returns_none():
    """If a day has no bars during the IB window at all (e.g. a data
    gap), skip it cleanly rather than crash or fake a range."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    day_df = make_bars(day, tz, [(9, 0, 101, 101.5, 100.5, 101)])  # starts after the IB window

    signal = ib.detect_ib_breakout_for_day(day_df, day)

    assert signal is None


def test_degenerate_zero_width_ib_range_returns_none():
    """A zero-width IB range (every bar flat at the same price -- e.g. a
    halted session or bad data) must not produce a trade. Same safeguard
    class as detect_fvg_entry.py's zero-risk-signal fix for exp-025."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    flat_bars = []
    for minute in range(30, 60):
        flat_bars.append((8, minute, 100.0, 100.0, 100.0, 100.0))
    df = make_bars(day, tz, flat_bars)
    # Even a real breakout-shaped bar afterward should never be reached --
    # the degenerate range should short-circuit before any signal fires.
    breakout = make_bars(day, tz, [(9, 0, 100, 105, 100, 104)])
    day_df = pd.concat([df, breakout])

    signal = ib.detect_ib_breakout_for_day(day_df, day)

    assert signal is None


def test_first_breakout_only_no_flip_flop():
    """If a long breakout fires first, a later short breakout in the same
    day must be ignored -- only the first qualifying event is tradeable,
    matching every other setup in this project."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = ib_bars(day, tz, low=100.0, high=102.0)
    long_break = make_bars(day, tz, [(9, 0, 102, 103.0, 102, 102.8)])
    short_break_later = make_bars(day, tz, [(9, 5, 99, 99.5, 98.0, 98.5)])
    day_df = pd.concat([df, long_break, short_break_later])

    signal = ib.detect_ib_breakout_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "long"
    assert signal["entry"] == 102.8


def test_breakout_after_noon_is_not_detected():
    """The breakout window ends at noon ET -- a close beyond the IB range
    at or after 12:00 PM must not produce a signal."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    df = ib_bars(day, tz, low=100.0, high=102.0)
    calm_bars = []
    for m in range(0, 180):  # 9:00 through 11:59, stays inside the range
        hour, minute = divmod(m, 60)
        calm_bars.append((9 + hour, minute, 101, 101.5, 100.5, 101))
    calm = make_bars(day, tz, calm_bars)
    late_breakout = make_bars(day, tz, [(12, 0, 102, 103.5, 102, 103.2)])
    day_df = pd.concat([df, calm, late_breakout])

    signal = ib.detect_ib_breakout_for_day(day_df, day)

    assert signal is None


def test_scan_all_days_counts_degenerate_days_separately():
    """scan_all_days()'s stats should distinguish a degenerate/missing IB
    day from a normal no-breakout day, not lump them together silently."""
    day1 = date(2024, 1, 2)
    day2 = date(2024, 1, 3)
    tz = "America/New_York"

    flat_bars = []
    for minute in range(30, 60):
        flat_bars.append((8, minute, 100.0, 100.0, 100.0, 100.0))
    day1_df = make_bars(day1, tz, flat_bars)

    day2_df = ib_bars(day2, tz, low=100.0, high=102.0)
    calm_bars = []
    for m in range(0, 180):
        hour, minute = divmod(m, 60)
        calm_bars.append((9 + hour, minute, 101, 101.5, 100.5, 101))
    day2_df = pd.concat([day2_df, make_bars(day2, tz, calm_bars)])

    df = pd.concat([day1_df, day2_df])

    signals, stats = ib.scan_all_days(df)

    assert signals == []
    assert stats["degenerate_or_missing_ib_days"] == 1
    assert stats["no_signal_days"] == 1
    assert stats["total_days"] == 2
