"""
test_detect_fade_the_gap.py
==============================
Automated tests for the Fade the Gap detection and noon-bounded
backtest logic (research/setups/fade-the-gap.md).

Same tiny-fake-dataset approach as test_detect_ib_breakout.py and
test_study_overnight_gap.py -- build DataFrames where we know exactly
what should happen, run the real code, check the answer.

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date
import pandas as pd
import detect_fade_the_gap as fg


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


def test_gap_up_produces_short_signal():
    """A higher open than the prior 4pm close should fade SHORT, with
    target = prior_close and a symmetric (1:1) stop on the other side."""
    prior_day = date(2024, 1, 2)
    day = date(2024, 1, 3)
    tz = "America/New_York"
    prior_day_df = make_bars(prior_day, tz, [(15, 59, 100.0, 100.5, 99.5, 100.0)])
    day_df = make_bars(day, tz, [(8, 30, 105.0, 105.5, 104.5, 105.0)])

    signal = fg.detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)

    assert signal is not None
    assert signal["direction"] == "short"
    assert signal["prior_close"] == 100.0
    assert signal["today_open"] == 105.0
    assert signal["gap"] == 5.0
    assert signal["entry"] == 105.0
    assert signal["target"] == 100.0  # the gap-fill level itself
    assert signal["stop"] == 110.0    # same 5-point distance, opposite side -- 1:1 R:R


def test_gap_down_produces_long_signal():
    """A lower open than the prior 4pm close should fade LONG."""
    prior_day = date(2024, 1, 2)
    day = date(2024, 1, 3)
    tz = "America/New_York"
    prior_day_df = make_bars(prior_day, tz, [(15, 59, 100.0, 100.5, 99.5, 100.0)])
    day_df = make_bars(day, tz, [(8, 30, 95.0, 95.5, 94.5, 95.0)])

    signal = fg.detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)

    assert signal is not None
    assert signal["direction"] == "long"
    assert signal["entry"] == 95.0
    assert signal["target"] == 100.0
    assert signal["stop"] == 90.0  # same 5-point distance, opposite side


def test_zero_gap_returns_none():
    """No gap means nothing to fade -- degenerate case, not a signal."""
    prior_day = date(2024, 1, 2)
    day = date(2024, 1, 3)
    tz = "America/New_York"
    prior_day_df = make_bars(prior_day, tz, [(15, 59, 100.0, 100.5, 99.5, 100.0)])
    day_df = make_bars(day, tz, [(8, 30, 100.0, 100.5, 99.5, 100.0)])

    signal = fg.detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)

    assert signal is None


def test_missing_prior_close_returns_none():
    """If the prior day has no bars at/before 4pm ET (e.g. a data gap),
    there's no reference close to gap against -- skip cleanly."""
    prior_day = date(2024, 1, 2)
    day = date(2024, 1, 3)
    tz = "America/New_York"
    prior_day_df = make_bars(prior_day, tz, [(20, 0, 100.0, 100.5, 99.5, 100.0)])  # after 4pm only
    day_df = make_bars(day, tz, [(8, 30, 105.0, 105.5, 104.5, 105.0)])

    signal = fg.detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)

    assert signal is None


def test_missing_today_open_returns_none():
    """If today has no bars at or after 8:30 AM ET at all (e.g. data
    ends early that day), there's no entry to define -- skip cleanly."""
    prior_day = date(2024, 1, 2)
    day = date(2024, 1, 3)
    tz = "America/New_York"
    prior_day_df = make_bars(prior_day, tz, [(15, 59, 100.0, 100.5, 99.5, 100.0)])
    day_df = make_bars(day, tz, [(7, 0, 105.0, 105.5, 104.5, 105.0)])  # ends before 8:30

    signal = fg.detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)

    assert signal is None


def test_entry_after_watch_window_returns_none():
    """Real-data edge case: if the earliest available bar at/after 8:30
    already falls at or past the noon watch-end cutoff (a very sparse or
    gappy morning session), there is no watch window left to hold the
    trade in -- this must return None, not a signal with zero time left
    to resolve. (Caught by a crash on the real Discovery-slice run,
    where backtest.simulate_trade() indexed into an empty truncated
    DataFrame -- not anticipated by the clean synthetic data above.)"""
    prior_day = date(2024, 1, 2)
    day = date(2024, 1, 3)
    tz = "America/New_York"
    prior_day_df = make_bars(prior_day, tz, [(15, 59, 100.0, 100.5, 99.5, 100.0)])
    day_df = make_bars(day, tz, [(13, 0, 105.0, 105.5, 104.5, 105.0)])  # first bar is after noon

    signal = fg.detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)

    assert signal is None


def test_watch_end_time_is_noon():
    """The signal's watch_end_time must be 12:00 PM ET on the signal day,
    matching the underlying study's own gap-fill watch window."""
    prior_day = date(2024, 1, 2)
    day = date(2024, 1, 3)
    tz = "America/New_York"
    prior_day_df = make_bars(prior_day, tz, [(15, 59, 100.0, 100.5, 99.5, 100.0)])
    day_df = make_bars(day, tz, [(8, 30, 105.0, 105.5, 104.5, 105.0)])

    signal = fg.detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)

    assert signal["watch_end_time"] == pd.Timestamp(day, tz=tz).replace(hour=12, minute=0)


def test_simulate_hits_target_before_noon():
    """A trade that reaches its target before the noon cutoff should
    resolve normally via backtest.py's own simulate_trade()."""
    day = date(2024, 1, 3)
    tz = "America/New_York"
    signal = pd.Series({
        "direction": "short", "entry": 105.0, "stop": 110.0, "target": 100.0,
        "entry_time": pd.Timestamp(day, tz=tz).replace(hour=8, minute=30),
        "watch_end_time": pd.Timestamp(day, tz=tz).replace(hour=12, minute=0),
    })
    day_df = make_bars(day, tz, [
        (8, 30, 105.0, 105.5, 104.5, 105.0),
        (9, 0, 104.0, 104.5, 100.0, 100.5),  # low touches the target (100.0)
        (13, 0, 99.0, 99.5, 98.5, 99.0),      # after noon -- must never be reached
    ])

    outcome = fg.simulate_fade_the_gap_trade(day_df, signal)

    assert outcome["exit_reason"] == "target"
    assert outcome["exit_price"] == 100.0


def test_simulate_unresolved_by_noon_is_relabeled_noon_cutoff():
    """If neither stop nor target is hit before noon, the trade must be
    closed at the noon cutoff and labeled 'unresolved_noon_cutoff' --
    NOT 'unresolved_end_of_data' (which would misleadingly suggest the
    day's data simply ran out, when in fact this setup deliberately
    declines to hold past noon). A target hit AFTER noon must be
    ignored entirely."""
    day = date(2024, 1, 3)
    tz = "America/New_York"
    signal = pd.Series({
        "direction": "short", "entry": 105.0, "stop": 110.0, "target": 100.0,
        "entry_time": pd.Timestamp(day, tz=tz).replace(hour=8, minute=30),
        "watch_end_time": pd.Timestamp(day, tz=tz).replace(hour=12, minute=0),
    })
    day_df = make_bars(day, tz, [
        (8, 30, 105.0, 105.5, 104.5, 105.0),
        (9, 0, 104.0, 104.5, 103.5, 104.0),   # stays between stop and target all morning
        (11, 59, 104.0, 104.5, 103.5, 104.0),
        (12, 30, 100.0, 100.5, 99.5, 100.0),  # would hit target, but after noon -- must be ignored
    ])

    outcome = fg.simulate_fade_the_gap_trade(day_df, signal)

    assert outcome["exit_reason"] == "unresolved_noon_cutoff"


def test_scan_all_days_counts_no_gap_day():
    """scan_all_days()'s stats should count a zero-gap day as no_gap_days,
    not missing_reference_days."""
    day0 = date(2024, 1, 1)
    day1 = date(2024, 1, 2)
    tz = "America/New_York"
    day0_df = make_bars(day0, tz, [(15, 59, 100.0, 100.5, 99.5, 100.0)])
    day1_df = make_bars(day1, tz, [(8, 30, 100.0, 100.5, 99.5, 100.0)])

    df = pd.concat([day0_df, day1_df])

    signals, stats = fg.scan_all_days(df)

    assert signals == []
    assert stats["total_day_pairs"] == 1
    assert stats["no_gap_days"] == 1
    assert stats["missing_reference_days"] == 0


def test_scan_all_days_counts_missing_reference_day_separately():
    """scan_all_days()'s stats should distinguish a missing-reference-close
    day (no bars at/before 4pm ET the prior day) from an ordinary
    zero-gap day -- not lump them together silently."""
    day0 = date(2024, 1, 1)
    day1 = date(2024, 1, 2)
    tz = "America/New_York"
    day0_df = make_bars(day0, tz, [(20, 0, 100.0, 100.5, 99.5, 100.0)])  # only a post-4pm bar
    day1_df = make_bars(day1, tz, [(8, 30, 105.0, 105.5, 104.5, 105.0)])

    df = pd.concat([day0_df, day1_df])

    signals, stats = fg.scan_all_days(df)

    assert signals == []
    assert stats["total_day_pairs"] == 1
    assert stats["missing_reference_days"] == 1
    assert stats["no_gap_days"] == 0
