"""S009, afternoon VWAP-completion continuation -- the frozen trade's mechanics on
synthetic bars: the |D| >= 0.30 x RNG condition, sign(D) continuation, the
0.50 x RNG stop, the 1.5R target, the 15:55 flat, and no look-ahead."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import strategy_s009_vwap_completion_continuation as s9  # noqa: E402


def _session(day: str, open_px: float, close_1330: float, width: float = 4.0) -> pd.DataFrame:
    """09:30 -> 16:00, one bar a minute, drifting linearly from the open to the
    13:30 close and flat after, with a fixed high/low envelope of `width`."""
    idx = pd.date_range(f"{day} 09:30", f"{day} 16:00", freq="min", tz="America/New_York")
    n1330 = int(np.searchsorted(idx, pd.Timestamp(f"{day} 13:30", tz="America/New_York")))
    px = np.empty(len(idx))
    px[: n1330 + 1] = np.linspace(open_px, close_1330, n1330 + 1)
    px[n1330 + 1:] = close_1330
    return pd.DataFrame({"Open": px, "Close": px,
                         "High": px + width / 2.0, "Low": px - width / 2.0,
                         "Volume": 1000.0}, index=idx)


def test_a_trending_session_is_dislocated_and_fires_long():
    """A session that rises steadily from 09:30 to 13:30 ends far above its own
    VWAP (the average of the path), so |D| clears 0.30 x RNG and it fires long."""
    df = _session("2021-02-15", 100.0, 140.0)
    sigs = s9.generate_signals(df, df)
    assert len(sigs) == 1
    sg = sigs[0]
    assert sg.direction == "long"                       # sign(D), continuation
    assert sg.market_context["dislocation_points"] > 0
    assert sg.instrument == "MNQ" and sg.market_context["time_exit"] == "15:55"
    assert round(sg.risk_multiple, 2) == s9.TARGET_R_MULTIPLE
    assert s9.audit(sigs)["pass"]


def test_direction_is_continuation_not_a_fade():
    df = _session("2021-02-15", 140.0, 100.0)
    sg = s9.generate_signals(df, df)[0]
    assert sg.direction == "short" and sg.market_context["dislocation_points"] < 0
    assert sg.stop > sg.entry and sg.target < sg.entry


def test_flat_session_does_not_fire():
    """No dislocation from VWAP -> no trade, however complete the session."""
    df = _session("2021-02-15", 100.0, 100.0)
    assert s9.generate_signals(df, df) == []


def test_stop_is_half_the_window_range_and_target_is_1_5R():
    df = _session("2021-02-15", 100.0, 140.0)
    sg = s9.generate_signals(df, df)[0]
    rng = sg.market_context["session_range"]
    risk = abs(sg.entry - sg.stop)
    assert abs(risk - s9.STOP_FRACTION * rng) < 1e-9
    assert abs(abs(sg.target - sg.entry) - s9.TARGET_R_MULTIPLE * risk) < 1e-6


def test_no_lookahead_entry_is_the_first_bar_after_the_decision():
    df = _session("2021-02-15", 100.0, 140.0)
    sg = s9.generate_signals(df, df)[0]
    decision = pd.Timestamp(sg.market_context["decision_time"])
    assert decision.strftime("%H:%M") == s9.DECISION_TIME
    assert pd.Timestamp(sg.timestamp) > decision
    assert pd.Timestamp(sg.timestamp).strftime("%H:%M") == "13:31"
    # the fill price is that bar's OPEN, never a later bar
    assert sg.entry == float(df.loc[pd.Timestamp(sg.timestamp), "Open"])


def test_session_fragment_is_skipped():
    """A session missing its 09:30 open bar or its 13:30 bar is not traded."""
    df = _session("2021-02-15", 100.0, 140.0)
    frag = df[df.index >= pd.Timestamp("2021-02-15 11:00", tz="America/New_York")]
    assert s9.generate_signals(frag, frag) == []


def test_zero_volume_session_is_skipped():
    df = _session("2021-02-15", 100.0, 140.0).assign(Volume=0.0)
    assert s9.generate_signals(df, df) == []


def test_one_trade_per_session_across_several_days():
    days = ["2021-02-15", "2021-02-16", "2021-02-17"]
    df = pd.concat([_session(d, 100.0, 140.0) for d in days])
    sigs = s9.generate_signals(df, df)
    assert [sg.market_context["date"] for sg in sigs] == days
    assert s9.audit(sigs)["pass"]
