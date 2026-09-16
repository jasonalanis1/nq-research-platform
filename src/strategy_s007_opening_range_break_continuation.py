"""
strategy_s007_opening_range_break_continuation.py -- S007, opening-range break
continuation with an opening-range-SCALED stop. The first candidate sourced under
Jason's Amendment 1 (September 16th 2026) preference for INTRADAY STRATEGIES THAT
TRADE MOST DAYS.

FROZEN with its spec:
research/infrastructure/strategy-specs/S007-opening-range-break-continuation.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit.

THIS IS NOT base_entry_b3.py. B3 is frozen PLUMBING with no claimed edge and,
by its own spec, an "unconditioned" stop (far side of the range) and target
(one range width). S007 puts a real trade around the same daily-firing event:

  opening range OR = high/low of 09:30:00-09:59:59 ET, width W = high - low
  break window     = 10:00:00-12:59:59 ET (covers the midday window hyp-000162
                     describes; B3 stops at 11:30)
  trigger          = first bar whose CLOSE > OR_high + 0.10*W (long)
                                    or CLOSE < OR_low  - 0.10*W (short)
                     -- the 0.10*W buffer is the decisiveness requirement
  one trade a day  = whichever side fires first
  entry            = the NEXT bar's OPEN after the trigger bar
  stop             = 0.50 * W against entry      (SCALED to the opening range --
                     the validated marker of the day's range regime, hyp-000162)
  target           = entry +/- 1.50 * risk       (1.5R; the enlarged midday
                     excursion is symmetric, so 1:1 cannot clear costs)
  time exit        = 15:55 ET, same session; no cross-session exit_ts
  sizing           = 1 micro MNQ, always
  costs            = ASSUMED $2.50/side + 1 tick/side = $6.00 per micro RT

NO LOOK-AHEAD: the OR is frozen at 10:00:00; the scan only moves forward; the
only bar read after the trigger is the next bar's open, which is the fill price
by construction.

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, generate_signals(df, history=None)
-> list[strategy_contract.Signal], the same shape S001a / S002 / S003 /
execution_dummy / base_entry_b3 expose to bot_stack_paper_run.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402

STRATEGY_ID = "S007"
STRATEGY_NAME = "s007_opening_range_break_continuation"
STRATEGY_VERSION = "S007-1.0 (frozen 2026-09-16)"
VALIDATION_STATUS = "paper-candidate"
SPEC_PATH = "research/infrastructure/strategy-specs/S007-opening-range-break-continuation.md"

RANGE_START, RANGE_END = "09:30", "10:00"       # opening range, inclusive-left
WINDOW_START, WINDOW_END = "10:00", "13:00"     # break window, inclusive-left
MIN_RANGE_BARS = 20                             # completeness guard on the OR window
BREAK_BUFFER = 0.10                             # decisive break = 0.10 * W beyond the extreme
STOP_FRACTION = 0.50                            # stop = 0.50 * W against entry
TARGET_R_MULTIPLE = 1.50                        # target = 1.50 * risk
TIME_EXIT = "15:55"
INSTRUMENT = "MNQ"


def signal_for_day(day_df: pd.DataFrame) -> dict | None:
    """Pure function of ONE session's bars. Returns a raw signal dict or None."""
    rng = day_df.between_time(RANGE_START, RANGE_END, inclusive="left")
    if len(rng) < MIN_RANGE_BARS:
        return None                                  # incomplete opening window
    hi, lo = float(rng["High"].max()), float(rng["Low"].min())
    width = hi - lo
    if width <= 0:
        return None                                  # degenerate range, no trade
    up = hi + BREAK_BUFFER * width
    dn = lo - BREAK_BUFFER * width
    win = day_df.between_time(WINDOW_START, WINDOW_END, inclusive="left")
    if win.empty:
        return None
    trigger_ts, direction = None, None
    for ts, c in zip(win.index, win["Close"].to_numpy(dtype=float)):
        if c > up:
            trigger_ts, direction = ts, "long"
            break
        if c < dn:
            trigger_ts, direction = ts, "short"
            break
    if trigger_ts is None:
        return None
    after = day_df[day_df.index > trigger_ts]
    if after.empty:
        return None
    entry_ts = after.index[0]
    entry = float(after["Open"].iloc[0])
    risk = STOP_FRACTION * width
    if risk <= 0:
        return None
    if direction == "long":
        stop = entry - risk
        target = entry + TARGET_R_MULTIPLE * risk
    else:
        stop = entry + risk
        target = entry - TARGET_R_MULTIPLE * risk
    return {"date": day_df.index[0].date(), "direction": direction,
            "range_high": hi, "range_low": lo, "range_width": width,
            "break_level": up if direction == "long" else dn,
            "trigger_time": trigger_ts, "entry_time": entry_ts,
            "entry": entry, "stop": stop, "target": target, "risk_points": risk}


def _to_signal(s: dict) -> Signal:
    return Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=s["entry_time"], instrument=INSTRUMENT, timeframe="1m",
        direction=s["direction"], entry=s["entry"], stop=s["stop"], target=s["target"],
        risk_multiple=risk_multiple(s["entry"], s["stop"], s["target"]),
        validation_status=VALIDATION_STATUS,
        market_context={
            "strategy_id": STRATEGY_ID, "spec": SPEC_PATH, "date": str(s["date"]),
            "condition": "close beyond opening range by >= 0.10 x range width, 10:00-13:00 ET",
            "range_high": s["range_high"], "range_low": s["range_low"],
            "range_width": s["range_width"], "break_level": s["break_level"],
            "trigger_time": str(s["trigger_time"]), "risk_points": s["risk_points"],
            "stop_basis": "0.50 x opening-range width (hyp-000162 / M30 magnitude fact)",
            "target_basis": f"{TARGET_R_MULTIPLE}R",
            "time_exit": TIME_EXIT,
        },
    )


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    """One or more sessions in `df`; at most one Signal per session. `history` is
    accepted for the loop's uniform call shape and is not needed (no trailing state)."""
    out = []
    for _, g in df.groupby(df.index.date):
        s = signal_for_day(g)
        if s is not None:
            out.append(_to_signal(s))
    return out


def audit(signals: list[Signal]) -> dict:
    dates = [sg.market_context["date"] for sg in signals]
    dup = len(dates) - len(set(dates))
    lookahead = sum(1 for sg in signals
                    if pd.Timestamp(sg.market_context["trigger_time"]) >= pd.Timestamp(sg.timestamp))
    bad_rr = sum(1 for sg in signals if round(sg.risk_multiple, 2) != TARGET_R_MULTIPLE)
    zero_risk = sum(1 for sg in signals if abs(sg.entry - sg.stop) <= 0)
    return {"n_signals": len(signals), "duplicate_days": dup, "lookahead_violations": lookahead,
            "wrong_reward_risk": bad_rr, "zero_risk_signals": zero_risk,
            "pass": dup == 0 and lookahead == 0 and bad_rr == 0 and zero_risk == 0}


def main():
    from data_loader import load_price_data
    df, syn = load_price_data(context="strategy_s007 (audit only)", apply_holdout=False)
    if syn:
        raise SystemExit("synthetic -- refusing")
    sigs = generate_signals(df)
    a = audit(sigs)
    days = len(set(df.index.date))
    print(json.dumps({"strategy": STRATEGY_NAME, "version": STRATEGY_VERSION,
                      "sessions_on_disk": days, "audit": a,
                      "fire_rate": round(a["n_signals"] / days, 3) if days else None},
                     indent=2, default=str))


if __name__ == "__main__":
    main()
