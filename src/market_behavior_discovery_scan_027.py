"""
market_behavior_discovery_scan_027.py
========================================

Scan 027. Draws Entry 26 (map anchor M22): month-end index
duration-extension flow, ZN (map channel, open scope).
Mechanism doc written BEFORE this scan:
research/mechanisms/month-end-duration-extension-zn-m22.md.

Frozen scope (doc Sections 2/4/5), Discovery only (2015-01 -> 2021-10):
Session = ZN RTH 08:20-15:00 ET (matches Scan 024/M19's convention).
Footprint = last-2-RTH-session close-to-close return / ATR14, anchored on
the last trading day of each calendar month, vs. ZN's unconditional
2-session-window drift (NULL 1, pooled every valid 2-session window in
Discovery -- same construction as Scan 024's 3-session pool).

THREE pre-registered cells (scan_027_2026-09-13):
  1. last-2-session return net of NULL 1, block CI      <== GATING (P1)
  2. unconditional 2-session pooled distribution mean (NULL 1 ref)
  3. share of the 2-session move in the final RTH minute of the month
     (KILL)

The doc's secondary, non-gating issuance-direction split (Section 2:
"months where net Treasury issuance data ... shows the auction calendar
added net long-dated supply") is OMITTED from this run: the only
issuance file on disk (data/treasury_auctions_notes_2015_2021.csv, used
by Scan 024/M19) contains 10-year note AUCTION DATES only -- no issuance
SIZE and no other maturity terms -- so it cannot support a "net
long-dated supply added this month" classification without inventing a
proxy the doc does not specify. Per the same precedent as Scan 024's
omitted bid-to-cover cell (data not present in the needed form), this
cell is skipped rather than approximated. The doc marked it non-gating
and low-power in advance, so the entry's verdict does not depend on it.

Block bootstrap (block=5, consistent with Scan 024/M19) is the CI of
record.

One shot. No new cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_027.py
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
BLOCK_EVENT = 5
N_BOOT = 3000
SEED = 20260913


def block_ci(v, block=BLOCK_EVENT, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < max(block * 3, 6):
        return [float("nan"), float("nan")]
    means = _block_means(v, block, N_BOOT, np.random.default_rng(SEED))
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


def cell(v, block=BLOCK_EVENT):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    ci = block_ci(v, block)
    cred = (not np.isnan(ci[0])) and ((ci[0] > 0) or (ci[1] < 0))
    return {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": ci,
            "credible_vs_zero": bool(cred), "direction": "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")}


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 027 (Entry 26 / map M22: month-end index duration-extension flow, ZN)"); print("=" * 78)
    zn_all, synth = load_price_data(context="market_behavior_discovery_scan_027.py", symbol="ZN")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(zn_all)

    daily_rows = []
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("08:20", "15:00", inclusive="left")
        if len(rth) < 200:
            continue
        daily_rows.append({"date": pd.Timestamp(day), "close": float(rth["Close"].iloc[-1]),
                            "range": float(rth["High"].max() - rth["Low"].min())})
    daily = pd.DataFrame(daily_rows).set_index("date").sort_index()
    daily["atr14"] = daily["range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    trading_days = list(daily.index)
    idx_of = {d: i for i, d in enumerate(trading_days)}
    n_days = len(trading_days)
    print(f"RTH trading sessions in Discovery: {n_days}")

    closes = daily["close"].to_numpy()
    atrs = daily["atr14"].to_numpy()

    # Unconditional pool: every valid 2-session forward return, ATR-normalized,
    # anchored at the day the window STARTS from. NULL 1 for the gating cell.
    uncond = []
    for i in range(n_days - 2):
        if np.isnan(atrs[i]):
            continue
        uncond.append((closes[i + 2] - closes[i]) / atrs[i])
    uncond = np.array(uncond)
    uncond_mean = float(uncond.mean())
    print(f"Unconditional 2-session windows: {len(uncond)}, pooled mean={uncond_mean:+.4f}")

    # Month-end anchors: the LAST trading day of each calendar month present
    # in the Discovery daily index (calendar-month boundary property of the
    # trading-day index already in use project-wide -- no external calendar
    # file needed).
    month_key = pd.Series(trading_days).dt.to_period("M")
    last_day_per_month = pd.Series(trading_days).groupby(month_key).max()
    month_end_days = sorted(last_day_per_month.tolist())
    print(f"Calendar month-ends in Discovery: {len(month_end_days)}")

    legs, fm_shares, skipped = [], [], 0
    event_rows = []
    for mend in month_end_days:
        if mend not in idx_of:
            skipped += 1; continue
        i = idx_of[mend]
        if i < 2 or np.isnan(atrs[i]):
            skipped += 1; continue
        leg_ret = (closes[i] - closes[i - 2]) / atrs[i]
        legs.append(leg_ret)

        # Kill check: final RTH minute of the month-end session, as a share
        # of the 2-session leg magnitude.
        day_bars = disc[disc.index.date == mend.date()]
        fm = day_bars.between_time("14:59", "15:00", inclusive="left")
        if not fm.empty and leg_ret != 0:
            fm_ret = (float(fm["Close"].iloc[-1]) - float(fm["Open"].iloc[0])) / atrs[i]
            fm_shares.append((abs(fm_ret), abs(leg_ret)))
        event_rows.append({"month_end": str(mend.date()), "leg_return": leg_ret})

    print(f"Month-ends used: {len(legs)}, skipped (insufficient history/ATR warm-up): {skipped}")

    leg_arr = np.array(legs)
    net_of_null = leg_arr - uncond_mean
    results = {}
    results["cell1_gating"] = cell(net_of_null)                     # P1 GATING
    results["cell2_null1"] = {"n": int(len(uncond)), "mean": uncond_mean}
    results["cell1_raw_mean"] = float(leg_arr.mean())

    fm_arr = np.array(fm_shares)
    if len(fm_arr) > 0:
        shares = fm_arr[:, 0] / fm_arr[:, 1]
        share_mean = float(np.mean(shares))
        kill = bool(share_mean > 0.5)
    else:
        share_mean = float("nan"); kill = False
    results["cell3_kill"] = {"n": int(len(fm_arr)), "share_of_leg_mean": share_mean, "kill": kill}

    print(f"\nLast-2-session ZN return / ATR14, net of NULL 1 (unconditional 2-session drift):")
    c1 = results["cell1_gating"]
    print(f"  n={c1['n']:>3} mean={c1['mean']:+.4f} ci_90=({c1['ci_90'][0]:+.4f},{c1['ci_90'][1]:+.4f}) {c1['direction']} <== GATING")
    print(f"  raw leg mean (pre-NULL1-subtraction)={results['cell1_raw_mean']:+.4f}; NULL 1 pooled mean={uncond_mean:+.4f}")
    print(f"  kill: final-minute share={share_mean:+.3f} (n={results['cell3_kill']['n']}) KILL={kill}")
    print("  Issuance-direction split: OMITTED (see module docstring -- no issuance-size data on disk).")

    p1_pass = c1["credible_vs_zero"] and c1["direction"] == "positive"
    if kill and p1_pass:
        verdict, note = "KILLED", "The month-end leg's response is concentrated in the final RTH minute of the month -- a settlement-price/marking artifact, not a multi-session flow building in. Family terminates per kill rule."
    elif p1_pass:
        verdict, note = "P1_PASS", "Last-2-session ZN return is credibly positive net of ZN's own unconditional 2-session drift, and not killed. Advance to Statistical per pipeline order. Issuance-direction split not run (data ceiling; non-gating per the frozen spec)."
    else:
        verdict, note = "P1_FAIL", "Last-2-session ZN return, net of ZN's own unconditional 2-session drift, does not credibly clear zero. The duration-extension flow is not visible in ZN futures at this data ceiling. Entry closes."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_month_ends": int(len(legs)), "skipped": int(skipped), "uncond_2session_mean": uncond_mean,
           "results": results, "verdict": verdict, "note": note,
           "issuance_split": "OMITTED -- no issuance-size data on disk (only 10Y auction dates from Scan 024/M19)"}
    (DATA_DIR / "market_behavior_discovery_scan_027_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_027_results.json'}")


if __name__ == "__main__":
    main()
