"""
market_behavior_discovery_scan_011.py
========================================

Scan 011. Draws Entry 9 (map anchor M10) from research/idea_inventory.md:
midday DIRECTIONAL retrace of the morning move. Mechanism doc written
BEFORE this scan: research/mechanisms/midday-directional-retrace-m10.md
(AMENDMENT v2.5). Nothing here re-derives the claim.

Frozen scope (from the mechanism doc, Section 6):
  - state variable: morning_move_vs_atr = (11:30 close - 9:30 open) / ATR14,
    signed; terciles by |value| cut on the Discovery sample.
  - outcomes (two horizons): 11:30 -> 13:30 ET return, and 11:30 -> 16:00 ET
    return, in ATR14 units, SIGN-ADJUSTED so that a move against the morning
    direction (a retrace) is POSITIVE.
  - window boundaries are half-open [start, end) per the KNOWN FAILURE MODE
    (between_time is inclusive at both ends).
  - SIX pre-registered cells: 3 |magnitude| terciles x 2 horizons.

Gating prediction (P1 in the doc): HIGH |morning-move| tercile, lull
horizon (11:30->13:30) -> mean sign-adjusted return > 0, credible (90% CI
lower bound > 0). Falsifiers: no positive relation in the HIGH tercile; or a
relation of the same size in the LOW tercile (not about move size); or the
effect living in 13:30->16:00 instead of the lull (P1 concentration fails).

Reported, not gated:
  P2 (thinning): within the HIGH tercile, split by lull-window (11:30-13:30)
     volume vs its trailing-20-day norm -- retrace predicted LARGER on
     low-lull-volume days. Reversed -> information, not liquidity.
  P3 (separability): within the HIGH tercile, split by the validated
     narrow-midday flag (volatility_conditioning.build_midday_afternoon_frame)
     -- retrace must hold on BOTH narrow and not-narrow days.

This is the entry's ONE pre-registered Discovery-stage shot. No new cells,
no peeking then adjusting, no retuning. scan_011_2026-09-12 (6 cells) was
registered in src/project_wide_multiplicity.py BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_011.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from volatility_conditioning import build_midday_afternoon_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_WINDOW = 14
VOL_LOOKBACK = 20
TERCILE_LABELS = ["low", "mid", "high"]
HORIZONS = {"lull_1130_1330": ("11:30", "13:30"), "to_close_1130_1600": ("11:30", "16:00")}


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = rng.choice(v, size=(n_bootstrap, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def summarize(vals: list) -> dict:
    n = len(vals)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": [float("nan"), float("nan")], "credible_vs_zero": False, "direction": "insufficient_n"}
    m = float(np.mean(vals)); ci = bootstrap_mean_ci(vals)
    credible = ci[0] > 0 or ci[1] < 0
    direction = "retrace" if (credible and ci[0] > 0) else ("continuation" if (credible and ci[1] < 0) else "null")
    return {"n": n, "mean": m, "ci_90": list(ci), "credible_vs_zero": bool(credible), "direction": direction}


def _px_at(day_df: pd.DataFrame, t: str, which: str) -> float | None:
    """Half-open convention: 'open' at t = first bar with time >= t; 'close'
    at t = last bar with time < t."""
    tt = pd.Timestamp(t).time()
    times = day_df.index.time
    if which == "open":
        sel = day_df[times >= tt]
        return float(sel["Open"].iloc[0]) if len(sel) else None
    sel = day_df[times < tt]
    return float(sel["Close"].iloc[-1]) if len(sel) else None


def build_frame(disc: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for day, d in disc.groupby(disc.index.date):
        rth = d.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue
        o930 = _px_at(rth, "09:30", "open"); c1130 = _px_at(rth, "11:30", "close")
        c1330 = _px_at(rth, "13:30", "close"); c1600 = _px_at(rth, "16:00", "close")
        lull = rth.between_time("11:30", "13:30", inclusive="left")
        rows.append({"date": day, "rth_range": float(rth["High"].max() - rth["Low"].min()),
                     "o930": o930, "c1130": c1130, "c1330": c1330, "c1600": c1600,
                     "lull_volume": float(lull["Volume"].sum()) if "Volume" in lull and len(lull) else np.nan})
    f = pd.DataFrame(rows).set_index("date").sort_index()
    f["atr14"] = f["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    f["lull_volume_norm"] = f["lull_volume"] / f["lull_volume"].rolling(VOL_LOOKBACK, min_periods=VOL_LOOKBACK).mean().shift(1)
    f = f.dropna(subset=["o930", "c1130", "c1330", "c1600", "atr14"]).copy()
    f["morning_move_vs_atr"] = (f["c1130"] - f["o930"]) / f["atr14"]
    f["abs_morning"] = f["morning_move_vs_atr"].abs()
    sgn = np.sign(f["morning_move_vs_atr"]).replace(0, 1)
    f["lull_1130_1330"] = -sgn * (f["c1330"] - f["c1130"]) / f["atr14"]
    f["to_close_1130_1600"] = -sgn * (f["c1600"] - f["c1130"]) / f["atr14"]
    return f


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 011 (Entry 9 / M10: midday directional retrace of the morning move)"); print("=" * 78)
    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_011.py")
    if is_synthetic:
        print("ABORT: only synthetic data available."); return
    disc = get_discovery_data(df)
    f = build_frame(disc)
    mid = build_midday_afternoon_frame(disc)[["narrow_midday"]]
    f = f.join(mid, how="left")
    print(f"Discovery days usable: {len(f)}")
    edges = np.nanpercentile(f["abs_morning"], [100 / 3, 200 / 3])
    f["bucket"] = pd.cut(f["abs_morning"], bins=[-np.inf, edges[0], edges[1], np.inf], labels=TERCILE_LABELS)

    cells = {}
    for h in HORIZONS:
        cells[h] = {}
        for b in TERCILE_LABELS:
            s = summarize(f.loc[f["bucket"] == b, h].dropna().tolist())
            cells[h][b] = s
            print(f"  {h:>20} {b:>4}: n={s['n']} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")

    gate = cells["lull_1130_1330"]["high"]
    p1_concentrated = gate["credible_vs_zero"] and gate["direction"] == "retrace"
    low_same = cells["lull_1130_1330"]["low"]
    verdict = "P1_PASS" if p1_concentrated and not (low_same["credible_vs_zero"] and low_same["direction"] == "retrace" and low_same["mean"] >= gate["mean"]) else "P1_FAIL"
    print(f"\nGATING (HIGH tercile, lull horizon): {verdict}")

    high = f[f["bucket"] == "high"]
    p2 = {}
    hv = high.dropna(subset=["lull_volume_norm"])
    if len(hv) >= 10:
        med = hv["lull_volume_norm"].median()
        p2 = {"low_lull_volume": summarize(hv.loc[hv["lull_volume_norm"] < med, "lull_1130_1330"].tolist()),
              "high_lull_volume": summarize(hv.loc[hv["lull_volume_norm"] >= med, "lull_1130_1330"].tolist())}
        print(f"  P2 low-lull-vol n={p2['low_lull_volume']['n']} mean={p2['low_lull_volume']['mean']:+.4f} {p2['low_lull_volume']['direction']} | high-lull-vol n={p2['high_lull_volume']['n']} mean={p2['high_lull_volume']['mean']:+.4f} {p2['high_lull_volume']['direction']}")
    p3 = {}
    hn = high.dropna(subset=["narrow_midday"])
    if len(hn) >= 10:
        p3 = {"narrow_midday": summarize(hn.loc[hn["narrow_midday"] == True, "lull_1130_1330"].tolist()),
              "not_narrow": summarize(hn.loc[hn["narrow_midday"] == False, "lull_1130_1330"].tolist())}
        print(f"  P3 narrow n={p3['narrow_midday']['n']} mean={p3['narrow_midday']['mean']:+.4f} {p3['narrow_midday']['direction']} | not-narrow n={p3['not_narrow']['n']} mean={p3['not_narrow']['mean']:+.4f} {p3['not_narrow']['direction']}")

    out = {"state_var": "morning_move_vs_atr", "tercile_edges_abs": [float(edges[0]), float(edges[1])], "cells": cells,
           "gating_verdict": verdict, "p2_lull_volume": p2, "p3_narrow_midday_separability": p3, "n_days": int(len(f))}
    out_path = DATA_DIR / "market_behavior_discovery_scan_011_results.json"
    out_path.write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
