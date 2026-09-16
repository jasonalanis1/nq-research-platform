"""
study_s002_night_leg_menu.py -- the SALVAGE-MENU breakdown (standing directive s.7)
of the overnight leg from Scan 020 / hyp-000145, run at S002's SOURCE -> SPECIFY so the
spec knows WHICH REGIME the night-leg trade should be built for. Discovery slice only.
Diagnostic for the Mechanism/Monetization agents; NOT a screen (S002's screen runs on
its frozen module after FREEZE).

THE RAW TRADE (Scan 020's realization path, no stop -- the stop is added at SPECIFY):
  long 1 micro (MNQ) at the 16:00 ET RTH close of session D-1, flat at the 09:30 ET
  open of the next RTH session D. Net $ at 1 micro = points x $2 - $6.00 ASSUMED
  round trip (src/paper_book.py). Sessions lacking either bar are dropped.
THE MENU, all labels KNOWN AT THE 16:00 ENTRY (no lookahead):
  1. VXN regime  VXN close of session D-2 (the last close printed before D-1's 16:00
                 entry; VXN prints at 16:15) over its trailing-20 mean: > 1 HIGH else LOW
  2. prior-day range contraction  prior_day_narrow flag of session D (= D-1's RTH range
                 vs trailing 20, the frozen hyp-000048 definition), known at D-1's close
  3. time of day  not applicable (fixed clock times); reported as one cell
  4. news day    D in the FOMC / CPI / NFP calendars -> NEWS, else QUIET
  + weekend leg  (spec-named for information only: Friday close -> Monday open;
                 hyp-000145's LEARN note says weekday-only is slicing, not a salvage)

USAGE   python3 src/study_s002_night_leg_menu.py [--out research/studies/S002-night-leg-menu-2026-09-15.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from paper_book import ASSUMED_COST_USD_PER_MICRO_RT, MNQ_USD_PER_PT  # noqa: E402
from salvage_check import _side_stats, news_labels  # noqa: E402

VXN_LOOKBACK = 20


def night_legs(df: pd.DataFrame) -> list[dict]:
    days = {d: g for d, g in df.groupby(df.index.date)}
    dates = sorted(days)
    out, prev_close, prev_date = [], None, None
    for d in dates:
        g = days[d]
        rth = g[(g.index.hour > 9) | ((g.index.hour == 9) & (g.index.minute >= 30))]
        rth = rth[rth.index.hour < 16]
        if rth.empty:
            continue
        first = rth.index[0]
        has_open = first.hour == 9 and first.minute == 30
        last = rth.index[-1]
        has_close = last.hour == 15 and last.minute >= 55
        if has_open and prev_close is not None:
            pts = float(rth["Open"].iloc[0]) - prev_close
            gross = pts * MNQ_USD_PER_PT
            out.append({"date": str(d), "entry_date": str(prev_date), "points": round(pts, 2),
                        "usd_gross_1": round(gross, 2), "usd_net_1": round(gross - ASSUMED_COST_USD_PER_MICRO_RT, 2),
                        "r_net": 0.0, "weekend": pd.Timestamp(d).weekday() == 0})
        prev_close, prev_date = (float(rth["Close"].iloc[-1]), d) if has_close else (None, None)
    return out


def vxn_labels_entry(dates: list) -> dict:
    from market_state_primitives_v2 import _load_vxn_daily
    vxn = _load_vxn_daily()
    idx = pd.Index(sorted(set(vxn.index) | set(dates)))
    v = vxn.reindex(idx).ffill()
    trailing = v.rolling(VXN_LOOKBACK, min_periods=VXN_LOOKBACK).mean()
    rel = (v / trailing).shift(2)          # D-2's close vs its trailing mean, as known at D-1 16:00
    return {d: ("HIGH" if rel.get(d, float("nan")) > 1 else ("LOW" if rel.get(d, float("nan")) <= 1 else "UNKNOWN")) for d in dates}


def narrow_labels(df: pd.DataFrame, dates: list) -> dict:
    from volatility_conditioning import build_conditioning_frame
    cond = build_conditioning_frame(df)
    return {d: ("NARROW" if (d in cond.index and bool(cond.loc[d, "prior_day_narrow"])) else
                ("WIDE" if d in cond.index else "UNKNOWN")) for d in dates}


def split(trades, key, name):
    groups: dict = {}
    for t in trades:
        groups.setdefault(t[key], []).append(t)
    sides = {k: _side_stats(v) for k, v in sorted(groups.items())}
    for k, v in groups.items():
        sides[k]["avg_pts"] = round(sum(x["points"] for x in v) / len(v), 3)
    return {"condition": name, "sides": sides}


def run(df: pd.DataFrame) -> dict:
    legs = night_legs(df)
    dates = [pd.Timestamp(t["date"]).date() for t in legs]
    vx, nr, nw = vxn_labels_entry(dates), narrow_labels(df, dates), news_labels(dates)
    for t, d in zip(legs, dates):
        t["vxn"], t["prior_day"], t["news"] = vx[d], nr[d], nw[d]
        t["weekend"] = "WEEKEND" if t["weekend"] else "WEEKDAY"
    allc = _side_stats(legs); allc["avg_pts"] = round(sum(x["points"] for x in legs) / len(legs), 3)
    return {"trade": "long 1 micro at 16:00 close (D-1) -> flat at 09:30 open (D), no stop, ASSUMED $6.00 RT",
            "slice": "discovery", "n": len(legs), "all": allc,
            "menu": [split(legs, "vxn", "1. VXN regime (D-2 close vs trailing-20, known at entry)"),
                     split(legs, "prior_day", "2. prior-day range contraction (prior_day_narrow of D, known at entry)"),
                     {"condition": "3. time of day", "sides": {"FIXED_1600_0930": allc}},
                     split(legs, "news", "4. scheduled-news day (D in FOMC/CPI/NFP)"),
                     split(legs, "weekend", "info: weekend leg (Fri close -> Mon open) -- NOT a menu condition")],
            "cross": split([t for t in legs if t["vxn"] != "UNKNOWN"],
                           "vxn", "1 x 4 not computed -- single conditions only (s.7 menu)")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    from data_loader import load_price_data
    from data_split import get_discovery_data
    df, synthetic = load_price_data(context="study_s002_night_leg_menu", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    res = run(get_discovery_data(df))
    print(f"NIGHT LEG, Discovery: n={res['n']}  net ${res['all']['net_usd_1']:,.2f} at 1 micro  "
          f"win {res['all']['win_rate']}  avg {res['all']['avg_pts']} pts/session")
    for m in res["menu"]:
        print(f"  {m['condition']}")
        for k, s in m["sides"].items():
            print(f"    {k:10s} n={s['n']:5d}  net ${s['net_usd_1']:>10,.2f}  win {s['win_rate']}  avg {s['avg_pts']} pts  profitable={s['profitable']}")
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, default=str))
        print(f"detail -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
