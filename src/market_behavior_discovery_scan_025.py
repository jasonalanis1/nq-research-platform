"""
market_behavior_discovery_scan_025.py
========================================

Scan 025. Draws Entry 25 (map anchor M21): ECB Governing Council rate
decision, pre/post-release volatility, 6E (open scope -- signal and
trade both in 6E). Mechanism doc written BEFORE this scan:
research/mechanisms/ecb-decision-day-volatility-6e-m21.md.

Frozen scope (doc Section 7), Discovery only (2015-01 -> 2021-10.03).
Event = ECB Governing Council press-conference meeting dates from
data/ecb_press_conference_dates_2015_2021.csv (n=54, fixed public
schedule since 2015 -- source: the Jarocinski-Karadi ECB monetary
policy shocks dataset, a public academic dataset indexed by Governing
Council meeting date, github.com/marekjarocinski/jkshocks_update_ecb).
Fetched fresh this cycle: the prior cycle's WebFetch attempt hit a
session-level rate limit before a usable historical source was found;
this cycle's fetch succeeded on a different, more suitable source (a
raw academic dataset CSV, not the ECB's own JS-rendered pages).

SIX pre-registered cells (scan_025_2026-09-13), 1 gating:
  1. decision-hour (08:30-09:30 ET) |return|/ATR14 mean MINUS
     unconditional RTH-equivalent-hour |return|/ATR14 mean, block CI  <== GATING (P1)
  2. decision-hour signed mean, block CI (P2, reported, unpinned sign)
  3. unconditional RTH-equivalent-hour |return|/ATR14 distribution mean (NULL 1 ref)
  4. share of the decision-hour |return| in the 07:45-07:46 statement-print bar (KILL)
  5-6. cell 1 on Discovery halves (P4, 2 cells)

RTH-equivalent hours (per the doc's own phrase, same convention as
M20/scan_023): 09:30-16:00 ET, six 1-hour bins, used for the
unconditional pool. Decision-hour (08:30-09:30 ET) is evaluated
directly on ECB dates using the same day's ATR14.

Block bootstrap (block=10) is the CI of record. One shot. No new
cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_025.py
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


def ecb_dates():
    df = pd.read_csv(DATA_DIR / "ecb_press_conference_dates_2015_2021.csv")
    dates = pd.to_datetime(df["Meeting Date"])
    return sorted(pd.Timestamp(d.date()) for d in dates)


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
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 025 (Entry 25 / map M21: ECB decision volatility, 6E)"); print("=" * 78)
    fx_all, synth = load_price_data(context="market_behavior_discovery_scan_025.py", symbol="6E")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(fx_all)

    daily_rows = []
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("07:30", "16:00", inclusive="left")
        if rth.empty:
            continue
        rth_equiv = g.between_time("09:30", "16:00", inclusive="left")
        if len(rth_equiv) < 200:
            continue
        daily_rows.append({"date": pd.Timestamp(day), "rth_range": float(rth_equiv["High"].max() - rth_equiv["Low"].min())})
    daily = pd.DataFrame(daily_rows).set_index("date").sort_index()
    daily["atr14"] = daily["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    atr_by_date = daily["atr14"].to_dict()

    dates = ecb_dates()
    print(f"ECB press-conference dates loaded (Discovery window): {len(dates)}")

    decision_signed, decision_abs, unconditional_abs, kill_rows = [], [], [], []
    dates_used, dates_skipped = 0, 0
    for day, g in disc.groupby(disc.index.date):
        ts = pd.Timestamp(day)
        rth_equiv = g.between_time("09:30", "16:00", inclusive="left")
        atr = atr_by_date.get(ts)
        if atr is None or np.isnan(atr) or len(rth_equiv) < 200:
            continue
        unconditional_abs.extend(hourly_abs_returns(rth_equiv, atr))
        if ts not in dates:
            continue
        dec = g.between_time("08:30", "09:30")
        first_min = g.between_time("07:45", "07:46")
        if dec.empty or first_min.empty:
            dates_skipped += 1; continue
        dates_used += 1
        dec_ret = (float(dec["Close"].iloc[-1]) - float(dec["Open"].iloc[0])) / atr
        fm_ret = (float(first_min["Close"].iloc[-1]) - float(first_min["Open"].iloc[0])) / atr
        decision_signed.append(dec_ret); decision_abs.append(abs(dec_ret))
        kill_rows.append({"dec_abs": abs(dec_ret), "fm_abs": abs(fm_ret)})

    print(f"ECB dates usable (decision-hour + statement-print bars present): {dates_used}; skipped: {dates_skipped}")

    half = dates_used // 2
    dec_abs_arr = np.array(decision_abs)
    uncond_arr = np.array(unconditional_abs)
    diff = dec_abs_arr.mean() - uncond_arr.mean()
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(N_BOOT):
        if len(dec_abs_arr) >= BLOCK:
            nb = int(np.ceil(len(dec_abs_arr) / BLOCK))
            starts = rng.integers(0, max(len(dec_abs_arr) - BLOCK, 1), size=nb)
            dboot = np.concatenate([dec_abs_arr[s:s + BLOCK] for s in starts])[:len(dec_abs_arr)]
        else:
            dboot = rng.choice(dec_abs_arr, size=len(dec_abs_arr), replace=True)
        uboot = rng.choice(uncond_arr, size=len(uncond_arr), replace=True)
        diffs.append(dboot.mean() - uboot.mean())
    diffs = np.sort(diffs)
    diff_ci = [float(diffs[int(0.05 * N_BOOT)]), float(diffs[int(0.95 * N_BOOT)])]
    p1_credible = diff_ci[0] > 0
    cells = {
        "1_decision_minus_unconditional_GATING": {"decision_mean": float(dec_abs_arr.mean()), "unconditional_mean": float(uncond_arr.mean()),
                                                    "diff": float(diff), "ci_90": diff_ci, "credible_positive": bool(p1_credible),
                                                    "n_ecb_dates": dates_used, "n_unconditional_hours": int(len(uncond_arr))},
        "2_decision_signed": cell(decision_signed),
        "3_unconditional_hourly_abs_ref": cell(list(uncond_arr)),
        "5_first_half": cell(decision_abs[:half]),
        "6_second_half": cell(decision_abs[half:]),
    }
    fm_abs = np.array([r["fm_abs"] for r in kill_rows]); dec_abs_for_fm = np.array([r["dec_abs"] for r in kill_rows])
    fm_share = float(fm_abs.mean() / dec_abs_for_fm.mean()) if len(kill_rows) and dec_abs_for_fm.mean() else float("nan")
    cells["4_first_minute_share_KILL"] = {"share": fm_share, "kill": bool((not np.isnan(fm_share)) and fm_share > 0.5)}

    print("\nCells:")
    c1 = cells["1_decision_minus_unconditional_GATING"]
    print(f"  1_GATING  decision_mean={c1['decision_mean']:.4f} unconditional_mean={c1['unconditional_mean']:.4f} "
          f"diff={c1['diff']:+.4f} ci_90=({c1['ci_90'][0]:+.4f},{c1['ci_90'][1]:+.4f}) credible_positive={c1['credible_positive']} n_ecb={c1['n_ecb_dates']}")
    for k in ["2_decision_signed", "3_unconditional_hourly_abs_ref", "5_first_half", "6_second_half"]:
        s = cells[k]
        print(f"  {k:<30} n={s['n']:>4} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
    k4 = cells["4_first_minute_share_KILL"]
    print(f"  4_first_minute_share      share={k4['share']:+.3f} KILL={k4['kill']}")

    if k4["kill"] and c1["credible_positive"]:
        verdict, note = "KILLED", "Decision-hour response is concentrated in the 07:45 statement-print minute -- a print artifact at the STATEMENT, not the Q&A repricing this mechanism claims. Closes per kill rule, even though magnitude alone was confirmed."
    elif c1["credible_positive"]:
        verdict, note = "P1_PASS", "Decision-hour |return| credibly exceeds the unconditional hourly baseline and is not a pure statement-print effect. Advance to Statistical per pipeline order."
    else:
        verdict, note = "P1_FAIL", "Decision-hour |return| not credibly larger than the unconditional hourly baseline. Entry closes on falsifier (a)."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_ecb_dates_loaded": len(dates), "n_ecb_dates_used": dates_used, "n_ecb_dates_skipped": dates_skipped,
           "cells": cells, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_025_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_025_results.json'}")


if __name__ == "__main__":
    main()
