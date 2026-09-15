"""
strategy_s001_level_sweep_reversal.py -- S001, Level Sweep Reversal on compressed
prior days (M26 via Salvage). FROZEN with its spec:
research/infrastructure/strategy-specs/S001-level-sweep-reversal.md (the rules,
the mechanism, the "where this should fail" menu, the pre-registered screen).
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is S001a or a FIX ONCE, never an edit.

THE RULES (restated from the spec; the spec is the authority)
  condition   trade only on sessions flagged prior_day_narrow (volatility_conditioning
              .build_conditioning_frame, the frozen hyp-000048 bottom-tercile definition)
  levels      SUPPORT = min(prior calendar day low, pre-market low before 08:30 ET);
              RESISTANCE = max(prior calendar day high, pre-market high)
              (detect_level_sweep.compute_levels, unchanged)
  window      08:30-10:00 ET (the family's convention, disclosed in the spec)
  signal      sweep of a level, then a bar CLOSING back beyond it by >= 5.0 pts
              (close_min_distance); first confirmation wins; one trade a session
  entry       the NEXT bar's open (no lookahead)
  stop        the sweep extreme;  target  entry +/- 1.35 x risk;  time exit 15:55 ET
  size        1 micro (MNQ)

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, generate_signals(df, history=None) ->
list[strategy_contract.Signal], the same shape execution_dummy.py and
base_entry_b3.py expose for bot_stack_paper_run.py. `df` is the session frame
(one day) the paper loop hands over; `history` is the full price frame the loop
already holds, used for the prior-day state and the prior day's levels. When
`history` is None (standalone use) the module loads the active price file itself,
once per process, and never touches data past the session being scored.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402
from detect_level_sweep import compute_levels, scan_for_signal  # noqa: E402
from volatility_conditioning import build_conditioning_frame  # noqa: E402

STRATEGY_ID = "S001"
STRATEGY_NAME = "s001_level_sweep_reversal_compressed_prior_day"
STRATEGY_VERSION = "S001-1.0 (frozen 2026-09-15)"
CONFIRMATION_MODE = "close_min_distance"     # 5.0-point confirm, detect_level_sweep.MIN_CONFIRM_DISTANCE_POINTS
TIME_EXIT = "15:55"
INSTRUMENT = "MNQ"
VALIDATION_STATUS = "paper-candidate"

_FULL_DF: pd.DataFrame | None = None
_PRE: dict = {}            # precompute() cache: {"cond": frame, "days": {date: frame}, "dates": [...], "src": id}


def _load_full() -> pd.DataFrame:
    global _FULL_DF
    if _FULL_DF is None:
        from data_loader import load_price_data
        df, synthetic = load_price_data(context="strategy_s001", apply_holdout=False)
        if synthetic:
            raise RuntimeError("synthetic data -- S001 refuses to run")
        _FULL_DF = df
    return _FULL_DF


def precompute(history: pd.DataFrame) -> None:
    """Build the frozen prior_day_narrow frame and the per-session frames ONCE
    over `history`. No lookahead is introduced: the flag for day D is a function
    of days before D only (rolling percentile, shifted), and each session's
    signal reads only its own bars and the prior session's. The paper loop and
    the screen both call this before scoring."""
    cond = build_conditioning_frame(history)
    days = {d: g for d, g in history.groupby(history.index.date)}
    _PRE.clear()
    _PRE.update({"cond": cond, "days": days, "dates": sorted(days), "src": id(history)})


def _ensure_pre(history: pd.DataFrame | None) -> None:
    if history is not None and _PRE.get("src") == id(history):
        return
    if history is None and _PRE.get("src") == "full":
        return
    src = history if history is not None else _load_full()
    precompute(src)
    if history is None:
        _PRE["src"] = "full"


def prior_day_narrow(day, history: pd.DataFrame | None = None) -> bool:
    """The frozen hyp-000048 state for `day` (False when there is too little
    history to classify it -- no state, no trade)."""
    _ensure_pre(history)
    cond = _PRE["cond"]
    return bool(cond.loc[day, "prior_day_narrow"]) if day in cond.index else False


def signals_for_day(day, day_df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    if not prior_day_narrow(day, history):
        return []
    dates = [d for d in _PRE["dates"] if d < day]
    if not dates:
        return []
    prior_day = dates[-1]
    levels = compute_levels(pd.concat([_PRE["days"][prior_day], day_df]), day, prior_day)
    if levels is None:
        return []
    raw = scan_for_signal(day_df, levels, CONFIRMATION_MODE)
    if raw is None:
        return []
    # entry = the NEXT bar's open (no lookahead); the confirming bar is raw["signal_time"]
    after = day_df[day_df.index > raw["signal_time"]]
    if after.empty:
        return []
    entry_ts = after.index[0]
    entry = float(after["Open"].iloc[0])
    stop = float(raw["stop"])
    risk = (entry - stop) if raw["direction"] == "long" else (stop - entry)
    if risk <= 0:
        return []          # the next bar opened through the stop: no trade
    target = entry + 1.35 * risk if raw["direction"] == "long" else entry - 1.35 * risk
    return [Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=entry_ts, instrument=INSTRUMENT, timeframe="1m",
        direction=raw["direction"], entry=entry, stop=stop, target=round(target, 4),
        risk_multiple=risk_multiple(entry, stop, target),
        validation_status=VALIDATION_STATUS,
        market_context={"strategy_id": STRATEGY_ID, "date": str(day), "trigger_time": str(raw["signal_time"]),
                        "time_exit": TIME_EXIT, "level_source": raw["level_source"],
                        "level_swept": float(raw["level_swept"]), "sweep_extreme": float(raw["sweep_extreme"]),
                        "condition": "prior_day_narrow=True (hyp-000048 frozen tercile)",
                        "spec": "research/infrastructure/strategy-specs/S001-level-sweep-reversal.md"},
    )]


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    """One or more sessions in `df`; at most one Signal per session."""
    out = []
    for day, g in df.groupby(df.index.date):
        out.extend(signals_for_day(day, g, history))
    return out


def audit(signals: list[Signal]) -> dict:
    per_day: dict[str, int] = {}
    for s in signals:
        per_day[s.market_context["date"]] = per_day.get(s.market_context["date"], 0) + 1
    lookahead = sum(1 for s in signals if pd.Timestamp(s.market_context["trigger_time"]) >= pd.Timestamp(s.timestamp))
    return {"n_signals": len(signals), "n_days": len(per_day), "days_over_one": sum(1 for n in per_day.values() if n > 1),
            "lookahead_violations": lookahead, "pass": lookahead == 0 and all(n == 1 for n in per_day.values())}
