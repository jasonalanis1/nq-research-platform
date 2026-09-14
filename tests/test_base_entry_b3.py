"""Tests for src/base_entry_b3.py (bot milestone B3 placeholder entry)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import base_entry_b3 as b3  # noqa: E402


def _day(prices, start="09:30", n=None, date="2026-09-08"):
    """Build one session of 1-minute bars from a list of closes; open=prev close."""
    n = n or len(prices)
    idx = pd.date_range(f"{date} {start}", periods=n, freq="1min", tz="America/New_York")
    closes = np.asarray(prices, dtype=float)[:n]
    opens = np.concatenate([[closes[0]], closes[:-1]])
    return pd.DataFrame({"Open": opens, "High": np.maximum(opens, closes) + 0.25,
                         "Low": np.minimum(opens, closes) - 0.25, "Close": closes, "Volume": 1}, index=idx)


def test_long_breakout_uses_next_bar_open_not_trigger_close():
    # range 09:30-10:00 flat at 100; first window bar closes above range high; entry must be the NEXT bar's open
    prices = [100.0] * 30 + [101.0, 101.5] + [101.5] * 100
    d = _day(prices)
    s = b3.signal_for_day(d)
    assert s["direction"] == "long"
    assert s["trigger_time"] == d.index[30]
    assert s["entry_time"] == d.index[31]
    assert s["entry"] == float(d["Open"].iloc[31])
    assert s["stop"] == s["range_low"]
    assert abs(s["target"] - (s["entry"] + s["range_width"])) < 1e-9


def test_short_breakout_and_one_trade_per_day():
    prices = [100.0] * 30 + [99.0] + [102.0] * 100   # short fires first; later long ignored
    s = b3.signal_for_day(_day(prices))
    assert s["direction"] == "short" and s["stop"] == s["range_high"]


def test_no_signal_when_no_breakout():
    assert b3.signal_for_day(_day([100.0] * 130)) is None


def test_no_signal_outside_breakout_window():
    # breakout only after 11:30 -> ignored
    prices = [100.0] * 30 + [100.0] * 90 + [105.0] * 60
    assert b3.signal_for_day(_day(prices)) is None


def test_signals_are_placeholder_and_audit_passes():
    prices = [100.0] * 30 + [101.0, 101.5] + [101.5] * 100
    sigs = b3.generate_signals(_day(prices))
    assert len(sigs) == 1 and sigs[0].validation_status == "placeholder"
    assert sigs[0].market_context["placeholder"] is True
    a = b3.audit(sigs)
    assert a["pass"] and a["lookahead_violations"] == 0 and a["duplicate_days"] == 0


def test_audit_catches_lookahead():
    prices = [100.0] * 30 + [101.0, 101.5] + [101.5] * 100
    sigs = b3.generate_signals(_day(prices))
    sigs[0].market_context["trigger_time"] = str(sigs[0].timestamp)  # trigger == entry -> violation
    assert b3.audit(sigs)["pass"] is False
