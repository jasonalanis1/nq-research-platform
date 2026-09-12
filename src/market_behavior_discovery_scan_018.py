"""
market_behavior_discovery_scan_018.py
========================================

Scan 018. Draws Entry 15 (map anchor M9) from research/idea_inventory.md:
Nasdaq-100 quarterly rebalance close-window volume/move vs. normal days,
next-day reaction. Mechanism doc written BEFORE this scan:
research/mechanisms/nasdaq-rebalance-close-window-m9.md.

Frozen scope (mechanism doc Section 6):
  - close_move_vs_atr = (16:00 RTH close - 15:50 close) / ATR14, ABSOLUTE
    VALUE (this is a magnitude claim -- rebalance flow is directionless in
    principle -- not a signed claim).
  - close_volume_vs_norm = volume in [15:50, 16:00) / trailing-20-day mean
    of that same window (shifted one day).
  - is_rebalance_day = the calendar day is a Nasdaq quarterly quad-witching
    Friday (src/nasdaq_rebalance_calendar.QUARTERLY_REBALANCE_FRIDAYS).
  - P1 (gating, single pre-registered comparison): mean |close_move_vs_atr|
    AND mean close_volume_vs_norm on rebalance days vs. all other (normal)
    days, bootstrap difference of means. Credible if BOTH differences are
    positive with 90% CI entirely above zero (rebalance days show more
    close-window move AND more close-window volume than normal days).
  - P2 (reported, read only if P1 passes): next full session's sign-
    adjusted (adjusted by the SIGNED close move's own sign) open-to-close
    return, following rebalance days vs. following normal days -- tests
    for partial reversal.

Reuses the close-window construction from market_behavior_discovery_scan_013
(same [15:50,16:00) window, same ATR14/volume-norm definitions) so the two
close-window studies are directly comparable.

ONE pre-registered shot; no retuning. scan_018_2026-09-12 (2 cells: move,
volume) registered in src/project_wide_multiplicity.py BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_018.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from nasdaq_rebalance_calendar import QUARTERLY_REBALANCE_FRIDAY_SET

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_WINDOW = 14
VOL_LOOKBACK = 20


def bootstrap_diff_ci(a, b, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]; b = b[~np.isnan(b)]
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    d = rng.choice(a, size=(n_bootstrap, len(a)), replace=True).mean(axis=1) - rng.choice(b, size=(n_bootstrap, len(b)), replace=True).mean(axis=1)
    return float(np.percentile(d, 5)), float(np.percentile(d, 95))


def summarize(vals) -> dict:
    vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
    n = len(vals)
    if n < 2:
        return {"n": n, "mean": float("nan")}
    return {"n": n, "mean": float(np.mean(vals))}


def build_frame(disc: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for day, d in disc.groupby(disc.index.date):
        rth = d.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue
        t = rth.index.time
        pre1550 = rth[t < pd.Timestamp("15:50").time()]
        win = rth.between_time("15:50", "16:00", inclusive="left")
        if pre1550.empty or win.empty:
            continue
        rows.append({"date": day, "rth_range": float(rth["High"].max() - rth["Low"].min()),
                     "c1550": float(pre1550["Close"].iloc[-1]), "c1600": float(win["Close"].iloc[-1]),
                     "o930": float(rth["Open"].iloc[0]), "close_vol": float(win["Volume"].sum())})
    f = pd.DataFrame(rows).set_index("date").sort_index()
    f["atr14"] = f["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    f["close_volume_vs_norm"] = f["close_vol"] / f["close_vol"].rolling(VOL_LOOKBACK, min_periods=VOL_LOOKBACK).mean().shift(1)
    f["signed_close_move_vs_atr"] = (f["c1600"] - f["c1550"]) / f["atr14"]
    f["abs_close_move_vs_atr"] = f["signed_close_move_vs_atr"].abs()
    sgn = np.sign(f["signed_close_move_vs_atr"]).replace(0, 1)
    f["next_session_sign_adj"] = sgn * (f["o930"].shift(-1) - f["c1600"]) / f["atr14"]
    # NOTE: this is a CONTINUATION-signed measure (positive = next session
    # extends the close move); P2's "reversal" reads as negative here.
    return f.dropna(subset=["atr14", "close_volume_vs_norm", "abs_close_move_vs_atr"]).copy()


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 018 (Entry 15 / M9: Nasdaq-100 quarterly rebalance close-window)"); print("=" * 78)
    df, syn = load_price_data(context="market_behavior_discovery_scan_018.py")
    if syn:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(df)
    f = build_frame(disc)
    print(f"Discovery days usable: {len(f)}")
    f["is_rebalance_day"] = [d in QUARTERLY_REBALANCE_FRIDAY_SET for d in f.index]
    n_reb = int(f["is_rebalance_day"].sum())
    print(f"Rebalance Fridays present in Discovery (usable): {n_reb}")

    reb = f[f["is_rebalance_day"]]
    normal = f[~f["is_rebalance_day"]]

    move_reb = reb["abs_close_move_vs_atr"].tolist(); move_norm = normal["abs_close_move_vs_atr"].tolist()
    vol_reb = reb["close_volume_vs_norm"].tolist(); vol_norm = normal["close_volume_vs_norm"].tolist()

    move_diff_ci = bootstrap_diff_ci(move_reb, move_norm)
    vol_diff_ci = bootstrap_diff_ci(vol_reb, vol_norm)
    move_diff_mean = float(np.mean(move_reb) - np.mean(move_norm))
    vol_diff_mean = float(np.mean(vol_reb) - np.mean(vol_norm))
    move_credible = move_diff_ci[0] > 0
    vol_credible = vol_diff_ci[0] > 0

    print(f"\nGATING (P1a, close-window |move| rebalance vs normal): reb_mean={np.mean(move_reb):.4f} normal_mean={np.mean(move_norm):.4f} diff={move_diff_mean:+.4f} ci_90=({move_diff_ci[0]:+.4f},{move_diff_ci[1]:+.4f}) credible={move_credible}")
    print(f"GATING (P1b, close-window volume ratio rebalance vs normal): reb_mean={np.mean(vol_reb):.4f} normal_mean={np.mean(vol_norm):.4f} diff={vol_diff_mean:+.4f} ci_90=({vol_diff_ci[0]:+.4f},{vol_diff_ci[1]:+.4f}) credible={vol_credible}")
    verdict = "P1_PASS" if (move_credible and vol_credible) else "P1_FAIL"
    print(f"\nVerdict (BOTH move and volume must be credible): {verdict}")

    p2 = {}
    if verdict == "P1_PASS":
        reb_next = summarize(reb["next_session_sign_adj"].dropna().tolist())
        norm_next = summarize(normal["next_session_sign_adj"].dropna().tolist())
        p2 = {"rebalance_days_next_session": reb_next, "normal_days_next_session": norm_next}
        print(f"  P2 next-session sign-adjusted: rebalance n={reb_next['n']} mean={reb_next['mean']:+.4f} | normal n={norm_next['n']} mean={norm_next['mean']:+.4f} (negative = reversal)")
    else:
        print("  P1 failed -- P2 next-session comparison not mined per the pre-registered scope (reported only, read if P1 passes).")

    out = {"n_days": int(len(f)), "n_rebalance_days": n_reb, "n_normal_days": int(len(normal)),
           "close_move_diff": {"rebalance_mean": float(np.mean(move_reb)), "normal_mean": float(np.mean(move_norm)), "diff_mean": move_diff_mean, "ci_90": list(move_diff_ci), "credible": bool(move_credible)},
           "close_volume_diff": {"rebalance_mean": float(np.mean(vol_reb)), "normal_mean": float(np.mean(vol_norm)), "diff_mean": vol_diff_mean, "ci_90": list(vol_diff_ci), "credible": bool(vol_credible)},
           "gating_verdict": verdict, "p2_next_session": p2}
    (DATA_DIR / "market_behavior_discovery_scan_018_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_018_results.json'}")


if __name__ == "__main__":
    main()
