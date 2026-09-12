"""
market_behavior_discovery_scan_013.py
========================================

Scan 013. Draws Entry 11 (map anchor M1): cash-close move conditioned on
close-window volume -> next-morning reversal. ATTEMPT 2 OF 2 on the
closing-move family (hyp-000110 was the unconditioned null). Mechanism doc
written BEFORE this scan: research/mechanisms/cash-close-imbalance-volume-
conditioned-m1.md (AMENDMENT v2.5).

Frozen scope (mechanism doc Section 6):
  - close_move_vs_atr = (16:00 RTH close - 15:50 close) / ATR14, signed
    (window [15:50, 16:00), half-open).
  - close_volume_vs_norm = volume in [15:50, 16:00) / trailing-20-day mean of
    that same window (shifted one day); terciles cut on the Discovery sample.
  - outcomes, SIGN-ADJUSTED so a reversal of the close move is positive:
    next-day 09:30 open vs 16:00 close; next-day 10:00 close (last bar
    before 10:00) vs 16:00 close; both / ATR14.
  - SIX pre-registered cells: 3 volume terciles x 2 horizons.
Gating (P1): HIGH volume tercile, open horizon, mean > 0 credible (90% CI
lower bound > 0) AND the LOW tercile is NOT equally credible-positive.
Reported: P2 (within HIGH, top vs bottom half by |close_move_vs_atr|),
P3 (open vs 10:00 within HIGH).

ONE pre-registered shot; no retuning. scan_013_2026-09-12 (6 cells)
registered in src/project_wide_multiplicity.py BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_013.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_WINDOW = 14
VOL_LOOKBACK = 20
TERCILE_LABELS = ["low", "mid", "high"]


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
    direction = "reversal" if (credible and ci[0] > 0) else ("continuation" if (credible and ci[1] < 0) else "null")
    return {"n": n, "mean": m, "ci_90": list(ci), "credible_vs_zero": bool(credible), "direction": direction}


def build_frame(disc: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for day, d in disc.groupby(disc.index.date):
        rth = d.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue
        t = rth.index.time
        pre1550 = rth[t < pd.Timestamp("15:50").time()]
        win = rth.between_time("15:50", "16:00", inclusive="left")
        pre1000 = rth[t < pd.Timestamp("10:00").time()]
        if pre1550.empty or win.empty or pre1000.empty:
            continue
        rows.append({"date": day, "rth_range": float(rth["High"].max() - rth["Low"].min()),
                     "c1550": float(pre1550["Close"].iloc[-1]), "c1600": float(win["Close"].iloc[-1]),
                     "close_vol": float(win["Volume"].sum()), "o930": float(rth["Open"].iloc[0]),
                     "c1000": float(pre1000["Close"].iloc[-1])})
    f = pd.DataFrame(rows).set_index("date").sort_index()
    f["atr14"] = f["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    f["close_volume_vs_norm"] = f["close_vol"] / f["close_vol"].rolling(VOL_LOOKBACK, min_periods=VOL_LOOKBACK).mean().shift(1)
    f["close_move_vs_atr"] = (f["c1600"] - f["c1550"]) / f["atr14"]
    sgn = np.sign(f["close_move_vs_atr"]).replace(0, 1)
    f["next_open"] = -sgn * (f["o930"].shift(-1) - f["c1600"]) / f["atr14"]
    f["next_1000"] = -sgn * (f["c1000"].shift(-1) - f["c1600"]) / f["atr14"]
    return f.dropna(subset=["atr14", "close_volume_vs_norm", "close_move_vs_atr", "next_open", "next_1000"]).copy()


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 013 (Entry 11 / M1: cash-close move x close-window volume -> next-morning reversal)"); print("=" * 78)
    df, syn = load_price_data(context="market_behavior_discovery_scan_013.py")
    if syn:
        print("ABORT: synthetic data."); return
    f = build_frame(get_discovery_data(df))
    print(f"Discovery days usable: {len(f)}")
    edges = np.nanpercentile(f["close_volume_vs_norm"], [100 / 3, 200 / 3])
    f["bucket"] = pd.cut(f["close_volume_vs_norm"], bins=[-np.inf, edges[0], edges[1], np.inf], labels=TERCILE_LABELS)
    print(f"close-volume tercile edges: {edges[0]:.3f}, {edges[1]:.3f}")
    cells = {}
    for h in ["next_open", "next_1000"]:
        cells[h] = {}
        for b in TERCILE_LABELS:
            s = summarize(f.loc[f["bucket"] == b, h].tolist()); cells[h][b] = s
            print(f"  {h:>9} {b:>4}: n={s['n']} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
    hi, lo = cells["next_open"]["high"], cells["next_open"]["low"]
    verdict = "P1_PASS" if (hi["direction"] == "reversal" and not (lo["direction"] == "reversal" and lo["mean"] >= hi["mean"])) else "P1_FAIL"
    print(f"\nGATING (HIGH close-volume, open horizon): {verdict}")
    high = f[f["bucket"] == "high"]
    p2 = {}
    if len(high) >= 10:
        med = high["close_move_vs_atr"].abs().median()
        p2 = {"large_close_move": summarize(high.loc[high["close_move_vs_atr"].abs() >= med, "next_open"].tolist()),
              "small_close_move": summarize(high.loc[high["close_move_vs_atr"].abs() < med, "next_open"].tolist())}
        print(f"  P2 large n={p2['large_close_move']['n']} mean={p2['large_close_move']['mean']:+.4f} {p2['large_close_move']['direction']} | small n={p2['small_close_move']['n']} mean={p2['small_close_move']['mean']:+.4f} {p2['small_close_move']['direction']}")
    out = {"state_vars": ["close_volume_vs_norm", "close_move_vs_atr"], "tercile_edges_volume": [float(edges[0]), float(edges[1])], "n_days": int(len(f)),
           "cells": cells, "gating_verdict": verdict, "p2_size_dependence_within_high": p2}
    (DATA_DIR / "market_behavior_discovery_scan_013_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_013_results.json'}")


if __name__ == "__main__":
    main()
