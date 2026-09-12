"""
market_behavior_discovery_scan_009.py
========================================

Scan 009 of the Market Behavior Discovery Engine. Draws Entry 4 from
research/idea_inventory.md (day_of_week, Friday RTH range vs trailing-20d
average) -- FIRST attempt on day_of_week as a standalone, individually
scanned state variable (its two prior ledger appearances, hyp-000016 and
hyp-000042, tested it only as one of many zeroed-out coefficients in a
joint next-day-return-sign model and never isolated a day_of_week effect
on its own native outcome).

Frozen scope, from idea_inventory.md Entry 4 (do not re-derive, no
retuning):
  - state variable: day_of_week (market_state_primitives.py, categorical
    Mon=0..Fri=4), restricted to Friday for this first cut
  - outcome: same-day RTH range vs trailing-20d average RTH range
    (existing convention, reused from the overnight-coil / opex-
    compression framing, same as Scan 007)
  - ONE pre-registered cell: day_of_week == Friday. No sweep across all
    five weekdays. Monday is explicitly flagged in the entry as a
    candidate SECOND cell only if Friday is credible and worth the added
    multiplicity -- not run here, not pooled in blind.

Predictions (written before any number is looked at, per Entry 4):
  P1 (risk-trimming / weekend-gap-avoidance): Friday RTH-range ratio < 1
     (compression), credible vs 1.0 (90% CI upper bound < 1.0).
  P2 (falsifying alternative -- thin-liquidity amplification): Friday
     RTH-range ratio > 1 (elevation), credible vs 1.0 (90% CI lower
     bound > 1.0).
  P1 and P2 are opposite-signed predictions for the identical cell, so
  the single test is informative regardless of which way it resolves; a
  clean null (not credibly different from 1.0) itself teaches that
  neither weekly-calendar mechanism moves raw same-day RTH range on this
  instrument.
  P3 (non-restating, reported not gated): if either mechanism is real
     and volume-driven, the effect should be WEAKER on Fridays that
     scored `high` (>= median) on volume_vs_expected (market_state_
     primitives_v2.py) than on `low` Fridays -- i.e. normal-or-above-
     participation Fridays should look more like an ordinary day. This
     is reported alongside the primary cell, never used to retune or
     re-cut P1/P2.

This is the entry's ONE pre-registered Discovery-stage shot. No new
cells, no peeking then adjusting, no retuning. Per SCAN_REGISTRY's
standing maintenance note, the scan_009_2026-09-11 entry is added to
src/project_wide_multiplicity.py before any CI here is quoted as final.

HOW TO RUN:
    PYTHONPATH=src python3 src/market_behavior_discovery_scan_009.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_behavior_discovery_scan_007 import build_rth_range_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
FRIDAY = 4


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        s = rng.choice(v, size=len(v), replace=True)
        means[i] = s.mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def summarize(ratios: list) -> dict:
    """No fixed 'direction' argument here (unlike Scan 007) -- P1 and P2
    are opposite-signed predictions for the SAME cell, so we report the
    raw credible-vs-1.0 result and let the writeup state which
    prediction it confirms, rather than pre-committing the summarizer to
    one direction."""
    n = len(ratios)
    if n < 2:
        return {"n": n, "mean_ratio": float("nan"), "ci_90": [float("nan"), float("nan")],
                "credible_vs_one": False, "direction": "insufficient_n"}
    mean_r = float(np.mean(ratios))
    ci = bootstrap_mean_ci(ratios)
    credible = ci[0] > 1.0 or ci[1] < 1.0
    direction = "compressed_(P1)" if (credible and ci[1] < 1.0) else (
        "elevated_(P2)" if (credible and ci[0] > 1.0) else "null"
    )
    return {"n": n, "mean_ratio": mean_r, "ci_90": list(ci),
            "credible_vs_one": bool(credible), "direction": direction}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 009 (day_of_week==Friday, RTH-range vs trailing-20d avg)")
    print("=" * 78)
    print("\nInput: research/idea_inventory.md Entry 4\n")

    df, is_synthetic = load_price_data(context="market_behavior_discovery_scan_009.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)

    # RTH range + trailing-20d average (Scan 007's convention, reused as-is)
    rth = build_rth_range_frame(discovery)
    rth = rth.dropna(subset=["trailing_avg_rth_range"]).copy()
    rth["ratio"] = rth["rth_range"] / rth["trailing_avg_rth_range"]

    # day_of_week (v1) + volume_vs_expected (v2), for the Friday split
    # and the P3 volume-conditioning check
    states = extend_state_frame(build_state_frame(discovery), discovery)
    states = states[["day_of_week", "volume_vs_expected"]]

    labeled = rth.join(states, how="inner")
    print(f"Discovery RTH-days available (with trailing avg + state): {len(labeled)}")

    friday = labeled[labeled["day_of_week"] == FRIDAY]
    ratios = friday["ratio"].dropna().tolist()
    primary = summarize(ratios)
    print(f"\n  friday: n={primary['n']} mean_ratio={primary['mean_ratio']:.4f} "
          f"ci_90=({primary['ci_90'][0]:.4f},{primary['ci_90'][1]:.4f}) "
          f"credible_vs_1={primary['credible_vs_one']} direction={primary['direction']}")

    # P3: non-restating, reported not gated -- split Friday's own cell by
    # its own volume_vs_expected median (low vs high participation)
    fri_valid_vol = friday.dropna(subset=["volume_vs_expected"])
    p3 = {"n_total": int(len(fri_valid_vol))}
    if len(fri_valid_vol) >= 10:
        med = fri_valid_vol["volume_vs_expected"].median()
        low_vol = fri_valid_vol[fri_valid_vol["volume_vs_expected"] < med]
        high_vol = fri_valid_vol[fri_valid_vol["volume_vs_expected"] >= med]
        low_summ = summarize(low_vol["ratio"].dropna().tolist())
        high_summ = summarize(high_vol["ratio"].dropna().tolist())
        p3["low_volume_vs_expected"] = low_summ
        p3["high_volume_vs_expected"] = high_summ
        print(f"\n  P3 (reported, not gated): low_vol n={low_summ['n']} mean={low_summ['mean_ratio']:.4f} "
              f"direction={low_summ['direction']}  |  high_vol n={high_summ['n']} mean={high_summ['mean_ratio']:.4f} "
              f"direction={high_summ['direction']}")
    else:
        print("\n  P3: insufficient Friday rows with volume_vs_expected for a median split (n < 10) -- not computed.")

    out_path = DATA_DIR / "market_behavior_discovery_scan_009_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "state_var": "day_of_week",
            "cell": "friday",
            "outcome": "rth_range_vs_trailing_20d_avg_ratio",
            "primary": primary,
            "p3_volume_conditioning_check": p3,
        }, f, indent=2)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
