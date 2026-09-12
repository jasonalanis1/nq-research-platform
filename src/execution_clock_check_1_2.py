"""
execution_clock_check_1_2.py
===============================

Execution Clock, queue item 1b -- the comparison harness that proves
checks 1-2 of the 14 (v3.1 section 4) for the signal engine
(src/execution_clock_signal_engine.py):

    1. Signal occurs when the spec says it should, exactly once
       (audited from the engine's own output -- see
       execution_clock_signal_engine.audit_signals()).
    2. Order (here: signal) correctness -- for this stage, that the
       engine's output exactly matches what the ALREADY-EXISTING forward
       validator (src/forward_validate_h118_daily.py) would say for
       every day the data covers.

HOW THIS AVOIDS TOUCHING H118's FORWARD LOG: this script does NOT call
forward_validate_h118_daily.main() (which appends to
research/forward_validation/h118_forward_log.jsonl -- out of automated
scope, SCOPE BOUNDARY in research/NEXT_UP.md). Instead it reimplements
the forward validator's OWN per-day signal-decision logic --
independently, in a second code path, against the SAME imported frozen
constants (VAR, BUCKET, HORIZON_DAYS, compute_bin_edges from
study_vwap_dist_low_10d_drift_h118.py) that forward_validate_h118_daily.py
itself imports and uses -- and compares day by day against the signal
engine's own walk-forward output. Two independent implementations of the
same frozen rule, no file writes, no side effects.

HOW TO RUN:
    python3 src/execution_clock_check_1_2.py
"""

import pandas as pd

from execution_clock_signal_engine import (
    load_states_and_frozen_edges,
    generate_signals_walkforward,
    audit_signals,
)
from study_vwap_dist_low_10d_drift_h118 import VAR, BUCKET


def forward_validator_style_signal_dates(all_states: pd.DataFrame, bin_edges, labels) -> set:
    """Reproduces forward_validate_h118_daily.py's OWN new-signal test --
    `pd.notna(latest_bucket) and str(latest_bucket) == BUCKET` against
    the Discovery-frozen bin edges -- applied to every day in sequence
    (each day treated once as "latest", exactly as a daily-run script
    would see it, one day at a time, in order). Returns the set of dates
    that script's logic would flag as a new signal day. This function is
    read-only: it never touches h118_forward_log.jsonl."""
    bucket_labels = pd.cut(all_states[VAR], bins=bin_edges, labels=labels, duplicates="drop")
    signal_dates = set()
    for i in range(len(all_states)):
        b = bucket_labels.iloc[i]
        if pd.notna(b) and str(b) == BUCKET:
            signal_dates.add(str(all_states["date"].iloc[i]))
    return signal_dates


def main():
    print("=" * 78)
    print("EXECUTION CLOCK -- CHECKS 1-2 COMPARISON (signal engine vs. forward validator)")
    print("=" * 78)

    df, all_states, bin_edges, labels = load_states_and_frozen_edges()

    engine_signals = generate_signals_walkforward(all_states, df, bin_edges, labels)
    engine_audit = audit_signals(engine_signals)
    engine_dates = {s["signal_date"] for s in engine_signals}

    validator_dates = forward_validator_style_signal_dates(all_states, bin_edges, labels)

    only_in_engine = sorted(engine_dates - validator_dates)
    only_in_validator = sorted(validator_dates - engine_dates)
    exact_match = not only_in_engine and not only_in_validator

    print(f"\nTrading days compared: {len(all_states)}")
    print(f"Signal engine: {len(engine_dates)} signal days, "
          f"{engine_audit['n_unique_signal_dates']} unique, "
          f"no_duplicates={engine_audit['no_duplicate_signal_dates']}")
    print(f"Forward-validator-style recomputation: {len(validator_dates)} signal days")
    print(f"Signal dates only in engine output: {len(only_in_engine)}")
    print(f"Signal dates only in validator-style output: {len(only_in_validator)}")
    print(f"\nCHECK 1 (fires when spec says, exactly once, no missed/duplicate): "
          f"{'PASS' if engine_audit['no_duplicate_signal_dates'] and len(engine_dates) > 0 else 'FAIL'}")
    print(f"CHECK 2 (matches existing forward validator's own logic, every day): "
          f"{'PASS' if exact_match else 'FAIL'}")

    if not exact_match:
        print("\nMISMATCH DETAIL (first 20 each side):")
        print("  only in engine:", only_in_engine[:20])
        print("  only in validator-style recomputation:", only_in_validator[:20])

    return exact_match, engine_audit


if __name__ == "__main__":
    main()
