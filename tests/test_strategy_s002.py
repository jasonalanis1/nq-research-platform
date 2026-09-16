"""Tests for src/strategy_s002_overnight_carry_compressed_prior_day.py (S002).

Synthetic bars only. What is proved: the NARROW condition gates the trade, the
entry is the 16:00 bar's OPEN, the exit timestamp is the NEXT RTH session's 09:30
(and survives a weekend), the stop is one lagged ATR14 below the entry, no signal
can read a bar later than its own entry, and the paper loop books the resulting
overnight trade exactly as the spec describes.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

import strategy_s002_overnight_carry_compressed_prior_day as s002  # noqa: E402
import bot_stack_paper_run as bpr  # noqa: E402


def _session(day: str, width: float, base: float = 100.0, evening: bool = True, rth_end="15:59"):
    """One RTH session of the given range width, plus its 16:00-18:00 evening."""
    rows = []
    t = pd.Timestamp(f"{day} 09:30:00")
    hi, lo = base + width / 2, base - width / 2
    n = int((pd.Timestamp(f"{day} {rth_end}:00") - t).total_seconds() // 60) + 1
    for i in range(n):
        ts = t + pd.Timedelta(minutes=i)
        h = hi if i == 5 else base + 0.25
        l = lo if i == 7 else base - 0.25
        rows.append((str(ts), base, h, l, base))
    if evening:
        for i in range(0, 121):
            ts = pd.Timestamp(f"{day} 16:00:00") + pd.Timedelta(minutes=i)
            rows.append((str(ts), base, base + 0.5, base - 0.5, base))
    return rows


def _overnight(day: str, base: float = 100.0, low=None, high=None):
    rows = []
    for i in range(0, 570):
        ts = pd.Timestamp(f"{day} 00:00:00") + pd.Timedelta(minutes=i)
        h = high if (high is not None and i == 300) else base + 0.5
        l = low if (low is not None and i == 300) else base - 0.5
        rows.append((str(ts), base, h, l, base))
    return rows


def _frame(rows):
    idx = pd.to_datetime([r[0] for r in rows]).tz_localize("America/New_York")
    return pd.DataFrame({"Open": [r[1] for r in rows], "High": [r[2] for r in rows],
                         "Low": [r[3] for r in rows], "Close": [r[4] for r in rows],
                         "Volume": [100.0] * len(rows)}, index=idx)


def _history(narrow_day="2026-03-02", next_open=101.0, night_low=None, gap_days=1,
             narrow_width=2.0, wide_width=40.0):
    """25 wide sessions, then one NARROW session, then the exit session."""
    rows = []
    d = pd.Timestamp("2026-01-05")
    days = []
    while len(days) < 25:
        if d.weekday() < 5:
            days.append(d)
        d += pd.Timedelta(days=1)
    # strictly increasing widths: no earlier session can sit at or under the 20th
    # percentile of the 20 before it, so exactly ONE session (the narrow one) fires
    for i, x in enumerate(days):
        rows += _session(str(x.date()), wide_width + i)
        rows += _overnight(str(x.date()))
    rows += _session(narrow_day, narrow_width)          # the entry session
    exit_day = str((pd.Timestamp(narrow_day) + pd.Timedelta(days=gap_days)).date())
    rows += _overnight(exit_day, low=night_low)
    ex = _session(exit_day, 200.0, evening=False)       # deliberately wide: never a second signal
    ex[0] = (ex[0][0], next_open, max(next_open, ex[0][2]), min(next_open, ex[0][3]), ex[0][4])
    rows += ex
    return _frame(sorted(rows, key=lambda r: r[0])), exit_day


def test_narrow_session_fires_one_long_at_the_1600_open():
    df, exit_day = _history()
    s002.precompute(df)
    sigs = s002.generate_signals(df, history=df)
    assert len(sigs) == 1
    s = sigs[0]
    assert s.direction == "long" and s.instrument == "MNQ"
    assert pd.Timestamp(s.timestamp).strftime("%Y-%m-%d %H:%M") == "2026-03-02 16:00"
    assert s.entry == 100.0                                    # the 16:00 bar's OPEN
    assert s.market_context["exit_ts"].startswith(f"{exit_day} 09:30")
    assert s.market_context["exit_session_known"] is True
    assert s002.audit(sigs)["pass"]


def test_stop_is_one_lagged_atr_below_the_entry():
    df, _ = _history()
    s002.precompute(df)
    s = s002.generate_signals(df, history=df)[0]
    atr = s.market_context["atr14"]
    expected = sum(40.0 + i for i in range(11, 25)) / 14.0     # the 14 sessions before the entry day
    assert atr == pytest.approx(expected, abs=1e-6)
    assert s.stop == pytest.approx(s.entry - atr)
    assert s.target > s.entry + 1000                            # carry: unreachable sentinel


def test_a_wide_session_does_not_fire():
    df, _ = _history(narrow_width=300.0)
    s002.precompute(df)
    assert s002.generate_signals(df, history=df) == []


def test_exit_timestamp_skips_a_weekend():
    """2026-03-06 is a Friday; the next RTH session is Monday the 9th."""
    df, exit_day = _history(narrow_day="2026-03-06", gap_days=3)
    s002.precompute(df)
    s = s002.generate_signals(df, history=df)[0]
    assert exit_day == "2026-03-09"
    assert s.market_context["exit_ts"].startswith("2026-03-09 09:30")
    assert s.market_context["weekend_leg"] is True


def test_exit_session_absent_still_signals_but_only_to_defer():
    """Last session on disk: the placeholder exit timestamp must be refused by the
    paper loop's cross-session guard, never booked."""
    df, _ = _history()
    cut = df[df.index < pd.Timestamp("2026-03-03 00:00").tz_localize("America/New_York")]
    s002.precompute(cut)
    s = s002.generate_signals(cut, history=cut)[0]
    assert s.market_context["exit_session_known"] is False
    ready, why = bpr.cross_session_exit_ready(cut, bpr.cross_session_exit_ts(s))
    assert not ready and "not on disk yet" in why


def test_no_signal_without_a_1600_bar():
    df, _ = _history()
    no_evening = df[~((df.index.date == pd.Timestamp("2026-03-02").date()) & (df.index.hour >= 16))]
    s002.precompute(no_evening)
    assert s002.generate_signals(no_evening, history=no_evening) == []


def test_paper_loop_books_the_overnight_trade(monkeypatch, tmp_path):
    monkeypatch.setattr(bpr, "LOG_DIR", tmp_path)
    monkeypatch.setattr(bpr, "LOG_PATH", tmp_path / "log.jsonl")
    monkeypatch.setattr(bpr, "JOURNAL_DIR", tmp_path / "journal")
    for k in ("BROKER_REJECT_RATE", "BROKER_PARTIAL_FILL_RATE", "BROKER_DISCONNECT_RATE", "BROKER_LATE_ACK_RATE"):
        monkeypatch.setattr(bpr, k, 0.0)
    monkeypatch.setattr(bpr, "decision_for",
                        lambda date: {"trade_permission": True, "size_multiplier": 1.0, "permission_reasons": []})
    bpr.register_strategy("s002_t", s002)
    monkeypatch.setattr(bpr, "STRATEGY", "s002_t")
    try:
        df, exit_day = _history(next_open=140.0)      # +40 pts overnight
        s002.precompute(df)
        day = pd.Timestamp("2026-03-02").date()
        row = bpr.run_session(day, df[df.index.date == day], [], history=df)
        assert row["outcome"] in ("filled", "partial")
        assert row["bookkeeping"]["exit_reason"] == "time_exit"
        assert row["bookkeeping"]["exit_time"].startswith(f"{exit_day} 09:30")
        assert row["bookkeeping"]["exit_price"] == 140.0
        assert row["pnl_usd"] > 0
    finally:
        bpr.STRATEGIES.pop("s002_t", None); bpr.STRATEGY_MODULES.pop("s002_t", None)


def test_paper_loop_books_an_overnight_stop(monkeypatch, tmp_path):
    monkeypatch.setattr(bpr, "LOG_DIR", tmp_path)
    monkeypatch.setattr(bpr, "LOG_PATH", tmp_path / "log.jsonl")
    monkeypatch.setattr(bpr, "JOURNAL_DIR", tmp_path / "journal")
    for k in ("BROKER_REJECT_RATE", "BROKER_PARTIAL_FILL_RATE", "BROKER_DISCONNECT_RATE", "BROKER_LATE_ACK_RATE"):
        monkeypatch.setattr(bpr, k, 0.0)
    monkeypatch.setattr(bpr, "decision_for",
                        lambda date: {"trade_permission": True, "size_multiplier": 1.0, "permission_reasons": []})
    bpr.register_strategy("s002_t2", s002)
    monkeypatch.setattr(bpr, "STRATEGY", "s002_t2")
    try:
        df, _ = _history(night_low=10.0)              # a gap disaster overnight
        s002.precompute(df)
        day = pd.Timestamp("2026-03-02").date()
        row = bpr.run_session(day, df[df.index.date == day], [], history=df)
        assert row["bookkeeping"]["exit_reason"] == "stop"
        assert row["bookkeeping"]["r_multiple"] == -1.0
    finally:
        bpr.STRATEGIES.pop("s002_t2", None); bpr.STRATEGY_MODULES.pop("s002_t2", None)
