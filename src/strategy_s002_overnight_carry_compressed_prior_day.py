"""
strategy_s002_overnight_carry_compressed_prior_day.py -- S002, the overnight carry
leg on compressed prior days (hyp-000145 / M15 via Salvage, directive s.7).
FROZEN with its spec:
research/infrastructure/strategy-specs/S002-overnight-carry-compressed-prior-day.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit. S002 has
no salvage of its own (one salvage per strategy; the M15 family's was spent on the
menu run that produced this candidate).

THE RULES (restated from the spec s.3; the spec is the authority)
  condition   session D-1's own RTH range is in the frozen hyp-000048 NARROW cell
              (<= the 20th percentile of the trailing 20 RTH ranges). This is the
              same number build_conditioning_frame() calls prior_day_narrow on the
              FOLLOWING session; read here on the ENTRY session so the flag never
              needs a bar that has not printed yet. Fully known at D-1's 15:59.
  entry       long 1 micro at the OPEN of D-1's 16:00 ET bar
  exit        flat at the OPEN of the 09:30 ET bar of the next RTH session D
              (declared to the paper loop as market_context["exit_ts"], the
              cross-session exit built 2026-09-16 -- choice 7 in
              bot_stack_paper_run.py)
  stop        entry - 1.0 x ATR14 (daily RTH true range, 14-session mean, lagged one
              session so it is known at the entry bar). A gap-disaster cap, not a
              management stop. R = 1.0 ATR.
  target      NONE. A carry has no target; the module passes an unreachable
              sentinel (NO_TARGET_PTS above entry) so the shared bookkeeping can
              only ever exit on the stop or the clock. `risk_multiple` is therefore
              meaningless for this strategy and is recorded as such.
  size        1 micro, always. Costs ASSUMED ($6.00 per micro round trip).

NO LOOKAHEAD. Every input is printed before the 16:00 entry bar: the NARROW flag
(D-1's own range and the 20 sessions before it), ATR14 (lagged one session), the
entry price (that bar's open). The exit timestamp is a CLOCK, not a price. When the
next session is not on disk yet, the signal still fires with a placeholder exit
timestamp that the loop's cross-session guard refuses: the session is DEFERRED
whole, nothing is logged, and it is re-scored once the exit session's data exists.
That placeholder can never book a trade -- only defer one.

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, precompute(history),
generate_signals(df, history=None) -> list[strategy_contract.Signal].
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402
from study_intraday_behavior_batch1 import (  # noqa: E402
    build_daily_frame, RANGE_NARROW_PCTL, LOOKBACK_DAYS as RANGE_LOOKBACK_DAYS,
)

STRATEGY_ID = "S002"
STRATEGY_NAME = "s002_overnight_carry_compressed_prior_day"
STRATEGY_VERSION = "S002-1.0 (frozen 2026-09-16)"
INSTRUMENT = "MNQ"
VALIDATION_STATUS = "paper-candidate"
ENTRY_TIME = "16:00"          # the bar whose OPEN is the entry
EXIT_TIME = "09:30"           # the next RTH session's opening bar; its OPEN is the exit
ATR_LOOKBACK = 14
ATR_STOP_MULTIPLE = 1.0
NO_TARGET_PTS = 1_000_000.0   # sentinel: a carry has no target (see the header)
SPEC_PATH = "research/infrastructure/strategy-specs/S002-overnight-carry-compressed-prior-day.md"

_FULL_DF: pd.DataFrame | None = None
_PRE: dict = {}


def _load_full() -> pd.DataFrame:
    global _FULL_DF
    if _FULL_DF is None:
        from data_loader import load_price_data
        df, synthetic = load_price_data(context="strategy_s002", apply_holdout=False)
        if synthetic:
            raise RuntimeError("synthetic data -- S002 refuses to run")
        _FULL_DF = df
    return _FULL_DF


def _rth(g: pd.DataFrame) -> pd.DataFrame:
    return g.between_time("09:30", "16:00", inclusive="left")


def precompute(history: pd.DataFrame) -> None:
    """Build, ONCE over `history`: the frozen NARROW flag per session, the lagged
    ATR14 per session, and the list of RTH session dates (a date with a 09:30
    bar). Nothing here reads a bar later than the session it describes."""
    daily = build_daily_frame(history)
    narrow_thresh = daily["range"].rolling(
        RANGE_LOOKBACK_DAYS, min_periods=RANGE_LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, RANGE_NARROW_PCTL), raw=True).shift(1)
    narrow = (daily["range"] <= narrow_thresh).fillna(False).astype(bool)

    prev_close = daily["Close"].shift(1)
    tr = pd.concat([daily["High"] - daily["Low"],
                    (daily["High"] - prev_close).abs(),
                    (daily["Low"] - prev_close).abs()], axis=1).max(axis=1)
    atr14 = tr.rolling(ATR_LOOKBACK, min_periods=ATR_LOOKBACK).mean().shift(1)

    days = {d: g for d, g in history.groupby(history.index.date)}
    rth_dates = []
    for d in sorted(days):
        r = _rth(days[d])
        if not r.empty and r.index[0].hour == 9 and r.index[0].minute == 30:
            rth_dates.append(d)
    _PRE.clear()
    _PRE.update({"narrow": narrow, "atr14": atr14, "days": days,
                 "rth_dates": rth_dates, "src": id(history)})


def _ensure_pre(history: pd.DataFrame | None) -> None:
    if history is not None and _PRE.get("src") == id(history):
        return
    if history is None and _PRE.get("src") == "full":
        return
    src = history if history is not None else _load_full()
    precompute(src)
    if history is None:
        _PRE["src"] = "full"


def narrow_entry_session(day, history: pd.DataFrame | None = None) -> bool:
    """The frozen hyp-000048 NARROW cell, read on the ENTRY session (identical by
    construction to prior_day_narrow on the session that follows it)."""
    _ensure_pre(history)
    n = _PRE["narrow"]
    return bool(n.loc[day]) if day in n.index else False


def _next_rth_date(day):
    later = [d for d in _PRE["rth_dates"] if d > day]
    return later[0] if later else None


def signals_for_day(day, day_df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    _ensure_pre(history)
    if not narrow_entry_session(day, history):
        return []
    rth = _rth(day_df)
    if rth.empty or rth.index[-1].strftime("%H:%M") < "15:55":
        return []                       # holiday half-day / fragment: no entry (spec s.3)
    entry_bars = day_df.between_time(ENTRY_TIME, ENTRY_TIME)
    if entry_bars.empty:
        return []                       # no 16:00 bar: no entry
    entry_ts = entry_bars.index[0]
    entry = float(entry_bars["Open"].iloc[0])
    atr = _PRE["atr14"].get(day, float("nan"))
    if not np.isfinite(atr) or atr <= 0:
        return []                       # no ATR yet: no stop, no trade
    stop = round(entry - ATR_STOP_MULTIPLE * float(atr), 4)
    target = entry + NO_TARGET_PTS

    nxt = _next_rth_date(day)
    known_next = nxt is not None
    exit_date = nxt if known_next else (pd.Timestamp(day) + pd.Timedelta(days=1)).date()
    exit_ts = (pd.Timestamp(f"{exit_date} {EXIT_TIME}:00")
               .tz_localize(entry_ts.tz) if entry_ts.tz is not None
               else pd.Timestamp(f"{exit_date} {EXIT_TIME}:00"))
    if known_next:
        nd = _PRE["days"][nxt]
        if nd.between_time(EXIT_TIME, EXIT_TIME).empty:
            return []                   # session D has no 09:30 bar (spec s.3 exclusion)

    return [Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=entry_ts, instrument=INSTRUMENT, timeframe="1m",
        direction="long", entry=entry, stop=stop, target=target,
        risk_multiple=risk_multiple(entry, stop, target),
        validation_status=VALIDATION_STATUS,
        market_context={
            "strategy_id": STRATEGY_ID, "date": str(day), "entry_time": ENTRY_TIME,
            "exit_ts": str(exit_ts), "exit_session_known": known_next,
            "atr14": round(float(atr), 4), "stop_basis": "entry - 1.0 x ATR14 (lagged), gap cap",
            "target_basis": "none (carry) -- unreachable sentinel; risk_multiple is meaningless here",
            "condition": "entry session in the frozen hyp-000048 NARROW cell (= prior_day_narrow of the next session)",
            "weekend_leg": bool(known_next and (pd.Timestamp(nxt) - pd.Timestamp(day)).days > 1),
            "spec": SPEC_PATH},
    )]


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    out = []
    for day, g in df.groupby(df.index.date):
        out.extend(signals_for_day(day, g, history))
    return out


def audit(signals: list[Signal]) -> dict:
    """Mechanical self-checks: one signal a session, every entry at 16:00, every
    exit timestamp strictly after its entry, every stop below its entry."""
    per_day: dict[str, int] = {}
    for s in signals:
        per_day[s.market_context["date"]] = per_day.get(s.market_context["date"], 0) + 1
    over = sum(1 for n in per_day.values() if n > 1)
    bad_entry = sum(1 for s in signals if pd.Timestamp(s.timestamp).strftime("%H:%M") != ENTRY_TIME)
    bad_exit = sum(1 for s in signals
                   if pd.Timestamp(s.market_context["exit_ts"]) <= pd.Timestamp(s.timestamp))
    bad_stop = sum(1 for s in signals if not s.stop < s.entry)
    return {"signals": len(signals), "sessions": len(per_day), "multi_signal_sessions": over,
            "entries_off_clock": bad_entry, "exits_not_after_entry": bad_exit,
            "stops_not_below_entry": bad_stop,
            "pass": bool(over == 0 and bad_entry == 0 and bad_exit == 0 and bad_stop == 0)}
