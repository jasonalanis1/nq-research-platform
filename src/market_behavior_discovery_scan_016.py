"""
market_behavior_discovery_scan_016.py
========================================

Scan 016. Draws Entry 13 (map anchor M3b) from research/idea_inventory.md:
post-FOMC-statement continuation vs. reversal. Mechanism doc written BEFORE
this scan: research/mechanisms/post-fomc-continuation-m3b.md.

Frozen scope (mechanism doc Section 6):
  - state: fomc_initial_move_vs_atr = (14:30 close - 14:00 close) / ATR14,
    signed, on FOMC statement days (study_fomc_volatility.FOMC_DATES).
  - gating outcome (P1, the single pre-registered cell, ALL FOMC days
    pooled -- too thin for terciles): sign-adjusted return 14:30 -> 16:00
    (90 min), / ATR14. Sign-adjusted = sign(state) * raw return, so
    "continuation" is positive regardless of which direction the initial
    move ran.
  - reported (P2, descriptive only, read if P1 passes): split by whether
    |initial move|/ATR is above/below the Discovery-sample median.

Reuses study_fomc_volatility.compute_forward_return_at() unmodified (the
anchor-time-parameterized forward-return helper already built for this
exact 14:00 ET anchor).

ONE pre-registered shot; no retuning. scan_016_2026-09-12 (1 cell)
registered in src/project_wide_multiplicity.py BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_016.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_fomc_volatility import FOMC_DATES, compute_forward_return_at
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


def summarize(vals) -> dict:
    vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
    n = len(vals)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": [float("nan"), float("nan")], "credible_vs_zero": False, "direction": "insufficient_n"}
    m = float(np.mean(vals)); ci = bootstrap_mean_ci(vals)
    credible = ci[0] > 0 or ci[1] < 0
    direction = "positive" if (credible and ci[0] > 0) else ("negative" if (credible and ci[1] < 0) else "null")
    return {"n": n, "mean": m, "ci_90": list(ci), "credible_vs_zero": bool(credible), "direction": direction}


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 016 (Entry 13 / M3b: post-FOMC-statement continuation)"); print("=" * 78)
    df, syn = load_price_data(context="market_behavior_discovery_scan_016.py", symbol="NQ")
    if syn:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(df)
    daily = rth_daily(disc)
    daily["atr14"] = daily["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    atr_by_date = {d.date(): v for d, v in daily["atr14"].items()}

    day_groups = {day: sub for day, sub in disc.groupby(disc.index.date)}
    fomc_days_in_discovery = [d for d in FOMC_DATES if d in day_groups]
    print(f"FOMC statement days present in Discovery: {len(fomc_days_in_discovery)} of {len(FOMC_DATES)} total registered")

    rows = []
    for day in fomc_days_in_discovery:
        day_df = day_groups[day]
        atr14 = atr_by_date.get(day)
        if atr14 is None or np.isnan(atr14):
            continue
        initial_move = compute_forward_return_at(day_df, day, 14, 0, 30)
        cont_90 = compute_forward_return_at(day_df, day, 14, 30, 90)
        cont_30 = compute_forward_return_at(day_df, day, 14, 30, 30)
        if initial_move is None or cont_90 is None:
            continue
        sign = 1.0 if initial_move >= 0 else -1.0
        rows.append({
            "date": str(day),
            "initial_move_vs_atr": abs(initial_move) / atr14,
            "gating_sign_adj_ret": sign * cont_90 / atr14,
            "reported_sign_adj_ret": (sign * cont_30 / atr14) if cont_30 is not None else float("nan"),
        })
    f = pd.DataFrame(rows)
    print(f"Usable FOMC days (initial move + gating window both available, ATR available): {len(f)}")

    gating = summarize(f["gating_sign_adj_ret"].tolist())
    print(f"\nGATING (P1, ALL FOMC days pooled, sign-adjusted 14:30->16:00 continuation): n={gating['n']} mean={gating['mean']:+.4f} ci_90=({gating['ci_90'][0]:+.4f},{gating['ci_90'][1]:+.4f}) {gating['direction']}")
    verdict = "P1_PASS" if gating["direction"] == "positive" else "P1_FAIL"
    print(f"Verdict: {verdict}")

    reported = {}
    if verdict == "P1_PASS" and len(f) >= 10:
        med = f["initial_move_vs_atr"].median()
        reported = {
            "large_initial_move": summarize(f.loc[f["initial_move_vs_atr"] >= med, "reported_sign_adj_ret"].tolist()),
            "small_initial_move": summarize(f.loc[f["initial_move_vs_atr"] < med, "reported_sign_adj_ret"].tolist()),
        }
        print(f"  P2 large-initial-move n={reported['large_initial_move']['n']} mean={reported['large_initial_move']['mean']:+.4f} {reported['large_initial_move']['direction']} | small-initial-move n={reported['small_initial_move']['n']} mean={reported['small_initial_move']['mean']:+.4f} {reported['small_initial_move']['direction']}")
    else:
        print("  P1 failed (or n<10) -- P2 not mined per the pre-registered scope (reported only, read if P1 passes).")

    out = {"state_var": "fomc_initial_move_vs_atr", "n_fomc_days_usable": int(len(f)),
           "gating_cell": gating, "gating_verdict": verdict, "p2_initial_move_size_split": reported}
    (DATA_DIR / "market_behavior_discovery_scan_016_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_016_results.json'}")


if __name__ == "__main__":
    main()
