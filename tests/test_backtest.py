"""
test_backtest.py
==================
Automated tests for the trade simulation logic -- making sure that
"which got hit first, the stop or the target" resolves correctly,
including the tricky/ambiguous cases.
"""
from datetime import date
import pandas as pd
import backtest as bt


def make_bars(day, tz, bars):
    rows, index = [], []
    for hour, minute, o, h, l, c in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 100})
    return pd.DataFrame(rows, index=index)


def make_long_signal(breakout_time, entry=103.0, stop=100.0, target=105.0):
    return pd.Series({
        "breakout_time": breakout_time,
        "direction": "long",
        "entry": entry,
        "stop": stop,
        "target": target,
    })


def test_target_hit_first_is_a_win():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    breakout_time = pd.Timestamp(day, tz=tz).replace(hour=8, minute=45)
    signal = make_long_signal(breakout_time, entry=103, stop=100, target=105)

    bars_after = make_bars(day, tz, [
        (8, 46, 103, 104, 102.5, 103.5),   # neither hit yet
        (8, 47, 103.5, 105.5, 103, 105.2),  # target (105) touched here
    ])
    day_df = pd.concat([make_bars(day, tz, [(8, 45, 103, 103, 103, 103)]), bars_after])

    result = bt.simulate_trade(day_df, signal)

    assert result["exit_reason"] == "target"
    assert result["exit_price"] == 105


def test_stop_hit_first_is_a_loss():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    breakout_time = pd.Timestamp(day, tz=tz).replace(hour=8, minute=45)
    signal = make_long_signal(breakout_time, entry=103, stop=100, target=105)

    bars_after = make_bars(day, tz, [
        (8, 46, 103, 103.5, 102, 102.5),
        (8, 47, 102.5, 102.5, 99.5, 99.8),  # stop (100) touched here
    ])
    day_df = pd.concat([make_bars(day, tz, [(8, 45, 103, 103, 103, 103)]), bars_after])

    result = bt.simulate_trade(day_df, signal)

    assert result["exit_reason"] == "stop"
    assert result["exit_price"] == 100


def test_ambiguous_same_bar_assumes_stop_conservatively():
    """If one wild bar's range touches BOTH the stop and the target, we
    can't know which happened first from 1-minute data -- the code should
    conservatively assume the worse outcome (the stop) rather than
    quietly assuming the better one."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    breakout_time = pd.Timestamp(day, tz=tz).replace(hour=8, minute=45)
    signal = make_long_signal(breakout_time, entry=103, stop=100, target=105)

    wild_bar = make_bars(day, tz, [(8, 46, 103, 106, 99, 104)])  # spans both levels
    day_df = pd.concat([make_bars(day, tz, [(8, 45, 103, 103, 103, 103)]), wild_bar])

    result = bt.simulate_trade(day_df, signal)

    assert result["exit_reason"] == "stop (ambiguous bar)"
    assert result["exit_price"] == 100


def test_unresolved_when_data_runs_out():
    day = date(2024, 1, 2)
    tz = "America/New_York"
    breakout_time = pd.Timestamp(day, tz=tz).replace(hour=8, minute=45)
    signal = make_long_signal(breakout_time, entry=103, stop=100, target=105)

    # Price never reaches either level before the data for the day ends.
    calm = make_bars(day, tz, [(8, 46 + m, 103, 103.5, 102.5, 103) for m in range(0, 5)])
    day_df = pd.concat([make_bars(day, tz, [(8, 45, 103, 103, 103, 103)]), calm])

    result = bt.simulate_trade(day_df, signal)

    assert result["exit_reason"] == "unresolved_end_of_data"
