"""Tests for the Operations Manager's mechanical checks.

These test the CHECKS, not the project's current state -- a check that
only passes because today happens to be tidy is worthless. Each one is
driven against a constructed fixture so it is provably able to fail.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import ops_checks  # noqa: E402
from ops_checks import PASS, WARN, FAIL  # noqa: E402


def _stamp(minutes_ago: int) -> str:
    t = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return t.strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Point every path in ops_checks at a throwaway tree."""
    research = tmp_path / "research"
    (research / "sessions").mkdir(parents=True)
    (research / "mechanisms").mkdir(parents=True)
    monkeypatch.setattr(ops_checks, "RESEARCH", research)
    monkeypatch.setattr(ops_checks, "SESSIONS_DIR", research / "sessions")
    monkeypatch.setattr(ops_checks, "MECHANISMS_DIR", research / "mechanisms")
    monkeypatch.setattr(ops_checks, "LOCK", research / "_worksession.lock")
    monkeypatch.setattr(ops_checks, "SESSION_LOG", research / "_session_log.txt")
    monkeypatch.setattr(ops_checks, "CONSOLE_STATE", research / "_console_state.json")
    monkeypatch.setattr(ops_checks, "NEXT_UP", research / "NEXT_UP.md")
    # keep the fixture hermetic: the real repo ledger must never make a
    # constructed workspace look alive
    monkeypatch.setattr(ops_checks, "LEDGER", research / "ledger.jsonl")
    return research


# ---------------------------------------------------------------- lock

def test_lock_free_passes(workspace):
    (workspace / "_worksession.lock").write_text(f"FREE {_stamp(5)}\n")
    assert ops_checks.check_lock_health().status == PASS


def test_lock_running_with_recent_activity_passes(workspace):
    (workspace / "_worksession.lock").write_text(f"RUNNING {_stamp(10)}\n")
    (workspace / "_session_log.txt").write_text(f"{_stamp(2)} automated: working\n")
    assert ops_checks.check_lock_health().status == PASS


def test_lock_running_but_silent_is_a_dead_session(workspace):
    """The 2026-09-10 failure: the bridge dropped mid-run, the session
    died, and the lock read RUNNING for hours while nothing happened."""
    (workspace / "_worksession.lock").write_text(f"RUNNING {_stamp(90)}\n")
    (workspace / "_session_log.txt").write_text(f"{_stamp(75)} automated: last checkpoint\n")
    result = ops_checks.check_lock_health()
    assert result.status == FAIL
    assert "died" in result.detail


def test_a_session_doing_real_work_is_not_reported_dead(workspace, monkeypatch):
    """2026-09-10: a healthy session spent 30 minutes running a Validation
    test, wrote ledger rows but no log line, and was reported dead.
    Liveness must come from the work, not only from prose."""
    (workspace / "_worksession.lock").write_text(f"RUNNING {_stamp(40)}\n")
    (workspace / "_session_log.txt").write_text(f"{_stamp(95)} automated: last prose\n")
    ledger = workspace / "ledger.jsonl"
    ledger.write_text('{"hypothesis_id": "hyp-1"}\n')  # written just now
    monkeypatch.setattr(ops_checks, "LEDGER", ledger)
    assert ops_checks.check_lock_health().status == PASS


def test_missing_lock_warns(workspace):
    assert ops_checks.check_lock_health().status == WARN


# ------------------------------------------------------------- console

def test_console_fresh_passes(workspace):
    (workspace / "_console_state.json").write_text(json.dumps({
        "generated_at": (datetime.now(timezone.utc) - timedelta(minutes=3))
        .strftime("%Y-%m-%dT%H:%M:%SZ")}))
    assert ops_checks.check_console_fresh().status == PASS


def test_console_stale_warns(workspace):
    (workspace / "_console_state.json").write_text(json.dumps({
        "generated_at": (datetime.now(timezone.utc) - timedelta(hours=4))
        .strftime("%Y-%m-%dT%H:%M:%SZ")}))
    assert ops_checks.check_console_fresh().status == WARN


def test_console_never_written_fails(workspace):
    assert ops_checks.check_console_fresh().status == FAIL


# ------------------------------------------------------------- reports

REPORT_OK = """## Session test

## Agents

**LEARN -- RAN.** Finding: something.

**Discovery -- NOT RUN.** Input condition not met -- no scan.

## Staff meeting
Not convened.
"""


def test_wellformed_report_passes(workspace):
    (workspace / "sessions" / "2026-09-10-0000.md").write_text(REPORT_OK)
    assert ops_checks.check_session_reports().status == PASS


def test_report_without_agent_section_warns(workspace):
    (workspace / "sessions" / "2026-09-10-0000.md").write_text("## Session\nnothing here\n")
    assert ops_checks.check_session_reports().status == WARN


def test_no_reports_fails(workspace):
    assert ops_checks.check_session_reports().status == FAIL


# ----------------------------------------------------- new information

def _report_with_info(text: str) -> str:
    return REPORT_OK + f"\n## WHAT NEW INFORMATION THIS RUN PRODUCED\n\n{text}\n"


def test_run_reporting_new_information_passes(workspace):
    (workspace / "sessions" / "2026-09-10-0400.md").write_text(
        _report_with_info("Scan 006 closed; two cells cleared the gate."))
    assert ops_checks.check_new_information().status == PASS


def test_consecutive_barren_runs_fail(workspace):
    """Three runs in a row producing nothing is a methodology signal."""
    for i, name in enumerate(("0000", "0400", "0800")):
        (workspace / "sessions" / f"2026-09-1{i}-{name}.md").write_text(
            _report_with_info("None — everything remaining is blocked."))
    result = ops_checks.check_new_information()
    assert result.status == FAIL
    assert "staff meeting" in result.detail


def test_missing_new_information_line_warns(workspace):
    (workspace / "sessions" / "2026-09-10-0400.md").write_text(REPORT_OK)
    assert ops_checks.check_new_information().status == WARN


# ------------------------------------------------------ awaiting Jason

def test_blocked_item_is_surfaced(workspace):
    (workspace / "NEXT_UP.md").write_text(
        "## Queue\n\n   1a. EXECUTION SPEC — BLOCKED until Jason answers the entry question\n")
    result = ops_checks.check_awaiting_jason()
    assert result.status == WARN
    assert "blocked on Jason" in result.detail


def test_unblocked_is_not_read_as_blocked(workspace):
    """'UNBLOCKED' contains 'BLOCKED'. An item Jason has already answered
    must stop reporting as waiting on him."""
    (workspace / "NEXT_UP.md").write_text(
        "## Queue\n\n   1a. EXECUTION SPEC — UNBLOCKED 2026-09-10, Jason chose option B\n")
    assert ops_checks.check_awaiting_jason().status == PASS


def test_clear_queue_passes(workspace):
    (workspace / "NEXT_UP.md").write_text("## Queue\n\n   1. Run Scan 006\n")
    assert ops_checks.check_awaiting_jason().status == PASS


# ------------------------------------------------------------ overall

def test_overall_is_worst_status():
    R = ops_checks.Result
    assert ops_checks.overall([R("a", PASS, ""), R("b", PASS, "")]) == PASS
    assert ops_checks.overall([R("a", PASS, ""), R("b", WARN, "")]) == WARN
    assert ops_checks.overall([R("a", WARN, ""), R("b", FAIL, "")]) == FAIL


def test_a_broken_check_never_takes_the_run_down(monkeypatch):
    """Operations must not be able to halt research by failing itself."""
    def explode():
        raise RuntimeError("boom")
    monkeypatch.setattr(ops_checks, "CHECKS", (explode,))
    results = ops_checks.run_all()
    assert len(results) == 1
    assert results[0].status == WARN
    assert "check itself failed" in results[0].detail
