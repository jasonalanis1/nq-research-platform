"""tests/test_broker_interface.py -- BOT MILESTONE B4a. Dataclass field/shape
sanity for the broker contract itself (src/broker_interface.py)."""
from datetime import datetime, timezone

import pytest

from broker_interface import BrokerInterface, Fill, Order, OrderAck, Position


def test_order_as_dict_roundtrips_fields():
    o = Order(order_id="O1", instrument="MNQ", direction="long", quantity=1,
               order_type="market", intended_price=100.0,
               submitted_at=datetime(2026, 9, 14, tzinfo=timezone.utc), client_tag="tag")
    d = o.as_dict()
    assert d["order_id"] == "O1"
    assert d["instrument"] == "MNQ"
    assert d["direction"] == "long"
    assert d["quantity"] == 1
    assert isinstance(d["submitted_at"], str)


def test_order_ack_latency_and_status():
    ack = OrderAck(order_id="O1", broker_order_id="B1", status="acknowledged", reason=None,
                    ack_at=datetime(2026, 9, 14, 0, 0, 2, tzinfo=timezone.utc), latency_s=2.0)
    assert ack.status == "acknowledged"
    assert ack.latency_s == 2.0
    d = ack.as_dict()
    assert isinstance(d["ack_at"], str)


def test_rejected_ack_has_no_broker_order_id():
    ack = OrderAck(order_id="O1", broker_order_id=None, status="rejected", reason="no reason given",
                    ack_at=datetime(2026, 9, 14, tzinfo=timezone.utc), latency_s=0.0)
    assert ack.broker_order_id is None
    assert ack.status == "rejected"


def test_fill_partial_flag_and_remaining():
    f = Fill(order_id="O1", broker_order_id="B1", fill_id="F1", quantity=1, price=100.5,
              filled_at=datetime(2026, 9, 14, tzinfo=timezone.utc), is_partial=True, remaining_qty=1)
    assert f.is_partial is True
    assert f.remaining_qty == 1
    d = f.as_dict()
    assert isinstance(d["filled_at"], str)


def test_position_signed_quantity():
    long_pos = Position(instrument="MNQ", quantity=2, avg_price=100.0)
    short_pos = Position(instrument="MNQ", quantity=-1, avg_price=100.0)
    assert long_pos.quantity > 0
    assert short_pos.quantity < 0
    assert long_pos.as_dict()["instrument"] == "MNQ"


def test_broker_interface_is_abstract():
    with pytest.raises(TypeError):
        BrokerInterface()   # cannot instantiate the ABC directly
