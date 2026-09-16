"""S010, thin-participation afternoon completion continuation -- the frozen trade's
mechanics on synthetic bars: the trailing-20 median VOLUME threshold, sign(M)
continuation, the 0.50 x RNG stop, the 1.5R target, the 15:55 flat, no look-ahead,
the fragment guard, one trade per session, and registration in the paper loop."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import strategy_s010_thin_participation_completion as s10  # noqa: E402


def _session(day: str, open_px: float, close_1400: float, volume: float = 1000.0,
             width: float = 10.0) -> pd.DataFrame:
    """09:30 -> 16:00, one bar a minute, drifting linearly from the open to the
    14:00 close and flat after, with a fixed high/low envelope of `width`."""
    idx = pd.date_range(f"{day} 09:30", f"{day} 16:00", freq="min", tz="America/New_York")
    n1400 = int(np.searchsorted(idx, pd.Timestamp(f"{day} 14:00", tz="America/New_York")))
    px = np.empty(len(idx))
    px[: n1400 + 1] = np.linspace(open_px, close_1400, n1400 + 1)
    px[n1400 + 1:] = close_1400
    return pd.DataFrame({"Open": px, "Close": px,
                         "High": px + width / 2.0, "Low": px - width / 2.0,
                         "Volume": volume}, index=idx)


def _history(n: int = 25, volume: float = 1000.0) -> pd.DataFrame:
    """Trailing history that sets the median volume and never fires itself: every
    session is FLAT to 14:00, so M == 0 and the `M != 0` rule excludes it."""
    days = pd.bdate_range("2021-01-04", periods=n)
    return pd.concat([_session(d.strftime("%Y-%m-%d"), 100.0, 100.0, volume=volume) for d in days])


def test_a_busy_day_does_not_fire_and_a_thin_day_does():
    hist = _history(volume=1000.0)
    busy = _session("2021-02-15", 100.0, 140.0, volume=2000.0)    # VOL above the trailing median
    thin = _session("2021-02-16", 100.0, 140.0, volume=500.0)     # VOL below it
    df = pd.concat([hist, busy, thin])
    s10.precompute(df)
    sigs = s10.generate_signals(df, df)
    assert [sg.market_context["date"] for sg in sigs] == ["2021-02-16"]
    sg = sigs[0]
    assert sg.direction == "long"                                  # sign(M)
    assert sg.instrument == "MNQ" and sg.market_context["time_exit"] == "15:55"
    assert sg.market_context["participation_ratio"] < 1.0


def test_first_twenty_sessions_never_fire_no_trailing_history():
    days = pd.bdate_range("2021-01-04", periods=10)
    df = pd.concat([_session(d.strftime("%Y-%m-%d"), 100.0, 140.0, volume=1.0) for d in days])
    s10.precompute(df)
    assert s10.generate_signals(df, df) == []


def test_direction_is_continuation_not_a_fade():
    df = pd.concat([_history(), _session("2021-02-15", 100.0, 60.0, volume=500.0)])
    s10.precompute(df)
    sg = s10.generate_signals(df, df)[0]
    assert sg.direction == "short" and sg.market_context["move_points"] < 0
    assert sg.stop > sg.entry and sg.target < sg.entry


def test_a_flat_session_has_no_side_and_does_not_fire():
    """M == 0: nobody is behind their benchmark on either side, so there is no trade
    even though participation was thin. (The trailing history is flat for the same
    reason, which is why it never fires.)"""
    df = pd.concat([_history(), _session("2021-02-15", 100.0, 100.0, volume=500.0)])
    s10.precompute(df)
    assert s10.generate_signals(df, df) == []


def test_stop_is_half_the_range_and_the_target_is_one_and_a_half_r():
    df = pd.concat([_history(), _session("2021-02-15", 100.0, 140.0, volume=500.0, width=10.0)])
    s10.precompute(df)
    sg = s10.generate_signals(df, df)[0]
    risk = abs(sg.entry - sg.stop)
    assert abs(risk - 0.50 * sg.market_context["session_range"]) < 1e-9
    assert abs(abs(sg.target - sg.entry) / risk - 1.50) < 1e-9
    assert round(sg.risk_multiple, 2) == 1.50


def test_entry_is_the_next_bar_open_after_the_decision_bar_no_lookahead():
    day = "2021-02-15"
    df = pd.concat([_history(), _session(day, 100.0, 140.0, volume=500.0)])
    s10.precompute(df)
    sg = s10.generate_signals(df, df)[0]
    assert pd.Timestamp(sg.market_context["decision_time"]).strftime("%H:%M") == "14:00"
    assert pd.Timestamp(sg.timestamp).strftime("%H:%M") == "14:01"
    assert pd.Timestamp(sg.timestamp) > pd.Timestamp(sg.market_context["decision_time"])
    assert s10.audit([sg])["pass"]


def test_a_fragment_session_is_skipped():
    day = "2021-02-15"
    frag = _session(day, 100.0, 140.0, volume=500.0).between_time("12:00", "16:00")
    df = pd.concat([_history(), frag])
    s10.precompute(df)
    assert s10.generate_signals(df, df) == []


def test_at_most_one_signal_per_session():
    df = pd.concat([_history()] + [_session(d, 100.0, 140.0, volume=500.0)
                                   for d in ("2021-02-15", "2021-02-16")])
    s10.precompute(df)
    sigs = s10.generate_signals(df, df)
    dates = [sg.market_context["date"] for sg in sigs]
    assert sorted(dates) == ["2021-02-15", "2021-02-16"] and len(set(dates)) == len(dates)


def test_frozen_constants_match_the_spec():
    assert s10.DECISION_TIME == "14:00" and s10.TIME_EXIT == "15:55"
    assert s10.PARTICIPATION_FRACTION == 1.00 and s10.STOP_FRACTION == 0.50
    assert s10.TARGET_R_MULTIPLE == 1.50 and s10.TRAILING_SESSIONS == 20
    assert "frozen 2026-09-16" in s10.STRATEGY_VERSION
    spec = Path(__file__).resolve().parent.parent / s10.SPEC_PATH
    assert spec.exists()
    txt = spec.read_text()
    for token in ("14:00", "15:55", "0.50", "1.5R", "ASSUMED", "OPTIMISTIC", "1.300 pt", "NOT SLOW"):
        assert token in txt


def test_registered_in_the_paper_loop():
    import bot_stack_paper_run as bpr
    assert "s010" in bpr.STRATEGIES and bpr.STRATEGY_MODULES["s010"] is s10
    assert "s010" not in bpr.PLUMBING_KEYS
