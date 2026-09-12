"""
market_behavior_discovery_scan_015.py
========================================

Scan 015. Draws Entry 12 (map anchor M5) from research/idea_inventory.md:
month-end NQ-vs-ZN relative performance -> last-2-session gating return,
first-2-session reported (reversal) window. Mechanism doc written BEFORE
this scan: research/mechanisms/nq-zn-month-end-relative-performance-m5.md.

Frozen scope (mechanism doc Section 6):
  - state variable: nq_minus_zn_mtd = NQ month-to-date RTH close-to-close
    return minus ZN month-to-date return, measured at the close of the
    3rd-to-last RTH session of the month (T-3); terciles cut on the
    Discovery sample (~45 month-ends).
  - gating outcome (P1, the single confirmatory cell): NQ return from the
    close of T-3 to the close of the last session of the month, / ATR14
    (trailing mean RTH range, shifted).
  - reported outcome (P2, descriptive support only, not a second
    independent test): NQ return from the close of the last session of
    the month to the close of the 2nd session of the FOLLOWING month, / ATR14.
  - TWO pre-registered cells (HIGH, LOW) on the gating outcome. Reported
    window is descriptive, read only if the gating cell passes.

Thin-sample: ~45 month-ends in Discovery x 2 cells (HIGH/LOW gating).
Minimum detectable effect at 90% CI, stated before running: roughly
>=0.35 ATR mean. A null here reads as "underpowered or absent," not a
clean refutation (per mechanism doc Section 6 and the Entry 12 generation
meeting Statistical note).

ONE pre-registered shot; no retuning, no widening the window post hoc.
scan_015_2026-09-12 (2 cells) registered in src/project_wide_multiplicity.py
BEFORE this ran.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_015.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_behavior_discovery_scan_012 import rth_daily

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_WINDOW = 14
TERCILE_LABELS = ["low", "mid", "high"]


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float); v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = rng.choice(v, size=(n_bootstrap, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def summarize(vals) -> dict:
    vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
    n = len(vals)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": [float("nan"), float("nan")], "credible_vs_zero": False, "direction": "insufficient_n"}
    m = float(np.mean(vals)); ci = bootstrap_mean_ci(vals)
    credible = ci[0] > 0 or ci[1] < 0
    direction = "positive" if (credible and ci[0] > 0) else ("negative" if (credible and ci[1] < 0) else "null")
    return {"n": n, "mean": m, "ci_90": list(ci), "credible_vs_zero": bool(credible), "direction": direction}


def month_end_events(d: pd.DataFrame) -> pd.DataFrame:
    """One row per calendar month with >=3 trailing sessions in `d` and
    >=2 leading sessions in the following month present in `d`. Uses
    positional session indices only (no lookahead beyond what a month-end
    observer, sitting at T-3's close, could already see for the state;
    the gating/reported outcomes are, by construction, realized after
    the state date)."""
    d = d.sort_index()
    months = d.index.to_period("M")
    rows = []
    unique_months = months.unique()
    for i, m in enumerate(unique_months):
        idx = np.where(months == m)[0]
        if len(idx) < 3:
            continue
        t3_pos, tlast_pos = idx[-3], idx[-1]
        # following month's first 2 sessions
        if i + 1 >= len(unique_months):
            continue
        next_idx = np.where(months == unique_months[i + 1])[0]
        if len(next_idx) < 2:
            continue
        n1_pos, n2_pos = next_idx[0], next_idx[1]
        rows.append({
            "month": str(m), "t3_pos": t3_pos, "tlast_pos": tlast_pos,
            "n1_pos": n1_pos, "n2_pos": n2_pos,
        })
    return pd.DataFrame(rows)


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 015 (Entry 12 / M5: month-end NQ-vs-ZN relative performance)"); print("=" * 78)
    nq, syn1 = load_price_data(context="market_behavior_discovery_scan_015.py", symbol="NQ")
    zn, syn2 = load_price_data(context="market_behavior_discovery_scan_015.py", symbol="ZN")
    if syn1 or syn2:
        print("ABORT: synthetic data."); return
    nq = get_discovery_data(nq); zn = get_discovery_data(zn)
    dn = rth_daily(nq); dz = rth_daily(zn)
    d = dn.join(dz[["rth_close"]].rename(columns={"rth_close": "zn_close"}), how="inner").sort_index()
    d["atr14"] = d["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    ev = month_end_events(d)
    print(f"Candidate month-ends (>=3 trailing + >=2 leading sessions, NQ+ZN aligned): {len(ev)}")

    closes_nq = d["rth_close"].to_numpy(); closes_zn = d["zn_close"].to_numpy(); atr = d["atr14"].to_numpy()
    rows = []
    for _, r in ev.iterrows():
        t3, tlast, n1, n2 = int(r.t3_pos), int(r.tlast_pos), int(r.n1_pos), int(r.n2_pos)
        month_start_pos = np.where(d.index.to_period("M") == pd.Period(r.month))[0][0]
        nq_mtd = closes_nq[t3] / closes_nq[month_start_pos] - 1.0
        zn_mtd = closes_zn[t3] / closes_zn[month_start_pos] - 1.0
        state = nq_mtd - zn_mtd
        atr_gate = atr[tlast]
        atr_rep = atr[n2]
        gating_ret = (closes_nq[tlast] - closes_nq[t3]) / atr_gate if atr_gate and not np.isnan(atr_gate) else float("nan")
        reported_ret = (closes_nq[n2] - closes_nq[tlast]) / atr_rep if atr_rep and not np.isnan(atr_rep) else float("nan")
        rows.append({"month": r.month, "nq_minus_zn_mtd": state, "gating_ret": gating_ret, "reported_ret": reported_ret})
    f = pd.DataFrame(rows).dropna(subset=["nq_minus_zn_mtd", "gating_ret"])
    print(f"Usable month-ends after ATR/state availability: {len(f)}")

    edges = np.nanpercentile(f["nq_minus_zn_mtd"], [100 / 3, 200 / 3])
    f["bucket"] = pd.cut(f["nq_minus_zn_mtd"], bins=[-np.inf, edges[0], edges[1], np.inf], labels=TERCILE_LABELS)
    print(f"nq_minus_zn_mtd tercile edges: {edges[0]:+.4f}, {edges[1]:+.4f}")

    cells = {}
    for b in TERCILE_LABELS:
        s = summarize(f.loc[f["bucket"] == b, "gating_ret"].tolist()); cells[b] = s
        print(f"  gating {b:>4}: n={s['n']} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
    hi = cells["high"]; lo = cells["low"]
    p1_pass = bool(hi["direction"] == "negative" or (hi["mean"] < lo["mean"] and (hi["credible_vs_zero"] or lo["credible_vs_zero"])))
    verdict = "P1_PASS" if p1_pass else "P1_FAIL"
    print(f"\nGATING (P1, HIGH tercile gating return credibly more negative than LOW): {verdict}")

    reported = {}
    if verdict == "P1_PASS":
        for b in TERCILE_LABELS:
            s = summarize(f.loc[f["bucket"] == b, "reported_ret"].dropna().tolist()); reported[b] = s
            print(f"  reported {b:>4}: n={s['n']} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}")
    else:
        print("  P1 failed at the gating cell -- reported/reversal window not mined per the pre-registered scope (descriptive support only, not a second independent test).")

    out = {"state_var": "nq_minus_zn_mtd", "tercile_edges": [float(edges[0]), float(edges[1])], "n_month_ends": int(len(f)),
           "gating_cells": cells, "gating_verdict": verdict, "reported_cells": reported}
    (DATA_DIR / "market_behavior_discovery_scan_015_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_015_results.json'}")


if __name__ == "__main__":
    main()
