"""
base_entry_b3.py -- BOT MILESTONE B3: the placeholder base entry, coded exactly to
research/infrastructure/base-entry-b3-spec.md (frozen 2026-09-13).

THIS IS NOT AN EDGE. Every Signal it emits carries validation_status="placeholder".
It exists so the order path (B4), execution measurement (B5), kill switches (B6)
and the paper run (B7) have something ordinary and fully specified to carry, and
so the Risk/State Engine (B2) can be measured against the same entry unconditioned.

The rule (America/New_York, 1-minute bars):
  opening range  = high/low of 09:30:00-09:59:59
  breakout window = 10:00:00-11:29:59
  long  trigger  = first bar in the window whose CLOSE > range high
  short trigger  = first bar in the window whose CLOSE < range low
  one trade/day  = whichever fires first
  entry          = the NEXT bar's open after the trigger bar (never the trigger close)
  stop           = opposite side of the range        (unconditioned)
  target         = entry +/- 1.0 x range width       (unconditioned)
  time exit      = 15:55 ET (recorded in market_context; exits are simulated downstream)
No lookahead: nothing after the trigger bar is read to form the signal except the
next bar's open, which is the fill price by construction.

Walk-forward audit (same guarantees execution_clock_signal_engine.py enforces for
H118): exactly one signal per day at most; entry timestamp strictly after the
trigger timestamp; every field derivable from bars at or before the entry bar.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402

STRATEGY_NAME = "base_entry_b3_orb_placeholder"
STRATEGY_VERSION = "B3-1.0 (spec frozen 2026-09-13)"
VALIDATION_STATUS = "placeholder"
RANGE_START, RANGE_END = "09:30", "10:00"
WINDOW_START, WINDOW_END = "10:00", "11:30"
TIME_EXIT = "15:55"
TARGET_MULT = 1.0


def signal_for_day(day_df: pd.DataFrame) -> dict | None:
    """Pure function of one session's bars. Returns a raw signal dict or None."""
    rng = day_df.between_time(RANGE_START, RANGE_END, inclusive="left")
    if len(rng) < 20:
        return None
    hi, lo = float(rng["High"].max()), float(rng["Low"].min())
    width = hi - lo
    if width <= 0:
        return None
    win = day_df.between_time(WINDOW_START, WINDOW_END, inclusive="left")
    if win.empty:
        return None
    closes = win["Close"].to_numpy(dtype=float)
    idx = win.index
    trigger_pos, direction = None, None
    for i, c in enumerate(closes):
        if c > hi:
            trigger_pos, direction = i, "long"; break
        if c < lo:
            trigger_pos, direction = i, "short"; break
    if trigger_pos is None:
        return None
    trigger_ts = idx[trigger_pos]
    after = day_df[day_df.index > trigger_ts]
    if after.empty:
        return None
    entry_ts = after.index[0]
    entry = float(after["Open"].iloc[0])
    if direction == "long":
        stop, target = lo, entry + TARGET_MULT * width
    else:
        stop, target = hi, entry - TARGET_MULT * width
    return {"date": day_df.index[0].date(), "direction": direction, "range_high": hi, "range_low": lo,
            "range_width": width, "trigger_time": trigger_ts, "entry_time": entry_ts,
            "entry": entry, "stop": stop, "target": target, "time_exit": TIME_EXIT}


def generate_signals(df: pd.DataFrame) -> list[Signal]:
    out = []
    for _, g in df.groupby(df.index.normalize()):
        s = signal_for_day(g)
        if s is None:
            continue
        out.append(Signal(
            strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
            timestamp=s["entry_time"], instrument="MNQ", timeframe="1m",
            direction=s["direction"], entry=s["entry"], stop=s["stop"], target=s["target"],
            risk_multiple=risk_multiple(s["entry"], s["stop"], s["target"]),
            validation_status=VALIDATION_STATUS,
            market_context={"placeholder": True, "range_high": s["range_high"], "range_low": s["range_low"],
                            "range_width": s["range_width"], "trigger_time": str(s["trigger_time"]),
                            "time_exit": TIME_EXIT, "date": str(s["date"])},
        ))
    return out


def audit(signals: list[Signal]) -> dict:
    dates = [sg.market_context["date"] for sg in signals]
    dup = len(dates) - len(set(dates))
    lookahead = sum(1 for sg in signals if pd.Timestamp(sg.market_context["trigger_time"]) >= pd.Timestamp(sg.timestamp))
    not_placeholder = sum(1 for sg in signals if sg.validation_status != VALIDATION_STATUS)
    return {"n_signals": len(signals), "duplicate_days": dup, "lookahead_violations": lookahead,
            "non_placeholder_labels": not_placeholder,
            "pass": dup == 0 and lookahead == 0 and not_placeholder == 0}


def main():
    from data_loader import load_price_data
    df, syn = load_price_data(context="base_entry_b3 (bot layer, holdout boundary not applied)", apply_holdout=False)
    if syn:
        raise SystemExit("synthetic -- refusing")
    sigs = generate_signals(df)
    a = audit(sigs)
    days = len(set(df.index.date))
    print(json.dumps({"strategy": STRATEGY_NAME, "version": STRATEGY_VERSION, "sessions_on_disk": days,
                      "audit": a, "fire_rate": round(a["n_signals"] / days, 3) if days else None,
                      "last_signal": None if not sigs else {"date": sigs[-1].market_context["date"], "direction": sigs[-1].direction,
                                                            "entry": sigs[-1].entry, "stop": sigs[-1].stop, "target": sigs[-1].target,
                                                            "validation_status": sigs[-1].validation_status}}, indent=2, default=str))


if __name__ == "__main__":
    main()
