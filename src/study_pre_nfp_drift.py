"""
study_pre_nfp_drift.py
========================

Pre-NFP (jobs report) announcement drift -- frozen spec:
research/studies/pre-nfp-drift-design-spec.md.

Continuation of the pre-FOMC drift thread (same macro-announcement-
premium family, Savor & Wilson 2013). Free calendar data (first
Friday of each month). Directional pre-commitment (positive
overnight-into-NFP drift) stated BEFORE this scan ran.

Non-trading, exploratory. Discovery data only.

HOW TO RUN:
    python3 src/study_pre_nfp_drift.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_bar_behavior_batch1 import build_daily_bars
from research_ledger import log_hypothesis

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_WINDOW = 14
ATR_NORMALIZED_FLOOR = 0.05
MIN_N_FOR_PROMISING = 40


def first_friday(year, month):
    d = pd.Timestamp(year=year, month=month, day=1)
    offset = (4 - d.weekday()) % 7  # Monday=0 ... Friday=4
    return (d + pd.Timedelta(days=offset)).date()


def bootstrap_diff_ci(cond, base, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    c, b = np.asarray(cond, dtype=float), np.asarray(base, dtype=float)
    if len(c) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        cs = rng.choice(c, size=len(c), replace=True)
        bs = rng.choice(b, size=len(b), replace=True)
        diffs[i] = cs.mean() - bs.mean()
    return float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))


def main():
    print("=" * 78)
    print("PRE-NFP ANNOUNCEMENT DRIFT -- frozen scan (exploratory)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/pre-nfp-drift-design-spec.md\n")

    df, is_synthetic = load_price_data(context="study_pre_nfp_drift.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index

    daily_bars = build_daily_bars(discovery).copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()
    avg_atr = float(daily_bars["atr14"].dropna().mean())

    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days available: {len(days_sorted)}")

    years = sorted(set(d.year for d in days_sorted))
    months = range(1, 13)
    nfp_dates_all = set()
    for y in years:
        for m in months:
            nfp_dates_all.add(first_friday(y, m))
    nfp_dates_in_discovery = sorted(d for d in nfp_dates_all if d in day_groups)
    print(f"NFP dates (first-Friday rule) in Discovery: {len(nfp_dates_in_discovery)}")

    overnight_return = {}
    for i, day in enumerate(days_sorted):
        if i == 0:
            continue
        rth = day_groups[day].between_time("09:30", "16:00")
        if rth.empty or len(rth) < 20:
            continue
        prior_day = days_sorted[i - 1]
        if prior_day not in daily_bars.index:
            continue
        prior_close = float(daily_bars.loc[prior_day, "Close"])
        overnight_return[day] = float(rth["Close"].iloc[0] - prior_close)

    nfp_overnight, complement_overnight = [], []
    for day, ret in overnight_return.items():
        if day in nfp_dates_all:
            nfp_overnight.append(ret)
        else:
            complement_overnight.append(ret)

    n_nfp, n_comp = len(nfp_overnight), len(complement_overnight)
    print(f"\nNFP-day overnight observations: {n_nfp}   complement: {n_comp}")

    c_arr, b_arr = np.array(nfp_overnight), np.array(complement_overnight)
    effect = float(c_arr.mean() - b_arr.mean())
    ci = bootstrap_diff_ci(c_arr, b_arr)
    atr_norm = abs(effect) / avg_atr if avg_atr > 0 else float("nan")
    cost_priority = "LOW_PRIORITY_COST_DOMINATED" if atr_norm < ATR_NORMALIZED_FLOOR else "NORMAL"
    credible = ci[0] > 0 or ci[1] < 0
    direction_matches = effect > 0

    if n_nfp >= MIN_N_FOR_PROMISING and credible and direction_matches and cost_priority == "NORMAL":
        label = "Promising"
    elif n_nfp < MIN_N_FOR_PROMISING and credible and direction_matches:
        label = "Interesting (n below promising threshold)"
    elif credible and direction_matches:
        label = "Interesting" if cost_priority == "NORMAL" else "Interesting (cost-dominated)"
    elif credible and not direction_matches:
        label = "Credible but WRONG DIRECTION vs literature"
    else:
        label = "No meaningful difference"

    print(f"\nNFP-day mean overnight return:  {c_arr.mean():.3f} pts")
    print(f"Complement mean overnight return: {b_arr.mean():.3f} pts")
    print(f"Effect size: {effect:.3f} pts   ci_90={ci}")
    print(f"Credible: {credible}   Direction matches literature: {direction_matches}")
    print(f"ATR-normalized effect: {atr_norm:.4f} -> {cost_priority}")
    print(f"\nLabel: {label}")

    out = {
        "spec": "research/studies/pre-nfp-drift-design-spec.md",
        "status": "EXPLORATORY -- not a finding, not a strategy",
        "n_nfp": n_nfp, "n_complement": n_comp,
        "nfp_mean_overnight": float(c_arr.mean()), "complement_mean_overnight": float(b_arr.mean()),
        "effect_size": effect, "ci_90_diff": ci, "credible": credible,
        "direction_matches_literature": direction_matches,
        "avg_atr14": avg_atr, "atr_normalized_effect": atr_norm,
        "cost_priority": cost_priority, "label": label,
    }
    out_path = DATA_DIR / "study_pre_nfp_drift_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved results to {out_path}.")

    record = log_hypothesis(
        strategy_name="pre_nfp_drift",
        strategy_origin="data_discovered",
        parameters={
            "n_nfp": n_nfp, "n_complement": n_comp, "nfp_mean": float(c_arr.mean()),
            "complement_mean": float(b_arr.mean()), "effect_size": effect, "ci_90": list(ci),
            "atr_normalized_effect": atr_norm,
        },
        data_slice_used="discovery",
        trade_count=n_nfp,
        strategy_status="PROMISING" if label == "Promising" else "REJECTED",
        notes=(
            f"Observatory v12 / pre-nfp-drift-design-spec.md. Continuation of the "
            f"pre-FOMC drift thread (macro-announcement-premium family, Savor & "
            f"Wilson 2013). Free calendar data (first-Friday NFP rule). CPI "
            f"deliberately not tested (literature shows no significant effect). "
            f"Result: {label}. effect={effect:.3f}pts ci_90={ci}. "
            f"Full: data/study_pre_nfp_drift_results.json."
        ),
    )
    print(f"\nLogged to ledger: {record.hypothesis_id} -- status {record.strategy_status}")


if __name__ == "__main__":
    main()
