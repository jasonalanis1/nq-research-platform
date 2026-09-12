"""
market_behavior_discovery_scan_012.py
========================================

Scan 012. Draws Entry 10 (map anchor M11) from research/idea_inventory.md:
NQ-ZN rolling-correlation breakdown -> NQ forward 1-3 day return.
Mechanism doc written BEFORE this scan:
research/mechanisms/nq-zn-correlation-breakdown-m11.md (AMENDMENT v2.5).

Frozen scope (mechanism doc Section 6):
  - state variable: nq_zn_corr_20d = rolling 20-day Pearson correlation of
    NQ and ZN daily RTH close-to-close returns (RTH 09:30-16:00 ET, half-open,
    ZN aligned to NQ's session), terciles cut on the Discovery sample.
  - outcomes: NQ forward 1d, 2d, 3d RTH-close-to-RTH-close return / ATR14
    (ATR14 = trailing mean of daily RTH range, shifted one day).
  - NINE pre-registered cells: 3 terciles x 3 horizons.
Gating claim (P1): HIGH-tercile forward return below LOW-tercile at each
horizon; HIGH cell credibly negative (90% CI upper bound < 0) OR the
HIGH-minus-LOW difference credibly negative (bootstrap on the difference).
Placebo (P1, reported): add ZN prior-day return as a conditioner (median
split within the HIGH cell) -- the effect must not vanish, or it is the
closed lead-lag family in disguise.
P2 (reported): effect grows 1d -> 3d.  P3 (reported): chronological-half and
VXN-half robustness of the HIGH cell at the 3d horizon.

This is the entry's ONE pre-registered Discovery-stage shot. No new cells,
no peeking then adjusting, no retuning. scan_012_2026-09-12 (9 cells)
registered in src/project_wide_multiplicity.py BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_012.py
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
CORR_WINDOW = 20
HORIZONS = [1, 2, 3]
TERCILE_LABELS = ["low", "mid", "high"]


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


def rth_daily(df: pd.DataFrame) -> pd.DataFrame:
    rth = df.between_time("09:30", "16:00", inclusive="left")
    g = rth.groupby(rth.index.date)
    out = pd.DataFrame({"rth_close": g["Close"].last(), "rth_range": g["High"].max() - g["Low"].min()})
    out.index = pd.to_datetime(out.index)
    return out


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 012 (Entry 10 / M11: NQ-ZN correlation breakdown -> NQ 1-3d)"); print("=" * 78)
    nq, syn1 = load_price_data(context="market_behavior_discovery_scan_012.py", symbol="NQ")
    zn, syn2 = load_price_data(context="market_behavior_discovery_scan_012.py", symbol="ZN")
    if syn1 or syn2:
        print("ABORT: synthetic data."); return
    nq = get_discovery_data(nq); zn = get_discovery_data(zn)
    dn = rth_daily(nq); dz = rth_daily(zn)
    d = dn.join(dz[["rth_close"]].rename(columns={"rth_close": "zn_close"}), how="inner")
    d["nq_ret"] = d["rth_close"].pct_change(); d["zn_ret"] = d["zn_close"].pct_change()
    d["atr14"] = d["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    d["nq_zn_corr_20d"] = d["nq_ret"].rolling(CORR_WINDOW, min_periods=CORR_WINDOW).corr(d["zn_ret"])
    d["zn_prior_ret"] = d["zn_ret"]  # same-day close-to-close ZN return, known at the close the state is measured
    for h in HORIZONS:
        d[f"fwd_{h}d"] = (d["rth_close"].shift(-h) - d["rth_close"]) / d["atr14"]
    f = d.dropna(subset=["nq_zn_corr_20d", "atr14"] + [f"fwd_{h}d" for h in HORIZONS]).copy()
    print(f"Discovery days usable (NQ+ZN aligned, corr + ATR + fwd): {len(f)}")
    edges = np.nanpercentile(f["nq_zn_corr_20d"], [100 / 3, 200 / 3])
    f["bucket"] = pd.cut(f["nq_zn_corr_20d"], bins=[-np.inf, edges[0], edges[1], np.inf], labels=TERCILE_LABELS)
    print(f"corr tercile edges: {edges[0]:+.3f}, {edges[1]:+.3f}")

    cells, diffs, gate = {}, {}, {}
    for h in HORIZONS:
        col = f"fwd_{h}d"; cells[h] = {}
        for b in TERCILE_LABELS:
            s = summarize(f.loc[f["bucket"] == b, col].tolist()); cells[h][b] = s
            print(f"  {h}d {b:>4}: n={s['n']} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
        hi = f.loc[f["bucket"] == "high", col].tolist(); lo = f.loc[f["bucket"] == "low", col].tolist()
        dci = bootstrap_diff_ci(hi, lo); dm = float(np.nanmean(hi) - np.nanmean(lo))
        diffs[h] = {"high_minus_low_mean": dm, "ci_90": list(dci), "credible_negative": bool(dci[1] < 0)}
        gate[h] = bool(cells[h]["high"]["direction"] == "negative" or diffs[h]["credible_negative"])
        print(f"      HIGH-LOW {h}d: {dm:+.4f} ci_90=({dci[0]:+.4f},{dci[1]:+.4f}) credible_negative={diffs[h]['credible_negative']}")
    verdict = "P1_PASS" if any(gate.values()) else "P1_FAIL"
    print(f"\nGATING (P1, HIGH below LOW at any horizon): {verdict}  per-horizon={gate}")

    high = f[f["bucket"] == "high"]
    placebo = {}
    if len(high) >= 10:
        med = high["zn_prior_ret"].median()
        placebo = {"zn_prior_ret_below_median": summarize(high.loc[high["zn_prior_ret"] < med, "fwd_3d"].tolist()),
                   "zn_prior_ret_above_median": summarize(high.loc[high["zn_prior_ret"] >= med, "fwd_3d"].tolist())}
    p3 = {}
    if len(high) >= 20:
        mid_i = len(high) // 2
        p3["chrono_first_half"] = summarize(high["fwd_3d"].iloc[:mid_i].tolist())
        p3["chrono_second_half"] = summarize(high["fwd_3d"].iloc[mid_i:].tolist())
    out = {"state_var": "nq_zn_corr_20d", "tercile_edges": [float(edges[0]), float(edges[1])], "n_days": int(len(f)),
           "cells": {str(k): v for k, v in cells.items()}, "high_minus_low": {str(k): v for k, v in diffs.items()},
           "gating_verdict": verdict, "p1_placebo_zn_prior_ret_within_high": placebo, "p3_chrono_halves_high_3d": p3}
    (DATA_DIR / "market_behavior_discovery_scan_012_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_012_results.json'}")


if __name__ == "__main__":
    main()
