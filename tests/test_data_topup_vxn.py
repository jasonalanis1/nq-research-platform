"""VXN reference-series top-up (2026-09-16): incremental, never rewrites
history, proves the fetched series IS the one on disk before extending it."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import data_topup_vxn as tv  # noqa: E402

# The header CBOE actually publishes, verified live 2026-09-16.
CBOE = """DATE,OPEN,HIGH,LOW,CLOSE
09/01/2026,21.100000,22.400000,20.900000,21.960000
09/02/2026,21.500000,21.900000,20.800000,21.070000
09/03/2026,21.000000,21.600000,20.500000,20.640000
09/04/2026,20.700000,21.100000,20.100000,20.330000
"""


def test_parse_cboe_csv_reads_the_published_shape():
    s = tv.parse_cboe_csv(CBOE)
    assert s[date(2026, 9, 1)] == 21.96 and s[date(2026, 9, 4)] == 20.33
    assert list(s) == sorted(s)


def test_parse_tolerates_a_blurb_above_the_header_and_iso_dates():
    s = tv.parse_cboe_csv("CBOE Nasdaq-100 Volatility Index\n\nDATE,CLOSE\n2026-09-01,21.96\n")
    assert s == {date(2026, 9, 1): 21.96}


def test_parse_refuses_a_page_with_no_recognisable_header():
    with pytest.raises(ValueError, match="header row"):
        tv.parse_cboe_csv("<html>we moved this file</html>")


def test_merge_only_appends_and_never_rewrites_history():
    old = {date(2026, 9, 1): 21.96, date(2026, 9, 2): 21.07}
    new = {date(2026, 9, 1): 99.99, date(2026, 9, 3): 20.64, date(2026, 9, 4): 20.33}
    merged, added = tv.merge(old, new)
    assert added == [date(2026, 9, 3), date(2026, 9, 4)]
    assert merged[date(2026, 9, 1)] == 21.96      # the disk value wins, always


def test_overlap_check_catches_a_different_series():
    old = {date(2026, 9, 1): 21.96, date(2026, 9, 2): 21.07}
    assert tv.check_overlap(old, dict(old))["ok"]
    bad = {date(2026, 9, 1): 0.2196, date(2026, 9, 2): 0.2107}    # unit change
    res = tv.check_overlap(old, bad)
    assert not res["ok"] and res["mismatches"]


def test_overlap_check_refuses_an_unverifiable_join():
    res = tv.check_overlap({date(2020, 1, 2): 15.0}, {date(2026, 9, 3): 20.64})
    assert not res["ok"] and "refusing" in res["note"].lower()


def test_continuity_rejects_an_implausible_value_and_an_unexplained_hole():
    old = {date(2026, 9, 2): 21.07}
    merged = {**old, date(2026, 9, 3): 4000.0}
    res = tv.check_continuity(old, merged, [date(2026, 9, 3)])
    assert res["status"] == "FAIL"
    merged2 = {**old, date(2026, 11, 3): 20.0}
    res2 = tv.check_continuity(old, merged2, [date(2026, 11, 3)])
    assert res2["status"] == "FAIL"
    assert any("hole" in c["check"] and c["status"] == "FAIL" for c in res2["checks"])


def test_continuity_passes_a_normal_top_up():
    old = {date(2026, 9, 2): 21.07}
    merged = {**old, date(2026, 9, 3): 20.64, date(2026, 9, 4): 20.33}
    res = tv.check_continuity(old, merged, [date(2026, 9, 3), date(2026, 9, 4)])
    assert res["status"] == "PASS" and res["n_added"] == 2


def test_end_to_end_from_file_writes_and_reference_data_reads_it_back(tmp_path):
    src = tmp_path / "cboe.csv"
    src.write_text(CBOE)
    disk = tmp_path / "VXN.csv"
    disk.write_text("observation_date,VXNCLS\n2026-09-01,21.96\n2026-09-02,21.07\n")
    log = tmp_path / "topup_log.jsonl"
    assert tv.main(["--from-file", str(src), "--path", str(disk), "--log-path", str(log)]) == 0
    assert log.exists() and "VXN" in log.read_text()
    import reference_data as rd
    assert rd.vxn_coverage_end(disk) == date(2026, 9, 4)
    assert rd.vxn_close(date(2026, 9, 3), disk) == 20.64
    assert rd.vxn_daily(disk)[date(2026, 9, 1)] == 21.96      # history intact
    assert tv.main(["--from-file", str(src), "--path", str(disk), "--log-path", str(log)]) == 0  # idempotent


def test_dry_run_and_a_mismatched_source_write_nothing(tmp_path):
    src = tmp_path / "cboe.csv"
    src.write_text(CBOE)
    disk = tmp_path / "VXN.csv"
    before = "observation_date,VXNCLS\n2026-09-01,21.96\n2026-09-02,21.07\n"
    disk.write_text(before)
    assert tv.main(["--from-file", str(src), "--path", str(disk), "--dry-run"]) == 0
    assert disk.read_text() == before

    wrong = tmp_path / "wrong.csv"
    wrong.write_text("DATE,CLOSE\n09/01/2026,0.2196\n09/02/2026,0.2107\n09/03/2026,0.2064\n")
    assert tv.main(["--from-file", str(wrong), "--path", str(disk)]) == 2
    assert disk.read_text() == before


def test_the_real_series_file_is_production_guarded():
    from production_paths import is_protected
    assert is_protected(tv.VXN_PATH)
