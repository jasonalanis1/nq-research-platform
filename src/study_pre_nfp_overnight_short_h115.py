"""
study_pre_nfp_overnight_short_h115.py
========================================

H115 / exp-130 -- frozen spec:
research/studies/pre-nfp-overnight-short-h115-spec.md.
SECOND AND FINAL monetization attempt for OBS-FINDING-012. ATR-scaled
stop/target (project's standard convention), not excursion-derived
(that was H114, which failed).

HOW TO RUN:
    python3 src/study_pre_nfp_overnight_short_h115.py
"""
import json
from pathlib import Path

import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from study_bar_behavior_batch1 import build_daily_bars
from study_pre_move_behavior_batch1 import analyze_r_multiples, MIN_PROSPECTIVE_N
from detect_level_sweep import TARGET_R_MULTIPLE

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SEARCH_BATCH_ID = "batch-2026-09-09-observatory-h115"
ATR_WINDOW = 14


def first_friday(year, month):
    d = pd.Timestamp(year=year, month=month, day=1)
    offset = (4 - d.weekday()) % 7
    return (d + pd.Timedelta(days=offset)).date()


def simulate_signal(window_df, sig):
    sig_series = pd.Series(sig)
    outcome = simulate_trade(window_df, sig_series, "signal_time")
    risk_points = abs(sig["entry"] - sig["stop"])
    if risk_points <= 0:
        return None
    pnl_gross = sig["entry"] - outcome["exit_price"]  # short
    is_resolved = not outcome["exit_reason"].startswith("unresolved")
    pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
    return pnl_net / risk_points


def main():
    print("=" * 78)
    print("H115/EXP-130: PRE-NFP OVERNIGHT SHORT, ATR-SCALED EXITS (FINAL ATTEMPT)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/pre-nfp-overnight-short-h115-spec.md\n")

    df, is_synthetic = load_price_data(context="study_pre_nfp_overnight_short_h115.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    years = sorted(set(d.year for d in days_sorted))
    nfp_dates = set()
    for y in years:
        for m in range(1, 13):
            nfp_dates.add(first_friday(y, m))

    short_r = []
    n_signals = 0
    for i, day in enumerate(days_sorted):
        if day not in nfp_dates or i == 0:
            continue
        prior_day = days_sorted[i - 1]
        if prior_day not in daily_bars.index:
            continue
        atr = daily_bars.loc[prior_day, "atr14"]
        if pd.isna(atr) or atr <= 0:
            continue
        atr = float(atr)
        rth = day_groups[day].between_time("09:30", "16:00")
        if rth.empty:
            continue
        open_ts = rth.index[0]
        prior_rth = day_groups[prior_day].between_time("09:30", "16:00")
        if prior_rth.empty:
            continue
        prior_close_ts = prior_rth.index[-1]
        prior_close = float(prior_rth["Close"].iloc[-1])

        window = discovery[(discovery.index > prior_close_ts) & (discovery.index <= open_ts)]
        if window.empty:
            continue

        entry = prior_close
        stop = entry + atr
        risk = abs(stop - entry)
        target = entry - TARGET_R_MULTIPLE * risk
        sig = {"signal_time": prior_close_ts, "direction": "short", "entry": entry, "stop": stop, "target": target}
        n_signals += 1
        r = simulate_signal(window, sig)
        if r is not None:
            short_r.append(r)

    print(f"\nPre-NFP overnight short signals: {n_signals}   resolved: {len(short_r)}")
    result = analyze_r_multiples(short_r)
    n = result.get("n", 0)
    if n == 0:
        verdict = "NO_DATA"
    elif result["statistically_credible"] and result["economically_meaningful"]:
        verdict = "STEP_1+2_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN_FOR_PROSPECTIVE"
    else:
        verdict = "STEP_1+2_FAIL"

    print(f"\nResult: {result}")
    print(f"Verdict: {verdict}")

    out = {"search_batch_id": SEARCH_BATCH_ID, "result": result, "verdict": verdict}
    with open(DATA_DIR / "study_pre_nfp_overnight_short_h115_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {DATA_DIR / 'study_pre_nfp_overnight_short_h115_results.json'}")


if __name__ == "__main__":
    main()
