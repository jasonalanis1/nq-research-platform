"""The paper book (standing directive s.5/s.6/s.11): per-strategy record, net of
ASSUMED costs, plumbing separated and never judged."""
from __future__ import annotations
import json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import paper_book as pb  # noqa: E402
import strategy_registry as sr  # noqa: E402


def _trade(day, strategy, r, risk=20.0, qty=1):
    return {"date": day, "strategy": strategy, "outcome": "filled", "pnl_usd": r * risk * 2.0 * qty,
            "signal": {"direction": "long"}, "order_path": {"filled_qty": qty},
            "bookkeeping": {"risk_points": risk, "r_multiple": r, "exit_reason": "target" if r > 0 else "stop"}}


def test_assumed_cost_basis_is_the_repo_constants_on_a_micro():
    # $2.50/side commission + 1 tick/side slippage on a $2/pt micro = $6.00 = 3.0 pts
    assert pb.ASSUMED_COST_USD_PER_MICRO_RT == 6.0
    assert pb.ASSUMED_COST_PTS_RT == 3.0
    assert pb.SLIPPAGE_BASIS == "ASSUMED"


def test_trades_are_net_of_assumed_costs_and_per_micro():
    rows = [_trade("2026-09-08", "s1", 1.0, risk=20.0, qty=2)]      # +$80 gross for 2 micros
    t = pb.trades_for(rows, "s1")
    assert len(t) == 1 and t[0]["usd_gross_1"] == 40.0 and t[0]["usd_net_1"] == 34.0
    assert abs(t[0]["r_net"] - 0.85) < 1e-9


def test_measure_every_s5_number():
    rows = [_trade("2026-09-01", "s1", 1.0), _trade("2026-09-02", "s1", -1.0), _trade("2026-09-03", "s1", -1.0),
            _trade("2026-09-04", "s1", 1.35), _trade("2026-09-05", "s1", -1.0)]
    m = pb.measure(pb.trades_for(rows, "s1"), "2026-09-01", today=date(2026, 9, 15))
    assert m["trades"] == 5 and m["days_elapsed"] == 14
    assert m["trades_to_judgment"] == 35 and m["weeks_to_judgment"] == 4.0 and not m["at_judgment_point"]
    assert m["win_rate"] == 0.4
    # net R: (0.85 -1.15 -1.15 +1.2 -1.15)/5
    assert abs(m["avg_r"] - (0.85 - 1.15 - 1.15 + 1.2 - 1.15) / 5) < 1e-6
    assert m["usd_net"]["5"] == 5 * m["usd_net"]["1"] and m["usd_net"]["10"] == 10 * m["usd_net"]["1"]
    assert m["worst_losing_streak"]["trades"] == 2 and m["worst_losing_streak"]["usd_1"] == -92.0
    sv = m["survivable_daily_limit"]
    assert sv["daily_limit_usd_1"] == round(3 * (34.0 + 48.0) / 2, 2) and sv["worst_streak_inside_limit"] is True
    assert m["slippage"] == "ASSUMED" and m["cost_fragile"] is True


def test_judgment_point_by_trades_and_by_weeks():
    rows = [_trade(f"2026-08-{d:02d}", "s1", 0.5) for d in range(1, 29)] + [_trade(f"2026-09-{d:02d}", "s1", 0.5) for d in range(1, 13)]
    m = pb.measure(pb.trades_for(rows, "s1"), "2026-08-01", today=date(2026, 9, 12))
    assert m["trades"] == 40 and m["at_judgment_point"] and "40 trades" in m["judgment_reason"]
    few = [_trade("2026-07-01", "s1", 0.5)]
    m2 = pb.measure(pb.trades_for(few, "s1"), "2026-07-01", today=date(2026, 9, 15))
    assert m2["at_judgment_point"] and "weeks" in m2["judgment_reason"] and "KILL" in m2["judgment_reason"]


def test_book_separates_plumbing_from_candidates(tmp_path, monkeypatch):
    log = tmp_path / "log.jsonl"; reg = tmp_path / "reg.jsonl"
    monkeypatch.setattr(pb, "LOG", log); monkeypatch.setattr(sr, "REGISTRY", reg)
    rows = [_trade("2026-09-08", "execution_dummy_4x_placeholder", 1.0), _trade("2026-09-08", "s001_x", -1.0),
            {"date": "2026-09-09", "strategy": "s001_x", "outcome": "no_signal"},
            {"date": "2026-09-08", "outcome": "blocked"}]   # a B3 row (no strategy field)
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    sr.append({"strategy_id": "S001", "name": "X", "stage": "PAPER", "paper_log_name": "s001_x", "ts": "2026-09-08T00:00:00"}, reg)
    sr.append({"strategy_id": "S002", "name": "Y", "stage": "SOURCE"}, reg)
    bk = pb.book(today=date(2026, 9, 15))
    assert [s["strategy_id"] for s in bk["strategies"]] == ["S001"]
    s = bk["strategies"][0]
    assert s["trades"] == 1 and s["sessions_scored"] == 2 and s["usd_net"]["1"] == -46.0
    names = {p["paper_log_name"] for p in bk["plumbing"]}
    assert names == {"execution_dummy_4x_placeholder", "base_entry_b3_orb_placeholder"}
    assert all("never judged" in p["label"] for p in bk["plumbing"])
    text = "\n".join(pb.plain_lines(bk))
    assert "S001 X" in text and "Plumbing (not a candidate, never judged)" in text and "ASSUMED" in text
    assert "1 / 5 / 10 micros" in text


def test_empty_book_says_so(tmp_path, monkeypatch):
    monkeypatch.setattr(pb, "LOG", tmp_path / "none.jsonl"); monkeypatch.setattr(sr, "REGISTRY", tmp_path / "none2.jsonl")
    bk = pb.book()
    assert bk["strategies"] == [] and bk["plumbing"] == []
    assert "empty" in pb.plain_lines(bk)[0]
