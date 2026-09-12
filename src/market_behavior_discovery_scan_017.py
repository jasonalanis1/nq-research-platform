"""
market_behavior_discovery_scan_017.py
========================================

Scan 017. Draws Entry 14 (map anchor M4) from research/idea_inventory.md:
pre-FOMC drift, EXACT Lucca-Moench window (prior-day 14:00 ET -> FOMC-day
14:00 ET). SECOND AND LAST attempt on pre-FOMC drift (hyp-000111 = attempt
1, a different, non-exact window). Mechanism doc written BEFORE this scan:
research/mechanisms/pre-fomc-drift-exact-lm-window-m4.md.

Frozen scope (mechanism doc Section 6):
  - state/outcome (same thing here -- no separate conditioning state, this
    is a pure calendar-event characterization, same convention as the
    already-closed FOMC/CPI release studies): return from the anchor value
    at 14:00 ET on the PRIOR trading day to the anchor value at 14:00 ET on
    the FOMC day, / ATR14 (trailing mean RTH range, computed through the
    prior day, no lookahead).
  - P1 (gating, single cell): FOMC-day-ending 14:00->14:00 windows, mean
    credibly positive.
  - P2 (reported): compared against the same 14:00->14:00 window ending on
    all NON-FOMC trading days in Discovery (baseline).

"Anchor value at 14:00" reuses the exact convention already established in
study_fomc_volatility.compute_forward_return_at(): the Open of the first
1-minute bar at or after 14:00 ET that day.

ONE pre-registered shot; no retuning. scan_017_2026-09-12 (1 cell)
registered in src/project_wide_multiplicity.py BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_017.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_fomc_volatility import FOMC_DATES
from market_behavior_discovery_scan_012 import rth_daily

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_WINDOW = 14


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float); v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = rng.choice(v, size=(n_bootstrap, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def bootstrap_diff_ci(a, b, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]; b = b[~np.isnan(b)]
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    d = rng.choice(a, size=(n_bootstrap, len(a)), replace=True).mean(axis=1) - rng.choice(b, size=(n_bootstrap, len(b)), replace=True).mean(axis=1)
    return float(np.percentile(d, 5)), float(np.percentile(d, 95))


def summarize(vals) -> dict:
    vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
    n = len(vals)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": [float("nan"), float("nan")], "credible_vs_zero": False, "direction": "insufficient_n"}
    m = float(np.mean(vals)); ci = bootstrap_mean_ci(vals)
    credible = ci[0] > 0 or ci[1] < 0
    direction = "positive" if (credible and ci[0] > 0) else ("negative" if (credible and ci[1] < 0) else "null")
    return {"n": n, "mean": m, "ci_90": list(ci), "credible_vs_zero": bool(credible), "direction": direction}


def anchor_value(day_df: pd.DataFrame, hour: int, minute: int, tz):
    if day_df.empty:
        return None
    anchor_ts = pd.Timestamp(day_df.index[0].date(), tz=tz).replace(hour=hour, minute=minute)
    bars = day_df[day_df.index >= anchor_ts]
    if bars.empty:
        return None
    return float(bars.iloc[0]["Open"])


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 017 (Entry 14 / M4: pre-FOMC drift, exact L-M window)"); print("=" * 78)
    df, syn = load_price_data(context="market_behavior_discovery_scan_017.py", symbol="NQ")
    if syn:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(df)
    daily = rth_daily(disc)
    daily["atr14"] = daily["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    atr_by_date = {d.date(): v for d, v in daily["atr14"].items()}

    tz = disc.index.tz
    day_groups = {day: sub for day, sub in disc.groupby(disc.index.date)}
    trading_days = sorted(day_groups.keys())
    anchor_14 = {d: anchor_value(day_groups[d], 14, 0, tz) for d in trading_days}

    rows = []
    for i in range(1, len(trading_days)):
        cur, prev = trading_days[i], trading_days[i - 1]
        v_cur, v_prev = anchor_14.get(cur), anchor_14.get(prev)
        atr14 = atr_by_date.get(prev)  # info available at the start of the window (prior day's trailing ATR)
        if v_cur is None or v_prev is None or atr14 is None or np.isnan(atr14):
            continue
        ret = (v_cur - v_prev) / atr14
        rows.append({"date": str(cur), "is_fomc": cur in FOMC_DATES, "ret_1400_to_1400": ret})
    f = pd.DataFrame(rows)
    print(f"Usable 14:00->14:00 windows (anchor + ATR available): {len(f)}")

    fomc_vals = f.loc[f["is_fomc"], "ret_1400_to_1400"].tolist()
    base_vals = f.loc[~f["is_fomc"], "ret_1400_to_1400"].tolist()
    fomc_summary = summarize(fomc_vals)
    base_summary = summarize(base_vals)
    print(f"\nGATING (P1, FOMC-day-ending 14:00->14:00 windows): n={fomc_summary['n']} mean={fomc_summary['mean']:+.4f} ci_90=({fomc_summary['ci_90'][0]:+.4f},{fomc_summary['ci_90'][1]:+.4f}) {fomc_summary['direction']}")
    verdict = "P1_PASS" if fomc_summary["direction"] == "positive" else "P1_FAIL"
    print(f"Verdict: {verdict}")

    diff = {}
    if verdict == "P1_PASS":
        dci = bootstrap_diff_ci(fomc_vals, base_vals)
        dm = float(np.mean(fomc_vals) - np.mean(base_vals))
        diff = {"fomc_minus_baseline_mean": dm, "ci_90": list(dci), "credible_positive": bool(dci[0] > 0)}
        print(f"  P2 baseline: n={base_summary['n']} mean={base_summary['mean']:+.4f} {base_summary['direction']} | FOMC-minus-baseline: {dm:+.4f} ci_90=({dci[0]:+.4f},{dci[1]:+.4f}) credible_positive={diff['credible_positive']}")
    else:
        print("  P1 failed -- P2 baseline comparison not mined per the pre-registered scope (reported only, read if P1 passes).")

    out = {"state_var": "fomc_1400_to_1400_return", "n_fomc_windows": int(fomc_summary["n"]), "n_baseline_windows": int(base_summary["n"]),
           "gating_cell": fomc_summary, "baseline_cell": base_summary, "gating_verdict": verdict, "p2_fomc_minus_baseline": diff}
    (DATA_DIR / "market_behavior_discovery_scan_017_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_017_results.json'}")


if __name__ == "__main__":
    main()
