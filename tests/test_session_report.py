"""Actual usage in the owner's briefing (Jason, refocus s.6, Sept 15th): the
OPERATIONS section prints this cycle's minutes from the budget clock and the
day's cycles + minutes from the compliance log. Read, never estimated."""
from __future__ import annotations
import json, sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import session_report as sr  # noqa: E402

UTC = ZoneInfo("UTC")


def _wire(tmp_path, monkeypatch):
    (tmp_path / "research").mkdir()
    monkeypatch.setattr(sr, "PROJ", tmp_path)
    return tmp_path / "research"


def test_cycle_minutes_from_checkpoint_done_and_running(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    t0 = datetime(2026, 9, 15, 14, 0, tzinfo=UTC)
    (r / "_cycle_checkpoint.json").write_text(json.dumps({
        "status": "done", "started": t0.isoformat(), "finished": (t0 + timedelta(minutes=47)).isoformat(),
        "budget_minutes": 105}))
    u = sr.cycle_minutes_used(now=t0 + timedelta(hours=5))
    assert round(u["minutes"]) == 47 and u["closed"] and u["budget"] == 105
    (r / "_cycle_checkpoint.json").write_text(json.dumps({"status": "running", "started": t0.isoformat(), "budget_minutes": 105}))
    u = sr.cycle_minutes_used(now=t0 + timedelta(minutes=12))
    assert round(u["minutes"]) == 12 and not u["closed"]
    assert sr.cycle_minutes_used() is not None
    (r / "_cycle_checkpoint.json").unlink()
    assert sr.cycle_minutes_used() is None


def test_day_usage_counts_distinct_cycles_today_and_sums_actual_minutes(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    now = datetime(2026, 9, 15, 20, 0, tzinfo=sr.CT)          # 8 pm CT
    def row(label, start_ct, mins, complete=True):
        st = start_ct.astimezone(UTC)
        return json.dumps({"label": label, "cycle_started": st.isoformat(),
                           "closed_at": (st + timedelta(minutes=mins)).isoformat(), "complete": complete})
    rows = [
        row("yesterday 11 pm", now.replace(hour=23) - timedelta(days=1), 40),   # not today
        row("9:00 am cycle", now.replace(hour=9), 31),
        row("11:00 am cycle", now.replace(hour=11), 58),
        row("11:00 am cycle", now.replace(hour=11), 63),                        # re-run close: same cycle, last row wins
        json.dumps({"label": "1:00 pm cycle", "closed_at": now.replace(hour=13).astimezone(UTC).isoformat(), "complete": False}),  # no start recorded
    ]
    (r / "_cycle_compliance.jsonl").write_text("\n".join(rows) + "\n")
    d = sr.day_usage(now=now)
    assert d["cycles"] == 3
    assert round(d["minutes"]) == 31 + 63
    assert d["unknown"] == 1
    assert d["labels"] == ["9:00 am cycle", "11:00 am cycle", "1:00 pm cycle"]


def test_operations_section_prints_the_numbers_not_estimates(tmp_path, monkeypatch):
    r = _wire(tmp_path, monkeypatch)
    t0 = datetime.now(UTC) - timedelta(minutes=33)
    (r / "_cycle_checkpoint.json").write_text(json.dumps({"status": "done", "started": t0.isoformat(),
                                                         "finished": (t0 + timedelta(minutes=33)).isoformat(), "budget_minutes": 105}))
    (r / "_cycle_compliance.jsonl").write_text(json.dumps({
        "label": "9:00 am cycle", "cycle_started": t0.isoformat(), "closed_at": (t0 + timedelta(minutes=33)).isoformat(),
        "complete": True, "failing": [], "checks": {"tests": {"detail": "500 passed"}, "git": {"ok": True}}}) + "\n")
    text = "\n".join(sr.operations())
    assert "This session used: **33 minutes** of the 105-minute budget" in text
    assert "1 cycle(s) run, 33 minutes used" in text
    assert "not estimated" in text
    assert "Test suite: **500 passed**" in text


def _trade(day, strategy, r, risk=20.0):
    return {"date": day, "strategy": strategy, "outcome": "filled", "pnl_usd": r * risk * 2.0,
            "signal": {"direction": "long"}, "order_path": {"filled_qty": 1},
            "bookkeeping": {"risk_points": risk, "r_multiple": r, "exit_reason": "target" if r > 0 else "stop"}}


def test_paper_book_section_lists_candidates_and_labels_plumbing(tmp_path, monkeypatch):
    """Standing directive s.5 (Sept 15th): the owner's briefing gains a PAPER BOOK
    section, per strategy, plain language; plumbing rows are one line, never judged."""
    import paper_book as pb, strategy_registry as srg
    log = tmp_path / "log.jsonl"; reg = tmp_path / "reg.jsonl"
    monkeypatch.setattr(pb, "LOG", log); monkeypatch.setattr(srg, "REGISTRY", reg)
    log.write_text("\n".join(json.dumps(r) for r in [
        _trade("2026-09-08", "execution_dummy_4x_placeholder", 1.0),
        _trade("2026-09-08", "s001_lsr", 1.35), _trade("2026-09-09", "s001_lsr", -1.0)]) + "\n")
    srg.append({"strategy_id": "S001", "name": "Level Sweep Reversal", "stage": "PAPER", "paper_log_name": "s001_lsr"}, reg)
    srg.append({"strategy_id": "S002", "name": "Overnight split", "stage": "SOURCE", "priority": 2}, reg)
    text = "\n".join(sr.paper_book_section())
    assert text.startswith("**1b. PAPER BOOK")
    assert "**S001 Level Sweep Reversal**" in text and "2 trades" in text
    assert "1 / 5 / 10 micros" in text and "ASSUMED" in text and "Win rate 50%" in text
    assert "Plumbing (not a candidate, never judged): execution_dummy_4x_placeholder" in text
    assert "Candidate queue" in text and "**S002**" in text


def test_paper_book_comes_right_after_money(monkeypatch):
    calls = []
    for name in ("money", "paper_book_section", "product", "pipeline", "operations", "your_desk"):
        monkeypatch.setattr(sr, name, (lambda n: (lambda *a, **k: calls.append(n) or [f"[{n}]"]))(name))
    out = sr.build("9:00 pm", "moved", "agents")
    assert calls[:2] == ["money", "paper_book_section"]
    assert out.index("[money]") < out.index("[paper_book_section]") < out.index("[product]")


# --- PIPELINE reads the STRATEGY REGISTRY, not only the hypothesis ledger -----
# Under the standing directive of September 15th 2026 every stage change is a row
# in research/ledger/strategies.jsonl. Reading only the old hypothesis ledger made
# this section report "nothing moved / the funnel is empty" on cycles that froze,
# screened, salvaged and killed a strategy (caught 2026-09-16).

def _wire_pipeline(tmp_path, monkeypatch, registry_rows, ledger_rows=()):
    import strategy_registry as _sr
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "research" / "ledger").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "pipeline_sweep.json").write_text(json.dumps({"rows": [], "shelf": "Shelf 0/3 DRAWABLE"}))
    led = tmp_path / "research" / "ledger" / "hypotheses.jsonl"
    led.write_text("".join(json.dumps(r) + "\n" for r in ledger_rows))
    reg = tmp_path / "research" / "ledger" / "strategies.jsonl"
    reg.write_text("".join(json.dumps(r) + "\n" for r in registry_rows))
    monkeypatch.setattr(sr, "PROJ", tmp_path)
    monkeypatch.setattr(_sr, "REGISTRY", reg)
    start = datetime.now().replace(tzinfo=None) - timedelta(minutes=30)
    monkeypatch.setattr(sr, "_cycle_start", lambda: start, raising=False)
    return reg


def _ts(minutes_ago: int) -> str:
    return (datetime.now(UTC) - timedelta(minutes=minutes_ago)).isoformat()


def test_pipeline_reports_registry_stage_changes_when_the_hypothesis_ledger_is_silent(tmp_path, monkeypatch):
    rows = [
        {"strategy_id": "S009", "name": "VWAP completion", "stage": "FREEZE", "ts": _ts(20)},
        {"strategy_id": "S009", "name": "VWAP completion", "stage": "SCREEN", "ts": _ts(15)},
        {"strategy_id": "S009", "name": "VWAP completion", "stage": "KILL",
         "verdict": "KILL -- lost money at SCREEN", "ts": _ts(10)},
    ]
    _wire_pipeline(tmp_path, monkeypatch, rows)
    out = "\n".join(sr.pipeline())
    assert "strategy registry" in out
    assert "S009" in out and "**FREEZE**" in out and "**SCREEN**" in out and "**KILL**" in out
    assert "Nothing. No candidate had input" not in out


def test_pipeline_in_flight_counts_the_registry_queue_and_the_paper_book(tmp_path, monkeypatch):
    rows = [
        {"strategy_id": "S008", "name": "Late-day rebalance", "stage": "PAPER", "slow": False, "ts": _ts(5000)},
        {"strategy_id": "S002", "name": "Overnight carry", "stage": "PAPER", "slow": True, "ts": _ts(5000)},
        {"strategy_id": "S004", "name": "H118 lineage", "stage": "SOURCE", "ts": _ts(5000)},
    ]
    _wire_pipeline(tmp_path, monkeypatch, rows)
    out = "\n".join(sr.pipeline())
    assert "*In flight (3 strategies):*" in out
    assert "S008" in out and "S002" in out and "S004" in out
    assert "[SLOW — background, no queue slot]" in out          # Amendment 1's label survives
    assert "the funnel is empty" not in out
    # a SOURCE row is owed its SPECIFY, and the section says so
    assert "owed next: SPECIFY" in out


def test_pipeline_says_so_only_when_the_registry_is_genuinely_empty(tmp_path, monkeypatch):
    _wire_pipeline(tmp_path, monkeypatch, [])
    out = "\n".join(sr.pipeline())
    assert "*In flight (0 strategies):*" in out
    assert "interrupt reason 2" in out                           # s.10, not a silent empty funnel


def test_pipeline_keeps_the_hypothesis_ledger_as_historical_context(tmp_path, monkeypatch):
    """The 159 hypotheses are still the all-time denominator in 'the odds'."""
    led = [{"hypothesis_id": "hyp-000001", "strategy_name": "old_thing",
            "strategy_status": "REJECTED", "logged_at": _ts(100000), "parameters": {}}]
    rows = [{"strategy_id": "S008", "name": "Late-day rebalance", "stage": "PAPER", "ts": _ts(5000)}]
    _wire_pipeline(tmp_path, monkeypatch, rows, led)
    out = "\n".join(sr.pipeline())
    assert "Tested and closed, all time: **1** of 1 logged" in out
