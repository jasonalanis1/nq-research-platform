"""S008, late-day constant-leverage rebalance continuation -- the frozen trade's
mechanics on synthetic bars: the trailing-20 threshold, sign(M) continuation, the
0.50 x RNG stop, the 1.5R target, the 15:55 flat, and no look-ahead."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import strategy_s008_late_day_rebalance_continuation as s8  # noqa: E402


def _session(day: str, open_px: float, close_1500: float, width: float = 10.0) -> pd.DataFrame:
    """09:30 -> 16:00, one bar a minute, drifting linearly from open to the 15:00
    close and flat after, with a fixed high/low envelope of `width`."""
    idx = pd.date_range(f"{day} 09:30", f"{day} 16:00", freq="min", tz="America/New_York")
    n1500 = int(np.searchsorted(idx, pd.Timestamp(f"{day} 15:00", tz="America/New_York")))
    px = np.empty(len(idx))
    px[: n1500 + 1] = np.linspace(open_px, close_1500, n1500 + 1)
    px[n1500 + 1:] = close_1500
    return pd.DataFrame({"Open": px, "Close": px,
                         "High": px + width / 2.0, "Low": px - width / 2.0,
                         "Volume": 1000.0}, index=idx)


def _history(n_quiet: int = 25, quiet_move: float = 1.0, width: float = 10.0) -> pd.DataFrame:
    days = pd.bdate_range("2021-01-04", periods=n_quiet)
    return pd.concat([_session(d.strftime("%Y-%m-%d"), 100.0, 100.0 + quiet_move, width) for d in days])


def test_quiet_days_do_not_fire_and_a_large_move_day_does():
    hist = _history()
    big = _session("2021-02-15", 100.0, 140.0, width=10.0)      # M = +40 on a ~11-pt trailing range
    df = pd.concat([hist, big])
    s8.precompute(df)
    sigs = s8.generate_signals(df, df)
    assert [sg.market_context["date"] for sg in sigs] == ["2021-02-15"]
    sg = sigs[0]
    assert sg.direction == "long"                                # sign(M)
    assert sg.instrument == "MNQ" and sg.market_context["time_exit"] == "15:55"


def test_first_twenty_sessions_never_fire_no_trailing_history():
    """min_periods = 20: a session with fewer than 20 prior sessions has no
    threshold and is not traded, however large its move."""
    days = pd.bdate_range("2021-01-04", periods=10)
    df = pd.concat([_session(d.strftime("%Y-%m-%d"), 100.0, 160.0) for d in days])
    s8.precompute(df)
    assert s8.generate_signals(df, df) == []


def test_direction_is_continuation_not_a_fade():
    hist = _history()
    down = _session("2021-02-15", 100.0, 60.0)
    df = pd.concat([hist, down])
    s8.precompute(df)
    sg = s8.generate_signals(df, df)[0]
    assert sg.direction == "short" and sg.market_context["move_points"] < 0
    assert sg.stop > sg.entry and sg.target < sg.entry


def test_stop_is_half_the_range_and_the_target_is_one_and_a_half_r():
    hist = _history()
    big = _session("2021-02-15", 100.0, 140.0, width=10.0)
    df = pd.concat([hist, big])
    s8.precompute(df)
    sg = s8.generate_signals(df, df)[0]
    rng = sg.market_context["session_range"]
    risk = abs(sg.entry - sg.stop)
    assert abs(risk - 0.50 * rng) < 1e-9
    assert abs(abs(sg.target - sg.entry) / risk - 1.50) < 1e-9
    assert round(sg.risk_multiple, 2) == 1.50


def test_entry_is_the_next_bar_open_after_the_decision_bar_no_lookahead():
    hist = _history()
    big = _session("2021-02-15", 100.0, 140.0)
    df = pd.concat([hist, big])
    s8.precompute(df)
    sg = s8.generate_signals(df, df)[0]
    decision = pd.Timestamp(sg.market_context["decision_time"])
    assert decision.strftime("%H:%M") == "15:00"
    assert pd.Timestamp(sg.timestamp) > decision
    assert pd.Timestamp(sg.timestamp).strftime("%H:%M") == "15:01"
    assert sg.entry == float(big.loc[sg.timestamp, "Open"])


def test_threshold_is_exactly_half_the_trailing_median_range():
    hist = _history(quiet_move=1.0, width=10.0)          # trailing median RNG ~= 11
    s8.precompute(hist)
    med = list(s8._TRAILING_MEDIAN.values())[-1]
    just_under = _session("2021-02-15", 100.0, 100.0 + 0.5 * med - 0.5)
    just_over = _session("2021-02-16", 100.0, 100.0 + 0.5 * med + 5.0)
    df = pd.concat([hist, just_under, just_over])
    s8.precompute(df)
    dates = [sg.market_context["date"] for sg in s8.generate_signals(df, df)]
    assert "2021-02-15" not in dates and "2021-02-16" in dates


def test_audit_passes_on_a_clean_run():
    hist = _history()
    df = pd.concat([hist] + [_session(d, 100.0, 100.0 + m)
                             for d, m in (("2021-02-15", 40.0), ("2021-02-16", -35.0))])
    s8.precompute(df)
    a = s8.audit(s8.generate_signals(df, df))
    assert a["pass"] and a["n_signals"] == 2
    assert a["duplicate_days"] == 0 and a["lookahead_violations"] == 0
    assert a["wrong_direction"] == 0 and a["below_threshold"] == 0


def test_costs_come_from_the_cost_model_not_a_local_constant():
    import cost_model as cm
    src = (Path(__file__).resolve().parent.parent / "src" /
           "strategy_s008_late_day_rebalance_continuation.py").read_text()
    assert "import cost_model" in src
    # the $6.00 figure appears only in the docstring's account of the error
    body = src.split('"""', 2)[2]
    assert "6.00" not in body and "3.0 " not in body
    hist = _history()
    df = pd.concat([hist, _session("2021-02-15", 100.0, 140.0)])
    s8.precompute(df)
    sg = s8.generate_signals(df, df)[0]
    assert sg.market_context["cost_basis"] == cm.DEFAULT_NOTE
