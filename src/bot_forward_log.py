"""
bot_forward_log.py -- BOT MILESTONE B4a/B7-EARLY: the FREE statistical forward
test of the bot stack. Queued in research/NEXT_UP.md ("B4a/B7-EARLY", added
September 13th ~10:30 pm CT): "can we paper trade until we can move to the
TradingView option?" -- yes, the free half of it. Built the cycle B4a's core
(src/order_path.py, src/simulated_broker.py) landed, per that item's own
instruction ("start it the first cycle B4a's core is in place").

TWO CLOCKS RULE, binding, restated here because it is easy to blur with B4a:
this is a STATISTICAL forward test, on the same pattern as
forward_validate_h118_daily.py. It measures whether base_entry_b3.py's signal
+ risk_state_engine.py's decision behave as expected on unseen days. It
measures NOTHING about execution -- no real order construction, no broker
submission, no slippage, no latency, no rejects. Its simulated fill is "the
session's own bars, after the fact" (legitimate once a session has closed --
this is not a live intraday feed), not a broker fill, and its output is NEVER
described as paper trading and NEVER compared against a broker paper run.
src/order_path.py + src/simulated_broker.py are the EXECUTION side (B4a); this
file is the STATISTICAL side. They share the same Signal and Risk/State
Engine inputs and nothing else.

B3's entry is a placeholder; its P&L here is never evidence of an edge (per
the base-entry-b3 spec). The one honest question this log exists to answer,
pre-registered in that spec: does B2 (Risk/State Engine sizing/stop/target/
permission) improve B3's risk-adjusted behaviour versus the same entry
unconditioned? So every row logs BOTH configurations side by side --
BASE (unconditioned stop/target, size 1, always permitted) and BASE+B2
(risk_state_engine's stop/target/size/permission) -- on the identical signal,
identical session.

FORWARD BOUNDARY: only sessions on/after BOT_FORWARD_ANCHOR are eligible --
matches the H118 forward-validation pattern (research/NEXT_UP.md item, and
forward_validate_h118_daily.py's FORWARD_VALIDATION_ANCHOR): earlier sessions
are historical and running this script on them would just be Discovery
wearing a forward costume, not genuine forward evidence. The anchor is the
date this file was built and B4a's core landed.

Log: research/forward_validation/bot_stack_forward_log.jsonl (append-only,
one JSON object per session that had a B3 signal; a no-signal day is not
logged as a row -- the fire rate is already characterized in
docs/BOT_ROADMAP.md / base_entry_b3.py's own audit). Idempotent: re-running
never re-logs a date already present.

HOW TO RUN (each cycle, same pattern as the H118 daily checker):
    python3 src/bot_forward_log.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from base_entry_b3 import STRATEGY_NAME, STRATEGY_VERSION, TIME_EXIT, signal_for_day  # noqa: E402
from risk_state_engine import decision_for  # noqa: E402

PROJECT_ROOT = ROOT.parent
LOG_DIR = PROJECT_ROOT / "research" / "forward_validation"
LOG_PATH = LOG_DIR / "bot_stack_forward_log.jsonl"

# The date B4a's core (src/order_path.py, src/simulated_broker.py) landed --
# see research/infrastructure/b4a-order-path-spec.md. Sessions before this
# are historical, not forward.
BOT_FORWARD_ANCHOR = pd.Timestamp("2026-09-14").date()


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
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(row, default=str) + "\n")


def _simulate_outcome(day_df: pd.DataFrame, direction: str, entry_ts, entry: float, stop: float,
                       target: float, time_exit: str) -> dict:
    """Walk the session's own already-elapsed bars forward from entry, bar by
    bar, first touch wins. Same-bar stop-and-target ambiguity resolves to the
    stop (conservative, never assumed in the strategy's favour). No lookahead
    concern: this only ever runs on a session that has already closed."""
    after = day_df[day_df.index > entry_ts]
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
        # never resolved within the day's own bars (shouldn't happen with a
        # 15:55 time-exit rule inside RTH) -- flat at the last bar, disclosed.
        last = day_df.iloc[-1]
        exit_price, exit_reason, exit_ts = float(last["Close"]), "session_end_fallback", day_df.index[-1]

    risk = abs(entry - stop)
    move = (exit_price - entry) if direction == "long" else (entry - exit_price)
    r_multiple = round(move / risk, 4) if risk else None
    return {"exit_price": round(exit_price, 4), "exit_reason": exit_reason, "exit_time": str(exit_ts),
            "r_multiple": r_multiple}


def build_row(date, day_df: pd.DataFrame) -> dict | None:
    raw = signal_for_day(day_df)
    if raw is None:
        return None   # no-signal day -- not logged as a row, per the header note

    base_outcome = _simulate_outcome(day_df, raw["direction"], raw["entry_time"], raw["entry"],
                                      raw["stop"], raw["target"], TIME_EXIT)

    b2 = decision_for(date=str(date))
    row = {
        "date": str(date), "strategy": STRATEGY_NAME, "strategy_version": STRATEGY_VERSION,
        "direction": raw["direction"], "entry_time": str(raw["entry_time"]), "entry": round(raw["entry"], 4),
        "base": {"stop": round(raw["stop"], 4), "target": round(raw["target"], 4), "size": 1,
                  "permitted": True, **base_outcome},
    }

    atr_pts = b2["inputs"].get("atr14_points")
    if b2["trade_permission"] and atr_pts:
        if raw["direction"] == "long":
            b2_stop = raw["entry"] - b2["stop_distance_atr"] * atr_pts
            b2_target = raw["entry"] + b2["target_distance_atr"] * atr_pts
        else:
            b2_stop = raw["entry"] + b2["stop_distance_atr"] * atr_pts
            b2_target = raw["entry"] - b2["target_distance_atr"] * atr_pts
        b2_outcome = _simulate_outcome(day_df, raw["direction"], raw["entry_time"], raw["entry"],
                                        b2_stop, b2_target, TIME_EXIT)
        row["base_plus_b2"] = {"stop": round(b2_stop, 4), "target": round(b2_target, 4),
                                 "size": b2["size_multiplier"], "permitted": True, **b2_outcome}
    else:
        row["base_plus_b2"] = {"permitted": False,
                                 "reason": "; ".join(b2.get("permission_reasons", [])) or "no usable B2 decision"}
    return row


def main():
    print("=" * 78)
    print("BOT STACK FORWARD LOG -- B4a/B7-EARLY (statistical forward test, no capital, no execution)")
    print("=" * 78)
    print(f"\nAnchor: sessions on/after {BOT_FORWARD_ANCHOR} only (forward, not historical).")
    print("TWO CLOCKS RULE: this measures the STACK's behaviour, not execution -- see file header.\n")

    from data_loader import load_price_data
    df, synthetic = load_price_data(context="bot_forward_log.py", apply_holdout=False)
    if synthetic:
        raise SystemExit("synthetic data -- refusing")

    existing = load_log()
    logged_dates = {r["date"] for r in existing}
    all_dates = sorted(set(df.index.date))
    eligible = [d for d in all_dates if d >= BOT_FORWARD_ANCHOR]

    if not eligible:
        print(f"No session on/after {BOT_FORWARD_ANCHOR} exists in the data on disk yet. Nothing to do.")
        return

    new_rows = 0
    for d in eligible:
        if str(d) in logged_dates:
            continue
        day_df = df[df.index.date == d]
        row = build_row(d, day_df)
        if row is not None:
            append_row(row)
            new_rows += 1
            print(f"  {d}: {row['direction']} signal -- BASE {row['base']['r_multiple']}R "
                  f"({row['base']['exit_reason']}), "
                  f"BASE+B2 {'blocked: ' + row['base_plus_b2']['reason'] if not row['base_plus_b2']['permitted'] else str(row['base_plus_b2']['r_multiple']) + 'R (' + row['base_plus_b2']['exit_reason'] + ')'}")
        else:
            print(f"  {d}: no B3 signal (one trade/day rule; not every session fires)")

    print(f"\n{new_rows} new row(s) appended. Log: {LOG_PATH}")
    print(f"Total logged: {len(load_log())}")


if __name__ == "__main__":
    main()
