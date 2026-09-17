"""
study_s004_scrutiny.py -- MEASUREMENT of S004's existing screen result, before
S004 is allowed anywhere near the paper book.

WHY THIS EXISTS
  S004 is H118's lineage -- the family that passed Discovery, Validation and
  Holdout and turned out to be the stock market going up. Its screen (arm A,
  554 trades, +76.0131 gross pt/trade) clears its own-drift baseline (arm B,
  1,663 trades, +60.7698 gross pt/trade) by +15.2433 pt/trade = +0.0118 R. The
  baseline gate is a POINT ESTIMATE on 10-session holds that overlap heavily:
  554 trades are nowhere near 554 independent observations.

WHAT THIS IS NOT
  It does not re-run the screen, does not change a parameter, does not touch the
  frozen spec (research/infrastructure/strategy-specs/S004-vwap-dist-low-drift-vs-own-drift.md)
  or the frozen module (src/strategy_s004_vwap_dist_low_drift.py). It reads
  data/screen_S004_with_baseline.json -- the frozen screen output -- and measures
  it. Directive s.13.

WHAT IT MEASURES
  1. OVERLAP-CORRECTED SIGNIFICANCE. Calendar-time moving-block bootstrap
     (the house convention: src/gate_conditions_hyp162.py resamples blocks of
     consecutive SESSIONS and re-derives the split inside each resample;
     src/baseline_relative.py:block_bootstrap_diff_ci uses block = the overlap
     length). Blocks of 10 and 20 consecutive sessions, block >= the 10-session
     hold. Plus a non-overlapping subsample: signal trades thinned so no two
     holds overlap.
  2. IS THE MARGIN LEVERAGED BETA? The two arms take the IDENTICAL trade -- the
     only difference is which sessions are selected -- so "exposure" here is
     (a) how volatile the selected windows are and (b) how large the index was
     when they happened. Points are not exposure-matched across an index that
     rose ~10x over the slice. The margin is therefore re-measured in three
     units: POINTS (the screen's unit), PERCENT of the entry price (notional-
     matched), and R = pts / (4 x atr14) (volatility-matched). Holding time is
     identical by construction (10 RTH sessions, both arms).
  3. SUBPERIOD STABILITY. Per calendar year and per chronological half, margin =
     mean(signal) - mean(all sessions in the same subperiod), in all three units.
  4. THE PLACEBO SUITE the project already owns: src/integrity_checks.py
     run_suite() on the signal arm against the CORRECT null (the own-drift
     baseline mean), with the full population and the selector mask so the
     placebo leg can actually run.

USAGE
    python3 src/study_s004_scrutiny.py [--out data/s004_scrutiny.json]
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
import integrity_checks  # noqa: E402

PROJECT_ROOT = ROOT.parent
SCREEN = PROJECT_ROOT / "data" / "screen_S004_with_baseline.json"
HOLD_SESSIONS = 10
ATR_STOP_MULTIPLE = 4.0
N_BOOT = 3000
SEED = 7
ALPHA = 0.10          # 90% interval, the project's convention


def load_table() -> pd.DataFrame:
    """One row per BASELINE session (the full population), in date order, with a
    boolean flag for the sessions the LOW-tercile filter selected."""
    d = json.loads(SCREEN.read_text())
    a = {t["date"]: t for t in d["strategy"]["trades_detail"]}
    b = {t["date"]: t for t in d["own_drift_baseline"]["trades_detail"]}
    assert set(a) <= set(b), "arm A must be a subset of arm B"
    for k, t in a.items():
        assert abs(t["pts_gross"] - b[k]["pts_gross"]) < 1e-6, f"arm A/B disagree on {k}"
    rows = []
    for date in sorted(b):
        t = b[date]
        atr = float(t["context"]["atr14"])
        rows.append({
            "date": date,
            "signal": date in a,
            "pts": float(t["pts_gross"]),
            "pct": 100.0 * float(t["pts_gross"]) / float(t["entry"]),
            "r": float(t["pts_gross"]) / (ATR_STOP_MULTIPLE * atr),
            "entry": float(t["entry"]),
            "atr14": atr,
            "risk_points": float(t["risk_points"]),
            "exit_reason": t["exit_reason"],
            "vwap_dist": float(t["context"]["vwap_dist_vs_atr"]),
        })
    df = pd.DataFrame(rows)
    df["ts"] = pd.to_datetime(df["date"])
    return df.sort_values("ts").reset_index(drop=True), d


def margin(df: pd.DataFrame, unit: str) -> float:
    """mean(signal sessions) - mean(ALL sessions): the two-nulls convention
    (src/baseline_relative.py) exactly as the screen's gate computes it."""
    s = df.loc[df["signal"], unit].to_numpy(float)
    a = df[unit].to_numpy(float)
    if len(s) < 2 or len(a) < 2:
        return float("nan")
    return float(s.mean() - a.mean())


def calendar_block_bootstrap(df: pd.DataFrame, unit: str, block: int,
                             n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    """Resample blocks of `block` CONSECUTIVE SESSIONS, then re-derive the
    signal/all split INSIDE each resample -- gate_conditions_hyp162's convention.
    A block at least as long as the hold keeps each overlapping cluster of trades
    together, so the resample inherits the real autocorrelation."""
    rng = np.random.default_rng(seed)
    vals = df[unit].to_numpy(float)
    flag = df["signal"].to_numpy(bool)
    n = len(vals)
    n_blocks = int(np.ceil(n / block))
    out = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, n - block + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).reshape(-1)[:n]
        v, f = vals[idx], flag[idx]
        out[i] = (v[f].mean() - v.mean()) if f.sum() >= 2 else np.nan
    out = out[np.isfinite(out)]
    lo, hi = np.percentile(out, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)])
    return {"unit": unit, "block_sessions": block, "n_boot": int(len(out)),
            "point_estimate": round(margin(df, unit), 6),
            "ci90": [round(float(lo), 6), round(float(hi), 6)],
            "clears_zero": bool(lo > 0 or hi < 0),
            "share_below_zero": round(float((out <= 0).mean()), 4)}


def non_overlapping(df: pd.DataFrame, unit: str, offset: int = 0) -> dict:
    """Thin the SIGNAL trades so no two holds overlap (>= HOLD_SESSIONS sessions
    apart), and thin the population the same way, so the margin is computed on
    genuinely independent observations. `offset` picks a different thinning."""
    idx_sig = np.flatnonzero(df["signal"].to_numpy(bool))
    keep, last = [], -10**9
    for i in idx_sig[offset:]:
        if i - last >= HOLD_SESSIONS:
            keep.append(i)
            last = i
    all_keep, last = [], -10**9
    for i in range(offset, len(df)):
        if i - last >= HOLD_SESSIONS:
            all_keep.append(i)
            last = i
    s = df.loc[keep, unit].to_numpy(float)
    a = df.loc[all_keep, unit].to_numpy(float)
    diff = float(s.mean() - a.mean())
    # iid bootstrap is legitimate here: these observations do not overlap
    rng = np.random.default_rng(SEED + offset)
    d = (rng.choice(s, size=(N_BOOT, len(s)), replace=True).mean(axis=1)
         - rng.choice(a, size=(N_BOOT, len(a)), replace=True).mean(axis=1))
    lo, hi = np.percentile(d, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)])
    return {"unit": unit, "offset": offset, "n_signal": len(s), "n_all": len(a),
            "point_estimate": round(diff, 6),
            "ci90": [round(float(lo), 6), round(float(hi), 6)],
            "clears_zero": bool(lo > 0 or hi < 0)}


def exposure_profile(df: pd.DataFrame) -> dict:
    """Does the filter select more volatile / differently-priced windows? If the
    margin is leveraged beta, the selected sessions carry more exposure per
    trade -- higher ATR relative to price -- and the points margin shrinks or
    vanishes once the unit is exposure-matched."""
    s, a = df[df["signal"]], df
    return {
        "atr14_mean_signal": round(float(s["atr14"].mean()), 4),
        "atr14_mean_all": round(float(a["atr14"].mean()), 4),
        "atr_over_price_signal_pct": round(float((100 * s["atr14"] / s["entry"]).mean()), 4),
        "atr_over_price_all_pct": round(float((100 * a["atr14"] / a["entry"]).mean()), 4),
        "entry_price_mean_signal": round(float(s["entry"].mean()), 2),
        "entry_price_mean_all": round(float(a["entry"].mean()), 2),
        "stop_rate_signal": round(float((s["exit_reason"] == "stop").mean()), 4),
        "stop_rate_all": round(float((a["exit_reason"] == "stop").mean()), 4),
        "hold_sessions_both_arms": HOLD_SESSIONS,
        "note": ("Both arms take the IDENTICAL trade -- same entry clock, same 10-session hold, "
                 "same 4.0 x atr14 stop, 1 micro -- so holding time and contract size are matched "
                 "by construction. What is NOT matched in POINTS is notional (the index rose ~10x "
                 "over the slice) and volatility (atr14 varies 5x). PERCENT and R are the "
                 "exposure-matched units."),
    }


def subperiods(df: pd.DataFrame) -> dict:
    out = {"by_year": [], "by_half": []}
    df = df.copy()
    df["year"] = df["ts"].dt.year
    for y, g in df.groupby("year"):
        row = {"period": str(y), "n_signal": int(g["signal"].sum()), "n_all": int(len(g))}
        for u in ("pts", "pct", "r"):
            row[f"margin_{u}"] = round(margin(g, u), 6) if row["n_signal"] >= 2 else None
            row[f"signal_mean_{u}"] = round(float(g.loc[g["signal"], u].mean()), 6) if row["n_signal"] else None
            row[f"all_mean_{u}"] = round(float(g[u].mean()), 6)
        out["by_year"].append(row)
    mid = len(df) // 2
    for label, g in (("first half", df.iloc[:mid]), ("second half", df.iloc[mid:])):
        row = {"period": f"{label} ({g['date'].iloc[0]}..{g['date'].iloc[-1]})",
               "n_signal": int(g["signal"].sum()), "n_all": int(len(g))}
        for u in ("pts", "pct", "r"):
            row[f"margin_{u}"] = round(margin(g, u), 6)
        out["by_half"].append(row)
    n_pos = sum(1 for r in out["by_year"] if r["margin_pts"] is not None and r["margin_pts"] > 0)
    n_yr = sum(1 for r in out["by_year"] if r["margin_pts"] is not None)
    out["years_with_positive_points_margin"] = f"{n_pos}/{n_yr}"
    n_pos_r = sum(1 for r in out["by_year"] if r["margin_r"] is not None and r["margin_r"] > 0)
    out["years_with_positive_r_margin"] = f"{n_pos_r}/{n_yr}"
    return out


def integrity(df: pd.DataFrame) -> dict:
    """The project's own mechanical suite, run against the CORRECT null -- the
    own-drift baseline mean -- with the full population and the selector mask so
    the placebo leg is not silently skipped."""
    sig = df[df["signal"]]
    obs = [{"date": r["date"], "value": r["pts"], "risk_points": r["risk_points"]}
           for _, r in sig.iterrows()]
    null_value = float(df["pts"].mean())
    return integrity_checks.run_suite(
        obs, null_value=null_value,
        null_label=("S004's own-drift baseline: the identical trade on every session with the "
                    "descriptor, filter off (arm B), %.4f gross pt/trade" % null_value),
        population=df["pts"].to_numpy(float), mask=df["signal"].to_numpy(bool),
        candidate="S004 (margin vs own-drift baseline, points)", seed=SEED)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(PROJECT_ROOT / "data" / "s004_scrutiny.json"))
    a = ap.parse_args(argv)

    df, screen = load_table()
    units = ("pts", "pct", "r")

    res = {
        "source": str(SCREEN.relative_to(PROJECT_ROOT)),
        "screen_gate": screen["gate"],
        "n_sessions_population": int(len(df)),
        "n_signal_trades": int(df["signal"].sum()),
        "date_range": [df["date"].iloc[0], df["date"].iloc[-1]],
        "point_estimates": {u: round(margin(df, u), 6) for u in units},
        "signal_mean": {u: round(float(df.loc[df["signal"], u].mean()), 6) for u in units},
        "all_mean": {u: round(float(df[u].mean()), 6) for u in units},
        "overlap_correction": {
            "calendar_block_bootstrap": [calendar_block_bootstrap(df, u, b)
                                         for u in units for b in (10, 20)],
            "non_overlapping": [non_overlapping(df, u, off) for u in units for off in (0, 5)],
            "effective_independent_signal_trades": int(np.ceil(df["signal"].sum() / HOLD_SESSIONS)),
        },
        "exposure": exposure_profile(df),
        "subperiods": subperiods(df),
        "integrity_suite": integrity(df),
    }
    Path(a.out).write_text(json.dumps(res, indent=2, default=str))

    print("=" * 78)
    print("S004 SCRUTINY -- measurement of the FROZEN screen result, no re-run, no retune")
    print("=" * 78)
    print(f"  population {res['n_sessions_population']} baseline sessions, "
          f"{res['n_signal_trades']} signal trades, {res['date_range'][0]}..{res['date_range'][1]}")
    print(f"  margin point estimates: " + "  ".join(
        f"{u}={res['point_estimates'][u]:+.6f}" for u in units))
    print("\n  1. OVERLAP CORRECTION (90% intervals)")
    for c in res["overlap_correction"]["calendar_block_bootstrap"]:
        print(f"     block bootstrap {c['unit']:>4} block={c['block_sessions']:>2} sessions: "
              f"{c['point_estimate']:+.6f}  CI90 [{c['ci90'][0]:+.6f}, {c['ci90'][1]:+.6f}]  "
              f"clears zero: {c['clears_zero']}  P(margin<=0)={c['share_below_zero']:.3f}")
    for c in res["overlap_correction"]["non_overlapping"]:
        print(f"     non-overlapping  {c['unit']:>4} offset={c['offset']}: n_sig={c['n_signal']} "
              f"n_all={c['n_all']}  {c['point_estimate']:+.6f}  "
              f"CI90 [{c['ci90'][0]:+.6f}, {c['ci90'][1]:+.6f}]  clears zero: {c['clears_zero']}")
    print("\n  2. EXPOSURE")
    for k, v in res["exposure"].items():
        if k != "note":
            print(f"     {k:<32} {v}")
    print("\n  3. SUBPERIODS")
    for r in res["subperiods"]["by_year"]:
        print(f"     {r['period']}  n_sig={r['n_signal']:>3}/{r['n_all']:>4}   "
              f"pts {r['margin_pts'] if r['margin_pts'] is None else format(r['margin_pts'], '+9.3f')}   "
              f"pct {r['margin_pct'] if r['margin_pct'] is None else format(r['margin_pct'], '+8.4f')}   "
              f"R   {r['margin_r'] if r['margin_r'] is None else format(r['margin_r'], '+8.4f')}")
    for r in res["subperiods"]["by_half"]:
        print(f"     {r['period']}  n_sig={r['n_signal']}/{r['n_all']}  "
              f"pts {r['margin_pts']:+.3f}  pct {r['margin_pct']:+.4f}  R {r['margin_r']:+.4f}")
    print(f"     years with a positive POINTS margin: {res['subperiods']['years_with_positive_points_margin']}"
          f"   positive R margin: {res['subperiods']['years_with_positive_r_margin']}")
    print("\n  4. INTEGRITY SUITE (src/integrity_checks.py, null = own-drift baseline)")
    for c in res["integrity_suite"]["checks"]:
        print(f"     {c['status']:<15}{c['check']:<30} n={c['n']}  {c.get('detail','')}")
    print("     " + res["integrity_suite"]["session_report_row"])
    print(f"\n  written: {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
