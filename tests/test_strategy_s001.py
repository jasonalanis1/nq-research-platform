"""S001 (Level Sweep Reversal on compressed prior days): the frozen module fires
only on prior_day_narrow sessions, enters at the next bar's open, stops at the
sweep extreme, targets 1.35R, exits 15:55, one trade a session, no lookahead."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import strategy_s001_level_sweep_reversal as s1  # noqa: E402


def _day(date, base, rth_range, sweep=None):
    """One synthetic session 04:00-16:00 ET, flat RTH bars spanning `rth_range`
    around `base`; optional (kind, sweep_low_or_high) at 08:35-08:37."""
    idx = pd.date_range(f"{date} 04:00", f"{date} 15:59", freq="min", tz="America/New_York")
    n = len(idx)
    o = np.full(n, base, float); h = o + 0.5; l = o - 0.5; c = o.copy()
    rth = (idx.hour > 9) | ((idx.hour == 9) & (idx.minute >= 30))
    # RTH bars alternate high/low so the RTH range is exactly rth_range
    h[rth] = base + rth_range / 2; l[rth] = base - rth_range / 2
    # pre-market stays inside (base-5, base+5) so the pre-market level is not the extreme
    if sweep:
        kind, extreme = sweep
        t0 = idx.get_loc(pd.Timestamp(f"{date} 08:35", tz="America/New_York"))
        if kind == "long":
            l[t0] = extreme; c[t0] = base - 5;                 # sweep below support, close still below
            c[t0 + 1] = base + 10; h[t0 + 1] = base + 10.5     # confirming bar: close >= support + 5
            o[t0 + 2] = base + 11                              # entry = next bar's open
            h[t0 + 3:t0 + 60] = base + 80                       # rally so the target is hit
        else:
            h[t0] = extreme; c[t0] = base + 5
            c[t0 + 1] = base - 10; l[t0 + 1] = base - 10.5
            o[t0 + 2] = base - 11
            l[t0 + 3:t0 + 60] = base - 80
    return pd.DataFrame({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 100.0}, index=idx)


def _history(narrow_last: bool, sweep=None, n_days=30):
    """n_days of business days; the LAST day's PRIOR day is narrow (range 2) or wide (range 60)
    against 20 prior days of range 40. The last day carries the optional sweep."""
    days = pd.bdate_range("2021-01-04", periods=n_days)
    frames = []
    for i, d in enumerate(days):
        if i == n_days - 2:
            rng = 2.0 if narrow_last else 60.0
        elif i == n_days - 1:
            rng = 40.0
        else:
            rng = 40.0
        frames.append(_day(d.date(), 1000.0, rng, sweep if i == n_days - 1 else None))
    return pd.concat(frames), days[-1].date()


def test_prior_day_narrow_flag_from_history():
    hist, last = _history(narrow_last=True)
    s1.precompute(hist)
    assert s1.prior_day_narrow(last, hist) is True
    hist2, last2 = _history(narrow_last=False)
    assert s1.prior_day_narrow(last2, hist2) is False


def test_no_trade_when_prior_day_not_narrow_even_with_a_sweep():
    # support = prior day's low = 1000 - 30 = 970 ; sweep to 965
    hist, last = _history(narrow_last=False, sweep=("long", 965.0))
    assert s1.generate_signals(hist[hist.index.date == last], history=hist) == []


def test_long_signal_enters_next_bar_open_stops_at_sweep_extreme_targets_1p35R():
    # prior day narrow: range 2 -> support = prior day's low = 999.0; sweep to 990
    hist, last = _history(narrow_last=True, sweep=("long", 990.0))
    day = hist[hist.index.date == last]
    sigs = s1.generate_signals(day, history=hist)
    assert len(sigs) == 1
    s = sigs[0]
    assert s.direction == "long" and s.strategy_name == s1.STRATEGY_NAME
    assert s.stop == 990.0 and s.entry == 1011.0                    # next bar's open
    assert s.target == pytest.approx(1011.0 + 1.35 * 21.0)
    assert s.timestamp == pd.Timestamp(f"{last} 08:37", tz="America/New_York")
    assert pd.Timestamp(s.market_context["trigger_time"]) < s.timestamp   # no lookahead
    assert s.market_context["time_exit"] == "15:55" and s.instrument == "MNQ"
    assert s1.audit(sigs)["pass"]


def test_short_side_mirrors():
    hist, last = _history(narrow_last=True, sweep=("short", 1010.0))
    sigs = s1.generate_signals(hist[hist.index.date == last], history=hist)
    assert len(sigs) == 1 and sigs[0].direction == "short"
    assert sigs[0].stop == 1010.0 and sigs[0].entry == 989.0
    assert sigs[0].target == pytest.approx(989.0 - 1.35 * 21.0)


def test_frozen_constants_match_the_spec():
    assert s1.CONFIRMATION_MODE == "close_min_distance" and s1.TIME_EXIT == "15:55"
    assert "frozen 2026-09-15" in s1.STRATEGY_VERSION
    spec = Path(__file__).resolve().parent.parent / "research" / "infrastructure" / "strategy-specs" / "S001-level-sweep-reversal.md"
    assert spec.exists() and "1.35" in spec.read_text() and "15:55" in spec.read_text()


def test_paper_loop_can_register_and_score_s001(monkeypatch):
    import bot_stack_paper_run as bpr
    bpr.register_strategy("s001_test", s1)
    try:
        monkeypatch.setattr(bpr, "STRATEGY", "s001_test")
        monkeypatch.setattr(bpr, "decision_for", lambda date: {"trade_permission": True, "size_multiplier": 1.0, "permission_reasons": []})
        for k in ("BROKER_REJECT_RATE", "BROKER_PARTIAL_FILL_RATE", "BROKER_DISCONNECT_RATE", "BROKER_LATE_ACK_RATE"):
            monkeypatch.setattr(bpr, k, 0.0)
        hist, last = _history(narrow_last=True, sweep=("long", 990.0))
        row = bpr.run_session(last, hist[hist.index.date == last], [], history=hist)
        assert row["strategy"] == s1.STRATEGY_NAME and row["outcome"] in ("filled", "partial")
        assert row["bookkeeping"]["exit_reason"] == "target" and row["pnl_usd"] > 0
        assert bpr._journal_dir().name == "s001_test"
    finally:
        bpr.STRATEGIES.pop("s001_test", None); bpr.STRATEGY_MODULES.pop("s001_test", None)
