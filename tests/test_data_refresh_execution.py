"""Tests for the data-refresh queue item (2026-09-14): data_continuity_check,
data_topup_databento's pure helpers, b7_replay (Step A) and execution_block."""
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bot_stack_paper_run as bpr  # noqa: E402
import b7_replay  # noqa: E402
import data_continuity_check as dcc  # noqa: E402
import data_topup_databento as topup  # noqa: E402
import execution_block  # noqa: E402
from test_bot_stack_paper_run import _orb_day, _permit  # noqa: E402

COLS = ["Open", "High", "Low", "Close", "Volume"]


def _series(start, n, base=100.0, step=1):
    idx = pd.date_range(start, periods=n, freq="min", tz="America/New_York")
    idx.name = "timestamp_ny"
    px = base + np.arange(n, dtype=float) * 0.01
    return pd.DataFrame({"Open": px, "High": px + 0.5, "Low": px - 0.5, "Close": px + 0.1,
                         "Volume": np.arange(n, dtype=float) + 1}, index=idx)


# ---------------------------------------------------------------- continuity
def test_continuity_pass_on_pure_append():
    old = _series("2026-09-08 09:30", 600)
    new = pd.concat([old, _series("2026-09-09 09:30", 600, base=float(old["Close"].iloc[-1]))])
    res = dcc.check_continuity(old, new)
    assert res["status"] == "PASS", res
    assert res["n_added"] == 600


def test_continuity_fails_if_a_historical_bar_changed():
    old = _series("2026-09-08 09:30", 600)
    new = pd.concat([old, _series("2026-09-09 09:30", 600, base=float(old["Close"].iloc[-1]))])
    new.iloc[10, new.columns.get_loc("Close")] += 0.25
    res = dcc.check_continuity(old, new)
    assert res["status"] == "FAIL"
    assert any(c["check"].startswith("4.") and c["status"] == "FAIL" for c in res["checks"])


def test_continuity_fails_if_old_bars_dropped_or_no_extension():
    old = _series("2026-09-08 09:30", 600)
    res = dcc.check_continuity(old, old.iloc[5:])
    assert res["status"] == "FAIL"
    res2 = dcc.check_continuity(old, old.copy())
    assert any(c["check"].startswith("5.") and c["status"] == "FAIL" for c in res2["checks"])


def test_continuity_junction_price_jump_fails_and_thin_session_only_warns():
    old = _series("2026-09-08 09:30", 600)
    jump = pd.concat([old, _series("2026-09-09 09:30", 600, base=200.0)])
    res = dcc.check_continuity(old, jump)
    assert any(c["check"].startswith("6.") and c["status"] == "FAIL" for c in res["checks"])
    thin = pd.concat([old, _series("2026-09-09 09:30", 20, base=float(old["Close"].iloc[-1]))])
    res2 = dcc.check_continuity(old, thin)
    assert res2["status"] == "PASS"
    assert any(c["check"].startswith("7.") and c["status"] == "WARN" for c in res2["checks"])


# --------------------------------------------------------------------- topup
def test_topup_window_starts_one_minute_after_last_bar_in_utc():
    old = _series("2026-09-08 19:55", 5)   # ends 19:59 NY = 23:59 UTC
    start, end = topup.topup_window(old, now_utc=dt.datetime(2026, 9, 14, 18, 30, 45),
                                    available_end=dt.datetime(2026, 9, 14, 23, 0))
    assert start == dt.datetime(2026, 9, 9, 0, 0)
    assert end == dt.datetime(2026, 9, 14, 18, 30)


def test_topup_window_clamps_to_the_dataset_available_end():
    """Regression, 2026-09-14: asking for end="now" is rejected outright with
    422 data_end_after_available_end -- GLBX.MDP3's historical end lags real time
    by ~20 minutes. The window must never run past the dataset's own end."""
    old = _series("2026-09-08 19:55", 5)
    start, end = topup.topup_window(old, now_utc=dt.datetime(2026, 9, 14, 23, 12),
                                    available_end=dt.datetime(2026, 9, 14, 22, 50, 31))
    assert start == dt.datetime(2026, 9, 9, 0, 0)
    assert end == dt.datetime(2026, 9, 14, 22, 50)


def test_topup_window_falls_back_to_a_lag_when_available_end_unknown():
    old = _series("2026-09-08 19:55", 5)
    _, end = topup.topup_window(old, now_utc=dt.datetime(2026, 9, 14, 23, 12))
    assert end == dt.datetime(2026, 9, 14, 23, 12) - dt.timedelta(minutes=topup.AVAILABLE_LAG_MINUTES)


def test_topup_window_refuses_when_available_end_is_behind_the_file():
    old = _series("2026-09-08 19:55", 5)
    with pytest.raises(SystemExit):
        topup.topup_window(old, now_utc=dt.datetime(2026, 9, 14, 23, 12),
                           available_end=dt.datetime(2026, 9, 8, 22, 0))


def test_topup_window_refuses_when_nothing_to_add():
    old = _series("2026-09-08 19:55", 5)
    with pytest.raises(SystemExit):
        topup.topup_window(old, now_utc=dt.datetime(2026, 9, 8, 23, 0),
                           available_end=dt.datetime(2026, 9, 8, 23, 0))


def test_merge_keeps_old_bars_authoritative_and_appends_only_after_end():
    old = _series("2026-09-08 09:30", 10)
    raw = _series("2026-09-08 09:35", 10, base=500.0)   # overlaps 5 bars with different prices
    merged = topup.merge(old, raw)
    assert len(merged) == 15
    assert merged.loc[old.index].equals(old)
    assert merged.index.is_monotonic_increasing and merged.index.is_unique


def test_to_pipeline_frame_converts_utc_lowercase_to_ny_schema():
    idx = pd.date_range("2026-09-09 00:00", periods=3, freq="min", tz="UTC")
    raw = pd.DataFrame({"open": [1.0] * 3, "high": [2.0] * 3, "low": [0.5] * 3, "close": [1.5] * 3,
                        "volume": [7] * 3, "symbol": ["NQ.c.0"] * 3}, index=idx)
    out = topup.to_pipeline_frame(raw)
    assert list(out.columns) == COLS and out.index.name == "timestamp_ny"
    assert str(out.index.tz) == "America/New_York" and out.index[0].hour == 20


def test_topup_cap_default_is_top_of_approved_estimate():
    assert topup.DEFAULT_CAP_USD == 15.00


# -------------------------------------------------------------------- replay
@pytest.fixture
def quiet_broker(monkeypatch):
    for k in ("BROKER_REJECT_RATE", "BROKER_PARTIAL_FILL_RATE", "BROKER_DISCONNECT_RATE", "BROKER_LATE_ACK_RATE"):
        monkeypatch.setattr(bpr, k, 0.0)
    monkeypatch.setattr(bpr, "decision_for", _permit())


def _two_day_frame():
    d1 = _orb_day(range_width=10.0, stop_pts=40.0, direction="long")   # $80 swing on MNQ: fits band
    d2 = _orb_day(range_width=10.0, stop_pts=40.0, direction="short")
    d2.index = d2.index + pd.Timedelta(days=1)
    return pd.concat([d1, d2])


def test_replay_runs_real_loop_into_its_own_dirs_and_passes_checks(tmp_path, quiet_broker, monkeypatch):
    live_log = tmp_path / "live" / "bot_stack_paper_log.jsonl"
    live_log.parent.mkdir()
    live_log.write_text('{"date": "2026-01-05", "outcome": "no_signal"}\n')
    monkeypatch.setattr(bpr, "LOG_PATH", live_log)
    monkeypatch.setattr(bpr, "JOURNAL_DIR", tmp_path / "live" / "journal")
    df = _two_day_frame()
    sessions = sorted(set(df.index.date))
    replay_dir = tmp_path / "replay"
    res = b7_replay.replay(df, sessions, replay_dir)
    assert len(res["rows"]) == 2 and all(r["replay"] for r in res["rows"])
    assert live_log.read_text().count("\n") == 1                      # live record untouched
    assert bpr.LOG_PATH == live_log and bpr.JOURNAL_DIR == tmp_path / "live" / "journal"
    checks = b7_replay.mechanical_checks(res["rows"], res["intents_per_session"], replay_dir / "journal", df, sessions)
    assert all(c["status"] == "PASS" for c in checks), checks
    assert sum(1 for r in res["rows"] if r.get("order_path", {}).get("filled_qty")) == 2
    # rebuilt from scratch on a second run, not accumulated
    res2 = b7_replay.replay(df, sessions, replay_dir)
    assert (replay_dir / "replay_log.jsonl").read_text().count("\n") == 2
    assert res2["intents_per_session"] == res["intents_per_session"]


def test_replay_checks_catch_a_requested_price_that_differs_from_spec(tmp_path, quiet_broker, monkeypatch):
    monkeypatch.setattr(bpr, "LOG_PATH", tmp_path / "live.jsonl")
    monkeypatch.setattr(bpr, "JOURNAL_DIR", tmp_path / "live_j")
    df = _two_day_frame()
    sessions = sorted(set(df.index.date))
    replay_dir = tmp_path / "replay"
    res = b7_replay.replay(df, sessions, replay_dir)
    # corrupt one journaled intent's intended_price to simulate a wrong order
    jp = next((replay_dir / "journal").glob("*.jsonl"))
    lines = jp.read_text().splitlines()
    for i, ln in enumerate(lines):
        rec = json.loads(ln)
        if rec["event"] == "order_intent":
            rec["intended_price"] += 1.0
            lines[i] = json.dumps(rec)
            break
    jp.write_text("\n".join(lines) + "\n")
    checks = b7_replay.mechanical_checks(res["rows"], res["intents_per_session"], replay_dir / "journal", df, sessions)
    r6 = next(c for c in checks if c["check"].startswith("R6"))
    assert r6["status"] == "FAIL" and r6["passed"] == r6["n"] - 1


def test_replay_checks_catch_hanging_order_and_double_order(tmp_path, quiet_broker, monkeypatch):
    monkeypatch.setattr(bpr, "LOG_PATH", tmp_path / "live.jsonl")
    monkeypatch.setattr(bpr, "JOURNAL_DIR", tmp_path / "live_j")
    df = _two_day_frame()
    sessions = sorted(set(df.index.date))
    replay_dir = tmp_path / "replay"
    res = b7_replay.replay(df, sessions, replay_dir)
    jp = next((replay_dir / "journal").glob("*.jsonl"))
    recs = [json.loads(l) for l in jp.read_text().splitlines()]
    intent = next(r for r in recs if r["event"] == "order_intent")
    orphan = dict(intent, order_id="B4A-orphan")
    jp.write_text("\n".join(json.dumps(r) for r in recs + [orphan]) + "\n")
    per = dict(res["intents_per_session"]); per[str(sessions[0])] = 2
    checks = b7_replay.mechanical_checks(res["rows"], per, replay_dir / "journal", df, sessions)
    by = {c["check"][:2]: c for c in checks}
    assert by["R2"]["status"] == "FAIL" and by["R4"]["status"] == "FAIL"


# ------------------------------------------------------------ execution block
def test_execution_block_no_fills_says_so_and_labels_replay(tmp_path):
    live = {"fills_total": 0, "fills_this_cycle": 0, "avg_slippage_pts": None, "max_abs_deviation_pts": None}
    txt = execution_block.render(replay_report=None, live=live, since="2026-09-14T00:00:00")
    assert "no live fills yet" in txt and "0 / 40" in txt and "no replay this cycle" in txt
    rep = {"n_fills": 3, "n_order_intents": 3, "sessions": ["a", "b", "c"], "defects": [],
           "mechanical_checks": [{}] * 8}
    txt2 = execution_block.render(replay_report=rep, live=live, since="2026-09-14T00:00:00")
    assert "3 (REPLAY" in txt2 and "not the live record" in txt2 and "none found in replay (8 checks PASS)" in txt2


def test_execution_block_reports_defects_as_unfixed_and_real_costs():
    live = {"fills_total": 21, "fills_this_cycle": 2, "avg_slippage_pts": 0.3125, "max_abs_deviation_pts": 1.25}
    rep = {"n_fills": 0, "n_order_intents": 1, "sessions": ["a"], "mechanical_checks": [{}],
           "defects": [{"check": "R4 every order terminal", "n": 1, "passed": 0, "note": "hanging: ['x']"}]}
    txt = execution_block.render(replay_report=rep, live=live, since="2026-09-14T00:00:00")
    assert "+0.3125 pts/fill" in txt and "21 / 40" in txt and "NOT yet fixed" in txt
    assert "none charged by the simulated broker" in txt


def test_live_stats_counts_fills_since_cycle_start(tmp_path):
    j = tmp_path / "j"; j.mkdir()
    recs = [{"event": "fill", "ts": "2026-09-14T10:00:00", "deviation_pts": 0.5},
            {"event": "fill", "ts": "2026-09-14T17:00:00", "deviation_pts": -0.25},
            {"event": "order_ack", "ts": "2026-09-14T17:00:00"}]
    (j / "2026-09-14.jsonl").write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    st = execution_block.live_stats(journal_dir=j, since="2026-09-14T16:00:00")
    assert st == {"fills_total": 2, "fills_this_cycle": 1, "avg_slippage_pts": 0.125, "max_abs_deviation_pts": 0.5}
