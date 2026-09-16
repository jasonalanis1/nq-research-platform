"""Cross-session (overnight) exits in the B7 paper loop -- choice 7 in
src/bot_stack_paper_run.py, built 2026-09-16 as S002's named FREEZE
PREREQUISITE.

Two things are proved here:

  1. THE SAME-SESSION PATH DID NOT MOVE. _REFERENCE_RESOLVE below is a verbatim
     copy of _resolve_fill_outcome as it stood BEFORE the change (commit adf46f7).
     Every same-session call -- B3, the execution dummy, S001a, anything without
     market_context["exit_ts"] -- must return a dict equal to the reference's,
     key for key, over a grid of synthetic sessions, and the loop's own rows for
     B3 and the dummy must match it end to end.
  2. AN OVERNIGHT TRADE IS BOOKKEPT OR IT STAYS OPEN. It resolves against the
     following session's bars (stop / target / time exit across the boundary),
     and when the EXIT session is not complete the entry session is deferred
     whole: nothing is written, nothing is force-closed, nothing is fabricated.
"""
import sys
import types
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

import bot_stack_paper_run as bpr  # noqa: E402
from strategy_contract import Signal, risk_multiple  # noqa: E402


# --------------------------------------------------------------------------
# the pre-change function, verbatim (do not "improve" it -- it is the baseline)
# --------------------------------------------------------------------------
def _REFERENCE_RESOLVE(day_df, direction, from_ts, entry_price, stop, target, time_exit):
    after = day_df[day_df.index > from_ts]
    exit_price, exit_reason, exit_ts = None, None, None
    for ts, bar in after.iterrows():
        lo, hi = float(bar["Low"]), float(bar["High"])
        if direction == "long":
            if lo <= stop:
                exit_price, exit_reason, exit_ts = stop, "stop", ts; break
            if hi >= target:
                exit_price, exit_reason, exit_ts = target, "target", ts; break
        else:
            if hi >= stop:
                exit_price, exit_reason, exit_ts = stop, "stop", ts; break
            if lo <= target:
                exit_price, exit_reason, exit_ts = target, "target", ts; break
        if ts.strftime("%H:%M") >= time_exit:
            exit_price, exit_reason, exit_ts = float(bar["Close"]), "time_exit", ts; break
    if exit_price is None:
        last = day_df.iloc[-1]
        exit_price, exit_reason, exit_ts = float(last["Close"]), "session_end_fallback", day_df.index[-1]
    risk = abs(entry_price - stop)
    move = (exit_price - entry_price) if direction == "long" else (entry_price - exit_price)
    r_multiple = round(move / risk, 4) if risk else None
    return {"exit_price": round(exit_price, 4), "exit_reason": exit_reason, "exit_time": str(exit_ts),
            "risk_points": round(risk, 4), "r_multiple": r_multiple}


def _bars(rows):
    idx = pd.to_datetime([r[0] for r in rows]).tz_localize("America/New_York")
    return pd.DataFrame({"Open": [r[1] for r in rows], "High": [r[2] for r in rows],
                         "Low": [r[3] for r in rows], "Close": [r[4] for r in rows]}, index=idx)


def _walk(day, start="09:30", n=390, base=100.0, drift=0.0, wiggle=1.0):
    """A deterministic pseudo-random session: no RNG, no fixtures on disk."""
    t0 = pd.Timestamp(f"{day} {start}:00")
    rows = []
    px = base
    for i in range(n):
        px = px + drift + wiggle * ((i * 7919) % 11 - 5) / 5.0
        rows.append((str(t0 + pd.Timedelta(minutes=i)), px, px + 2.0, px - 2.0, px + 0.5))
    return rows


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(bpr, "LOG_DIR", tmp_path)
    monkeypatch.setattr(bpr, "LOG_PATH", tmp_path / "bot_stack_paper_log.jsonl")
    monkeypatch.setattr(bpr, "JOURNAL_DIR", tmp_path / "order_path_journal")
    monkeypatch.setattr(bpr, "B7_ANCHOR_PATH", tmp_path / "anchor.json")
    monkeypatch.setattr(bpr, "BROKER_REJECT_RATE", 0.0)
    monkeypatch.setattr(bpr, "BROKER_PARTIAL_FILL_RATE", 0.0)
    monkeypatch.setattr(bpr, "BROKER_DISCONNECT_RATE", 0.0)
    monkeypatch.setattr(bpr, "BROKER_LATE_ACK_RATE", 0.0)
    yield


# ==========================================================================
# 1. the same-session path is unchanged
# ==========================================================================
def test_same_session_bookkeeping_is_identical_to_the_pre_change_function():
    """Every combination that matters -- stop hit, target hit, time exit,
    session-end fallback, both directions, several stop/target widths -- run
    through the new function with its new arguments defaulted, and through the
    frozen pre-change copy. The two dicts must be equal."""
    df = _bars(_walk("2026-01-06", n=200, drift=0.05))
    cases = 0
    for direction in ("long", "short"):
        for width in (1.0, 3.0, 7.5, 40.0, 400.0):
            for time_exit in ("09:45", "11:30", "15:55", "23:59"):
                from_ts = df.index[0]
                entry = float(df.iloc[1]["Open"])
                stop = entry - width if direction == "long" else entry + width
                target = entry + width * 2 if direction == "long" else entry - width * 2
                got = bpr._resolve_fill_outcome(df, direction, from_ts, entry, stop, target, time_exit)
                want = _REFERENCE_RESOLVE(df, direction, from_ts, entry, stop, target, time_exit)
                assert got == want, (direction, width, time_exit)
                cases += 1
    assert cases == 40
    # and the fallback branch is genuinely exercised by the grid above
    assert any(_REFERENCE_RESOLVE(df, "long", df.index[0], 100.0, -1e9, 1e9, t)["exit_reason"]
               == "session_end_fallback" for t in ("23:59",))


def test_explicit_none_arguments_are_the_same_call():
    df = _bars(_walk("2026-01-06", n=60))
    a = bpr._resolve_fill_outcome(df, "long", df.index[0], 100.0, 90.0, 110.0, "15:55")
    b = bpr._resolve_fill_outcome(df, "long", df.index[0], 100.0, 90.0, 110.0, "15:55",
                                  scan_df=None, exit_ts=None)
    assert a == b == _REFERENCE_RESOLVE(df, "long", df.index[0], 100.0, 90.0, 110.0, "15:55")


def _full_session(day, base=100.0):
    """A complete RTH session (last bar >= 15:55) that fires B3's ORB."""
    t = pd.Timestamp(f"{day} 09:30:00")
    hi, lo = base + 5.0, base - 5.0
    rows = [(str(t + pd.Timedelta(minutes=i)), base, hi, lo, base) for i in range(30)]
    bts = t + pd.Timedelta(minutes=30)
    rows.append((str(bts), base, hi + 1, hi - 0.1, hi + 0.5))
    entry = lo + 30.0 + 0.05
    ets = bts + pd.Timedelta(minutes=1)
    rows.append((str(ets), entry, entry + 0.5, entry - 0.1, entry + 0.2))
    for i in range(1, 355):
        ts = ets + pd.Timedelta(minutes=i)
        rows.append((str(ts), entry, entry + 15.0, entry - 0.1, entry + 10.0))
    return rows


def _permit():
    return lambda date: {"trade_permission": True, "size_multiplier": 1.0, "permission_reasons": []}


@pytest.mark.parametrize("strategy", ["b3", "dummy"])
def test_plumbing_rows_are_unchanged_and_never_defer(strategy, monkeypatch):
    """B3 and the execution dummy declare no exit_ts, so the loop must hand
    _resolve_fill_outcome scan_df=None/exit_ts=None and book exactly what the
    frozen pre-change function books. Neither may ever produce a deferred row."""
    monkeypatch.setattr(bpr, "decision_for", _permit())
    monkeypatch.setattr(bpr, "STRATEGY", strategy)
    day = pd.Timestamp("2026-01-06").date()
    df = _bars(_full_session("2026-01-06"))
    out = bpr.run_session(day, df, [], history=df)
    rows = out if isinstance(out, list) else [out]
    assert rows, "fixture produced no row"
    # the strategy's own signals, so each row's time exit is the real one
    name, gen = bpr.STRATEGIES[strategy]
    by_ts = {str(s.timestamp): s for s in bpr._signals(gen, df, df)}
    booked = 0
    for row in rows:
        assert "_defer" not in row and row["outcome"] != "open_trade_deferred"
        if "bookkeeping" not in row:
            continue
        sig = by_ts[row["signal"]["timestamp"]]
        te = (sig.market_context or {}).get("time_exit") or "15:55"
        want = _REFERENCE_RESOLVE(df, sig.direction, sig.timestamp, float(sig.entry),
                                  float(sig.stop), float(sig.target), te)
        assert row["bookkeeping"] == want
        booked += 1
    assert booked >= 1, "fixture booked no fill -- the comparison never ran"


def test_s001a_declares_no_cross_session_exit():
    import strategy_s001a_level_sweep_reversal_prior_day as s001a  # noqa: F401
    sig = Signal(strategy_name="x", strategy_version="1", timestamp=pd.Timestamp("2026-01-06 10:00"),
                 instrument="MNQ", timeframe="1m", direction="long", entry=100.0, stop=99.0,
                 target=102.0, risk_multiple=2.0, validation_status="research",
                 market_context={"time_exit": "15:55", "level_source": "prior_day_low"})
    assert bpr.cross_session_exit_ts(sig) is None


# ==========================================================================
# 2. the overnight trade
# ==========================================================================
def _overnight_frame(d1="2026-01-06", d2="2026-01-07", night_low=95.0, night_high=105.0,
                     next_open=103.0, d2_complete=True, d2_present=True):
    """D-1 RTH + its 16:00 evening bars, then D's overnight + RTH bars."""
    rows = [(str(pd.Timestamp(f"{d1} 09:30:00") + pd.Timedelta(minutes=i)), 100.0, 100.5, 99.5, 100.0)
            for i in range(0, 390)]                       # 09:30 -> 15:59
    # the 16:00 bar (entry bar) and the evening
    for i in range(0, 120):
        ts = pd.Timestamp(f"{d1} 16:00:00") + pd.Timedelta(minutes=i)
        rows.append((str(ts), 100.0, 100.5, 99.5, 100.0))
    if d2_present:
        # D's overnight bars carry the night's extremes
        for i in range(0, 570):                           # 00:00 -> 09:29
            ts = pd.Timestamp(f"{d2} 00:00:00") + pd.Timedelta(minutes=i)
            hi = night_high if i == 300 else 100.5
            lo = night_low if i == 300 else 99.5
            rows.append((str(ts), 100.0, hi, lo, 100.0))
        n_rth = 390 if d2_complete else 60                # complete -> last bar 15:59; else 10:29
        for i in range(0, n_rth):
            ts = pd.Timestamp(f"{d2} 09:30:00") + pd.Timedelta(minutes=i)
            o = next_open if i == 0 else 100.0
            rows.append((str(ts), o, max(o, 100.5), min(o, 99.5), 100.0))
    return _bars(rows)


def _night_signal(d1="2026-01-06", d2="2026-01-07", stop=90.0, target=1e9):
    entry_ts = pd.Timestamp(f"{d1} 16:00:00").tz_localize("America/New_York")
    exit_ts = pd.Timestamp(f"{d2} 09:30:00").tz_localize("America/New_York")
    return Signal(strategy_name="night_test", strategy_version="1", timestamp=entry_ts,
                  instrument="MNQ", timeframe="1m", direction="long", entry=100.0, stop=stop,
                  target=target, risk_multiple=risk_multiple(100.0, stop, target),
                  validation_status="research",
                  market_context={"exit_ts": str(exit_ts), "date": d1})


def test_cross_session_time_exit_books_the_next_sessions_open():
    df = _overnight_frame(next_open=103.0)
    sig = _night_signal()
    out = bpr._resolve_fill_outcome(df[df.index.date == pd.Timestamp("2026-01-06").date()],
                                    "long", sig.timestamp, 100.0, 90.0, 1e9, "15:55",
                                    scan_df=df, exit_ts=bpr.cross_session_exit_ts(sig))
    assert out["exit_reason"] == "time_exit"
    assert out["exit_price"] == 103.0                      # the 09:30 bar's OPEN
    assert out["exit_time"].startswith("2026-01-07 09:30")
    assert out["r_multiple"] == pytest.approx(0.3)         # +3 pts on a 10 pt risk


def test_cross_session_stop_fires_overnight_before_the_time_exit():
    df = _overnight_frame(night_low=88.0, next_open=103.0)
    out = bpr._resolve_fill_outcome(df[df.index.date == pd.Timestamp("2026-01-06").date()],
                                    "long", _night_signal().timestamp, 100.0, 90.0, 1e9, "15:55",
                                    scan_df=df, exit_ts=pd.Timestamp("2026-01-07 09:30").tz_localize("America/New_York"))
    assert out["exit_reason"] == "stop" and out["exit_price"] == 90.0
    assert out["r_multiple"] == -1.0
    assert out["exit_time"].startswith("2026-01-07 05:00")  # the overnight bar, not an RTH one


def test_cross_session_target_fires_overnight():
    df = _overnight_frame(night_high=130.0)
    out = bpr._resolve_fill_outcome(df[df.index.date == pd.Timestamp("2026-01-06").date()],
                                    "long", _night_signal().timestamp, 100.0, 90.0, 120.0, "15:55",
                                    scan_df=df, exit_ts=pd.Timestamp("2026-01-07 09:30").tz_localize("America/New_York"))
    assert out["exit_reason"] == "target" and out["exit_price"] == 120.0


def test_cross_session_never_falls_back_to_a_fabricated_session_end():
    """Data ends before the exit timestamp: the trade is OPEN. The same-session
    fallback (last bar's close) must NOT fire across a boundary."""
    df = _overnight_frame(d2_present=False)
    out = bpr._resolve_fill_outcome(df[df.index.date == pd.Timestamp("2026-01-06").date()],
                                    "long", _night_signal().timestamp, 100.0, 90.0, 1e9, "15:55",
                                    scan_df=df, exit_ts=pd.Timestamp("2026-01-07 09:30").tz_localize("America/New_York"))
    assert out is None


# ---- the completeness guard, extended to the EXIT session ----
def test_exit_session_readiness():
    x = pd.Timestamp("2026-01-07 09:30").tz_localize("America/New_York")
    ok, why = bpr.cross_session_exit_ready(_overnight_frame(), x)
    assert ok and why == ""
    ok, why = bpr.cross_session_exit_ready(_overnight_frame(d2_complete=False), x)
    assert not ok and "not complete" in why
    ok, why = bpr.cross_session_exit_ready(_overnight_frame(d2_present=False), x)
    assert not ok and "not on disk yet" in why
    ok, why = bpr.cross_session_exit_ready(None, x)
    assert not ok


def _night_module(**kw):
    def gen(day_df, history=None):
        d = str(day_df.index[0].date())
        if d != "2026-01-06":
            return []
        return [_night_signal(**kw)]
    return types.SimpleNamespace(STRATEGY_NAME="night_test_strategy", generate_signals=gen)


@pytest.fixture
def _night_registered(monkeypatch):
    bpr.register_strategy("night_test", _night_module())
    monkeypatch.setattr(bpr, "STRATEGY", "night_test")
    monkeypatch.setattr(bpr, "decision_for", _permit())
    yield
    bpr.STRATEGIES.pop("night_test", None)
    bpr.STRATEGY_MODULES.pop("night_test", None)


def test_run_session_books_an_overnight_trade(_night_registered):
    df = _overnight_frame(next_open=103.0)
    day = pd.Timestamp("2026-01-06").date()
    row = bpr.run_session(day, df[df.index.date == day], [], history=df)
    assert row["outcome"] in ("filled", "partial")
    assert row["bookkeeping"]["exit_reason"] == "time_exit"
    assert row["bookkeeping"]["exit_time"].startswith("2026-01-07 09:30")
    assert row["pnl_usd"] > 0


def test_open_trade_stays_open_when_the_exit_session_is_incomplete(_night_registered):
    """The directive's completeness guard, on the exit side: not force-closed,
    not fabricated, not written -- deferred, and reconsidered later."""
    df = _overnight_frame(d2_complete=False)
    day = pd.Timestamp("2026-01-06").date()
    row = bpr.run_session(day, df[df.index.date == day], [], history=df)
    assert row["outcome"] == "open_trade_deferred" and row["_defer"] is True
    assert "not complete" in row["note"]
    assert "pnl_usd" not in row and "bookkeeping" not in row


def test_open_trade_stays_open_when_the_exit_session_is_absent(_night_registered):
    df = _overnight_frame(d2_present=False)
    day = pd.Timestamp("2026-01-06").date()
    row = bpr.run_session(day, df[df.index.date == day], [], history=df)
    assert row["outcome"] == "open_trade_deferred"
    assert "not on disk yet" in row["note"]


def test_main_writes_nothing_for_a_deferred_session_then_scores_it_later(_night_registered, monkeypatch):
    """End to end: the first run has only a partial next session and logs NOTHING
    for the entry session; once that session completes, the SAME entry session is
    scored exactly once. The log is never rewritten."""
    import data_loader
    partial = _overnight_frame(d2_complete=False)
    monkeypatch.setattr(data_loader, "load_price_data", lambda **kw: (partial, False))
    monkeypatch.setattr(bpr, "B7_ANCHOR_PATH", bpr.B7_ANCHOR_PATH)   # anchor = latest date on disk
    bpr._b7_execution_anchor([pd.Timestamp("2026-01-06").date()])     # pin the anchor at D-1
    bpr.main(["--strategy", "night_test"])
    assert [r for r in bpr.load_log() if r.get("strategy") == "night_test_strategy"] == []

    complete = _overnight_frame(d2_complete=True, next_open=103.0)
    monkeypatch.setattr(data_loader, "load_price_data", lambda **kw: (complete, False))
    bpr.main(["--strategy", "night_test"])
    rows = [r for r in bpr.load_log()
            if r.get("strategy") == "night_test_strategy" and r["date"] == "2026-01-06"]
    assert len(rows) == 1
    assert rows[0]["bookkeeping"]["exit_time"].startswith("2026-01-07 09:30")

    bpr.main(["--strategy", "night_test"])                            # idempotent
    assert len([r for r in bpr.load_log()
                if r.get("strategy") == "night_test_strategy" and r["date"] == "2026-01-06"]) == 1


# ==========================================================================
# 3. the SCREEN uses the same bookkeeping
# ==========================================================================
def test_screen_resolves_an_overnight_trade_and_excludes_an_open_one():
    import screen_strategy
    mod = _night_module()
    mod.STRATEGY_VERSION = "1"
    res = screen_strategy.screen(mod, _overnight_frame(next_open=103.0), "synthetic")
    assert res["trades"] == 1 and res["open_unresolved_trades_excluded"] == 0
    assert res["trades_detail"][0]["exit_reason"] == "time_exit"
    open_res = screen_strategy.screen(mod, _overnight_frame(d2_present=False), "synthetic")
    assert open_res["trades"] == 0 and open_res["open_unresolved_trades_excluded"] == 1
    assert open_res["net_usd_1_micro"] == 0
