"""Tests for src/execution_measurement.py (BOT MILESTONE B5, first cut)."""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import execution_measurement as em  # noqa: E402
from order_path import OrderPath  # noqa: E402
from simulated_broker import SimulatedBroker  # noqa: E402
from strategy_contract import Signal, risk_multiple  # noqa: E402


def _signal():
    return Signal(strategy_name="base_entry_b3_orb_placeholder", strategy_version="B3-1.0",
                   timestamp=datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc), instrument="MNQ",
                   timeframe="1m", direction="long", entry=100.0, stop=98.0, target=104.0,
                   risk_multiple=risk_multiple(100.0, 98.0, 104.0), validation_status="placeholder")


def _today():
    return dict(strategy="b4a_test", paper_trades=0, paper_slippage_measured=False, paper_net_usd=0.0,
                per_trade_swing_usd=100.0, equity_usd=0.0, peak_profit_usd=0.0, remaining_budget_usd=300.0,
                day_pnl_usd=0.0, working_edge_pts=10.0, live_signals_today=[], reference_signals_today=[])


def test_empty_journal_reports_insufficient_sample_never_a_false_pass(tmp_path):
    out = em.measure(tmp_path)
    assert out["n_order_intents"] == 0
    numeric_checks = [c for c in out["checks"] if "n" in c]
    assert all(c["status"] == "INSUFFICIENT SAMPLE" for c in numeric_checks)


def test_happy_path_order_scores_all_measurable_checks_pass(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    path = OrderPath(broker, journal_dir=tmp_path)
    path.submit_signal(_signal(), today=_today(), price_source=100.5)

    out = em.measure(tmp_path)
    by_name = {c["check"]: c for c in out["checks"]}
    assert by_name["3. Correct order generated"]["status"] == "PASS"
    assert by_name["4. Correct quantity generated"]["status"] == "PASS"
    assert by_name["5. Entry/exit instructions correct"]["status"] == "PASS"
    assert by_name["6. Orders reach the broker"]["status"] == "PASS"
    assert by_name["7. Fills are recorded"]["status"] == "PASS"
    assert by_name["8. Expected vs. actual fill measured"]["status"] == "PASS"
    assert by_name["9. Slippage measured, not assumed"]["status"] == "PASS"
    assert by_name["10. Latency measured"]["status"] == "PASS"
    assert by_name["12. Position state reconciled"]["status"] == "PASS"
    assert by_name["14. Everything logged for reconstruction"]["status"] == "PASS"
    assert out["stage_3_qualified"] is False   # never self-authorizes a stage transition


def test_rejected_order_is_counted_not_hidden(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    broker.force_reject()
    path = OrderPath(broker, journal_dir=tmp_path)
    path.submit_signal(_signal(), today=_today())

    out = em.measure(tmp_path)
    assert out["n_rejected"] == 1
    by_name = {c["check"]: c for c in out["checks"]}
    # a rejected order never reaches a fill -- check 7's denominator excludes it
    assert by_name["7. Fills are recorded"]["status"] == "INSUFFICIENT SAMPLE"
    reject_check = by_name["11. Rejected/missed/duplicate orders detected"]
    assert reject_check["n_rejected_observed"] == 1


def test_recovery_actions_are_counted(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    path = OrderPath(broker, journal_dir=tmp_path)
    path.journal.append("order_intent", order_id="ORPHAN-1", instrument="MNQ", direction="long",
                         quantity=1, intended_price=100.0, stop_distance=2.0, strategy="b4a_test",
                         client_tag="orphan")
    from broker_interface import Order
    broker.submit_order(Order(order_id="ORPHAN-1", instrument="MNQ", direction="long", quantity=1,
                               order_type="market", intended_price=100.0,
                               submitted_at=datetime.now(timezone.utc), client_tag="orphan"))
    broker.fill("ORPHAN-1", price_source=100.0)
    path.recover()

    out = em.measure(tmp_path)
    assert out["n_recovery_actions"] == 1
    by_name = {c["check"]: c for c in out["checks"]}
    assert by_name["13. Crash cannot silently leave a position open"]["recovery_action_records"] == 1
    assert by_name["6. Orders reach the broker"]["status"] == "PASS"   # counted via recovery, not hidden
