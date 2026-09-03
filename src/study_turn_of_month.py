"""
study_turn_of_month.py
=======================

Implements "Turn-of-the-Month Effect -- Cheap Side-Check (exp-043)"
frozen in `research/studies/turn-of-month-check.md`. A deliberately
narrow, two-step-gated check: Step 1 is a free descriptive look at
whether NQ daily point-returns differ on turn-of-month days; Step 2
(a costed long-only rule) runs ONLY if Step 1 clears both of its
pre-registered conditions.

HOW TO RUN:
    python3 src/study_turn_of_month.py
"""

import json
from pathlib import Path

import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes  # reused unmodified
from study_nq_trend_following import bootstrap_mean_ci  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def compute_point_returns(ref_closes: dict) -> pd.DataFrame:
    """One row per classifiable day (from the second valid day onward):
    date, point_return = ref_close[t] - ref_close[t-1]. Same convention
    as study_nq_trend_following.compute_daily_pnl's price_change."""
    valid_days = [d for d in sorted(ref_closes.keys()) if ref_closes[d] is not None]
    rows = []
    for i in range(1, len(valid_days)):
        prev_day, day = valid_days[i - 1], valid_days[i]
        rows.append({
            "date": day,
            "point_return": float(ref_closes[day] - ref_closes[prev_day]),
        })
    return pd.DataFrame(rows)


def classify_turn_of_month(dates: list) -> dict:
    """date -> True if it is the LAST classifiable trading day of its
    calendar month, or one of the FIRST THREE classifiable trading
    days of the following calendar month. Frozen spec definition,
    computed purely from the project's own classifiable-day calendar
    (no external holiday list needed)."""
    sorted_dates = sorted(dates)
    by_month = {}
    for d in sorted_dates:
        key = (d.year, d.month)
        by_month.setdefault(key, []).append(d)

    month_keys_sorted = sorted(by_month.keys())
    is_turn = {d: False for d in sorted_dates}

    for i, key in enumerate(month_keys_sorted):
        days_in_month = by_month[key]
        last_day = days_in_month[-1]
        is_turn[last_day] = True
        if i + 1 < len(month_keys_sorted):
            next_key = month_keys_sorted[i + 1]
            next_days = by_month[next_key][:3]
            for d in next_days:
                is_turn[d] = True

    return is_turn


def describe_group(values) -> dict:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "ci_90": (float("nan"), float("nan")),
                "statistically_credible_positive": False}
    mean_v = float(sum(values) / n)
    ci_low, ci_high = bootstrap_mean_ci(values) if n >= 2 else (float("nan"), float("nan"))
    return {
        "n": int(n),
        "mean": mean_v,
        "ci_90": (ci_low, ci_high),
        "statistically_credible_positive": bool(n >= 2 and ci_low > 0),
    }


def run_step1(returns_df: pd.DataFrame) -> dict:
    turn_flags = classify_turn_of_month(returns_df["date"].tolist())
    returns_df = returns_df.copy()
    returns_df["is_turn_of_month"] = returns_df["date"].map(turn_flags)

    turn_vals = returns_df.loc[returns_df["is_turn_of_month"], "point_return"].tolist()
    other_vals = returns_df.loc[~returns_df["is_turn_of_month"], "point_return"].tolist()

    turn_stats = describe_group(turn_vals)
    other_stats = describe_group(other_vals)

    step1_pass = bool(
        turn_stats["n"] >= 2
        and turn_stats["mean"] > 0
        and turn_stats["statistically_credible_positive"]
    )

    return {
        "turn_of_month_days": turn_stats,
        "other_days": other_stats,
        "step1_pass": step1_pass,
        "returns_df": returns_df,
    }


def run_step2(returns_df: pd.DataFrame) -> dict:
    """Only called if Step 1 passes. Long-only on turn-of-month days,
    one round-trip cost charged per day held."""
    turn_df = returns_df[returns_df["is_turn_of_month"]].copy()
    turn_df["net_pnl"] = turn_df["point_return"] - ROUND_TRIP_COST_POINTS
    n = len(turn_df)
    net = turn_df["net_pnl"].tolist()
    mean_net = float(sum(net) / n) if n else float("nan")
    ci_low, ci_high = bootstrap_mean_ci(net) if n >= 2 else (float("nan"), float("nan"))
    statistically_credible = bool(n >= 2 and ci_low > 0)
    economic_threshold = 2 * ROUND_TRIP_COST_POINTS
    economically_meaningful = bool(mean_net >= economic_threshold) if n else False
    return {
        "n": int(n),
        "mean_net_pnl": mean_net,
        "ci_90": (ci_low, ci_high),
        "statistically_credible": statistically_credible,
        "economic_threshold_points": economic_threshold,
        "economically_meaningful": economically_meaningful,
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_turn_of_month.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)
    returns_df = compute_point_returns(ref_closes)

    print("=" * 78)
    print("TURN-OF-THE-MONTH EFFECT -- Cheap Side-Check (exp-043) -- Discovery slice")
    print("=" * 78)
    print(f"\nClassifiable days with a computed point-return: {len(returns_df)}")

    step1 = run_step1(returns_df)
    print("\n--- STEP 1: descriptive, no cost ---")
    print("  Turn-of-month days:", step1["turn_of_month_days"])
    print("  Other days:        ", step1["other_days"])
    print(f"\n  Step 1 pass (positive AND statistically credible on turn-of-month days)? "
          f"{step1['step1_pass']}")

    out = {
        "step1": {
            "turn_of_month_days": step1["turn_of_month_days"],
            "other_days": step1["other_days"],
            "step1_pass": step1["step1_pass"],
        }
    }

    if step1["step1_pass"]:
        print("\n--- STEP 2: costed long-only rule on turn-of-month days (gated, triggered) ---")
        step2 = run_step2(step1["returns_df"])
        for k, v in step2.items():
            print(f"  {k}: {v}")
        out["step2"] = step2
    else:
        print("\n--- STEP 2: NOT RUN (Step 1 did not clear both pre-registered conditions) ---")
        out["step2"] = None

    print("\n" + "=" * 78)

    csv_path = DATA_DIR / "study_turn_of_month_discovery.csv"
    step1["returns_df"].to_csv(csv_path, index=False)
    json_path = DATA_DIR / "study_turn_of_month_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
