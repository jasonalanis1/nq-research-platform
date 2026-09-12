"""
market_behavior_discovery_scan_023.py
========================================

Scan 023. Draws Entry 24 (map anchor M20): EIA weekly petroleum status
report, pre/post-release volatility, CL (open scope -- signal and trade
both in CL). Mechanism doc written BEFORE this scan:
research/mechanisms/eia-inventory-report-drift-cl-m20.md.

Frozen scope (doc Section 7), Discovery only. Release-day rule (public,
mechanical): EIA releases the Weekly Petroleum Status Report on
Wednesday at 10:30 ET, EXCEPT the Wednesday of a week whose Monday is a
US federal holiday, when it shifts to Thursday. Federal holidays taken
from pandas.tseries.holiday.USFederalHolidayCalendar (a standard, public,
independently verifiable calendar) -- not fabricated, not fit to data.

SIX pre-registered cells (scan_023_2026-09-12), 1 gating:
  1. post-release hour (10:30-11:30) |return|/ATR14 mean MINUS
     unconditional RTH-hour |return|/ATR14 mean, block CI on the
     difference                                          <== GATING (P1)
  2. pre-release hour (09:30-10:30) signed mean, block CI (P2, reported,
     unpinned sign)
  3. unconditional RTH-hour |return|/ATR14 distribution mean (NULL 1 ref)
  4. share of the post-release |return| in the 10:30-10:31 bar (KILL)
  5-6. cell 1 on Discovery halves (P4, 2 cells)
Block bootstrap (block=10) is the CI of record. Roll-day / partial
sessions dropped and counted; Globex-only calendar days are not sessions
(Scan 020 lesson, though this scan does not chain across days so it
matters less here).

One shot. No new cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_023.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

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


def eia_release_dates(start, end):
    """Every Wednesday, shifted to Thursday when that week's Monday is a
    US federal holiday (pandas USFederalHolidayCalendar -- public,
    independently verifiable, not fabricated)."""
    hols = set(USFederalHolidayCalendar().holidays(start=start, end=end))
    wednesdays = pd.date_range(start, end, freq="W-WED")
    dates = []
    for w in wednesdays:
        monday = w - pd.Timedelta(days=2)
        dates.append(w + pd.Timedelta(days=1) if monday in hols else w)
    return set(pd.Timestamp(d.date()) for d in dates)


def hourly_abs_returns(g_rth, atr):
    """All RTH clock hours' |return|/ATR for one session's RTH bars."""
    out = []
    for hstart in ["09:30", "10:30", "11:30", "12:30", "13:30", "14:30"]:
        hend = str(int(hstart[:2]) + 1).zfill(2) + hstart[2:]
        sub = g_rth.between_time(hstart, hend, inclusive="left")
        if len(sub) < 50:
            continue
        r = abs(float(sub["Close"].iloc[-1] - sub["Open"].iloc[0])) / atr
        out.append(r)
    return out


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 023 (Entry 24 / map M20: EIA report volatility, CL)"); print("=" * 78)
    cl_all, synth = load_price_data(context="market_behavior_discovery_scan_023.py", symbol="CL")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(cl_all)

    daily_rows = []; dropped = 0
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue
        if len(rth) < 300:
            dropped += 1; continue
        daily_rows.append({"date": pd.Timestamp(day), "rth_range": float(rth["High"].max() - rth["Low"].min())})
    daily = pd.DataFrame(daily_rows).set_index("date").sort_index()
    daily["atr14"] = daily["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    atr_by_date = daily["atr14"].to_dict()

    release_dates = eia_release_dates(disc.index.min(), disc.index.max())
    print(f"EIA release dates computed in Discovery window: {len(release_dates)}")

    pre_signed, post_abs, post_signed, unconditional_abs, kill_share_rows = [], [], [], [], []
    dates_used, dates_skipped = 0, 0
    for day, g in disc.groupby(disc.index.date):
        ts = pd.Timestamp(day)
        rth = g.between_time("09:30", "16:00", inclusive="left")
        atr = atr_by_date.get(ts)
        if rth.empty or atr is None or np.isnan(atr) or len(rth) < 300:
            continue
        all_hours = hourly_abs_returns(rth, atr)
        unconditional_abs.extend(all_hours)
        if ts not in release_dates:
            continue
        pre = g.between_time("09:30", "10:29")
        post = g.between_time("10:30", "11:29")
        first_min = g.between_time("10:30", "10:30")
        if pre.empty or post.empty or first_min.empty:
            dates_skipped += 1; continue
        dates_used += 1
        pre_ret = (float(pre["Close"].iloc[-1]) - float(pre["Open"].iloc[0])) / atr
        post_ret = (float(post["Close"].iloc[-1]) - float(post["Open"].iloc[0])) / atr
        fm_ret = (float(first_min["Close"].iloc[-1]) - float(first_min["Open"].iloc[0])) / atr
        pre_signed.append(pre_ret)
        post_abs.append(abs(post_ret)); post_signed.append(post_ret)
        kill_share_rows.append({"post_abs": abs(post_ret), "fm_abs": abs(fm_ret)})

    print(f"Release dates usable (pre+post+first-min bars present): {dates_used}; skipped (data gap on release day): {dates_skipped}")
    print(f"Non-release RTH sessions dropped (partial/roll): {dropped}")

    half = dates_used // 2
    post_abs_arr = np.array(post_abs)
    uncond_arr = np.array(unconditional_abs)
    diff = post_abs_arr.mean() - uncond_arr.mean()
    # bootstrap the difference: resample post-release dates AND unconditional-hour pool independently, block on each
    rng = np.random.default_rng(SEED)
    diffs = []
    nb_post = int(np.ceil(len(post_abs_arr) / BLOCK)) if len(post_abs_arr) >= BLOCK else 1
    for _ in range(N_BOOT):
        if len(post_abs_arr) >= BLOCK:
            starts = rng.integers(0, max(len(post_abs_arr) - BLOCK, 1), size=nb_post)
            pboot = np.concatenate([post_abs_arr[s:s + BLOCK] for s in starts])[:len(post_abs_arr)]
        else:
            pboot = rng.choice(post_abs_arr, size=len(post_abs_arr), replace=True)
        uboot = rng.choice(uncond_arr, size=len(uncond_arr), replace=True)
        diffs.append(pboot.mean() - uboot.mean())
    diffs = np.sort(diffs)
    diff_ci = [float(diffs[int(0.05 * N_BOOT)]), float(diffs[int(0.95 * N_BOOT)])]
    p1_credible = diff_ci[0] > 0
    cells = {
        "1_post_minus_unconditional_GATING": {"post_mean": float(post_abs_arr.mean()), "unconditional_mean": float(uncond_arr.mean()),
                                               "diff": float(diff), "ci_90": diff_ci, "credible_positive": bool(p1_credible),
                                               "n_release_dates": dates_used, "n_unconditional_hours": int(len(uncond_arr))},
        "2_pre_release_signed": cell(pre_signed),
        "3_unconditional_hourly_abs_ref": cell(list(uncond_arr)),
        "5_first_half": cell(post_abs[:half]),
        "6_second_half": cell(post_abs[half:]),
    }
    fm_share = float(np.mean([r["fm_abs"] for r in kill_share_rows]) / post_abs_arr.mean()) if post_abs_arr.mean() else float("nan")
    cells["4_first_minute_share_KILL"] = {"share": fm_share, "kill": bool(fm_share > 0.5) if not np.isnan(fm_share) else False}

    print("\nCells:")
    c1 = cells["1_post_minus_unconditional_GATING"]
    print(f"  1_GATING  post_mean={c1['post_mean']:.4f} unconditional_mean={c1['unconditional_mean']:.4f} "
          f"diff={c1['diff']:+.4f} ci_90=({c1['ci_90'][0]:+.4f},{c1['ci_90'][1]:+.4f}) credible_positive={c1['credible_positive']} n_release={c1['n_release_dates']}")
    for k in ["2_pre_release_signed", "3_unconditional_hourly_abs_ref", "5_first_half", "6_second_half"]:
        s = cells[k]
        print(f"  {k:<30} n={s['n']:>4} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
    k4 = cells["4_first_minute_share_KILL"]
    print(f"  4_first_minute_share      share={k4['share']:+.3f} KILL={k4['kill']}")

    if k4["kill"] and c1["credible_positive"]:
        verdict, note = "KILLED", "Post-release response concentrated in the release's own first minute -- a print artifact, not a repricing-window signature. Closes per kill rule (b), even though magnitude alone was confirmed."
    elif c1["credible_positive"]:
        verdict, note = "P1_PASS", "Post-release-hour |return| credibly exceeds the unconditional hourly baseline and is not a pure first-minute print effect. Advance to Statistical per pipeline order."
    else:
        verdict, note = "P1_FAIL", "Post-release-hour |return| not credibly larger than the unconditional hourly baseline. Entry closes on falsifier (a)."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_release_dates_computed": len(release_dates), "n_release_dates_used": dates_used, "n_release_dates_skipped": dates_skipped,
           "n_nonrelease_sessions_dropped": int(dropped), "cells": cells, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_023_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_023_results.json'}")


if __name__ == "__main__":
    main()
