"""
strategy_s010_thin_participation_completion.py -- S010, thin-participation
afternoon completion continuation.

FROZEN with its spec:
research/infrastructure/strategy-specs/S010-thin-participation-completion.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit.

THE MECHANISM (one paragraph; the spec is the authority)
  The forced counterparty is the same one S008 and S009 trade -- benchmark- and
  close-referenced institutional execution, whose quantity is fixed in the
  morning and whose deadline is the cash close -- but the quantity this strategy
  selects on is NOT the day's price move. It is the LIQUIDITY THE RESIDUAL HAS TO
  BE PUSHED THROUGH. Market impact is a function of order size RELATIVE TO
  AVAILABLE VOLUME (the square-root law: impact ~ sigma * sqrt(Q / ADV)), so the
  same unfinished parent order moves price further on a thin day than on a busy
  one. A session whose cumulative 09:30-14:00 volume is below its own trailing
  norm is a session where participation did not show up, the completion residual
  is unchanged (the algo does not get to do less because fewer people traded),
  and the last two hours must absorb it into a thinner book. The direction that
  residual presses is the direction the session has already gone, for S009's
  reason: the side price has moved away from is the side that is behind its
  benchmark with quantity left. So: THIN PARTICIPATION selects the day,
  the day's own move gives the sign, and the trade is continuation into the close.

THE RULES (restated from the spec)
  known-at     14:00 ET. From that session's 09:30-14:00 RTH bars only:
                 VOL = sum(Volume, 09:30..14:00)
                 RNG = High(09:30..14:00) - Low(09:30..14:00)
                 M   = Close(14:00 bar) - Open(09:30 bar)
               plus TRAILING = the median VOL of the previous 20 sessions
               (STRICTLY earlier sessions only).
  condition    VOL <= PARTICIPATION_FRACTION * TRAILING   (a participation
               deficit) AND M != 0
  direction    sign(M) -- continuation, never a fade
  entry        the NEXT bar's OPEN after the 14:00 ET bar
  stop         0.50 * RNG against entry
  target       entry +/- 1.50 * risk (1.5R)
  time exit    15:55 ET, same session; flat before the cash close; no
               cross-session exit_ts
  sizing       1 micro MNQ, always
  costs        src/cost_model.py. MNQ market $2.60 = 1.300 pt (decision basis);
               MNQ limit $2.10 = 1.050 pt (OPTIMISTIC); NQ market $14.90 =
               0.745 pt; NQ limit $9.90 = 0.495 pt (OPTIMISTIC). ASSUMED (s.11).

NOT A RESURRECTION: the selection variable is session VOLUME against its own
trailing median, not a price level, a breakout, a gap or a volume-graded
REVERSAL (hyp-000152, CLOSED, which tested next-DAY reversal graded by daily
volume -- a different horizon, a different direction and a different variable).
S008 selects on |Close(15:00) - Open(09:30)| against a trailing RANGE and enters
at 15:00; S009 selected on the 13:30 VWAP gap. This one selects on VOLUME and
enters at 14:00. The correlation with S008 is real and is disclosed in the spec.

NO LOOK-AHEAD: VOL, RNG and M are measured from bars at or before 14:00 and the
trailing median from strictly earlier sessions; the only bar read after the
decision is the next bar's open, which is the fill price by construction.

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, precompute(history),
generate_signals(df, history=None) -> list[strategy_contract.Signal], the same
shape S008 / S009 / execution_dummy / base_entry_b3 expose to
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

STRATEGY_ID = "S010"
STRATEGY_NAME = "s010_thin_participation_completion"
STRATEGY_VERSION = "S010-1.0 (frozen 2026-09-16)"
VALIDATION_STATUS = "paper-candidate"
SPEC_PATH = "research/infrastructure/strategy-specs/S010-thin-participation-completion.md"

SESSION_OPEN = "09:30"
DECISION_TIME = "14:00"          # the bar at which participation is measured
PARTICIPATION_FRACTION = 1.00    # VOL <= 1.00 x the trailing-20 median VOL
STOP_FRACTION = 0.50             # stop = 0.50 * RNG against entry
TARGET_R_MULTIPLE = 1.50
TRAILING_SESSIONS = 20
MIN_WINDOW_BARS = 250            # completeness guard on 09:30-14:00 (270 minutes)
TIME_EXIT = "15:55"
INSTRUMENT = "MNQ"

# Filled by precompute(): session date -> median VOL of the previous 20 sessions.
_TRAILING_MEDIAN_VOL: dict = {}


def session_window(day_df: pd.DataFrame) -> pd.DataFrame:
    """09:30 through the 14:00 bar inclusive -- everything known at the decision."""
    return day_df.between_time(SESSION_OPEN, DECISION_TIME, inclusive="both")


def session_stats(day_df: pd.DataFrame) -> dict | None:
    """VOL, RNG and M for one session, or None if the session is a fragment."""
    win = session_window(day_df)
    if len(win) < MIN_WINDOW_BARS:
        return None
    if win.index[0].strftime("%H:%M") != SESSION_OPEN or win.index[-1].strftime("%H:%M") != DECISION_TIME:
        return None                                   # no 09:30 open bar or no 14:00 bar
    vol = float(win["Volume"].astype(float).sum())
    if not (vol > 0):
        return None
    rng = float(win["High"].max() - win["Low"].min())
    if not (rng > 0):
        return None
    return {"window": win, "volume": vol, "range": rng,
            "move": float(win["Close"].iloc[-1] - win["Open"].iloc[0])}


def precompute(history: pd.DataFrame) -> None:
    """Build, ONCE over `history`, the trailing-20-session median of VOL for every
    session -- from sessions STRICTLY BEFORE it, so nothing reads its own day or
    any later one."""
    _TRAILING_MEDIAN_VOL.clear()
    dates, vols = [], []
    for day, g in history.groupby(history.index.date):
        st = session_stats(g)
        if st is None:
            continue
        dates.append(day)
        vols.append(st["volume"])
    s = pd.Series(vols, index=pd.Index(dates))
    med = s.rolling(TRAILING_SESSIONS, min_periods=TRAILING_SESSIONS).median().shift(1)
    for d, m in med.items():
        if np.isfinite(m):
            _TRAILING_MEDIAN_VOL[d] = float(m)


def signal_for_day(day_df: pd.DataFrame) -> dict | None:
    """Pure function of ONE session's bars plus the precomputed trailing median."""
    day = day_df.index[0].date()
    trailing = _TRAILING_MEDIAN_VOL.get(day)
    if trailing is None or not (trailing > 0):
        return None                                   # no 20-session history yet
    st = session_stats(day_df)
    if st is None:
        return None
    if st["volume"] > PARTICIPATION_FRACTION * trailing:
        return None                                   # participation was NOT thin
    move = st["move"]
    if move == 0:
        return None                                   # no side to be behind on
    win = st["window"]
    after = day_df[day_df.index > win.index[-1]]
    if after.empty:
        return None
    entry_ts = after.index[0]
    if entry_ts.strftime("%H:%M") >= TIME_EXIT:
        return None                                   # no room before the flat time
    entry = float(after["Open"].iloc[0])
    direction = "long" if move > 0 else "short"
    risk = STOP_FRACTION * st["range"]
    if risk <= 0:
        return None
    if direction == "long":
        stop, target = entry - risk, entry + TARGET_R_MULTIPLE * risk
    else:
        stop, target = entry + risk, entry - TARGET_R_MULTIPLE * risk
    return {"date": day, "direction": direction, "move": move, "session_volume": st["volume"],
            "trailing_median_volume": trailing, "participation_ratio": st["volume"] / trailing,
            "session_range": st["range"], "decision_time": win.index[-1],
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
            "condition": (f"Volume({SESSION_OPEN}-{DECISION_TIME}) <= {PARTICIPATION_FRACTION} x "
                          f"trailing-{TRAILING_SESSIONS} median of the same window, and "
                          f"Close({DECISION_TIME}) != Open({SESSION_OPEN})"),
            "move_points": s["move"], "session_volume": s["session_volume"],
            "trailing_median_volume": s["trailing_median_volume"],
            "participation_ratio": s["participation_ratio"],
            "session_range": s["session_range"],
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
    if not _TRAILING_MEDIAN_VOL:
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
    not_thin = sum(1 for sg in signals
                   if sg.market_context["participation_ratio"] > PARTICIPATION_FRACTION + 1e-12)
    return {"n_signals": len(signals), "duplicate_days": dup, "lookahead_violations": lookahead,
            "wrong_reward_risk": bad_rr, "zero_risk_signals": zero_risk,
            "wrong_direction": wrong_dir, "not_thin": not_thin,
            "pass": dup == 0 and lookahead == 0 and bad_rr == 0 and zero_risk == 0
                    and wrong_dir == 0 and not_thin == 0}


def main():
    from data_loader import load_price_data
    df, syn = load_price_data(context="strategy_s010 (audit only)", apply_holdout=False)
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
