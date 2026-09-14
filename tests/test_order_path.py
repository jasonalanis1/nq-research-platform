"""tests/test_order_path.py -- BOT MILESTONE B4a. The order path against
SimulatedBroker: happy path, capital-protection block, partial fill, crash
recovery, and reconciliation-mismatch handling. Frozen spec:
research/infrastructure/b4a-order-path-spec.md"""
from datetime import datetime, timezone

import pytest

import capital_protection
from broker_interface import BrokerDisconnected, Fill
from order_path import OrderPath, ReconciliationError
from simulated_broker import SimulatedBroker
from strategy_contract import Signal, risk_multiple


def _signal(direction="long", entry=100.0, stop=98.0, target=104.0):
    return Signal(strategy_name="base_entry_b3_orb_placeholder", strategy_version="B3-1.0",
                   timestamp=datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc), instrument="MNQ",
                   timeframe="1m", direction=direction, entry=entry, stop=stop, target=target,
                   risk_multiple=risk_multiple(entry, stop, target), validation_status="placeholder")


def _passing_today(strategy="b4a_test"):
    # remaining_budget_usd must be > 0: capital_protection.daily_loss_cap_hit()
    # fail-closes (returns True) at remaining_budget_usd <= 0, by design.
    return dict(strategy=strategy, paper_trades=0, paper_slippage_measured=False, paper_net_usd=0.0,
                per_trade_swing_usd=100.0, equity_usd=0.0, peak_profit_usd=0.0, remaining_budget_usd=300.0,
                day_pnl_usd=0.0, working_edge_pts=10.0, live_signals_today=[], reference_signals_today=[])


def test_happy_path_ack_fill_reconcile_and_journal(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    path = OrderPath(broker, journal_dir=tmp_path)
    result = path.submit_signal(_signal(), today=_passing_today())
    assert result["status"] == "filled"
    assert result["filled_qty"] == 1
    events = [r["event"] for r in path.journal.all_records()]
    assert events == ["order_intent", "order_ack", "fill"]


def test_capital_protection_blocks_before_any_order_reaches_broker(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    path = OrderPath(broker, journal_dir=tmp_path)
    today = _passing_today(strategy="H118")   # excluded strategy -> budget 0 -> blocked
    result = path.submit_signal(_signal(), today=today)
    assert result["status"] == "blocked"
    assert any("H118" in r or "fundable" in r for r in result["reasons"])
    events = [r["event"] for r in path.journal.all_records()]
    assert events == ["blocked"]
    assert broker.get_positions() == {}   # nothing was ever submitted


def test_rejected_order_is_journaled_and_never_fills(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    broker.force_reject()
    path = OrderPath(broker, journal_dir=tmp_path)
    result = path.submit_signal(_signal(), today=_passing_today())
    assert result["status"] == "rejected"
    events = [r["event"] for r in path.journal.all_records()]
    assert events == ["order_intent", "order_rejected"]


def test_partial_fill_polls_to_completion(tmp_path):
    # The frozen cap is 1 contract; raise it here only to exercise the
    # multi-fill polling loop (order_path.submit_signal's own cap logic is
    # covered separately -- see test_contracts_capped_at_capital_config_max).
    # pre_order_check binds its `cfg` default arg to this SAME CONFIG object
    # at import time, so the field is mutated in place (object.__setattr__,
    # bypassing the frozen dataclass) and restored in `finally` -- replacing
    # the module attribute with a new instance would not reach that bound
    # default.
    original = capital_protection.CONFIG.max_contracts
    object.__setattr__(capital_protection.CONFIG, "max_contracts", 4)
    try:
        broker = SimulatedBroker(seed=1)
        broker.connect()
        broker.force_partial(0.5)   # applies once, to the FIRST fill() call only
        path = OrderPath(broker, journal_dir=tmp_path)
        result = path.submit_signal(_signal(), today=_passing_today(), size_multiplier=4.0)
        assert result["requested_qty"] == 4
        assert result["status"] == "filled"
        assert result["filled_qty"] == 4
        assert len(result["fills"]) == 2             # first partial (2), then the remainder (2)
        assert result["fills"][0]["is_partial"] is True
        assert result["fills"][1]["remaining_qty"] == 0
    finally:
        object.__setattr__(capital_protection.CONFIG, "max_contracts", original)


def test_contracts_capped_at_capital_config_max(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    path = OrderPath(broker, journal_dir=tmp_path)
    result = path.submit_signal(_signal(), today=_passing_today(), size_multiplier=5.0)
    assert result["requested_qty"] == 1   # CapitalConfig.max_contracts is frozen at 1


def test_fill_deviation_recorded_never_assumed_zero(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    path = OrderPath(broker, journal_dir=tmp_path)
    signal = _signal(direction="long", entry=100.0, stop=98.0, target=104.0)
    result = path.submit_signal(signal, today=_passing_today(), price_source=100.75)
    fill_record = [r for r in result["journal"] if r["event"] == "fill"][0]
    assert fill_record["intended_price"] == 100.0
    assert fill_record["price"] == 100.75
    assert fill_record["deviation_pts"] == pytest.approx(0.75)
    assert fill_record["deviation_r"] == pytest.approx(0.75 / 2.0)


def test_crash_recovery_completes_an_unresolved_order(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    signal = _signal()

    # Simulate: the order actually reached the broker and was filled, but the
    # process crashed before the ack/fill were ever journaled -- only the
    # pre-submission intent made it to disk.
    path = OrderPath(broker, journal_dir=tmp_path)
    order_id = "B4A-CRASHTEST"
    path.journal.append("order_intent", order_id=order_id, instrument="MNQ", direction="long",
                         quantity=1, intended_price=signal.entry, stop_distance=2.0, strategy="b4a_test",
                         client_tag="crash-test")
    from broker_interface import Order
    order = Order(order_id=order_id, instrument="MNQ", direction="long", quantity=1, order_type="market",
                   intended_price=signal.entry, submitted_at=datetime.now(timezone.utc), client_tag="crash-test")
    broker.submit_order(order)
    broker.fill(order_id, price_source=100.5)

    # A fresh OrderPath (simulating a restart) against the same journal + broker.
    fresh = OrderPath(broker, journal_dir=tmp_path)
    actions = fresh.recover()
    assert len(actions) == 1
    assert actions[0]["action"] == "reconciled_from_broker"
    fill_events = [r for r in fresh.journal.all_records() if r["event"] == "fill" and r["order_id"] == order_id]
    assert len(fill_events) == 1
    assert fill_events[0]["quantity"] == 1
    # calling recover() again is a no-op -- the order is now resolved
    assert fresh.recover() == []


def test_recovery_escalates_when_broker_is_unreachable(tmp_path):
    class UnreachableBroker(SimulatedBroker):
        def get_fills(self, order_id):
            raise BrokerDisconnected("simulated: broker unreachable during recovery")

    broker = UnreachableBroker(seed=1)
    broker.connect()
    path = OrderPath(broker, journal_dir=tmp_path)
    path.journal.append("order_intent", order_id="B4A-UNREACHABLE", instrument="MNQ", direction="long",
                         quantity=1, intended_price=100.0, stop_distance=2.0, strategy="b4a_test",
                         client_tag="unreachable-test")
    actions = path.recover()
    assert len(actions) == 1
    assert actions[0]["action"] == "ESCALATE_broker_unreachable"


def test_reconciliation_mismatch_raises_never_silently_accepted(tmp_path):
    class LyingBroker(SimulatedBroker):
        def get_positions(self):
            return {}   # always claims flat, even after a fill -- the mismatch case

    broker = LyingBroker(seed=1)
    broker.connect()
    path = OrderPath(broker, journal_dir=tmp_path)
    with pytest.raises(ReconciliationError):
        path.submit_signal(_signal(), today=_passing_today())
    mismatch_events = [r for r in path.journal.all_records() if r["event"] == "reconciliation_mismatch"]
    assert len(mismatch_events) == 1


def test_disconnect_mid_order_is_escalated_not_swallowed(tmp_path):
    broker = SimulatedBroker(seed=1)
    broker.connect()
    broker.force_disconnect_after_next_ack()
    path = OrderPath(broker, journal_dir=tmp_path)
    result = path.submit_signal(_signal(), today=_passing_today())
    assert result["status"] == "escalate"
    events = [r["event"] for r in result["journal"]]
    assert events == ["order_intent", "order_ack", "recovery_action"]
