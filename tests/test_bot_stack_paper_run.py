"""Tests for src/bot_stack_paper_run.py (BOT MILESTONE B7)."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

import bot_stack_paper_run as bpr  # noqa: E402


def _bars(rows):
    idx = pd.to_datetime([r[0] for r in rows]).tz_localize("America/New_York")
    return pd.DataFrame(
        {"Open": [r[1] for r in rows], "High": [r[2] for r in rows],
         "Low": [r[3] for r in rows], "Close": [r[4] for r in rows]},
        index=idx,
    )


def _orb_day(range_width, stop_pts, direction="long"):
    """A synthetic RTH day that fires base_entry_b3's ORB with a controlled
    range width (and therefore a controlled stop distance), so tests can
    exercise both "swing fits the $50-150 MNQ band" and "swing too wide"
    without depending on real market data."""
    t = pd.Timestamp("2026-01-06 09:30:00")
    hi, lo = 100.0 + range_width / 2, 100.0 - range_width / 2
    rows = [(str(t + pd.Timedelta(minutes=i)), 100.0, hi, lo, 100.0) for i in range(30)]
    breakout_ts = t + pd.Timedelta(minutes=30)   # 10:00
    entry_ts = breakout_ts + pd.Timedelta(minutes=1)
    if direction == "long":
        rows.append((str(breakout_ts), 100.0, hi + 1, hi - 0.1, hi + 0.5))     # closes above hi
        entry = lo + stop_pts + 0.05
        rows.append((str(entry_ts), entry, entry + 0.5, entry - 0.1, entry + 0.2))
        # rally after entry so a fill can resolve to target
        for i in range(1, 40):
            ts = entry_ts + pd.Timedelta(minutes=i)
            rows.append((str(ts), entry, entry + range_width * 3, entry - 0.1, entry + range_width * 2))
    else:
        rows.append((str(breakout_ts), 100.0, lo + 0.1, lo - 1, lo - 0.5))     # closes below lo
        entry = hi - stop_pts - 0.05
        rows.append((str(entry_ts), entry, entry + 0.1, entry - 0.5, entry - 0.2))
        for i in range(1, 40):
            ts = entry_ts + pd.Timedelta(minutes=i)
            rows.append((str(ts), entry, entry + 0.1, entry - range_width * 3, entry - range_width * 2))
    return _bars(rows)


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(bpr, "LOG_DIR", tmp_path)
    monkeypatch.setattr(bpr, "LOG_PATH", tmp_path / "bot_stack_paper_log.jsonl")
    monkeypatch.setattr(bpr, "JOURNAL_DIR", tmp_path / "order_path_journal")
    monkeypatch.setattr(bpr, "B7_ANCHOR_PATH", tmp_path / "anchor.json")
    # deterministic broker behaviour for tests that expect a specific fill
    # outcome -- production keeps the real (low, non-zero) hostile rates.
    monkeypatch.setattr(bpr, "BROKER_REJECT_RATE", 0.0)
    monkeypatch.setattr(bpr, "BROKER_PARTIAL_FILL_RATE", 0.0)
    monkeypatch.setattr(bpr, "BROKER_DISCONNECT_RATE", 0.0)
    monkeypatch.setattr(bpr, "BROKER_LATE_ACK_RATE", 0.0)
    yield


def test_seed_for_is_deterministic_not_python_hash():
    d = pd.Timestamp("2026-01-06").date()
    assert bpr._seed_for(d) == bpr._seed_for(d) == 20260106


def _permit(size_multiplier=1.0):
    return lambda date: {"trade_permission": True, "size_multiplier": size_multiplier, "permission_reasons": []}


def test_load_log_empty():
    assert bpr.load_log() == []


def test_append_and_load_roundtrip():
    bpr.append_row({"date": "2026-01-01", "outcome": "no_signal"})
    rows = bpr.load_log()
    assert len(rows) == 1 and rows[0]["date"] == "2026-01-01"


def test_running_state_folds_pnl():
    rows = [{"pnl_usd": 50.0}, {"pnl_usd": -20.0}, {"outcome": "no_signal"}, {"pnl_usd": 30.0}]
    st = bpr.running_state(rows)
    assert st["equity_usd"] == 60.0
    assert st["paper_trades"] == 3


def test_running_state_peak_tracks_drawdown_correctly():
    """Peak must reflect the HIGHEST equity ever reached, not just the final
    number -- capital_protection's trailing kill depends on this."""
    rows = [{"pnl_usd": 100.0}, {"pnl_usd": -80.0}]
    st = bpr.running_state(rows)
    assert st["equity_usd"] == 20.0
    assert st["peak_profit_usd"] == 100.0


def test_b7_execution_anchor_set_once():
    dates = [pd.Timestamp("2026-01-01").date(), pd.Timestamp("2026-01-05").date()]
    a1 = bpr._b7_execution_anchor(dates)
    assert a1 == pd.Timestamp("2026-01-05").date()
    assert bpr.B7_ANCHOR_PATH.exists()
    a2 = bpr._b7_execution_anchor([pd.Timestamp("2026-02-01").date()])
    assert a2 == a1   # a later, newer max date must not move an already-set anchor


def test_resolve_fill_outcome_stop_wins_on_tie():
    df = _bars([
        ("2026-01-06 10:00:00", 100.0, 100.0, 100.0, 100.0),
        ("2026-01-06 10:01:00", 100.0, 105.0, 95.0, 100.0),   # touches both stop and target same bar
    ])
    out = bpr._resolve_fill_outcome(df, "long", df.index[0], 100.0, 95.0, 105.0, "15:55")
    assert out["exit_reason"] == "stop"
    assert out["r_multiple"] == -1.0


def test_run_session_no_signal():
    df = _bars([("2026-01-06 09:30:00", 100, 100.5, 99.5, 100)] * 5)
    row = bpr.run_session(pd.Timestamp("2026-01-06").date(), df, [])
    assert row["outcome"] == "no_signal"


def test_run_session_wide_stop_blocked_under_LIVE_dollar_config(monkeypatch):
    """Mirrors the real 2026-09-08 session under the LIVE capital model: a real
    signal fires, the risk_state_engine permits trading, but the stop (~230pts
    here, $460) is far outside Jason's $50-150 swing band -- capital_protection
    blocks it fail-closed rather than silently sizing it down. That band is a
    live rule (B8); the paper loop no longer applies it -- see the next test."""
    import capital_protection as cp
    monkeypatch.setattr(bpr, "decision_for", _permit())
    monkeypatch.setattr(bpr, "CAPITAL_CFG", cp.CONFIG)
    df = _orb_day(range_width=230, stop_pts=230, direction="long")
    row = bpr.run_session(pd.Timestamp("2026-01-06").date(), df, [])
    assert row["outcome"] == "blocked"
    assert any("swing" in r for r in row["order_path"]["reasons"])
    assert "pnl_usd" not in row


def test_run_session_wide_stop_TRADES_under_paper_R_config(monkeypatch):
    """The 2026-09-14 staff-meeting change: in paper the capital model is
    R-denominated, so the same $460 swing that the live band blocks is a
    legitimate 1R paper trade with a 4R budget behind it."""
    import capital_protection as cp
    monkeypatch.setattr(bpr, "decision_for", _permit())
    assert bpr.CAPITAL_CFG is cp.PAPER_CONFIG        # the loop's default IS paper mode
    df = _orb_day(range_width=230, stop_pts=230, direction="long")
    row = bpr.run_session(pd.Timestamp("2026-01-06").date(), df, [])
    assert row["outcome"] in ("filled", "partial")
    assert row["gate"]["capital_model"] == "paper_R"
    assert row["gate"]["one_r_usd"] == pytest.approx(460.1)
    assert row["gate"]["remaining_budget_usd"] == pytest.approx(4 * 460.1)
    assert "pnl_usd" in row


def test_paper_mode_still_blocks_a_nonpositive_R():
    import capital_protection as cp
    assert not cp.swing_fits_budget(0.0, cp.PAPER_CONFIG)
    assert not cp.swing_fits_budget(float("nan"), cp.PAPER_CONFIG)
    assert cp.swing_fits_budget(460.0, cp.PAPER_CONFIG)
    assert not cp.swing_fits_budget(460.0, cp.CONFIG)      # live band unchanged


def test_effective_config_keeps_every_ratio_jason_set():
    import capital_protection as cp
    eff = cp.effective_config(cp.PAPER_CONFIG, 100.0)
    assert eff.starting_budget_usd == 400.0 and eff.raised_budget_usd == 600.0
    assert eff.trailing_floor_usd == 400.0
    assert eff.trailing_giveback_fraction == cp.CONFIG.trailing_giveback_fraction
    assert cp.effective_config(cp.CONFIG, 100.0) is cp.CONFIG   # live: untouched


def test_run_session_blocked_by_risk_state_engine(monkeypatch):
    monkeypatch.setattr(bpr, "decision_for", lambda date: {
        "trade_permission": False, "size_multiplier": 1.0,
        "permission_reasons": ["expected range in bottom decile"],
    })
    df = _orb_day(range_width=230, stop_pts=230, direction="long")
    row = bpr.run_session(pd.Timestamp("2026-01-06").date(), df, [])
    assert row["outcome"] == "blocked_by_risk_state_engine"
    assert row["reasons"] == ["expected range in bottom decile"]
    # the order path must never even be consulted when risk_state_engine itself refuses
    assert "order_path" not in row


def test_run_session_fills_and_books_pnl(monkeypatch):
    """A stop distance inside the $50-150 swing band (30pts -> $60) should
    actually submit, fill, and produce a bookkept pnl_usd."""
    monkeypatch.setattr(bpr, "decision_for", _permit())
    df = _orb_day(range_width=10, stop_pts=30, direction="long")
    row = bpr.run_session(pd.Timestamp("2026-01-06").date(), df, [])
    assert row["outcome"] in ("filled", "partial")
    assert "pnl_usd" in row and "bookkeeping" in row
    assert row["order_path"]["filled_qty"] > 0
    # the rally fixture is built to hit target, never the stop
    assert row["bookkeeping"]["exit_reason"] in ("target", "time_exit")


def test_run_session_short_side_fills_too(monkeypatch):
    monkeypatch.setattr(bpr, "decision_for", _permit())
    df = _orb_day(range_width=10, stop_pts=30, direction="short")
    row = bpr.run_session(pd.Timestamp("2026-01-06").date(), df, [])
    assert row["signal"]["direction"] == "short"
    assert row["outcome"] in ("filled", "partial")
    assert row["pnl_usd"] > 0   # fixture is built to rally the short into its target


def test_running_state_feeds_forward_between_sessions(monkeypatch):
    """A second session's gate must see the first session's realized pnl,
    not start over -- that's the whole point of a CONTINUOUS paper run."""
    monkeypatch.setattr(bpr, "decision_for", _permit())
    df = _orb_day(range_width=10, stop_pts=30, direction="long")
    row1 = bpr.run_session(pd.Timestamp("2026-01-06").date(), df, [])
    assert row1["gate"]["equity_usd"] == 0.0   # first session: no prior track record
    row2 = bpr.run_session(pd.Timestamp("2026-01-07").date(), df, [row1])
    assert row2["gate"]["paper_trades"] == 1
    assert row2["gate"]["equity_usd"] == row1["pnl_usd"]


def test_main_is_idempotent(monkeypatch, tmp_path):
    """Two calls to main() over the same data must not double-log a session
    that's already in the paper log."""
    monkeypatch.setattr(bpr, "decision_for", _permit())

    import data_loader
    day = _orb_day(range_width=10, stop_pts=30, direction="long")
    # pad to the close: the session-completeness guard (2026-09-14) refuses a day
    # whose last bar is before 15:55 ET, and this fixture represents a FULL session
    last_ts, last = day.index[-1], day.iloc[-1]
    close = last_ts.normalize() + pd.Timedelta(hours=15, minutes=59)
    extra_idx = pd.date_range(last_ts + pd.Timedelta(minutes=1), close, freq="min")
    df = pd.concat([day, pd.DataFrame({c: [float(last[c])] * len(extra_idx) for c in day.columns},
                                       index=extra_idx)])
    monkeypatch.setattr(data_loader, "load_price_data", lambda **kw: (df, False))

    bpr.main()
    n_after_first = len(bpr.load_log())
    assert n_after_first == 1
    bpr.main()
    assert len(bpr.load_log()) == n_after_first
