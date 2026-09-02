"""
study_es_gap_incremental_info.py
====================================

Implements "ES Overnight Gap as Incremental Information Beyond NQ's Own
Overnight Gap" frozen in
`research/studies/es-overnight-gap-incremental-information.md` --
Mechanism 3 from the ES Cross-Market Feasibility Report
(`research/studies/es-cross-market-feasibility.md`). This is the
project's first two-instrument analysis.

CHARACTERIZATION STUDY, not a strategy. No trades, no ledger entry
unless the study doc's own Step 2 gate (all five conditions) is
satisfied.

ONE primary test: in a joint OLS regression of NQ's 90-minute post-8:30
forward return on both NQ's own overnight gap and ES's overnight gap,
does ES's gap coefficient (b2) carry incremental information -- i.e. is
its 90% bootstrap CI entirely on one side of zero, after NQ's own gap
(already found real in exp-032) is already in the model? Four secondary
horizons (30/60/120/180 min) are reported descriptively only, never
used to judge the study.

HOW TO RUN:
    python3 src/study_es_gap_incremental_info.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from detect_ib_breakout import OPEN_HOUR, OPEN_MINUTE
from study_overnight_gap import get_reference_close  # reused unmodified, applied to both instruments
from study_volatility_regime import compute_forward_return  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

PRIMARY_HORIZON_MINUTES = 90       # frozen -- anchored to exp-032's own established finding, not results-chosen here
SECONDARY_HORIZON_MINUTES = [30, 60, 120, 180]  # descriptive only, never used to judge the study
N_BOOTSTRAP = 2000
RANDOM_SEED = 11                   # matches study_volatility_regime.py's current-convention seed, not exp-032's older seed=42
ECONOMIC_THRESHOLD_POINTS = 2 * ROUND_TRIP_COST_POINTS  # frozen Step-2-gate #2, same bar as exp-036


def compute_instrument_day_data(df: pd.DataFrame) -> dict:
    """day -> {"ref_close", "open", "day_df"} for one instrument's data,
    reusing get_reference_close() and the OPEN_HOUR/OPEN_MINUTE 8:30 AM
    ET convention, both unmodified. `ref_close` and/or `open` are None
    when that day has no usable bar for the corresponding reference
    point."""
    day_groups = {day: sub for day, sub in df.groupby(df.index.date)}
    out = {}
    for day in sorted(day_groups.keys()):
        day_df = day_groups[day]
        tz = day_df.index.tz
        ref_close = get_reference_close(day_df, day, tz)
        open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
        open_bars = day_df[day_df.index >= open_ts]
        today_open = float(open_bars.iloc[0]["Open"]) if not open_bars.empty else None
        out[day] = {"ref_close": ref_close, "open": today_open, "day_df": day_df}
    return out


def compute_gap(instrument_days: dict, day, prior_day):
    """gap[day] = today_open - prior_day's ref_close for ONE instrument,
    or None if either reference point is missing -- identical
    convention to study_overnight_gap.py's gap, applied here to
    whichever instrument's per-day dict is passed in (NQ or ES)."""
    if prior_day not in instrument_days or day not in instrument_days:
        return None
    prior_close = instrument_days[prior_day]["ref_close"]
    today_open = instrument_days[day]["open"]
    if prior_close is None or today_open is None:
        return None
    return today_open - prior_close


def build_joint_dataset(nq_df: pd.DataFrame, es_df: pd.DataFrame) -> pd.DataFrame:
    """Inner-joins NQ and ES on trading day (frozen spec item 3): a day
    survives only if BOTH instruments have a valid reference close and
    8:30 open. For each surviving day, computes NQ_gap, ES_gap (against
    the immediately preceding day in this same joined, valid-on-both
    list -- the same "previous day available in the data" semantics
    study_overnight_gap.py already uses on a single instrument), and
    NQ's forward return at every horizon."""
    nq_days = compute_instrument_day_data(nq_df)
    es_days = compute_instrument_day_data(es_df)

    nq_valid_days = {d for d, v in nq_days.items() if v["ref_close"] is not None and v["open"] is not None}
    es_valid_days = {d for d, v in es_days.items() if v["ref_close"] is not None and v["open"] is not None}
    common_days = sorted(nq_valid_days & es_valid_days)

    rows = []
    horizons = [PRIMARY_HORIZON_MINUTES] + SECONDARY_HORIZON_MINUTES
    for i in range(1, len(common_days)):
        prior_day, day = common_days[i - 1], common_days[i]
        nq_gap = compute_gap(nq_days, day, prior_day)
        es_gap = compute_gap(es_days, day, prior_day)
        if nq_gap is None or es_gap is None:
            continue
        row = {"date": day, "nq_gap": nq_gap, "es_gap": es_gap}
        for h in horizons:
            row[f"nq_fwd_return_{h}m"] = compute_forward_return(nq_days[day]["day_df"], day, h)
        rows.append(row)
    return pd.DataFrame(rows)


def fit_regression(nq_gap, es_gap, y):
    """Point-estimate OLS fit of y = b0 + b1*nq_gap + b2*es_gap + e on
    the full (non-resampled) data. Returns (b0, b1, b2)."""
    nq_gap = np.asarray(nq_gap, dtype=float)
    es_gap = np.asarray(es_gap, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(y)
    X = np.column_stack([np.ones(n), nq_gap, es_gap])
    coefs, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(coefs[0]), float(coefs[1]), float(coefs[2])


def bootstrap_regression_coef_ci(nq_gap, es_gap, y, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    """90% bootstrap CI on b2, the ES_gap coefficient in the OLS model
    y = b0 + b1*nq_gap + b2*es_gap + e -- the frozen spec's primary
    test. Resamples (nq_gap, es_gap, y) triples JOINTLY, with
    replacement, using trading days as the resampling unit -- the same
    nonparametric resample-and-recompute convention as every other
    bootstrap in this project (study_futures_expiration.bootstrap_mean_diff_ci,
    study_overnight_gap.bootstrap_correlation_ci), generalized here to a
    regression coefficient rather than a mean difference or a
    correlation -- the smallest addition needed, not new statistical
    machinery."""
    rng = np.random.default_rng(seed)
    nq_gap = np.asarray(nq_gap, dtype=float)
    es_gap = np.asarray(es_gap, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(y)
    idx_pool = np.arange(n)
    b2_samples = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=n, replace=True)
        _, _, b2 = fit_regression(nq_gap[idx], es_gap[idx], y[idx])
        b2_samples[i] = b2
    return float(np.percentile(b2_samples, 5)), float(np.percentile(b2_samples, 95))


def analyze_horizon(df: pd.DataFrame, horizon_minutes: int) -> dict:
    """Full regression + bootstrap CI + Step-2-gate checks 1 and 2 for
    one horizon column."""
    col = f"nq_fwd_return_{horizon_minutes}m"
    sub = df.dropna(subset=[col, "nq_gap", "es_gap"])
    n = len(sub)

    b0, b1, b2 = fit_regression(sub["nq_gap"], sub["es_gap"], sub[col])
    ci_low, ci_high = bootstrap_regression_coef_ci(sub["nq_gap"], sub["es_gap"], sub[col])
    significant = (ci_low > 0) or (ci_high < 0)

    es_gap_iqr = float(np.percentile(sub["es_gap"], 75) - np.percentile(sub["es_gap"], 25))
    translated_effect_points = abs(b2 * es_gap_iqr)

    return {
        "horizon_minutes": horizon_minutes,
        "n": int(n),
        "b0_intercept": b0,
        "b1_nq_gap_coef": b1,
        "b2_es_gap_coef": b2,
        "b2_90ci": (ci_low, ci_high),
        "significant": bool(significant),
        "es_gap_iqr": es_gap_iqr,
        "translated_effect_points": translated_effect_points,
        "economically_meaningful": bool(translated_effect_points >= ECONOMIC_THRESHOLD_POINTS),
    }


def robustness_drop_largest_es_gap_day(df: pd.DataFrame) -> dict:
    """Step-2-gate check 4(a): primary-horizon regression with the
    single largest-|ES_gap| day removed entirely."""
    col = f"nq_fwd_return_{PRIMARY_HORIZON_MINUTES}m"
    sub = df.dropna(subset=[col, "nq_gap", "es_gap"]).copy()
    if sub.empty:
        return {}
    idx_to_drop = sub["es_gap"].abs().idxmax()
    dropped_date = sub.loc[idx_to_drop, "date"]
    reduced = sub.drop(index=idx_to_drop)
    result = analyze_horizon(reduced, PRIMARY_HORIZON_MINUTES)
    result["dropped_date"] = str(dropped_date)
    return result


def robustness_split_half(df: pd.DataFrame) -> dict:
    """Step-2-gate check 4(b): first-half vs second-half chronological
    stability of the primary-horizon regression."""
    col = f"nq_fwd_return_{PRIMARY_HORIZON_MINUTES}m"
    sub = df.dropna(subset=[col, "nq_gap", "es_gap"]).sort_values("date").reset_index(drop=True)
    midpoint = len(sub) // 2
    first_half = sub.iloc[:midpoint]
    second_half = sub.iloc[midpoint:]
    return {
        "first_half": analyze_horizon(first_half, PRIMARY_HORIZON_MINUTES),
        "second_half": analyze_horizon(second_half, PRIMARY_HORIZON_MINUTES),
    }


def main():
    nq_df, nq_is_synthetic = load_price_data(context="study_es_gap_incremental_info.py (NQ)", symbol="NQ")
    if nq_is_synthetic:
        print("ABORT: only synthetic NQ data is available -- this study requires real data.")
        return
    es_df, es_is_synthetic = load_price_data(context="study_es_gap_incremental_info.py (ES)", symbol="ES")
    if es_is_synthetic:
        print("ABORT: only synthetic ES data is available -- this study requires real data.")
        return

    nq_discovery = get_discovery_data(nq_df)
    es_discovery = get_discovery_data(es_df)

    joint_df = build_joint_dataset(nq_discovery, es_discovery)
    out_path = DATA_DIR / "study_es_gap_incremental_info_discovery.csv"
    joint_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("ES OVERNIGHT GAP INCREMENTAL-INFORMATION STUDY -- Discovery slice")
    print("=" * 78)
    print(f"\nJoint (NQ + ES) usable days: {len(joint_df)}")

    print(f"\n--- PRIMARY: {PRIMARY_HORIZON_MINUTES}-minute NQ forward return ~ NQ_gap + ES_gap ---")
    primary = analyze_horizon(joint_df, PRIMARY_HORIZON_MINUTES)
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible, b2 CI excludes zero): {primary['significant']}")
    print(f"  Step-2-gate check 2 (economically meaningful, translated effect >= "
          f"{ECONOMIC_THRESHOLD_POINTS:.3f} pts): {primary['economically_meaningful']}")

    print("\n--- Robustness 4(a): drop single largest-magnitude ES_gap day ---")
    drop_result = robustness_drop_largest_es_gap_day(joint_df)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness 4(b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(joint_df)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n--- SECONDARY horizons (descriptive only) ---")
    secondary = {}
    for h in SECONDARY_HORIZON_MINUTES:
        r = analyze_horizon(joint_df, h)
        secondary[h] = r
        print(f"  {h}min: b2={r['b2_es_gap_coef']:+.4f}  90% CI=[{r['b2_90ci'][0]:+.4f}, {r['b2_90ci'][1]:+.4f}]  "
              f"{'SIGNIFICANT' if r['significant'] else 'not significant'}")

    print("\n" + "=" * 78)

    out = {
        "primary": primary,
        "robustness_drop_largest_es_gap": drop_result,
        "robustness_split_half": split_result,
        "secondary": secondary,
    }
    json_path = DATA_DIR / "study_es_gap_incremental_info_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
