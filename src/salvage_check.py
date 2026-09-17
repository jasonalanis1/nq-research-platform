"""
salvage_check.py -- the SALVAGE CHECK (standing directive s.7): before a strategy
is closed, break its trade list down by the FIXED menu of conditions and ask
when it did work. Menu only -- the Integrity Gate rejects any salvage that reads
as "find the slice that looks good" -- plus the conditions the strategy's own
spec named under "where this should fail".

THE MENU (s.7), as computed here for a trade dated D:
  1. volatility   VXN vs its trailing level: market_state_primitives_v2's
                  vxn_level_vs_trailing convention (prior day's VXN close over
                  its trailing-20-day mean, minus 1) > 0 -> HIGH, else LOW
  2. trend/range  the day's OWN RTH range vs the trailing-20-day average RTH
                  range (study_intraday_behavior_batch1.build_daily_frame):
                  ratio > 1 -> TREND (expansion), else RANGE. (Prior-day
                  contraction is the other half of this condition; when it is
                  the strategy's own filter it is not re-split.)
  3. time of day  the signal's trigger time: OPEN (< 09:30 ET pre-market /
                  cash-open window), MIDDAY (09:30-12:00), AFTERNOON (>= 12:00)
                  -- for S001 the split that matters is pre-09:30 vs after
  4. news day     D in the FOMC / CPI / NFP calendars (study_fomc_volatility,
                  study_economic_calendar) -> NEWS, else QUIET
  + spec-named    any `context` field the spec named (e.g. level_source,
                  direction), passed with --extra

A condition side is called PROFITABLE when its net $ at 1 micro (ASSUMED costs
already inside every trade's usd_net_1, on src/cost_model.py's decision basis --
MNQ market entry, $2.60 = 1.30 index points per round trip, CORRECTED September
16th 2026 from the wrong $6.00/3.00-pt figure that charged a full-size NQ
commission to a micro) is > 0 AND it has at least MIN_N trades
(15, the s.6 floor a paper run needs to be judged at all); a profitable side with
fewer trades is reported as THIN, not spawned. One salvage per strategy.

USAGE
    python3 src/salvage_check.py data/screen_S001_2026-09-15.json --extra level_source,direction \
        --out data/salvage_S001_2026-09-15.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

MIN_N = 15
VXN_LOOKBACK = 20
RANGE_LOOKBACK = 20


def _side_stats(trades: list[dict]) -> dict:
    n = len(trades)
    net = round(sum(t["usd_net_1"] for t in trades), 2)
    wins = sum(1 for t in trades if t["usd_net_1"] > 0)
    avg_r = round(sum(t["r_net"] for t in trades) / n, 4) if n else None
    return {"n": n, "net_usd_1": net, "win_rate": round(wins / n, 3) if n else None, "avg_r_net": avg_r,
            "profitable": bool(n >= MIN_N and net > 0), "thin": n < MIN_N, "positive_but_thin": bool(n and n < MIN_N and net > 0)}


def split(trades: list[dict], label_fn, name: str) -> dict:
    groups: dict[str, list] = {}
    for t in trades:
        groups.setdefault(label_fn(t), []).append(t)
    return {"condition": name, "sides": {k: _side_stats(v) for k, v in sorted(groups.items())}}


def vxn_labels(dates: list[date]) -> dict:
    """FAIL-CLOSED (2026-09-16). A session past the VXN series' coverage end is
    REFUSED, not carried forward. Before this, the ffill below silently handed a
    two-week-old volatility reading to menu condition 1, so a salvage could be
    decided -- and a candidate spawned -- on a number that was never measured on
    the day it was attributed to."""
    from market_state_primitives_v2 import _load_vxn_daily
    from reference_data import ReferenceDataUnavailable, vxn_coverage_end
    end = vxn_coverage_end()
    past = sorted(d for d in set(dates) if d > end)
    if past:
        raise ReferenceDataUnavailable(
            "VXN", past[0], end,
            f"{len(past)} of {len(set(dates))} trade date(s) in this Salvage check lie past the series "
            f"(latest {past[-1]}). Salvage menu condition 1 cannot be judged on a carried-forward level.")
    vxn = _load_vxn_daily()
    idx = pd.Index(sorted(set(vxn.index) | set(dates)))
    v = vxn.reindex(idx).ffill()
    trailing = v.rolling(VXN_LOOKBACK, min_periods=VXN_LOOKBACK).mean().shift(1)
    rel = (v.shift(1) / trailing) - 1.0
    return {d: ("HIGH" if rel.get(d, float("nan")) > 0 else ("LOW" if rel.get(d, float("nan")) <= 0 else "UNKNOWN")) for d in dates}


def range_labels(df: pd.DataFrame, dates: list[date]) -> dict:
    from study_intraday_behavior_batch1 import build_daily_frame
    daily = build_daily_frame(df)
    avg = daily["range"].rolling(RANGE_LOOKBACK, min_periods=RANGE_LOOKBACK).mean().shift(1)
    ratio = daily["range"] / avg
    out = {}
    for d in dates:
        r = ratio.get(d, float("nan"))
        out[d] = "TREND" if r > 1 else ("RANGE" if r <= 1 else "UNKNOWN")
    return out


def news_labels(dates: list[date]) -> dict:
    """FAIL-CLOSED (2026-09-16). Menu condition 4 used to read `d in FOMC_SET`
    and call every miss QUIET -- so a 2026 date was "quiet" because the sourced
    lists stop in 2021, not because the day held no release. That is a fabricated
    classification. Coverage now comes from src/reference_data.py and a date past
    it raises rather than defaulting to QUIET."""
    from reference_data import scheduled_events_on
    return {d: ("NEWS" if scheduled_events_on(d) else "QUIET") for d in dates}


def tod_label(t: dict) -> str:
    ts = (t.get("context") or {}).get("trigger_time") or t.get("exit_time") or ""
    try:
        hm = pd.Timestamp(ts).strftime("%H:%M")
    except Exception:  # noqa: BLE001
        return "UNKNOWN"
    if hm < "09:30":
        return "OPEN_PRE0930"
    if hm < "12:00":
        return "MIDDAY_0930_1200" if hm >= "10:00" else "OPEN_0930_1000"
    return "AFTERNOON"


def run(trades: list[dict], df: pd.DataFrame | None, extra: list[str]) -> dict:
    dates = [pd.Timestamp(t["date"]).date() for t in trades]
    for t, d in zip(trades, dates):
        t["_d"] = d
    vx = vxn_labels(dates)
    rg = range_labels(df, dates) if df is not None else {d: "UNKNOWN" for d in dates}
    nw = news_labels(dates)
    results = [
        split(trades, lambda t: vx[t["_d"]], "1. volatility: VXN vs trailing (HIGH > trailing, LOW <= trailing)"),
        split(trades, lambda t: rg[t["_d"]], "2. trend vs range: the day's own RTH range vs trailing-20 average"),
        split(trades, tod_label, "3. time of day: signal trigger time"),
        split(trades, lambda t: nw[t["_d"]], "4. scheduled-news day (FOMC / CPI / NFP) vs quiet"),
    ]
    for field in extra:
        results.append(split(trades, lambda t, f=field: str((t.get("context") or {}).get(f, t.get(f, "UNKNOWN"))),
                             f"spec-named: {field}"))
    for t in trades:
        t.pop("_d", None)
    found = []
    thin = []
    for r in results:
        for side, s in r["sides"].items():
            if s["profitable"]:
                found.append({"condition": r["condition"], "side": side, **s})
            elif s["positive_but_thin"]:
                thin.append({"condition": r["condition"], "side": side, **s})
    return {"min_n": MIN_N, "n_trades": len(trades), "overall": _side_stats(trades), "conditions": results,
            "profitable_conditions": found, "positive_but_thin": thin,
            "verdict": ("condition found: " + "; ".join(f"{f['condition']} = {f['side']} (n={f['n']}, net ${f['net_usd_1']:+,.2f}, avg {f['avg_r_net']:+.3f}R)" for f in found)
                        if found else "nothing: no menu condition was profitable with >= %d trades" % MIN_N)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("screen_json")
    ap.add_argument("--extra", default="", help="comma-separated context fields the spec named")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-price-data", action="store_true", help="skip condition 2 (no price load)")
    a = ap.parse_args(argv)
    res = json.loads(Path(a.screen_json).read_text())
    trades = res["trades_detail"]
    df = None
    if not a.no_price_data:
        from data_loader import load_price_data
        from data_split import get_discovery_data
        full, synthetic = load_price_data(context="salvage_check", apply_holdout=True)
        if synthetic:
            raise SystemExit("synthetic data -- refusing")
        df = get_discovery_data(full)
    out = run(trades, df, [x for x in a.extra.split(",") if x])
    out["strategy_name"] = res.get("strategy_name"); out["screen_source"] = a.screen_json
    print("=" * 78)
    print(f"SALVAGE CHECK  {out['strategy_name']}  ({out['n_trades']} trades, overall net ${out['overall']['net_usd_1']:+,.2f} at 1 micro)")
    print("=" * 78)
    for r in out["conditions"]:
        print(f"  {r['condition']}")
        for side, s in r["sides"].items():
            tag = "PROFITABLE" if s["profitable"] else ("positive but THIN (< %d)" % MIN_N if s["positive_but_thin"] else "losing")
            print(f"      {side:<18} n={s['n']:<4} net ${s['net_usd_1']:+9,.2f}  win {s['win_rate']}  avg {s['avg_r_net']:+.3f}R  -> {tag}")
    print(f"\n  VERDICT: {out['verdict']}")
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1, default=str))
        print(f"  detail -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
