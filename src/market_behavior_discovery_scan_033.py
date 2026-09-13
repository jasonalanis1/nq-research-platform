"""
Scan 033 -- Entry 30 / M26: Level Sweep Reversal (close_min_distance)
conditioned on prior_day_narrow. First sanctioned CONDITIONAL RETEST under the
eight-condition protocol adopted 2026-09-13 (UPGRADE QUEUE v3, U3).

Frozen scope: research/mechanisms/level-sweep-reversal-range-contraction-m26.md
Section 9. Four cells, registered before this file was written:
  1. compressed-day (prior_day_narrow=True) per-trade net R, block CI   <== GATING P1
  2. non-compressed-day per-trade net R, block CI                        (reference)
  3. compressed minus non-compressed, block CI                          <== P2 (the real test)
  4. trade counts per cell                                               (falsifier c, thin-sample)

Construction, all reused unmodified:
  - signals: src/detect_level_sweep.py scan_all_days(df, "close_min_distance")
    (5.0-point confirm distance, existing entry/stop/target)
  - trade outcome: src/backtest.py simulate_trade + ROUND_TRIP_COST_POINTS
    (net R, costs only on resolved trades -- identical to exp-023)
  - condition: src/volatility_conditioning.py build_conditioning_frame(...)
    ["prior_day_narrow"] -- the frozen bottom-tercile trailing prior-day-range
    definition (hyp-000048), computed once, never refit
  - slice: src/data_split.get_discovery_data (2015-01-01 .. 2021-10-03)
  - stats: src/baseline_relative._block_means, block=5 (thin per-trade series,
    same convention as M19/M22/M24/M25), N_BOOT=3000, SEED=20260913, 90% CI,
    "credible" = CI entirely on one side of zero.
One shot. No new cells, no retuning after seeing results.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
from detect_level_sweep import scan_all_days  # noqa: E402
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS  # noqa: E402
from volatility_conditioning import build_conditioning_frame  # noqa: E402
from baseline_relative import _block_means  # noqa: E402

SCAN_ID = "scan_033_2026-09-13"
MAP_ANCHOR = "M26"
ENTRY = 30
BLOCK = 5
N_BOOT = 3000
SEED = 20260913
ALPHA = 0.10
THIN_SAMPLE_N = 40
OUT = ROOT.parent / "data" / "market_behavior_discovery_scan_033_results.json"


def block_ci(x: np.ndarray, rng) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return float("nan"), float("nan")
    m = _block_means(x, BLOCK, N_BOOT, rng)
    return float(np.percentile(m, 100 * ALPHA / 2)), float(np.percentile(m, 100 * (1 - ALPHA / 2)))


def cell(x: np.ndarray, rng) -> dict:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    lo, hi = block_ci(x, rng)
    return {"n": int(len(x)), "mean": float(np.mean(x)) if len(x) else float("nan"),
            "ci_90": [lo, hi], "credible_positive": bool(len(x) >= 2 and lo > 0),
            "credible_negative": bool(len(x) >= 2 and hi < 0)}


def diff_cell(a: np.ndarray, b: np.ndarray, rng) -> dict:
    a = np.asarray(a, dtype=float); a = a[np.isfinite(a)]
    b = np.asarray(b, dtype=float); b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return {"mean_diff": float("nan"), "ci_90": [float("nan"), float("nan")],
                "credible_positive": False}
    d = _block_means(a, BLOCK, N_BOOT, rng) - _block_means(b, BLOCK, N_BOOT, rng)
    lo, hi = float(np.percentile(d, 100 * ALPHA / 2)), float(np.percentile(d, 100 * (1 - ALPHA / 2)))
    return {"mean_diff": float(a.mean() - b.mean()), "ci_90": [lo, hi],
            "credible_positive": bool(lo > 0)}


def main() -> None:
    df, is_synthetic = load_price_data(context="scan_033_m26")
    if is_synthetic:
        raise SystemExit("synthetic data -- refusing to run a scan of record")
    disc = get_discovery_data(df)

    # --- signals, exactly as exp-023, but scanned one calendar year at a time
    # (scan_all_days re-materializes df.index.date per day, which is O(rows)
    # per day; year chunks with a 4-day overlap give identical signals in a
    # fraction of the time -- the device shell has a hard 3-minute limit) ---
    signals, total_days = [], 0
    for year in range(disc.index[0].year, disc.index[-1].year + 1):
        lo = pd.Timestamp(f"{year - 1}-12-28", tz="America/New_York")
        hi = pd.Timestamp(f"{year}-12-31 23:59", tz="America/New_York")
        sub = disc[(disc.index >= lo) & (disc.index <= hi)]
        if sub.empty:
            continue
        sigs, _ = scan_all_days(sub, "close_min_distance")
        signals += [s for s in sigs if pd.Timestamp(s["date"]).year == year]
        total_days += len({d for d in sub.index.date if d.year == year})
    stats = {"total_days": total_days}

    # --- trade outcomes, exactly as exp-023 (simulate_trade + net costs) ---
    day_groups = {k.date(): g for k, g in disc.groupby(disc.index.normalize())}
    rows = []
    for s in signals:
        day = pd.Timestamp(s["date"]).date()
        day_df = day_groups[day]
        sig = pd.Series(s)
        out = simulate_trade(day_df, sig, "signal_time")
        risk = abs(s["entry"] - s["stop"])
        gross = (out["exit_price"] - s["entry"]) if s["direction"] == "long" else (s["entry"] - out["exit_price"])
        resolved = not out["exit_reason"].startswith("unresolved")
        net = gross - ROUND_TRIP_COST_POINTS if resolved else gross
        rows.append({"date": day, "direction": s["direction"], "r_net": net / risk if risk else np.nan,
                     "resolved": resolved, "exit_reason": out["exit_reason"]})
    trades = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    # --- frozen condition ---
    cond = build_conditioning_frame(disc)
    cond_idx = {pd.Timestamp(i).date(): bool(v) for i, v in cond["prior_day_narrow"].items()}
    trades["prior_day_narrow"] = trades["date"].map(lambda d: cond_idx.get(d, False))

    rng = np.random.default_rng(SEED)
    comp = trades.loc[trades["prior_day_narrow"], "r_net"].to_numpy()
    non = trades.loc[~trades["prior_day_narrow"], "r_net"].to_numpy()
    c1 = cell(comp, rng)
    c2 = cell(non, rng)
    c3 = diff_cell(comp, non, rng)
    c4 = {"n_total": int(len(trades)), "n_compressed": int(len(comp)), "n_non_compressed": int(len(non)),
          "thin_sample_threshold": THIN_SAMPLE_N, "compressed_underpowered": bool(len(comp) < THIN_SAMPLE_N),
          "resolved_share_compressed": float(trades.loc[trades["prior_day_narrow"], "resolved"].mean()) if len(comp) else float("nan"),
          "n_days_scanned": int(stats.get("total_days", 0))}

    p1 = c1["credible_positive"]
    p2 = c3["credible_positive"]
    if c4["compressed_underpowered"] and not p1:
        verdict = "UNDERPOWERED"   # falsifier (c): disclose, do not claim a null
    elif p1 and p2:
        verdict = "P1_PASS_P2_PASS"
    elif p1:
        verdict = "P1_PASS_P2_FAIL"
    else:
        verdict = "P1_FAIL"

    result = {
        "scan_id": SCAN_ID, "map_anchor": MAP_ANCHOR, "entry": ENTRY, "instrument": "NQ",
        "slice": "discovery", "cells_scanned": 4, "block": BLOCK, "n_boot": N_BOOT, "seed": SEED,
        "cell_1_compressed_R_gating": c1, "cell_2_non_compressed_R_reference": c2,
        "cell_3_compressed_minus_non_compressed_P2": c3, "cell_4_counts": c4,
        "verdict": verdict,
        "exp023_reference": {"n": 461, "mean_r_net": -0.038, "note": "unconditional close_min_distance on the same slice"},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
