"""
market_behavior_discovery_scan_030.py
========================================

Scan 030. Draws Entry 27 (map anchor M23): London FX session-open
volatility burst, 6E (open scope -- signal and trade both in 6E).
Mechanism doc written BEFORE this scan:
research/mechanisms/london-open-volatility-6e-m23.md.

Frozen scope (doc Sections 4-5), Discovery only (2015-01 -> 2021-10-03).
This is an UNCONDITIONAL, daily-recurring claim -- no event-date list,
fires every Discovery-slice trading day (largest-n entry in the open-scope
family so far).

FOUR pre-registered cells (scan_030_2026-09-13), 1 gating:
  1. London-open hour (03:00-04:00 ET) |return|/ATR14 mean MINUS
     unconditional RTH-equivalent-hour |return|/ATR14 mean, block CI  <== GATING (P1)
  2. pre-London hour (02:00-03:00 ET) |return|/ATR14 mean MINUS
     unconditional mean, block CI (secondary, reported UNPINNED --
     specificity check per doc Section 2)
  3. unconditional RTH-equivalent-hour |return|/ATR14 distribution mean (NULL 1 ref)
  4. share of the London-open hour's |return| in the first minute
     (03:00-03:01 ET) (KILL)

RTH-equivalent hours for the unconditional pool: 09:30-16:00 ET, six
1-hour bins, same convention as M20/M21/scan_025. ATR14 = trailing-14-
session mean of the 09:30-16:00 daily range, shifted by 1 (no lookahead),
matching M21's convention so the two families stay comparable.

Block bootstrap (block=10) is the CI of record. One shot. No new cells,
no retuning after seeing results.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_030.py
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
ATR_WINDOW = 14; BLOCK = 10; N_BOOT = 3000; SEED = 20260913


def block_ci(v, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < BLOCK * 3:
        return [float("nan"), float("nan")]
    means = _block_means(v, BLOCK, N_BOOT, np.random.default_rng(SEED))
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


def cell(v):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    ci = block_ci(v); cred = (not np.isnan(ci[0])) and ((ci[0] > 0) or (ci[1] < 0))
    return {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": ci,
            "credible_vs_zero": bool(cred), "direction": "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")}


def diff_ci_block_vs_iid(sample_arr, uncond_arr):
    """Block-bootstrap the sequential (one-per-day) sample series; iid-resample
    the pooled unconditional series. Same convention as scan_025's decision-vs-
    unconditional diff."""
    diff = float(sample_arr.mean() - uncond_arr.mean())
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(N_BOOT):
        if len(sample_arr) >= BLOCK:
            nb = int(np.ceil(len(sample_arr) / BLOCK))
            starts = rng.integers(0, max(len(sample_arr) - BLOCK, 1), size=nb)
            sboot = np.concatenate([sample_arr[s:s + BLOCK] for s in starts])[:len(sample_arr)]
        else:
            sboot = rng.choice(sample_arr, size=len(sample_arr), replace=True)
        uboot = rng.choice(uncond_arr, size=len(uncond_arr), replace=True)
        diffs.append(sboot.mean() - uboot.mean())
    diffs = np.sort(diffs)
    ci = [float(diffs[int(0.05 * N_BOOT)]), float(diffs[int(0.95 * N_BOOT)])]
    return diff, ci


def hourly_abs_returns(g_rth, atr):
    """All RTH-equivalent clock hours' |return|/ATR for one session's bars."""
    out = []
    for hstart in ["09:30", "10:30", "11:30", "12:30", "13:30", "14:30"]:
        hend = str(int(hstart[:2]) + 1).zfill(2) + hstart[2:]
        sub = g_rth.between_time(hstart, hend, inclusive="left")
        if len(sub) < 30:
            continue
        r = abs(float(sub["Close"].iloc[-1] - sub["Open"].iloc[0])) / atr
        out.append(r)
    return out


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 030 (Entry 27 / map M23: London-open volatility, 6E)"); print("=" * 78)
    fx_all, synth = load_price_data(context="market_behavior_discovery_scan_030.py", symbol="6E")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(fx_all)

    daily_rows = []
    for day, g in disc.groupby(disc.index.date):
        rth_equiv = g.between_time("09:30", "16:00", inclusive="left")
        if len(rth_equiv) < 200:
            continue
        daily_rows.append({"date": pd.Timestamp(day), "rth_range": float(rth_equiv["High"].max() - rth_equiv["Low"].min())})
    daily = pd.DataFrame(daily_rows).set_index("date").sort_index()
    daily["atr14"] = daily["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    atr_by_date = daily["atr14"].to_dict()

    london_abs, prelondon_abs, unconditional_abs, kill_rows = [], [], [], []
    days_used, days_skipped = 0, 0
    for day, g in disc.groupby(disc.index.date):
        ts = pd.Timestamp(day)
        rth_equiv = g.between_time("09:30", "16:00", inclusive="left")
        atr = atr_by_date.get(ts)
        if atr is None or np.isnan(atr) or len(rth_equiv) < 200:
            continue
        london = g.between_time("03:00", "04:00", inclusive="left")
        prelondon = g.between_time("02:00", "03:00", inclusive="left")
        first_min = g.between_time("03:00", "03:01", inclusive="left")
        if london.empty or prelondon.empty or first_min.empty:
            days_skipped += 1; continue
        days_used += 1
        unconditional_abs.extend(hourly_abs_returns(rth_equiv, atr))
        lon_ret = (float(london["Close"].iloc[-1]) - float(london["Open"].iloc[0])) / atr
        pre_ret = (float(prelondon["Close"].iloc[-1]) - float(prelondon["Open"].iloc[0])) / atr
        fm_ret = (float(first_min["Close"].iloc[-1]) - float(first_min["Open"].iloc[0])) / atr
        london_abs.append(abs(lon_ret)); prelondon_abs.append(abs(pre_ret))
        kill_rows.append({"lon_abs": abs(lon_ret), "fm_abs": abs(fm_ret)})

    print(f"Discovery days usable (London hour + pre-London hour + first-minute bars present): {days_used}; skipped: {days_skipped}")

    lon_arr = np.array(london_abs); pre_arr = np.array(prelondon_abs); uncond_arr = np.array(unconditional_abs)
    lon_diff, lon_ci = diff_ci_block_vs_iid(lon_arr, uncond_arr)
    pre_diff, pre_ci = diff_ci_block_vs_iid(pre_arr, uncond_arr)
    p1_credible = lon_ci[0] > 0

    cells = {
        "1_london_minus_unconditional_GATING": {"london_mean": float(lon_arr.mean()), "unconditional_mean": float(uncond_arr.mean()),
                                                  "diff": lon_diff, "ci_90": lon_ci, "credible_positive": bool(p1_credible),
                                                  "n_days": days_used, "n_unconditional_hours": int(len(uncond_arr))},
        "2_prelondon_minus_unconditional_SECONDARY_UNPINNED": {"prelondon_mean": float(pre_arr.mean()), "unconditional_mean": float(uncond_arr.mean()),
                                                                 "diff": pre_diff, "ci_90": pre_ci, "credible_positive": bool(pre_ci[0] > 0),
                                                                 "n_days": days_used},
        "3_unconditional_hourly_abs_ref": cell(list(uncond_arr)),
    }

    fm_abs = np.array([r["fm_abs"] for r in kill_rows]); lon_abs_for_fm = np.array([r["lon_abs"] for r in kill_rows])
    fm_share = float(fm_abs.mean() / lon_abs_for_fm.mean()) if len(kill_rows) and lon_abs_for_fm.mean() else float("nan")
    cells["4_first_minute_share_KILL"] = {"share": fm_share, "kill": bool((not np.isnan(fm_share)) and fm_share > 0.5)}

    print("\nCells:")
    c1 = cells["1_london_minus_unconditional_GATING"]
    print(f"  1_GATING  london_mean={c1['london_mean']:.4f} unconditional_mean={c1['unconditional_mean']:.4f} "
          f"diff={c1['diff']:+.4f} ci_90=({c1['ci_90'][0]:+.4f},{c1['ci_90'][1]:+.4f}) credible_positive={c1['credible_positive']} n_days={c1['n_days']}")
    c2 = cells["2_prelondon_minus_unconditional_SECONDARY_UNPINNED"]
    print(f"  2_SECONDARY prelondon_mean={c2['prelondon_mean']:.4f} unconditional_mean={c2['unconditional_mean']:.4f} "
          f"diff={c2['diff']:+.4f} ci_90=({c2['ci_90'][0]:+.4f},{c2['ci_90'][1]:+.4f}) credible_positive={c2['credible_positive']}")
    c3 = cells["3_unconditional_hourly_abs_ref"]
    print(f"  3_unconditional_hourly_abs_ref n={c3['n']:>5} mean={c3['mean']:+.4f} ci_90=({c3['ci_90'][0]:+.4f},{c3['ci_90'][1]:+.4f}) {c3['direction']}")
    k4 = cells["4_first_minute_share_KILL"]
    print(f"  4_first_minute_share      share={k4['share']:+.3f} KILL={k4['kill']}")

    if k4["kill"] and c1["credible_positive"]:
        verdict, note = "KILLED", "London-open-hour response is concentrated in the 03:00 first-minute print -- a stale-quote/thin-liquidity artifact, not a genuine hour-long liquidity effect. Closes per kill rule, even though magnitude alone was confirmed."
    elif c1["credible_positive"]:
        if c2["credible_positive"]:
            verdict, note = "P1_PASS_AMBIGUOUS", "London-open hour credibly exceeds the unconditional baseline, but so does the pre-London hour -- suggests broader overnight-session elevation (overnight-coil territory) rather than a genuine session-boundary discontinuity specific to the London open. Advance to Statistical with this caveat disclosed, not a clean pass."
        else:
            verdict, note = "P1_PASS", "London-open hour credibly exceeds the unconditional hourly baseline and the pre-London hour does not -- concentrated at the session boundary as the mechanism predicts, and not a pure first-minute print artifact. Advance to Statistical per pipeline order."
    else:
        verdict, note = "P1_FAIL", "London-open hour |return| not credibly larger than the unconditional hourly baseline. Entry closes on falsifier (a)."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_days_used": days_used, "n_days_skipped": days_skipped, "cells": cells, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_030_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_030_results.json'}")


if __name__ == "__main__":
    main()
