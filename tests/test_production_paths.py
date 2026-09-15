"""Production write guard (Jason, refocus memo 7.3, September 15th): a test
cannot reach a production record even if tests/conftest.py's redirect fixture
were deleted, because every guarded writer refuses without TONY_PRODUCTION=1
and no test ever sets it."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import production_paths as pp  # noqa: E402
import research_ledger as rl  # noqa: E402
import bot_stack_paper_run as bpr  # noqa: E402
import order_path  # noqa: E402
import cycle_budget as cb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _snapshot(p: Path):
    return (p.stat().st_size, p.stat().st_mtime_ns) if p.exists() else None


def test_flag_is_unset_in_the_test_session():
    assert os.environ.get("TONY_PRODUCTION") != "1"
    assert not pp.production_enabled()


def test_protected_set_covers_the_execution_record_and_ledger():
    for rel in ("research/ledger/hypotheses.jsonl",
                "research/forward_validation/bot_stack_paper_log.jsonl",
                "research/forward_validation/order_path_journal/2026-09-15.jsonl",
                "research/forward_validation/b7_replay/replay_log.jsonl",
                "research/_batch_screen_state.json",
                "research/idea_inventory.md",
                "data/NQ_1min_databento_2026-09-14.csv"):
        assert pp.is_protected(ROOT / rel), rel
        assert pp.is_protected(rel), rel                      # relative spelling too
    assert not pp.is_protected(ROOT / "research" / "sessions" / "x.md")
    assert not pp.is_protected("/tmp/anything.jsonl")


def test_guard_refuses_protected_and_allows_tmp(tmp_path):
    with pytest.raises(pp.ProductionWriteRefused):
        pp.assert_writable(ROOT / "research" / "ledger" / "hypotheses.jsonl")
    assert pp.assert_writable(tmp_path / "hypotheses.jsonl") == tmp_path / "hypotheses.jsonl"


def test_ledger_append_is_refused_without_the_flag_even_at_the_real_path():
    """The real ledger, the real function, no monkeypatch: refused, untouched."""
    real = ROOT / "research" / "ledger" / "hypotheses.jsonl"
    before = _snapshot(real)
    with pytest.raises(pp.ProductionWriteRefused):
        rl.log_hypothesis(strategy_name="guard_probe", strategy_origin="external_claim", parameters={},
                          data_slice_used="discovery", trade_count=0, expectancy_r=0.0, profit_factor=0.0,
                          max_drawdown_r=0.0, strategy_status="REJECTED", notes="must never land",
                          ledger_path=real)
    assert _snapshot(real) == before


def test_live_execution_log_and_journal_refused_without_the_flag(monkeypatch):
    """Undo the conftest redirect on purpose: the guard alone must hold."""
    real_log = ROOT / "research" / "forward_validation" / "bot_stack_paper_log.jsonl"
    real_journal = ROOT / "research" / "forward_validation" / "order_path_journal"
    monkeypatch.setattr(bpr, "LOG_DIR", real_log.parent)
    monkeypatch.setattr(bpr, "LOG_PATH", real_log)
    before = _snapshot(real_log)
    with pytest.raises(pp.ProductionWriteRefused):
        bpr.append_row({"probe": True})
    assert _snapshot(real_log) == before
    j = order_path.OrderPathJournal(real_journal)
    files_before = sorted(p.name for p in real_journal.glob("*.jsonl")) if real_journal.exists() else []
    sizes_before = {p.name: p.stat().st_size for p in real_journal.glob("*.jsonl")} if real_journal.exists() else {}
    with pytest.raises(pp.ProductionWriteRefused):
        j.append("probe")
    assert sorted(p.name for p in real_journal.glob("*.jsonl")) == files_before
    assert {p.name: p.stat().st_size for p in real_journal.glob("*.jsonl")} == sizes_before


def test_cycle_history_refused_at_real_path_but_fine_in_tmp(tmp_path, monkeypatch):
    real = ROOT / "research" / "_cycle_history.jsonl"
    before = _snapshot(real)
    monkeypatch.setattr(cb, "CKPT", tmp_path / "ckpt.json")
    monkeypatch.setattr(cb, "HIST", real)
    (tmp_path / "ckpt.json").write_text(json.dumps({"status": "running", "started": "2026-09-15T00:00:00+00:00",
                                                    "budget_minutes": 105, "snapshot_at_start": {}}))
    with pytest.raises(pp.ProductionWriteRefused):
        cb.main(["done"])
    assert _snapshot(real) == before


def test_flag_opens_the_door_only_for_that_process(tmp_path, monkeypatch):
    """With the flag set (monkeypatched, restored after), a protected path is
    writable -- proving the mechanism is the flag and nothing else. The write
    itself still goes to tmp: we never touch the real record from a test."""
    monkeypatch.setenv("TONY_PRODUCTION", "1")
    assert pp.production_enabled()
    pp.assert_writable(ROOT / "research" / "ledger" / "hypotheses.jsonl")   # no raise
    monkeypatch.delenv("TONY_PRODUCTION")
    assert not pp.production_enabled()


def test_enable_production_is_not_called_at_import_time():
    """Importing every entry point must not set the flag; only their
    `if __name__ == '__main__'` blocks do."""
    for m in ("bot_stack_paper_run", "b7_replay", "bot_forward_log", "risk_state_engine",
              "forward_validate_h118_daily", "batch_screen", "cycle_budget", "cycle_close",
              "data_topup_databento"):
        __import__(m)
    assert not pp.production_enabled()
    for m in ("bot_stack_paper_run", "b7_replay", "bot_forward_log", "risk_state_engine",
              "forward_validate_h118_daily", "batch_screen", "cycle_budget", "cycle_close",
              "data_topup_databento", "data_fetch_databento", "study_prospective_exp047"):
        src = (ROOT / "src" / f"{m}.py").read_text()
        main_block = src[src.index('if __name__ == "__main__":'):]
        assert "enable_production()" in main_block, m
        assert "enable_production()" not in src[:src.index('if __name__ == "__main__":')], f"{m} enables production outside __main__"
