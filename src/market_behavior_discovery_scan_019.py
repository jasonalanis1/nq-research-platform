"""
market_behavior_discovery_scan_019.py
========================================

Scan 019. Draws Entry 16 (map anchor M12) from research/idea_inventory.md:
cross-asset correlation CONVERGENCE across the NQ/ZN/6E/CL basket as a
forced-delevering trigger for risk-parity / vol-targeting books, measured
as NQ forward 1-3 day drift.

Mechanism doc written BEFORE this scan:
research/mechanisms/cross-asset-correlation-convergence-m12.md

Frozen scope (mechanism doc Section 6):
  - Daily log returns for NQ, ZN, 6E, CL from each instrument's reference
    close, via study_volatility_regime.compute_daily_ref_closes and
    compute_daily_log_returns, both reused UNMODIFIED.
  - avg_corr[t] = mean of the six pairwise Pearson correlations over the
    20 trading days ending at t (inclusive of t -- known at t's close).
  - delta_corr[t] = avg_corr[t] - avg_corr[t-5] on the common calendar.
  - Terciles of delta_corr frozen ONCE on the full Discovery slice.
  - Outcome: (NQ ref close at t+h - NQ ref close at t) / ATR14 at t,
    ATR14 = trailing 14-day mean RTH range through t-1 (no lookahead).
  - 9 cells (3 terciles x h in {1,2,3}). GATING = HIGH tercile at h=3,
    claim: mean credibly NEGATIVE (90% bootstrap CI entirely below zero).

BINDING CONFOUND CHECK (mechanism doc Section 5 -- required, pre-
registered, not optional): correlation spikes cluster inside selloffs, so
this scan MUST report (1) mean trailing 5-day NQ return by tercile and
(2) the gating cell split by the SIGN of that trailing return. If the
negative drift lives ONLY in the already-falling subset, the entry closes
as the already-closed momentum/continuation family restated, NOT as a
finding -- regardless of how good the headline number looks.

ONE pre-registered shot; no retuning. scan_019_2026-09-12 (9 cells)
registered in src/project_wide_multiplicity.py BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_019.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes, compute_daily_log_returns
from market_behavior_discovery_scan_012 import rth_daily

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_WINDOW = 14
CORR_WINDOW = 20
DELTA_LAG = 5
HORIZONS = (1, 2, 3)
BASKET = ["NQ", "ZN", "6E", "CL"]


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = rng.choice(v, size=(n_bootstrap, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def summarize(vals) -> dict:
    vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
    n = len(vals)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": [float("nan"), float("nan")],
                "credible_vs_zero": False, "direction": "insufficient_n"}
    m = float(np.mean(vals))
    ci = bootstrap_mean_ci(vals)
    credible = ci[0] > 0 or ci[1] < 0
    direction = "positive" if (credible and ci[0] > 0) else ("negative" if (credible and ci[1] < 0) else "null")
    return {"n": n, "mean": m, "ci_90": list(ci), "credible_vs_zero": bool(credible), "direction": direction}


def daily_returns_for(symbol: str) -> dict:
    """day -> daily log return, Discovery slice only. Reuses the project's
    existing reference-close and log-return functions unmodified."""
    df, syn = load_price_data(context="market_behavior_discovery_scan_019.py", symbol=symbol)
    if syn:
        raise RuntimeError(f"synthetic data for {symbol}")
    disc = get_discovery_data(df)
    day_groups = {day: sub for day, sub in disc.groupby(disc.index.date)}
    return compute_daily_log_returns(compute_daily_ref_closes(day_groups)), day_groups


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 019 (Entry 16 / M12: cross-asset correlation convergence)")
    print("=" * 78)

    returns = {}
    nq_day_groups = None
    for sym in BASKET:
        r, groups = daily_returns_for(sym)
        returns[sym] = r
        if sym == "NQ":
            nq_day_groups = groups
        print(f"  {sym}: {len(r)} daily returns")

    # Common calendar: days where ALL FOUR instruments have a return.
    common = sorted(set.intersection(*[set(returns[s].keys()) for s in BASKET]))
    print(f"Common trading days (all 4 instruments): {len(common)}")

    ret_matrix = np.array([[returns[s][d] for s in BASKET] for d in common])  # rows = days

    # avg_corr[t]: mean of 6 pairwise correlations over the CORR_WINDOW days ending at t.
    avg_corr = {}
    for i in range(CORR_WINDOW - 1, len(common)):
        w = ret_matrix[i - CORR_WINDOW + 1: i + 1]
        cm = np.corrcoef(w, rowvar=False)
        iu = np.triu_indices(len(BASKET), k=1)
        pair_corrs = cm[iu]
        if np.any(np.isnan(pair_corrs)):
            continue
        avg_corr[common[i]] = float(np.mean(pair_corrs))

    # delta_corr[t] = avg_corr[t] - avg_corr[t - DELTA_LAG] (positional on the common calendar)
    corr_days = [d for d in common if d in avg_corr]
    pos = {d: i for i, d in enumerate(corr_days)}
    delta_corr = {}
    for d in corr_days:
        i = pos[d]
        if i >= DELTA_LAG:
            delta_corr[d] = avg_corr[d] - avg_corr[corr_days[i - DELTA_LAG]]
    print(f"Days with avg_corr: {len(avg_corr)}; with delta_corr: {len(delta_corr)}")

    # NQ ATR14 (trailing mean RTH range through t-1) and NQ reference closes.
    nq_full, _ = load_price_data(context="market_behavior_discovery_scan_019.py (NQ ATR)", symbol="NQ")
    nq_disc = get_discovery_data(nq_full)
    daily = rth_daily(nq_disc)
    daily["atr14"] = daily["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    atr_by_date = {d.date(): v for d, v in daily["atr14"].items()}
    nq_ref = compute_daily_ref_closes(nq_day_groups)

    nq_days = sorted([d for d in nq_ref.keys() if nq_ref[d] is not None])
    nq_pos = {d: i for i, d in enumerate(nq_days)}

    rows = []
    for d in sorted(delta_corr.keys()):
        atr = atr_by_date.get(d)
        if atr is None or np.isnan(atr) or atr <= 0 or d not in nq_pos:
            continue
        i = nq_pos[d]
        base = nq_ref[d]
        row = {"date": d, "delta_corr": delta_corr[d], "avg_corr": avg_corr[d]}
        ok = True
        for h in HORIZONS:
            if i + h >= len(nq_days):
                ok = False
                break
            row[f"fwd_{h}d"] = (nq_ref[nq_days[i + h]] - base) / atr
        if not ok:
            continue
        # Confound input: trailing 5-day NQ return in ATR units, ending at t.
        if i >= DELTA_LAG:
            row["trail_5d"] = (base - nq_ref[nq_days[i - DELTA_LAG]]) / atr
        else:
            row["trail_5d"] = float("nan")
        rows.append(row)

    f = pd.DataFrame(rows)
    print(f"Usable observations (delta_corr + ATR + all horizons): {len(f)}")

    # Terciles frozen ONCE on the full Discovery slice.
    lo_edge, hi_edge = f["delta_corr"].quantile([1 / 3, 2 / 3]).tolist()
    print(f"Frozen tercile edges on delta_corr: LOW < {lo_edge:+.4f} <= MID < {hi_edge:+.4f} <= HIGH")

    def bucket(x):
        return "LOW" if x < lo_edge else ("MID" if x < hi_edge else "HIGH")

    f["tercile"] = f["delta_corr"].apply(bucket)

    cells = {}
    print("\nAll 9 cells (3 terciles x 3 horizons), NQ forward return in ATR units:")
    for terc in ("LOW", "MID", "HIGH"):
        sub = f[f["tercile"] == terc]
        for h in HORIZONS:
            s = summarize(sub[f"fwd_{h}d"].tolist())
            cells[f"{terc}_h{h}"] = s
            tag = " <== GATING" if (terc == "HIGH" and h == 3) else ""
            print(f"  {terc:<4} h={h}: n={s['n']:>4} mean={s['mean']:+.4f} "
                  f"ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}{tag}")

    gating = cells["HIGH_h3"]
    p1_pass = gating["direction"] == "negative"
    print(f"\nP1 (GATING, HIGH tercile h=3, claim = credibly NEGATIVE): {'P1_PASS' if p1_pass else 'P1_FAIL'}")

    # ---- BINDING CONFOUND DISCLOSURE (mechanism doc Section 5) ----
    print("\nCONFOUND CHECK 1 -- trailing 5-day NQ return by tercile (is HIGH just 'already fell'?):")
    trail_by_terc = {}
    for terc in ("LOW", "MID", "HIGH"):
        sub = f[f["tercile"] == terc]["trail_5d"].dropna()
        t = summarize(sub.tolist())
        trail_by_terc[terc] = t
        print(f"  {terc:<4}: n={t['n']:>4} mean trailing 5d = {t['mean']:+.4f} ATR ({t['direction']})")

    print("\nCONFOUND CHECK 2 -- gating cell (HIGH, h=3) split by sign of trailing 5-day NQ return:")
    high = f[f["tercile"] == "HIGH"].dropna(subset=["trail_5d"])
    split = {}
    for label, sub in (("trailing_NEGATIVE", high[high["trail_5d"] < 0]),
                       ("trailing_POSITIVE", high[high["trail_5d"] >= 0])):
        s = summarize(sub["fwd_3d"].tolist())
        split[label] = s
        print(f"  {label}: n={s['n']:>4} mean={s['mean']:+.4f} "
              f"ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")

    both_subsets_negative = (split["trailing_NEGATIVE"]["direction"] == "negative"
                             and split["trailing_POSITIVE"]["direction"] == "negative")
    if p1_pass:
        if both_subsets_negative:
            verdict = "P1_PASS_CONFOUND_CLEARED"
            note = ("Gating cell credible AND present in BOTH trailing-sign subsets -- supports the "
                    "delevering mechanism over the momentum explanation. Advance per pipeline order.")
        else:
            verdict = "P1_PASS_BUT_CONFOUNDED"
            note = ("Gating cell credible but NOT present in both trailing-sign subsets. Per the "
                    "pre-registered falsifier (b) this is the already-closed momentum/continuation "
                    "family restated, NOT a finding. CLOSES.")
    else:
        verdict = "P1_FAIL"
        note = "Gating cell not credibly negative. Entry closes on its own pre-registered falsifier (a)."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {
        "n_obs": int(len(f)),
        "tercile_edges": {"low_upper": float(lo_edge), "high_lower": float(hi_edge)},
        "cells": cells,
        "gating_cell": "HIGH_h3",
        "p1_pass": bool(p1_pass),
        "confound_trailing_5d_by_tercile": trail_by_terc,
        "confound_gating_split_by_trailing_sign": split,
        "verdict": verdict,
        "note": note,
    }
    (DATA_DIR / "market_behavior_discovery_scan_019_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_019_results.json'}")


if __name__ == "__main__":
    main()
