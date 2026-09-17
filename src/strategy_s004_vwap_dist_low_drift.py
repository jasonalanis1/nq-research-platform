"""
strategy_s004_vwap_dist_low_drift.py -- S004, the H118 VWAP-distance drift
lineage built as a STRATEGY and measured against NQ's OWN unconditional drift.
FROZEN with its spec:
research/infrastructure/strategy-specs/S004-vwap-dist-low-drift-vs-own-drift.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit.

WHY THIS IS A NEW CANDIDATE AND NOT H118
  H118 passed Discovery, Validation and Holdout and was REJECTED on 2026-09-12
  because its LOW-tercile 10-day drift is not distinguishable from NQ's own
  10-day drift (LOW minus ALL = +0.1162 R on Discovery, block-10 bootstrap CI
  -0.2630..+0.4895; +0.0481 on Validation, CI -0.5851..+0.6255 --
  research/studies/h118-baseline-diagnostic-2026-09-12.md). It made money
  because the index went up. H118's own spec, module and forward log are NOT
  touched by this file.
  S004 asks the question H118 never asked: does the SIGNAL beat simply being
  long NQ for the same ten sessions? The own-drift baseline is a GATE (spec
  s.5), run by src/screen_s004_own_drift_baseline.py, not a diagnostic.

THE RULES (restated from the spec s.2; the spec is the authority)
  descriptor  vwap_dist_vs_atr(P) = (RTH close of session P - that session's own
              RTH VWAP at its last bar) / atr14(P), atr14 = 14-session mean daily
              RTH range LAGGED one session. H118's descriptor, unchanged.
  condition   vwap_dist_vs_atr(P) in the LOW tercile on bucket edges FROZEN from
              Discovery and never refit (H118's published Discovery edges,
              data/study_vwap_dist_low_10d_drift_h118_results.json), hardcoded
              below as LOW_EDGE so no slice is ever re-fitted at paper time.
  entry       LONG 1 micro at the OPEN of the 09:30 ET bar of session P+1. NOT
              P's close: the descriptor is only known once P's last bar prints.
  exit        the OPEN of the 09:30 ET bar of session P+11 -- exactly 10 RTH
              sessions held -- as an absolute market_context["exit_ts"], walked
              by choice 7's cross-session bookkeeping in bot_stack_paper_run.py.
  stop        entry - 4.0 x atr14. A DISASTER CAP, not a management stop (H118
              had no stop at all; a strategy must have one). R = 4.0 x atr14.
  target      NONE. Unreachable sentinel; risk_multiple is meaningless here,
              exactly as for S003.
  size        1 micro, always. Costs from src/cost_model.py (ASSUMED).

NO REFERENCE DATA. Every input is price: RTH bars, session VWAP, ATR. S004 reads
no VXN and no macro calendar, so no series in research/ledger/data_coverage.json
can block its SCREEN. The validated VXN->next-session-range sizing fact was
deliberately NOT used for the stop for exactly that reason (spec s.2).

NO LOOKAHEAD. The descriptor reads only session P's bars; atr14 is lagged one
session; the entry price is the open of the first bar of P+1; the exit is a
session fact declared at entry. When P+11 is not yet on disk the signal carries a
PLACEHOLDER exit timestamp that the loop's cross-session guard refuses: the entry
session is DEFERRED whole, nothing is logged, and it is re-scored once the exit
session exists. The placeholder can never book a trade.

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
from market_state_primitives import build_state_frame  # noqa: E402
from market_state_primitives_v2 import _rth_volume_and_close_vwap_dist_by_day  # noqa: E402

STRATEGY_ID = "S004"
STRATEGY_NAME = "s004_vwap_dist_low_drift_vs_own_drift"
STRATEGY_VERSION = "S004-1.0 (frozen 2026-09-17)"
INSTRUMENT = "MNQ"
VALIDATION_STATUS = "paper-candidate"

# H118's DISCOVERY tercile edges, published in
# data/study_vwap_dist_low_10d_drift_h118_results.json and never refit. The LOW
# bucket is everything at or below the lower edge.
LOW_EDGE = -0.04604781358468863
MID_EDGE = 0.14705460626358577

ENTRY_TIME = "09:30"          # the bar whose OPEN is the entry, session P+1
EXIT_TIME = "09:30"           # the same bar of session P+11
HOLD_SESSIONS = 10            # RTH sessions held, entry session inclusive of neither endpoint's close
ATR_STOP_MULTIPLE = 4.0       # disaster cap
NO_TARGET_PTS = 1_000_000.0   # sentinel: a drift trade has no target
SESSION_COMPLETE_BY = "15:55"
SPEC_PATH = "research/infrastructure/strategy-specs/S004-vwap-dist-low-drift-vs-own-drift.md"

_FULL_DF: pd.DataFrame | None = None
_PRE: dict = {}

# The all-sessions baseline (spec s.5) removes ONLY the tercile filter. It is set
# by src/screen_s004_own_drift_baseline.py and is False in every production path.
UNCONDITIONAL_BASELINE = False


def _load_full() -> pd.DataFrame:
    global _FULL_DF
    if _FULL_DF is None:
        from data_loader import load_price_data
        df, synthetic = load_price_data(context="strategy_s004", apply_holdout=False)
        if synthetic:
            raise RuntimeError("synthetic data -- S004 refuses to run")
        _FULL_DF = df
    return _FULL_DF


def _rth(g: pd.DataFrame) -> pd.DataFrame:
    return g.between_time("09:30", "16:00", inclusive="left")


def precompute(history: pd.DataFrame) -> None:
    """Build ONCE over `history`: the RTH session list, lagged atr14, and the
    per-session vwap_dist_vs_atr descriptor. Nothing here reads a bar later than
    the session it describes."""
    states = build_state_frame(history)                 # v1, price-only: atr14 is lagged
    atr14 = states["atr14"]
    _vol, vwap_dist = _rth_volume_and_close_vwap_dist_by_day(history, atr14)

    days = {d: g for d, g in history.groupby(history.index.date)}
    rth_dates = []
    for d in sorted(days):
        r = _rth(days[d])
        if not r.empty and r.index[0].hour == 9 and r.index[0].minute == 30:
            rth_dates.append(d)

    _PRE.clear()
    _PRE.update({"atr14": atr14, "vwap_dist": vwap_dist, "days": days,
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


def bucket_for(value: float | None) -> str | None:
    """H118's frozen Discovery terciles. None when the descriptor is missing."""
    if value is None or not np.isfinite(value):
        return None
    if value <= LOW_EDGE:
        return "low"
    if value <= MID_EDGE:
        return "mid"
    return "high"


def prior_session(day, history: pd.DataFrame | None = None):
    """The RTH session immediately before `day`, or None."""
    _ensure_pre(history)
    i = _PRE["rth_index"].get(day)
    if i is None or i < 1:
        return None
    return _PRE["rth_dates"][i - 1]


def _exit_session(day):
    """The RTH session HOLD_SESSIONS after the entry session `day`, when it is on
    disk AND the data reaches strictly past it; otherwise None."""
    i = _PRE["rth_index"].get(day)
    if i is None:
        return None
    j = i + HOLD_SESSIONS
    rth = _PRE["rth_dates"]
    if j >= len(rth):
        return None
    return rth[j]


def signals_for_day(day, day_df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    _ensure_pre(history)
    if day not in _PRE["rth_index"]:
        return []

    prior = prior_session(day, history)
    if prior is None:
        return []
    if not UNCONDITIONAL_BASELINE:
        dist = _PRE["vwap_dist"].get(prior)
        if bucket_for(None if dist is None else float(dist)) != "low":
            return []
        dist_val = float(dist)
    else:
        dist = _PRE["vwap_dist"].get(prior)
        if dist is None or not np.isfinite(float(dist)):
            return []                    # same descriptor availability as the filtered arm
        dist_val = float(dist)

    entry_bars = day_df.between_time(ENTRY_TIME, ENTRY_TIME)
    if entry_bars.empty:
        return []
    entry_ts = entry_bars.index[0]
    entry = float(entry_bars["Open"].iloc[0])

    atr = _PRE["atr14"].get(day, float("nan"))
    if not np.isfinite(atr) or atr <= 0:
        return []
    stop = round(entry - ATR_STOP_MULTIPLE * float(atr), 4)
    target = entry + NO_TARGET_PTS

    nxt = _exit_session(day)
    known_exit = nxt is not None
    if known_exit:
        nd = _PRE["days"][nxt]
        if nd.between_time(EXIT_TIME, EXIT_TIME).empty:
            return []                    # exit session has no 09:30 bar (half day / fragment)
        exit_date = nxt
    else:
        # PLACEHOLDER: HOLD_SESSIONS weekdays forward. The cross-session guard
        # refuses it, the entry session is deferred whole, nothing is booked.
        exit_date = (pd.Timestamp(day) + pd.tseries.offsets.BDay(HOLD_SESSIONS)).date()
    exit_ts = (pd.Timestamp(f"{exit_date} {EXIT_TIME}:00").tz_localize(entry_ts.tz)
               if entry_ts.tz is not None else pd.Timestamp(f"{exit_date} {EXIT_TIME}:00"))

    cond = ("prior session's vwap_dist_vs_atr in H118's FROZEN Discovery LOW tercile (<= %.17g)" % LOW_EDGE
            if not UNCONDITIONAL_BASELINE else
            "OWN-DRIFT BASELINE ARM: every session, tercile filter removed (spec s.5) -- NOT a strategy")

    return [Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=entry_ts, instrument=INSTRUMENT, timeframe="1m",
        direction="long", entry=entry, stop=stop, target=target,
        risk_multiple=risk_multiple(entry, stop, target),
        validation_status=VALIDATION_STATUS,
        market_context={
            "strategy_id": STRATEGY_ID, "date": str(day), "entry_time": ENTRY_TIME,
            "signal_session": str(prior), "vwap_dist_vs_atr": round(dist_val, 6),
            "tercile_edges_frozen_discovery": [LOW_EDGE, MID_EDGE],
            "exit_ts": str(exit_ts), "exit_session_known": known_exit,
            "hold_sessions": HOLD_SESSIONS,
            "atr14": round(float(atr), 4),
            "stop_basis": "entry - 4.0 x atr14 (lagged) = disaster cap, not a management stop",
            "target_basis": "none (drift trade) -- unreachable sentinel; risk_multiple is meaningless here",
            "baseline_arm": bool(UNCONDITIONAL_BASELINE),
            "baseline_rule": ("SCREEN passes only if net > 0 AND net per trade beats the same trade taken on "
                              "EVERY session (NQ's own drift over the same 10-session hold) -- spec s.5"),
            "condition": cond,
            "spec": SPEC_PATH},
    )]


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    out = []
    for day, g in df.groupby(df.index.date):
        out.extend(signals_for_day(day, g, history))
    return out


def audit(signals: list[Signal]) -> dict:
    """Mechanical self-checks: one signal a session, every entry at 09:30, every
    exit strictly after its entry, stops below entry, and -- when the filter is
    on -- every signal's descriptor genuinely inside the frozen LOW tercile."""
    per_day: dict[str, int] = {}
    for s in signals:
        d = s.market_context["date"]
        per_day[d] = per_day.get(d, 0) + 1
    over = sum(1 for n in per_day.values() if n > 1)
    bad_entry = sum(1 for s in signals if pd.Timestamp(s.timestamp).strftime("%H:%M") != ENTRY_TIME)
    bad_exit = sum(1 for s in signals
                   if pd.Timestamp(s.market_context["exit_ts"]) <= pd.Timestamp(s.timestamp))
    bad_stop = sum(1 for s in signals if not s.stop < s.entry)
    off_bucket = 0 if UNCONDITIONAL_BASELINE else sum(
        1 for s in signals if s.market_context["vwap_dist_vs_atr"] > LOW_EDGE)
    return {"signals": len(signals), "sessions": len(per_day),
            "multi_signal_sessions": over, "entries_off_clock": bad_entry,
            "exits_not_after_entry": bad_exit, "stops_not_below_entry": bad_stop,
            "signals_outside_frozen_low_tercile": off_bucket,
            "baseline_arm": bool(UNCONDITIONAL_BASELINE),
            "pass": bool(over == 0 and bad_entry == 0 and bad_exit == 0
                         and bad_stop == 0 and off_bucket == 0)}
