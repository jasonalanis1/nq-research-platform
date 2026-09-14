"""tests/test_simulated_broker.py -- BOT MILESTONE B4a. One deterministic test
per failure mode SimulatedBroker exists to exercise (AMENDMENT v3.1 S4, the 14
execution checks this milestone must survive), plus a seeded soak test."""
from datetime import datetime, timezone

import pytest

from broker_interface import BrokerDisconnected, Order
from simulated_broker import SimulatedBroker


def _order(order_id="O1", qty=1, direction="long", price=100.0):
    return Order(order_id=order_id, instrument="MNQ", direction=direction, quantity=qty,
                 order_type="market", intended_price=price,
                 submitted_at=datetime(2026, 9, 14, 10, 0, 0, tzinfo=timezone.utc), client_tag="t")


def test_disconnected_broker_raises_on_every_method():
    b = SimulatedBroker(seed=1)
    with pytest.raises(BrokerDisconnected):
        b.submit_order(_order())
    with pytest.raises(BrokerDisconnected):
        b.get_positions()


def test_normal_submit_ack_fill_reconcile():
    b = SimulatedBroker(seed=1)
    b.connect()
    o = _order(price=100.0)
    ack = b.submit_order(o)
    assert ack.status == "acknowledged"
    assert ack.broker_order_id is not None
    assert ack.latency_s == 0.0
    fills = b.fill(o.order_id, price_source=100.25)
    assert len(fills) == 1
    assert fills[0].quantity == 1
    assert fills[0].remaining_qty == 0
    assert fills[0].price == 100.25
    pos = b.get_positions()["MNQ"]
    assert pos.quantity == 1
    assert pos.avg_price == 100.25


def test_deterministic_reject():
    b = SimulatedBroker(seed=1)
    b.connect()
    b.force_reject()
    ack = b.submit_order(_order())
    assert ack.status == "rejected"
    assert ack.broker_order_id is None
    assert b.get_fills(_order().order_id) == []


def test_deterministic_partial_fill_then_completion():
    b = SimulatedBroker(seed=1)
    b.connect()
    o = _order(qty=4)
    b.submit_order(o)
    b.force_partial(0.5)
    fills1 = b.fill(o.order_id, price_source=100.0)
    assert len(fills1) == 1
    assert fills1[0].quantity == 2
    assert fills1[0].is_partial is True
    assert fills1[0].remaining_qty == 2
    # broker "catches up" -- no override this time, fills the remainder
    fills2 = b.fill(o.order_id, price_source=100.5)
    assert fills2[0].quantity == 2
    assert fills2[0].remaining_qty == 0
    status = b.order_status(o.order_id)
    assert status["filled_qty"] == 4


def test_disconnect_mid_order_then_reconnect_recovers_visibility():
    b = SimulatedBroker(seed=1)
    b.connect()
    o = _order()
    b.force_disconnect_after_next_ack()
    ack = b.submit_order(o)
    assert ack.status == "acknowledged"          # the ack itself succeeded
    assert b.is_connected() is False              # but the connection is now down
    with pytest.raises(BrokerDisconnected):
        b.get_fills(o.order_id)                   # every call fails while down -- proves the path
                                                   # cannot silently assume a fill happened
    b.connect()
    fills = b.fill(o.order_id, price_source=100.0)
    assert len(fills) == 1                        # order state survived the outage


def test_deterministic_late_ack_reports_honest_latency():
    b = SimulatedBroker(seed=1)
    b.connect()
    b.force_late_ack(3.5)
    ack = b.submit_order(_order())
    assert ack.latency_s == 3.5
    assert ack.ack_at > _order().submitted_at


def test_cancel_stops_further_fills():
    b = SimulatedBroker(seed=1)
    b.connect()
    o = _order(qty=2)
    b.submit_order(o)
    assert b.cancel_order(o.order_id) is True
    fills = b.fill(o.order_id, price_source=100.0)
    assert fills == []
    assert b.cancel_order(o.order_id) is False   # already cancelled -- no double-cancel


def test_short_position_is_negative_quantity():
    b = SimulatedBroker(seed=1)
    b.connect()
    o = _order(direction="short", qty=1)
    b.submit_order(o)
    b.fill(o.order_id, price_source=100.0)
    assert b.get_positions()["MNQ"].quantity == -1


def test_seeded_soak_run_is_reproducible():
    def run(seed):
        b = SimulatedBroker(seed=seed, reject_rate=0.3, partial_fill_rate=0.4, late_ack_rate=0.3)
        b.connect()
        outcomes = []
        for i in range(30):
            o = _order(order_id=f"O{i}", qty=2)
            ack = b.submit_order(o)
            outcomes.append((ack.status, round(ack.latency_s, 3)))
            if ack.status == "acknowledged":
                fills = b.fill(o.order_id, price_source=100.0)
                fills2 = b.fill(o.order_id, price_source=100.0) if fills and fills[0].remaining_qty else []
                outcomes.append(tuple((f.quantity, f.is_partial) for f in fills + fills2))
        return outcomes

    assert run(42) == run(42)          # same seed -> identical outcome sequence
    assert run(42) != run(7)           # different seed -> not trivially identical
