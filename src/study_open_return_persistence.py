"""
study_open_return_persistence.py
===================================

Implements the "Open Return Persistence Study" frozen in
`research/studies/open-return-persistence.md`. This is a CHARACTERIZATION
STUDY, not a strategy backtest -- no entry/stop/target, no trades, no
hypothesis ledger entry. It asks a direct, model-free question: does the
Initial Balance's own directional return predict anything about what
happens afterward, at several fixed horizons, with no chart pattern
imposed at all?

REUSES, UNCHANGED: the Initial Balance window
(OPEN_HOUR/OPEN_MINUTE/IB_MINUTES) from detect_ib_breakout.py -- not
redefined here, so this study is directly comparable to exp-028 rather
than introducing a fresh, unjustified window choice.

HOW TO RUN:
    python3 src/study_open_return_persistence.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_ib_breakout import OPEN_HOUR, OPEN_MINUTE, IB_MINUTES

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

HORIZON_MINUTES = [30, 60, 90, 120, 180]  # measured from the END of the IB window (9:00 AM ET)
N_BOOTSTRAP = 2000
RANDOM_SEED = 42


def compute_day_returns(day_df: pd.DataFrame, day) -> dict | None:
    """
    For one day's bars, returns a dict with the IB return and the
    forward return at each horizon in HORIZON_MINUTES, or None if the
    day doesn't have enough data to compute the IB window at all.
    Horizons with no data yet within the day (e.g. a short/holiday
    session) are recorded as None for that horizon only -- the day
    isn't dropped entirely just because one long horizon is missing.
    """
    tz = day_df.index.tz
    open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
    ib_end_ts = open_ts + pd.Timedelta(minutes=IB_MINUTES)

    ib_bars = day_df[(day_df.index >= open_ts) & (day_df.index < ib_end_ts)]
    if ib_bars.empty:
        return None  # not enough data to define the IB window for this day

    ib_open = ib_bars.iloc[0]["Open"]
    ib_close = ib_bars.iloc[-1]["Close"]
    ib_return = ib_close - ib_open

    # Bars are indexed by OPEN timestamp, so the last bar's data only
    # covers up to (its index + 1 bar). A day's coverage must reach
    # horizon_end_ts - 1 bar for that horizon to be considered fully
    # observed -- otherwise a short/early-close session would silently
    # get treated as if a shorter window (whatever data happened to
    # exist) were the full-horizon forward return, corrupting that
    # horizon's column with an apples-to-oranges number.
    day_last_ts = day_df.index.max()
    bar_duration = pd.Timedelta(minutes=1)

    row = {"date": day, "ib_open": ib_open, "ib_close": ib_close, "ib_return": ib_return}
    for h in HORIZON_MINUTES:
        horizon_end_ts = ib_end_ts + pd.Timedelta(minutes=h)
        if day_last_ts < horizon_end_ts - bar_duration:
            row[f"fwd_return_{h}m"] = None  # day doesn't have data reaching this far out
            continue
        window = day_df[(day_df.index >= ib_end_ts) & (day_df.index < horizon_end_ts)]
        row[f"fwd_return_{h}m"] = (window.iloc[-1]["Close"] - ib_close) if not window.empty else None
    return row


def scan_all_days(df: pd.DataFrame) -> pd.DataFrame:
    """Walks every day in df and returns a DataFrame, one row per day
    that had a usable IB window (see compute_day_returns)."""
    all_days = sorted(set(df.index.date))
    rows = []
    for day in all_days:
        day_df = df[df.index.date == day]
        row = compute_day_returns(day_df, day)
        if row is not None:
            rows.append(row)
    return pd.DataFrame(rows)


def bootstrap_correlation_ci(x: np.ndarray, y: np.ndarray, n_bootstrap: int = N_BOOTSTRAP,
                              seed: int = RANDOM_SEED) -> tuple[float, float]:
    """90% bootstrap CI on the Pearson correlation between x and y,
    resampling (x, y) PAIRS together with replacement -- same convention
    confidence_analysis.py already uses elsewhere in this project."""
    rng = np.random.default_rng(seed)
    n = len(x)
    corrs = np.empty(n_bootstrap)
    idx_pool = np.arange(n)
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=n, replace=True)
        corrs[i] = np.corrcoef(x[idx], y[idx])[0, 1]
    return float(np.percentile(corrs, 5)), float(np.percentile(corrs, 95))


def bootstrap_mean_diff_ci(pos_vals: np.ndarray, neg_vals: np.ndarray, n_bootstrap: int = N_BOOTSTRAP,
                            seed: int = RANDOM_SEED) -> tuple[float, float]:
    """90% bootstrap CI on (mean of pos_vals - mean of neg_vals), each
    group resampled independently with replacement."""
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        pos_sample = rng.choice(pos_vals, size=len(pos_vals), replace=True)
        neg_sample = rng.choice(neg_vals, size=len(neg_vals), replace=True)
        diffs[i] = pos_sample.mean() - neg_sample.mean()
    return float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))


def analyze_horizon(returns_df: pd.DataFrame, horizon: int) -> dict:
    """Computes the correlation and conditional-mean statistics for one
    horizon, dropping only the days missing data for THIS horizon."""
    col = f"fwd_return_{horizon}m"
    valid = returns_df.dropna(subset=[col])
    x = valid["ib_return"].to_numpy()
    y = valid[col].to_numpy()
    n = len(valid)

    corr = float(np.corrcoef(x, y)[0, 1]) if n >= 2 else float("nan")
    corr_ci_low, corr_ci_high = bootstrap_correlation_ci(x, y) if n >= 2 else (float("nan"), float("nan"))
    corr_significant = (corr_ci_low > 0) or (corr_ci_high < 0) if n >= 2 else False

    pos = valid[valid["ib_return"] > 0][col].to_numpy()
    neg = valid[valid["ib_return"] < 0][col].to_numpy()
    mean_after_up = float(pos.mean()) if len(pos) else float("nan")
    mean_after_down = float(neg.mean()) if len(neg) else float("nan")
    mean_diff = mean_after_up - mean_after_down if len(pos) and len(neg) else float("nan")
    diff_ci_low, diff_ci_high = (
        bootstrap_mean_diff_ci(pos, neg) if len(pos) >= 2 and len(neg) >= 2 else (float("nan"), float("nan"))
    )
    diff_significant = (diff_ci_low > 0) or (diff_ci_high < 0) if len(pos) >= 2 and len(neg) >= 2 else False

    return {
        "horizon_minutes": horizon,
        "n_days": n,
        "n_ib_up_days": len(pos),
        "n_ib_down_days": len(neg),
        "correlation": corr,
        "correlation_90ci": (corr_ci_low, corr_ci_high),
        "correlation_significant": corr_significant,
        "mean_fwd_return_after_ib_up": mean_after_up,
        "mean_fwd_return_after_ib_down": mean_after_down,
        "mean_diff_90ci": (diff_ci_low, diff_ci_high),
        "mean_diff_significant": diff_significant,
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_open_return_persistence.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    returns_df = scan_all_days(discovery_df)
    out_path = DATA_DIR / "study_open_return_persistence_discovery.csv"
    returns_df.to_csv(out_path, index=False)
    print(f"\nComputed IB + forward returns for {len(returns_df)} Discovery day(s). Saved to {out_path}.\n")

    print("=" * 78)
    print("OPEN RETURN PERSISTENCE STUDY -- Discovery slice")
    print("=" * 78)
    for h in HORIZON_MINUTES:
        r = analyze_horizon(returns_df, h)
        print(f"\n--- Horizon: +{h} min after IB end (9:00 AM ET) --- n={r['n_days']} "
              f"({r['n_ib_up_days']} IB-up, {r['n_ib_down_days']} IB-down)")
        print(f"  Correlation(ib_return, fwd_return): {r['correlation']:+.4f}   "
              f"90% CI: [{r['correlation_90ci'][0]:+.4f}, {r['correlation_90ci'][1]:+.4f}]   "
              f"{'SIGNIFICANT' if r['correlation_significant'] else 'not significant'}")
        print(f"  Mean fwd return after IB-up:   {r['mean_fwd_return_after_ib_up']:+.2f} pts")
        print(f"  Mean fwd return after IB-down: {r['mean_fwd_return_after_ib_down']:+.2f} pts")
        print(f"  Difference (up - down): 90% CI: [{r['mean_diff_90ci'][0]:+.2f}, {r['mean_diff_90ci'][1]:+.2f}]   "
              f"{'SIGNIFICANT' if r['mean_diff_significant'] else 'not significant'}")
    print("\n" + "=" * 78)


if __name__ == "__main__":
    main()
