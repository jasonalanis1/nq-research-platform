"""
strategy_s011_daily_reversal_vs_own_drift.py -- S011, NQ daily reversal faded at
the open, measured against NQ's own next-session drift.

FROZEN with its spec:
research/infrastructure/strategy-specs/S011-daily-reversal-vs-own-drift.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit.

LINEAGE: hyp-000152 / M18, closed 2026-09-13 P1_PASS_P2_FAIL. The GATING cell
passed (next-session sign-adjusted return credibly negative after a high-volume
session, ci_90 -0.1523..-0.0463) and only the VOLUME GRADIENT failed (HIGH minus
LOW ci_90 -0.1253..+0.0054, not credible). What is traded here is cell 5, the
UNCONDITIONAL reversal (mean -0.0425 x ATR14), NOT the HIGH-volume cell.

THERE IS NO VOLUME FILTER, ON PURPOSE (spec s.2). The closure form's own
`not_retest` line is "Volume as a gradient on daily reversal", and NEXT_UP's
sourcing line for S011 forbids reintroducing a volume tercile. Selecting the
HIGH cell because it is the bigger number would be selecting on a difference the
data refused to support. `vol_ratio` IS recorded in every signal's
market_context, for the record only -- it is never read by any decision in this
file and no screen output splits on it.

THE MECHANISM (one paragraph; the spec is the authority)
  The forced counterparty is the liquidity provider (dealer, market maker,
  short-horizon arbitrageur) who ends a session holding inventory he did not
  choose, taken on at a price concession from non-informational flow he had to
  absorb. His constraint is capital and overnight risk, not opinion, and his
  deadline is the next session, when the inventory is worked off -- buying back
  what he sold into a falling tape, selling what he bought into a rising one.
  That is pressure AGAINST the prior session's direction, spread through the
  next session rather than concentrated at its open (Scan 026's first-minute
  share of the response was 0.036 against a 0.5 kill threshold). WHERE THIS IS
  WEAK, and the spec says so at length: the mechanism's own size prediction
  FAILED -- if this were inventory concession its magnitude should scale with
  flow size, and volume, the best available proxy for flow size, does not grade
  it. What survives is a real, measured, session-long reversal with a plausible
  but UNCONFIRMED story attached; it may be index-level negative lag-1
  autocorrelation with no identifiable forced seller behind it. That is why the
  own-drift baseline is a GATE here and not a diagnostic.

THE RULES (restated from the spec)
  signal session P  any completed RTH session (09:30 bar and a last RTH bar).
  M(P)              Close(last RTH bar of P) - Open(09:30 bar of P). Skip M == 0.
  known at          P's RTH close; atr14 is the 14-session mean RTH range, LAGGED.
  direction         FADE: short if M(P) > 0, long if M(P) < 0.
  entry             the OPEN of the 09:30 ET bar of the next RTH session T.
  stop              entry -/+ 2.0 x atr14 -- a DISASTER CAP, not a management stop.
  target            none; unreachable sentinel. risk_multiple is meaningless here.
  time exit         15:55 ET of session T, same session. No cross-session hold,
                    no exit_ts -- the paper loop's ordinary same-session path.
  sizing            1 micro MNQ, always.
  costs             src/cost_model.py. MNQ market $2.60 = 1.300 pt (decision
                    basis); MNQ limit $2.10 = 1.050 pt (OPTIMISTIC); NQ market
                    $14.90 = 0.745 pt; NQ limit $9.90 = 0.495 pt (OPTIMISTIC).
                    ASSUMED (s.11).

THE OWN-DRIFT BASELINE ARM (spec s.6, the two-nulls rule that killed H118 and
rebuilt S004): BASELINE_ALWAYS_LONG forces the direction LONG on the identical
set of sessions with every other rule unchanged -- NQ's own next-session drift
over the identical window. It is set ONLY by
src/screen_s011_own_drift_baseline.py and is False in every production path.
Arm B is NOT a strategy: never registered, never papered, never judged.

NOT A RESURRECTION: hyp-000152 closed the VOLUME GRADIENT and this file does not
measure it. Building a closed raw effect as a whole trade for the first time is
the S003 precedent (hyp-000157, CLOSED P1_FAIL, built as S003).

NO LOOK-AHEAD: M(P) and atr14 come from bars at or before P's close; the only
bar of session T read before the fill is its 09:30 bar's OPEN, which IS the fill
price by construction.

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, precompute(history),
generate_signals(df, history=None) -> list[strategy_contract.Signal], the same
shape S004 / S008 / S010 expose to bot_stack_paper_run.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402
from market_state_primitives import build_state_frame  # noqa: E402
import cost_model  # noqa: E402

STRATEGY_ID = "S011"
STRATEGY_NAME = "s011_daily_reversal_vs_own_drift"
STRATEGY_VERSION = "S011-1.0 (frozen 2026-09-18)"
INSTRUMENT = "MNQ"
VALIDATION_STATUS = "paper-candidate"
SPEC_PATH = "research/infrastructure/strategy-specs/S011-daily-reversal-vs-own-drift.md"

RTH_OPEN = "09:30"
RTH_CLOSE = "16:00"           # exclusive right edge: the last RTH bar is 15:59
ENTRY_TIME = "09:30"
TIME_EXIT = "15:55"
ATR_STOP_MULTIPLE = 2.0       # disaster cap
NO_TARGET_PTS = 1_000_000.0   # sentinel: a reversal-to-the-close trade has no target
VOL_TRAILING_SESSIONS = 20    # RECORD ONLY -- never a decision input (spec s.2)

_FULL_DF: pd.DataFrame | None = None
_PRE: dict = {}

# The own-drift baseline arm (spec s.6). Set ONLY by
# src/screen_s011_own_drift_baseline.py; False in every production path.
BASELINE_ALWAYS_LONG = False


def _load_full() -> pd.DataFrame:
    global _FULL_DF
    if _FULL_DF is None:
        from data_loader import load_price_data
        df, synthetic = load_price_data(context="strategy_s011", apply_holdout=False)
        if synthetic:
            raise RuntimeError("synthetic data -- S011 refuses to run")
        _FULL_DF = df
    return _FULL_DF


def _rth(g: pd.DataFrame) -> pd.DataFrame:
    return g.between_time(RTH_OPEN, RTH_CLOSE, inclusive="left")


def precompute(history: pd.DataFrame) -> None:
    """Build ONCE over `history`: the ordered RTH session list, each session's own
    RTH move M and RTH volume, the lagged trailing-20 mean volume (record only),
    and the lagged atr14. Nothing here reads a bar later than the session it
    describes."""
    states = build_state_frame(history)               # v1, price-only: atr14 is lagged
    atr14 = states["atr14"]

    rth_dates, moves, vols = [], {}, {}
    for d, g in history.groupby(history.index.date):
        r = _rth(g)
        if r.empty:
            continue
        if not (r.index[0].hour == 9 and r.index[0].minute == 30):
            continue                                  # no 09:30 open bar -> not a session
        rth_dates.append(d)
        moves[d] = float(r["Close"].iloc[-1] - r["Open"].iloc[0])
        vols[d] = float(r["Volume"].astype(float).sum())

    rth_dates.sort()
    s = pd.Series([vols[d] for d in rth_dates], index=pd.Index(rth_dates))
    trail = s.rolling(VOL_TRAILING_SESSIONS, min_periods=VOL_TRAILING_SESSIONS).mean().shift(1)

    _PRE.clear()
    _PRE.update({"atr14": atr14, "moves": moves, "vols": vols,
                 "vol_trailing": {d: float(v) for d, v in trail.items() if np.isfinite(v)},
                 "rth_dates": rth_dates,
                 "rth_index": {d: i for i, d in enumerate(rth_dates)},
                 "src": id(history)})


def _ensure_pre(history: pd.DataFrame | None) -> None:
    if history is not None and _PRE.get("src") == id(history):
        return
    if history is None and _PRE.get("src") == "full":
        return
    src = history if history is not None else _load_full()
    precompute(src)
    if history is None:
        _PRE["src"] = "full"


def prior_session(day, history: pd.DataFrame | None = None):
    """The RTH session immediately before `day`, or None."""
    _ensure_pre(history)
    i = _PRE["rth_index"].get(day)
    if i is None or i < 1:
        return None
    return _PRE["rth_dates"][i - 1]


def signals_for_day(day, day_df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    _ensure_pre(history)
    if day not in _PRE["rth_index"]:
        return []

    prior = prior_session(day, history)
    if prior is None:
        return []
    move = _PRE["moves"].get(prior)
    if move is None or not np.isfinite(move) or move == 0.0:
        return []                                     # no side to fade

    entry_bars = day_df.between_time(ENTRY_TIME, ENTRY_TIME)
    if entry_bars.empty:
        return []
    entry_ts = entry_bars.index[0]
    entry = float(entry_bars["Open"].iloc[0])

    atr = _PRE["atr14"].get(day, float("nan"))
    if not np.isfinite(atr) or atr <= 0:
        return []
    risk = ATR_STOP_MULTIPLE * float(atr)

    # THE ONE DECISION IN THIS FILE: fade the prior session's sign -- unless the
    # own-drift baseline arm is on, which forces LONG and changes nothing else.
    direction = "long" if BASELINE_ALWAYS_LONG else ("short" if move > 0 else "long")
    if direction == "long":
        stop, target = round(entry - risk, 4), entry + NO_TARGET_PTS
    else:
        stop, target = round(entry + risk, 4), entry - NO_TARGET_PTS

    trailing_vol = _PRE["vol_trailing"].get(prior)
    prior_vol = _PRE["vols"].get(prior)
    vol_ratio = (prior_vol / trailing_vol) if (trailing_vol and trailing_vol > 0) else None

    cond = ("FADE sign(M(prior RTH session)) -- unconditional, EVERY session (hyp-000152 cell 5)"
            if not BASELINE_ALWAYS_LONG else
            "OWN-DRIFT BASELINE ARM: direction forced LONG on the identical sessions (spec s.6) -- NOT a strategy")

    return [Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=entry_ts, instrument=INSTRUMENT, timeframe="1m",
        direction=direction, entry=entry, stop=stop, target=target,
        risk_multiple=risk_multiple(entry, stop, target),
        validation_status=VALIDATION_STATUS,
        market_context={
            "strategy_id": STRATEGY_ID, "date": str(day), "entry_time": ENTRY_TIME,
            "signal_session": str(prior), "prior_session_move_points": round(float(move), 4),
            "prior_session_direction": "up" if move > 0 else "down",
            "atr14": round(float(atr), 4), "risk_points": round(risk, 4),
            "stop_basis": f"entry -/+ {ATR_STOP_MULTIPLE} x atr14 (lagged) = disaster cap, not a management stop",
            "target_basis": "none (reversal-to-the-close trade) -- unreachable sentinel; risk_multiple is meaningless here",
            "time_exit": TIME_EXIT,
            "vol_ratio_RECORD_ONLY": (round(float(vol_ratio), 6) if vol_ratio is not None else None),
            "vol_ratio_note": ("RECORD ONLY -- never a decision input. hyp-000152 closed the volume "
                               "gradient (not_retest) and this strategy does not reintroduce a volume tercile."),
            "baseline_arm": bool(BASELINE_ALWAYS_LONG),
            "baseline_rule": ("SCREEN passes only if net > 0 AND net points/trade beats the identical trade "
                              "taken LONG on the same sessions (NQ's own next-session drift) -- spec s.6"),
            "condition": cond,
            "cost_basis": cost_model.DEFAULT_NOTE,
            "spec": SPEC_PATH},
    )]


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    out = []
    for day, g in df.groupby(df.index.date):
        out.extend(signals_for_day(day, g, history))
    return out


def audit(signals: list[Signal]) -> dict:
    """Mechanical self-checks: one signal a session, every entry at 09:30, the
    signal session strictly before the entry session, stops on the correct side,
    and -- when the strategy arm is on -- every direction genuinely the FADE of
    its signal session's move."""
    per_day: dict[str, int] = {}
    for s in signals:
        d = s.market_context["date"]
        per_day[d] = per_day.get(d, 0) + 1
    over = sum(1 for n in per_day.values() if n > 1)
    bad_entry = sum(1 for s in signals if pd.Timestamp(s.timestamp).strftime("%H:%M") != ENTRY_TIME)
    bad_order = sum(1 for s in signals
                    if pd.Timestamp(s.market_context["signal_session"]).date()
                    >= pd.Timestamp(s.market_context["date"]).date())
    bad_stop = sum(1 for s in signals
                   if (s.direction == "long" and not s.stop < s.entry)
                   or (s.direction == "short" and not s.stop > s.entry))
    not_faded = 0 if BASELINE_ALWAYS_LONG else sum(
        1 for s in signals
        if (s.market_context["prior_session_move_points"] > 0) != (s.direction == "short"))
    all_long = sum(1 for s in signals if s.direction == "long")
    return {"signals": len(signals), "sessions": len(per_day),
            "multi_signal_sessions": over, "entries_off_clock": bad_entry,
            "signal_session_not_before_entry": bad_order,
            "stops_on_wrong_side": bad_stop, "directions_not_faded": not_faded,
            "long_signals": all_long, "baseline_arm": bool(BASELINE_ALWAYS_LONG),
            "pass": bool(over == 0 and bad_entry == 0 and bad_order == 0
                         and bad_stop == 0 and not_faded == 0)}
