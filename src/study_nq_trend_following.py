"""
study_nq_trend_following.py
===============================

Implements "NQ Daily Time-Series Momentum (Trend-Following)" frozen in
`research/studies/nq-daily-trend-following.md`. First daily-resolution
study in this project's history, following the 2026-09-02 pivot
(docs/ROADMAP.md) after twelve straight null intraday hypotheses. Also
the first study whose promotion mechanics are a disclosed, one-time
adaptation of the standing 150-trades bar -- see that doc's "Why the
promotion bar is adapted for this study" section, and the matching
note in docs/ROADMAP.md's "Promotion bar" section.

CHARACTERIZATION-AND-PROMOTION STUDY, structured like every prior
hypothesis test in this project: one primary question, pre-committed,
with a Step 2 gate checked honestly -- not a loosening of standards,
an adaptation of how they're measured for a slow-rebalancing signal.

ONE primary test: is the mean daily net P&L of a 252-trading-day
time-series-momentum position (long when the trailing ~12-month log
return is positive, short when negative, daily rebalanced, fully
causal) positive and statistically credible -- 90% bootstrap CI on the
mean entirely above zero?

HOW TO RUN:
    python3 src/study_nq_trend_following.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes, compute_daily_log_returns  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

MOMENTUM_LOOKBACK_DAYS = 252   # frozen -- ~12 months, the Moskowitz/Ooi/Pedersen time-series-momentum convention
N_BOOTSTRAP = 2000
RANDOM_SEED = 11               # matches study_volatility_regime.py's current-convention seed
FLIP_COST_POINTS = 2 * ROUND_TRIP_COST_POINTS  # closing the old position + opening the new one on a flip


def compute_momentum_signal(returns: dict, all_days: list) -> dict:
    """day_t -> mom[day_t] = SUM of the MOMENTUM_LOOKBACK_DAYS most
    recent daily log returns strictly before day_t (the trailing
    cumulative log return, i.e. trend direction/magnitude), or absent
    from the dict if fewer than that many prior returns are available.
    Structurally identical to
    study_volatility_regime.compute_trailing_volatility(), swapping
    stdev for sum -- no minimum floor beyond the lookback itself."""
    return_days_sorted = sorted(returns.keys())
    mom = {}
    for day_t in all_days:
        prior = [d for d in return_days_sorted if d < day_t]
        if len(prior) < MOMENTUM_LOOKBACK_DAYS:
            continue
        window_days = prior[-MOMENTUM_LOOKBACK_DAYS:]
        mom[day_t] = float(sum(returns[d] for d in window_days))
    return mom


def compute_positions(mom_by_day: dict) -> dict:
    """day -> +1 (long) if mom[day] > 0, -1 (short) if mom[day] < 0.
    In the practically-impossible exact-zero case, holds the previous
    day's position (defaulting to +1 if it's also the very first
    classifiable day) -- frozen spec item 4."""
    positions = {}
    prev = 1
    for day in sorted(mom_by_day.keys()):
        m = mom_by_day[day]
        if m > 0:
            pos = 1
        elif m < 0:
            pos = -1
        else:
            pos = prev
        positions[day] = pos
        prev = pos
    return positions


def compute_daily_pnl(positions: dict, ref_closes: dict) -> pd.DataFrame:
    """One row per classifiable day with a valid reference close, from
    the second such day onward: today's P&L uses TODAY's position
    (already known before today's session, since it was computed from
    data through yesterday's close) against today's actual price
    change (frozen spec item 6), charging FLIP_COST_POINTS when
    today's position differs from the PRIOR VALID day's position.

    A day is first filtered OUT entirely if it has no valid
    ref_close (rather than being walked and then skipped), so its
    predecessor and successor pair directly with each other -- one
    missing day costs one day of P&L, not two. Same "filter to valid
    days first, then walk consecutive pairs in that filtered list"
    convention already used for the cross-instrument join in
    study_es_gap_incremental_info.build_joint_dataset()."""
    days = sorted(d for d in positions.keys() if ref_closes.get(d) is not None)
    rows = []
    for i in range(1, len(days)):
        prev_day, day = days[i - 1], days[i]
        prev_close = ref_closes[prev_day]
        today_close = ref_closes[day]
        position = positions[day]
        prev_position = positions[prev_day]
        price_change = today_close - prev_close
        pnl = position * price_change
        flipped = position != prev_position
        cost = FLIP_COST_POINTS if flipped else 0.0
        rows.append({
            "date": day,
            "position": position,
            "flipped": bool(flipped),
            "price_change": price_change,
            "pnl": pnl,
            "cost": cost,
            "net_pnl": pnl - cost,
        })
    return pd.DataFrame(rows)


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    """90% bootstrap CI on the mean of `values`, resampling with
    replacement -- the same nonparametric resample-and-recompute
    convention as every other bootstrap in this project."""
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    means = np.empty(n_bootstrap)
    idx_pool = np.arange(n)
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=n, replace=True)
        means[i] = arr[idx].mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def analyze_primary(pnl_df: pd.DataFrame) -> dict:
    """The adapted Step-2-gate checks 1 and 2 (frozen spec item 9),
    plus the mandatory flip-count disclosure (item 10)."""
    n = len(pnl_df)
    net_pnl = pnl_df["net_pnl"].to_numpy()
    mean_net_pnl = float(net_pnl.mean()) if n else float("nan")
    ci_low, ci_high = bootstrap_mean_ci(net_pnl) if n >= 2 else (float("nan"), float("nan"))
    statistically_credible = bool(ci_low > 0) if n >= 2 else False

    n_flips = int(pnl_df["flipped"].sum()) if n else 0
    total_cost = float(pnl_df["cost"].sum()) if n else 0.0
    avg_daily_cost_drag = total_cost / n if n else 0.0
    economic_threshold = 2 * avg_daily_cost_drag
    economically_meaningful = bool(mean_net_pnl >= economic_threshold) if n else False

    return {
        "n": int(n),
        "mean_net_pnl": mean_net_pnl,
        "ci_90": (ci_low, ci_high),
        "statistically_credible": statistically_credible,
        "n_flips": n_flips,
        "total_cost_points": total_cost,
        "avg_daily_cost_drag": avg_daily_cost_drag,
        "economic_threshold_points": economic_threshold,
        "economically_meaningful": economically_meaningful,
    }


def robustness_drop_largest_pnl_day(pnl_df: pd.DataFrame) -> dict:
    """Robustness check (a): primary result with the single
    largest-magnitude daily net P&L day removed entirely."""
    if pnl_df.empty:
        return {}
    idx_to_drop = pnl_df["net_pnl"].abs().idxmax()
    dropped_date = pnl_df.loc[idx_to_drop, "date"]
    reduced = pnl_df.drop(index=idx_to_drop)
    result = analyze_primary(reduced)
    result["dropped_date"] = str(dropped_date)
    return result


def robustness_split_half(pnl_df: pd.DataFrame) -> dict:
    """Robustness check (b): first-half vs second-half chronological
    stability, same convention as exp-036/exp-037."""
    sub = pnl_df.sort_values("date").reset_index(drop=True)
    midpoint = len(sub) // 2
    first_half = sub.iloc[:midpoint]
    second_half = sub.iloc[midpoint:]
    return {
        "first_half": analyze_primary(first_half),
        "second_half": analyze_primary(second_half),
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_nq_trend_following.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)
    returns = compute_daily_log_returns(ref_closes)
    all_days = sorted(day_groups.keys())

    mom_by_day = compute_momentum_signal(returns, all_days)
    positions = compute_positions(mom_by_day)
    pnl_df = compute_daily_pnl(positions, ref_closes)

    out_path = DATA_DIR / "study_nq_trend_following_discovery.csv"
    pnl_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("NQ DAILY TIME-SERIES MOMENTUM STUDY -- Discovery slice")
    print("=" * 78)
    print(f"\nClassifiable days ({MOMENTUM_LOOKBACK_DAYS}+ prior daily returns): {len(mom_by_day)}")
    print(f"Days with a computed daily P&L: {len(pnl_df)}")

    primary = analyze_primary(pnl_df)
    print("\n--- PRIMARY: mean daily net P&L ---")
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['statistically_credible']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= 2x own realized cost drag): "
          f"{primary['economically_meaningful']}")
    print(f"\n  MANDATORY DISCLOSURE -- position flips: {primary['n_flips']} "
          f"across {primary['n']} classifiable days")

    print("\n--- Robustness (a): drop single largest-magnitude daily net P&L day ---")
    drop_result = robustness_drop_largest_pnl_day(pnl_df)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(pnl_df)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n" + "=" * 78)

    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
    }
    json_path = DATA_DIR / "study_nq_trend_following_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
