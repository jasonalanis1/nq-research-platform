"""
study_turn_of_month.py
=======================

Turn-of-the-Month (TOM) effect scan -- frozen spec:
research/studies/turn-of-the-month-design-spec.md.

First flow/calendar-mechanism candidate tested by this project (all
prior findings were pure volatility-clustering). Data requirement:
none beyond existing NQ 1-min bars -- TOM classification is derived
purely from the calendar. Directional pre-commitment (TOM > non-TOM
mean return) stated in the frozen spec, per the literature
(Ariel 1987; Lakonishok & Smidt 1988), BEFORE this scan ran.

Non-trading, exploratory. Discovery data only.

HOW TO RUN:
    python3 src/study_turn_of_month.py
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
ROUND_TRIP_COST_PTS = 0.75


def is_tom_day(trading_days_this_month, day):
    """TOM window: last trading day of month through 3rd trading day of
    following month, inclusive (Ariel / Lakonishok-Smidt convention)."""
    idx_in_month = trading_days_this_month.index(day)
    is_last_of_month = idx_in_month == len(trading_days_this_month) - 1
    return is_last_of_month


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
    print("TURN-OF-THE-MONTH EFFECT -- frozen scan (exploratory)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/turn-of-the-month-design-spec.md\n")

    df, is_synthetic = load_price_data(context="study_turn_of_month.py")
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

    # trading days grouped by (year, month) to find TOM window per protocol
    by_month = {}
    for d in days_sorted:
        key = (d.year, d.month)
        by_month.setdefault(key, []).append(d)
    for key in by_month:
        by_month[key].sort()

    month_keys_sorted = sorted(by_month.keys())

    tom_days = set()
    for mi, key in enumerate(month_keys_sorted):
        month_days = by_month[key]
        # last trading day of this month
        tom_days.add(month_days[-1])
        # first up-to-3 trading days of the NEXT month
        if mi + 1 < len(month_keys_sorted):
            next_days = by_month[month_keys_sorted[mi + 1]]
            for d in next_days[:3]:
                tom_days.add(d)

    tom_rets, non_tom_rets = [], []
    tom_rets_r, non_tom_rets_r = [], []
    n_skipped = 0

    for day in days_sorted:
        if day not in daily_bars.index:
            n_skipped += 1
            continue
        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty or len(rth) < 20:
            n_skipped += 1
            continue
        open_price = float(rth["Close"].iloc[0])
        close_price = float(rth["Close"].iloc[-1])
        ret = close_price - open_price
        ret_r = ret / ROUND_TRIP_COST_PTS  # simple R convention used elsewhere in project (points / cost unit)

        if day in tom_days:
            tom_rets.append(ret)
            tom_rets_r.append(ret_r)
        else:
            non_tom_rets.append(ret)
            non_tom_rets_r.append(ret_r)

    n_tom, n_non_tom = len(tom_rets), len(non_tom_rets)
    print(f"\nTOM days: {n_tom}   non-TOM days: {n_non_tom}   skipped: {n_skipped}")

    tom_arr, non_tom_arr = np.array(tom_rets), np.array(non_tom_rets)
    effect_size = float(tom_arr.mean() - non_tom_arr.mean())
    ci = bootstrap_diff_ci(tom_arr, non_tom_arr)
    atr_normalized_effect = abs(effect_size) / avg_atr if avg_atr > 0 else float("nan")
    cost_priority = "LOW_PRIORITY_COST_DOMINATED" if atr_normalized_effect < ATR_NORMALIZED_FLOOR else "NORMAL"

    credible = ci[0] > 0 or ci[1] < 0
    direction_matches_literature = effect_size > 0  # pre-specified: TOM > non-TOM

    print(f"\nTOM mean RTH return:     {tom_arr.mean():.3f} pts")
    print(f"non-TOM mean RTH return: {non_tom_arr.mean():.3f} pts")
    print(f"Effect size (diff):      {effect_size:.3f} pts")
    print(f"90% bootstrap CI:        {ci}")
    print(f"Credible (CI excludes 0): {credible}")
    print(f"Direction matches literature (TOM > non-TOM): {direction_matches_literature}")
    print(f"ATR-normalized effect: {atr_normalized_effect:.4f} (floor {ATR_NORMALIZED_FLOOR}) -> {cost_priority}")

    label = "No meaningful difference"
    if credible and direction_matches_literature and cost_priority == "NORMAL":
        label = "Promising"
    elif credible and direction_matches_literature:
        label = "Interesting (cost-dominated)"
    elif credible and not direction_matches_literature:
        label = "Credible but WRONG DIRECTION vs literature"

    print(f"\nLabel: {label}")

    out = {
        "spec": "research/studies/turn-of-the-month-design-spec.md",
        "status": "EXPLORATORY -- not a finding, not a strategy",
        "n_tom_days": n_tom,
        "n_non_tom_days": n_non_tom,
        "n_skipped": n_skipped,
        "tom_mean_return": float(tom_arr.mean()),
        "non_tom_mean_return": float(non_tom_arr.mean()),
        "effect_size": effect_size,
        "ci_90_diff": ci,
        "credible": credible,
        "direction_matches_literature": direction_matches_literature,
        "avg_atr14": avg_atr,
        "atr_normalized_effect": atr_normalized_effect,
        "cost_priority": cost_priority,
        "label": label,
    }
    out_path = DATA_DIR / "study_turn_of_month_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved results to {out_path}.")

    record = log_hypothesis(
        strategy_name="turn_of_month_effect",
        strategy_origin="data_discovered",
        parameters={
            "n_tom": n_tom, "n_non_tom": n_non_tom,
            "tom_mean": float(tom_arr.mean()), "non_tom_mean": float(non_tom_arr.mean()),
            "effect_size": effect_size, "ci_90": list(ci),
            "atr_normalized_effect": atr_normalized_effect,
        },
        data_slice_used="discovery",
        trade_count=n_tom,
        strategy_status="PROMISING" if label == "Promising" else "REJECTED",
        notes=(
            f"Observatory v8 / turn-of-month-design-spec.md. First flow/calendar-"
            f"mechanism candidate (vs. prior volatility-clustering findings). "
            f"Free/zero-cost data (calendar-derived from existing bars). "
            f"Result: {label}. effect={effect_size:.3f}pts ci_90={ci}. "
            f"Full: data/study_turn_of_month_results.json."
        ),
    )
    print(f"\nLogged to ledger: {record.hypothesis_id} -- status {record.strategy_status}")


if __name__ == "__main__":
    main()
