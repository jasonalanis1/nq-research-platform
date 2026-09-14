"""
broker_interface.py -- BOT MILESTONE B4a (order path against a simulated broker).

Frozen spec: research/infrastructure/b4a-order-path-spec.md

WHAT THIS IS
  The instrument-agnostic, strategy-agnostic contract every broker adapter speaks:
  four methods (connect/submit_order/get_fills/get_positions + cancel_order,
  is_connected, disconnect) and four dataclasses (Order, OrderAck, Fill,
  Position). src/simulated_broker.py implements it today with deliberately
  hostile behaviour; B4b (a real broker, e.g. IBKR) implements the exact same
  surface later. Nothing in src/order_path.py or above ever needs to change
  when B4b lands -- that is the point of the contract.

  This module knows NOTHING about strategies, signals, sizing, or P&L. It is
  pure order-mechanics plumbing.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


class BrokerDisconnected(RuntimeError):
    """Raised by every BrokerInterface method while the (simulated or real)
    connection is down. The order path must catch this, never let it
    silently swallow a possibly-in-flight order -- see OrderPath.recover()."""


@dataclass
class Order:
    order_id: str
    instrument: str
    direction: str            # "long" or "short"
    quantity: int
    order_type: str           # "market" -- the only type this milestone supports
    intended_price: float     # the reference price the signal was built against;
                               # NEVER assumed equal to the eventual fill
    submitted_at: datetime
    client_tag: str           # links back to the originating Signal (e.g. strategy_name+timestamp)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["submitted_at"] = str(self.submitted_at)
        return d


@dataclass
class OrderAck:
    order_id: str
    broker_order_id: Optional[str]
    status: str                # "acknowledged" or "rejected"
    reason: Optional[str]
    ack_at: datetime
    latency_s: float           # ack_at - submitted_at, in seconds (check 10, never assumed zero)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["ack_at"] = str(self.ack_at)
        return d


@dataclass
class Fill:
    order_id: str
    broker_order_id: Optional[str]
    fill_id: str
    quantity: int
    price: float
    filled_at: datetime
    is_partial: bool
    remaining_qty: int         # 0 once the order is fully filled

    def as_dict(self) -> dict:
        d = asdict(self)
        d["filled_at"] = str(self.filled_at)
        return d


@dataclass
class Position:
    instrument: str
    quantity: int              # signed: positive = long, negative = short
    avg_price: float

    def as_dict(self) -> dict:
        return asdict(self)


class BrokerInterface(ABC):
    """Every broker adapter (simulated or real) implements exactly this surface."""

    @abstractmethod
    def connect(self) -> bool:
        ...

    @abstractmethod
    def disconnect(self) -> None:
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        ...

    @abstractmethod
    def submit_order(self, order: Order) -> OrderAck:
        ...

    @abstractmethod
    def get_fills(self, order_id: str) -> list[Fill]:
        ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        ...

    @abstractmethod
    def get_positions(self) -> dict:
        """instrument -> Position"""
        ...
