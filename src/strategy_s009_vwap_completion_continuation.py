"""
strategy_s009_vwap_completion_continuation.py -- S009, afternoon VWAP-completion
continuation.

FROZEN with its spec:
research/infrastructure/strategy-specs/S009-afternoon-vwap-completion-continuation.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit.

THE MECHANISM (one paragraph; the spec is the authority)
  The forced counterparty is agency execution: institutional parent orders worked
  to a full-day VWAP / percentage-of-volume benchmark. The quantity is fixed in
  the morning, the deadline is the cash close, and the US volume curve is
  back-loaded, so whatever is still outstanding in the early afternoon is worked
  into the remaining hours REGARDLESS OF PRICE. An algo whose side is behind the
  session VWAP -- buyers when price has risen above it, sellers when price has
  fallen below it -- cannot wait for a better price; it must press. That is
  price-insensitive, one-directional flow on a clock, and it predicts
  CONTINUATION of the benchmark gap into the close. The quantity the mechanism is
  defined on is the distance of price from the session's own VWAP, not the day's
  directional move.

THE RULES (restated from the spec)
  known-at     13:30 ET. From that session's 09:30-13:30 RTH bars only:
                 VWAP = sum(TP * Volume) / sum(Volume), TP = (H + L + C) / 3
                 RNG  = High(09:30..13:30) - Low(09:30..13:30)
                 D    = Close(13:30 bar) - VWAP
  condition    |D| >= 0.30 * RNG
  direction    sign(D) -- continuation, never a fade
  entry        the NEXT bar's OPEN after the 13:30 ET bar
  stop         0.50 * RNG against entry
  target       entry +/- 1.50 * risk (1.5R)
  time exit    15:55 ET, same session; flat before the cash close; no
               cross-session exit_ts
  sizing       1 micro MNQ, always
  costs        src/cost_model.py. MNQ market $2.60 = 1.300 pt (decision basis);
               MNQ limit $2.10 = 1.050 pt (OPTIMISTIC); NQ market $14.90 =
               0.745 pt; NQ limit $9.90 = 0.495 pt (OPTIMISTIC). ASSUMED (s.11).

NO LOOK-AHEAD: VWAP, RNG and D are measured from bars at or before 13:30; the
only bar read after that is the next bar's open, which is the fill price by
construction. The scan never moves backwards.

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, precompute(history),
generate_signals(df, history=None) -> list[strategy_contract.Signal], the same
shape S001a / S002 / S003 / S008 / execution_dummy / base_entry_b3 expose to
bot_stack_paper_run.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402
import cost_model  # noqa: E402

STRATEGY_ID = "S009"
STRATEGY_NAME = "s009_vwap_completion_continuation"
STRATEGY_VERSION = "S009-1.0 (frozen 2026-09-16)"
VALIDATION_STATUS = "paper-candidate"
SPEC_PATH = "research/infrastructure/strategy-specs/S009-afternoon-vwap-completion-continuation.md"

SESSION_OPEN = "09:30"
DECISION_TIME = "13:30"          # the bar whose CLOSE is measured against the session VWAP
DISLOCATION_FRACTION = 0.30      # |D| >= 0.30 * RNG
STOP_FRACTION = 0.50             # stop = 0.50 * RNG against entry
TARGET_R_MULTIPLE = 1.50
MIN_WINDOW_BARS = 220            # completeness guard on 09:30-13:30 (240 minutes)
TIME_EXIT = "15:55"
INSTRUMENT = "MNQ"


def precompute(history: pd.DataFrame) -> None:
    """S009 carries no trailing state: every input is measured inside the session
    being traded. Present so the module satisfies the paper-loop contract."""
    return None


def session_window(day_df: pd.DataFrame) -> pd.DataFrame:
    """09:30 through the 13:30 bar inclusive -- everything known at the decision."""
    return day_df.between_time(SESSION_OPEN, DECISION_TIME, inclusive="both")


def session_stats(day_df: pd.DataFrame) -> dict | None:
    """VWAP, RNG and D for one session, or None if the session is a fragment."""
    win = session_window(day_df)
    if len(win) < MIN_WINDOW_BARS:
        return None
    if win.index[0].strftime("%H:%M") != SESSION_OPEN or win.index[-1].strftime("%H:%M") != DECISION_TIME:
        return None                                   # no 09:30 open bar or no 13:30 bar
    vol = win["Volume"].astype(float)
    total_vol = float(vol.sum())
    if not (total_vol > 0):
        return None
    tp = (win["High"] + win["Low"] + win["Close"]) / 3.0
    vwap = float((tp * vol).sum() / total_vol)
    rng = float(win["High"].max() - win["Low"].min())
    if not (rng > 0):
        return None
    return {"window": win, "vwap": vwap, "range": rng,
            "dislocation": float(win["Close"].iloc[-1]) - vwap}


def signal_for_day(day_df: pd.DataFrame) -> dict | None:
    """Pure function of ONE session's bars. Returns a raw signal dict or None."""
    day = day_df.index[0].date()
    st = session_stats(day_df)
    if st is None:
        return None
    rng, d = st["range"], st["dislocation"]
    if abs(d) < DISLOCATION_FRACTION * rng:
        return None                                   # not dislocated from the benchmark
    win = st["window"]
    after = day_df[day_df.index > win.index[-1]]
    if after.empty:
        return None
    entry_ts = after.index[0]
    if entry_ts.strftime("%H:%M") >= TIME_EXIT:
        return None                                   # no room before the flat time
    entry = float(after["Open"].iloc[0])
    direction = "long" if d > 0 else "short"
    risk = STOP_FRACTION * rng
    if risk <= 0:
        return None
    if direction == "long":
        stop, target = entry - risk, entry + TARGET_R_MULTIPLE * risk
    else:
        stop, target = entry + risk, entry - TARGET_R_MULTIPLE * risk
    return {"date": day, "direction": direction, "dislocation": d, "vwap": st["vwap"],
            "session_range": rng, "decision_time": win.index[-1], "entry_time": entry_ts,
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
            "condition": (f"|Close({DECISION_TIME}) - VWAP({SESSION_OPEN}-{DECISION_TIME})| >= "
                          f"{DISLOCATION_FRACTION} x the {SESSION_OPEN}-{DECISION_TIME} range"),
            "dislocation_points": s["dislocation"], "session_vwap": s["vwap"],
            "session_range": s["session_range"],
            "decision_time": str(s["decision_time"]), "risk_points": s["risk_points"],
            "stop_basis": f"{STOP_FRACTION} x the {SESSION_OPEN}-{DECISION_TIME} range",
            "target_basis": f"{TARGET_R_MULTIPLE}R",
            "cost_basis": cost_model.DEFAULT_NOTE,
            "time_exit": TIME_EXIT,
        },
    )


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    """One or more sessions in `df`; at most one Signal per session."""
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
                    if pd.Timestamp(sg.market_context["decision_time"]) >= pd.Timestamp(sg.timestamp))
    bad_rr = sum(1 for sg in signals if round(sg.risk_multiple, 2) != TARGET_R_MULTIPLE)
    zero_risk = sum(1 for sg in signals if abs(sg.entry - sg.stop) <= 0)
    wrong_dir = sum(1 for sg in signals
                    if (sg.market_context["dislocation_points"] > 0) != (sg.direction == "long"))
    below_thresh = sum(1 for sg in signals
                       if abs(sg.market_context["dislocation_points"])
                       < DISLOCATION_FRACTION * sg.market_context["session_range"] - 1e-9)
    return {"n_signals": len(signals), "duplicate_days": dup, "lookahead_violations": lookahead,
            "wrong_reward_risk": bad_rr, "zero_risk_signals": zero_risk,
            "wrong_direction": wrong_dir, "below_threshold": below_thresh,
            "pass": dup == 0 and lookahead == 0 and bad_rr == 0 and zero_risk == 0
                    and wrong_dir == 0 and below_thresh == 0}


def main():
    from data_loader import load_price_data
    df, syn = load_price_data(context="strategy_s009 (audit only)", apply_holdout=False)
    if syn:
        raise SystemExit("synthetic -- refusing")
    sigs = generate_signals(df, df)
    a = audit(sigs)
    days = len(set(df.index.date))
    print(json.dumps({"strategy": STRATEGY_NAME, "version": STRATEGY_VERSION,
                      "sessions": days, "audit": a}, indent=1, default=str))
    return 0 if a["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
