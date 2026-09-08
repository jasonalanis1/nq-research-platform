"""
study_ib_breakout_volatility_conditioned.py
=================================================

exp-093 -- frozen spec: research/studies/ib-breakout-volatility-conditioned-spec.md.
Tests whether the IB Breakout continuation setup's economics differ on
days the volatility_conditioning module classifies "wide" (an
above-average range expected), a mechanistically motivated pairing --
unlike the earlier overlay screens (exp-077/086/087), which conditioned
a MEAN-REVERSION setup on a volatility fact and found nothing.

REUSED, UNMODIFIED: detect_ib_breakout.scan_all_days,
backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS,
volatility_conditioning.build_conditioning_frame.

HOW TO RUN:
    python3 src/study_ib_breakout_volatility_conditioned.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_ib_breakout import detect_ib_breakout_for_day
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from volatility_conditioning import build_conditioning_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_BUCKET_TRADES = 30


def bootstrap_diff_ci(a, b, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    a_arr, b_arr = np.array(a), np.array(b)
    diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        diffs[i] = rng.choice(a_arr, size=len(a_arr), replace=True).mean() - rng.choice(b_arr, size=len(b_arr), replace=True).mean()
    return float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))


def main():
    print("=" * 78)
    print("EXP-093: IB BREAKOUT, CONDITIONED ON THE VOLATILITY CONDITIONING")
    print("MODULE'S 'WIDE PRIOR DAY' FLAG")
    print("=" * 78)
    print("\nFrozen spec: research/studies/ib-breakout-volatility-conditioned-spec.md\n")

    df, is_synthetic = load_price_data(context="study_ib_breakout_volatility_conditioned.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)

    # NOTE: detect_ib_breakout.scan_all_days() re-filters the FULL frame
    # by date for every single day (O(n_days * n_rows)) -- fine for an
    # interactive one-off run, far too slow chained after this script's
    # own per-day work on a multi-year dataset. Group once instead and
    # call detect_ib_breakout_for_day() directly per pre-grouped day --
    # identical detection logic, unmodified, just not re-scanning the
    # whole frame per day.
    day_groups = {d: g for d, g in discovery.groupby(discovery.index.date)}
    signals = []
    for day, day_df in day_groups.items():
        sig = detect_ib_breakout_for_day(day_df, day)
        if sig is not None:
            signals.append(sig)
    print(f"IB Breakout signals on Discovery: {len(signals)} (of {len(day_groups)} days scanned)")

    conditioning = build_conditioning_frame(discovery)

    results = []
    for sig in signals:
        day = sig["date"]
        day_df = day_groups.get(day)
        if day_df is None:
            continue
        sig_series = pd.Series(sig)
        outcome = simulate_trade(day_df, sig_series, "breakout_time")

        risk_points = abs(sig["entry"] - sig["stop"])
        if sig["direction"] == "long":
            pnl_gross = outcome["exit_price"] - sig["entry"]
        else:
            pnl_gross = sig["entry"] - outcome["exit_price"]
        is_resolved = not outcome["exit_reason"].startswith("unresolved")
        pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
        r_multiple_net = pnl_net / risk_points if risk_points else float("nan")

        wide = bool(conditioning.loc[day, "prior_day_wide"]) if day in conditioning.index else False

        results.append({"date": day, "r_multiple_net": r_multiple_net, "wide_prior_day": wide})

    res_df = pd.DataFrame(results).dropna(subset=["r_multiple_net"])
    wide_group = res_df.loc[res_df["wide_prior_day"], "r_multiple_net"].tolist()
    rest_group = res_df.loc[~res_df["wide_prior_day"], "r_multiple_net"].tolist()

    print(f"\nWide-prior-day trades: n={len(wide_group)}, mean r_multiple_net={np.mean(wide_group):.4f}" if wide_group else "\nWide-prior-day trades: n=0")
    print(f"Rest of trades:        n={len(rest_group)}, mean r_multiple_net={np.mean(rest_group):.4f}" if rest_group else "Rest of trades: n=0")

    out = {"n_wide": len(wide_group), "n_rest": len(rest_group)}
    if len(wide_group) >= MIN_BUCKET_TRADES and len(rest_group) >= MIN_BUCKET_TRADES:
        diff = float(np.mean(wide_group) - np.mean(rest_group))
        ci = bootstrap_diff_ci(wide_group, rest_group)
        credible = ci[0] > 0 or ci[1] < 0
        print(f"\nDiff (wide - rest): {diff:.4f}, ci_90={ci}, credible={credible}")
        out.update({"diff": diff, "ci_90": ci, "credible": credible,
                     "mean_wide": float(np.mean(wide_group)), "mean_rest": float(np.mean(rest_group))})
    else:
        print(f"\nToo few trades in one bucket (min {MIN_BUCKET_TRADES}) -- skipped.")
        out["note"] = "too few trades in one bucket, skipped"

    out_path = DATA_DIR / "study_ib_breakout_volatility_conditioned_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
