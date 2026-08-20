"""
strategy_contract.py
======================

WHAT THIS FILE DOES (plain English):
Defines the shared `Signal` shape approved in
docs/AUTOMATION_ARCHITECTURE.md, so every detector (detect_setups.py,
detect_level_sweep.py, and future ones) can produce output in one common
format instead of each inventing its own signal-file shape. This is the
first step toward backtest.py/score_results.py/confidence_analysis.py
being able to run against ANY conforming detector through one interface.

THIS IS AN EXTRACTION, NOT A REWRITE (2026-08-20): the detectors' actual
detection math (detect_orb_for_day, compute_levels, scan_for_signal,
_support_confirmed, _resistance_confirmed) is completely UNCHANGED. Each
detector now also exposes a `generate_signals()` function that runs that
same unchanged logic and translates its output into this Signal shape.
Verified before being trusted: generate_signals() for both Level Sweep
variants (close_min_distance, full_bar_range) was checked to produce
byte-identical entry/stop/target/direction/date values against the
existing detect_level_sweep.py CSV output, row for row.

STATUS: backtest.py, score_results.py, and confidence_analysis.py have
NOT been rewired to consume Signal objects yet -- they still read the
CSV files the detectors already write. That's deliberately a separate,
later step, so it can be verified on its own instead of bundled with
this extraction.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Signal:
    """
    One detected trade candidate, in the shape approved in
    docs/AUTOMATION_ARCHITECTURE.md's "Signal schema, approved
    2026-08-20" section.

    Field notes:
      - risk_multiple: the signal's planned reward-to-risk ratio
        (|target - entry| / |entry - stop|), computed at signal time --
        NOT a realized trade outcome. That's a different, later number
        backtest.py computes (r_multiple_net/r_multiple_gross) once a
        signal is actually resolved.
      - historical_sample_size / historical_expectancy: aggregate stats
        about this strategy/variant's track record so far. Left as None
        by the bare detector functions below -- they describe historical
        performance, which isn't something a detector can know about
        itself; something downstream (e.g. Tony, or a future dashboard
        step) fills these in from the logged experiments.
      - market_context: free-form dict for whatever extra detail a given
        strategy wants to attach (e.g. which level was swept). Optional,
        not used by the core pipeline.
    """
    strategy_name: str
    strategy_version: str
    timestamp: object            # the signal/confirmation bar's timestamp
    instrument: str
    timeframe: str
    direction: str                # "long" or "short"
    entry: float
    stop: float
    target: float
    risk_multiple: float
    validation_status: str        # research / holdout-validated / paper / live-approved
    historical_sample_size: Optional[int] = None
    historical_expectancy: Optional[float] = None
    market_context: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


def risk_multiple(entry: float, stop: float, target: float) -> float:
    """Shared helper: planned reward-to-risk ratio for a signal, computed
    the same way regardless of which detector produced it."""
    risk = abs(entry - stop)
    if risk == 0:
        return float("nan")
    return round(abs(target - entry) / risk, 6)
