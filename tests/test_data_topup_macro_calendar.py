"""Scheduled macro-event calendar top-up (2026-09-16).

A mis-parsed schedule is a FABRICATED EVENT DATE, so the parser is treated as
wrong until it proves otherwise: it must reproduce the project's own frozen,
sourced lists on the overlap, and the result must have the shape a real
schedule has. Anything less writes nothing.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import data_topup_macro_calendar as mc  # noqa: E402
import reference_data as rd  # noqa: E402
from study_fomc_volatility import FOMC_DATES  # noqa: E402

MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


def fed_page(decision_dates) -> str:
    """The federalreserve.gov calendar page, in the shape it prints: a year
    heading, then each two-day meeting as 'Month D-D' (or 'Month D-Month D'
    when it straddles a month end). Built FROM the frozen sourced list, so a
    parser that reads it correctly is a parser that reproduces known-good data."""
    by_year = defaultdict(list)
    for d in decision_dates:
        by_year[d.year].append(d)
    out = ["<html><body>"]
    for year, days in sorted(by_year.items()):
        out.append(f"<h4>{year} FOMC Meetings</h4><table>")
        for d in sorted(days):
            start = d - timedelta(days=1)
            if start.month == d.month:
                cell = f"{MONTH_NAMES[d.month]}</td><td>{start.day}-{d.day}"
            else:
                cell = f"{MONTH_NAMES[start.month]}</td><td>{start.day}-{MONTH_NAMES[d.month]} {d.day}"
            out.append(f"<tr><td>{cell}</td></tr>")
        out.append("</table>")
    return "\n".join(out) + "</body></html>"


def bls_page(dates, spelling="slash") -> str:
    rows = []
    for d in dates:
        if spelling == "slash":
            cell = f"{d.month:02d}/{d.day:02d}/{d.year}"
        elif spelling == "long":
            cell = f"{MONTH_NAMES[d.month]} {d.day}, {d.year}"
        else:
            cell = f"{MONTH_NAMES[d.month][:3]}. {d.day}, {d.year}"
        rows.append(f"<tr><td>Reference month</td><td>{cell}</td><td>08:30 AM</td></tr>")
    return "<html><body><table>" + "".join(rows) + "</table></body></html>"


def _monthly(year, weekday, n=12):
    """One release a month, on the first `weekday` of the month."""
    out = []
    for m in range(1, n + 1):
        d = date(year, m, 1)
        while d.weekday() != weekday:
            d += timedelta(days=1)
        out.append(d)
    return out


# --------------------------------------------------------------------------
# parsers
# --------------------------------------------------------------------------
def test_fomc_parser_reproduces_the_frozen_sourced_list_exactly():
    parsed = mc.parse_fomc(fed_page(FOMC_DATES))
    assert parsed == sorted(FOMC_DATES)


def test_fomc_parser_handles_a_meeting_straddling_a_month_end():
    parsed = mc.parse_fomc(fed_page([date(2017, 2, 1)]))
    assert parsed == [date(2017, 2, 1)]        # 'January 31-February 1' -> the SECOND day


def test_fomc_parser_skips_unscheduled_items():
    page = fed_page([date(2026, 1, 28)]).replace(
        "</table>", "<tr><td>Meeting (unscheduled)</td><td>March 3-4</td></tr></table>")
    assert mc.parse_fomc(page) == [date(2026, 1, 28)]


def test_fomc_parser_refuses_a_page_whose_layout_moved():
    with pytest.raises(ValueError, match="layout changed"):
        mc.parse_fomc("<html><body>We have relocated this calendar.</body></html>")


@pytest.mark.parametrize("spelling", ["slash", "long", "abbr"])
def test_bls_parser_reads_every_date_spelling_bls_has_used(spelling):
    days = _monthly(2026, 4)
    assert mc.parse_bls_schedule(bls_page(days, spelling)) == days


def test_bls_parser_refuses_a_page_with_no_dates():
    with pytest.raises(ValueError, match="layout changed"):
        mc.parse_bls_schedule("<html><body>Schedule temporarily unavailable</body></html>")


# --------------------------------------------------------------------------
# verification -- what stops a bad parse becoming a fabricated event date
# --------------------------------------------------------------------------
def test_overlap_check_fails_when_a_parsed_date_contradicts_the_frozen_list():
    wrong = sorted(set(FOMC_DATES) - {FOMC_DATES[3]} | {FOMC_DATES[3] + timedelta(days=1)})
    res = mc.check_overlap_against_frozen("FOMC", wrong)
    assert not res["ok"] and res["extra"] and res["missing"]


def test_overlap_check_passes_and_is_skipped_cleanly_outside_the_frozen_range():
    assert mc.check_overlap_against_frozen("FOMC", sorted(FOMC_DATES))["ok"]
    res = mc.check_overlap_against_frozen("CPI", _monthly(2026, 2))
    assert res["ok"] and res["n_checked"] == 0


def test_shape_check_rejects_an_nfp_date_that_is_not_a_friday():
    days = _monthly(2026, 4)
    days[5] = days[5] + timedelta(days=1)          # a Saturday
    res = mc.check_shape("NFP", days)
    assert not res["ok"] and any("Friday" in p or "weekend" in p for p in res["problems"])


def test_shape_check_rejects_two_releases_in_one_month_and_a_short_parse():
    days = _monthly(2026, 2) + [date(2026, 3, 25)]
    assert not mc.check_shape("CPI", days)["ok"]
    assert not mc.check_shape("CPI", days[:4])["ok"]


def test_shape_check_rejects_a_fomc_decision_on_the_wrong_weekday_or_a_ninth_meeting():
    ok = [d for d in FOMC_DATES if d.year == 2015]
    assert mc.check_shape("FOMC", ok)["ok"]
    assert not mc.check_shape("FOMC", ok + [date(2015, 5, 4), date(2015, 5, 11)])["ok"]   # nine
    # a Monday decision is a parse error; the Thursday ones in the frozen list are real
    assert not mc.check_shape("FOMC", ok[:-1] + [date(2015, 12, 14)])["ok"]
    assert all(d.weekday() in (1, 2, 3) for d in FOMC_DATES)


def test_shape_check_passes_a_real_looking_schedule():
    assert mc.check_shape("NFP", _monthly(2026, 4))["ok"]
    assert mc.check_shape("CPI", _monthly(2026, 2))["ok"]


# --------------------------------------------------------------------------
# merge and write
# --------------------------------------------------------------------------
def test_merge_never_re_adds_a_date_the_frozen_list_already_holds():
    merged, added = mc.merge_extension({e: set() for e in mc.EVENTS},
                                       {"FOMC": sorted(FOMC_DATES) + [date(2026, 1, 28)],
                                        "CPI": [], "NFP": []})
    assert added["FOMC"] == [date(2026, 1, 28)]
    assert merged["FOMC"] == [date(2026, 1, 28)]     # the extension holds ONLY the new dates


def test_end_to_end_from_files_extends_coverage_so_a_2026_session_classifies(tmp_path, monkeypatch):
    fomc = [date(2026, 1, 28), date(2026, 3, 18), date(2026, 4, 29), date(2026, 6, 17),
            date(2026, 7, 29), date(2026, 9, 16), date(2026, 10, 28), date(2026, 12, 9)]
    cpi, nfp = _monthly(2026, 2), _monthly(2026, 4)
    (tmp_path / "f.htm").write_text(fed_page(fomc))
    (tmp_path / "c.htm").write_text(bls_page(cpi))
    (tmp_path / "n.htm").write_text(bls_page(nfp))
    cal, cov = tmp_path / "macro.csv", tmp_path / "macro_cov.json"
    log = tmp_path / "log.jsonl"
    monkeypatch.setattr(mc, "log_topup", lambda *a, **k: log.write_text("logged"))

    argv = ["--fomc-file", str(tmp_path / "f.htm"), "--cpi-file", str(tmp_path / "c.htm"),
            "--nfp-file", str(tmp_path / "n.htm"), "--calendar-path", str(cal),
            "--coverage-path", str(cov)]
    assert mc.main(argv + ["--dry-run"]) == 0
    assert not cal.exists()                       # dry run writes nothing

    assert mc.main(argv) == 0
    assert rd.macro_coverage_end(cal, cov) == min(max(fomc), max(cpi), max(nfp))
    assert rd.scheduled_events_on(date(2026, 9, 16), cal, cov) == {"FOMC"}
    assert rd.scheduled_events_on(date(2026, 9, 15), cal, cov) == set()
    # and it STILL fails closed past the published schedule
    with pytest.raises(rd.ReferenceDataUnavailable):
        rd.scheduled_events_on(date(2027, 6, 1), cal, cov)


def test_a_failed_verification_writes_absolutely_nothing(tmp_path):
    bad = _monthly(2026, 4)
    bad[3] = bad[3] + timedelta(days=1)            # Saturday NFP
    (tmp_path / "f.htm").write_text(fed_page([date(2026, 1, 28)]))
    (tmp_path / "c.htm").write_text(bls_page(_monthly(2026, 2)))
    (tmp_path / "n.htm").write_text(bls_page(bad))
    cal, cov = tmp_path / "macro.csv", tmp_path / "macro_cov.json"
    assert mc.main(["--fomc-file", str(tmp_path / "f.htm"), "--cpi-file", str(tmp_path / "c.htm"),
                    "--nfp-file", str(tmp_path / "n.htm"), "--calendar-path", str(cal),
                    "--coverage-path", str(cov)]) == 2
    assert not cal.exists() and not cov.exists()


def test_the_calendar_files_are_production_guarded():
    from production_paths import is_protected
    assert is_protected(rd.MACRO_CALENDAR_PATH) and is_protected(rd.MACRO_COVERAGE_PATH)
