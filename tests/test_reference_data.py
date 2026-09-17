"""Reference-data coverage and the FAIL-CLOSED rule (2026-09-16).

The rule these tests exist to hold: a session past a reference series' coverage
end is REFUSED, never guessed. Fail open is how a stale calendar turns a 2026
paper record into a fiction -- every day "quiet" because the sourced list stops
in 2021, every session carrying the last VXN close that was ever fetched.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import reference_data as rd  # noqa: E402


@pytest.fixture()
def vxn_file(tmp_path):
    p = tmp_path / "vxn.csv"
    p.write_text("observation_date,VXNCLS\n2026-08-31,20.18\n2026-09-01,21.96\n2026-09-02,21.07\n")
    return p


def test_vxn_close_inside_coverage(vxn_file):
    assert rd.vxn_coverage_end(vxn_file) == date(2026, 9, 2)
    assert rd.vxn_close(date(2026, 9, 1), vxn_file) == 21.96
    # a market holiday INSIDE the series still resolves to the last known close
    assert rd.vxn_close(date(2026, 9, 2), vxn_file) == 21.07


def test_vxn_past_coverage_is_refused_not_carried_forward(vxn_file):
    """THE fail-closed test: the session the paper loop would actually score."""
    with pytest.raises(rd.ReferenceDataUnavailable) as e:
        rd.vxn_close(date(2026, 9, 16), vxn_file)
    assert e.value.series == "VXN"
    assert e.value.covered_through == date(2026, 9, 2)
    assert "REFUSING" in str(e.value) and "data_topup_vxn" in str(e.value)


def test_vxn_blank_and_dot_rows_are_skipped(tmp_path):
    p = tmp_path / "v.csv"
    p.write_text("observation_date,VXNCLS\n2026-09-01,21.96\n2026-09-02,.\n2026-09-03,\n")
    assert rd.vxn_coverage_end(p) == date(2026, 9, 1)


# --------------------------------------------------------------------------
# macro calendar
# --------------------------------------------------------------------------
def _extension(tmp_path, rows, covered):
    cal = tmp_path / "macro.csv"
    cal.write_text("date,event,source\n" + "".join(f"{d},{e},test\n" for d, e in rows))
    cov = tmp_path / "macro_cov.json"
    cov.write_text(json.dumps({k: {"covered_through": v} for k, v in covered.items()}))
    return cal, cov


def test_frozen_lists_are_still_the_authority_over_their_own_range():
    from study_fomc_volatility import FOMC_SET
    ev = rd.macro_events()
    assert set(FOMC_SET) <= ev["FOMC"]
    assert rd.is_scheduled_news_day(sorted(FOMC_SET)[0]) is True


def test_a_verified_quiet_day_inside_coverage_is_not_an_error():
    # 2015-01-05 carries no FOMC, CPI or NFP release and sits inside every list
    assert rd.scheduled_events_on(date(2015, 1, 5)) == set()
    assert rd.is_scheduled_news_day(date(2015, 1, 5)) is False


def test_a_day_past_calendar_coverage_raises_instead_of_reading_quiet():
    """The bug this whole module exists for: with lists ending in 2021/2023, a
    2026 date used to come back QUIET. It must now refuse."""
    with pytest.raises(rd.ReferenceDataUnavailable) as e:
        rd.is_scheduled_news_day(date(2026, 9, 16))
    assert "macro calendar" in str(e.value)
    assert "FOMC" in str(e.value)          # names which series ran out and where


def test_coverage_end_is_the_minimum_across_the_three_series(tmp_path):
    cal, cov = _extension(tmp_path, [("2027-01-28", "FOMC")],
                          {"FOMC": "2027-12-31", "CPI": "2026-12-31", "NFP": "2026-11-30"})
    per = rd.macro_coverage_by_event(cal, cov)
    assert per["FOMC"] == date(2027, 12, 31)
    # a day is only honestly "quiet" once EVERY series that could hold an event
    # on it has been checked, so the overall end is the minimum
    assert rd.macro_coverage_end(cal, cov) == date(2026, 11, 30)


def test_extension_extends_coverage_and_classifies_a_2026_session(tmp_path):
    cal, cov = _extension(tmp_path, [("2026-09-16", "FOMC"), ("2026-09-11", "CPI")],
                          {"FOMC": "2026-12-31", "CPI": "2026-12-31", "NFP": "2026-12-31"})
    assert rd.scheduled_events_on(date(2026, 9, 16), cal, cov) == {"FOMC"}
    assert rd.scheduled_events_on(date(2026, 9, 15), cal, cov) == set()   # verified quiet, not a guess
    assert rd.is_scheduled_news_day(date(2026, 9, 11), cal, cov) is True
    # still fails closed past the extension
    with pytest.raises(rd.ReferenceDataUnavailable):
        rd.scheduled_events_on(date(2027, 1, 4), cal, cov)


def test_missing_sidecar_falls_back_to_the_frozen_lists_conservatively(tmp_path):
    cal = tmp_path / "none.csv"
    cov = tmp_path / "none.json"
    end = rd.macro_coverage_end(cal, cov)
    from study_fomc_volatility import FOMC_SET
    assert end == max(FOMC_SET)      # refuses MORE, never less


# --------------------------------------------------------------------------
# the coverage state the cycle reads
# --------------------------------------------------------------------------
def test_coverage_state_names_every_series_its_consumers_and_its_updater():
    st = rd.coverage()
    assert set(st["series"]) == {"VXN", "FOMC", "CPI", "NFP"}
    for name, rec in st["series"].items():
        assert rec["consumers"] and rec["updater"] and rec["source"]
    assert "salvage_check" in " ".join(st["series"]["FOMC"]["consumers"])
    assert isinstance(st["stale_series"], list)
    assert st["ok"] == (not st["stale_series"])


def test_plain_lines_flag_stale_series_and_state_the_fail_closed_rule():
    lines = rd.plain_lines({
        "price_data_end": "2026-09-16",
        "series": {"VXN": {"last_date": "2026-09-02", "stale": True,
                           "days_short_of_price_data": 14, "consumers": ["x"],
                           "updater": "src/data_topup_vxn.py"}},
        "stale_series": ["VXN"], "ok": False})
    assert any("STALE" in ln and "2026-09-02" in ln for ln in lines)
    assert any("FAIL CLOSED" in ln for ln in lines)


def test_coverage_ledger_write_is_production_guarded(tmp_path, monkeypatch):
    monkeypatch.delenv("TONY_PRODUCTION", raising=False)
    out = tmp_path / "data_coverage.json"
    rd.write_coverage_ledger(out)          # not a protected path -> allowed
    assert json.loads(out.read_text())["series"]["VXN"]
    from production_paths import is_protected
    assert is_protected(rd.COVERAGE_LEDGER_PATH)   # the real one IS guarded
