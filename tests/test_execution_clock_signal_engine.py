"""
test_execution_clock_signal_engine.py
========================================
Tests for the Execution Clock signal engine (queue item 1b,
src/execution_clock_signal_engine.py, src/execution_clock_check_1_2.py).

Unit tests use small synthetic frames (no dependency on real price data
being present, matching this project's convention for pure-logic tests
-- e.g. tests/test_larry_validate.py). One integration-style test runs
the real comparison harness against whatever real price data is on disk
and is skipped (not failed) if none is available, since data presence
is an environment fact, not a code defect.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import execution_clock_signal_engine as engine  # noqa: E402


# ---------------------------------------------------------------------------
# generate_signals_walkforward -- synthetic states, no file I/O
# ---------------------------------------------------------------------------

def _make_states(values, start="2024-01-01"):
    """A minimal states-like frame with a business-day `date` column and
    the state variable engine.VAR, shaped like extend_state_frame's
    reset_index() output."""
    dates = pd.bdate_range(start=start, periods=len(values))
    return pd.DataFrame({"date": dates.date, engine.VAR: values})


def _edges_labels():
    # Frozen-style tercile edges: LOW is anything < 0, everything else
    # falls in mid/high. Mirrors compute_bin_edges' shape (list of edges,
    # -inf/+inf capped) without depending on real Discovery data.
    return [-np.inf, 0.0, 1.0, np.inf], ["low", "mid", "high"]


def _fake_df_with_all_bars(states):
    """A tiny 1-min-bar-shaped frame with a bar at engine.EXECUTION_TIME_NY
    on every date in `states` -- so entry/exit bar-existence checks all
    come back True."""
    idx = pd.DatetimeIndex([
        pd.Timestamp(f"{d} {engine.EXECUTION_TIME_NY}", tz=engine.EXECUTION_TZ)
        for d in states["date"]
    ])
    return pd.DataFrame({"Close": 100.0}, index=idx)


def test_fires_on_every_low_day_and_only_low_days():
    # low, mid, low, high, low -- horizon long enough that none resolve
    states = _make_states([-1.0, 0.5, -2.0, 5.0, -0.5])
    bin_edges, labels = _edges_labels()
    df = _fake_df_with_all_bars(states)
    signals = engine.generate_signals_walkforward(states, df, bin_edges, labels)
    fired_on = [s["entry_row_idx"] for s in signals]
    assert fired_on == [0, 2, 4]


def test_exactly_once_per_signal_no_duplicates():
    states = _make_states([-1.0] * 5)  # every day qualifies
    bin_edges, labels = _edges_labels()
    df = _fake_df_with_all_bars(states)
    signals = engine.generate_signals_walkforward(states, df, bin_edges, labels)
    audit = engine.audit_signals(signals)
    assert audit["n_signals"] == 5
    assert audit["n_unique_signal_dates"] == 5
    assert audit["no_duplicate_signal_dates"] is True


def test_walkforward_uses_only_same_day_value_no_lookahead():
    """A day's signal/no-signal decision must not change depending on
    what comes AFTER it in the sequence -- process a prefix and the full
    series and confirm the prefix's own decisions are identical."""
    values = [-1.0, 0.5, -2.0, 5.0, -0.5, 10.0, -3.0]
    bin_edges, labels = _edges_labels()

    full_states = _make_states(values)
    full_df = _fake_df_with_all_bars(full_states)
    full_signals = engine.generate_signals_walkforward(full_states, full_df, bin_edges, labels)
    full_fired = {s["entry_row_idx"] for s in full_signals if s["entry_row_idx"] < 4}

    prefix_states = _make_states(values[:4])
    prefix_df = _fake_df_with_all_bars(prefix_states)
    prefix_signals = engine.generate_signals_walkforward(prefix_states, prefix_df, bin_edges, labels)
    prefix_fired = {s["entry_row_idx"] for s in prefix_signals}

    assert full_fired == prefix_fired


def test_entry_and_exit_timestamps_use_frozen_execution_time_and_tz():
    states = _make_states([-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    bin_edges, labels = _edges_labels()
    df = _fake_df_with_all_bars(states)
    signals = engine.generate_signals_walkforward(states, df, bin_edges, labels)
    assert len(signals) == 1
    s = signals[0]
    assert s["horizon_days"] == engine.HORIZON_DAYS
    # entry_timestamp is stored via .isoformat(), which round-trips as a
    # fixed UTC offset rather than the original IANA zone name -- assert
    # on the wall-clock time (the frozen convention's actual content)
    # rather than re-parsing back to "America/New_York" specifically.
    entry_ts = pd.Timestamp(s["entry_timestamp"])
    assert entry_ts.tzinfo is not None
    assert (entry_ts.hour, entry_ts.minute, entry_ts.second) == (15, 58, 0)
    assert s["entry_bar_exists"] is True
    if s["resolved"]:
        exit_ts = pd.Timestamp(s["exit_timestamp"])
        assert (exit_ts.hour, exit_ts.minute, exit_ts.second) == (15, 58, 0)


def test_missing_execution_bar_is_flagged_not_silently_skipped():
    """If a signal day (or its exit day) has no bar at the frozen
    timestamp, the engine must still record the signal -- and mark the
    bar missing -- rather than silently dropping it or inventing a
    substitute timestamp (binding Integrity Gate guardrail)."""
    states = _make_states([-1.0] + [0.5] * 10)
    bin_edges, labels = _edges_labels()
    df = _fake_df_with_all_bars(states)
    # Remove the entry day's 15:58:00 bar to simulate a holiday/early close.
    signal_date = states["date"].iloc[0]
    df = df[~(df.index.date == signal_date)]

    signals = engine.generate_signals_walkforward(states, df, bin_edges, labels)
    assert len(signals) == 1
    assert signals[0]["entry_bar_exists"] is False

    audit = engine.audit_signals(signals)
    assert audit["n_entry_bar_missing"] == 1
    assert str(signal_date) in audit["entry_bar_missing_dates"]


def test_unresolved_signal_near_end_of_data_has_no_exit_fields():
    """A signal whose horizon has not yet elapsed (not enough forward
    data) must be recorded as unresolved, not given a fabricated exit."""
    states = _make_states([-1.0] * 3)  # horizon_days (10) exceeds available rows
    bin_edges, labels = _edges_labels()
    df = _fake_df_with_all_bars(states)
    signals = engine.generate_signals_walkforward(states, df, bin_edges, labels)
    assert len(signals) == 3
    for s in signals:
        assert s["resolved"] is False
        assert s["exit_date"] is None
        assert s["exit_timestamp"] is None


def test_audit_signals_flags_duplicates_if_present():
    """audit_signals() itself must be able to catch a duplicate -- proven
    directly, not just trusted, per this project's testing convention
    (e.g. test_ops_checks.py: every check must be provably able to fail)."""
    signals = [
        {"signal_date": "2024-01-02", "entry_bar_exists": True, "exit_bar_exists": True, "resolved": True},
        {"signal_date": "2024-01-02", "entry_bar_exists": True, "exit_bar_exists": True, "resolved": True},
    ]
    audit = engine.audit_signals(signals)
    assert audit["no_duplicate_signal_dates"] is False
    assert audit["n_signals"] == 2
    assert audit["n_unique_signal_dates"] == 1


# ---------------------------------------------------------------------------
# Integration: engine vs. the forward validator's own logic, on real data
# ---------------------------------------------------------------------------

def test_engine_matches_forward_validator_style_recomputation_on_real_data():
    """Check 2: the walk-forward engine's signal days must exactly match
    a second, independent recomputation of forward_validate_h118_daily.py's
    own per-day signal test, over every day real price data covers. Does
    NOT call forward_validate_h118_daily.main() and never touches
    h118_forward_log.jsonl. Skipped (not failed) if no real data is on
    disk in this environment."""
    try:
        import execution_clock_check_1_2 as harness
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"comparison harness unavailable: {exc}")

    try:
        df, all_states, bin_edges, labels = engine.load_states_and_frozen_edges()
    except (FileNotFoundError, RuntimeError) as exc:
        pytest.skip(f"real price data unavailable in this environment: {exc}")

    engine_signals = engine.generate_signals_walkforward(all_states, df, bin_edges, labels)
    engine_audit = engine.audit_signals(engine_signals)
    engine_dates = {s["signal_date"] for s in engine_signals}

    validator_dates = harness.forward_validator_style_signal_dates(all_states, bin_edges, labels)

    assert engine_audit["no_duplicate_signal_dates"] is True
    assert engine_dates == validator_dates
    assert len(engine_dates) > 0
