"""The strategy registry (standing directive 2026-09-15): append-only, one row
per stage event, latest row is the stage of record, production-guarded."""
from __future__ import annotations
import json, sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import strategy_registry as sr  # noqa: E402
import production_paths as pp  # noqa: E402


def _reg(tmp_path, monkeypatch):
    p = tmp_path / "strategies.jsonl"
    monkeypatch.setattr(sr, "REGISTRY", p)
    return p


def test_append_validates_stage_and_ids(tmp_path, monkeypatch):
    p = _reg(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        sr.append({"strategy_id": "S001", "name": "x", "stage": "NOT_A_STAGE"}, p)
    with pytest.raises(ValueError):
        sr.append({"name": "x", "stage": "SOURCE"}, p)
    row = sr.append({"strategy_id": "S001", "name": "x", "stage": "SOURCE"}, p)
    assert row["ts"] and json.loads(p.read_text().splitlines()[0])["stage"] == "SOURCE"


def test_freeze_needs_hashes_screen_needs_result_verdict_needs_verdict(tmp_path, monkeypatch):
    p = _reg(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        sr.append({"strategy_id": "S001", "name": "x", "stage": "FREEZE"}, p)
    sr.append({"strategy_id": "S001", "name": "x", "stage": "FREEZE", "spec_hash": {"spec": "a" * 64, "module": "b" * 64}}, p)
    with pytest.raises(ValueError):
        sr.append({"strategy_id": "S001", "name": "x", "stage": "SCREEN"}, p)
    sr.append({"strategy_id": "S001", "name": "x", "stage": "SCREEN", "screen_result": {"net_usd_1_micro": 1.0}}, p)
    with pytest.raises(ValueError):
        sr.append({"strategy_id": "S001", "name": "x", "stage": "KILL"}, p)
    sr.append({"strategy_id": "S001", "name": "x", "stage": "KILL", "verdict": "lost money: -3.1R over 40"}, p)
    assert sr.latest(sr.read_rows(p))["S001"]["stage"] == "KILL"


def test_latest_stage_queue_paper_and_salvage_views(tmp_path, monkeypatch):
    p = _reg(tmp_path, monkeypatch)
    sr.append({"strategy_id": "S001", "name": "a", "stage": "SOURCE", "priority": 1}, p)
    sr.append({"strategy_id": "S002", "name": "b", "stage": "SOURCE", "priority": 2}, p)
    sr.append({"strategy_id": "S003", "name": "c", "stage": "SOURCE", "priority": 3}, p)
    sr.append({"strategy_id": "S001", "name": "a", "stage": "SPECIFY"}, p)
    sr.append({"strategy_id": "S001", "name": "a", "stage": "FREEZE", "spec_hash": {"spec": "x", "module": "y"}}, p)
    sr.append({"strategy_id": "S001", "name": "a", "stage": "SCREEN", "screen_result": {"net_usd_1_micro": 5}}, p)
    sr.append({"strategy_id": "S001", "name": "a", "stage": "PAPER", "paper_log_name": "a_v1"}, p)
    sr.append({"strategy_id": "S003", "name": "c", "stage": "KILL", "verdict": "lost"}, p)
    rows = sr.read_rows(p)
    assert sr.stage_map(rows) == {"S001": "PAPER", "S002": "SOURCE", "S003": "KILL"}
    assert [r["strategy_id"] for r in sr.queue(rows)] == ["S002"]
    assert [r["strategy_id"] for r in sr.in_paper(rows)] == ["S001"]
    assert [r["strategy_id"] for r in sr.salvage_queue(rows)] == ["S003"]
    ev = sr.count_events(rows)
    assert ev["verdicts"] == 1 and ev["salvage_checks"] == 0
    sr.append({"strategy_id": "S003", "name": "c", "stage": "SALVAGE", "verdict": "nothing: no menu condition profitable"}, p)
    rows = sr.read_rows(p)
    assert sr.count_events(rows)["salvage_checks"] == 1 and sr.salvage_queue(rows) == []
    assert any("in paper: S001 PAPER" in ln for ln in sr.summary_lines(rows))


def test_queue_orders_by_director_priority_then_first_seen(tmp_path, monkeypatch):
    p = _reg(tmp_path, monkeypatch)
    sr.append({"strategy_id": "S002", "name": "b", "stage": "SOURCE"}, p)          # no priority -> last
    sr.append({"strategy_id": "S003", "name": "c", "stage": "SOURCE", "priority": 2}, p)
    sr.append({"strategy_id": "S001", "name": "a", "stage": "SOURCE", "priority": 1}, p)
    assert [r["strategy_id"] for r in sr.queue(sr.read_rows(p))] == ["S001", "S003", "S002"]


def test_registry_is_a_protected_production_path():
    assert pp.is_protected(sr.REGISTRY)
    assert pp.is_protected(pp.ROOT / "research" / "ledger" / "revamp_list.json")
    assert pp.is_protected(pp.ROOT / "research" / "infrastructure" / "strategy-specs" / "S001-x.md")
    with pytest.raises(pp.ProductionWriteRefused):
        sr.append({"strategy_id": "S999", "name": "never", "stage": "SOURCE"})   # default path, flag unset


def test_history_keeps_every_event_in_order(tmp_path, monkeypatch):
    p = _reg(tmp_path, monkeypatch)
    for st in ("SOURCE", "SPECIFY"):
        sr.append({"strategy_id": "S001", "name": "a", "stage": st}, p)
    sr.append({"strategy_id": "S002", "name": "b", "stage": "SOURCE"}, p)
    assert [r["stage"] for r in sr.history(sr.read_rows(p), "S001")] == ["SOURCE", "SPECIFY"]
