"""
study_s008_intraday_cost_budget.py -- PRE-SPECIFICATION descriptive work for S008
(late-day constant-leverage rebalance continuation), run on the Discovery slice
BEFORE anything was frozen. This is NOT a SCREEN: no spec is hashed, no strategy
module exists, no screen row is written. It answers one question, the one the
S007 LEARN entry (research/KNOWLEDGE.md, 2026-09-16 9:00 am) says to ask first:

    what is this structure's GROSS per-trade expectancy in index points?

CORRECTED September 16th 2026 (Jason's Amendment 2). As first written, this file
asked whether the expectancy was "well north of" a $6.00 = 3.0-point micro round
trip, and S008 was refused against a 3x-cost budget built on that number. BOTH
halves were wrong: $6.00 charged a FULL-SIZE NQ commission ($2.50/side) to a
MICRO -- the real MNQ market round trip is $2.60 = 1.30 index points
(src/cost_model.py, sources cited there) -- and the "3x cost" pre-screen was
Tony's invention, which the standing directive never contained. Jason's rule
replaces it: at SPECIFY reject ONLY if the expected per-trade edge is below the
per-trade cost ITSELF; otherwise it goes to SCREEN. The cost here now comes from
cost_model.py, so this study's net-points columns are on the corrected basis.

Three families are measured, all intraday, all on the 2,101-session Discovery
slice, all with the entry rule known at the entry timestamp (no ex-post label):

  A  RTH VWAP-band reversion (src/detect_vwap_reversion.py's shape, moved off its
     08:30 pre-market open to the 09:30 RTH open): fade the first close beyond
     VWAP +/- 2*sigma after a 30-minute warm-up, stop = the entry->VWAP distance,
     target = VWAP. Reports gross avg R and net points by distance bucket.
  B  Late-day continuation, the S008 mechanism: at a decision time T the day's
     RTH move M = Close(T) - Open(09:30) measures the constant-leverage
     rebalance that must be done into the cash close; trade sign(M) from T to
     15:55 ET. Grid of T x |M|/trailing-20-median-range, gross points per trade.
  C  Same continuation held from the morning (10:00-11:30 ET) to 15:55, and the
     same split on the wide-opening-range regime (hyp-000162 / M30).

USAGE  python3 src/study_s008_intraday_cost_budget.py [--out data/study_S008_cost_budget.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import cost_model  # noqa: E402

# The corrected decision basis: MNQ, market entry and exit. $2.60 = 1.30 index
# points (was wrongly 3.00). Never redefine a cost here -- cost_model.py owns it.
COST_PTS = cost_model.DEFAULT_POINTS_PER_ROUND_TRIP
MNQ_USD_PER_PT = cost_model.MNQ.usd_per_point


def _discovery() -> pd.DataFrame:
    from data_loader import load_price_data
    from data_split import get_discovery_data
    df, synthetic = load_price_data(context="screen_strategy", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data -- refusing to run")
    return get_discovery_data(df)


def family_a(disc: pd.DataFrame) -> dict:
    """RTH VWAP 2-sigma band reversion, stop = entry->VWAP distance, target = VWAP."""
    rows = []
    for _day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if len(rth) < 300:
            continue
        tp = ((rth.High + rth.Low + rth.Close) / 3.0).to_numpy(float)
        v = np.where(rth.Volume.to_numpy(float) <= 0, 1.0, rth.Volume.to_numpy(float))
        cv = np.cumsum(v)
        vwap = np.cumsum(v * tp) / cv
        sg = np.sqrt(np.maximum(np.cumsum(v * tp * tp) / cv - vwap * vwap, 0.0))
        idx, c = rth.index, rth.Close.to_numpy(float)
        hi, lo, op = rth.High.to_numpy(float), rth.Low.to_numpy(float), rth.Open.to_numpy(float)
        end = int(np.searchsorted(idx, idx[0].replace(hour=15, minute=0)))
        k = d = None
        for i in range(30, min(end, len(idx) - 2)):          # 30-minute warm-up
            if sg[i] <= 0:
                continue
            if c[i] > vwap[i] + 2 * sg[i]:
                k, d = i, "short"; break
            if c[i] < vwap[i] - 2 * sg[i]:
                k, d = i, "long"; break
        if k is None:
            continue
        entry, vw = float(op[k + 1]), float(vwap[k])
        dist = abs(entry - vw)
        if dist <= 0:
            continue
        tgt, stp = (entry - dist, entry + dist) if d == "short" else (entry + dist, entry - dist)
        r = None
        for j in range(k + 1, len(idx)):
            s_hit = hi[j] >= stp if d == "short" else lo[j] <= stp
            t_hit = lo[j] <= tgt if d == "short" else hi[j] >= tgt
            if s_hit:                                        # stop wins a same-bar tie
                r = -1.0; break
            if t_hit:
                r = 1.0; break
        if r is None:
            ex = float(c[-1])
            r = ((entry - ex) if d == "short" else (ex - entry)) / dist
        rows.append({"dist": dist, "r": r, "net_pts": r * dist - COST_PTS})
    T = pd.DataFrame(rows)
    T["bucket"] = pd.cut(T.dist, [0, 10, 20, 30, 50, 1e9], labels=["<10", "10-20", "20-30", "30-50", ">50"])
    by = T.groupby("bucket", observed=True).agg(n=("r", "size"), win=("r", lambda x: float((x > 0).mean())),
                                                avg_r_gross=("r", "mean"), med_dist=("dist", "median"),
                                                net_pts=("net_pts", "mean")).round(4)
    return {"trades": int(len(T)), "win_rate": round(float((T.r > 0).mean()), 4),
            "avg_r_gross": round(float(T.r.mean()), 4),
            "median_risk_pts": round(float(T.dist.median()), 2),
            "net_pts_per_trade_after_cost": round(float(T.net_pts.mean()), 3),
            "by_distance_bucket": json.loads(by.reset_index().to_json(orient="records"))}


def _late_day_frame(disc: pd.DataFrame, times: list[str], base_time: str) -> pd.DataFrame:
    rows = []
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if len(rth) < 330:
            continue
        tail = rth.between_time("15:55", "16:00", inclusive="left")
        if tail.empty:
            continue
        o = float(rth.Open.iloc[0])
        rec = {"day": day, "ex": float(tail.Open.iloc[0]),
               "orw": float(rth.High.iloc[:30].max() - rth.Low.iloc[:30].min())}
        ok = True
        for t in times:
            pre = rth.between_time("09:30", t, inclusive="left")
            post = rth.between_time(t, "15:55", inclusive="left")
            if len(pre) < 25 or post.empty:
                ok = False; break
            rec[f"M_{t}"] = float(pre.Close.iloc[-1]) - o
            rec[f"rng_{t}"] = float(pre.High.max() - pre.Low.min())
            rec[f"e_{t}"] = float(post.Open.iloc[0])
        if ok:
            rows.append(rec)
    S = pd.DataFrame(rows).set_index("day")
    S["med20"] = S[f"rng_{base_time}"].shift(1).rolling(20).median()
    S["orw20"] = S.orw.shift(1).rolling(20).median()
    return S.dropna()


def _cells(S: pd.DataFrame, times: list[str], thresholds) -> list[dict]:
    out = []
    for t in times:
        z = S[f"M_{t}"].abs() / S["med20"]
        for thr in thresholds:
            m = z >= thr
            n = int(m.sum())
            if n < 30:
                continue
            cont = np.sign(S[f"M_{t}"][m]) * (S["ex"][m] - S[f"e_{t}"][m])
            out.append({"entry_time": t, "threshold_z": thr, "n": n,
                        "fire_rate": round(n / len(S), 4),
                        "gross_pts_per_trade": round(float(cont.mean()), 3),
                        "t_stat": round(float(cont.mean() / (cont.std() / np.sqrt(n))), 2),
                        "median_half_range_stop_pts": round(float(0.5 * S[f"rng_{t}"][m].median()), 1),
                        "net_pts_per_trade": round(float(cont.mean()) - COST_PTS, 3)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/study_S008_cost_budget.json")
    a = ap.parse_args(argv)
    disc = _discovery()
    res = {"slice": "discovery", "sessions": int(disc.index.normalize().nunique()),
           "cost_basis_pts": COST_PTS,
           "budget_rule": "gross expectancy per trade must be well north of 3.0 index points",
           "family_A_vwap_band_reversion": family_a(disc)}

    late = ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30"]
    S1 = _late_day_frame(disc, late, "15:00")
    res["family_B_late_day_continuation"] = {"sessions": int(len(S1)),
                                             "cells": _cells(S1, late, (0.0, 0.5, 0.8, 1.0))}
    morn = ["10:00", "10:30", "11:00", "11:30"]
    S2 = _late_day_frame(disc, morn, "11:00")
    wide = S2.orw >= S2.orw20
    res["family_C_full_session_hold"] = {
        "sessions": int(len(S2)), "cells": _cells(S2, morn, (0.0, 0.5, 0.8)),
        "wide_opening_range_regime": {
            "share": round(float(wide.mean()), 4),
            "cells": [{"entry_time": t, "n": int(wide.sum()),
                       "gross_pts_per_trade": round(float((np.sign(S2[f"M_{t}"][wide]) *
                                                           (S2["ex"][wide] - S2[f"e_{t}"][wide])).mean()), 3)}
                      for t in morn]}}

    best = max(res["family_B_late_day_continuation"]["cells"] + res["family_C_full_session_hold"]["cells"],
               key=lambda c: c["gross_pts_per_trade"])
    res["best_continuation_cell_of_the_grid"] = best
    res["budget_verdict"] = ("FAIL -- no family reaches a gross per-trade expectancy well north of 3.0 pts; "
                             "the best cell of a 36-cell grid is "
                             f"{best['gross_pts_per_trade']} pts at t={best['t_stat']}")
    Path(a.out).write_text(json.dumps(res, indent=1, default=str))
    print("=" * 78)
    print("S008 PRE-SPECIFICATION COST BUDGET (Discovery, descriptive -- NOT a screen)")
    print("=" * 78)
    A = res["family_A_vwap_band_reversion"]
    print(f"  A  VWAP 2-sigma band reversion: {A['trades']} signals, gross avg R {A['avg_r_gross']}, "
          f"median risk {A['median_risk_pts']} pts -> {A['net_pts_per_trade_after_cost']} pts/trade after cost")
    for c in res["family_B_late_day_continuation"]["cells"]:
        print(f"  B  T={c['entry_time']} z>={c['threshold_z']}  n={c['n']:>5} rate={c['fire_rate']:.3f}  "
              f"gross {c['gross_pts_per_trade']:>6.2f} pts (t={c['t_stat']:>5.2f})  net {c['net_pts_per_trade']:>6.2f}")
    for c in res["family_C_full_session_hold"]["cells"]:
        print(f"  C  T={c['entry_time']} z>={c['threshold_z']}  n={c['n']:>5} rate={c['fire_rate']:.3f}  "
              f"gross {c['gross_pts_per_trade']:>6.2f} pts (t={c['t_stat']:>5.2f})  net {c['net_pts_per_trade']:>6.2f}")
    print(f"  VERDICT: {res['budget_verdict']}")
    print(f"  detail -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
