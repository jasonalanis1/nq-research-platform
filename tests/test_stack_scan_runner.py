"""Tests for src/stack_scan_runner.py -- synthetic bars only, no price data."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import stack_scan_runner as sr  # noqa: E402


def _day(prices, date="2026-09-08"):
    idx = pd.date_range(f"{date} 09:30", periods=len(prices), freq="1min", tz="America/New_York")
    c = np.asarray(prices, dtype=float)
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({"Open": o, "High": np.maximum(o, c) + 0.25,
                         "Low": np.minimum(o, c) - 0.25, "Close": c, "Volume": 1}, index=idx)


def test_target_before_stop_gives_positive_r():
    d = _day([100.0] * 30 + [101.0] + [101.0] * 20 + [110.0] * 100)
    sig = sr.trigger_orb_break_b3(d)
    assert sig is not None and sig["direction"] == "long"
    r = sr.realised_r(d, sig)
    assert r is not None and r > 0


def test_stop_hit_gives_exactly_minus_one_r():
    d = _day([100.0] * 30 + [101.0] + [90.0] * 100)
    sig = sr.trigger_orb_break_b3(d)
    assert sr.realised_r(d, sig) == -1.0


def test_stop_wins_when_one_bar_spans_both():
    # a bar whose range covers stop and target at once must resolve to the stop,
    # the conservative assumption fixed in advance
    d = _day([100.0] * 30 + [101.0] + [101.0] * 10)
    sig = sr.trigger_orb_break_b3(d)
    i = d.index.get_loc(sig["entry_time"])
    d.iloc[i, d.columns.get_loc("High")] = sig["target"] + 5
    d.iloc[i, d.columns.get_loc("Low")] = sig["stop"] - 5
    assert sr.realised_r(d, sig) == -1.0


def test_time_exit_r_is_scaled_by_risk():
    d = _day([100.0] * 30 + [101.0] + [101.5] * 100)
    sig = sr.trigger_orb_break_b3(d)
    r = sr.realised_r(d, sig)
    expected = (float(d["Close"].iloc[-1]) - sig["entry"]) / abs(sig["entry"] - sig["stop"])
    assert abs(r - round(expected, 4)) < 1e-3


def test_bootstrap_difference_recovers_a_known_gap():
    rng = np.random.default_rng(1)
    a = rng.normal(0.30, 1.0, 4000)
    b = rng.normal(0.00, 1.0, 4000)
    lo, hi, _ = sr._boot_diff(a, b, n_boot=2000, seed=7)
    assert lo > 0 and hi > lo
    assert abs(((lo + hi) / 2) - (a.mean() - b.mean())) < 0.05
