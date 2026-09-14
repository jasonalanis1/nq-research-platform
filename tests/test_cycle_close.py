"""Tests for src/cycle_close.py and src/cycle_review.py.

These are the record Jason reviews at the end of an unattended day, so the
thing that matters most is that they cannot report a cycle as clean when it
was not, and cannot quietly omit a cycle that never closed at all.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

import cycle_close as cc  # noqa: E402
import cycle_review as cr  # noqa: E402


# ---------------------------------------------------------------------------
# the individual close checks
# ---------------------------------------------------------------------------

def test_git_check_fails_on_unpushed_commits(monkeypatch):
    monkeypatch.setattr(cc, "_run", lambda argv, timeout=30: (0, "## main...origin/main [ahead 2]\n", ""))
    r = cc.check_git()
    assert r["ok"] is False and r["unpushed"] == 2
    assert "NOT PUSHED" in r["detail"]


def test_git_check_fails_on_uncommitted_tracked_files(monkeypatch):
    monkeypatch.setattr(cc, "_run", lambda argv, timeout=30:
                        (0, "## main...origin/main\n M src/thing.py\n", ""))
    r = cc.check_git()
    assert r["ok"] is False and r["uncommitted"] == 1


def test_git_check_ignores_untracked_files(monkeypatch):
    """Scratch files must not make a clean cycle look dirty."""
    monkeypatch.setattr(cc, "_run", lambda argv, timeout=30:
                        (0, "## main...origin/main\n?? scratch.txt\n", ""))
    assert cc.check_git()["ok"] is True


def test_lock_check_fails_when_the_lock_was_left_held(monkeypatch):
    monkeypatch.setattr(cc, "_run", lambda argv, timeout=30: (0, "BUSY owner=cycle ...\n", ""))
    assert cc.check_lock()["ok"] is False


def test_tests_check_reports_failures(monkeypatch):
    monkeypatch.setattr(cc, "_run", lambda argv, timeout=170: (1, "3 failed, 400 passed\n", ""))
    r = cc.check_tests(skip=False)
    assert r["ok"] is False and r["failed"] == 3


def test_ops_fail_is_not_ok_but_warn_is(monkeypatch):
    monkeypatch.setattr(cc, "_run", lambda argv, timeout=120:
                        (0, json.dumps({"overall": "WARN",
                                        "checks": [{"name": "awaiting-jason", "status": "WARN"}]}), ""))
    assert cc.check_ops()["ok"] is True
    monkeypatch.setattr(cc, "_run", lambda argv, timeout=120:
                        (0, json.dumps({"overall": "FAIL",
                                        "checks": [{"name": "preflight", "status": "FAIL"}]}), ""))
    r = cc.check_ops()
    assert r["ok"] is False and "preflight" in r["failing"]


def test_preflight_receipt_from_a_previous_cycle_is_not_accepted(tmp_path, monkeypatch):
    """The failure this whole apparatus exists to prevent: a cycle inheriting
    the previous cycle's opening sequence and reporting itself complete."""
    monkeypatch.setattr(cc, "PREFLIGHT", tmp_path / "pre.json")
    monkeypatch.setattr(cc, "CHECKPOINT", tmp_path / "ckpt.json")
    (tmp_path / "pre.json").write_text(json.dumps(
        {"ran_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
         "failed": [], "steps": {}}))
    (tmp_path / "ckpt.json").write_text(json.dumps(
        {"started": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()}))
    r = cc.check_preflight_receipt()
    assert r["ok"] is False
    assert "PREVIOUS cycle" in r["detail"]


def test_preflight_receipt_missing_is_a_failure_not_a_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(cc, "PREFLIGHT", tmp_path / "nope.json")
    r = cc.check_preflight_receipt()
    assert r["ok"] is False
    assert "never ran" in r["detail"]


# ---------------------------------------------------------------------------
# the day review
# ---------------------------------------------------------------------------

def _write(tmp_path, monkeypatch, rows):
    f = tmp_path / "_cycle_compliance.jsonl"
    f.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(cr, "COMPLIANCE", f)
    return f


def _row(hour_ct, complete=True, moved=False, day="2026-09-14"):
    utc = datetime.fromisoformat(f"{day}T00:00:00+00:00").replace(hour=(hour_ct + 5) % 24)
    if hour_ct + 5 >= 24:
        utc += timedelta(days=1)
    return {"closed_at": utc.isoformat(), "label": f"{hour_ct}:00 cycle",
            "complete": complete, "failing": [] if complete else ["tests"],
            "checks": {"preflight": {"ok": True}, "tests": {"ok": complete},
                       "ops": {"ok": True}, "git": {"ok": True}, "lock": {"ok": True}},
            "moved": moved, "delta": {"ledger_rows": 1} if moved else {}}


def test_review_lists_cycles_that_closed(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, [_row(1), _row(3, moved=True)])
    d = cr.build("2026-09-14")
    assert d["n_cycles"] == 2 and d["n_moved"] == 1


def test_review_calls_out_a_cycle_that_never_closed(tmp_path, monkeypatch):
    """The most important case: a cycle that fired and died leaves NO row, and
    an absence is easy to miss. It has to be named, not silently omitted."""
    _write(tmp_path, monkeypatch, [_row(1)])
    d = cr.build("2026-09-14", now_ct=datetime.fromisoformat("2026-09-14T06:30:00"))
    assert 5 in d["missing_hours"] and 3 in d["missing_hours"]
    assert 1 not in d["missing_hours"]          # that one did close
    assert "NO RECORDED CLOSE" in cr.render(d)


def test_review_does_not_flag_cycles_that_are_not_due_yet(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, [_row(1)])
    d = cr.build("2026-09-14", now_ct=datetime.fromisoformat("2026-09-14T02:10:00"))
    assert d["missing_hours"] == []


def test_review_counts_an_incomplete_cycle_as_not_complete(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, [_row(1, complete=False)])
    d = cr.build("2026-09-14")
    assert d["n_cycles"] == 1 and d["n_complete"] == 0


def test_review_ignores_other_days(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, [_row(1, day="2026-09-13"), _row(3)])
    d = cr.build("2026-09-14")
    assert d["n_cycles"] == 1


def test_review_survives_a_corrupt_line(tmp_path, monkeypatch):
    f = tmp_path / "_cycle_compliance.jsonl"
    f.write_text(json.dumps(_row(1)) + "\n{ broken\n")
    monkeypatch.setattr(cr, "COMPLIANCE", f)
    assert cr.build("2026-09-14")["n_cycles"] == 1
