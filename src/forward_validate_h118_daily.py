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

    rows = load_log()
    logged_dates = {r["signal_date"] for r in rows}

    bucket_labels = pd.cut(all_states[VAR], bins=bin_edges, labels=labels, duplicates="drop")
    latest_bucket = bucket_labels.iloc[-1]
    latest_row_idx = len(all_states) - 1

    # 1. New signal check
    if pd.notna(latest_bucket) and str(latest_bucket) == BUCKET and str(latest_date) not in logged_dates:
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
