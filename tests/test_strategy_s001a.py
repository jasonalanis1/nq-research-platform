"""S001a (S001 restricted to PRIOR-DAY levels): identical to S001 on a prior-day-level
sweep; NO trade when the session's first confirmed sweep is of a pre-market level;
frozen constants match the spec; registered in the paper loop under 's001a'."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import strategy_s001_level_sweep_reversal as s1  # noqa: E402
import strategy_s001a_level_sweep_reversal_prior_day as s1a  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_strategy_s001 import _history, _day  # noqa: E402


def _history_premarket_extreme(sweep_low: float, n_days: int = 30):
    """Like _history(narrow_last=True) but the last day's PRE-MARKET makes a lower low
    than yesterday's low, so SUPPORT's source is premarket_low; the sweep goes below it."""
    days = pd.bdate_range("2021-01-04", periods=n_days)
    frames = []
    for i, d in enumerate(days):
        rng = 2.0 if i == n_days - 2 else 40.0
        f = _day(d.date(), 1000.0, rng, ("long", sweep_low) if i == n_days - 1 else None)
        if i == n_days - 1:
            t = pd.Timestamp(f"{d.date()} 05:00", tz="America/New_York")
            f.loc[t, "Low"] = 995.0          # pre-market low 995 < prior-day low 999
        frames.append(f)
    return pd.concat(frames), days[-1].date()


def test_prior_day_level_sweep_is_s001s_trade_relabelled():
    hist, last = _history(narrow_last=True, sweep=("long", 990.0))   # support = prior-day low 999
    day = hist[hist.index.date == last]
    a = s1a.generate_signals(day, history=hist)
    b = s1.generate_signals(day, history=hist)
    assert len(a) == 1 and len(b) == 1
    assert (a[0].direction, a[0].entry, a[0].stop, a[0].target, a[0].timestamp) == \
           (b[0].direction, b[0].entry, b[0].stop, b[0].target, b[0].timestamp)
    assert a[0].strategy_name == s1a.STRATEGY_NAME and a[0].market_context["strategy_id"] == "S001a"
    assert a[0].market_context["level_source"] == "prior_day_low"
    assert s1a.audit(a)["pass"]


def test_premarket_level_sweep_is_no_trade_for_s001a_but_a_trade_for_s001():
    hist, last = _history_premarket_extreme(sweep_low=985.0)
    day = hist[hist.index.date == last]
    b = s1.generate_signals(day, history=hist)
    assert len(b) == 1 and b[0].market_context["level_source"] == "premarket_low"
    assert s1a.generate_signals(day, history=hist) == []


def test_no_trade_when_prior_day_not_narrow():
    hist, last = _history(narrow_last=False, sweep=("long", 965.0))
    assert s1a.generate_signals(hist[hist.index.date == last], history=hist) == []


def test_frozen_constants_match_the_spec():
    assert s1a.PRIOR_DAY_SOURCES == ("prior_day_low", "prior_day_high")
    assert s1a.CONFIRMATION_MODE == "close_min_distance" and s1a.TIME_EXIT == "15:55"
    assert "frozen 2026-09-15" in s1a.STRATEGY_VERSION
    spec = Path(__file__).resolve().parent.parent / s1a.SPEC_PATH
    txt = spec.read_text()
    assert spec.exists() and "1.35" in txt and "15:55" in txt and "prior_day_low" in txt and "ASSUMED" in txt


def test_registered_in_the_paper_loop_and_scores(monkeypatch):
    import bot_stack_paper_run as bpr
    assert "s001a" in bpr.STRATEGIES and bpr.STRATEGY_MODULES["s001a"] is s1a
    assert "s001a" not in bpr.PLUMBING_KEYS
    monkeypatch.setattr(bpr, "STRATEGY", "s001a")
    monkeypatch.setattr(bpr, "decision_for", lambda date: {"trade_permission": True, "size_multiplier": 1.0, "permission_reasons": []})
    for k in ("BROKER_REJECT_RATE", "BROKER_PARTIAL_FILL_RATE", "BROKER_DISCONNECT_RATE", "BROKER_LATE_ACK_RATE"):
        monkeypatch.setattr(bpr, k, 0.0)
    hist, last = _history(narrow_last=True, sweep=("long", 990.0))
    row = bpr.run_session(last, hist[hist.index.date == last], [], history=hist)
    assert row["strategy"] == s1a.STRATEGY_NAME and row["outcome"] in ("filled", "partial")
    assert row["bookkeeping"]["exit_reason"] == "target" and row["pnl_usd"] > 0
    assert bpr._journal_dir().name == "s001a"
