"""Resume safety + busy-work alert (Jason, 2026-09-11): each new check and the
budget clock must be provably able to fail."""
from __future__ import annotations
import json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import cycle_budget as cb  # noqa: E402
import ops_checks  # noqa: E402


def _wire(tmp_path, monkeypatch):
    research = tmp_path / "research"; (research / "ledger").mkdir(parents=True); (research / "mechanisms").mkdir(); (research / "studies").mkdir()
    (tmp_path / "src").mkdir(); (tmp_path / "data").mkdir()
    (research / "ledger" / "hypotheses.jsonl").write_text('{"a":1}\n')
    (research / "idea_inventory.md").write_text("## ENTRY 1 — x\n")
    (research / "mechanisms" / "README.md").write_text(""); (research / "mechanisms" / "TEMPLATE.md").write_text("")
    (tmp_path / "src" / "project_wide_multiplicity.py").write_text('    "scan_001_2026-01-01": {},\n')
    monkeypatch.setattr(cb, "ROOT", tmp_path); monkeypatch.setattr(cb, "R", research)
    monkeypatch.setattr(cb, "CKPT", research / "_cycle_checkpoint.json"); monkeypatch.setattr(cb, "HIST", research / "_cycle_history.jsonl")
    monkeypatch.setattr(ops_checks, "RESEARCH", research); monkeypatch.setattr(ops_checks, "LOCK", research / "_worksession.lock")
    return research


def test_budget_clock_signals_close_out_and_over(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    cb.main(["start", "--minutes", "105"])
    assert cb.main(["remaining"]) == 0
    c = json.loads(cb.CKPT.read_text()); c["started"] = (datetime.now(timezone.utc) - timedelta(minutes=95)).isoformat(); cb.CKPT.write_text(json.dumps(c))
    assert cb.main(["remaining"]) == 3          # <= 15 min left -> close out
    c["started"] = (datetime.now(timezone.utc) - timedelta(minutes=120)).isoformat(); cb.CKPT.write_text(json.dumps(c))
    assert cb.main(["remaining"]) == 4          # over budget


def test_unfinished_checkpoint_is_flagged_for_resume(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    cb.main(["start"]); cb.main(["checkpoint", "--item", "Entry 12", "--step", "scan written, not run", "--files", "src/x.py"])
    (r / "_worksession.lock").write_text("FREE 2026-01-01 00:00:00")
    res = ops_checks.check_unfinished_checkpoint()
    assert res.status == ops_checks.WARN and "UNFINISHED" in res.detail and "Entry 12" in res.detail
    cb.main(["done"])
    assert ops_checks.check_unfinished_checkpoint().status == ops_checks.PASS


def _row(hid, status, slice_="discovery"):
    return json.dumps({"hypothesis_id": hid, "strategy_status": status, "data_slice_used": slice_}) + "\n"


def test_done_records_whether_anything_moved(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    cb.main(["start"]); cb.main(["done"])
    assert json.loads(cb.HIST.read_text().splitlines()[-1])["moved"] is False
    # a study alone is activity, not movement (refocus 7.1) -- recorded, but moved stays False
    cb.main(["start"]); (r / "studies" / "new.md").write_text("x"); cb.main(["done"])
    last = json.loads(cb.HIST.read_text().splitlines()[-1])
    assert last["moved"] is False and last["delta"]["studies"] == 1
    # a candidate changing stage IS movement
    cb.main(["start"]); (r / "ledger" / "hypotheses.jsonl").open("a").write(_row("hyp-000001", "PROMISING")); cb.main(["done"])
    assert json.loads(cb.HIST.read_text().splitlines()[-1])["moved"] is True


def test_inventory_additions_alone_are_not_movement(tmp_path, monkeypatch):
    """Refocus 7.1 (Jason, Sept 15th): batch screening added 25 shelf rows and
    discovered nothing; the busy-work guard must NOT count that as movement."""
    r = _wire(tmp_path, monkeypatch)
    cb.main(["start"])
    inv = r / "idea_inventory.md"
    inv.write_text(inv.read_text() + "".join(f"## ENTRY {n} — survivor\n" for n in range(2, 27)))
    (r / "mechanisms" / "m1.md").write_text("mechanism doc")
    cb.main(["done"])
    last = json.loads(cb.HIST.read_text().splitlines()[-1])
    assert last["delta"]["inventory_entries"] == 25 and last["delta"]["mechanism_docs"] == 1
    assert last["delta"]["stage_changes"] == 0
    assert last["moved"] is False
    # three such cycles in a row is BUSY WORK
    (tmp_path / "data" / "pipeline_sweep.json").write_text(json.dumps({"rows": [{"tier": "OPEN", "next_owed": "Statistical"}], "shelf": "Shelf 3/3 live"}))
    for _ in range(2):
        cb.HIST.open("a").write(json.dumps({"moved": False, "delta": {"inventory_entries": 25}}) + "\n")
    res = ops_checks.check_value_per_cycle()
    assert res.status == ops_checks.FAIL and "BUSY WORK" in res.detail


def test_stage_change_is_movement_but_a_repeated_status_is_not(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    led = r / "ledger" / "hypotheses.jsonl"
    led.write_text(_row("hyp-000001", "PROMISING"))
    # same status re-logged on the same slice: a row changed, no stage changed
    cb.main(["start"]); led.open("a").write(_row("hyp-000001", "PROMISING")); cb.main(["done"])
    last = json.loads(cb.HIST.read_text().splitlines()[-1])
    assert last["delta"]["ledger_rows"] == 1 and last["delta"]["stage_changes"] == 0 and last["moved"] is False
    # Discovery -> Validation slice: stage change
    cb.main(["start"]); led.open("a").write(_row("hyp-000001", "PROMISING", "validation")); cb.main(["done"])
    last = json.loads(cb.HIST.read_text().splitlines()[-1])
    assert last["delta"]["stage_changes"] == 1 and last["moved"] is True
    # PROMISING -> REJECTED: stage change; a brand-new hypothesis: stage change
    cb.main(["start"]); led.open("a").write(_row("hyp-000001", "REJECTED", "validation") + _row("hyp-000002", "REJECTED")); cb.main(["done"])
    assert json.loads(cb.HIST.read_text().splitlines()[-1])["delta"]["stage_changes"] == 2


def test_scan_registered_and_bot_milestone_flip_are_movement(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    reg = tmp_path / "src" / "project_wide_multiplicity.py"
    cb.main(["start"]); reg.write_text(reg.read_text() + '    "scan_002_2026-01-02": {},\n'); cb.main(["done"])
    assert json.loads(cb.HIST.read_text().splitlines()[-1])["moved"] is True
    (tmp_path / "docs").mkdir()
    rm = tmp_path / "docs" / "BOT_ROADMAP.md"
    rm.write_text("| B8 | Live-Limited | **MISSING** | x |\n")
    cb.main(["start"]); rm.write_text("| B8 | Live-Limited | **DONE** | x |\n"); cb.main(["done"])
    last = json.loads(cb.HIST.read_text().splitlines()[-1])
    assert last["delta"]["bot_milestones_flipped"] == 1 and last["moved"] is True


def test_value_check_fails_on_three_stalled_cycles_and_on_exhausted_queue(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    (tmp_path / "data" / "pipeline_sweep.json").write_text(json.dumps({"rows": [{"tier": "OPEN", "next_owed": "Statistical"}], "shelf": "Shelf 3/3 live"}))
    for _ in range(3):
        cb.HIST.open("a").write(json.dumps({"moved": False, "delta": {}}) + "\n")
    res = ops_checks.check_value_per_cycle(); assert res.status == ops_checks.FAIL and "BUSY WORK" in res.detail
    cb.HIST.open("a").write(json.dumps({"moved": True, "delta": {"studies": 1}}) + "\n")
    assert ops_checks.check_value_per_cycle().status == ops_checks.PASS
    (tmp_path / "data" / "pipeline_sweep.json").write_text(json.dumps({"rows": [{"tier": "FROZEN", "next_owed": "nothing"}], "shelf": "Shelf 0/3 live () -> TOP-UP OWED"}))
    res = ops_checks.check_value_per_cycle(); assert res.status == ops_checks.PASS and "sourcing owed" in res.detail


def test_value_ack_downgrades_to_warn_and_expires_when_something_moves(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    (tmp_path / "data" / "pipeline_sweep.json").write_text(json.dumps({"rows": [{"tier": "FROZEN", "next_owed": "nothing"}], "shelf": "Shelf 0/3 live () -> TOP-UP OWED"}))
    assert ops_checks.check_value_per_cycle().status == ops_checks.PASS  # empty shelf is sourcing-owed, not exhausted (v2)
    (r / "_value_ack.json").write_text(json.dumps({"by": "Jason", "at": "2026-09-12T07:00:00+00:00", "reason": "map empty by choice"}))
    # busy-work path is also downgraded while acknowledged
    (tmp_path / "data" / "pipeline_sweep.json").write_text(json.dumps({"rows": [{"tier": "OPEN", "next_owed": "Statistical"}], "shelf": "Shelf 3/3 live"}))
    for _ in range(3):
        cb.HIST.open("a").write(json.dumps({"moved": False, "delta": {}, "finished": "2026-09-12T08:00:00+00:00"}) + "\n")
    assert ops_checks.check_value_per_cycle().status == ops_checks.WARN
    # a cycle that MOVES after the ack expires it; a fresh stall then FAILs again
    cb.HIST.open("a").write(json.dumps({"moved": True, "delta": {"studies": 1}, "finished": "2026-09-12T10:00:00+00:00"}) + "\n")
    assert ops_checks.check_value_per_cycle().status == ops_checks.PASS
    for _ in range(3):
        cb.HIST.open("a").write(json.dumps({"moved": False, "delta": {}, "finished": "2026-09-12T12:00:00+00:00"}) + "\n")
    assert ops_checks.check_value_per_cycle().status == ops_checks.FAIL


def test_shelf_starving_after_three_cycles_without_restock(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    (tmp_path / "data" / "pipeline_sweep.json").write_text(json.dumps({"rows": [], "shelf": "Shelf 0/3 DRAWABLE (Entry none; pending: none) -> SOURCING OWED"}))
    assert ops_checks.check_shelf_starving().status == ops_checks.WARN
    for _ in range(3):
        cb.HIST.open("a").write(json.dumps({"moved": True, "delta": {"inventory_entries": 0, "studies": 1}}) + "\n")
    assert ops_checks.check_shelf_starving().status == ops_checks.FAIL
    cb.HIST.open("a").write(json.dumps({"moved": True, "delta": {"inventory_entries": 1}}) + "\n")
    assert ops_checks.check_shelf_starving().status == ops_checks.WARN
    (tmp_path / "data" / "pipeline_sweep.json").write_text(json.dumps({"rows": [], "shelf": "Shelf 3/3 DRAWABLE (Entry 1, 2, 3; pending: none) -> next DRAW: Entry 1"}))
    assert ops_checks.check_shelf_starving().status == ops_checks.PASS
