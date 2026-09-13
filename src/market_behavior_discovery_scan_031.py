"""
market_behavior_discovery_scan_031.py
========================================

Scan 031. Draws Entry 28 (map anchor M24): month-end payment-cycle
reversal, NQ (literature channel, open scope). Mechanism doc written
BEFORE this scan:
research/mechanisms/month-end-payment-cycle-reversal-m24.md.

Frozen scope (doc Section 10), Discovery only (2015-01 -> 2021-10-01).
THIN-SAMPLE family, flagged in advance: ~82 monthly observations, ~27
per tercile.

TEN pre-registered cells (scan_031_2026-09-13), 1 gating:
  1. LOW-tercile next-month mean, net of NULL 1 (unconditional next-
     month mean), block CI                                <== GATING (P1)
  2. HIGH-tercile next-month mean, net of NULL 1, block CI (P2
     asymmetry check, reported)
  3. MID-tercile next-month mean, net of NULL 1 (reported)
  4. LOW minus HIGH difference, bootstrap CI (P2, reported)
  5. unconditional next-month mean (NULL 1 reference)
  6-7. share of the LOW-tercile next-month return attributable to its
       first 3 RTH sessions vs. the remainder (confound/kill check
       against hyp-000108/M6)
  8-9. LOW-tercile cell on Discovery first-half vs second-half
       (P4, explicitly low-power, descriptive only)
  10. LOW-tercile restricted to months where the next month does NOT
      itself start with a further leg down (stability check, reported)

Last-week-of-month return = NQ close-to-close return over the final 5
RTH sessions of the month (min 4 for short months). Next-month return =
close-to-close from month t's last session to month t+1's last session.
Terciles of last-week return frozen on Discovery. Block bootstrap
(block=3, thin-sample convention) is the CI of record.

One shot. No new cells, no retuning after seeing results.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_031.py
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
BLOCK = 3; N_BOOT = 3000; SEED = 20260913


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


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 031 (Entry 28 / map M24: month-end payment-cycle reversal, NQ)"); print("=" * 78)
    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_031.py", symbol="NQ")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(nq_all)

    daily_rows = []
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty or len(rth) < 200:
            continue
        daily_rows.append({"date": pd.Timestamp(day), "close": float(rth["Close"].iloc[-1]),
                            "open": float(rth["Open"].iloc[0])})
    daily = pd.DataFrame(daily_rows).set_index("date").sort_index()
    trading_days = list(daily.index)
    idx_of = {d: i for i, d in enumerate(trading_days)}
    closes = daily["close"].to_numpy()
    opens = daily["open"].to_numpy()
    n_days = len(trading_days)
    print(f"RTH trading sessions in Discovery: {n_days}")

    month_key = pd.Series(trading_days).dt.to_period("M")
    months = sorted(set(month_key))
    last_day_per_month = {m: pd.Series(trading_days)[month_key == m].max() for m in months}
    first3_per_month = {m: sorted(pd.Series(trading_days)[month_key == m].tolist())[:3] for m in months}
    all_days_per_month = {m: sorted(pd.Series(trading_days)[month_key == m].tolist()) for m in months}

    month_rows = []
    for i, m in enumerate(months):
        if i == 0 or i == len(months) - 1:
            continue  # need a prior close and a next month-end
        prior_m = months[i - 1]
        next_m = months[i + 1]
        this_end = last_day_per_month[m]
        prior_end = last_day_per_month[prior_m]
        next_end = last_day_per_month[next_m]
        if this_end not in idx_of or prior_end not in idx_of or next_end not in idx_of:
            continue
        this_days = all_days_per_month[m]
        # last-week-of-month: final 5 sessions of month m (min 4)
        if len(this_days) < 4:
            continue
        last_week_days = this_days[-5:] if len(this_days) >= 5 else this_days[-4:]
        lw_start_idx = idx_of[last_week_days[0]] - 1  # close of the session BEFORE the last-week window starts
        if lw_start_idx < 0:
            continue
        last_week_ret = (closes[idx_of[this_end]] - closes[lw_start_idx]) / closes[lw_start_idx]
        next_month_ret = (closes[idx_of[next_end]] - closes[idx_of[this_end]]) / closes[idx_of[this_end]]

        # first-3-RTH-session share of next month's cumulative return
        next_days = all_days_per_month[next_m]
        if len(next_days) < 4:
            first3_ret = float("nan")
        else:
            d3 = next_days[2]
            first3_ret = (closes[idx_of[d3]] - closes[idx_of[this_end]]) / closes[idx_of[this_end]]

        # does next month itself start with a further leg down (first 3 sessions negative)?
        further_leg_down = (not np.isnan(first3_ret)) and (first3_ret < 0)

        month_rows.append({"month": str(m), "last_week_ret": last_week_ret, "next_month_ret": next_month_ret,
                            "first3_ret": first3_ret, "further_leg_down": further_leg_down})

    mdf = pd.DataFrame(month_rows)
    print(f"Usable calendar months: {len(mdf)}")

    q1, q2 = mdf["last_week_ret"].quantile([1 / 3, 2 / 3])
    mdf["tercile"] = pd.cut(mdf["last_week_ret"], bins=[-np.inf, q1, q2, np.inf], labels=["LOW", "MID", "HIGH"])
    print(f"Tercile edges: q1={q1:+.4f} q2={q2:+.4f}; counts: {mdf['tercile'].value_counts().to_dict()}")

    uncond_next_month = mdf["next_month_ret"].to_numpy()
    uncond_mean = float(np.nanmean(uncond_next_month))

    low = mdf[mdf["tercile"] == "LOW"]
    mid = mdf[mdf["tercile"] == "MID"]
    high = mdf[mdf["tercile"] == "HIGH"]

    cells = {}
    cells["1_low_net_of_null1_GATING"] = cell(low["next_month_ret"].to_numpy() - uncond_mean)
    cells["2_high_net_of_null1"] = cell(high["next_month_ret"].to_numpy() - uncond_mean)
    cells["3_mid_net_of_null1"] = cell(mid["next_month_ret"].to_numpy() - uncond_mean)
    cells["4_low_minus_high"] = diff_cell(low["next_month_ret"].to_numpy(), high["next_month_ret"].to_numpy())
    cells["5_null1_unconditional"] = {"n": int(len(uncond_next_month)), "mean": uncond_mean}

    low_first3 = low["first3_ret"].dropna().to_numpy()
    low_total = low["next_month_ret"].to_numpy()[: len(low_first3)]
    fm_share = float(np.mean(np.abs(low_first3)) / np.mean(np.abs(low_total))) if len(low_first3) and np.mean(np.abs(low_total)) else float("nan")
    kill_confound = bool((not np.isnan(fm_share)) and fm_share > 0.5)
    cells["6_7_first3_share_of_low_tercile_CONFOUND"] = {"n": int(len(low_first3)), "share": fm_share, "confounded": kill_confound}

    half = len(low) // 2
    low_sorted = low.sort_values("month")
    cells["8_low_first_half"] = cell(low_sorted["next_month_ret"].to_numpy()[:half] - uncond_mean)
    cells["9_low_second_half"] = cell(low_sorted["next_month_ret"].to_numpy()[half:] - uncond_mean)

    low_no_further_leg = low[~low["further_leg_down"]]
    cells["10_low_excl_further_leg_down"] = cell(low_no_further_leg["next_month_ret"].to_numpy() - uncond_mean)

    print("\nCells:")
    c1 = cells["1_low_net_of_null1_GATING"]
    print(f"  1_GATING (LOW net of NULL1)  n={c1['n']:>3} mean={c1['mean']:+.4f} ci_90=({c1['ci_90'][0]:+.4f},{c1['ci_90'][1]:+.4f}) {c1['direction']}")
    c2 = cells["2_high_net_of_null1"]
    print(f"  2_HIGH_asymmetry             n={c2['n']:>3} mean={c2['mean']:+.4f} ci_90=({c2['ci_90'][0]:+.4f},{c2['ci_90'][1]:+.4f}) {c2['direction']}")
    c3 = cells["3_mid_net_of_null1"]
    print(f"  3_MID                        n={c3['n']:>3} mean={c3['mean']:+.4f} ci_90=({c3['ci_90'][0]:+.4f},{c3['ci_90'][1]:+.4f}) {c3['direction']}")
    c4 = cells["4_low_minus_high"]
    print(f"  4_LOW_minus_HIGH             diff={c4['diff']:+.4f} ci_90=({c4['ci_90'][0]:+.4f},{c4['ci_90'][1]:+.4f}) credible={c4['credible_vs_zero']}")
    c5 = cells["5_null1_unconditional"]
    print(f"  5_NULL1_unconditional        n={c5['n']:>3} mean={c5['mean']:+.4f}")
    c67 = cells["6_7_first3_share_of_low_tercile_CONFOUND"]
    print(f"  6-7_first3_share             n={c67['n']:>3} share={c67['share']:+.3f} CONFOUNDED={c67['confounded']}")
    c8 = cells["8_low_first_half"]; c9 = cells["9_low_second_half"]
    print(f"  8_LOW_first_half             n={c8['n']:>3} mean={c8['mean']:+.4f} ci_90=({c8['ci_90'][0]:+.4f},{c8['ci_90'][1]:+.4f}) {c8['direction']}")
    print(f"  9_LOW_second_half            n={c9['n']:>3} mean={c9['mean']:+.4f} ci_90=({c9['ci_90'][0]:+.4f},{c9['ci_90'][1]:+.4f}) {c9['direction']}")
    c10 = cells["10_low_excl_further_leg_down"]
    print(f"  10_LOW_excl_further_leg_down n={c10['n']:>3} mean={c10['mean']:+.4f} ci_90=({c10['ci_90'][0]:+.4f},{c10['ci_90'][1]:+.4f}) {c10['direction']}")

    p1_pass = c1["credible_vs_zero"] and c1["direction"] == "positive"
    if kill_confound and p1_pass:
        verdict, note = "KILLED", "The LOW-tercile next-month return is concentrated in the first 3 RTH sessions -- indistinguishable from the closed turn-of-month inflow effect (hyp-000108/M6) bleeding across the calendar boundary, not an independent month-long reversal. Confounded per kill rule, even though the gating cell alone passed."
    elif p1_pass:
        verdict, note = "P1_PASS", "LOW-tercile next-month return credibly exceeds NQ's own unconditional next-month drift, and is not concentrated in the first 3 sessions (not confounded with M6). Advance to Statistical per pipeline order."
    else:
        verdict, note = "P1_FAIL", "LOW-tercile next-month return, net of NQ's own unconditional next-month drift, does not credibly clear zero. The payment-cycle friction is not visible in NQ futures at this data ceiling (thin-sample family, n~27 per tercile -- a null here is not strong evidence the effect does not exist, only that it is not visible at this data ceiling). Entry closes."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_months_used": int(len(mdf)), "tercile_edges": {"q1": float(q1), "q2": float(q2)},
           "tercile_counts": mdf["tercile"].value_counts().to_dict(), "cells": cells, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_031_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_031_results.json'}")


if __name__ == "__main__":
    main()
