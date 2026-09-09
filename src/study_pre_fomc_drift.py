"""
study_pre_fomc_drift.py
=========================

Pre-FOMC announcement drift -- frozen spec:
research/studies/pre-fomc-drift-design-spec.md.

Direct outcome of the 2026-09-09 "identify direction" staff meeting.
Sourced from Lucca & Moench (2015). Free calendar data (FOMC decision
dates). Directional pre-commitment (positive pre-FOMC drift) stated
BEFORE this scan ran.

FOMC date list compiled from public historical records, spot-checked
but not independently re-verified line-by-line this session -- see
frozen spec caveat.

Non-trading, exploratory. Discovery data only.

HOW TO RUN:
    python3 src/study_pre_fomc_drift.py
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

# Scheduled FOMC statement-release dates, 2015 through Discovery cutoff
# (2021-10-03). Compiled from public historical records; see frozen
# spec caveat on verification.
FOMC_DATES = [
    "2015-01-28", "2015-03-18", "2015-04-29", "2015-06-17", "2015-07-29",
    "2015-09-17", "2015-10-28", "2015-12-16",
    "2016-01-27", "2016-03-16", "2016-04-27", "2016-06-15", "2016-07-27",
    "2016-09-21", "2016-11-02", "2016-12-14",
    "2017-02-01", "2017-03-15", "2017-05-03", "2017-06-14", "2017-07-26",
    "2017-09-20", "2017-11-01", "2017-12-13",
    "2018-01-31", "2018-03-21", "2018-05-02", "2018-06-13", "2018-08-01",
    "2018-09-26", "2018-11-08", "2018-12-19",
    "2019-01-30", "2019-03-20", "2019-05-01", "2019-06-19", "2019-07-31",
    "2019-09-18", "2019-10-30", "2019-12-11",
    "2020-01-29", "2020-03-03", "2020-03-15", "2020-04-29", "2020-06-10",
    "2020-07-29", "2020-09-16", "2020-11-05", "2020-12-16",
    "2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28",
    "2021-09-22",
]


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
    print("PRE-FOMC ANNOUNCEMENT DRIFT -- frozen scan (exploratory)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/pre-fomc-drift-design-spec.md\n")

    df, is_synthetic = load_price_data(context="study_pre_fomc_drift.py")
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

    fomc_dates_all = set(pd.Timestamp(d).date() for d in FOMC_DATES)
    fomc_dates_in_discovery = sorted(d for d in fomc_dates_all if d in day_groups)
    print(f"FOMC dates in date list: {len(fomc_dates_all)}   present in Discovery: {len(fomc_dates_in_discovery)}")

    # per-day RTH return and overnight return (prior close -> today's open)
    rth_return = {}
    overnight_return = {}
    for i, day in enumerate(days_sorted):
        rth = day_groups[day].between_time("09:30", "16:00")
        if rth.empty or len(rth) < 20:
            continue
        rth_return[day] = float(rth["Close"].iloc[-1] - rth["Close"].iloc[0])
        if i > 0:
            prior_day = days_sorted[i - 1]
            if prior_day in daily_bars.index:
                prior_close = float(daily_bars.loc[prior_day, "Close"])
                overnight_return[day] = float(rth["Close"].iloc[0] - prior_close)

    # sub-window (a): prior trading day's RTH return, ahead of an FOMC day
    prior_day_rth_pre_fomc, prior_day_rth_complement = [], []
    # sub-window (b): overnight return into FOMC morning
    overnight_pre_fomc, overnight_complement = [], []

    for i, day in enumerate(days_sorted):
        if day in overnight_return:
            if day in fomc_dates_all:
                overnight_pre_fomc.append(overnight_return[day])
            else:
                overnight_complement.append(overnight_return[day])

    for i, day in enumerate(days_sorted):
        if i == 0:
            continue
        prior_day = days_sorted[i - 1]
        if prior_day not in rth_return:
            continue
        if day in fomc_dates_all:
            prior_day_rth_pre_fomc.append(rth_return[prior_day])
        # complement: prior day's RTH return when TODAY is not an FOMC day
        # (avoids double-counting; each prior-day return classified once,
        # by whether the day it precedes is an FOMC day)
        else:
            prior_day_rth_complement.append(rth_return[prior_day])

    results = {}
    for label, cond, comp in [
        ("prior_day_rth_pre_fomc", prior_day_rth_pre_fomc, prior_day_rth_complement),
        ("overnight_pre_fomc", overnight_pre_fomc, overnight_complement),
    ]:
        n_cond, n_comp = len(cond), len(comp)
        if n_cond < 5 or n_comp < 20:
            results[label] = {"n": n_cond, "label": "insufficient n"}
            continue
        c_arr, b_arr = np.array(cond), np.array(comp)
        effect = float(c_arr.mean() - b_arr.mean())
        ci = bootstrap_diff_ci(c_arr, b_arr)
        atr_norm = abs(effect) / avg_atr if avg_atr > 0 else float("nan")
        cost_priority = "LOW_PRIORITY_COST_DOMINATED" if atr_norm < ATR_NORMALIZED_FLOOR else "NORMAL"
        credible = ci[0] > 0 or ci[1] < 0
        direction_matches = effect > 0  # pre-specified: positive pre-FOMC drift

        if n_cond >= MIN_N_FOR_PROMISING and credible and direction_matches and cost_priority == "NORMAL":
            lbl = "Promising"
        elif n_cond < MIN_N_FOR_PROMISING and credible and direction_matches:
            lbl = "Interesting (n below promising threshold)"
        elif credible and direction_matches:
            lbl = "Interesting" if cost_priority == "NORMAL" else "Interesting (cost-dominated)"
        elif credible and not direction_matches:
            lbl = "Credible but WRONG DIRECTION vs literature"
        else:
            lbl = "No meaningful difference"

        print(f"\n{label}: n={n_cond} (complement n={n_comp}) cond_mean={c_arr.mean():.3f} "
              f"comp_mean={b_arr.mean():.3f} effect={effect:.3f} ci_90={ci} "
              f"atr_norm={atr_norm:.4f} -> {cost_priority} -> {lbl}")

        results[label] = {
            "n": n_cond, "n_complement": n_comp, "cond_mean": float(c_arr.mean()),
            "complement_mean": float(b_arr.mean()), "effect_size": effect, "ci_90_diff": ci,
            "atr_normalized_effect": atr_norm, "cost_priority": cost_priority,
            "direction_matches_literature": bool(direction_matches), "label": lbl,
        }

    out = {
        "spec": "research/studies/pre-fomc-drift-design-spec.md",
        "status": "EXPLORATORY -- not a finding, not a strategy",
        "n_fomc_dates_in_discovery": len(fomc_dates_in_discovery),
        "avg_atr14": avg_atr,
        "results": results,
    }
    out_path = DATA_DIR / "study_pre_fomc_drift_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved results to {out_path}.")

    any_promising = any(r.get("label", "").startswith("Promising") for r in results.values())
    summary = "; ".join(f"{k}: {v.get('label','?')} (n={v.get('n','?')})" for k, v in results.items())

    record = log_hypothesis(
        strategy_name="pre_fomc_drift",
        strategy_origin="data_discovered",
        parameters={"n_fomc_dates": len(fomc_dates_in_discovery), "results": results},
        data_slice_used="discovery",
        trade_count=len(fomc_dates_in_discovery),
        strategy_status="PROMISING" if any_promising else "REJECTED",
        notes=(
            f"Observatory v11 / pre-fomc-drift-design-spec.md. Direct outcome of "
            f"2026-09-09 'identify direction' staff meeting. Free calendar data "
            f"(FOMC dates). Directional pre-commitment (positive drift, Lucca & "
            f"Moench 2015) stated before running. Thin sample (~31 FOMC dates) -- "
            f"treat any positive result with skepticism per LEARN taxonomy. "
            f"Results: {summary}. Full: data/study_pre_fomc_drift_results.json."
        ),
    )
    print(f"\nLogged to ledger: {record.hypothesis_id} -- status {record.strategy_status}")


if __name__ == "__main__":
    main()
