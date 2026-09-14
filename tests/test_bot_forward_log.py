"""Tests for src/bot_forward_log.py (BOT MILESTONE B4a/B7-EARLY: the free
statistical forward test of the bot stack -- NOT execution, see file header
docstring for the two-clocks distinction from src/order_path.py)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import bot_forward_log as bfl  # noqa: E402


def _day(prices, start="09:30", n=None, date="2026-09-14"):
    n = n or len(prices)
    idx = pd.date_range(f"{date} {start}", periods=n, freq="1min", tz="America/New_York")
    closes = np.asarray(prices, dtype=float)[:n]
    opens = np.concatenate([[closes[0]], closes[:-1]])
    return pd.DataFrame({"Open": opens, "High": np.maximum(opens, closes) + 0.25,
                         "Low": np.minimum(opens, closes) - 0.25, "Close": closes, "Volume": 1}, index=idx)


def test_simulate_outcome_long_hits_target_first():
    prices = [100.0] * 30 + [101.0, 101.5] + [104.0] * 100   # jumps straight to target after entry
    d = _day(prices)
    entry_ts = d.index[31]
    out = bfl._simulate_outcome(d, "long", entry_ts, entry=float(d["Open"].iloc[31]), stop=99.5,
                                 target=103.0, time_exit="15:55")
    assert out["exit_reason"] == "target"
    assert out["r_multiple"] > 0


def test_simulate_outcome_long_hits_stop_first():
    prices = [100.0] * 30 + [101.0, 101.5] + [95.0] * 100    # collapses through the stop
    d = _day(prices)
    entry_ts = d.index[31]
    out = bfl._simulate_outcome(d, "long", entry_ts, entry=float(d["Open"].iloc[31]), stop=99.5,
                                 target=110.0, time_exit="15:55")
    assert out["exit_reason"] == "stop"
    assert out["r_multiple"] < 0


def test_simulate_outcome_same_bar_ambiguity_resolves_to_stop():
    # one bar after entry has BOTH stop and target inside its High/Low range
    prices = [100.0] * 30 + [101.0, 101.5] + [101.5] * 100
    d = _day(prices).copy()
    entry_ts = d.index[31]
    after_ts = d.index[32]
    d.loc[after_ts, "Low"] = 90.0    # far below any plausible stop
    d.loc[after_ts, "High"] = 120.0  # far above any plausible target
    out = bfl._simulate_outcome(d, "long", entry_ts, entry=101.5, stop=99.0, target=104.0, time_exit="15:55")
    assert out["exit_reason"] == "stop"   # conservative -- never assumed in the strategy's favour


def test_simulate_outcome_falls_through_to_time_exit():
    prices = [100.0] * 30 + [101.0, 101.5] + [101.5] * 100   # flat -- never touches stop or target
    d = _day(prices)
    entry_ts = d.index[31]
    out = bfl._simulate_outcome(d, "long", entry_ts, entry=101.5, stop=50.0, target=200.0, time_exit="09:45")
    assert out["exit_reason"] == "time_exit"


def test_short_direction_mirrors_stop_and_target():
    prices = [100.0] * 30 + [99.0] + [103.0] * 100   # short signal, price runs up through the stop
    d = _day(prices)
    entry_ts = d.index[31]
    out = bfl._simulate_outcome(d, "short", entry_ts, entry=99.0, stop=100.5, target=95.0, time_exit="15:55")
    assert out["exit_reason"] == "stop"
    assert out["r_multiple"] < 0


def test_build_row_returns_none_on_no_signal_day():
    d = _day([100.0] * 130)
    assert bfl.build_row(d.index[0].date(), d) is None


def test_build_row_base_plus_b2_blocked_when_permission_false(monkeypatch):
    prices = [100.0] * 30 + [101.0, 101.5] + [101.5] * 100
    d = _day(prices)

    def fake_decision_for(date=None):
        return {"trade_permission": False, "permission_reasons": ["expected range in bottom decile"],
                "inputs": {"atr14_points": 50.0}, "stop_distance_atr": 0.5, "target_distance_atr": 1.0,
                "size_multiplier": 1.0}

    monkeypatch.setattr(bfl, "decision_for", fake_decision_for)
    row = bfl.build_row(d.index[0].date(), d)
    assert row is not None
    assert row["base_plus_b2"]["permitted"] is False
    assert "bottom decile" in row["base_plus_b2"]["reason"]
    assert row["base"]["permitted"] is True   # BASE is never gated by B2's permission flag


def test_build_row_base_plus_b2_uses_atr_conditioned_distances(monkeypatch):
    prices = [100.0] * 30 + [101.0, 101.5] + [104.0] * 100
    d = _day(prices)

    def fake_decision_for(date=None):
        return {"trade_permission": True, "permission_reasons": [], "inputs": {"atr14_points": 4.0},
                "stop_distance_atr": 0.5, "target_distance_atr": 1.0, "size_multiplier": 2.0}

    monkeypatch.setattr(bfl, "decision_for", fake_decision_for)
    row = bfl.build_row(d.index[0].date(), d)
    entry = row["entry"]
    assert row["base_plus_b2"]["stop"] == round(entry - 0.5 * 4.0, 4)
    assert row["base_plus_b2"]["target"] == round(entry + 1.0 * 4.0, 4)
    assert row["base_plus_b2"]["size"] == 2.0


def test_log_append_and_idempotent_load(tmp_path, monkeypatch):
    monkeypatch.setattr(bfl, "LOG_DIR", tmp_path)
    monkeypatch.setattr(bfl, "LOG_PATH", tmp_path / "bot_stack_forward_log.jsonl")
    assert bfl.load_log() == []
    bfl.append_row({"date": "2026-09-14", "x": 1})
    bfl.append_row({"date": "2026-09-15", "x": 2})
    rows = bfl.load_log()
    assert len(rows) == 2
    assert {r["date"] for r in rows} == {"2026-09-14", "2026-09-15"}
    # the file itself is genuinely append-only JSONL, one object per line
    lines = bfl.LOG_PATH.read_text().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["date"] == "2026-09-14"
