"""Handoff guarantees for the work-session lock (src/worksession_lock.py).

Each test is one documented failure from 2026-09-10/11 that must never recur.
"""
import json
from datetime import datetime, timedelta, timezone

import pytest

import worksession_lock as wl

FMT = "%Y-%m-%d %H:%M:%S"


@pytest.fixture
def lock_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(wl, "LOCK", tmp_path / "_worksession.lock")
    monkeypatch.setattr(wl, "META", tmp_path / "_worksession.lock.meta")
    (tmp_path / "_worksession.lock").write_text("FREE 2026-09-11 00:00:00\n")
    return tmp_path


def _age_meta(minutes):
    m = json.loads(wl.META.read_text())
    old = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).strftime(FMT)
    m["heartbeat"] = m["started"] = old
    wl.META.write_text(json.dumps(m))
    wl.LOCK.write_text(f"RUNNING {old}\n")


def test_lock_file_stays_one_line_for_existing_parsers(lock_dir):
    assert wl.acquire("interactive") == 0
    text = wl.LOCK.read_text()
    parts = text.strip().split(None, 1)
    assert len(parts) == 2 and parts[0] == "RUNNING"
    datetime.strptime(parts[1], FMT)  # exact format ops_checks expects
    assert "UTC" not in text  # the documented parser-breaking suffix


def test_second_session_is_refused_while_first_is_alive(lock_dir):
    assert wl.acquire("interactive") == 0
    assert wl.acquire("cycle") == 2
    assert json.loads(wl.META.read_text())["owner"] == "interactive"  # not clobbered


def test_reentrant_claim_by_same_owner_is_refused(lock_dir):
    assert wl.acquire("cycle") == 0
    assert wl.acquire("cycle") == 2


def test_dead_holder_is_taken_over_and_recorded(lock_dir):
    assert wl.acquire("interactive") == 0
    _age_meta(wl.STALE_MINUTES + 15)
    code, line = wl.status()
    assert code == 3 and line.startswith("STALE")
    assert wl.acquire("cycle") == 0
    meta = json.loads(wl.META.read_text())
    assert meta["owner"] == "cycle"
    assert meta["took_over_from"]["owner"] == "interactive"


def test_fresh_heartbeat_keeps_a_long_session_alive(lock_dir):
    assert wl.acquire("cycle") == 0
    _age_meta(wl.STALE_MINUTES + 15)
    assert wl.heartbeat() == 0
    code, _ = wl.status()
    assert code == 2  # busy, not stale


def test_wrong_owner_cannot_release(lock_dir):
    assert wl.acquire("interactive") == 0
    assert wl.release("cycle") == 2
    assert wl.LOCK.read_text().startswith("RUNNING")
    assert wl.release("interactive") == 0
    assert wl.LOCK.read_text().startswith("FREE")


def test_acquire_detects_a_race(lock_dir, monkeypatch):
    calls = {"n": 0}
    real = wl._read_lock

    def racy():
        calls["n"] += 1
        if calls["n"] == 3:  # the compare-and-swap re-read sees a new claim
            return "RUNNING", "RUNNING 2026-09-11 00:00:05\n"
        return real()

    monkeypatch.setattr(wl, "_read_lock", racy)
    assert wl.acquire("cycle") == 4
    assert wl.LOCK.read_text().startswith("FREE")  # we wrote nothing


def test_garbled_running_line_is_treated_as_dead_holder_not_free(lock_dir):
    wl.LOCK.write_text("RUNNING 2026-09-11 00:00:00 UTC\n")  # the old parser-breaking bug
    code, line = wl.status()
    assert code == 3 and line.startswith("STALE")  # take over WITH a record, never silently
    assert wl.acquire("cycle") == 0
    assert "took_over_from" in json.loads(wl.META.read_text())


def test_missing_lock_is_free(lock_dir):
    wl.LOCK.unlink()
    assert wl.status()[0] == 0
    assert wl.acquire("cycle") == 0
