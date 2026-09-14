# B4a — order path against a simulated broker interface (frozen spec)

Written: September 13th/14th, 11:00 pm CT cycle. Bot milestone B4a per
`docs/BOT_ROADMAP.md`. Status: **SPEC FROZEN, coded to this spec same cycle.**

## What this is, and what it is not

The whole order path — `Signal` → order construction → submission →
acknowledgement → fill record → position reconciliation → crash recovery —
plus B6's kill switches (`src/capital_protection.py`) wired into every order,
written against a `BrokerInterface` contract that any real broker adapter
(B4b) can later implement without touching this code. This is infrastructure,
not a strategy and not a P&L claim: it is exercised with `src/base_entry_b3.py`
(the placeholder entry) and `src/risk_state_engine.py` (sizing/stops), and its
own output is never described as an edge, per the base-entry-b3 spec and the
bot roadmap's closing rule.

**The deliberate-failure broker exists on purpose.** A first order path
written only against a broker that always behaves is a path whose failure
modes were never exercised. `SimulatedBroker` can reject, partially fill,
disconnect mid-order, and return a late acknowledgement — on command
(deterministic, for tests) or at a seeded random rate (for a soak run) —
because those are exactly the cases the back-half spec's 14 execution checks
(AMENDMENT v3.1 §4) require the path to survive.

## Contract (`src/broker_interface.py`)

Dataclasses, instrument-agnostic, no strategy knowledge:

- `Order`: order_id, instrument, direction (long/short), quantity, order_type
  ("market" only, this milestone), intended_price (the reference price the
  signal was built against — never assumed equal to the fill), submitted_at,
  client_tag (links back to the originating `Signal`).
- `OrderAck`: order_id, broker_order_id (None if rejected), status
  ("acknowledged" | "rejected"), reason, ack_at, latency_s (ack_at −
  submitted_at, check 10).
- `Fill`: order_id, broker_order_id, fill_id, quantity, price, filled_at,
  is_partial, remaining_qty.
- `Position`: instrument, quantity (signed: + long, − short), avg_price.

`BrokerInterface` (ABC): `connect`, `disconnect`, `is_connected`,
`submit_order(order) -> OrderAck`, `get_fills(order_id) -> list[Fill]`,
`cancel_order(order_id) -> bool`, `get_positions() -> dict[instrument,
Position]`. B4b implements the same four-method surface against IBKR; nothing
above this layer changes.

## Simulated broker (`src/simulated_broker.py`)

`SimulatedBroker(BrokerInterface)`. Deterministic by construction: seeded
`random.Random(seed)`, never the global RNG. Fill price source is injected
(a callable or an explicit price), never invented — in production use it is
the next bar's open, exactly as `base_entry_b3.py`'s own entry convention
already uses (no lookahead introduced at this layer).

Failure modes, each independently triggerable two ways — an explicit
one-shot hook for tests (`force_reject()`, `force_partial(fraction)`,
`force_disconnect()`, `force_late_ack(extra_seconds)`) and a seeded-random
rate (`reject_rate`, `partial_fill_rate`, `disconnect_rate`,
`late_ack_rate`) for a longer soak run — so every one of the 14 checks has a
deterministic test and the soak mode is still reproducible from its seed.

- **Reject**: `submit_order` returns `OrderAck(status="rejected", ...)`
  immediately; no fill ever exists for that order_id.
- **Partial fill**: `get_fills` returns a first `Fill` for less than the
  full quantity, `is_partial=True`, `remaining_qty>0`; a second call after
  the broker "catches up" returns the remainder as a second fill (or the
  order stays partially filled if the simulated disconnect hits first —
  the order path must handle a position smaller than requested).
- **Disconnect mid-order**: `is_connected()` flips False after
  `submit_order` returns an ack but before `get_fills` is called; every
  interface method raises `BrokerDisconnected` while down; `connect()`
  restores it. This is the scenario check 13 exists for.
- **Late ack**: `OrderAck.ack_at` is stamped later than `submitted_at` by
  the configured delay (simulated clock offset, not a real sleep — this is
  a deterministic test double, not a timing benchmark); `latency_s` reports
  it honestly.

No hidden zero-slippage assumption anywhere: the simulated fill price is
always compared against `intended_price` and the deviation is recorded in
both points and (once a stop distance is known) R — never assumed zero,
matching the non-negotiable carried from the H118 execution-approximation
spec (`research/NEXT_UP.md` item 1a).

## Order path / execution engine (`src/order_path.py`)

`OrderPath(broker, journal_path, capital_state)`. One method matters:
`submit_signal(signal: Signal, today: dict) -> dict`.

1. **Capital-protection gate first, fail-closed** (check: nothing below
   this line runs if blocked). Calls
   `capital_protection.pre_order_check(state)` with `state` built by
   `OrderPathLedger` from the journal's own history (equity, peak profit,
   today's order/position counts, the last 20 fill deviations, the
   catastrophe-flag window) plus `today` (strategy, signal-derived
   per-trade swing, live vs. reference signal list for the divergence
   check). A blocked decision is journaled and returned; no order is built.
2. **Order construction** (checks 3–5): quantity from
   `risk_state_engine`'s `size_multiplier` × 1 contract, floor 1, capped at
   `CapitalConfig.max_contracts`; direction/entry/stop/target copied
   verbatim from the `Signal` — this layer never re-derives them.
3. **Journal the intent BEFORE submission** (`"order_intent"` record) — the
   write that makes check 13 provable: a crash between this line and the
   broker's ack is detectable on restart because the intent is on disk with
   no matching terminal record yet.
4. **Submit**, journal the ack or the rejection reason.
5. **Poll fills** (bounded retries — a live implementation would be
   event-driven; this milestone polls, which is honest about what is built
   today), journal every fill with intended price, actual price, deviation
   in points, latency, and — once the signal's stop distance is known —
   deviation in R.
6. **Reconcile position**: compare the ledger's rebuilt position (sum of
   journaled fills) against `broker.get_positions()`; any mismatch is
   journaled as a `"reconciliation_mismatch"` and raises, it is never
   silently accepted (check 12).
7. **Recovery** (`OrderPath.recover()`, check 13): replay the journal,
   find any `order_intent` with no terminal record (ack/reject, or a fill
   set that accounts for the full quantity, or a cancel), query the broker
   for that order_id's authoritative current status and fills, and either
   complete the journal record or escalate — an unresolved position is
   never left silently open. Called at the start of every `OrderPath`
   construction, not just after a real crash, so the guarantee is exercised
   on every run, not only when something goes wrong.

Everything above is one journal line per event (check 14): `order_intent`,
`order_ack`, `order_rejected`, `fill`, `reconciliation_mismatch`,
`recovery_action`, `blocked`. The journal is append-only JSONL, one file per
day, under `research/forward_validation/order_path_journal/`.

## What this milestone deliberately does not do

No real broker connection (B4b). No slippage/latency *statistics* across a
paper-run sample — that is B5's job, measuring what this layer only
*records* per-order. No wiring into the actual continuous paper loop (B7) —
this milestone proves the path works against deliberately hostile fills;
B7 runs it every session. Kill-switch *thresholds* are unchanged from
`capital_protection.py`'s frozen config; this milestone only proves they are
actually called before every order, which they were not before today.

## Test coverage (this cycle)

`tests/test_broker_interface.py` — dataclass field/shape sanity.
`tests/test_simulated_broker.py` — one deterministic test per failure mode
(reject, partial fill, disconnect mid-order + reconnect, late ack), plus a
seeded soak test that reproduces byte-identical outcomes for the same seed.
`tests/test_order_path.py` — happy path (ack → full fill → reconciled
position, journal has every expected record); capital-protection block
(pre_order_check denies, no order reaches the broker, journaled as
`"blocked"`); partial-fill handling; crash recovery (an `order_intent`
written with no terminal record, then a fresh `OrderPath` against the same
journal + broker recovers it without a silent open position); reconciliation
mismatch raises rather than swallowing the discrepancy.
