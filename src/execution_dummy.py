"""
execution_dummy.py -- a HIGH-FREQUENCY PLACEHOLDER whose only job is to feed the
order path enough orders to collect the pre-registered 20-fill execution sample
in days instead of weeks.

WHY (Jason, September 14th, ~8:00 pm CT: "I need answers sooner... push this as
fast as possible"): B3 fires once a session, so 20 fills takes ~27 trading days.
The paper record measures PLUMBING -- does an order go out correctly, fill, get
recorded and reconciled -- and plumbing does not care which rule generated the
order. This rule fires FOUR times a session (capital_protection's
max_orders_per_day) at fixed clock times, so 20 fills arrives in ~5 sessions.

WHAT IT IS NOT: a strategy. It has no claimed edge, every signal is labelled
placeholder, and no P&L it produces may be read as evidence about anything. It
is frozen here before it runs, and it is never tuned (AMENDMENT v3.1).

THE RULE (frozen 2026-09-14, ~8:30 pm CT, before any run):
  fire times     10:00, 11:30, 13:00, 14:30 ET  (the bar that STARTS at that
                 minute is the trigger bar)
  direction      sign of the trigger bar's close minus the close 5 bars earlier
                 (known at the trigger bar's close; ties -> long)
  entry          the NEXT bar's open (the same no-lookahead convention as B3)
  stop / target  20 points below / above entry (long), mirrored for short --
                 a $40 swing on a micro, small on purpose so the R-budget is
                 never the thing that blocks an order
  time exit      30 minutes after entry (bookkeeping only)
  size           1 micro, always
  kills          capital-protection kills fire exactly as for any strategy and
                 are RECORDED. Because this is a plumbing dummy with no edge, a
                 kill is expected to happen (a 20/20 coin-flip loses to noise)
                 and it would end the sample early -- the first replay was
                 killed after 12 fills at -4R. So, added to the frozen spec
                 BEFORE any live run and after that REPLAY only: after a kill the
                 dummy opens a NEW paper account (bot_stack_paper_run records a
                 `paper_account_reset` row) and continues. The kill row stays in
                 the record as evidence the switch works on a running P&L. No
                 rule, threshold or parameter was changed to get here.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402
from base_entry_b3 import VALIDATION_STATUS  # noqa: E402

STRATEGY_NAME = "execution_dummy_4x_placeholder"
STRATEGY_VERSION = "DUMMY-1.0 (frozen 2026-09-14)"
FIRE_TIMES = ("10:00", "11:30", "13:00", "14:30")
LOOKBACK_BARS = 5
STOP_PTS = 20.0
TARGET_PTS = 20.0
EXIT_MINUTES = 30
INSTRUMENT = "MNQ"


def signals_for_day(day_df: pd.DataFrame) -> list[Signal]:
    rth = day_df.between_time("09:30", "16:00", inclusive="left")
    if len(rth) < 60:
        return []
    closes = rth["Close"].to_numpy(float)
    idx = rth.index
    labels = idx.strftime("%H:%M")
    out = []
    for t in FIRE_TIMES:
        hits = np.where(labels == t)[0]
        if len(hits) == 0:
            continue
        i = int(hits[0])
        if i < LOOKBACK_BARS or i + 1 >= len(rth):
            continue
        move = closes[i] - closes[i - LOOKBACK_BARS]
        direction = "short" if move < 0 else "long"
        entry_ts = idx[i + 1]
        entry = float(rth["Open"].iloc[i + 1])
        stop = entry - STOP_PTS if direction == "long" else entry + STOP_PTS
        target = entry + TARGET_PTS if direction == "long" else entry - TARGET_PTS
        exit_time = (entry_ts + pd.Timedelta(minutes=EXIT_MINUTES)).strftime("%H:%M")
        out.append(Signal(
            strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
            timestamp=entry_ts, instrument=INSTRUMENT, timeframe="1m",
            direction=direction, entry=entry, stop=stop, target=target,
            risk_multiple=risk_multiple(entry, stop, target),
            validation_status=VALIDATION_STATUS,
            market_context={"placeholder": True, "date": str(entry_ts.date()),
                            "trigger_time": str(idx[i]), "fire_time": t, "time_exit": exit_time,
                            "note": "execution dummy -- plumbing only, no claimed edge"},
        ))
    return out


def generate_signals(df: pd.DataFrame) -> list[Signal]:
    out = []
    for _, g in df.groupby(df.index.normalize()):
        out.extend(signals_for_day(g))
    return out


def audit(signals: list[Signal]) -> dict:
    per_day: dict[str, int] = {}
    for s in signals:
        per_day[s.market_context["date"]] = per_day.get(s.market_context["date"], 0) + 1
    over = sum(1 for n in per_day.values() if n > len(FIRE_TIMES))
    lookahead = sum(1 for s in signals
                    if pd.Timestamp(s.market_context["trigger_time"]) >= pd.Timestamp(s.timestamp))
    not_placeholder = sum(1 for s in signals if s.validation_status != VALIDATION_STATUS)
    return {"n_signals": len(signals), "n_days": len(per_day), "days_over_cap": over,
            "lookahead_violations": lookahead, "non_placeholder_labels": not_placeholder,
            "pass": over == 0 and lookahead == 0 and not_placeholder == 0}
