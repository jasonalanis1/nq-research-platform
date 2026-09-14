"""Tests for src/cycle_preflight.py and the two ops checks added with it.

These exist because of a specific failure: across the four cycles of
2026-09-14 the H118 daily checker ran zero times, the pipeline sweep ran once,
and nothing detected any of it. The tests below are about DETECTION -- that a
skipped or failed opening sequence is visible, and that committed-but-unpushed
work is visible. A guardrail nobody tests is a guardrail nobody can trust.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

import cycle_preflight as cp  # noqa: E402
import ops_checks as oc  # noqa: E402


# ---------------------------------------------------------------------------
# shelf / sourcing reporting
# ---------------------------------------------------------------------------

def test_shelf_status_flags_sourcing_owed_at_the_floor(tmp_path, monkeypatch):
    d = tmp_path / "data"; d.mkdir()
    (d / "pipeline_sweep.json").write_text(json.dumps(
        {"shelf": "Shelf 3/3 DRAWABLE (Entry 32, 33, 35; pending: Entry 15)"}))
    monkeypatch.setattr(cp, "ROOT", tmp_path)
    s = cp.shelf_status()
    assert s["known"] is True and s["count"] == 3 and s["floor"] == 3
    assert s["sourcing_owed"] is True


def test_shelf_status_above_the_floor_is_not_owed(tmp_path, monkeypatch):
    d = tmp_path / "data"; d.mkdir()
    (d / "pipeline_sweep.json").write_text(json.dumps({"shelf": "Shelf 5/3 DRAWABLE (...)"}))
    monkeypatch.setattr(cp, "ROOT", tmp_path)
    s = cp.shelf_status()
    assert s["count"] == 5 and s["sourcing_owed"] is False


def test_shelf_status_is_honest_when_the_sweep_has_not_run(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    monkeypatch.setattr(cp, "ROOT", tmp_path)
    s = cp.shelf_status()
    assert s["known"] is False
    assert "run the sweep" in s["note"]


# ---------------------------------------------------------------------------
# the preflight check -- the thing that would have caught this morning
# ---------------------------------------------------------------------------

def _receipt(tmp_path, monkeypatch, **over):
    body = {"ran_at": datetime.now(timezone.utc).isoformat(), "owner": "cycle",
            "failed": [], "ok": True, "steps": {"shelf": {"sourcing_owed": False}}}
    body.update(over)
    research = tmp_path / "research"; research.mkdir(exist_ok=True)
    (research / "_cycle_preflight.json").write_text(json.dumps(body))
    monkeypatch.setattr(oc, "RESEARCH", research)
    return body


def test_preflight_fails_when_no_receipt_exists(tmp_path, monkeypatch):
    research = tmp_path / "research"; research.mkdir()
    monkeypatch.setattr(oc, "RESEARCH", research)
    r = oc.check_preflight()
    assert r.status == oc.FAIL
    assert "no preflight receipt" in r.detail


def test_preflight_fails_when_a_step_failed(tmp_path, monkeypatch):
    _receipt(tmp_path, monkeypatch, failed=["h118"], ok=False)
    r = oc.check_preflight()
    assert r.status == oc.FAIL
    assert "h118" in r.detail


def test_preflight_fails_on_a_stale_receipt_from_a_previous_cycle(tmp_path, monkeypatch):
    """THE ACTUAL 2026-09-14 FAILURE: the checkers last ran in the 11:00 pm
    cycle and four later cycles inherited that stale state unnoticed. A
    receipt older than one cycle must not satisfy this check."""
    old = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
    _receipt(tmp_path, monkeypatch, ran_at=old)
    r = oc.check_preflight()
    assert r.status == oc.FAIL
    assert "has not run its" in r.detail


def test_preflight_passes_on_a_fresh_clean_receipt(tmp_path, monkeypatch):
    _receipt(tmp_path, monkeypatch)
    r = oc.check_preflight()
    assert r.status == oc.PASS


def test_preflight_surfaces_sourcing_owed(tmp_path, monkeypatch):
    _receipt(tmp_path, monkeypatch, steps={"shelf": {"sourcing_owed": True}})
    r = oc.check_preflight()
    assert r.status == oc.PASS
    assert "SOURCING OWED" in r.detail


def test_preflight_warns_rather_than_crashes_on_a_corrupt_receipt(tmp_path, monkeypatch):
    research = tmp_path / "research"; research.mkdir()
    (research / "_cycle_preflight.json").write_text("{not json")
    monkeypatch.setattr(oc, "RESEARCH", research)
    r = oc.check_preflight()
    assert r.status == oc.WARN


# ---------------------------------------------------------------------------
# git sync -- nothing in ops_checks looked at git at all before this
# ---------------------------------------------------------------------------

def test_git_sync_fails_on_unpushed_commits(monkeypatch):
    class P:
        stdout = "## main...origin/main [ahead 3]\n"
    monkeypatch.setattr(oc.__dict__["subprocess"] if "subprocess" in oc.__dict__ else __import__("subprocess"),
                        "run", lambda *a, **k: P())
    r = oc.check_git_sync()
    assert r.status == oc.FAIL
    assert "NOT PUSHED" in r.detail


def test_git_sync_passes_when_in_sync(monkeypatch):
    class P:
        stdout = "## main...origin/main\n"
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: P())
    r = oc.check_git_sync()
    assert r.status == oc.PASS


def test_git_sync_warns_when_behind(monkeypatch):
    class P:
        stdout = "## main...origin/main [behind 2]\n"
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: P())
    r = oc.check_git_sync()
    assert r.status == oc.WARN


# ---------------------------------------------------------------------------
# registration -- a check that exists but is never run is worse than none
# ---------------------------------------------------------------------------

def test_both_new_checks_are_registered_in_CHECKS():
    names = [c.__name__ for c in oc.CHECKS]
    assert "check_preflight" in names
    assert "check_git_sync" in names


def test_every_registered_check_is_callable_without_arguments():
    for c in oc.CHECKS:
        assert callable(c)
        assert c.__code__.co_argcount == 0, f"{c.__name__} takes arguments; run_all() calls it bare"


# ---------------------------------------------------------------------------
# awaiting-jason: the section named "Blocked — needs Jason" was never read
# ---------------------------------------------------------------------------

def _next_up(tmp_path, monkeypatch, body):
    f = tmp_path / "NEXT_UP.md"
    f.write_text(body)
    monkeypatch.setattr(oc, "NEXT_UP", f)
    monkeypatch.setattr(oc, "RESEARCH", tmp_path)   # no pipeline_sweep.json -> no GATED rows
    return f


def test_awaiting_jason_reads_the_blocked_needs_jason_section(tmp_path, monkeypatch):
    """The pre-2026-09-14 check ignored this section entirely, so the IBKR
    question, the 6E data pull and the H118 anchor decision were all invisible
    to the one check whose job is to watch things parked on him."""
    _next_up(tmp_path, monkeypatch,
             "## Blocked — needs Jason\n\n"
             "- **H118 anchor decision. YOUR CALL.**\n"
             "  continuation line that must not count as its own item\n\n"
             "SHELF RULE v2 (not a blocked item)\n"
             "- SOURCING RUNS EVERY CYCLE, FIRST\n")
    r = oc.check_awaiting_jason()
    assert r.status == oc.WARN
    assert "1 item(s)" in r.detail
    assert "H118" in r.detail


def test_awaiting_jason_stops_at_the_first_non_bullet_block(tmp_path, monkeypatch):
    """Bounding the section by 'the next ## heading' swept in 21k characters of
    rules and decided notes and reported 10 phantom items."""
    _next_up(tmp_path, monkeypatch,
             "## Blocked — needs Jason\n\n"
             "- one real item\n\n"
             "A paragraph of rules.\n\n"
             "- a bullet that belongs to the rules, not to Jason\n")
    r = oc.check_awaiting_jason()
    assert "1 item(s)" in r.detail


def test_awaiting_jason_skips_items_already_decided(tmp_path, monkeypatch):
    _next_up(tmp_path, monkeypatch,
             "## Blocked — needs Jason\n\n"
             "- H118 DECIDED (Sept 12th): reclassified, no action\n"
             "- data question ANSWERED: no purchase\n")
    r = oc.check_awaiting_jason()
    assert r.status == oc.PASS


def test_awaiting_jason_does_not_skip_an_item_merely_containing_the_word_decision(tmp_path, monkeypatch):
    """Regression: 'DECISION' was briefly a skip word, which silently dropped
    'H118 anchor decision -- YOUR CALL' -- an item still awaiting him. A false
    negative here means the item goes unwatched and nobody finds out."""
    _next_up(tmp_path, monkeypatch,
             "## Blocked — needs Jason\n\n- H118 anchor decision needed -- YOUR CALL\n")
    r = oc.check_awaiting_jason()
    assert r.status == oc.WARN


def test_awaiting_jason_passes_when_the_section_is_empty(tmp_path, monkeypatch):
    _next_up(tmp_path, monkeypatch, "## Blocked — needs Jason\n\nNothing right now.\n")
    r = oc.check_awaiting_jason()
    assert r.status == oc.PASS


def test_preflight_fails_when_the_receipt_predates_the_current_cycle(tmp_path, monkeypatch):
    """The bug in the first version of this very check: a bare age bound would
    let a cycle inherit the PREVIOUS cycle's preflight and pass -- which is the
    exact failure mode the check was built to close."""
    research = tmp_path / "research"; research.mkdir()
    receipt_time = datetime.now(timezone.utc) - timedelta(minutes=100)
    (research / "_cycle_preflight.json").write_text(json.dumps(
        {"ran_at": receipt_time.isoformat(), "failed": [], "ok": True, "steps": {}}))
    (research / "_cycle_checkpoint.json").write_text(json.dumps(
        {"status": "running", "started": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()}))
    monkeypatch.setattr(oc, "RESEARCH", research)
    r = oc.check_preflight()
    assert r.status == oc.FAIL
    assert "PREVIOUS cycle" in r.detail


def test_preflight_passes_when_the_receipt_follows_the_cycle_start(tmp_path, monkeypatch):
    research = tmp_path / "research"; research.mkdir()
    (research / "_cycle_checkpoint.json").write_text(json.dumps(
        {"status": "running", "started": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()}))
    (research / "_cycle_preflight.json").write_text(json.dumps(
        {"ran_at": (datetime.now(timezone.utc) - timedelta(minutes=9)).isoformat(),
         "failed": [], "ok": True, "steps": {}}))
    monkeypatch.setattr(oc, "RESEARCH", research)
    assert oc.check_preflight().status == oc.PASS


def test_git_sync_does_not_false_fail_on_a_stale_tracking_ref(monkeypatch):
    """A stale .git/refs/remotes/origin/main.lock freezes the tracking ref, so
    `git status -sb` says "ahead 1" against a remote that already has the work.
    Seen live 2026-09-14. The check must confirm against the actual remote
    before failing -- it would otherwise have failed every unattended cycle."""
    import subprocess
    sha = "f91a141758e088616d59c4bf99446c01cd943b6f"
    def fake(argv, **kw):
        class P: pass
        p = P()
        if argv[1] == "status":
            p.stdout = "## main...origin/main [ahead 1]\n"
        elif argv[1] == "rev-parse":
            p.stdout = sha + "\n"
        else:                                   # ls-remote
            p.stdout = f"{sha}\tHEAD\n"
        return p
    monkeypatch.setattr(subprocess, "run", fake)
    r = oc.check_git_sync()
    assert r.status == oc.PASS
    assert "tracking ref stale" in r.detail


def test_git_sync_still_fails_when_the_remote_really_is_behind(monkeypatch):
    """The guard must not become a blanket excuse for unpushed work."""
    import subprocess
    def fake(argv, **kw):
        class P: pass
        p = P()
        if argv[1] == "status":
            p.stdout = "## main...origin/main [ahead 2]\n"
        elif argv[1] == "rev-parse":
            p.stdout = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        else:
            p.stdout = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\tHEAD\n"
        return p
    monkeypatch.setattr(subprocess, "run", fake)
    r = oc.check_git_sync()
    assert r.status == oc.FAIL
    assert "NOT PUSHED" in r.detail
