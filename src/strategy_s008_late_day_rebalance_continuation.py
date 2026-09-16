"""
strategy_s008_late_day_rebalance_continuation.py -- S008, late-day
constant-leverage rebalance continuation.

REOPENED AS AN INPUT-ERROR CORRECTION, NOT A SALVAGE AND NOT A SECOND ATTEMPT.
S008 was specified on September 16th 2026 and sent to LEARN **without a screen**,
refused at a pre-freeze "cost budget" that required a gross edge of 3x the
assumed cost. Both halves of that refusal were wrong:
  * the assumed cost, $6.00 per micro round trip = 3.00 index points, charged a
    FULL-SIZE NQ commission ($2.50/side) to a MICRO contract. The real MNQ
    market round trip is $2.60 = 1.30 index points (src/cost_model.py);
  * the "3x cost" pre-screen was Tony's own invention. The standing directive
    never contained it, and Jason deleted it in Amendment 2: at SPECIFY a
    candidate is rejected only if its expected per-trade edge is below the
    per-trade COST ITSELF.
The candidate's specified cell grossed +2.55 points per trade, which is above
every one of the four corrected costs. It was therefore rejected on an ERRONEOUS
INPUT, never on evidence, and it goes through the loop normally from here.

FROZEN with its spec:
research/infrastructure/strategy-specs/S008-late-day-rebalance-continuation.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit.

THE RULES (restated from the spec; the spec is the authority)
  known-at     15:00 ET. From that session's RTH bars only:
                 RNG = High(09:30..15:00) - Low(09:30..15:00)
                 M   = Close(15:00 bar) - Open(09:30 bar)
  condition    |M| >= 0.50 * median(RNG) over the trailing 20 RTH sessions,
               strictly BEFORE this one (a large-move day: the forced rebalance
               notional is proportional to the day's return)
  direction    sign(M) -- continuation, never a fade
  entry        the NEXT bar's OPEN after the 15:00 ET bar
  stop         0.50 * RNG against entry
  target       entry +/- 1.50 * risk (1.5R)
  time exit    15:55 ET, same session; flat before the cash close; no
               cross-session exit_ts
  sizing       1 micro MNQ, always
  costs        src/cost_model.py. MNQ market $2.60 = 1.300 pt (decision basis);
               MNQ limit $2.10 = 1.050 pt (OPTIMISTIC); NQ market $14.90 =
               0.745 pt; NQ limit $9.90 = 0.495 pt (OPTIMISTIC). ASSUMED (s.11).

NO LOOK-AHEAD: the trailing-20 median is built only from sessions strictly
earlier than the one being traded; RNG and M are measured from bars at or before
15:00; the only bar read after that is the next bar's open, which is the fill
price by construction. The scan never moves backwards.

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, precompute(history),
generate_signals(df, history=None) -> list[strategy_contract.Signal], the same
shape S001a / S002 / S003 / execution_dummy / base_entry_b3 expose to
bot_stack_paper_run.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402
import cost_model  # noqa: E402

STRATEGY_ID = "S008"
STRATEGY_NAME = "s008_late_day_rebalance_continuation"
STRATEGY_VERSION = "S008-1.0 (frozen 2026-09-16)"
VALIDATION_STATUS = "paper-candidate"
SPEC_PATH = "research/infrastructure/strategy-specs/S008-late-day-rebalance-continuation.md"

SESSION_OPEN = "09:30"
DECISION_TIME = "15:00"          # the bar whose CLOSE measures the day's move
MOVE_THRESHOLD = 0.50            # |M| >= 0.50 * trailing-20 median RNG
STOP_FRACTION = 0.50             # stop = 0.50 * RNG against entry
TARGET_R_MULTIPLE = 1.50
TRAILING_SESSIONS = 20
MIN_WINDOW_BARS = 300            # completeness guard on 09:30-15:00 (330 minutes)
TIME_EXIT = "15:55"
INSTRUMENT = "MNQ"

# Filled by precompute(): session date -> median RNG of the previous 20 sessions.
_TRAILING_MEDIAN: dict = {}


def session_window(day_df: pd.DataFrame) -> pd.DataFrame:
    """09:30 through the 15:00 bar inclusive -- everything known at the decision."""
    return day_df.between_time(SESSION_OPEN, DECISION_TIME, inclusive="both")


def session_range(day_df: pd.DataFrame) -> float | None:
    """RNG = the 09:30-15:00 high-low range, or None if the session is a fragment."""
    win = session_window(day_df)
    if len(win) < MIN_WINDOW_BARS:
        return None
    if win.index[0].strftime("%H:%M") != SESSION_OPEN or win.index[-1].strftime("%H:%M") != DECISION_TIME:
        return None                                   # no 09:30 open bar or no 15:00 bar
    rng = float(win["High"].max() - win["Low"].min())
    return rng if rng > 0 else None


def precompute(history: pd.DataFrame) -> None:
    """Build, ONCE over `history`, the trailing-20-session median of RNG for every
    session -- from sessions STRICTLY BEFORE it, so nothing reads its own day or
    any later one."""
    _TRAILING_MEDIAN.clear()
    dates, rngs = [], []
    for day, g in history.groupby(history.index.date):
        r = session_range(g)
        if r is None:
            continue
        dates.append(day)
        rngs.append(r)
    s = pd.Series(rngs, index=pd.Index(dates))
    med = s.rolling(TRAILING_SESSIONS, min_periods=TRAILING_SESSIONS).median().shift(1)
    for d, m in med.items():
        if np.isfinite(m):
            _TRAILING_MEDIAN[d] = float(m)


def signal_for_day(day_df: pd.DataFrame) -> dict | None:
    """Pure function of ONE session's bars plus the precomputed trailing median.
    Returns a raw signal dict or None."""
    day = day_df.index[0].date()
    trailing = _TRAILING_MEDIAN.get(day)
    if trailing is None or not (trailing > 0):
        return None                                   # no 20-session history yet
    rng = session_range(day_df)
    if rng is None:
        return None
    win = session_window(day_df)
    move = float(win["Close"].iloc[-1] - win["Open"].iloc[0])
    if abs(move) < MOVE_THRESHOLD * trailing:
        return None                                   # not a large-move day
    after = day_df[day_df.index > win.index[-1]]
    if after.empty:
        return None
    entry_ts = after.index[0]
    if entry_ts.strftime("%H:%M") >= TIME_EXIT:
        return None                                   # no room before the flat time
    entry = float(after["Open"].iloc[0])
    direction = "long" if move > 0 else "short"
    risk = STOP_FRACTION * rng
    if risk <= 0:
        return None
    if direction == "long":
        stop, target = entry - risk, entry + TARGET_R_MULTIPLE * risk
    else:
        stop, target = entry + risk, entry - TARGET_R_MULTIPLE * risk
    return {"date": day, "direction": direction, "move": move, "session_range": rng,
            "trailing_median_range": trailing, "decision_time": win.index[-1],
            "entry_time": entry_ts, "entry": entry, "stop": stop, "target": target,
            "risk_points": risk}


def _to_signal(s: dict) -> Signal:
    return Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=s["entry_time"], instrument=INSTRUMENT, timeframe="1m",
        direction=s["direction"], entry=s["entry"], stop=s["stop"], target=s["target"],
        risk_multiple=risk_multiple(s["entry"], s["stop"], s["target"]),
        validation_status=VALIDATION_STATUS,
        market_context={
            "strategy_id": STRATEGY_ID, "spec": SPEC_PATH, "date": str(s["date"]),
            "condition": (f"|Close({DECISION_TIME}) - Open({SESSION_OPEN})| >= {MOVE_THRESHOLD} x "
                          f"trailing-{TRAILING_SESSIONS} median {SESSION_OPEN}-{DECISION_TIME} range"),
            "move_points": s["move"], "session_range": s["session_range"],
            "trailing_median_range": s["trailing_median_range"],
            "decision_time": str(s["decision_time"]), "risk_points": s["risk_points"],
            "stop_basis": f"{STOP_FRACTION} x the {SESSION_OPEN}-{DECISION_TIME} range",
            "target_basis": f"{TARGET_R_MULTIPLE}R",
            "cost_basis": cost_model.DEFAULT_NOTE,
            "time_exit": TIME_EXIT,
        },
    )


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    """One or more sessions in `df`; at most one Signal per session. `history` is
    used only to build the trailing-20 median when precompute() has not run."""
    if not _TRAILING_MEDIAN:
        precompute(history if history is not None else df)
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
                    if (sg.market_context["move_points"] > 0) != (sg.direction == "long"))
    below_thresh = sum(1 for sg in signals
                       if abs(sg.market_context["move_points"])
                       < MOVE_THRESHOLD * sg.market_context["trailing_median_range"] - 1e-9)
    return {"n_signals": len(signals), "duplicate_days": dup, "lookahead_violations": lookahead,
            "wrong_reward_risk": bad_rr, "zero_risk_signals": zero_risk,
            "wrong_direction": wrong_dir, "below_threshold": below_thresh,
            "pass": dup == 0 and lookahead == 0 and bad_rr == 0 and zero_risk == 0
                    and wrong_dir == 0 and below_thresh == 0}


def main():
    from data_loader import load_price_data
    df, syn = load_price_data(context="strategy_s008 (audit only)", apply_holdout=False)
    if syn:
        raise SystemExit("synthetic -- refusing")
    precompute(df)
    sigs = generate_signals(df, df)
    a = audit(sigs)
    days = len(set(df.index.date))
    print(json.dumps({"strategy": STRATEGY_NAME, "version": STRATEGY_VERSION,
                      "sessions_on_disk": days, "audit": a,
                      "fire_rate": round(a["n_signals"] / days, 3) if days else None},
                     indent=2, default=str))


if __name__ == "__main__":
    main()
