"""S004, the H118 VWAP-distance drift lineage measured against NQ's OWN drift --
the frozen trade's mechanics on synthetic bars: the FROZEN Discovery tercile edges,
the signal-session/entry-session split (no look-ahead), the 09:30 entry, the exact
ten-session hold declared as an absolute exit_ts, the 4.0 x atr14 disaster cap, the
absent target, one trade per session, the deferred-exit placeholder, and the
own-drift baseline arm that removes ONLY the tercile filter."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import strategy_s004_vwap_dist_low_drift as s4  # noqa: E402


def _session(day: str, open_px: float, close_px: float, width: float = 10.0,
             volume: float = 1000.0) -> pd.DataFrame:
    """09:30 -> 16:00, one bar a minute, drifting linearly from open to close."""
    idx = pd.date_range(f"{day} 09:30", f"{day} 16:00", freq="min", tz="America/New_York")
    px = np.linspace(open_px, close_px, len(idx))
    return pd.DataFrame({"Open": px, "Close": px,
                         "High": px + width / 2.0, "Low": px - width / 2.0,
                         "Volume": volume}, index=idx)


def _history(n: int = 30, start: str = "2021-01-04") -> pd.DataFrame:
    """Flat sessions: close == session VWAP, so vwap_dist_vs_atr ~ 0 -> MID bucket,
    which never fires. Gives atr14 a full window."""
    days = pd.bdate_range(start, periods=n)
    return pd.concat([_session(d.strftime("%Y-%m-%d"), 100.0, 100.0) for d in days])


def test_frozen_discovery_tercile_edges_are_hardcoded_and_never_refit():
    # H118's published Discovery edges (data/study_vwap_dist_low_10d_drift_h118_results.json)
    assert s4.LOW_EDGE == -0.04604781358468863
    assert s4.MID_EDGE == 0.14705460626358577
    assert s4.bucket_for(-1.0) == "low" and s4.bucket_for(s4.LOW_EDGE) == "low"
    assert s4.bucket_for(0.0) == "mid" and s4.bucket_for(1.0) == "high"
    assert s4.bucket_for(None) is None and s4.bucket_for(float("nan")) is None


def test_reads_no_reference_data():
    """S004's entry, stop and exit are price-only: no VXN, no macro calendar. Checked
    on the module's CODE (comments and docstrings stripped), which is what executes."""
    import io, tokenize
    src = Path(s4.__file__).read_text()
    code = []
    prev_end = (1, 0)
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.COMMENT, tokenize.STRING) or tok.string.strip() == "":
            continue
        code.append(tok.string)
    code = " ".join(code)
    for forbidden in ("VXN", "vxn", "macro_event_calendar", "reference_data",
                      "extend_state_frame", "FOMC", "NFP", "CPI"):
        assert forbidden not in code, forbidden


def _fire_case():
    """A session that closes far BELOW its own VWAP -> LOW tercile -> the NEXT
    session is the entry session."""
    hist = _history(30)
    signal_day = _session("2021-02-15", 100.0, 40.0)      # closes far under the session VWAP
    tail = pd.concat([_session(d.strftime("%Y-%m-%d"), 100.0, 100.0)
                      for d in pd.bdate_range("2021-02-16", periods=15)])
    return pd.concat([hist, signal_day, tail])


def test_signal_fires_on_the_session_after_the_low_close_and_never_on_it():
    df = _fire_case()
    s4.precompute(df)
    sigs = s4.generate_signals(df, df)
    dates = [sg.market_context["date"] for sg in sigs]
    assert "2021-02-15" not in dates                  # the signal session is never the entry session
    assert "2021-02-16" in dates
    sg = [x for x in sigs if x.market_context["date"] == "2021-02-16"][0]
    assert sg.market_context["signal_session"] == "2021-02-15"
    assert sg.direction == "long" and sg.instrument == "MNQ"
    assert pd.Timestamp(sg.timestamp).strftime("%H:%M") == "09:30"
    entry_bar = df.loc[df.index.date == pd.Timestamp("2021-02-16").date()].between_time("09:30", "09:30")
    assert sg.entry == float(entry_bar["Open"].iloc[0])      # the entry IS that bar's open


def test_hold_is_exactly_ten_rth_sessions_and_the_exit_is_absolute():
    df = _fire_case()
    s4.precompute(df)
    sg = [x for x in s4.generate_signals(df, df) if x.market_context["date"] == "2021-02-16"][0]
    rth = s4._PRE["rth_dates"]
    i = s4._PRE["rth_index"][pd.Timestamp("2021-02-16").date()]
    assert sg.market_context["hold_sessions"] == 10
    assert sg.market_context["exit_session_known"] is True
    assert pd.Timestamp(sg.market_context["exit_ts"]).date() == rth[i + 10]
    assert pd.Timestamp(sg.market_context["exit_ts"]).strftime("%H:%M") == "09:30"
    assert pd.Timestamp(sg.market_context["exit_ts"]) > pd.Timestamp(sg.timestamp)


def test_stop_is_four_atr14_and_there_is_no_target():
    df = _fire_case()
    s4.precompute(df)
    sg = [x for x in s4.generate_signals(df, df) if x.market_context["date"] == "2021-02-16"][0]
    atr = float(s4._PRE["atr14"].get(pd.Timestamp("2021-02-16").date()))
    assert sg.stop == round(sg.entry - 4.0 * atr, 4) and sg.stop < sg.entry
    assert sg.market_context["atr14"] == round(atr, 4)
    assert sg.target - sg.entry == s4.NO_TARGET_PTS          # unreachable sentinel


def test_one_signal_a_session_and_the_audit_passes():
    df = _fire_case()
    s4.precompute(df)
    sigs = s4.generate_signals(df, df)
    a = s4.audit(sigs)
    assert a["multi_signal_sessions"] == 0 and a["entries_off_clock"] == 0
    assert a["exits_not_after_entry"] == 0 and a["stops_not_below_entry"] == 0
    assert a["signals_outside_frozen_low_tercile"] == 0 and a["pass"] is True


def test_an_unknown_exit_session_gets_a_placeholder_the_loop_refuses():
    """Data that ends before the tenth session forward: the signal still fires with
    a placeholder exit the cross-session guard rejects -- it can never book."""
    import bot_stack_paper_run as bpr
    hist = _history(30)
    signal_day = _session("2021-02-15", 100.0, 40.0)
    short_tail = pd.concat([_session(d.strftime("%Y-%m-%d"), 100.0, 100.0)
                            for d in pd.bdate_range("2021-02-16", periods=3)])
    df = pd.concat([hist, signal_day, short_tail])
    s4.precompute(df)
    sg = [x for x in s4.generate_signals(df, df) if x.market_context["date"] == "2021-02-16"][0]
    assert sg.market_context["exit_session_known"] is False
    ready, why = bpr.cross_session_exit_ready(df, bpr.cross_session_exit_ts(sg))
    assert ready is False and why


def test_the_baseline_arm_removes_only_the_tercile_filter():
    df = _fire_case()
    s4.precompute(df)
    filtered = {x.market_context["date"] for x in s4.generate_signals(df, df)}
    s4.UNCONDITIONAL_BASELINE = True
    try:
        s4._PRE.clear()
        s4.precompute(df)
        base = s4.generate_signals(df, df)
        base_dates = {x.market_context["date"] for x in base}
    finally:
        s4.UNCONDITIONAL_BASELINE = False
        s4._PRE.clear()
    assert filtered < base_dates                     # strictly more sessions, same trade
    assert all(x.market_context["baseline_arm"] is True for x in base)
    assert all(x.market_context["hold_sessions"] == 10 for x in base)
    assert all(x.direction == "long" for x in base)


def test_registered_in_the_paper_loop_but_not_scored_while_the_gate_blocks():
    """S004 passed SCREEN, so it is registered under 's004' and can enter PAPER the
    first cycle reference-data coverage is current. Registration is not entry: the
    registry's stage of record is BLOCKED_PENDING_REFERENCE_DATA, not PAPER."""
    import bot_stack_paper_run as bpr
    import strategy_registry as sr
    assert "s004" in bpr.STRATEGIES
    assert bpr.STRATEGIES["s004"][0] == s4.STRATEGY_NAME
    assert "s004" not in bpr.PLUMBING_KEYS
    latest = sr.latest(sr.read_rows()).get("S004")
    assert latest is not None and latest["stage"] != "PAPER"
