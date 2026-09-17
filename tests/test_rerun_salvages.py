"""Tests for src/rerun_salvages.py (Jason's follow-up 1, September 16th 2026).

The single most important property of this tool is that it REFUSES. The
salvages it re-runs were decided on labels the code invented -- menu condition 4
called every post-2021-09-22 session QUIET because the sourced lists stop there.
A rerun computed the same way would look authoritative and be worth nothing,
which is strictly worse than no rerun at all. So: it refuses while coverage is
stale, it refuses when it has no coverage record at all, and it only runs when
every series the menu reads covers every trade date in the salvage's own screen.
"""
import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import rerun_salvages as rs  # noqa: E402


# --------------------------------------------------------------------------
# the refusal
# --------------------------------------------------------------------------
def test_it_refuses_while_the_macro_calendar_is_stale():
    """S009's screen has 4 trades after 2021-09-22 (the honest macro coverage
    end = MIN across FOMC/CPI/NFP). They are what got labelled QUIET."""
    with pytest.raises(rs.CoverageStale) as e:
        rs.require_current("S009", vxn_end=date(2026, 9, 2), macro_end=date(2021, 9, 22))
    msg = str(e.value)
    assert "REFUSING" in msg
    assert "S009" in msg
    assert "data_topup_macro_calendar.py" in msg


def test_the_refusal_names_how_many_trades_are_uncovered_and_the_first_one():
    chk = rs.coverage_check("S009", vxn_end=date(2026, 9, 2), macro_end=date(2021, 9, 22))
    assert chk["ok"] is False
    assert chk["stale_series"] == ["CPI", "FOMC", "NFP"]
    assert chk["series"]["FOMC"]["uncovered_trades"] == 4
    assert chk["series"]["FOMC"]["first_uncovered"] == "2021-09-23"
    assert chk["series"]["VXN"]["ok"] is True          # condition 1 was never corrupted


def test_s007_is_stale_on_the_calendar_only_with_six_uncovered_trades():
    chk = rs.coverage_check("S007", vxn_end=date(2026, 9, 2), macro_end=date(2021, 9, 22))
    assert chk["series"]["CPI"]["uncovered_trades"] == 6
    assert chk["series"]["VXN"]["ok"] is True


def test_missing_coverage_is_treated_as_covering_nothing():
    """FAIL CLOSED: no coverage record is not evidence of currency."""
    chk = rs.coverage_check("S009", vxn_end=None, macro_end=None)
    assert chk["ok"] is False
    assert set(chk["stale_series"]) == {"CPI", "FOMC", "NFP", "VXN"}
    with pytest.raises(rs.CoverageStale):
        rs.require_current("S009", vxn_end=None, macro_end=None)


def test_rerun_one_refuses_before_touching_anything(monkeypatch):
    called = []
    monkeypatch.setattr(rs, "require_current",
                        lambda sid, **kw: (_ for _ in ()).throw(rs.CoverageStale("stale")))
    import salvage_check as sc
    monkeypatch.setattr(sc, "run", lambda *a, **k: called.append(1))
    with pytest.raises(rs.CoverageStale):
        rs.rerun_one("S009")
    assert called == []


def test_the_cli_exits_nonzero_and_writes_nothing_while_coverage_is_stale(capsys):
    rc = rs.main([])
    out = capsys.readouterr().out
    assert rc == 2
    assert "REFUSING TO RUN" in out
    assert not list((Path(rs.DATA_DIR)).glob("salvage_*_rerun_*.json"))


# --------------------------------------------------------------------------
# it runs once coverage genuinely reaches the trades
# --------------------------------------------------------------------------
def test_it_accepts_once_the_calendar_reaches_past_the_last_trade():
    chk = rs.require_current("S009", vxn_end=date(2026, 9, 30), macro_end=date(2026, 12, 31))
    assert chk["ok"] is True
    assert all(r["ok"] for r in chk["series"].values())


def test_what_is_owed_comes_from_the_registry_not_from_this_module():
    rows = [{"ts": "2026-09-17T00:00:00+00:00", "strategy_id": "S009", "name": "x",
             "stage": "SUPERSEDED", "supersedes": "y", "blocked_by": ["FOMC"]},
            {"ts": "2026-09-17T00:00:01+00:00", "strategy_id": "S007", "name": "x",
             "stage": "SUPERSEDED", "supersedes": "y", "blocked_by": ["FOMC"]},
            {"ts": "2026-09-18T00:00:00+00:00", "strategy_id": "S007", "name": "x",
             "stage": "SALVAGE", "verdict": "rerun of record"}]
    assert rs.owed(rows) == ["S009"]          # S007 already has its rerun
    assert rs.owed([]) == []


def test_a_kill_whose_first_salvage_never_ran_is_owed_too():
    """S004 was KILLED on 2026-09-17 before paper entry and its MANDATORY s.7
    salvage was BLOCKED by the reference-data gate, so it was never run at all --
    not superseded, just never done. That is owed for the same reason a rerun is
    owed and is refused for the same reason, so it goes through the same door."""
    rows = [{"ts": "2026-09-17T04:00:00+00:00", "strategy_id": "S004", "name": "x",
             "stage": "KILL", "verdict": "KILL -- margin does not survive overlap correction"}]
    assert rs.owed(rows) == ["S004"]
    # ...and stops being owed the moment its salvage is recorded
    rows2 = rows + [{"ts": "2026-09-18T00:00:00+00:00", "strategy_id": "S004", "name": "x",
                     "stage": "SALVAGE", "verdict": "nothing taken"}]
    assert rs.owed(rows2) == []


def test_a_kill_this_module_has_no_inputs_for_is_left_out_not_guessed():
    rows = [{"ts": "2026-09-17T04:00:00+00:00", "strategy_id": "S999", "name": "x",
             "stage": "KILL", "verdict": "KILL"}]
    assert rs.owed(rows) == []


def test_s004s_trades_are_read_from_the_two_arm_screen_file():
    """S004's screen output nests its trades under 'strategy' (it has two arms).
    The owed salvage must read the STRATEGY arm, never the baseline null."""
    trades = rs.screen_trades("S004")
    assert len(trades) == 554
    dates = rs.trade_dates("S004")
    assert dates[0] == date(2015, 2, 9) and dates[-1] == date(2021, 9, 15)


# --------------------------------------------------------------------------
# re-deciding the spawn (directive s.7)
# --------------------------------------------------------------------------
def _cond(label, side, net, n=100):
    return {"condition": label, "side": side, "net_usd_1": net, "n": n, "avg_r_net": 0.05,
            "win_rate": 0.5, "profitable": True, "thin": False, "positive_but_thin": False}


def test_an_ex_post_only_condition_cannot_carry_a_spawn():
    """Menu condition 2 measures the session's OWN range -- a filter nobody
    could have applied at 09:30. Refused out loud, not silently dropped."""
    res = {"profitable_conditions": [
        _cond("2. trend vs range: the day's own RTH range vs trailing-20 average", "TREND", 5000.0)]}
    d = rs.redecide_spawn(res, "S00Xa")
    assert d["spawn"] is False
    assert "NOTHING TAKEN" in d["verdict"]
    assert d["refused"] and "EX-POST ONLY" in d["refused"][0]["refused_because"]


def test_one_salvage_per_strategy_takes_exactly_one_condition():
    res = {"profitable_conditions": [
        _cond("1. volatility: VXN vs trailing (HIGH > trailing, LOW <= trailing)", "LOW", 400.0),
        _cond("4. scheduled-news day (FOMC / CPI / NFP) vs quiet", "QUIET", 900.0),
        _cond("2. trend vs range: the day's own RTH range vs trailing-20 average", "TREND", 9999.0)]}
    d = rs.redecide_spawn(res, "S009a")
    assert d["spawn"] is True
    assert d["taken"]["side"] == "QUIET"          # best EX-ANTE condition, not the ex-post one
    assert len(d["not_taken"]) == 1
    assert d["refused"][0]["side"] == "TREND"


def test_an_unlisted_spec_named_field_is_refused_rather_than_assumed_tradeable():
    res = {"profitable_conditions": [_cond("spec-named: exit_reason", "target", 800.0)]}
    d = rs.redecide_spawn(res, "S00Xa")
    assert d["spawn"] is False
    assert "whitelist" in d["refused"][0]["refused_because"]


def test_a_whitelisted_spec_named_field_may_carry_a_spawn():
    res = {"profitable_conditions": [_cond("spec-named: level_source", "prior_day_low", 426.74, n=17)]}
    d = rs.redecide_spawn(res, "S001a")
    assert d["spawn"] is True and d["taken"]["side"] == "prior_day_low"


def test_nothing_profitable_means_nothing_spawned():
    d = rs.redecide_spawn({"profitable_conditions": []}, "S009a")
    assert d["spawn"] is False and d["taken"] is None
    assert "stays KILLED" in d["verdict"]
