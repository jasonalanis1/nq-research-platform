"""
bot_stack_paper_run.py -- BOT MILESTONE B7: the continuous paper run.

WHAT THIS IS
  The three existing bot pieces, wired into one loop that runs every session:
  base_entry_b3.py's signal -> risk_state_engine.py's decision -> (if the
  signal fires AND both gates allow it) order_path.py's real order machinery
  against simulated_broker.py. Every session gets exactly one row in the
  paper log, whatever happened (signal or none, gate decision, order-path
  result) -- unlike bot_forward_log.py's statistical log, which only logs a
  row when a signal fired, this file logs "nothing happened" too, because it
  is a record of what the operational loop DID each session, not just of
  signal outcomes.

TWO CLOCKS RULE, restated from the EXECUTION side (bot_forward_log.py
restates it from the statistical side -- see that file's header): this file
is what actually submits orders through order_path.py/simulated_broker.py.
Its numbers are execution numbers -- fills, deviation, reconciliation,
capital-protection gate decisions -- never a statistical forward-test claim,
and never compared against bot_forward_log.py's row-for-row statistical
numbers even though both read the same signal and decision for a given day.
The file split (bot_stack_forward_log.jsonl vs. bot_stack_paper_log.jsonl)
is that rule made concrete, not just a naming convention.

SCOPE / CHOICES MADE EXPLICIT (this cycle's instruction: note them, don't
silently decide them)
  1. EXECUTION ANCHOR. bot_forward_log.py's BOT_FORWARD_ANCHOR (2026-09-14)
     is a STATISTICAL forward boundary -- it exists so a statistical claim is
     never made on sessions that were available during Discovery/search. B7
     is not making a statistical claim; it is proving the order-path
     machinery runs, unattended, every session, without skipping one. Using
     the statistical anchor here would mean B7 does nothing until 2026-09-14
     data exists on disk, even though the data on disk right now (through
     2026-09-08) is exactly as good a test of "does the loop run correctly
     end-to-end" as any later date. So B7 gets its OWN anchor,
     B7_EXECUTION_ANCHOR, set to the latest session already on disk the
     first time this file runs (2026-09-08) -- not the start of history
     (2015). Replaying years of history is not this cycle's job and is not
     what B7 exists to prove; it exists to prove every session GOING FORWARD
     from here gets processed exactly once, which only requires that this
     run and every later one never skip a session, not that today's run
     replay years of data it was never asked to touch. This constant is
     written to disk the first time it's needed (see B7_ANCHOR_PATH) so a
     later cycle doesn't silently redefine it.
  2. BROKER LIFETIME. A fresh SimulatedBroker() per session. At this
     milestone's scale (one strategy, at most one order a session, the
     capital-protection cap of 1 open position) no cross-session broker
     state -- a carried position, an in-flight order spanning sessions -- is
     assumed yet. A persistent broker across sessions (to model overnight
     carry, or multiple concurrent strategies) is a real design question for
     a later B7 iteration, parked here rather than decided silently.
  3. WHICH STOP/TARGET GETS ORDERED. The order is built from B3's own raw
     signal (entry/stop/target, unconditioned) -- exactly what B4a's tests
     already exercise. risk_state_engine's decision contributes
     size_multiplier (how many contracts) and trade_permission (whether to
     trade at all), not a substitute stop/target: B2's ATR-scaled
     stop_distance_atr/target_distance_atr are the STATISTICAL comparison
     bot_forward_log.py's "base_plus_b2" row already answers ("does sizing
     help"); wiring them into the actual order as well would blur that
     comparison with a live decision this milestone was never asked to make.
  4. BOOKKEEPING EXIT (equity/peak/daily-P&L inputs to capital_protection's
     gate, NOT the statistical log). Once an order fills, this file walks
     the SAME session's own already-elapsed bars forward from the fill,
     first-touch-wins, same-bar stop/target ambiguity resolved to the stop --
     mechanically identical to bot_forward_log.py's _simulate_outcome, but
     re-implemented locally rather than imported, on purpose: importing it
     would make the execution log borrow logic from the statistical file,
     which is exactly the coupling the two-clocks rule exists to prevent,
     even when the underlying arithmetic happens to be the same. Legitimate
     here (the session has already closed by the time this script runs);
     not a live intraday feed, and used ONLY to give capital_protection's
     gate real dollar inputs instead of placeholders -- never logged or
     described as a forward-test result.
  5. FILL PRICE. price_source=signal.entry (a plain float, not a callable)
     -- the same next-bar-open price used for the order's intended_price.
     There is no live intraday feed at this milestone, so the fill happens
     at the intended price and deviation_pts is 0 by construction. This is
     disclosed, not hidden: real deviation needs either tick-level fill data
     lined up with the entry bar or a real broker (B4b), neither of which
     exists yet.
  6. DOLLAR P&L IS GROSS. MNQ_MULTIPLIER=$2/index point (backtest.py's own
     comment: "CONTRACT_MULTIPLIER: $20/point is standard full-size NQ.
     Micro NQ (MNQ) is $2/point instead"). No commission or slippage-beyond-
     fill is deducted -- backtest.py's own cost model is explicitly a
     placeholder for full-size NQ, and fabricating a MNQ commission number
     here rather than stating "no cost model yet" would be exactly the kind
     of invented data the standing rules forbid. A costed number is future
     work once real execution costs are known (B4b or a funded paper
     account).

LOG: research/forward_validation/bot_stack_paper_log.jsonl (append-only, one
row per session, idempotent -- a session already logged is never re-run).

USAGE
    python3 src/bot_stack_paper_run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from production_paths import assert_writable, enable_production
from base_entry_b3 import STRATEGY_NAME as B3_NAME, generate_signals as b3_signals  # noqa: E402
import execution_dummy  # noqa: E402

# STRATEGY SWITCH (2026-09-14 ~8:45 pm CT, Jason: "push this as fast as possible").
#   "b3"    -- the frozen one-trade-a-day placeholder (default; unchanged)
#   "dummy" -- execution_dummy: four orders a session at fixed clock times, so the
#              pre-registered 20-fill execution sample arrives in ~5 sessions.
# Both are placeholders with no claimed edge. Rows carry `strategy` so the two
# are never conflated in the execution record. Set by main(--strategy) or by the
# replay harness; tests may set it directly.
STRATEGY = "b3"
STRATEGIES = {
    "b3": (B3_NAME, b3_signals),
    "dummy": (execution_dummy.STRATEGY_NAME, execution_dummy.generate_signals),
}
# PAPER BOOK (standing directive 2026-09-15, s.2 PAPER / s.14): every frozen
# strategy that passed its SCREEN is registered here under its strategy_id and
# scored by `--strategy <key>`. "b3" and "dummy" are PLUMBING placeholders
# (Jason, September 15th: the dummy stays labelled a plumbing test, its record
# kept separate, never judged); everything else is a CANDIDATE whose record
# src/paper_book.py measures and the Director judges at 40 trades / 6 weeks.
PLUMBING_KEYS = ("b3", "dummy")


STRATEGY_MODULES: dict = {}


def register_strategy(key: str, module) -> None:
    """Add a frozen strategy module (STRATEGY_NAME + generate_signals) to the book."""
    STRATEGIES[key] = (module.STRATEGY_NAME, module.generate_signals)
    STRATEGY_MODULES[key] = module


# S001a (Level Sweep Reversal, compressed prior day, PRIOR-DAY levels only) --
# registered at its FREEZE (2026-09-15, 7:00 pm CT cycle) so that a passing SCREEN
# can put it into PAPER the same cycle with `--strategy s001a` (directive s.14.4).
import strategy_s001a_level_sweep_reversal_prior_day as _s001a  # noqa: E402
register_strategy("s001a", _s001a)


def _strategy():
    return STRATEGIES[STRATEGY]


def _journal_dir() -> Path:
    """Plumbing keys share the legacy journal (their record is history). Each
    CANDIDATE gets its own journal subtree so the daily order cap, the fill-
    deviation window and the capital-protection state are per strategy -- two
    strategies on the same session must not consume each other's budget."""
    return JOURNAL_DIR if STRATEGY in PLUMBING_KEYS else JOURNAL_DIR / STRATEGY


def _signals(gen, day_df: pd.DataFrame, history):
    """A strategy that needs prior sessions (a trailing state variable) takes
    `history=` -- the full frame the loop already holds -- so it never has to
    reload the price file itself. Older modules take the day frame only."""
    import inspect
    try:
        takes_history = "history" in inspect.signature(gen).parameters
    except (TypeError, ValueError):
        takes_history = False
    return gen(day_df, history=history) if (takes_history and history is not None) else gen(day_df)


STRATEGY_NAME = B3_NAME   # kept for older imports; run_session uses _strategy()
# --- candidates in the PAPER BOOK (registered after a positive SCREEN; see
# research/ledger/strategies.jsonl for the record of when and why) ---
from risk_state_engine import decision_for  # noqa: E402
from order_path import OrderPath  # noqa: E402
from simulated_broker import SimulatedBroker  # noqa: E402
import capital_protection  # noqa: E402

PROJECT_ROOT = ROOT.parent
LOG_DIR = PROJECT_ROOT / "research" / "forward_validation"
LOG_PATH = LOG_DIR / "bot_stack_paper_log.jsonl"
JOURNAL_DIR = LOG_DIR / "order_path_journal"
B7_ANCHOR_PATH = PROJECT_ROOT / "research" / "infrastructure" / "b7-execution-anchor.json"

MNQ_MULTIPLIER = 2.0    # dollars per index point, MNQ -- see backtest.py's CONTRACT_MULTIPLIER comment

# Deliberately hostile (matches simulated_broker.py's own reason for existing --
# see its file header): low, non-zero rates so the order path's failure modes
# stay exercised on every real run, not just in tests/test_order_path.py's
# one-shot hooks. Module-level so tests can override them to 0 for a
# deterministic fill outcome without touching SimulatedBroker itself.
# Capital model for the paper loop: R-denominated (research/infrastructure/
# staff-meeting-swing-band-2026-09-14.md). Jason's dollar band and budget are
# live rules and belong to B8. Pre-registered 2026-09-14 ~8:30 pm CT, applied
# to sessions scored from then on; the four sessions already logged as blocked
# under the dollar band stay in the log as history and are NOT re-scored.
CAPITAL_CFG = capital_protection.PAPER_CONFIG
PAPER_MODE_SINCE = "2026-09-14"

BROKER_REJECT_RATE = 0.03
BROKER_PARTIAL_FILL_RATE = 0.05
BROKER_DISCONNECT_RATE = 0.01
BROKER_LATE_ACK_RATE = 0.03


def _seed_for(date) -> int:
    """Deterministic per-session seed. NOT Python's built-in hash() -- str
    hashing is randomized per-process (PYTHONHASHSEED) unless disabled, which
    would make a soak run irreproducible across cycles, exactly what
    simulated_broker.py's own docstring says never to do."""
    return int(pd.Timestamp(date).strftime("%Y%m%d"))


def _b7_execution_anchor(all_dates: list) -> object:
    """The first time this runs, the anchor is the latest session already on
    disk (choice 1 above), written to disk so a later cycle -- which will see
    MORE sessions on disk -- doesn't silently move the goalposts backward or
    forward. Every session strictly after the anchor is processed by every
    run from then on; the anchor session itself is the first one processed,
    the run that establishes it."""
    if B7_ANCHOR_PATH.exists():
        return pd.Timestamp(json.loads(B7_ANCHOR_PATH.read_text())["anchor"]).date()
    anchor = max(all_dates)
    B7_ANCHOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    assert_writable(B7_ANCHOR_PATH, "B7 execution anchor")
    B7_ANCHOR_PATH.write_text(json.dumps({
        "anchor": str(anchor),
        "set_by": "bot_stack_paper_run.py, first run",
        "note": "B7's OWN execution anchor -- see bot_stack_paper_run.py choice 1. "
                "NOT the same as bot_forward_log.py's BOT_FORWARD_ANCHOR (statistical).",
    }, indent=2))
    return anchor


SESSION_COMPLETE_BY = "15:55"   # the bookkeeping time-exit in _resolve_fill_outcome


def session_is_complete(day_df: pd.DataFrame) -> tuple[bool, str]:
    """Is this session safe to score, or is it a fragment?

    ADDED 2026-09-14 after the FIRST Step A replay on fresh data (the queue
    item's whole purpose: "any defect found here is fixed before live paper
    begins"). Two fragments came through the loop, both of which would have
    entered the permanent execution record as if they were ordinary sessions:

      * 2026-09-13, a SUNDAY -- Globex reopens at 18:00 ET, so a Sunday-evening-
        only block of bars looked like a session and produced a no_signal row.
        There is no RTH in it at all.
      * 2026-09-14, the CURRENT day, whose data ended at 11:14 ET. It happened to
        be gate-blocked, so nothing was booked -- but had it filled,
        _resolve_fill_outcome would have hit its session_end_fallback and booked
        an exit at the last bar on disk, i.e. a fabricated outcome for a trade
        that is still open in the real world.

    Both are refused here rather than downstream, so the execution record only
    ever contains sessions that could actually be scored. A session qualifies
    when it has bars inside RTH AND its last bar is at or after the bookkeeping
    time-exit."""
    rth = day_df.between_time("09:30", "16:00", inclusive="left")
    if rth.empty:
        return False, "no RTH bars (overnight/Sunday-evening fragment)"
    last = day_df.index[-1].strftime("%H:%M")
    if last < SESSION_COMPLETE_BY:
        return False, f"session still in progress (last bar {last} ET < {SESSION_COMPLETE_BY})"
    return True, ""


def load_log() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    rows = []
    with LOG_PATH.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_row(row: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    assert_writable(LOG_PATH, "live execution log")
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(row, default=str) + "\n")


def running_state(rows: list[dict]) -> dict:
    """Fold every prior FILLED/PARTIAL row's pnl_usd into a running track
    record. Floor peak_profit_usd at 0 (matches capital_protection's own
    trailing_kill_level convention: peak = max(0, peak_profit_usd))."""
    equity = 0.0
    peak = 0.0
    trades = 0
    # PAPER ACCOUNT RESET (2026-09-14, dummy mode): a capital-protection kill is
    # final for the account it fired on. In dummy mode the next order opens a
    # NEW paper account so fill collection continues; the reset row is the
    # boundary and everything before it is history, not state. Rows after the
    # last reset are the live account.
    last_reset = max((i for i, r in enumerate(rows) if r.get("outcome") == "paper_account_reset"), default=-1)
    for r in rows[last_reset + 1:]:
        pnl = r.get("pnl_usd")
        if pnl is not None:
            equity += pnl
            trades += 1
            peak = max(peak, equity)
    return {"equity_usd": equity, "peak_profit_usd": peak, "paper_trades": trades, "paper_net_usd": equity}


def _resolve_fill_outcome(day_df: pd.DataFrame, direction: str, from_ts, entry_price: float,
                           stop: float, target: float, time_exit: str) -> dict:
    """EXECUTION-side bookkeeping exit -- see choice 4 above. Deliberately not
    shared code with bot_forward_log.py's _simulate_outcome."""
    after = day_df[day_df.index > from_ts]
    exit_price, exit_reason, exit_ts = None, None, None
    for ts, bar in after.iterrows():
        lo, hi = float(bar["Low"]), float(bar["High"])
        if direction == "long":
            if lo <= stop:
                exit_price, exit_reason, exit_ts = stop, "stop", ts; break
            if hi >= target:
                exit_price, exit_reason, exit_ts = target, "target", ts; break
        else:
            if hi >= stop:
                exit_price, exit_reason, exit_ts = stop, "stop", ts; break
            if lo <= target:
                exit_price, exit_reason, exit_ts = target, "target", ts; break
        if ts.strftime("%H:%M") >= time_exit:
            exit_price, exit_reason, exit_ts = float(bar["Close"]), "time_exit", ts; break
    if exit_price is None:
        last = day_df.iloc[-1]
        exit_price, exit_reason, exit_ts = float(last["Close"]), "session_end_fallback", day_df.index[-1]
    risk = abs(entry_price - stop)
    move = (exit_price - entry_price) if direction == "long" else (entry_price - exit_price)
    r_multiple = round(move / risk, 4) if risk else None
    return {"exit_price": round(exit_price, 4), "exit_reason": exit_reason, "exit_time": str(exit_ts),
            "risk_points": round(risk, 4), "r_multiple": r_multiple}


def run_session(date, day_df: pd.DataFrame, prior_rows: list[dict], history: pd.DataFrame | None = None):
    """B3 mode returns ONE row (one trade/day). Dummy mode returns a LIST of
    rows, one per order (up to max_orders_per_day), each run through the same
    gate -> order path -> bookkeeping as a B3 row, with the budget state
    evolving within the session. A CANDIDATE strategy (paper book) returns ONE
    row: its first signal of the session is the trade (one trade a session).
    `prior_rows` are THIS strategy's own rows (main() filters per strategy)."""
    name, gen = _strategy()
    sigs = _signals(gen, day_df, history)
    if STRATEGY == "dummy":
        rows, acc = [], list(prior_rows)
        # B2's decision is per DATE (it reloads the whole price file each call,
        # ~25s); compute it once per session and share it across the legs.
        decision = decision_for(date=str(date)) if sigs else None
        for sig in sigs[:CAPITAL_CFG.max_orders_per_day]:
            row = _run_one(date, day_df, acc, sig, name, decision=decision)
            row["leg"] = sig.market_context.get("fire_time")
            reasons = row.get("order_path", {}).get("reasons", []) if row["outcome"] == "blocked" else []
            if any("KILL" in str(x) for x in reasons):
                # The kill is RECORDED as a real capital-protection trip (it is
                # one, and a kill firing on a running P&L is itself evidence the
                # switch works). Then, because the dummy exists only to collect
                # fills, a fresh paper account opens and the same order is placed
                # once more under it. One reset per leg, never more.
                rows.append(row); acc.append(row)
                reset = {"date": str(date), "strategy": name, "leg": row["leg"],
                         "outcome": "paper_account_reset",
                         "note": "capital-protection kill on the dummy's paper account; new paper "
                                 "account opened so the execution sample keeps accumulating. "
                                 "The kill row above is the evidence; nothing was tuned.",
                         "killed_by": reasons}
                rows.append(reset); acc.append(reset)
                row = _run_one(date, day_df, acc, sig, name, decision=decision)
                row["leg"] = sig.market_context.get("fire_time")
            rows.append(row); acc.append(row)
        if not rows:
            rows = [{"date": str(date), "strategy": name, "outcome": "no_signal",
                     "note": "dummy: no fire time had a usable bar"}]
        return rows
    if not sigs:
        return {"date": str(date), "strategy": name, "outcome": "no_signal",
                "note": ("no B3 signal (one trade/day rule; not every session fires)" if STRATEGY == "b3"
                         else "no signal this session (strategy's own rules; one trade a session)")}
    return _run_one(date, day_df, prior_rows, sigs[0], name)


def _run_one(date, day_df: pd.DataFrame, prior_rows: list[dict], signal, name: str,
             decision: dict | None = None) -> dict:

    decision = decision if decision is not None else decision_for(date=str(date))
    if not decision["trade_permission"]:
        return {"date": str(date), "outcome": "blocked_by_risk_state_engine",
                "signal": {"direction": signal.direction, "entry": signal.entry, "stop": signal.stop,
                           "target": signal.target},
                "reasons": decision["permission_reasons"]}

    state = running_state(prior_rows)
    stop_distance_pts = abs(signal.entry - signal.stop)
    n_fills_so_far = sum(1 for r in prior_rows for _ in r.get("order_path", {}).get("fills", []))
    paper_slippage_measured = n_fills_so_far >= CAPITAL_CFG.slippage_window_fills
    # R-denominated paper capital model (2026-09-14 staff meeting): the budget
    # is computed against THIS trade's own swing as 1R, never against live dollars
    swing_usd = round(stop_distance_pts * MNQ_MULTIPLIER, 2)   # ONE rounded figure, used everywhere below
    eff = capital_protection.effective_config(CAPITAL_CFG, swing_usd)
    budget = capital_protection.budget_allowed(name, state["paper_trades"],
                                                paper_slippage_measured, state["paper_net_usd"], eff)
    remaining_budget_usd = max(0.0, budget + min(0.0, state["equity_usd"]))

    today = {
        "session_date": str(date),      # so the daily order cap counts THIS session's orders
        "strategy": name,
        "paper_trades": state["paper_trades"],
        "paper_slippage_measured": paper_slippage_measured,
        "paper_net_usd": state["paper_net_usd"],
        "per_trade_swing_usd": swing_usd,
        "capital_model": "paper_R" if CAPITAL_CFG.paper_mode else "live_usd",
        "one_r_usd": swing_usd,
        "paper_budget_r": CAPITAL_CFG.paper_starting_budget_r if CAPITAL_CFG.paper_mode else None,
        "equity_usd": state["equity_usd"],
        "peak_profit_usd": state["peak_profit_usd"],
        "remaining_budget_usd": remaining_budget_usd,
        "day_pnl_usd": 0.0,   # B3 is one trade/day -- always 0 at gate time, see choice notes in header
        "working_edge_pts": round(stop_distance_pts, 4),   # NOT a claimed edge -- see choice above
        "live_signals_today": [signal.direction],
        "reference_signals_today": [signal.direction],
    }

    leg = (getattr(signal, "market_context", {}) or {}).get("fire_time", "")
    seed = _seed_for(date) * 100 + (int(leg.replace(":", "")) % 100 if leg else 0)
    broker = SimulatedBroker(seed=seed,
                              reject_rate=BROKER_REJECT_RATE, partial_fill_rate=BROKER_PARTIAL_FILL_RATE,
                              disconnect_rate=BROKER_DISCONNECT_RATE, late_ack_rate=BROKER_LATE_ACK_RATE)
    broker.connect()
    path = OrderPath(broker, journal_dir=_journal_dir(), instrument=signal.instrument, cfg=CAPITAL_CFG)
    path.recover()
    result = path.submit_signal(signal, today=today, size_multiplier=decision["size_multiplier"],
                                 price_source=signal.entry)

    row = {"date": str(date), "strategy": name, "outcome": result["status"], "gate": today,
           "signal": {"direction": signal.direction, "entry": signal.entry, "stop": signal.stop,
                      "target": signal.target, "timestamp": str(signal.timestamp)},
           "decision": {"trade_permission": decision["trade_permission"],
                        "size_multiplier": decision["size_multiplier"]},
           "order_path": {k: v for k, v in result.items() if k != "journal"}}

    filled_qty = result.get("filled_qty", 0) or 0
    if filled_qty > 0:
        fills = result.get("fills", [])
        fill_price = float(fills[0]["price"]) if fills else float(signal.entry)
        time_exit = (getattr(signal, "market_context", {}) or {}).get("time_exit") or "15:55"
        outcome = _resolve_fill_outcome(day_df, signal.direction, signal.timestamp, fill_price,
                                         signal.stop, signal.target, time_exit)
        pnl_usd = round((outcome["r_multiple"] or 0.0) * outcome["risk_points"] * filled_qty * MNQ_MULTIPLIER, 2)
        row["bookkeeping"] = outcome
        row["pnl_usd"] = pnl_usd
    return row


def main(argv=None):
    import argparse
    global STRATEGY
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", choices=sorted(STRATEGIES), default=STRATEGY)
    a = ap.parse_args(argv if argv is not None else [])   # tests call main() bare
    STRATEGY = a.strategy
    print("=" * 78)
    print(f"BOT STACK PAPER RUN -- B7 (execution loop: signal -> decision -> order path)  strategy={STRATEGY}")
    print("=" * 78)

    from data_loader import load_price_data
    df, synthetic = load_price_data(context="bot_stack_paper_run.py", apply_holdout=False)
    if synthetic:
        raise SystemExit("synthetic data -- refusing")

    all_dates = sorted(set(df.index.date))
    anchor = _b7_execution_anchor(all_dates)
    mod = STRATEGY_MODULES.get(STRATEGY)
    if mod is not None and hasattr(mod, "precompute"):
        mod.precompute(df)          # trailing state variables, built once, no lookahead (see the module)
    print(f"\nB7 execution anchor: {anchor} (see choice 1 in the file header)")

    rows = load_log()
    # coverage is PER STRATEGY: a session B3 already scored is still unscored for
    # the dummy, and vice versa. Rows before the strategy field existed are B3's.
    name = _strategy()[0]
    logged_dates = {r["date"] for r in rows if r.get("strategy", B3_NAME) == name}
    eligible = [d for d in all_dates if d >= anchor and str(d) not in logged_dates]
    # the running track record (equity, peak, trade count) is PER STRATEGY too:
    # a candidate's paper account is its own, never pooled with the plumbing's
    own_rows = [r for r in rows if r.get("strategy", B3_NAME) == name]

    if not eligible:
        print(f"Nothing new: no session on/after {anchor} is both on disk and unlogged.")
        return

    skipped, n_appended = [], 0
    for d in eligible:
        day_df = df[df.index.date == d]
        ok, why = session_is_complete(day_df)
        if not ok:
            skipped.append((d, why))
            print(f"  {d}: SKIPPED -- {why}")
            continue
        out = run_session(d, day_df, own_rows, history=df)
        for row in (out if isinstance(out, list) else [out]):
            append_row(row)
            rows.append(row)
            own_rows.append(row)
            n_appended += 1
            tag = f"{d}" + (f" {row['leg']}" if row.get("leg") else "")
            if row["outcome"] == "no_signal":
                print(f"  {tag}: no signal")
            elif "pnl_usd" in row:
                print(f"  {tag}: {row['outcome']} -- {row['order_path']['filled_qty']} filled, "
                      f"{row['bookkeeping']['r_multiple']}R, ${row['pnl_usd']}")
            else:
                print(f"  {tag}: {row['outcome']}")

    if skipped:
        print(f"\n{len(skipped)} session(s) skipped as incomplete (not logged, will be "
              f"reconsidered on a later run once their data is complete).")
    print(f"\n{n_appended} new row(s) appended across {len(eligible) - len(skipped)} session(s). Log: {LOG_PATH}")
    print(f"Total logged: {len(load_log())}")


if __name__ == "__main__":
    enable_production()   # command-line entry point: the live paper loop may write its record
    main(sys.argv[1:])
