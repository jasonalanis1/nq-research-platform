"""
simulated_broker.py -- BOT MILESTONE B4a. Frozen spec:
research/infrastructure/b4a-order-path-spec.md

WHAT THIS IS
  A BrokerInterface implementation that is DELIBERATELY hostile: it rejects,
  partially fills, disconnects mid-order, and returns late acknowledgements --
  on command (deterministic hooks, for tests) or at a seeded random rate (for
  a longer soak run). A first order path written only against a broker that
  always behaves is a path whose failure modes were never exercised; this is
  the fixture the back-half spec's 14 execution checks (AMENDMENT v3.1 S4)
  need to be provably survived, not just assumed away.

  Deterministic by construction: every random choice goes through
  random.Random(seed), never the global `random` module, so a soak run is
  reproducible from its seed alone (tests/test_simulated_broker.py pins this).

  The fill price is always supplied by the caller (an explicit price, or a
  callable) -- this module never invents a market price. In production use
  that price is the next bar's open, the same no-lookahead convention
  src/base_entry_b3.py already uses; this layer adds no new lookahead.
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Callable, Optional, Union

from broker_interface import (
    BrokerDisconnected, BrokerInterface, Fill, Order, OrderAck, Position,
)

PriceSource = Union[float, Callable[[Order], float]]


class _PendingOrder:
    __slots__ = ("order", "broker_order_id", "filled_qty", "fills", "rejected",
                 "reject_reason", "cancelled")

    def __init__(self, order: Order, broker_order_id: Optional[str]):
        self.order = order
        self.broker_order_id = broker_order_id
        self.filled_qty = 0
        self.fills: list[Fill] = []
        self.rejected = False
        self.reject_reason: Optional[str] = None
        self.cancelled = False


class SimulatedBroker(BrokerInterface):
    def __init__(self, seed: int = 0, reject_rate: float = 0.0, partial_fill_rate: float = 0.0,
                 disconnect_rate: float = 0.0, late_ack_rate: float = 0.0,
                 late_ack_seconds: float = 2.0, default_partial_fraction: float = 0.5):
        self._rng = random.Random(seed)
        self.reject_rate = reject_rate
        self.partial_fill_rate = partial_fill_rate
        self.disconnect_rate = disconnect_rate
        self.late_ack_rate = late_ack_rate
        self.late_ack_seconds = late_ack_seconds
        self.default_partial_fraction = default_partial_fraction

        self._connected = False
        self._orders: dict[str, _PendingOrder] = {}
        self._positions: dict[str, Position] = {}

        # one-shot deterministic overrides, consumed by the NEXT relevant call only
        self._force_reject_next = False
        self._force_partial_next: Optional[float] = None
        self._force_disconnect_after_ack = False
        self._force_late_ack_next: Optional[float] = None

    # -- deterministic one-shot hooks, for tests --------------------------------
    def force_reject(self) -> None:
        self._force_reject_next = True

    def force_partial(self, fraction: float = 0.5) -> None:
        self._force_partial_next = fraction

    def force_disconnect(self) -> None:
        """Disconnect immediately -- every subsequent call raises until connect()."""
        self._connected = False

    def force_disconnect_after_next_ack(self) -> None:
        """The NEXT submit_order() acknowledges normally, then the broker goes
        down before get_fills() can be called -- the scenario check 13 exists for."""
        self._force_disconnect_after_ack = True

    def force_late_ack(self, extra_seconds: float) -> None:
        self._force_late_ack_next = extra_seconds

    # -- BrokerInterface ----------------------------------------------------
    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def _require_connected(self) -> None:
        if not self._connected:
            raise BrokerDisconnected("simulated broker is disconnected")

    def submit_order(self, order: Order) -> OrderAck:
        self._require_connected()
        if order.order_id in self._orders:
            raise ValueError(f"duplicate order_id submitted: {order.order_id}")

        do_reject = self._force_reject_next or (self.reject_rate and self._rng.random() < self.reject_rate)
        self._force_reject_next = False

        delay = 0.0
        if self._force_late_ack_next is not None:
            delay = self._force_late_ack_next
            self._force_late_ack_next = None
        elif self.late_ack_rate and self._rng.random() < self.late_ack_rate:
            delay = self.late_ack_seconds
        ack_at = order.submitted_at + timedelta(seconds=delay)

        if do_reject:
            pending = _PendingOrder(order, broker_order_id=None)
            pending.rejected = True
            pending.reject_reason = "simulated rejection"
            self._orders[order.order_id] = pending
            return OrderAck(order_id=order.order_id, broker_order_id=None, status="rejected",
                             reason="simulated rejection", ack_at=ack_at, latency_s=delay)

        broker_order_id = f"SIM-{uuid.uuid4().hex[:12]}"
        self._orders[order.order_id] = _PendingOrder(order, broker_order_id=broker_order_id)

        if self._force_disconnect_after_ack:
            self._force_disconnect_after_ack = False
            self._connected = False   # ack succeeds; connection drops before any fill can be read

        return OrderAck(order_id=order.order_id, broker_order_id=broker_order_id, status="acknowledged",
                         reason=None, ack_at=ack_at, latency_s=delay)

    def _resolve_price(self, price_source: PriceSource, order: Order) -> float:
        return price_source(order) if callable(price_source) else float(price_source)

    def fill(self, order_id: str, price_source: PriceSource, filled_at: Optional[datetime] = None) -> list[Fill]:
        """Advance an acknowledged order toward being filled. Called explicitly by
        the order path (or a test) rather than happening automatically inside
        submit_order, because a real broker's fill is a separate, later event too."""
        self._require_connected()
        pending = self._orders.get(order_id)
        if pending is None or pending.rejected or pending.cancelled:
            return []
        order = pending.order
        remaining = order.quantity - pending.filled_qty
        if remaining <= 0:
            return []
        filled_at = filled_at or order.submitted_at
        price = self._resolve_price(price_source, order)

        do_partial = (self._force_partial_next is not None or
                      (self.partial_fill_rate and self._rng.random() < self.partial_fill_rate))
        fraction = self._force_partial_next if self._force_partial_next is not None else self.default_partial_fraction
        self._force_partial_next = None

        qty = max(1, min(remaining, int(round(remaining * fraction)))) if do_partial else remaining
        pending.filled_qty += qty
        remaining_after = order.quantity - pending.filled_qty
        f = Fill(order_id=order_id, broker_order_id=pending.broker_order_id,
                  fill_id=f"FILL-{uuid.uuid4().hex[:12]}", quantity=qty, price=price,
                  filled_at=filled_at, is_partial=remaining_after > 0, remaining_qty=remaining_after)
        pending.fills.append(f)
        self._apply_to_position(order, qty, price)
        return [f]

    def _apply_to_position(self, order: Order, qty: int, price: float) -> None:
        signed = qty if order.direction == "long" else -qty
        pos = self._positions.get(order.instrument)
        if pos is None or pos.quantity == 0:
            self._positions[order.instrument] = Position(instrument=order.instrument, quantity=signed, avg_price=price)
            return
        new_qty = pos.quantity + signed
        if new_qty == 0:
            self._positions[order.instrument] = Position(instrument=order.instrument, quantity=0, avg_price=0.0)
        elif (pos.quantity > 0) == (signed > 0):
            # adding to the same side -- weighted average
            total_cost = pos.avg_price * abs(pos.quantity) + price * abs(signed)
            self._positions[order.instrument] = Position(instrument=order.instrument, quantity=new_qty,
                                                           avg_price=total_cost / abs(new_qty))
        elif (new_qty > 0) == (pos.quantity > 0):
            # partial reduction on the same side -- basis unchanged
            self._positions[order.instrument] = Position(instrument=order.instrument, quantity=new_qty, avg_price=pos.avg_price)
        else:
            # flipped through zero -- new basis is this fill's price
            self._positions[order.instrument] = Position(instrument=order.instrument, quantity=new_qty, avg_price=price)

    def get_fills(self, order_id: str) -> list[Fill]:
        self._require_connected()
        pending = self._orders.get(order_id)
        if pending is None:
            return []
        return list(pending.fills)

    def cancel_order(self, order_id: str) -> bool:
        self._require_connected()
        pending = self._orders.get(order_id)
        if pending is None or pending.rejected or pending.cancelled:
            return False
        remaining = pending.order.quantity - pending.filled_qty
        if remaining <= 0:
            return False   # already fully filled -- nothing to cancel
        pending.cancelled = True
        return True

    def get_positions(self) -> dict:
        self._require_connected()
        return dict(self._positions)

    # -- test/introspection helper, not part of the interface --------------
    def order_status(self, order_id: str) -> dict:
        pending = self._orders.get(order_id)
        if pending is None:
            return {"exists": False}
        return {"exists": True, "rejected": pending.rejected, "cancelled": pending.cancelled,
                "filled_qty": pending.filled_qty, "requested_qty": pending.order.quantity,
                "n_fills": len(pending.fills)}
