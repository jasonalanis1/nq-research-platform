"""S011, the hyp-000152 / M18 daily reversal built as a whole trade and measured
against NQ's OWN next-session drift -- the frozen trade's mechanics on synthetic
bars: the signal-session/entry-session split (no look-ahead), the 09:30 entry,
the FADE direction, the same-session 15:55 exit with NO cross-session exit_ts,
the 2.0 x atr14 disaster cap, the absent target, one trade per session, the
absence of any volume decision (hyp-000152's not_retest line), and the own-drift
baseline arm that forces LONG and changes nothing else."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import strategy_s011_daily_reversal_vs_own_drift as s11  # noqa: E402


def _session(day: str, open_px: float, close_px: float, width: float = 10.0,
             volume: float = 1000.0) -> pd.DataFrame:
    idx = pd.date_range(f"{day} 09:30", f"{day} 16:00", freq="min", tz="America/New_York")
    px = np.linspace(open_px, close_px, len(idx))
    return pd.DataFrame({"Open": px, "Close": px,
                         "High": px + width / 2.0, "Low": px - width / 2.0,
                         "Volume": volume}, index=idx)


def _history(n: int = 30, start: str = "2021-01-04") -> pd.DataFrame:
    days = pd.bdate_range(start, periods=n)
    return pd.concat([_session(d.strftime("%Y-%m-%d"), 100.0, 100.0) for d in days])


def _case(signal_open: float, signal_close: float, volume: float = 1000.0):
    hist = _history(30)
    sig = _session("2021-02-15", signal_open, signal_close, volume=volume)
    entry = _session("2021-02-16", 100.0, 100.0)
    df = pd.concat([hist, sig, entry])
    s11._PRE.clear()
    return df


def _sig_on(df, day: str):
    s11.precompute(df)
    g = df[df.index.date == pd.Timestamp(day).date()]
    return s11.signals_for_day(pd.Timestamp(day).date(), g, df)


def test_reads_no_reference_data():
    """Price-only: no VXN, no macro calendar. Checked on the module's CODE
    (comments and strings stripped), which is what executes."""
    import io, tokenize
    src = Path(s11.__file__).read_text()
    code = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.COMMENT, tokenize.STRING) or tok.string.strip() == "":
            continue
        code.append(tok.string)
    code = " ".join(code)
    for forbidden in ("VXN", "vxn", "macro_event_calendar", "reference_data",
                      "extend_state_frame", "FOMC", "NFP", "CPI"):
        assert forbidden not in code, forbidden


def test_up_session_is_faded_short_on_the_next_session_and_never_on_itself():
    df = _case(100.0, 140.0)
    assert _sig_on(df, "2021-02-15") == [] or all(
        s.market_context["signal_session"] != "2021-02-15" for s in _sig_on(df, "2021-02-15"))
    sigs = _sig_on(df, "2021-02-16")
    assert len(sigs) == 1
    s = sigs[0]
    assert s.direction == "short"
    assert s.market_context["signal_session"] == "2021-02-15"
    assert s.market_context["date"] == "2021-02-16"
    assert pd.Timestamp(s.timestamp).strftime("%H:%M") == "09:30"
    assert s.entry == 100.0                      # the 09:30 bar's OPEN of the entry session
    assert s.stop > s.entry                      # short: stop above
    assert s.target < s.entry - 100_000          # unreachable sentinel, no target


def test_down_session_is_faded_long():
    df = _case(140.0, 100.0)
    s = _sig_on(df, "2021-02-16")[0]
    assert s.direction == "long"
    assert s.stop < s.entry and s.target > s.entry + 100_000


def test_flat_session_gives_no_side_to_fade():
    df = _case(100.0, 100.0)
    assert _sig_on(df, "2021-02-16") == []


def test_stop_is_two_atr14_and_the_exit_is_same_session_with_no_exit_ts():
    df = _case(100.0, 140.0)
    s = _sig_on(df, "2021-02-16")[0]
    atr = s.market_context["atr14"]          # rounded to 4dp in the context dict
    assert abs(abs(s.stop - s.entry) - 2.0 * atr) < 1e-3
    assert abs(s.market_context["risk_points"] - 2.0 * atr) < 1e-3
    assert s.market_context["time_exit"] == "15:55"
    assert "exit_ts" not in s.market_context     # same-session: never a cross-session hold


def test_volume_is_recorded_but_never_decides():
    """hyp-000152's not_retest line: volume as a gradient on daily reversal is
    closed. Ten-fold volume must not change the signal in any way."""
    quiet = _sig_on(_case(100.0, 140.0, volume=1000.0), "2021-02-16")[0]
    heavy = _sig_on(_case(100.0, 140.0, volume=10000.0), "2021-02-16")[0]
    assert quiet.direction == heavy.direction
    assert (quiet.entry, quiet.stop, quiet.target) == (heavy.entry, heavy.stop, heavy.target)
    assert quiet.market_context["vol_ratio_RECORD_ONLY"] is not None
    assert heavy.market_context["vol_ratio_RECORD_ONLY"] is not None


def test_baseline_arm_forces_long_and_changes_nothing_else():
    df = _case(100.0, 140.0)
    a = _sig_on(df, "2021-02-16")[0]
    s11.BASELINE_ALWAYS_LONG = True
    try:
        s11._PRE.clear()
        b = _sig_on(df, "2021-02-16")[0]
    finally:
        s11.BASELINE_ALWAYS_LONG = False
        s11._PRE.clear()
    assert a.direction == "short" and b.direction == "long"
    assert a.entry == b.entry
    assert abs(abs(b.stop - b.entry) - abs(a.stop - a.entry)) < 1e-9
    assert b.market_context["baseline_arm"] is True
    assert a.market_context["baseline_arm"] is False


def test_one_signal_a_session_and_the_audit_passes():
    df = _case(100.0, 140.0)
    s11.precompute(df)
    sigs = s11.generate_signals(df, df)
    dates = [s.market_context["date"] for s in sigs]
    assert len(dates) == len(set(dates))
    rep = s11.audit(sigs)
    assert rep["pass"], rep
    assert rep["directions_not_faded"] == 0
