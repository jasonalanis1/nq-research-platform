"""
market_behavior_discovery_scan_021.py
========================================

Scan 021. Draws Entry 20 (map anchor M16): market intraday momentum
(Gao, Han, Li, Zhou 2018 JFE), NQ. Mechanism doc written BEFORE this scan:
research/mechanisms/market-intraday-momentum-m16.md.

Frozen scope (doc Section 7), Discovery only:
  R_first30 = prior session 16:00 close -> 10:00 ET close, / ATR14
  R_mid     = 10:00 -> 15:30, / ATR14
  R_last30  = 15:30 -> 16:00, / ATR14
  terciles of R_first30 frozen on Discovery.
TEN pre-registered cells (scan_021_2026-09-12):
  1. sign-adjusted mean(R_last30 | first30 in TOP or BOTTOM tercile),
     block CI                                            <== GATING (P1)
  2. mean(R_last30 | MIDDLE tercile)                    (NULL 1, reported)
  3. unconditional mean(R_last30)                       (NULL 1, reported)
  4. OLS coefficient on R_first30 with R_mid included, bootstrap CI (P2)
  5. OLS coefficient on R_mid                           (P2)
  6a/6b. cell 1 on high- vs low-ATR14-tercile sessions (P3)
  7a/7b. cell 1 on Discovery halves                     (P4)
  8. share of cell 1 in the 15:59->16:00 bar            (KILL rule)
Block bootstrap (block=10) is the CI of record. Calendar days with only
Globex bars are not sessions and do not break the chain (Scan 020 lesson).
One shot. No new cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_021.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
from baseline_relative import _block_means  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ATR_WINDOW = 14; BLOCK = 10; N_BOOT = 3000; SEED = 20260912


def block_ci(v, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < BLOCK * 3:
        return [float("nan"), float("nan")]
    means = _block_means(v, BLOCK, N_BOOT, np.random.default_rng(SEED))
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


def cell(v):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    ci = block_ci(v); cred = (ci[0] > 0) or (ci[1] < 0)
    return {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": ci,
            "credible_vs_zero": bool(cred), "direction": "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")}


def ols_block_ci(y, X, col, rng):
    """Bootstrap the OLS coefficient for column `col` by resampling blocks of rows."""
    n = len(y); nb = int(np.ceil(n / BLOCK)); coefs = np.empty(N_BOOT)
    Xc = np.column_stack([np.ones(n), X])
    for i in range(N_BOOT):
        starts = rng.integers(0, max(n - BLOCK, 1), size=nb)
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in starts])[:n]
        idx = idx[idx < n]
        b, *_ = np.linalg.lstsq(Xc[idx], y[idx], rcond=None)
        coefs[i] = b[col + 1]
    b, *_ = np.linalg.lstsq(Xc, y, rcond=None)
    return float(b[col + 1]), [float(np.percentile(coefs, 5)), float(np.percentile(coefs, 95))]


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 021 (Entry 20 / M16: market intraday momentum)"); print("=" * 78)
    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_021.py", symbol="NQ")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(nq_all)

    rows = []; dropped = 0; prior_close = None
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue
        b0930 = g.between_time("09:30", "09:30"); b1000 = g.between_time("09:59", "09:59")
        b1530 = g.between_time("15:29", "15:29"); b1559 = g.between_time("15:59", "15:59"); b1558 = g.between_time("15:58", "15:58")
        if any(b.empty for b in (b0930, b1000, b1530, b1559, b1558)) or len(rth) < 200:
            dropped += 1; prior_close = None; continue
        c1000 = float(b1000["Close"].iloc[-1]); c1530 = float(b1530["Close"].iloc[-1])
        c1558 = float(b1558["Close"].iloc[-1]); c1559 = float(b1559["Close"].iloc[-1])
        rows.append({"date": pd.Timestamp(day), "prior_close": prior_close, "c1000": c1000, "c1530": c1530,
                     "c1558": c1558, "c1559": c1559, "rth_range": float(rth["High"].max() - rth["Low"].min())})
        prior_close = c1559
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["atr14"] = d["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    d = d.dropna(subset=["prior_close", "atr14"])
    d["first30"] = (d["c1000"] - d["prior_close"]) / d["atr14"]
    d["mid"] = (d["c1530"] - d["c1000"]) / d["atr14"]
    d["last30"] = (d["c1559"] - d["c1530"]) / d["atr14"]
    d["last_print"] = (d["c1559"] - d["c1558"]) / d["atr14"]   # the 15:59->16:00 bar
    print(f"Sessions usable: {len(d)}; dropped: {dropped}")

    lo, hi = d["first30"].quantile([1 / 3, 2 / 3]).tolist()
    d["terc"] = np.where(d["first30"] < lo, "BOTTOM", np.where(d["first30"] < hi, "MIDDLE", "TOP"))
    ext = d[d["terc"] != "MIDDLE"].copy()
    ext["sa_last30"] = np.sign(ext["first30"]) * ext["last30"]
    ext["sa_print"] = np.sign(ext["first30"]) * ext["last_print"]
    print(f"Frozen tercile edges on first30: {lo:+.4f} / {hi:+.4f}")

    rng = np.random.default_rng(SEED)
    X = d[["first30", "mid"]].values; y = d["last30"].values
    b1, ci1 = ols_block_ci(y, X, 0, rng); b2, ci2 = ols_block_ci(y, X, 1, np.random.default_rng(SEED + 1))
    atr_lo, atr_hi = d["atr14"].quantile([1 / 3, 2 / 3]).tolist()
    half = len(ext) // 2
    cells = {
        "1_extreme_signadj_last30_GATING": cell(ext["sa_last30"]),
        "2_middle_last30": cell(d.loc[d["terc"] == "MIDDLE", "last30"]),
        "3_unconditional_last30": cell(d["last30"]),
        "4_ols_first30_with_mid": {"coef": b1, "ci_90": ci1, "credible_positive": bool(ci1[0] > 0)},
        "5_ols_mid": {"coef": b2, "ci_90": ci2, "credible_positive": bool(ci2[0] > 0)},
        "6a_extreme_highATR": cell(ext.loc[ext["atr14"] >= atr_hi, "sa_last30"]),
        "6b_extreme_lowATR": cell(ext.loc[ext["atr14"] < atr_lo, "sa_last30"]),
        "7a_extreme_first_half": cell(ext["sa_last30"].iloc[:half]),
        "7b_extreme_second_half": cell(ext["sa_last30"].iloc[half:]),
    }
    g = cells["1_extreme_signadj_last30_GATING"]
    print_share = float(ext["sa_print"].mean() / g["mean"]) if g["mean"] else float("nan")
    cells["8_closing_print_share_KILL"] = {"print_mean": float(ext["sa_print"].mean()), "share": print_share,
                                            "kill": bool(abs(print_share) > 0.5) if not np.isnan(print_share) else False}
    print("\nCells (ATR units, block bootstrap 90% CI):")
    for k, s in cells.items():
        if "ci_90" in s and "n" in s:
            print(f"  {k:<34} n={s['n']:>4} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
        elif "coef" in s:
            print(f"  {k:<34} coef={s['coef']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) credible_pos={s['credible_positive']}")
    k8 = cells["8_closing_print_share_KILL"]
    print(f"  8_closing_print_share            print_mean={k8['print_mean']:+.4f} share={k8['share']:+.3f} KILL={k8['kill']}")

    if k8["kill"] and g["direction"] == "positive":
        verdict, note = "KILLED", "Response concentrated in the 15:59->16:00 bar. Family terminates per kill rule (c)."
    elif g["direction"] != "positive":
        verdict, note = "P1_FAIL", "Sign-adjusted last-30 after an extreme first-30 not credibly positive. Closes on falsifier (a)."
    elif not cells["4_ols_first30_with_mid"]["credible_positive"]:
        verdict, note = "P1_PASS_BUT_CONFOUNDED", "Gate passes but the first-30 coefficient is not credibly positive once the mid-day return is included: day-so-far momentum (M13 territory), not Gao et al. Recorded confounded; closes on falsifier (b)."
    else:
        verdict, note = "P1_PASS", "Gate passes and the first-30 coefficient survives the mid-day control. Advance to Statistical per pipeline order."
    print(f"\nVERDICT: {verdict}\n  {note}")
    out = {"n_sessions": int(len(d)), "dropped": int(dropped), "tercile_edges": [lo, hi], "cells": cells, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_021_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_021_results.json'}")


if __name__ == "__main__":
    main()
