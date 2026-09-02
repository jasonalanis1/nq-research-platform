"""
study_volatility_regime.py
=============================

Implements the "Volatility-Regime Conditioning of Post-8:30 Directional
Return" study frozen in
`research/studies/volatility-regime-post-open-behavior.md`. This went
through the most deliberate freeze process in this project's history:
a formal Phase 2 Research Direction Report, a Frozen Study
Specification presented for review before any code was written, and
one Jason-approved modification (the originally-proposed minimum
prior-history floor was removed) -- see the study doc's History section.

CHARACTERIZATION STUDY, not a strategy. No trades, no ledger entry
unless the study doc's own Step 2 gate (all five conditions) is
satisfied.

ONE primary test: does the mean 30-minute post-8:30 return differ
between the high- and low-realized-volatility tercile groups? Four
secondary horizons (60/90/120/180 min) are reported descriptively only.

HOW TO RUN:
    python3 src/study_volatility_regime.py
"""

import bisect
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_ib_breakout import OPEN_HOUR, OPEN_MINUTE
from study_overnight_gap import get_reference_close
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified, same seed/method
from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified -- "do not alter the existing cost model"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

VOL_LOOKBACK_DAYS = 20            # frozen -- not tested against alternatives
PRIMARY_HORIZON_MINUTES = 30      # frozen -- structural (Initial Balance window), not results-chosen
SECONDARY_HORIZON_MINUTES = [60, 90, 120, 180]  # descriptive only, never used to judge the study
N_BOOTSTRAP = 2000
RANDOM_SEED = 11                  # matches study_futures_expiration.py / confidence_analysis.py
ECONOMIC_THRESHOLD_POINTS = 2 * ROUND_TRIP_COST_POINTS  # frozen Step-2-gate #2, derived from the existing cost model


def compute_daily_ref_closes(day_groups: dict) -> dict:
    """day -> reference close (study_overnight_gap.get_reference_close(),
    unmodified) or None if that day has no usable bar at/before 4pm ET."""
    tz = None
    out = {}
    for day in sorted(day_groups.keys()):
        day_df = day_groups[day]
        if tz is None and len(day_df):
            tz = day_df.index.tz
        out[day] = get_reference_close(day_df, day, tz) if len(day_df) else None
    return out


def compute_daily_log_returns(ref_closes: dict) -> dict:
    """day -> r[day] = ln(ref_close[day] / ref_close[prev_valid_day]),
    where prev_valid_day is the immediately preceding day (in sorted
    order) that also has a valid ref_close -- "20 trading days," not
    calendar days, and naturally skips any day with no usable close."""
    valid_days = [d for d in sorted(ref_closes.keys()) if ref_closes[d] is not None]
    returns = {}
    for i in range(1, len(valid_days)):
        prev_day, day = valid_days[i - 1], valid_days[i]
        returns[day] = float(np.log(ref_closes[day] / ref_closes[prev_day]))
    return returns


def compute_trailing_volatility(returns: dict, all_days: list) -> dict:
    """day_t -> vol[day_t] = sample stdev (ddof=1) of the VOL_LOOKBACK_DAYS
    most recent entries in `returns` strictly before day_t, or absent
    from the dict if fewer than VOL_LOOKBACK_DAYS are available (no
    minimum beyond that -- the frozen spec's Jason-approved change)."""
    return_days_sorted = sorted(returns.keys())
    vol = {}
    for day_t in all_days:
        prior = [d for d in return_days_sorted if d < day_t]
        if len(prior) < VOL_LOOKBACK_DAYS:
            continue
        window_days = prior[-VOL_LOOKBACK_DAYS:]
        window_returns = [returns[d] for d in window_days]
        vol[day_t] = float(np.std(window_returns, ddof=1))
    return vol


def classify_regimes(vol_by_day: dict) -> dict:
    """day -> 'high' / 'low' / 'mid', via an EXPANDING causal percentile
    rank -- day_t is ranked only against {vol[s] : s <= day_t}, in
    chronological order, one day at a time. Percentile rank = (count of
    pool values <= vol[day_t]) / pool size, pool including day_t itself.
    High: rank >= 2/3. Low: rank <= 1/3. No minimum pool size is
    required (frozen spec's approved change) -- the earliest days are
    ranked against very small pools, see the study doc's Honesty flags."""
    regimes = {}
    sorted_pool = []  # kept sorted via bisect.insort, small enough (~2000) that this is cheap
    for day_t in sorted(vol_by_day.keys()):
        v = vol_by_day[day_t]
        bisect.insort(sorted_pool, v)
        n = len(sorted_pool)
        count_le = bisect.bisect_right(sorted_pool, v)
        rank = count_le / n
        if rank >= 2.0 / 3.0:
            regimes[day_t] = "high"
        elif rank <= 1.0 / 3.0:
            regimes[day_t] = "low"
        else:
            regimes[day_t] = "mid"
    return regimes


def compute_forward_return(day_df: pd.DataFrame, day, horizon_minutes: int):
    """Signed NQ-point return from today's own 8:30 AM Open to the last
    available Close within [open, open+horizon) -- identical convention
    to study_overnight_gap.py's / study_open_return_persistence.py's
    forward-return computation, factored out here since this study
    doesn't need the gap half of that logic."""
    if day_df.empty:
        return None
    tz = day_df.index.tz
    open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
    open_bars = day_df[day_df.index >= open_ts]
    if open_bars.empty:
        return None
    today_open = float(open_bars.iloc[0]["Open"])

    horizon_end_ts = open_ts + pd.Timedelta(minutes=horizon_minutes)
    day_last_ts = day_df.index.max()
    bar_duration = pd.Timedelta(minutes=1)
    if day_last_ts < horizon_end_ts - bar_duration:
        return None
    window = day_df[(day_df.index >= open_ts) & (day_df.index < horizon_end_ts)]
    if window.empty:
        return None
    return float(window.iloc[-1]["Close"] - today_open)


def scan_all_days(df: pd.DataFrame) -> pd.DataFrame:
    """Full pipeline: group once, compute ref closes -> daily log
    returns -> trailing volatility -> causal expanding-tercile regime,
    then each classifiable day's primary + secondary horizon returns."""
    day_groups = {day: sub for day, sub in df.groupby(df.index.date)}
    all_days = sorted(day_groups.keys())

    ref_closes = compute_daily_ref_closes(day_groups)
    returns = compute_daily_log_returns(ref_closes)
    vol_by_day = compute_trailing_volatility(returns, all_days)
    regimes = classify_regimes(vol_by_day)

    rows = []
    horizons = [PRIMARY_HORIZON_MINUTES] + SECONDARY_HORIZON_MINUTES
    for day in sorted(vol_by_day.keys()):
        row = {"date": day, "vol": vol_by_day[day], "regime": regimes[day]}
        day_df = day_groups[day]
        for h in horizons:
            row[f"return_{h}m"] = compute_forward_return(day_df, day, h)
        rows.append(row)
    return pd.DataFrame(rows)


def analyze_horizon(df: pd.DataFrame, horizon_minutes: int) -> dict:
    """High vs low tercile comparison for one horizon column. Mid-tercile
    rows are excluded from the primary comparison per the frozen spec."""
    col = f"return_{horizon_minutes}m"
    sub = df.dropna(subset=[col])
    high = sub[sub["regime"] == "high"][col]
    low = sub[sub["regime"] == "low"][col]

    diff_low, diff_high = bootstrap_mean_diff_ci(high, low, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED)
    significant = (diff_low > 0) or (diff_high < 0)

    pooled_n = len(high) + len(low) - 2
    pooled_std = np.sqrt(
        ((len(high) - 1) * high.std(ddof=1) ** 2 + (len(low) - 1) * low.std(ddof=1) ** 2) / pooled_n
    ) if pooled_n > 0 else float("nan")
    mean_diff = float(high.mean() - low.mean())
    cohens_d = mean_diff / pooled_std if pooled_std and pooled_std > 0 else float("nan")

    return {
        "horizon_minutes": horizon_minutes,
        "n_high": int(len(high)), "n_low": int(len(low)),
        "mean_high": float(high.mean()), "mean_low": float(low.mean()),
        "median_high": float(high.median()), "median_low": float(low.median()),
        "std_high": float(high.std(ddof=1)), "std_low": float(low.std(ddof=1)),
        "mean_diff_points": mean_diff,
        "mean_diff_dollars": mean_diff * 20.0,  # CONTRACT_MULTIPLIER, matches backtest.py
        "ci_90": (diff_low, diff_high),
        "cohens_d": float(cohens_d),
        "significant": bool(significant),
        "economically_meaningful": bool(abs(mean_diff) >= ECONOMIC_THRESHOLD_POINTS),
    }


def robustness_drop_largest_magnitude_day(df: pd.DataFrame) -> dict:
    """Step-2-gate check 4(a): primary-horizon comparison with the single
    largest-|return| day removed entirely (not just from one regime)."""
    col = f"return_{PRIMARY_HORIZON_MINUTES}m"
    sub = df.dropna(subset=[col]).copy()
    if sub.empty:
        return {}
    idx_to_drop = sub[col].abs().idxmax()
    dropped_date = sub.loc[idx_to_drop, "date"]
    reduced = sub.drop(index=idx_to_drop)
    result = analyze_horizon(reduced, PRIMARY_HORIZON_MINUTES)
    result["dropped_date"] = str(dropped_date)
    return result


def robustness_split_half(df: pd.DataFrame) -> dict:
    """Step-2-gate check 4(b): first-half vs second-half chronological
    stability of the primary-horizon high-vs-low comparison."""
    col = f"return_{PRIMARY_HORIZON_MINUTES}m"
    sub = df.dropna(subset=[col]).sort_values("date").reset_index(drop=True)
    midpoint = len(sub) // 2
    first_half = sub.iloc[:midpoint]
    second_half = sub.iloc[midpoint:]
    return {
        "first_half": analyze_horizon(first_half, PRIMARY_HORIZON_MINUTES),
        "second_half": analyze_horizon(second_half, PRIMARY_HORIZON_MINUTES),
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_volatility_regime.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    results_df = scan_all_days(discovery_df)
    out_path = DATA_DIR / "study_volatility_regime_discovery.csv"
    results_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("VOLATILITY-REGIME CONDITIONING STUDY -- Discovery slice")
    print("=" * 78)
    print(f"\nClassifiable days: {len(results_df)}  "
          f"(high={sum(results_df['regime'] == 'high')}, "
          f"mid={sum(results_df['regime'] == 'mid')}, "
          f"low={sum(results_df['regime'] == 'low')})")

    print(f"\n--- PRIMARY: {PRIMARY_HORIZON_MINUTES}-minute post-8:30 return, high vs low tercile ---")
    primary = analyze_horizon(results_df, PRIMARY_HORIZON_MINUTES)
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['significant']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= {ECONOMIC_THRESHOLD_POINTS:.3f} pts): "
          f"{primary['economically_meaningful']}")

    print("\n--- Robustness 4(a): drop single largest-magnitude return day ---")
    drop_result = robustness_drop_largest_magnitude_day(results_df)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness 4(b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(results_df)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n--- SECONDARY horizons (descriptive only) ---")
    secondary = {}
    for h in SECONDARY_HORIZON_MINUTES:
        r = analyze_horizon(results_df, h)
        secondary[h] = r
        print(f"  {h}min: mean_diff={r['mean_diff_points']:+.3f}pts  "
              f"90% CI=[{r['ci_90'][0]:+.3f}, {r['ci_90'][1]:+.3f}]  "
              f"{'SIGNIFICANT' if r['significant'] else 'not significant'}")

    print("\n" + "=" * 78)

    import json
    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "secondary": secondary,
    }
    json_path = DATA_DIR / "study_volatility_regime_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
