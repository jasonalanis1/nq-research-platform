"""
forward_validate_h118_daily.py
=================================

Daily Forward Validation check for H118 (frozen spec:
research/studies/vwap-dist-low-10d-drift-h118-forward-validation-spec.md).
Paper only, no capital. Meant to run once per trading day (recommended:
a scheduled daily task). Two things it does each run:

  1. Checks if TODAY is a new signal day (vwap_dist_vs_atr in the LOW
     tercile, bucket edges frozen from Discovery -- never refit). If
     so, appends an OPEN paper position to the forward log.
  2. Checks every currently-open paper position to see if today is its
     10-trading-day exit. If so, records the exit price/outcome and
     closes it.

Log: research/forward_validation/h118_forward_log.jsonl (append-only,
one JSON object per signal, updated in place only to add the exit
fields once resolved -- never to change entry fields).

HOW TO RUN (daily):
    python3 src/forward_validate_h118_daily.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from backtest import ROUND_TRIP_COST_POINTS
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from study_vwap_dist_low_10d_drift_h118 import VAR, BUCKET, HORIZON_DAYS, compute_bin_edges

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "research" / "forward_validation"
LOG_PATH = LOG_DIR / "h118_forward_log.jsonl"

# --- Forward Generation boundary (added 2026-09-09, bug fix) ---------------
# data_holdout.py's ALLOW_HOLDOUT_DATA=1 bypass (used below to see recent
# data at all) grants access to the ENTIRE "Holdout Generation 1" legacy
# reserve (2026-04-07 onward, ~130+ trading days), not just today. Per the
# frozen spec (research/studies/vwap-dist-low-10d-drift-h118-forward-
# validation-spec.md): "Forward Validation only uses data from 2026-09-09
# (today) forward ... NOT a slice of existing historical data (that would
# just be more Holdout, and the Holdout budget is separate and already
# partly spent)." Per docs/RESEARCH_INTEGRITY_PROTOCOL.md's own three-
# generation model, Forward Validation is supposed to run on the distinct
# "Forward Generation: live future data -> ongoing, never exhausted" --
# never Holdout Generation 1. The original version of this script relied
# only on always reading `.iloc[-1]` (the single latest row) to keep this
# safe in practice, but never enforced the boundary explicitly -- which
# let one signal (2026-09-08, logged before this fix) get through one day
# EARLIER than the frozen spec's stated boundary, because trading-day data
# lags roughly a day behind the fetch date. That entry is left in the log
# uncorrected (never hand-edit logged results -- see CLAUDE.md's research/
# rules) but is flagged wherever it's discussed. This constant makes the
# boundary explicit and hard-enforced from here on, independent of
# whatever Holdout Generation 1 data happens to be technically reachable.
FORWARD_VALIDATION_ANCHOR = pd.Timestamp("2026-09-09").date()


def load_log():
    if not LOG_PATH.exists():
        return []
    rows = []
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def save_log(rows):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")


def main():
    print("=" * 78)
    print("H118 FORWARD VALIDATION -- daily check (paper only, no capital)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/vwap-dist-low-10d-drift-h118-forward-validation-spec.md\n")

    # ALLOW_HOLDOUT_DATA=1 is required here -- Forward Validation deliberately
    # uses the most recent data available (today forward), which otherwise
    # gets excluded by the standard research-only holdout boundary.
    import os
    os.environ.setdefault("ALLOW_HOLDOUT_DATA", "1")
    df, is_synthetic = load_price_data(context="forward_validate_h118_daily.py", apply_holdout=False)
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    # Bucket edges frozen from Discovery -- identical across every prior stage, never refit.
    discovery = get_discovery_data(df)
    disc_states = extend_state_frame(build_state_frame(discovery), discovery).reset_index()
    bin_edges, labels = compute_bin_edges(disc_states)

    all_states = extend_state_frame(build_state_frame(df), df).reset_index()
    if all_states.empty:
        print("No data available.")
        return

    latest_date = all_states["date"].iloc[-1]
    print(f"Latest available trading day: {latest_date}")

    latest_day_is_forward_eligible = pd.Timestamp(latest_date).date() >= FORWARD_VALIDATION_ANCHOR
    if not latest_day_is_forward_eligible:
        print(f"Latest available day ({latest_date}) is before the Forward Validation "
              f"anchor ({FORWARD_VALIDATION_ANCHOR}) -- this would be Holdout Generation 1 "
              f"data, not genuinely forward data. Skipping the new-signal check for today "
              f"(existing OPEN positions, if any, still get checked for their exit below -- "
              f"that lookup is by row index into already-loaded data, not a new read of "
              f"anything, and does not depend on this boundary).")

    rows = load_log()
    logged_dates = {r["signal_date"] for r in rows}

    bucket_labels = pd.cut(all_states[VAR], bins=bin_edges, labels=labels, duplicates="drop")
    latest_bucket = bucket_labels.iloc[-1]
    latest_row_idx = len(all_states) - 1

    # 1. New signal check
    if latest_day_is_forward_eligible and pd.notna(latest_bucket) and str(latest_bucket) == BUCKET and str(latest_date) not in logged_dates:
        entry_close = float(all_states["Close"].iloc[-1])
        entry_atr = all_states["atr14"].iloc[-1]
        if pd.notna(entry_atr) and entry_atr > 0:
            rows.append({
                "signal_date": str(latest_date),
                "state_var": VAR, "bucket": BUCKET, "horizon_days": HORIZON_DAYS,
                "entry_row_idx": latest_row_idx,
                "entry_close": entry_close, "entry_atr14": float(entry_atr),
                "status": "OPEN", "exit_date": None, "exit_close": None,
                "net_points": None, "r_multiple": None,
            })
            print(f"NEW SIGNAL: {latest_date} -- low-tercile vwap_dist_vs_atr, entry_close={entry_close:.2f}")
        else:
            print(f"Signal day but ATR unavailable, skipped: {latest_date}")
    else:
        print(f"No new signal today ({latest_date} bucket={latest_bucket}).")

    # 2. Resolve any open positions whose exit day has arrived
    n_resolved_today = 0
    for r in rows:
        if r["status"] != "OPEN":
            continue
        exit_idx = r["entry_row_idx"] + HORIZON_DAYS
        if exit_idx >= len(all_states):
            continue  # not enough forward data yet
        exit_close = float(all_states["Close"].iloc[exit_idx])
        exit_date = str(all_states["date"].iloc[exit_idx])
        net = (exit_close - r["entry_close"]) - ROUND_TRIP_COST_POINTS
        r_mult = net / r["entry_atr14"]
        r.update({
            "status": "CLOSED", "exit_date": exit_date, "exit_close": exit_close,
            "net_points": net, "r_multiple": r_mult,
        })
        n_resolved_today += 1
        print(f"RESOLVED: signal {r['signal_date']} -> exit {exit_date}  net={net:+.2f}pts  r={r_mult:+.3f}")

    save_log(rows)

    open_n = sum(1 for r in rows if r["status"] == "OPEN")
    closed = [r for r in rows if r["status"] == "CLOSED"]
    print(f"\nLog: {len(rows)} total signals, {open_n} open, {len(closed)} closed, {n_resolved_today} resolved today.")
    if closed:
        r_mults = [r["r_multiple"] for r in closed]
        print(f"Closed-trade running mean R: {np.mean(r_mults):+.3f} (n={len(closed)}, "
              f"not yet bootstrap-tested -- too few forward signals for a meaningful CI)")
    print(f"\nLog saved to {LOG_PATH}")


if __name__ == "__main__":
    main()
