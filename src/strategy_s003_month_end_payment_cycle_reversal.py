"""
strategy_s003_month_end_payment_cycle_reversal.py -- S003, the month-end
payment-cycle reversal (M24 / hyp-000157) built as a FULL strategy for the first
time (standing directive s.9, the revamp list; the directive names it).
FROZEN with its spec:
research/infrastructure/strategy-specs/S003-month-end-payment-cycle-reversal.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit.

THE RULES (restated from the spec s.3; the spec is the authority)
  universe    the final RTH session of each calendar month
  condition   that session's LAST-WEEK RETURN (entry price / Close of the 5th-
              prior RTH session - 1) is <= the 33.3rd percentile of the previous
              24 month-end observations of the same quantity (>= 12 required)
  entry       long 1 micro at the OPEN of the 15:59 ET bar of month t's final
              RTH session
  exit        flat at the OPEN of the 15:59 ET bar of month t+1's final RTH
              session, declared as market_context["exit_ts"] (choice 7's
              cross-session walk in bot_stack_paper_run.py)
  stop        entry - 4.0 x ATR20 (daily RTH true range, 20-session mean, lagged
              one session). A disaster cap, not a management stop. R = 4.0 ATR20.
  target      NONE. Unreachable sentinel; risk_multiple is meaningless here.
  size        1 micro, always. Costs ASSUMED ($6.00 per micro round trip).

WHY A TRAILING PERCENTILE AND NOT SCAN 031's FROZEN TERCILE: a trader standing
at a month end cannot know a boundary computed over 2015-2021. 24 months is the
shortest window that sees each calendar month twice; 33.3% is Scan 031's own
split, carried over unchanged. Neither number is tuned.

NO LOOKAHEAD. Every input is printed before the 15:59 entry bar opens: the
trailing threshold (prior month-ends only, never this one), the 5th-prior
session's daily Close, ATR20 (lagged one session), the entry price (that bar's
open). Historical month-end observations use the daily Close of their session;
the CURRENT month-end uses the entry price (the 15:59 OPEN) because its own
close has not printed at entry time -- a one-minute difference, disclosed here
and in the spec, and it is the lookahead-free choice of the two. "Final RTH
session of the month" is a CALENDAR fact; where the data on disk cannot yet
confirm it, the module declines rather than guesses.

When the exit month's final session is not on disk yet the signal still fires
with a placeholder exit timestamp that the loop's cross-session guard refuses:
the entry session is DEFERRED whole, nothing is logged, and it is re-scored once
the exit session's data exists. The placeholder can never book a trade.

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, precompute(history),
generate_signals(df, history=None) -> list[strategy_contract.Signal].
"""
from __future__ import annotations

import calendar as _calendar
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402
from study_intraday_behavior_batch1 import build_daily_frame  # noqa: E402

STRATEGY_ID = "S003"
STRATEGY_NAME = "s003_month_end_payment_cycle_reversal"
STRATEGY_VERSION = "S003-1.0 (frozen 2026-09-16)"
INSTRUMENT = "MNQ"
VALIDATION_STATUS = "paper-candidate"
ENTRY_TIME = "15:59"          # the bar whose OPEN is the entry (last RTH minute)
EXIT_TIME = "15:59"           # the same bar of the NEXT month's final RTH session
LAST_WEEK_SESSIONS = 5        # the forced-selling window (M24 s.4)
PCTL = 33.3333                # Scan 031's tercile split, unchanged
PCTL_LOOKBACK = 24            # month-end observations
PCTL_MIN_OBS = 12
ATR_LOOKBACK = 20
ATR_STOP_MULTIPLE = 4.0       # ~ sqrt(21) daily ATRs, just inside one month's walk
NO_TARGET_PTS = 1_000_000.0   # sentinel: a decay trade has no target
SESSION_COMPLETE_BY = "15:55"
SPEC_PATH = "research/infrastructure/strategy-specs/S003-month-end-payment-cycle-reversal.md"

_FULL_DF: pd.DataFrame | None = None
_PRE: dict = {}


def _load_full() -> pd.DataFrame:
    global _FULL_DF
    if _FULL_DF is None:
        from data_loader import load_price_data
        df, synthetic = load_price_data(context="strategy_s003", apply_holdout=False)
        if synthetic:
            raise RuntimeError("synthetic data -- S003 refuses to run")
        _FULL_DF = df
    return _FULL_DF


def _rth(g: pd.DataFrame) -> pd.DataFrame:
    return g.between_time("09:30", "16:00", inclusive="left")


def precompute(history: pd.DataFrame) -> None:
    """Build ONCE over `history`: the RTH session list, the daily frame, lagged
    ATR20, and the per-month final RTH session. Nothing here reads a bar later
    than the session it describes."""
    daily = build_daily_frame(history)
    prev_close = daily["Close"].shift(1)
    tr = pd.concat([daily["High"] - daily["Low"],
                    (daily["High"] - prev_close).abs(),
                    (daily["Low"] - prev_close).abs()], axis=1).max(axis=1)
    atr20 = tr.rolling(ATR_LOOKBACK, min_periods=ATR_LOOKBACK).mean().shift(1)

    days = {d: g for d, g in history.groupby(history.index.date)}
    rth_dates = []
    for d in sorted(days):
        r = _rth(days[d])
        if not r.empty and r.index[0].hour == 9 and r.index[0].minute == 30:
            rth_dates.append(d)

    # final RTH session ON DISK per (year, month), and the closes by session
    month_last: dict[tuple[int, int], object] = {}
    for d in rth_dates:
        month_last[(d.year, d.month)] = d

    _PRE.clear()
    _PRE.update({"daily": daily, "atr20": atr20, "days": days, "rth_dates": rth_dates,
                 "rth_index": {d: i for i, d in enumerate(rth_dates)},
                 "month_last": month_last, "src": id(history)})


def _ensure_pre(history: pd.DataFrame | None) -> None:
    if history is not None and _PRE.get("src") == id(history):
        return
    if history is None and _PRE.get("src") == "full":
        return
    src = history if history is not None else _load_full()
    precompute(src)
    if history is None:
        _PRE["src"] = "full"


def _weekday_remains_in_month(day) -> bool:
    """Is there any later WEEKDAY in `day`'s calendar month? Used only when the
    data ends on `day`, where 'final session of the month' cannot be confirmed
    from disk. Conservative: a remaining weekday means we decline the trade."""
    last_dom = _calendar.monthrange(day.year, day.month)[1]
    for dom in range(day.day + 1, last_dom + 1):
        if pd.Timestamp(year=day.year, month=day.month, day=dom).weekday() < 5:
            return True
    return False


def is_month_final_session(day, history: pd.DataFrame | None = None) -> bool:
    """CALENDAR fact, decided without any price information from `day` onward."""
    _ensure_pre(history)
    rth = _PRE["rth_dates"]
    if day not in _PRE["rth_index"]:
        return False
    later_same_month = any(d > day and d.month == day.month and d.year == day.year for d in rth)
    if later_same_month:
        return False
    if rth[-1] > day:
        return True                      # the data itself confirms no later session this month
    return not _weekday_remains_in_month(day)


def last_week_return(day, entry_price: float, history: pd.DataFrame | None = None) -> float | None:
    """Return over the final LAST_WEEK_SESSIONS RTH sessions of the month, measured
    to the entry instant. None when the 5th-prior session does not exist."""
    _ensure_pre(history)
    i = _PRE["rth_index"].get(day)
    if i is None or i < LAST_WEEK_SESSIONS:
        return None
    base_day = _PRE["rth_dates"][i - LAST_WEEK_SESSIONS]
    daily = _PRE["daily"]
    if base_day not in daily.index:
        return None
    base = float(daily["Close"].loc[base_day])
    if not np.isfinite(base) or base <= 0:
        return None
    return entry_price / base - 1.0


def _prior_month_end_returns(day, history: pd.DataFrame | None = None) -> list[float]:
    """The same quantity for every month-end BEFORE `day`, measured close-to-close
    (their own closes have long since printed). Most recent PCTL_LOOKBACK of them."""
    _ensure_pre(history)
    daily = _PRE["daily"]
    idx = _PRE["rth_index"]
    out = []
    for (y, m), d in sorted(_PRE["month_last"].items()):
        if d >= day:
            continue
        i = idx.get(d)
        if i is None or i < LAST_WEEK_SESSIONS:
            continue
        base_day = _PRE["rth_dates"][i - LAST_WEEK_SESSIONS]
        if base_day not in daily.index or d not in daily.index:
            continue
        base = float(daily["Close"].loc[base_day])
        end = float(daily["Close"].loc[d])
        if np.isfinite(base) and base > 0 and np.isfinite(end):
            out.append(end / base - 1.0)
    return out[-PCTL_LOOKBACK:]


def _next_month_final_session(day):
    """The final RTH session ON DISK of the calendar month after `day`'s, or None
    when the data does not yet reach past that month."""
    y, m = (day.year + (day.month == 12)), (1 if day.month == 12 else day.month + 1)
    d = _PRE["month_last"].get((y, m))
    if d is None:
        return None
    if _PRE["rth_dates"][-1] <= d:
        return None                      # that month may not be finished on disk yet
    return d


def signals_for_day(day, day_df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    _ensure_pre(history)
    if not is_month_final_session(day, history):
        return []
    rth = _rth(day_df)
    if rth.empty or rth.index[-1].strftime("%H:%M") < SESSION_COMPLETE_BY:
        return []                        # fragment / holiday half-day: no entry (spec s.3)
    entry_bars = day_df.between_time(ENTRY_TIME, ENTRY_TIME)
    if entry_bars.empty:
        return []
    entry_ts = entry_bars.index[0]
    entry = float(entry_bars["Open"].iloc[0])

    lwr = last_week_return(day, entry, history)
    if lwr is None:
        return []
    prior = _prior_month_end_returns(day, history)
    if len(prior) < PCTL_MIN_OBS:
        return []                        # not enough history for a knowable threshold
    thresh = float(np.percentile(prior, PCTL))
    if lwr > thresh:
        return []                        # not a heavily-sold month end

    atr = _PRE["atr20"].get(day, float("nan"))
    if not np.isfinite(atr) or atr <= 0:
        return []
    stop = round(entry - ATR_STOP_MULTIPLE * float(atr), 4)
    target = entry + NO_TARGET_PTS

    nxt = _next_month_final_session(day)
    known_next = nxt is not None
    if known_next:
        nd = _PRE["days"][nxt]
        if nd.between_time(EXIT_TIME, EXIT_TIME).empty:
            return []                    # exit session has no 15:59 bar (spec s.3 exclusion)
        exit_date = nxt
    else:
        y, m = (day.year + (day.month == 12)), (1 if day.month == 12 else day.month + 1)
        exit_date = pd.Timestamp(year=y, month=m, day=_calendar.monthrange(y, m)[1]).date()
    exit_ts = (pd.Timestamp(f"{exit_date} {EXIT_TIME}:00").tz_localize(entry_ts.tz)
               if entry_ts.tz is not None else pd.Timestamp(f"{exit_date} {EXIT_TIME}:00"))

    return [Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=entry_ts, instrument=INSTRUMENT, timeframe="1m",
        direction="long", entry=entry, stop=stop, target=target,
        risk_multiple=risk_multiple(entry, stop, target),
        validation_status=VALIDATION_STATUS,
        market_context={
            "strategy_id": STRATEGY_ID, "date": str(day), "entry_time": ENTRY_TIME,
            "exit_ts": str(exit_ts), "exit_session_known": known_next,
            "last_week_return": round(float(lwr), 6),
            "threshold_pctl_33_trailing_24_month_ends": round(thresh, 6),
            "prior_month_end_obs": len(prior),
            "atr20": round(float(atr), 4),
            "stop_basis": "entry - 4.0 x ATR20 (lagged), ~sqrt(21) daily ATRs = disaster cap, not a management stop",
            "target_basis": "none (decay trade) -- unreachable sentinel; risk_multiple is meaningless here",
            "condition": "final RTH session of the month; last-week return <= trailing 24-month-end 33.3rd pctl",
            "spec": SPEC_PATH},
    )]


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    out = []
    for day, g in df.groupby(df.index.date):
        out.extend(signals_for_day(day, g, history))
    return out


def audit(signals: list[Signal]) -> dict:
    """Mechanical self-checks: one signal a session, at most one a calendar month,
    every entry at 15:59, every exit strictly after its entry, stops below entry."""
    per_day: dict[str, int] = {}
    per_month: dict[str, int] = {}
    for s in signals:
        d = s.market_context["date"]
        per_day[d] = per_day.get(d, 0) + 1
        per_month[d[:7]] = per_month.get(d[:7], 0) + 1
    over = sum(1 for n in per_day.values() if n > 1)
    over_month = sum(1 for n in per_month.values() if n > 1)
    bad_entry = sum(1 for s in signals if pd.Timestamp(s.timestamp).strftime("%H:%M") != ENTRY_TIME)
    bad_exit = sum(1 for s in signals
                   if pd.Timestamp(s.market_context["exit_ts"]) <= pd.Timestamp(s.timestamp))
    bad_stop = sum(1 for s in signals if not s.stop < s.entry)
    return {"signals": len(signals), "sessions": len(per_day), "months": len(per_month),
            "multi_signal_sessions": over, "multi_signal_months": over_month,
            "entries_off_clock": bad_entry, "exits_not_after_entry": bad_exit,
            "stops_not_below_entry": bad_stop,
            "pass": bool(over == 0 and over_month == 0 and bad_entry == 0
                         and bad_exit == 0 and bad_stop == 0)}
