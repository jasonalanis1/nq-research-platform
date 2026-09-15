"""
order_path.py -- BOT MILESTONE B4a: the order path against a simulated broker.
Frozen spec: research/infrastructure/b4a-order-path-spec.md

WHAT THIS IS
  Signal -> order construction -> submission -> acknowledgement -> fill record
  -> position reconciliation -> crash recovery, with B6's kill switches
  (src/capital_protection.py) called before every single order. Written
  against src/broker_interface.py's BrokerInterface so a real broker (B4b)
  swaps in later without this file changing.

  This is infrastructure, not an edge and not a P&L claim -- see the base-
  entry-b3 spec and docs/BOT_ROADMAP.md's closing rule. It is exercised with
  base_entry_b3.py's placeholder Signal and risk_state_engine.py's sizing,
  but never described as evidence of anything about the market.

JOURNAL
  Append-only JSONL, one file per UTC date, under
  research/forward_validation/order_path_journal/<YYYY-MM-DD>.jsonl.
  One line per event: order_intent, order_ack, order_rejected, fill,
  reconciliation_mismatch, recovery_action, blocked. This is check 14 (AMENDMENT
  v3.1 S4) and also the input `recover()` reads to prove check 13: a crash
  cannot silently leave an unintended position open.

USAGE (illustrative -- see tests/test_order_path.py for real examples)
  broker = SimulatedBroker(seed=1); broker.connect()
  path = OrderPath(broker, journal_dir="research/forward_validation/order_path_journal")
  path.recover()   # always run first -- cheap when there is nothing to recover
  result = path.submit_signal(signal, today={...}, size_multiplier=1.0,
                               price_source=lambda o: signal.entry)
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import capital_protection  # noqa: E402
from broker_interface import BrokerDisconnected, BrokerInterface, Order  # noqa: E402


class ReconciliationError(RuntimeError):
    """The ledger's rebuilt position does not match the broker's reported
    position. Never silently accepted -- check 12."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OrderPathJournal:
    """Append-only JSONL, one file per UTC date. Reading is always a full
    replay of every day's file that exists -- this milestone's volume (a few
    orders a day, one strategy) makes that the honest, simple choice; nothing
    here claims to scale beyond it."""

    def __init__(self, journal_dir: str | Path):
        self.dir = Path(journal_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, dt: datetime) -> Path:
        return self.dir / f"{dt.date().isoformat()}.jsonl"

    def append(self, event: str, **fields) -> dict:
        record = {"ts": _now().isoformat(), "event": event, **fields}
        with self._path_for(_now()).open("a") as f:
            f.write(json.dumps(record, default=str) + "\n")
        return record

    def all_records(self) -> list[dict]:
        out = []
        for p in sorted(self.dir.glob("*.jsonl")):
            for line in p.read_text().splitlines():
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def records_for_order(self, order_id: str) -> list[dict]:
        return [r for r in self.all_records() if r.get("order_id") == order_id]


class OrderPathLedger:
    """Rebuilds the capital-protection gate's `state` dict from the journal's
    own history, so the gate reflects what actually happened, not what the
    caller claims happened. Fields the ledger cannot know (strategy identity,
    paper-track record, live-vs-reference signal comparison) are supplied by
    the caller via `today` and merged in -- see OrderPath.submit_signal."""

    def __init__(self, journal: OrderPathJournal):
        self.journal = journal

    def fill_deviation_pts(self, record: dict) -> Optional[float]:
        dev = record.get("deviation_pts")
        return None if dev is None else float(dev)

    def recent_fill_deviations(self, window: int = 20) -> list[float]:
        records = [r for r in self.journal.all_records() if r.get("event") == "fill"]
        devs = [self.fill_deviation_pts(r) for r in records]
        devs = [d for d in devs if d is not None]
        return devs[-window:]

    def orders_today(self, session_date: Optional[str] = None) -> int:
        """Orders already sent for THIS SESSION.

        FIXED 2026-09-14 (found by Step A in dummy mode): this used to count
        order_intents by the WALL-CLOCK day they were journaled. When the paper
        loop catches up several sessions in one run -- which it does every time
        data lands -- every session's orders share one wall-clock day, so the
        daily cap tripped for every session after the first four orders. In B3
        mode (one order a session) three sessions fit under the cap and it went
        unnoticed; four-a-session made it obvious. The session date now comes
        from `today["session_date"]` when the caller supplies it (the paper loop
        does), and each intent's own client_tag carries its signal timestamp, so
        the count is per SESSION regardless of when the run happened. The
        wall-clock fallback is kept for callers that do not supply a date."""
        if session_date:
            return sum(1 for r in self.journal.all_records()
                       if r.get("event") == "order_intent"
                       and str(r.get("client_tag", "")).split(":", 1)[-1].strip().startswith(session_date))
        today = _now().date().isoformat()
        return sum(1 for r in self.journal.all_records()
                   if r.get("event") == "order_intent" and str(r.get("ts", "")).startswith(today))

    def catastrophe_flags(self) -> list[bool]:
        return [bool(r.get("catastrophe")) for r in self.journal.all_records() if r.get("event") == "fill"]

    def build_state(self, today: dict, open_positions: int, contracts: int) -> dict:
        state = dict(today)
        state.setdefault("fill_deviations_pts", self.recent_fill_deviations())
        state.setdefault("orders_today", self.orders_today(today.get("session_date")))
        state.setdefault("catastrophe_flags", self.catastrophe_flags())
        state["open_positions"] = open_positions
        state["contracts"] = contracts
        return state


class OrderPath:
    def __init__(self, broker: BrokerInterface, journal_dir: str | Path,
                 instrument: str = "MNQ", cfg=None):
        self.broker = broker
        self.journal = OrderPathJournal(journal_dir)
        self.ledger = OrderPathLedger(self.journal)
        self.instrument = instrument
        # capital config: CONFIG (live dollars) by default; the paper loop passes
        # capital_protection.PAPER_CONFIG (R-denominated, 2026-09-14 staff meeting)
        self.cfg = cfg if cfg is not None else capital_protection.CONFIG

    # ------------------------------------------------------------------
    # check 13 -- a crash cannot silently leave an unintended position open
    # ------------------------------------------------------------------
    def recover(self) -> list[dict]:
        """Replay the journal; for every order_intent with no terminal record
        (ack/reject, or fills covering the full requested quantity, or a
        cancel), query the broker for its authoritative status and either
        complete the record or escalate. Safe to call on every startup, not
        just after a real crash -- that is how the guarantee gets exercised
        on every run instead of only when something already went wrong."""
        actions = []
        records = self.journal.all_records()
        intents = {r["order_id"]: r for r in records if r.get("event") == "order_intent"}
        # An ack record alone is not terminal unless the order is also fully
        # filled or cancelled -- but for THIS milestone (immediate
        # poll-to-completion within one submit_signal call), an ack always
        # precedes its fill records in the same call, so an order missing its
        # post-ack fills IS exactly the crash case recover() exists to catch.
        filled_qty: dict[str, int] = {}
        rejected_ids = {r["order_id"] for r in records if r.get("event") == "order_rejected"}
        for r in records:
            if r.get("event") == "fill":
                filled_qty[r["order_id"]] = filled_qty.get(r["order_id"], 0) + int(r.get("quantity", 0))
        cancelled_ids = {r["order_id"] for r in records if r.get("event") == "recovery_action"
                          and r.get("action") == "cancelled"}

        for order_id, intent in intents.items():
            if order_id in rejected_ids or order_id in cancelled_ids:
                continue
            requested = int(intent.get("quantity", 0))
            if filled_qty.get(order_id, 0) >= requested and requested > 0:
                continue
            # unresolved -- ask the broker
            try:
                if not self.broker.is_connected():
                    self.broker.connect()
                status = getattr(self.broker, "order_status", None)
                broker_fills = self.broker.get_fills(order_id)
                already_journaled = {r.get("fill_id") for r in records if r.get("event") == "fill"}
                for f in broker_fills:
                    if f.fill_id not in already_journaled:
                        self._journal_fill(f, intent)
                info = status(order_id) if status else {}
                action = self.journal.append("recovery_action", order_id=order_id,
                                              action="reconciled_from_broker",
                                              broker_info=info, recovered_fills=len(broker_fills))
                actions.append(action)
            except BrokerDisconnected:
                action = self.journal.append("recovery_action", order_id=order_id,
                                              action="ESCALATE_broker_unreachable",
                                              note="order_intent has no terminal record and the broker "
                                                   "cannot be reached -- this must be escalated to a human, "
                                                   "never assumed resolved")
                actions.append(action)
        return actions

    def _journal_fill(self, f, intent: dict) -> dict:
        intended_price = float(intent["intended_price"])
        deviation_pts = round(f.price - intended_price, 6) if intent.get("direction") == "long" \
            else round(intended_price - f.price, 6)
        stop_distance = intent.get("stop_distance")
        deviation_r = round(deviation_pts / stop_distance, 6) if stop_distance else None
        return self.journal.append(
            "fill", order_id=f.order_id, broker_order_id=f.broker_order_id, fill_id=f.fill_id,
            quantity=f.quantity, price=f.price, is_partial=f.is_partial, remaining_qty=f.remaining_qty,
            intended_price=intended_price, deviation_pts=deviation_pts, deviation_r=deviation_r,
        )

    # ------------------------------------------------------------------
    # the main path
    # ------------------------------------------------------------------
    def submit_signal(self, signal, today: dict, size_multiplier: float = 1.0,
                       price_source=None, max_fill_polls: int = 5) -> dict:
        """signal: a strategy_contract.Signal. `today` supplies the fields the
        ledger cannot derive on its own (see OrderPathLedger.build_state).
        price_source: passed straight to broker.fill(); if None, the signal's
        own `entry` price is used (matching base_entry_b3's no-lookahead
        next-bar-open convention -- this layer does not relax it)."""
        price_source = price_source if price_source is not None else signal.entry
        instrument = getattr(signal, "instrument", self.instrument)

        positions = self._safe_positions()
        open_positions = sum(1 for p in positions.values() if p.quantity != 0)
        contracts = max(1, int(size_multiplier)) if size_multiplier and size_multiplier > 0 else 1
        contracts = min(contracts, self.cfg.max_contracts)

        state = self.ledger.build_state(today, open_positions=open_positions, contracts=contracts)
        decision = capital_protection.pre_order_check(state, self.cfg)
        if not decision.allow:
            record = self.journal.append("blocked", strategy=today.get("strategy"),
                                          reasons=decision.reasons, divergences=decision.divergences,
                                          signal=str(getattr(signal, "timestamp", "")))
            return {"status": "blocked", "reasons": decision.reasons, "divergences": decision.divergences,
                    "journal": [record]}

        order_id = f"B4A-{uuid.uuid4().hex[:12]}"
        stop_distance = abs(float(signal.entry) - float(signal.stop))
        intent = self.journal.append(
            "order_intent", order_id=order_id, instrument=instrument, direction=signal.direction,
            quantity=contracts, intended_price=float(signal.entry), stop_distance=stop_distance,
            strategy=today.get("strategy"), client_tag=f"{getattr(signal, 'strategy_name', '?')}:{getattr(signal, 'timestamp', '?')}",
        )

        order = Order(order_id=order_id, instrument=instrument, direction=signal.direction,
                       quantity=contracts, order_type="market", intended_price=float(signal.entry),
                       submitted_at=_now(), client_tag=intent["client_tag"])
        try:
            ack = self.broker.submit_order(order)
        except BrokerDisconnected as e:
            record = self.journal.append("recovery_action", order_id=order_id,
                                          action="ESCALATE_disconnected_at_submit", note=str(e))
            return {"status": "escalate", "journal": [intent, record]}

        journal_records = [intent]
        if ack.status == "rejected":
            record = self.journal.append("order_rejected", order_id=order_id, reason=ack.reason,
                                          latency_s=ack.latency_s)
            journal_records.append(record)
            return {"status": "rejected", "reason": ack.reason, "journal": journal_records}

        record = self.journal.append("order_ack", order_id=order_id, broker_order_id=ack.broker_order_id,
                                      latency_s=ack.latency_s)
        journal_records.append(record)

        fills = []
        try:
            for _ in range(max_fill_polls):
                new_fills = self.broker.fill(order_id, price_source)
                for f in new_fills:
                    journal_records.append(self._journal_fill(f, intent))
                    fills.append(f)
                if new_fills and new_fills[-1].remaining_qty == 0:
                    break
                if not new_fills:
                    break
        except BrokerDisconnected as e:
            record = self.journal.append("recovery_action", order_id=order_id,
                                          action="ESCALATE_disconnected_during_fill", note=str(e))
            journal_records.append(record)
            return {"status": "escalate", "journal": journal_records, "fills": fills}

        total_filled = sum(f.quantity for f in fills)
        recon = self._reconcile(instrument, signal.direction, total_filled, fills)
        if recon is not None:
            journal_records.append(recon)

        status = "filled" if total_filled >= contracts else ("partial" if total_filled > 0 else "unfilled")
        return {"status": status, "order_id": order_id, "filled_qty": total_filled,
                "requested_qty": contracts, "fills": [f.as_dict() for f in fills], "journal": journal_records}

    def _safe_positions(self) -> dict:
        try:
            if not self.broker.is_connected():
                self.broker.connect()
            return self.broker.get_positions()
        except BrokerDisconnected:
            return {}

    def _reconcile(self, instrument: str, direction: str, total_filled: int, fills) -> Optional[dict]:
        """A single order's own contribution to a shared instrument position
        is not separable from any other open position in general, so this
        milestone reconciles at the level that is still meaningful with a
        single strategy and a 1-contract scale: after fills exist, the
        broker MUST report a non-zero position in that instrument. A genuine
        mismatch (broker unreachable, or fills recorded with no corresponding
        broker position at all) is journaled and raised -- never swallowed,
        per check 12."""
        if total_filled == 0:
            return None
        try:
            positions = self.broker.get_positions()
        except BrokerDisconnected:
            self.journal.append("reconciliation_mismatch", instrument=instrument,
                                 reason="broker unreachable during reconciliation")
            raise ReconciliationError("broker unreachable during reconciliation") from None
        pos = positions.get(instrument)
        if pos is None or pos.quantity == 0:
            self.journal.append("reconciliation_mismatch", instrument=instrument,
                                 reason=f"{total_filled} contracts filled but broker reports no position",
                                 broker_position=None if pos is None else pos.as_dict())
            raise ReconciliationError(f"{total_filled} contracts filled but broker reports no position in {instrument}")
        return None
