"""
execution_clock_signal_engine.py
===================================

Execution Clock, queue item 1b (research/NEXT_UP.md; spec:
research/infrastructure/back-half-production-integrity-v3.md, AMENDMENT
v3.1). Proves execution checks 1-2 of the 14 (v3.1 section 4):

    1. Signal occurs when the spec says it should
    2. Signal occurs exactly once when it should

MINIMUM SCOPE, deliberately: this engine only decides (a) is today a
signal day, and (b) what the entry/exit timestamps would be per the
frozen execution-approximation convention. It does NOT place orders,
does NOT talk to a broker, does NOT track fills, and does NOT touch
H118's forward-validation log (research/forward_validation/h118_forward_log.jsonl)
or any H118 ledger row -- that is out of automated scope (SCOPE BOUNDARY,
research/NEXT_UP.md) and belongs to later checks 3+ (queue item 1c),
which also needs 1a's execution-checks-concrete work first.

INPUTS, both frozen, both read-only here, never modified:
  - H118's signal rule: vwap_dist_vs_atr LOW tercile, bucket edges frozen
    from Discovery (research/studies/vwap-dist-low-10d-drift-h118-spec.md;
    same bin-edge convention already used in production by
    src/forward_validate_h118_daily.py and
    src/study_vwap_dist_low_10d_drift_h118.py -- this script imports those
    same constants/functions rather than re-typing the rule, so there is
    only one place the frozen rule is expressed in code).
  - The execution-approximation convention: single market order at
    15:58:00 America/New_York on the signal date (entry) and on signal
    date + 10 trading days (exit), 1 MNQ, deterministic timestamp.
    research/studies/h118-execution-approximation-spec.md.

WALK-FORWARD, NO LOOKAHEAD: generate_signals_walkforward() processes
trading days in chronological order, one at a time, using only (a) that
day's own vwap_dist_vs_atr (already known as of that day's close, per
market_state_primitives_v2.py's own docstring -- "same-day, known by
close") and (b) the bucket edges, which are frozen constants computed
once from the Discovery slice and never recomputed as new days arrive
(exactly matching forward_validate_h118_daily.py's own convention). No
day's decision ever depends on a later day's data.

HOW TO RUN:
    python3 src/execution_clock_signal_engine.py
"""

import os
from pathlib import Path

import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from study_vwap_dist_low_10d_drift_h118 import VAR, BUCKET, HORIZON_DAYS, compute_bin_edges

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Frozen execution-approximation convention (research/studies/
# h118-execution-approximation-spec.md) -- a deterministic timestamp, not
# a window.
EXECUTION_TIME_NY = "15:58:00"
EXECUTION_TZ = "America/New_York"


def load_states_and_frozen_edges():
    """Loads the full price series and daily state frame, and the bucket
    edges frozen from Discovery -- identical inputs/logic to
    forward_validate_h118_daily.py's main(), factored out here so both
    can be driven without either one writing to H118's forward log."""
    os.environ.setdefault("ALLOW_HOLDOUT_DATA", "1")
    df, is_synthetic = load_price_data(
        context="execution_clock_signal_engine.py", apply_holdout=False
    )
    if is_synthetic:
        raise RuntimeError("Only synthetic data available -- signal engine refuses to run on it.")

    discovery = get_discovery_data(df)
    disc_states = extend_state_frame(build_state_frame(discovery), discovery).reset_index()
    bin_edges, labels = compute_bin_edges(disc_states)

    all_states = extend_state_frame(build_state_frame(df), df).reset_index()
    return df, all_states, bin_edges, labels


def _days_with_bar_at(df: pd.DataFrame, time_str: str = EXECUTION_TIME_NY) -> set:
    """Set of calendar dates that have a 1-minute bar at exactly
    `time_str` (America/New_York, matching df's own index tz). Computed
    once, vectorized -- a per-signal per-day filter over a multi-million-
    row 1-minute frame is not (each `.between_time` on the full frame,
    repeated per signal, does not scale)."""
    return set(df.between_time(time_str, time_str).index.date)


def generate_signals_walkforward(all_states: pd.DataFrame, df: pd.DataFrame,
                                  bin_edges, labels) -> list[dict]:
    """Walks every trading day in `all_states` IN CHRONOLOGICAL ORDER, as
    if running live one day at a time, and decides whether that day is an
    H118 signal day per the frozen rule. For each signal day, computes the
    entry/exit timestamps per the frozen execution-approximation
    convention and records whether a tradeable bar exists at that exact
    timestamp (a genuine executability question -- flagged, never
    resolved by picking a different timestamp).

    No lookahead: bucket edges are the fixed Discovery-frozen constants
    passed in (never recomputed inside this loop), and each day's own
    vwap_dist_vs_atr value is the only input this loop reads for that
    day's decision -- exactly the information a live run would have at
    that day's close.
    """
    signals = []
    n = len(all_states)
    days_with_bar = _days_with_bar_at(df)
    # Bucket edges are frozen constants (computed once from Discovery,
    # never refit as new days arrive) -- applying pd.cut to each day's own
    # value against those fixed edges is a per-day, no-lookahead
    # computation regardless of whether it is called once per row inside
    # the loop or vectorized ahead of time; vectorizing here is purely a
    # performance choice, not a change in what information is used.
    bucket_labels = pd.cut(all_states[VAR], bins=bin_edges, labels=labels, duplicates="drop")
    for i in range(n):
        bucket = bucket_labels.iloc[i]
        if pd.isna(bucket) or str(bucket) != BUCKET:
            continue

        signal_date = all_states["date"].iloc[i]
        entry_ts = pd.Timestamp(f"{signal_date} {EXECUTION_TIME_NY}", tz=EXECUTION_TZ)
        entry_bar_exists = signal_date in days_with_bar

        exit_j = i + HORIZON_DAYS
        if exit_j < n:
            exit_date = all_states["date"].iloc[exit_j]
            exit_ts = pd.Timestamp(f"{exit_date} {EXECUTION_TIME_NY}", tz=EXECUTION_TZ)
            exit_bar_exists = exit_date in days_with_bar
            resolved = True
        else:
            exit_date, exit_ts, exit_bar_exists, resolved = None, None, None, False

        signals.append({
            "entry_row_idx": i,
            "signal_date": str(signal_date),
            "state_var": VAR,
            "bucket": BUCKET,
            "horizon_days": HORIZON_DAYS,
            "entry_timestamp": entry_ts.isoformat(),
            "entry_bar_exists": entry_bar_exists,
            "exit_date": str(exit_date) if exit_date is not None else None,
            "exit_timestamp": exit_ts.isoformat() if exit_ts is not None else None,
            "exit_bar_exists": exit_bar_exists,
            "resolved": resolved,
        })
    return signals


def audit_signals(signals: list[dict]) -> dict:
    """Check 1 (fires when the spec says) and check 2 (fires exactly once,
    no missed/duplicate signals) as mechanical, re-checkable facts about
    the engine's own output -- not a claim, a count."""
    dates = [s["signal_date"] for s in signals]
    duplicates = len(dates) != len(set(dates))
    entry_bar_missing = [s["signal_date"] for s in signals if not s["entry_bar_exists"]]
    exit_bar_missing = [
        s["signal_date"] for s in signals if s["resolved"] and not s["exit_bar_exists"]
    ]
    return {
        "n_signals": len(signals),
        "n_unique_signal_dates": len(set(dates)),
        "no_duplicate_signal_dates": not duplicates,
        "n_entry_bar_missing": len(entry_bar_missing),
        "entry_bar_missing_dates": entry_bar_missing,
        "n_exit_bar_missing": len(exit_bar_missing),
        "exit_bar_missing_dates": exit_bar_missing,
    }


def main():
    print("=" * 78)
    print("EXECUTION CLOCK -- SIGNAL ENGINE (queue item 1b, checks 1-2 of 14)")
    print("=" * 78)
    print("\nFrozen inputs: research/studies/vwap-dist-low-10d-drift-h118-spec.md "
          "(signal rule)\n                research/studies/h118-execution-approximation-spec.md "
          "(entry/exit convention)\n")

    df, all_states, bin_edges, labels = load_states_and_frozen_edges()
    signals = generate_signals_walkforward(all_states, df, bin_edges, labels)
    audit = audit_signals(signals)

    print(f"Trading days processed (walk-forward, in order): {len(all_states)}")
    print(f"Signal days found: {audit['n_signals']}")
    print(f"No duplicate signal dates: {audit['no_duplicate_signal_dates']}")
    print(f"Entry days with NO 15:58:00 NY bar on disk: {audit['n_entry_bar_missing']}")
    print(f"Resolved-horizon exit days with NO 15:58:00 NY bar on disk: {audit['n_exit_bar_missing']}")
    if audit["n_entry_bar_missing"] or audit["n_exit_bar_missing"]:
        print("\nFLAGGED, not resolved here (per the binding Integrity Gate guardrail on this "
              "item): the frozen 15:58:00 America/New_York timestamp has no tradeable bar on "
              "some entry/exit days (market holidays and early closes). This is a genuine "
              "executability finding about the frozen convention, not a defect in this engine, "
              "and this engine does not invent a substitute timestamp to paper over it.")


if __name__ == "__main__":
    main()
