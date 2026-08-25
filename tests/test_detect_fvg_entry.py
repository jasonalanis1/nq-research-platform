"""
test_detect_fvg_entry.py
==========================
Automated tests for the FVG Entry Trigger variant's own logic (the
3-candle Fair Value Gap search that runs after Level Sweep Reversal's
existing, unchanged sweep/rejection confirmation). See
research/setups/fvg-entry-trigger.md for the frozen definition these
tests check against.
"""
from datetime import date
import pandas as pd
import detect_fvg_entry as dfe


def make_bars(day, tz, bars):
    rows, index = [], []
    for hour, minute, o, h, l, c in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 100})
    return pd.DataFrame(rows, index=index)


def test_obvious_long_fvg_is_detected():
    """Bullish FVG: candle1's high (100) is below candle3's low (110) --
    also places candle1 exactly at the window's inclusive lower bound
    (rejection close time + 1 minute)."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    day_df = make_bars(day, tz, [
        (8, 31, 100, 100, 100, 100),  # rejection-confirming candle
        (8, 32, 100, 100, 100, 100),  # candle1 (= window_start exactly)
        (8, 33, 100, 100, 100, 100),  # candle2
        (8, 34, 100, 110, 110, 105),  # candle3 -- low=110, gap vs candle1.high=100
    ])
    rejection = {"direction": "long", "signal_time": day_df.index[0]}

    result = dfe.find_fvg_after_rejection(day_df, rejection)

    assert result is not None
    assert result["fvg_candle1_time"] == day_df.index[1]
    assert result["fvg_candle3_time"] == day_df.index[3]
    assert result["entry_bar_close"] == 105


def test_obvious_short_fvg_is_detected():
    """Bearish FVG (mirror image): candle1's low (100) is above candle3's
    high (90)."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    day_df = make_bars(day, tz, [
        (8, 31, 100, 100, 100, 100),  # rejection-confirming candle
        (8, 32, 100, 100, 100, 100),  # candle1
        (8, 33, 100, 100, 100, 100),  # candle2
        (8, 34, 90, 90, 90, 95),      # candle3 -- high=90, gap vs candle1.low=100
    ])
    rejection = {"direction": "short", "signal_time": day_df.index[0]}

    result = dfe.find_fvg_after_rejection(day_df, rejection)

    assert result is not None
    assert result["fvg_candle1_time"] == day_df.index[1]
    assert result["fvg_candle3_time"] == day_df.index[3]
    assert result["entry_bar_close"] == 95


def test_rejection_candle_cannot_be_fvg_candle_one():
    """Proves the exclusion rule: the rejection-confirming candle itself
    (high=100) would wrongly pair with the bar 2 minutes later (low=110)
    to look like a valid gap if it were allowed to act as candle1. The
    REAL candle1 (the next bar, high=130) paired with the REAL candle3
    (low=90) has no gap (130 < 90 is false) -- so a correct
    implementation must return None, not the "gap" the buggy pairing
    would find."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    day_df = make_bars(day, tz, [
        (8, 31, 100, 100, 100, 100),  # rejection-confirming candle -- must NOT be usable as candle1
        (8, 32, 130, 130, 130, 130),  # REAL candle1
        (8, 33, 110, 110, 110, 110),  # would-be buggy "candle3" if rejection bar were candle1
        (8, 34, 90, 90, 90, 90),      # REAL candle3
    ])
    rejection = {"direction": "long", "signal_time": day_df.index[0]}

    assert dfe.find_fvg_after_rejection(day_df, rejection) is None


def test_candle_one_exactly_at_30min_boundary_is_excluded():
    """The window is half-open: candle1's open time must be STRICTLY less
    than window_start + 30min. A "perfect" gap is planted with candle1
    exactly at that boundary -- it must be rejected, not detected."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    bars = [(8, 31, 100, 100, 100, 100)]  # rejection-confirming candle, at 08:31
    # window_start = 08:32 (rejection close + 1 min); window_end_exclusive = 09:02.
    # Fill 08:32 through 09:06 with flat bars, except the planted boundary case.
    for minute_offset in range(1, 36):
        hour = 8 + (31 + minute_offset) // 60
        minute = (31 + minute_offset) % 60
        if minute_offset == 31:      # candle1 exactly at window_end_exclusive (09:02) -- must be excluded
            bars.append((hour, minute, 100, 100, 100, 100))
        elif minute_offset == 33:    # would-be candle3, 2 minutes later -- forms a "perfect" gap if wrongly allowed
            bars.append((hour, minute, 110, 110, 110, 110))
        else:
            bars.append((hour, minute, 100, 100, 100, 100))
    day_df = make_bars(day, tz, bars)
    rejection = {"direction": "long", "signal_time": day_df.index[0]}

    assert dfe.find_fvg_after_rejection(day_df, rejection) is None


def test_no_qualifying_fvg_returns_none():
    """Every bar flat/identical -- no possible gap in either direction."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    bars = [(8, 31, 100, 100, 100, 100)]
    for m in range(1, 40):
        hour = 8 + (31 + m) // 60
        minute = (31 + m) % 60
        bars.append((hour, minute, 100, 100, 100, 100))
    day_df = make_bars(day, tz, bars)
    rejection = {"direction": "long", "signal_time": day_df.index[0]}

    assert dfe.find_fvg_after_rejection(day_df, rejection) is None


def test_earlier_of_two_fvgs_in_window_is_returned():
    """Two independently valid FVGs form in the same window -- the
    earlier one must be returned, and the later one must be ignored
    entirely (it's obviously different: a huge, unmistakable gap)."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    day_df = make_bars(day, tz, [
        (8, 31, 100, 100, 100, 100),  # rejection-confirming candle
        (8, 32, 100, 100, 100, 100),  # candle1 of the FIRST (earlier) gap
        (8, 33, 100, 100, 100, 100),
        (8, 34, 100, 110, 110, 105),  # candle3 of the first gap (low=110)
        (8, 41, 100, 100, 100, 100),  # candle1 of a SECOND, later, much bigger gap
        (8, 42, 100, 100, 100, 100),
        (8, 43, 100, 200, 200, 150),  # candle3 of the second gap (low=200) -- must be ignored
    ])
    rejection = {"direction": "long", "signal_time": day_df.index[0]}

    result = dfe.find_fvg_after_rejection(day_df, rejection)

    assert result is not None
    assert result["fvg_candle1_time"] == day_df.index[1]
    assert result["fvg_candle3_time"] == day_df.index[3]


def test_zero_risk_fvg_is_discarded_not_emitted():
    """DISCOVERED 2026-08-24 on real data: candle3's close can, rarely,
    exactly match the sweep extreme (stop) -- a zero-risk 'trade' that
    can't be sized or scored (NaN r_multiple). scan_day_for_fvg_entry()
    must treat this as a no-trade outcome, not return a degenerate
    signal.

    scan_day_for_fvg_entry() computes levels itself from the full
    multi-day df (unlike find_fvg_after_rejection(), tested in
    isolation above), so this needs a real prior day + pre-market bar
    to get a valid support level, not just a hand-built levels dict."""
    tz = "America/New_York"
    prior_day = date(2024, 1, 1)
    today = date(2024, 1, 2)

    prior_day_bars = make_bars(prior_day, tz, [(10, 0, 105, 110, 100, 105)])  # prior day low=100, high=110
    today_bars = make_bars(today, tz, [
        (7, 0, 100, 105, 102, 103),      # pre-market: low=102 (>=100, so support stays prior-day-low=100)
        (8, 30, 102, 103, 98, 99),       # sweeps support, low=98 -- this becomes the stop
        (8, 31, 99, 99, 98.5, 100.5),    # closes back above support (100) -- rejection confirms here
        (8, 32, 90, 90, 90, 90),         # candle1 -- flat at 90
        (8, 33, 95, 95, 95, 95),         # candle2 -- flat at 95, irrelevant to the gap check
        (8, 34, 98, 98, 98, 98),         # candle3 -- flat at 98: gap vs candle1 (90 < 98), but closes at
                                          # EXACTLY 98 -- the same price as the stop (the sweep extreme)
    ])
    df = pd.concat([prior_day_bars, today_bars])

    result = dfe.scan_day_for_fvg_entry(df, today, prior_day, "close_any")

    assert result is None


def test_search_continues_past_first_non_matching_candle_one():
    """The first several candle1 candidates in the window do NOT form a
    gap -- the search must keep walking forward rather than stopping
    after the first miss, and find the later match."""
    tz = "America/New_York"
    day = date(2024, 1, 2)
    day_df = make_bars(day, tz, [
        (8, 31, 100, 100, 100, 100),  # rejection-confirming candle
        (8, 32, 100, 100, 100, 100),  # candle1 attempt 1 (with candle3 @ 8:34) -- no gap
        (8, 33, 100, 100, 100, 100),
        (8, 34, 100, 100, 100, 100),  # candle3 for attempt 1 -- flat, no gap
        (8, 35, 100, 100, 100, 100),
        (8, 36, 100, 100, 100, 100),  # candle1 that DOES form a gap (with candle3 @ 8:38)
        (8, 37, 100, 100, 100, 100),
        (8, 38, 100, 120, 120, 110),  # candle3 -- low=120, gap vs candle1.high=100
    ])
    rejection = {"direction": "long", "signal_time": day_df.index[0]}

    result = dfe.find_fvg_after_rejection(day_df, rejection)

    assert result is not None
    assert result["fvg_candle1_time"] == day_df.index[5]
    assert result["fvg_candle3_time"] == day_df.index[7]
