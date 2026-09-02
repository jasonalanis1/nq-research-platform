"""
study_futures_expiration.py
==============================

Implements the "Futures Expiration/Rollover Proximity Conditioning of
Initial Balance Breakout" study frozen in
`research/studies/futures-expiration-effects.md`. CHARACTERIZATION
STUDY, not a strategy backtest -- no new trades, no ledger entry unless
a concrete mechanical rule is triggered by a real finding.

Two independent checks, both against the Discovery slice:

  Check A: IB Breakout's already-resolved 1654 Discovery trades
  (data/backtest_results_ib_breakout_discovery.csv, from exp-028,
  unmodified) split into "Expiration Week" vs "Normal Week" using the
  public CME quarterly IMM expiration calendar (3rd Friday of
  Mar/Jun/Sep/Dec). No re-backtest.

  Check B: the overnight gap magnitude itself (reusing
  study_overnight_gap.py's own get_reference_close()/gap computation,
  unmodified), split the same way -- does |gap| run larger near
  expiration, which is what a continuous-contract splice would predict?

HOW TO RUN:
    python3 src/study_futures_expiration.py
"""

import calendar
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_overnight_gap import scan_all_days as scan_all_gaps

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

EXPIRATION_MONTHS = [3, 6, 9, 12]  # quarterly IMM contract months for NQ
N_BOOTSTRAP = 2000
RANDOM_SEED = 11  # matches confidence_analysis.py's convention, distinct from study_overnight_gap.py's 42


def third_friday(year: int, month: int) -> date:
    """The standard CME quarterly index-futures expiration convention:
    the third Friday of the given month."""
    cal = calendar.Calendar()
    fridays = [d for d in cal.itermonthdates(year, month)
               if d.month == month and d.weekday() == calendar.FRIDAY]
    return fridays[2]


def expiration_dates(start_year: int, end_year: int) -> list[date]:
    """All quarterly expiration dates (inclusive of both end years) for
    NQ's four contract months."""
    return sorted(
        third_friday(y, m)
        for y in range(start_year, end_year + 1)
        for m in EXPIRATION_MONTHS
    )


def expiration_week_ranges(start_year: int, end_year: int) -> list[tuple[date, date]]:
    """For each expiration date, the Monday-Friday range of its calendar
    week (as a closed [monday, friday] interval)."""
    ranges = []
    for exp in expiration_dates(start_year, end_year):
        monday = exp - timedelta(days=exp.weekday())  # weekday(): Monday=0
        friday = monday + timedelta(days=4)
        ranges.append((monday, friday))
    return ranges


def make_is_expiration_week(start_year: int, end_year: int):
    """Returns a fast lookup function date -> bool, precomputing the set
    of individual calendar dates that fall in any expiration week (only
    business days matter in practice, since only business days ever
    have a trading session, but weekend dates are included in the set
    for simplicity -- they never get looked up against real trade
    dates anyway)."""
    ranges = expiration_week_ranges(start_year - 1, end_year + 1)  # pad a year either side, cheap and safe
    days_in_any_range = set()
    for monday, friday in ranges:
        d = monday
        while d <= friday:
            days_in_any_range.add(d)
            d += timedelta(days=1)
    return lambda d: d in days_in_any_range


def bootstrap_total_r_ci(r_values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    """90% bootstrap CI on the TOTAL R across a group of trades -- same
    convention as confidence_analysis.py (resample with replacement,
    same size, 2000 times, take the 5th/95th percentile of the sums)."""
    rng = np.random.default_rng(seed)
    r_values = np.asarray(r_values, dtype=float)
    n = len(r_values)
    if n == 0:
        return float("nan"), float("nan")
    totals = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        sample = rng.choice(r_values, size=n, replace=True)
        totals[i] = sample.sum()
    return float(np.percentile(totals, 5)), float(np.percentile(totals, 95))


def bootstrap_mean_diff_ci(group_a, group_b, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    """90% bootstrap CI on mean(group_a) - mean(group_b), resampling
    each group independently with replacement."""
    rng = np.random.default_rng(seed)
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        sa = rng.choice(a, size=len(a), replace=True)
        sb = rng.choice(b, size=len(b), replace=True)
        diffs[i] = sa.mean() - sb.mean()
    return float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))


def analyze_ib_breakout_by_expiration(is_exp_week) -> dict:
    path = DATA_DIR / "backtest_results_ib_breakout_discovery.csv"
    trades = pd.read_csv(path, parse_dates=["date"])
    trades["is_exp_week"] = trades["date"].dt.date.apply(is_exp_week)

    result = {}
    for label, mask in [("expiration_week", trades["is_exp_week"]),
                         ("normal_week", ~trades["is_exp_week"])]:
        sub = trades[mask]
        n = len(sub)
        wins = (sub["exit_reason"] == "target").sum()
        win_rate = wins / n if n else float("nan")
        expectancy = sub["r_multiple_net"].mean() if n else float("nan")
        ci_low, ci_high = bootstrap_total_r_ci(sub["r_multiple_net"]) if n >= 2 else (float("nan"), float("nan"))
        result[label] = {
            "n": n, "win_rate": win_rate, "expectancy_r": expectancy,
            "total_r_90ci": (ci_low, ci_high),
        }
    return result


def analyze_gap_magnitude_by_expiration(discovery_df: pd.DataFrame, is_exp_week) -> dict:
    gaps_df = scan_all_gaps(discovery_df)
    gaps_df["abs_gap"] = gaps_df["gap"].abs()
    gaps_df["is_exp_week"] = gaps_df["date"].apply(is_exp_week)

    exp_gaps = gaps_df[gaps_df["is_exp_week"]]["abs_gap"]
    normal_gaps = gaps_df[~gaps_df["is_exp_week"]]["abs_gap"]

    diff_ci_low, diff_ci_high = bootstrap_mean_diff_ci(exp_gaps, normal_gaps)

    return {
        "expiration_week": {"n": len(exp_gaps), "mean_abs_gap": float(exp_gaps.mean())},
        "normal_week": {"n": len(normal_gaps), "mean_abs_gap": float(normal_gaps.mean())},
        "mean_diff_90ci": (diff_ci_low, diff_ci_high),
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_futures_expiration.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    years = sorted(set(discovery_df.index.year))
    is_exp_week = make_is_expiration_week(min(years), max(years))

    print("=" * 78)
    print("FUTURES EXPIRATION/ROLLOVER PROXIMITY STUDY -- Discovery slice")
    print("=" * 78)

    print("\n--- Check A: Initial Balance Breakout trades (exp-028, unmodified), by expiration proximity ---")
    ib_result = analyze_ib_breakout_by_expiration(is_exp_week)
    for label, r in ib_result.items():
        promo = "CLEARS bar" if (r["expectancy_r"] > 0 and r["n"] >= 150 and r["total_r_90ci"][0] > 0) else "does not clear bar"
        print(f"  {label:16s}: n={r['n']:5d}  win_rate={r['win_rate']:.1%}  "
              f"expectancy={r['expectancy_r']:+.3f}R  90% CI on total R=[{r['total_r_90ci'][0]:+.2f}R, {r['total_r_90ci'][1]:+.2f}R]  ({promo})")

    print("\n--- Check B: overnight gap magnitude (study_overnight_gap.py, unmodified), by expiration proximity ---")
    gap_result = analyze_gap_magnitude_by_expiration(discovery_df, is_exp_week)
    exp_g, norm_g = gap_result["expiration_week"], gap_result["normal_week"]
    diff_low, diff_high = gap_result["mean_diff_90ci"]
    significant = (diff_low > 0) or (diff_high < 0)
    print(f"  expiration_week: n={exp_g['n']:5d}  mean |gap|={exp_g['mean_abs_gap']:.2f} pts")
    print(f"  normal_week:     n={norm_g['n']:5d}  mean |gap|={norm_g['mean_abs_gap']:.2f} pts")
    print(f"  90% CI on (expiration_week - normal_week) mean |gap|: [{diff_low:+.3f}, {diff_high:+.3f}] pts  "
          f"{'SIGNIFICANT' if significant else 'not significant'}")

    print("\n" + "=" * 78)

    # Save the raw grouped data for the write-up / any follow-up.
    out = {
        "ib_breakout": ib_result,
        "gap_magnitude": gap_result,
    }
    import json
    out_path = DATA_DIR / "study_futures_expiration_discovery.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved results to {out_path}.")


if __name__ == "__main__":
    main()
