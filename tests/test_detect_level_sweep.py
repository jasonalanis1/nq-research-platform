"""
test_detect_level_sweep.py
============================
Automated tests for the Level Sweep Reversal setup (support/resistance
sweep + close-back confirmation).
"""
from datetime import date
import pandas as pd
import detect_level_sweep as dls


def make_bars(day, tz, bars):
    rows, index = [], []
    for hour, minute, o, h, l, c in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 100})
    return pd.DataFrame(rows, index=index)


def test_compute_levels_picks_the_more_extreme_of_each_pair():
    tz = "America/New_York"
    prior_day = date(2024, 1, 1)
    today = date(2024, 1, 2)

    # Prior day traded 100-110. Pre-market (before 8:30 today) traded 95-105
    # -- so the TRUE support should be the pre-market low (95, more extreme
    # than prior day's 100), and TRUE resistance should be prior day's high
    # (110, more extreme than pre-market's 105).
    prior_day_bars = make_bars(prior_day, tz, [(10, 0, 105, 110, 100, 105)])
    premarket_bars = make_bars(today, tz, [(7, 0, 100, 105, 95, 100)])
    df = pd.concat([prior_day_bars, premarket_bars])

    levels = dls.compute_levels(df, today, prior_day)

    assert levels is not None
    assert levels["support"] == 95
    assert levels["support_source"] == "premarket_low"
    assert levels["resistance"] == 110
    assert levels["resistance_source"] == "prior_day_high"


def test_compute_levels_returns_none_without_prior_day():
    tz = "America/New_York"
    today = date(2024, 1, 2)
    missing_prior_day = date(2024, 1, 1)
    df = make_bars(today, tz, [(7, 0, 100, 105, 95, 100)])

    assert dls.compute_levels(df, today, missing_prior_day) is None


def test_same_bar_sweep_and_reversal_is_detected():
    """The cleanest case shown in the reference video: one bar dips below
    support with its LOW, but closes back above it -- that's the entry,
    same bar."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    levels = {"support": 100.0, "support_source": "prior_day_low",
              "resistance": 120.0, "resistance_source": "prior_day_high",
              "open_ts": pd.Timestamp(day, tz=tz).replace(hour=8, minute=30)}

    day_df = make_bars(day, tz, [
        (8, 30, 102, 103, 101, 102),           # calm, no sweep yet
        (8, 31, 102, 103, 98, 101.5),          # sweeps support (low=98) but closes back above (101.5) -- signal
    ])

    signal = dls.scan_for_signal(day_df, levels)

    assert signal is not None
    assert signal["direction"] == "long"
    assert signal["level_source"] == "prior_day_low"
    assert signal["sweep_extreme"] == 98
    assert signal["entry"] == 101.5
    assert signal["stop"] == 98
    assert signal["target"] == 120.0  # the opposite level


def test_sweep_without_reversal_produces_no_signal():
    tz = "America/New_York"
    day = date(2024, 1, 2)
    levels = {"support": 100.0, "support_source": "prior_day_low",
              "resistance": 120.0, "resistance_source": "prior_day_high",
              "open_ts": pd.Timestamp(day, tz=tz).replace(hour=8, minute=30)}

    # Price sweeps support and just keeps falling -- never closes back above.
    day_df = make_bars(day, tz, [
        (8, 30, 102, 103, 99, 99.5),
        (8, 31, 99.5, 99.5, 95, 96),
        (8, 32, 96, 96, 90, 91),
    ])

    signal = dls.scan_for_signal(day_df, levels)

    assert signal is None


def test_multi_bar_sweep_tracks_the_worst_extreme_as_the_stop():
    """If price stays below support for a few bars before reversing, the
    stop should be the WORST point reached during the whole sweep, not
    just the first bar that dipped below."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    levels = {"support": 100.0, "support_source": "prior_day_low",
              "resistance": 120.0, "resistance_source": "prior_day_high",
              "open_ts": pd.Timestamp(day, tz=tz).replace(hour=8, minute=30)}

    day_df = make_bars(day, tz, [
        (8, 30, 100, 100, 98, 99),     # first dip below support, low=98
        (8, 31, 99, 99, 94, 95),       # worse dip, low=94 -- this should become the stop
        (8, 32, 95, 101, 95, 100.5),   # reverses and closes back above support
    ])

    signal = dls.scan_for_signal(day_df, levels)

    assert signal is not None
    assert signal["stop"] == 94
