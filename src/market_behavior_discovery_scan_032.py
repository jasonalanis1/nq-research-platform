"""
market_behavior_discovery_scan_032.py
========================================

Scan 032. Draws Entry 29 (map anchor M25): monthly options-expiration
week delta-hedge unwind, NQ (literature channel, open scope). Mechanism
doc written BEFORE this scan:
research/mechanisms/monthly-opex-week-delta-hedge-m25.md.

Frozen scope (doc Section 9), Discovery only (2015-01 -> Discovery cutoff).
Calendar-week partition: EXPIRATION week = the calendar week (Mon-Fri)
containing the month's third Friday; NON-EXPIRATION = every other week.
Normalization (decided at scan-write time, disclosed per the doc's own
instruction): weekly close-to-close return divided by the average of
that week's own trailing daily ATR14 values (same ATR14 convention used
project-wide, shifted so no lookahead) -- NOT scaled by day-count, same
convention as the hourly M20/M21/M23 family normalizing by a single
ATR14 without window-length scaling.

TEN pre-registered cells (scan_032_2026-09-13), 1 gating:
  1. Expiration-week return net of NULL 1 (unconditional weekly return),
     block CI                                            <== GATING (P1)
  2. Non-expiration-week return net of NULL 1 (reported comparison)
  3. Expiration minus non-expiration difference, bootstrap CI (P2)
  4. NULL 1 unconditional weekly mean (reference)
  5-9. Within-expiration-week day-of-week cumulative return (Mon/Tue/
       Wed/Thu/Fri cumulative from week start), reported -- falsifier
       (b): does the effect build across the week or concentrate in one
       day?
  10. KILL: share of the expiration week's total |return| coming from
      the week's first RTH session's first 1-minute bar

Block bootstrap (block=5, consistent with the M19/M22 monthly-frequency
convention -- weekly events are a similarly thin annual count, ~12/year)
is the CI of record.

One shot. No new cells, no retuning after seeing results.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_032.py
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
ATR_WINDOW = 14
BLOCK = 5
N_BOOT = 3000
SEED = 20260913


def block_ci(v, block=BLOCK, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < max(block * 3, 6):
        return [float("nan"), float("nan")]
    means = _block_means(v, block, N_BOOT, np.random.default_rng(SEED))
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


def cell(v, block=BLOCK):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    ci = block_ci(v, block)
    cred = (not np.isnan(ci[0])) and ((ci[0] > 0) or (ci[1] < 0))
    return {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": ci,
            "credible_vs_zero": bool(cred), "direction": "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")}


def diff_cell(a, b, block=BLOCK):
    a = np.asarray([x for x in a if not np.isnan(x)], float)
    b = np.asarray([x for x in b if not np.isnan(x)], float)
    diff = float(a.mean() - b.mean()) if len(a) and len(b) else float("nan")
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(N_BOOT):
        aboot = rng.choice(a, size=len(a), replace=True) if len(a) else a
        bboot = rng.choice(b, size=len(b), replace=True) if len(b) else b
        diffs.append((aboot.mean() if len(aboot) else np.nan) - (bboot.mean() if len(bboot) else np.nan))
    diffs = np.array([d for d in diffs if not np.isnan(d)])
    if len(diffs) < 10:
        ci = [float("nan"), float("nan")]
    else:
        diffs = np.sort(diffs)
        ci = [float(diffs[int(0.05 * len(diffs))]), float(diffs[int(0.95 * len(diffs))])]
    cred = (not np.isnan(ci[0])) and ((ci[0] > 0) or (ci[1] < 0))
    return {"n_a": int(len(a)), "n_b": int(len(b)), "diff": diff, "ci_90": ci, "credible_vs_zero": bool(cred)}


def third_friday(year, month):
    fridays = [d for d in pd.date_range(f"{year}-{month:02d}-01", periods=31, freq="D")
               if d.month == month and d.weekday() == 4]
    return fridays[2]


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 032 (Entry 29 / map M25: monthly opex-week delta-hedge unwind, NQ)"); print("=" * 78)
    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_032.py", symbol="NQ")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(nq_all)

    daily_rows = []
    minute_bars_by_day = {}
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty or len(rth) < 200:
            continue
        daily_rows.append({"date": pd.Timestamp(day), "close": float(rth["Close"].iloc[-1]),
                            "range": float(rth["High"].max() - rth["Low"].min())})
        minute_bars_by_day[pd.Timestamp(day)] = rth
    daily = pd.DataFrame(daily_rows).set_index("date").sort_index()
    daily["atr14"] = daily["range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    trading_days = list(daily.index)
    idx_of = {d: i for i, d in enumerate(trading_days)}
    closes = daily["close"].to_numpy()
    atrs = daily["atr14"].to_numpy()
    n_days = len(trading_days)
    print(f"RTH trading sessions in Discovery: {n_days}")

    # Calendar-week grouping: ISO (year, week) of each trading day.
    iso = pd.Series(trading_days).apply(lambda d: (d.isocalendar().year, d.isocalendar().week))
    week_groups = {}
    for d, wk in zip(trading_days, iso):
        week_groups.setdefault(wk, []).append(d)
    ordered_weeks = sorted(week_groups.keys())

    # Third-Friday-of-month calendar weeks (by ISO year/week), across the
    # full range of months touched by the Discovery trading days.
    months_touched = sorted({(d.year, d.month) for d in trading_days})
    expiration_weeks = set()
    for (y, m) in months_touched:
        tf = third_friday(y, m)
        iso_yr, iso_wk, _ = tf.isocalendar()
        expiration_weeks.add((iso_yr, iso_wk))

    # Unconditional pool: every valid week-over-week close-to-close return,
    # ATR-normalized by that week's own mean daily ATR14. NULL 1.
    week_rows = []
    for i, wk in enumerate(ordered_weeks):
        if i == 0:
            continue
        days_this = week_groups[wk]
        prior_wk = ordered_weeks[i - 1]
        days_prior = week_groups[prior_wk]
        start_anchor = days_prior[-1]  # prior week's last session (close-to-close anchor)
        end_day = days_this[-1]
        if start_anchor not in idx_of or end_day not in idx_of:
            continue
        week_atrs = atrs[[idx_of[d] for d in days_this]]
        week_atrs = week_atrs[~np.isnan(week_atrs)]
        if len(week_atrs) == 0:
            continue
        mean_atr = float(week_atrs.mean())
        if mean_atr == 0:
            continue
        # Points-difference over the week, normalized by the week's own
        # mean daily ATR14 (points) -- same convention as Scan 027/M22
        # (point diff / ATR14, not a fractional-return/ATR ratio).
        week_ret_norm = (closes[idx_of[end_day]] - closes[idx_of[start_anchor]]) / mean_atr
        is_expiration = wk in expiration_weeks
        week_rows.append({"week": f"{wk[0]}-W{wk[1]:02d}", "days": days_this, "start_anchor": start_anchor,
                           "week_ret_norm": week_ret_norm, "is_expiration": is_expiration})

    wdf = pd.DataFrame(week_rows)
    print(f"Usable calendar weeks: {len(wdf)} (expiration: {int(wdf['is_expiration'].sum())}, non-expiration: {int((~wdf['is_expiration']).sum())})")

    uncond = wdf["week_ret_norm"].to_numpy()
    uncond_mean = float(np.nanmean(uncond))

    exp_weeks = wdf[wdf["is_expiration"]]
    nonexp_weeks = wdf[~wdf["is_expiration"]]

    cells = {}
    cells["1_expiration_net_of_null1_GATING"] = cell(exp_weeks["week_ret_norm"].to_numpy() - uncond_mean)
    cells["2_nonexpiration_net_of_null1"] = cell(nonexp_weeks["week_ret_norm"].to_numpy() - uncond_mean)
    cells["3_expiration_minus_nonexpiration"] = diff_cell(exp_weeks["week_ret_norm"].to_numpy(), nonexp_weeks["week_ret_norm"].to_numpy())
    cells["4_null1_unconditional"] = {"n": int(len(uncond)), "mean": uncond_mean}

    # Within-expiration-week day-of-week cumulative return (Mon..Fri cumulative from start_anchor)
    dow_labels = ["5_mon_cum", "6_tue_cum", "7_wed_cum", "8_thu_cum", "9_fri_cum"]
    for k, label in enumerate(dow_labels):
        vals = []
        for _, row in exp_weeks.iterrows():
            days = row["days"]
            if k >= len(days):
                continue
            anchor_close = closes[idx_of[row["start_anchor"]]]
            week_atrs_k = atrs[[idx_of[d] for d in days]]
            week_atrs_k = week_atrs_k[~np.isnan(week_atrs_k)]
            if anchor_close == 0 or len(week_atrs_k) == 0:
                continue
            mean_atr_k = float(week_atrs_k.mean())
            if mean_atr_k == 0:
                continue
            cum_ret_norm = (closes[idx_of[days[k]]] - anchor_close) / mean_atr_k
            vals.append(cum_ret_norm)
        cells[label] = cell(np.array(vals))  # reported vs zero, descriptive, same ATR-normalized units as cell 1

    # KILL: share of the expiration week's total |return| from the week's
    # first RTH session's first 1-minute bar.
    first_min_shares = []
    for _, row in exp_weeks.iterrows():
        days = row["days"]
        first_day = days[0]
        bars = minute_bars_by_day.get(first_day)
        anchor_close = closes[idx_of[row["start_anchor"]]]
        if bars is None or len(bars) < 2 or anchor_close == 0:
            continue
        first_bar_ret = abs(float(bars["Close"].iloc[0]) - anchor_close) / anchor_close
        total_week_ret = abs(row["week_ret_norm"]) if row["week_ret_norm"] == row["week_ret_norm"] else np.nan
        # use raw (non-ATR-normalized) week move for the share calc, consistent units
        end_day = days[-1]
        raw_week_move = abs(closes[idx_of[end_day]] - anchor_close) / anchor_close
        if raw_week_move == 0 or np.isnan(raw_week_move):
            continue
        first_min_shares.append(first_bar_ret / raw_week_move)
    kill_share = float(np.mean(first_min_shares)) if first_min_shares else float("nan")
    kill_confound = bool((not np.isnan(kill_share)) and kill_share > 0.5)
    cells["10_kill_first_minute_share"] = {"n": int(len(first_min_shares)), "share": kill_share, "killed": kill_confound}

    print("\nCells:")
    c1 = cells["1_expiration_net_of_null1_GATING"]
    print(f"  1_GATING (expiration net of NULL1) n={c1['n']:>3} mean={c1['mean']:+.4f} ci_90=({c1['ci_90'][0]:+.4f},{c1['ci_90'][1]:+.4f}) {c1['direction']}")
    c2 = cells["2_nonexpiration_net_of_null1"]
    print(f"  2_nonexpiration                    n={c2['n']:>3} mean={c2['mean']:+.4f} ci_90=({c2['ci_90'][0]:+.4f},{c2['ci_90'][1]:+.4f}) {c2['direction']}")
    c3 = cells["3_expiration_minus_nonexpiration"]
    print(f"  3_expiration_minus_nonexpiration   diff={c3['diff']:+.4f} ci_90=({c3['ci_90'][0]:+.4f},{c3['ci_90'][1]:+.4f}) credible={c3['credible_vs_zero']}")
    c4 = cells["4_null1_unconditional"]
    print(f"  4_NULL1_unconditional              n={c4['n']:>3} mean={c4['mean']:+.4f}")
    for label in dow_labels:
        cc = cells[label]
        print(f"  {label:<34} n={cc['n']:>3} mean={cc['mean']:+.4f} ci_90=({cc['ci_90'][0]:+.4f},{cc['ci_90'][1]:+.4f}) {cc['direction']}")
    c10 = cells["10_kill_first_minute_share"]
    print(f"  10_kill_first_minute_share         n={c10['n']:>3} share={c10['share']:+.3f} KILLED={c10['killed']}")

    p1_pass = c1["credible_vs_zero"] and c1["direction"] == "positive"
    p2_pass = c3["credible_vs_zero"] and c3["diff"] > 0
    if kill_confound and p1_pass:
        verdict, note = "KILLED", "The expiration week's return is concentrated in the first RTH session's first 1-minute bar -- a gap/print artifact, not a week-long hedge-unwind buildup. Falsifier (c) applies."
    elif p1_pass and p2_pass:
        verdict, note = "P1_P2_PASS", "Expiration-week NQ return credibly exceeds NQ's own unconditional weekly drift, AND credibly exceeds the non-expiration-week return -- not merely a restatement of NQ's own positive intraday drift (M15). Advance to Statistical per pipeline order."
    elif p1_pass:
        verdict, note = "P1_PASS_P2_FAIL", "Expiration-week return is credibly positive vs NULL1, but not credibly different from the non-expiration-week return -- falsifier (a) applies in substance: the level looks positive but the WEEK-SPECIFIC premium claim (P2) is not established. Same failure-mode discipline as P1-without-P2 elsewhere in this project (M13/M14/M18): not treated as a real finding."
    else:
        verdict, note = "P1_FAIL", "Expiration-week NQ return, net of NQ's own unconditional weekly drift, does not credibly clear zero. The dealer-hedge-unwind premium documented for S&P 100 stocks is not visible in NQ futures at this data ceiling. Falsifier (a) applies. Entry closes."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_weeks_used": int(len(wdf)), "n_expiration_weeks": int(len(exp_weeks)), "n_nonexpiration_weeks": int(len(nonexp_weeks)),
           "cells": cells, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_032_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_032_results.json'}")


if __name__ == "__main__":
    main()
