"""
study_overnight_gap.py
=========================

Implements the "Overnight Gap Behavior Study" frozen in
`research/studies/overnight-gap-behavior.md`. CHARACTERIZATION STUDY,
not a strategy backtest -- no trades, no ledger entry unless Step 3 is
reached with a concrete mechanical rule.

Asks two things about the SIGNED gap between the prior day's 4:00 PM ET
reference close and today's 8:30 AM ET open: (1) how often does price
fill it back by noon, and (2) does its size/direction correlate with
forward returns at the same horizons already used in
open-return-persistence.md?

REUSES the OPEN_HOUR/OPEN_MINUTE convention from detect_ib_breakout.py
(8:30 AM ET) for "today's open" -- not redefined here.

HOW TO RUN:
    python3 src/study_overnight_gap.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_ib_breakout import OPEN_HOUR, OPEN_MINUTE

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

GAP_REFERENCE_HOUR, GAP_REFERENCE_MINUTE = 16, 0   # 4:00 PM ET -- standard "cash close" convention, see study doc #1
GAP_FILL_WATCH_END_HOUR, GAP_FILL_WATCH_END_MINUTE = 12, 0   # noon ET, matches this project's other morning windows
HORIZON_MINUTES = [30, 60, 90, 120, 180]  # measured from today's 8:30 AM open, same horizons as open-return-persistence.md
N_BOOTSTRAP = 2000
RANDOM_SEED = 42


def get_reference_close(day_df: pd.DataFrame, day, tz) -> float | None:
    """The last available bar's Close at or before 4:00 PM ET on `day`,
    or None if `day_df` has no bars at/before that time."""
    ref_ts = pd.Timestamp(day, tz=tz).replace(hour=GAP_REFERENCE_HOUR, minute=GAP_REFERENCE_MINUTE)
    bars_before_ref = day_df[day_df.index <= ref_ts]
    if bars_before_ref.empty:
        return None
    return float(bars_before_ref.iloc[-1]["Close"])


def compute_day_gap_and_returns(prior_day_df: pd.DataFrame, day_df: pd.DataFrame,
                                 day, prior_day) -> dict | None:
    """For one (prior_day, day) pair, returns a dict with the gap and its
    forward returns/fill status, or None if either reference point is
    missing (not enough data to compute a gap for this day at all)."""
    tz = day_df.index.tz
    prior_close = get_reference_close(prior_day_df, prior_day, tz)
    if prior_close is None:
        return None

    open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
    open_bars = day_df[day_df.index >= open_ts]
    if open_bars.empty:
        return None
    today_open = float(open_bars.iloc[0]["Open"])

    gap = today_open - prior_close

    row = {"date": day, "prior_close": prior_close, "today_open": today_open, "gap": gap}

    # --- Step 1: gap-fill by noon ---
    if gap == 0:
        row["gap_filled_by_noon"] = None  # no gap to fill
    else:
        fill_end_ts = pd.Timestamp(day, tz=tz).replace(
            hour=GAP_FILL_WATCH_END_HOUR, minute=GAP_FILL_WATCH_END_MINUTE
        )
        watch_bars = day_df[(day_df.index >= open_ts) & (day_df.index < fill_end_ts)]
        if watch_bars.empty:
            row["gap_filled_by_noon"] = None
        elif gap > 0:
            row["gap_filled_by_noon"] = bool((watch_bars["Low"] <= prior_close).any())
        else:
            row["gap_filled_by_noon"] = bool((watch_bars["High"] >= prior_close).any())

    # --- Step 2: forward returns at fixed horizons from today_open ---
    day_last_ts = day_df.index.max()
    bar_duration = pd.Timedelta(minutes=1)
    for h in HORIZON_MINUTES:
        horizon_end_ts = open_ts + pd.Timedelta(minutes=h)
        if day_last_ts < horizon_end_ts - bar_duration:
            row[f"fwd_return_{h}m"] = None
            continue
        window = day_df[(day_df.index >= open_ts) & (day_df.index < horizon_end_ts)]
        row[f"fwd_return_{h}m"] = (window.iloc[-1]["Close"] - today_open) if not window.empty else None

    return row


def scan_all_days(df: pd.DataFrame) -> pd.DataFrame:
    """Walks every (prior_day, day) consecutive pair in df and returns a
    DataFrame, one row per day that had a usable gap."""
    all_days = sorted(set(df.index.date))
    rows = []
    for i in range(1, len(all_days)):
        prior_day, day = all_days[i - 1], all_days[i]
        prior_day_df = df[df.index.date == prior_day]
        day_df = df[df.index.date == day]
        row = compute_day_gap_and_returns(prior_day_df, day_df, day, prior_day)
        if row is not None:
            rows.append(row)
    return pd.DataFrame(rows)


def bootstrap_correlation_ci(x, y, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    n = len(x)
    corrs = np.empty(n_bootstrap)
    idx_pool = np.arange(n)
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=n, replace=True)
        corrs[i] = np.corrcoef(x[idx], y[idx])[0, 1]
    return float(np.percentile(corrs, 5)), float(np.percentile(corrs, 95))


def bootstrap_proportion_ci(successes: int, n: int, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    """90% bootstrap CI on a fill rate, resampling the binary outcomes."""
    rng = np.random.default_rng(seed)
    data = np.array([1] * successes + [0] * (n - successes))
    props = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        sample = rng.choice(data, size=n, replace=True)
        props[i] = sample.mean()
    return float(np.percentile(props, 5)), float(np.percentile(props, 95))


def analyze_gap_fill(gaps_df: pd.DataFrame) -> dict:
    result = {}
    for label, mask in [("gap_up", gaps_df["gap"] > 0), ("gap_down", gaps_df["gap"] < 0)]:
        sub = gaps_df[mask].dropna(subset=["gap_filled_by_noon"])
        n = len(sub)
        filled = int(sub["gap_filled_by_noon"].sum())
        rate = filled / n if n else float("nan")
        ci_low, ci_high = bootstrap_proportion_ci(filled, n) if n >= 2 else (float("nan"), float("nan"))
        result[label] = {"n": n, "filled": filled, "fill_rate": rate, "fill_rate_90ci": (ci_low, ci_high)}
    return result


def analyze_horizon(gaps_df: pd.DataFrame, horizon: int) -> dict:
    col = f"fwd_return_{horizon}m"
    valid = gaps_df.dropna(subset=[col])
    x = valid["gap"].to_numpy()
    y = valid[col].to_numpy()
    n = len(valid)
    corr = float(np.corrcoef(x, y)[0, 1]) if n >= 2 else float("nan")
    ci_low, ci_high = bootstrap_correlation_ci(x, y) if n >= 2 else (float("nan"), float("nan"))
    significant = (ci_low > 0) or (ci_high < 0) if n >= 2 else False
    return {"horizon_minutes": horizon, "n": n, "correlation": corr,
            "correlation_90ci": (ci_low, ci_high), "significant": significant}


def main():
    full_df, is_synthetic = load_price_data(context="study_overnight_gap.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    gaps_df = scan_all_days(discovery_df)
    out_path = DATA_DIR / "study_overnight_gap_discovery.csv"
    gaps_df.to_csv(out_path, index=False)
    print(f"\nComputed gaps for {len(gaps_df)} Discovery day(s). Saved to {out_path}.\n")

    print("=" * 78)
    print("OVERNIGHT GAP BEHAVIOR STUDY -- Discovery slice")
    print("=" * 78)

    print("\n--- Step 1: gap-fill rate by noon ---")
    fill = analyze_gap_fill(gaps_df)
    for label, r in fill.items():
        print(f"  {label}: n={r['n']}  filled={r['filled']}  rate={r['fill_rate']:.1%}  "
              f"90% CI=[{r['fill_rate_90ci'][0]:.1%}, {r['fill_rate_90ci'][1]:.1%}]")

    print("\n--- Step 2: correlation(gap, forward_return) at each horizon ---")
    for h in HORIZON_MINUTES:
        r = analyze_horizon(gaps_df, h)
        print(f"  +{h:3d} min: n={r['n']:4d}  correlation={r['correlation']:+.4f}  "
              f"90% CI=[{r['correlation_90ci'][0]:+.4f}, {r['correlation_90ci'][1]:+.4f}]  "
              f"{'SIGNIFICANT' if r['significant'] else 'not significant'}")
    print("\n" + "=" * 78)


if __name__ == "__main__":
    main()
