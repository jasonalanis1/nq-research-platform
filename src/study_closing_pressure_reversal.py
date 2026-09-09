"""
study_closing_pressure_reversal.py
====================================

Closing-pressure reversal -- frozen spec:
research/studies/closing-pressure-reversal-design-spec.md.

Sourced from the market-microstructure research agent (2026-09-09).
Free, OHLCV-derivable proxy for closing-auction imbalance (last-15-min
RTH return) vs. next-session return. Directional pre-commitment
(reversal, not continuation) stated in the frozen spec BEFORE this
scan ran, per Bogousslavsky & Muravyev (2023).

Non-trading, exploratory. Discovery data only.

HOW TO RUN:
    python3 src/study_closing_pressure_reversal.py
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

LOOKBACK_DAYS = 20
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_WINDOW = 14
ATR_NORMALIZED_FLOOR = 0.05
MIN_N_FOR_PROMISING = 40


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
    print("CLOSING-PRESSURE REVERSAL -- frozen scan (exploratory)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/closing-pressure-reversal-design-spec.md\n")

    df, is_synthetic = load_price_data(context="study_closing_pressure_reversal.py")
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

    # per-day: last-15-min RTH return, and full RTH return
    late_return = {}
    day_return = {}
    for day in days_sorted:
        rth = day_groups[day].between_time("09:30", "16:00")
        if rth.empty or len(rth) < 30:
            continue
        day_return[day] = float(rth["Close"].iloc[-1] - rth["Close"].iloc[0])
        late = rth.between_time("15:45", "16:00")
        if late.empty or len(late) < 5:
            continue
        late_return[day] = float(late["Close"].iloc[-1] - late["Close"].iloc[0])

    days_with_late = sorted(late_return.keys())
    print(f"Days with usable last-15-min + next-day data: {len(days_with_late)}")

    late_up_next, late_down_next, moderate_next = [], [], []

    for i, day in enumerate(days_with_late):
        # need a next trading day with a full RTH return
        idx_in_all = days_sorted.index(day)
        next_day = None
        for j in range(idx_in_all + 1, len(days_sorted)):
            if days_sorted[j] in day_return:
                next_day = days_sorted[j]
                break
        if next_day is None:
            continue
        next_ret = day_return[next_day]

        # trailing 20-day distribution of late_return, excluding today
        prior_days = [d for d in days_with_late if d < day][-LOOKBACK_DAYS:]
        if len(prior_days) < LOOKBACK_DAYS:
            continue
        prior_vals = np.array([late_return[d] for d in prior_days])
        p33, p67 = np.percentile(prior_vals, [33.33, 66.67])

        today_late = late_return[day]
        if today_late >= p67 and today_late > 0:
            late_up_next.append(next_ret)
        elif today_late <= p33 and today_late < 0:
            late_down_next.append(next_ret)
        else:
            moderate_next.append(next_ret)

    n_up, n_down, n_mod = len(late_up_next), len(late_down_next), len(moderate_next)
    print(f"\nlate_up observations: {n_up}   late_down observations: {n_down}   moderate: {n_mod}")

    results = {}
    for label, group in [("late_up", late_up_next), ("late_down", late_down_next)]:
        if len(group) < 5 or n_mod < 20:
            results[label] = None
            continue
        g_arr = np.array(group)
        m_arr = np.array(moderate_next)
        effect = float(g_arr.mean() - m_arr.mean())
        ci = bootstrap_diff_ci(g_arr, m_arr)
        atr_norm = abs(effect) / avg_atr if avg_atr > 0 else float("nan")
        cost_priority = "LOW_PRIORITY_COST_DOMINATED" if atr_norm < ATR_NORMALIZED_FLOOR else "NORMAL"
        credible = ci[0] > 0 or ci[1] < 0
        # pre-specified reversal direction: late_up -> negative next-day effect; late_down -> positive
        expected_sign = -1 if label == "late_up" else 1
        direction_matches = np.sign(effect) == expected_sign if effect != 0 else False

        n_this = len(group)
        if n_this >= MIN_N_FOR_PROMISING and credible and direction_matches and cost_priority == "NORMAL":
            lbl = "Promising"
        elif credible and direction_matches:
            lbl = "Interesting" if cost_priority == "NORMAL" else "Interesting (cost-dominated)"
        elif credible and not direction_matches:
            lbl = "Credible but WRONG DIRECTION vs literature"
        else:
            lbl = "No meaningful difference"

        print(f"\n{label}: n={n_this} mean_next_day={g_arr.mean():.3f} vs moderate={m_arr.mean():.3f} "
              f"effect={effect:.3f} ci_90={ci} atr_norm={atr_norm:.4f} -> {cost_priority} -> {lbl}")

        results[label] = {
            "n": n_this, "mean_next_day": float(g_arr.mean()), "moderate_mean": float(m_arr.mean()),
            "effect_size": effect, "ci_90_diff": ci, "atr_normalized_effect": atr_norm,
            "cost_priority": cost_priority, "direction_matches_literature": bool(direction_matches),
            "label": lbl,
        }

    out = {
        "spec": "research/studies/closing-pressure-reversal-design-spec.md",
        "status": "EXPLORATORY -- not a finding, not a strategy",
        "n_late_up": n_up, "n_late_down": n_down, "n_moderate": n_mod,
        "avg_atr14": avg_atr,
        "results": results,
    }
    out_path = DATA_DIR / "study_closing_pressure_reversal_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved results to {out_path}.")

    any_promising = any(r and r["label"] == "Promising" for r in results.values())
    summary_bits = []
    for label, r in results.items():
        if r is None:
            summary_bits.append(f"{label}: insufficient n")
        else:
            summary_bits.append(f"{label}: {r['label']} (n={r['n']}, effect={r['effect_size']:.3f}, ci_90={r['ci_90_diff']})")
    summary = "; ".join(summary_bits)

    record = log_hypothesis(
        strategy_name="closing_pressure_reversal",
        strategy_origin="data_discovered",
        parameters={"n_late_up": n_up, "n_late_down": n_down, "n_moderate": n_mod, "results": results},
        data_slice_used="discovery",
        trade_count=n_up + n_down,
        strategy_status="PROMISING" if any_promising else "REJECTED",
        notes=(
            f"Observatory v10 / closing-pressure-reversal-design-spec.md. Sourced from "
            f"market-microstructure research agent (2026-09-09), free/zero-cost OHLCV-"
            f"derivable data (last-15-min RTH return as closing-imbalance proxy). "
            f"Directional pre-commitment: reversal (Bogousslavsky & Muravyev 2023), "
            f"stated before running. Results: {summary}. "
            f"Full: data/study_closing_pressure_reversal_results.json."
        ),
    )
    print(f"\nLogged to ledger: {record.hypothesis_id} -- status {record.strategy_status}")


if __name__ == "__main__":
    main()
