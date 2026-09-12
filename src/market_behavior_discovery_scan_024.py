"""
market_behavior_discovery_scan_024.py
========================================

Scan 024. Draws Entry 23 (map anchor M19): Treasury 10-year note auction
concession and rebound, ZN (open scope -- signal and trade both in ZN).
Mechanism doc written BEFORE this scan:
research/mechanisms/treasury-auction-concession-zn-m19.md.

Frozen scope (doc Section 7), Discovery only (2015-01 -> 2021-10).
Event = 10-year note ORIGINAL-TERM auction dates (securityTerm=="10-Year"
exactly -- reopenings, labeled with their remaining term, e.g. "9-Year
10-Month", are excluded per the frozen scope's literal wording) from
data/treasury_auctions_notes_2015_2021.csv (supplied by Jason from
TreasuryDirect's Auction Query, free public data). 41 auction dates in
the Discovery window.

Session = ZN RTH 08:20-15:00 ET (the cash Treasury day; ZN's pit hours).
Daily close = last bar before 15:00 ET. ATR14 = trailing 14-session mean
RTH range, known through t-1 (no lookahead), evaluated at the auction day
for both legs (mechanism doc Section 1: "ZN's RTH close-to-close return,
/ ATR14").

TEN pre-registered cells (scan_024_2026-09-12; bid-to-cover cell from
Section 7 item 6 omitted -- the supplied file has no bid-to-cover column,
per the doc's own "only if the file has it" condition; the doc's "11
without bid-to-cover" estimate is not exact -- the unconditional 3-session
reference is implemented as ONE shared pooled distribution for both legs,
per Section 7 item 3's singular wording, not a duplicate per leg):
  1. pre-leg (t-3 -> t) mean minus unconditional, block CI      <== GATING (P1)
  2. post-leg (t -> t+3) mean minus unconditional, block CI     <== GATING (P2)
  3. unconditional 3-session |ATR-normalized return| distribution mean (NULL 1 ref)
  4. same-day-of-month no-auction placebo, pre leg
  5. same-day-of-month no-auction placebo, post leg
  6. pre-leg, first half of Discovery auctions
  7. pre-leg, second half of Discovery auctions
  8. post-leg, first half of Discovery auctions
  9. post-leg, second half of Discovery auctions
  10. share of the post-leg magnitude concentrated in the first 1-minute
      bar after the 1:00pm ET auction-result announcement (KILL)

Placebo month mapping (deterministic, fixed before any result is seen):
auction months in this dataset are {1,2,5,7,8,11}; each maps to a FIXED
non-auction month with the same day-of-month: {1:3, 2:4, 5:6, 7:9, 8:10,
11:12}. Nearest actual trading day to the mapped calendar date is used.

Block bootstrap (block=5, appropriate for ~41 non-overlapping event
legs) is the CI of record for the gating cells; the unconditional pool is
large (thousands of daily 3-session windows) and resampled i.i.d.

One shot. No new cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_024.py
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
SEED = 20260912
PLACEBO_MONTH_MAP = {1: 3, 2: 4, 5: 6, 7: 9, 8: 10, 11: 12}


def block_ci(v, block, alpha=0.10):
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


def load_auction_dates():
    df = pd.read_csv(DATA_DIR / "treasury_auctions_notes_2015_2021.csv")
    df = df[df["Security Term"].str.strip() == "10-Year"]
    dates = pd.to_datetime(df["Auction Date"], format="%m/%d/%Y")
    return sorted(pd.Timestamp(d.date()) for d in dates)


def nearest_trading_day(target, trading_days):
    """First trading day on or after `target` (calendar date)."""
    for d in trading_days:
        if d >= target:
            return d
    return None


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 024 (Entry 23 / map M19: Treasury 10-year auction concession, ZN)"); print("=" * 78)
    zn_all, synth = load_price_data(context="market_behavior_discovery_scan_024.py", symbol="ZN")
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

    # Unconditional pool: every valid 3-session forward return, ATR-normalized,
    # anchored at the day the window STARTS from (used as NULL 1 for both legs).
    uncond = []
    for i in range(n_days - 3):
        if np.isnan(atrs[i]):
            continue
        uncond.append((closes[i + 3] - closes[i]) / atrs[i])
    uncond = np.array(uncond)
    print(f"Unconditional 3-session windows: {len(uncond)}")

    auction_dates = load_auction_dates()
    print(f"10-year auction dates loaded (Discovery window): {len(auction_dates)}")

    pre_legs, post_legs, fm_shares, skipped = [], [], [], 0
    event_rows = []
    for adate in auction_dates:
        # nearest trading day on/after the auction date (handles the rare
        # case the exact calendar date isn't a session)
        t = nearest_trading_day(adate, trading_days)
        if t is None or t not in idx_of:
            skipped += 1; continue
        i = idx_of[t]
        if i < 3 or i > n_days - 4 or np.isnan(atrs[i]):
            skipped += 1; continue
        pre_ret = (closes[i] - closes[i - 3]) / atrs[i]
        post_ret = (closes[i + 3] - closes[i]) / atrs[i]
        pre_legs.append(pre_ret); post_legs.append(post_ret)

        # Kill check: first 1-minute bar after the 1:00pm ET announcement,
        # on the auction day itself, as a share of the post-leg magnitude.
        day_bars = disc[disc.index.date == t.date()]
        fm = day_bars.between_time("13:01", "13:02", inclusive="left")
        if not fm.empty:
            fm_ret = (float(fm["Close"].iloc[-1]) - float(fm["Open"].iloc[0])) / atrs[i]
            fm_shares.append((abs(fm_ret), abs(post_ret)))
        event_rows.append({"auction_date": str(adate.date()), "trading_day": str(t.date()),
                            "pre_leg": pre_ret, "post_leg": post_ret})

    print(f"Auction events usable: {len(pre_legs)}; skipped (no session / no ATR / edge of sample): {skipped}")

    pre_arr = np.array(pre_legs); post_arr = np.array(post_legs)
    uncond_mean = float(uncond.mean())

    def diff_ci(event_arr, block=BLOCK_EVENT):
        rng = np.random.default_rng(SEED)
        diffs = []
        for _ in range(N_BOOT):
            if len(event_arr) >= block:
                nb = int(np.ceil(len(event_arr) / block))
                starts = rng.integers(0, max(len(event_arr) - block, 1), size=nb)
                eboot = np.concatenate([event_arr[s:s + block] for s in starts])[:len(event_arr)]
            else:
                eboot = rng.choice(event_arr, size=len(event_arr), replace=True)
            uboot = rng.choice(uncond, size=len(uncond), replace=True)
            diffs.append(eboot.mean() - uboot.mean())
        diffs = np.sort(diffs)
        return [float(diffs[int(0.05 * N_BOOT)]), float(diffs[int(0.95 * N_BOOT)])]

    pre_diff = float(pre_arr.mean() - uncond_mean); pre_diff_ci = diff_ci(pre_arr)
    post_diff = float(post_arr.mean() - uncond_mean); post_diff_ci = diff_ci(post_arr)
    p1_credible_negative = pre_diff_ci[1] < 0
    p2_credible_positive = post_diff_ci[0] > 0

    # Placebo: same day-of-month, fixed non-auction month mapping.
    placebo_pre, placebo_post = [], []
    for adate in auction_dates:
        pm = PLACEBO_MONTH_MAP.get(adate.month)
        if pm is None:
            continue
        target = pd.Timestamp(year=adate.year, month=pm, day=min(adate.day, 28))
        t = nearest_trading_day(target, trading_days)
        if t is None or t not in idx_of:
            continue
        i = idx_of[t]
        if i < 3 or i > n_days - 4 or np.isnan(atrs[i]):
            continue
        placebo_pre.append((closes[i] - closes[i - 3]) / atrs[i])
        placebo_post.append((closes[i + 3] - closes[i]) / atrs[i])

    half = len(pre_legs) // 2
    cells = {
        "1_pre_leg_minus_unconditional_GATING": {"pre_mean": float(pre_arr.mean()), "unconditional_mean": uncond_mean,
                                                  "diff": pre_diff, "ci_90": pre_diff_ci, "credible_negative": bool(p1_credible_negative),
                                                  "n_events": int(len(pre_arr))},
        "2_post_leg_minus_unconditional_GATING": {"post_mean": float(post_arr.mean()), "unconditional_mean": uncond_mean,
                                                   "diff": post_diff, "ci_90": post_diff_ci, "credible_positive": bool(p2_credible_positive),
                                                   "n_events": int(len(post_arr))},
        "3_unconditional_3session_ref": {"n": int(len(uncond)), "mean": uncond_mean},
        "4_placebo_pre_leg": cell(placebo_pre),
        "5_placebo_post_leg": cell(placebo_post),
        "6_pre_leg_first_half": cell(pre_legs[:half]),
        "7_pre_leg_second_half": cell(pre_legs[half:]),
        "8_post_leg_first_half": cell(post_legs[:half]),
        "9_post_leg_second_half": cell(post_legs[half:]),
    }
    fm_abs = np.array([x[0] for x in fm_shares]); post_abs_for_fm = np.array([x[1] for x in fm_shares])
    fm_share = float(fm_abs.mean() / post_abs_for_fm.mean()) if len(fm_shares) and post_abs_for_fm.mean() != 0 else float("nan")
    cells["10_first_minute_share_KILL"] = {"share": fm_share, "kill": bool((not np.isnan(fm_share)) and fm_share > 0.5)}

    print("\nCells:")
    c1 = cells["1_pre_leg_minus_unconditional_GATING"]; c2 = cells["2_post_leg_minus_unconditional_GATING"]
    print(f"  1_GATING(pre)  pre_mean={c1['pre_mean']:+.4f} unconditional={c1['unconditional_mean']:+.4f} "
          f"diff={c1['diff']:+.4f} ci_90=({c1['ci_90'][0]:+.4f},{c1['ci_90'][1]:+.4f}) credible_negative={c1['credible_negative']} n={c1['n_events']}")
    print(f"  2_GATING(post) post_mean={c2['post_mean']:+.4f} unconditional={c2['unconditional_mean']:+.4f} "
          f"diff={c2['diff']:+.4f} ci_90=({c2['ci_90'][0]:+.4f},{c2['ci_90'][1]:+.4f}) credible_positive={c2['credible_positive']} n={c2['n_events']}")
    for k in ["4_placebo_pre_leg", "5_placebo_post_leg", "6_pre_leg_first_half", "7_pre_leg_second_half",
              "8_post_leg_first_half", "9_post_leg_second_half"]:
        s = cells[k]
        print(f"  {k:<28} n={s['n']:>3} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
    k10 = cells["10_first_minute_share_KILL"]
    print(f"  10_first_minute_share      share={k10['share']:+.3f} KILL={k10['kill']}")

    both_confound = p1_credible_negative and p2_credible_positive
    if k10["kill"] and both_confound:
        verdict, note = "KILLED", "Post-leg response is concentrated in the auction-result print minute -- an announcement artifact, not a multi-session inventory concession/rebound. Closes per kill rule, even though both gating legs were confirmed."
    elif p1_credible_negative or p2_credible_positive:
        verdict, note = "P1_OR_P2_PASS", "At least one gating leg (pre-auction concession or post-auction rebound) is credibly non-zero vs. ZN's unconditional 3-session drift and is not a pure announcement-print effect. Advance to Statistical per pipeline order -- flag the thin-sample rule (n~41 events, failure mode #2)."
    else:
        verdict, note = "P1_AND_P2_FAIL", "Neither the pre-auction concession nor the post-auction rebound is credibly larger than ZN's unconditional 3-session drift. Entry closes on falsifier (a)."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_auction_dates_loaded": len(auction_dates), "n_events_used": len(pre_legs), "n_events_skipped": skipped,
           "n_unconditional_windows": int(len(uncond)), "cells": cells, "verdict": verdict, "note": note,
           "events": event_rows}
    (DATA_DIR / "market_behavior_discovery_scan_024_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_024_results.json'}")


if __name__ == "__main__":
    main()
