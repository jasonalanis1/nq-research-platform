"""
strategy_s001a_level_sweep_reversal_prior_day.py -- S001a, Level Sweep Reversal on
compressed prior days, PRIOR-DAY levels only (the S001 salvage spawn, directive s.7).
FROZEN with its spec:
research/infrastructure/strategy-specs/S001a-level-sweep-reversal-prior-day-levels.md.
Standing directive s.13: not edited after the FREEZE row in
research/ledger/strategies.jsonl. A change is a FIX ONCE, never an edit. S001a has
no salvage of its own (one salvage per strategy; S001's was spent).

THE RULES (restated from the spec; the spec is the authority)
  everything     S001's trade, unchanged: prior_day_narrow condition, levels from
                 detect_level_sweep.compute_levels, 08:30-10:00 ET window, close back
                 through the level by >= 5.0 pts, next-bar-open entry, stop at the
                 sweep extreme, 1.35R target, 15:55 ET time exit, 1 micro
  THE ONE CHANGE a signal is taken ONLY when the swept level's source is the PRIOR DAY
                 (prior_day_low / prior_day_high). If the session's first confirmed
                 sweep is of a pre-market level, the session is NO TRADE (the first
                 confirmation still wins, as in S001, so the screen reproduces S001's
                 prior-day cell by construction).

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, precompute(history),
generate_signals(df, history=None) -> list[strategy_contract.Signal], the same
shape S001 / execution_dummy / base_entry_b3 expose to bot_stack_paper_run.py.
The signal itself is computed by the frozen S001 module (imported, not copied):
S001a filters S001's signal by its `level_source` tag and relabels it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal  # noqa: E402
import strategy_s001_level_sweep_reversal as s001  # noqa: E402

STRATEGY_ID = "S001a"
STRATEGY_NAME = "s001a_level_sweep_reversal_prior_day_levels"
STRATEGY_VERSION = "S001a-1.0 (frozen 2026-09-15)"
PRIOR_DAY_SOURCES = ("prior_day_low", "prior_day_high")     # THE added rule
CONFIRMATION_MODE = s001.CONFIRMATION_MODE
TIME_EXIT = s001.TIME_EXIT
INSTRUMENT = s001.INSTRUMENT
VALIDATION_STATUS = "paper-candidate"
SPEC_PATH = "research/infrastructure/strategy-specs/S001a-level-sweep-reversal-prior-day-levels.md"


def precompute(history: pd.DataFrame) -> None:
    """Same trailing state as S001 (prior_day_narrow, per-session frames), built once."""
    s001.precompute(history)


def prior_day_narrow(day, history: pd.DataFrame | None = None) -> bool:
    return s001.prior_day_narrow(day, history)


def _relabel(sig: Signal) -> Signal:
    ctx = dict(sig.market_context or {})
    ctx.update({"strategy_id": STRATEGY_ID, "spec": SPEC_PATH,
                "condition": ctx.get("condition", "") + "; level_source in prior_day_{low,high} (S001 salvage condition)",
                "parent_strategy": s001.STRATEGY_ID})
    return Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=sig.timestamp, instrument=sig.instrument, timeframe=sig.timeframe,
        direction=sig.direction, entry=sig.entry, stop=sig.stop, target=sig.target,
        risk_multiple=sig.risk_multiple, validation_status=VALIDATION_STATUS,
        market_context=ctx,
    )


def signals_for_day(day, day_df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    out = []
    for sig in s001.signals_for_day(day, day_df, history):
        if (sig.market_context or {}).get("level_source") in PRIOR_DAY_SOURCES:
            out.append(_relabel(sig))
    return out


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    """One or more sessions in `df`; at most one Signal per session."""
    out = []
    for day, g in df.groupby(df.index.date):
        out.extend(signals_for_day(day, g, history))
    return out


def audit(signals: list[Signal]) -> dict:
    base = s001.audit(signals)
    wrong_source = sum(1 for s in signals if (s.market_context or {}).get("level_source") not in PRIOR_DAY_SOURCES)
    base["wrong_level_source"] = wrong_source
    base["pass"] = bool(base["pass"] and wrong_source == 0)
    return base
