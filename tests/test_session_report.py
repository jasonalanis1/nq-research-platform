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
