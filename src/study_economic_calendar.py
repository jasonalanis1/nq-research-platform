"""
study_economic_calendar.py
==============================

Implements "Scheduled Macro-Release Volatility (CPI/NFP)" frozen in
`research/studies/economic-release-volatility.md`. Fifth mechanism
family tested in this project (scheduled information), and the first
whose grouping variable comes from an external, non-derivable
reference calendar rather than something computed from price data or a
fixed rule (unlike futures expiration, which
`study_futures_expiration.py` computes algorithmically).

CHARACTERIZATION STUDY testing MAGNITUDE (announcement-volatility
clustering), not direction -- no trades, no ledger entry unless the
Step 2 gate (all five conditions) is satisfied, and even then a
positive result would point toward a volatility-capture structure, not
a simple long/short rule. See the study doc's "What this is NOT" and
Honesty flags.

ONE primary test: does the mean ABSOLUTE 30-minute post-8:30 return
differ between CPI/NFP release days (pooled) and normal days? Four
secondary horizons, and CPI-only/NFP-only breakdowns, are reported
descriptively only -- never used to judge the study.

HOW TO RUN:
    python3 src/study_economic_calendar.py
"""

import json
from datetime import date
from pathlib import Path

import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified
from study_volatility_regime import compute_forward_return  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

PRIMARY_HORIZON_MINUTES = 30      # frozen -- structural (Initial Balance window), matches study_volatility_regime.py
SECONDARY_HORIZON_MINUTES = [60, 90, 120, 180]  # descriptive only, never used to judge the study
N_BOOTSTRAP = 2000
RANDOM_SEED = 11
ECONOMIC_THRESHOLD_POINTS = 2 * ROUND_TRIP_COST_POINTS  # frozen Step-2-gate #2, same bar as every prior study

# Frozen, sourced reference calendar -- compiled from bls.gov's own
# year-by-year "Schedule of Releases" archive pages
# (bls.gov/schedule/{year}/home.htm), cross-validated against each
# date's published day-of-week. Release time confirmed 8:30 AM ET for
# both series via bls.gov/schedule/news_release/cpi.htm and
# .../empsit.htm. See research/studies/economic-release-volatility.md
# item 1 for the full provenance. Verified zero same-day overlap
# between the two lists (asserted below, not just claimed).
#
# Compiled in two phases: the original 2015-2021 dates (Discovery
# window) drafted alongside the frozen spec, and a 2021-2023 extension
# (Validation window) added 2026-09-02 when the first Validation-slice
# out-of-sample check on exp-039 found zero release days classified --
# the original list simply hadn't been extended past Discovery's end.
# Same sourcing and verification discipline applied to both phases;
# see docs/ROADMAP.md's 2026-09-02 Validation-check entry for the full
# account of why the extension was needed.
CPI_DATES = [
    date(2015, 1, 16), date(2015, 2, 26), date(2015, 3, 24), date(2015, 4, 17),
    date(2015, 5, 22), date(2015, 6, 18), date(2015, 7, 17), date(2015, 8, 19),
    date(2015, 9, 16), date(2015, 10, 15), date(2015, 11, 17), date(2015, 12, 15),
    date(2016, 1, 20), date(2016, 2, 19), date(2016, 3, 16), date(2016, 4, 14),
    date(2016, 5, 17), date(2016, 6, 16), date(2016, 7, 15), date(2016, 8, 16),
    date(2016, 9, 16), date(2016, 10, 18), date(2016, 11, 17), date(2016, 12, 15),
    date(2017, 1, 18), date(2017, 2, 15), date(2017, 3, 15), date(2017, 4, 14),
    date(2017, 5, 12), date(2017, 6, 14), date(2017, 7, 14), date(2017, 8, 11),
    date(2017, 9, 14), date(2017, 10, 13), date(2017, 11, 15), date(2017, 12, 13),
    date(2018, 1, 12), date(2018, 2, 14), date(2018, 3, 13), date(2018, 4, 11),
    date(2018, 5, 10), date(2018, 6, 12), date(2018, 7, 12), date(2018, 8, 10),
    date(2018, 9, 13), date(2018, 10, 11), date(2018, 11, 14), date(2018, 12, 12),
    date(2019, 1, 11), date(2019, 2, 13), date(2019, 3, 12), date(2019, 4, 10),
    date(2019, 5, 10), date(2019, 6, 12), date(2019, 7, 11), date(2019, 8, 13),
    date(2019, 9, 12), date(2019, 10, 10), date(2019, 11, 13), date(2019, 12, 11),
    date(2020, 1, 14), date(2020, 2, 13), date(2020, 3, 11), date(2020, 4, 10),
    date(2020, 5, 12), date(2020, 6, 10), date(2020, 7, 14), date(2020, 8, 12),
    date(2020, 9, 11), date(2020, 10, 13), date(2020, 11, 12), date(2020, 12, 10),
    date(2021, 1, 13), date(2021, 2, 10), date(2021, 3, 10), date(2021, 4, 13),
    date(2021, 5, 12), date(2021, 6, 10), date(2021, 7, 13), date(2021, 8, 11),
    date(2021, 9, 14),

    # Extension for the Validation slice (2021-10-04 -> 2024-01-03),
    # compiled 2026-09-02 -- same bls.gov sourcing and verification
    # discipline as the dates above.
    date(2021, 10, 13), date(2021, 11, 10), date(2021, 12, 10),
    date(2022, 1, 12), date(2022, 2, 10), date(2022, 3, 10),
    date(2022, 4, 12), date(2022, 5, 11), date(2022, 6, 10),
    date(2022, 7, 13), date(2022, 8, 10), date(2022, 9, 13),
    date(2022, 10, 13), date(2022, 11, 10), date(2022, 12, 13),
    date(2023, 1, 12), date(2023, 2, 14), date(2023, 3, 14),
    date(2023, 4, 12), date(2023, 5, 10), date(2023, 6, 13),
    date(2023, 7, 12), date(2023, 8, 10), date(2023, 9, 13),
    date(2023, 10, 12), date(2023, 11, 14), date(2023, 12, 12),
]

NFP_DATES = [
    date(2015, 1, 9), date(2015, 2, 6), date(2015, 3, 6), date(2015, 4, 3),
    date(2015, 5, 8), date(2015, 6, 5), date(2015, 7, 2), date(2015, 8, 7),
    date(2015, 9, 4), date(2015, 10, 2), date(2015, 11, 6), date(2015, 12, 4),
    date(2016, 1, 8), date(2016, 2, 5), date(2016, 3, 4), date(2016, 4, 1),
    date(2016, 5, 6), date(2016, 6, 3), date(2016, 7, 8), date(2016, 8, 5),
    date(2016, 9, 2), date(2016, 10, 7), date(2016, 11, 4), date(2016, 12, 2),
    date(2017, 1, 6), date(2017, 2, 3), date(2017, 3, 10), date(2017, 4, 7),
    date(2017, 5, 5), date(2017, 6, 2), date(2017, 7, 7), date(2017, 8, 4),
    date(2017, 9, 1), date(2017, 10, 6), date(2017, 11, 3), date(2017, 12, 8),
    date(2018, 1, 5), date(2018, 2, 2), date(2018, 3, 9), date(2018, 4, 6),
    date(2018, 5, 4), date(2018, 6, 1), date(2018, 7, 6), date(2018, 8, 3),
    date(2018, 9, 7), date(2018, 10, 5), date(2018, 11, 2), date(2018, 12, 7),
    date(2019, 1, 4), date(2019, 2, 1), date(2019, 3, 8), date(2019, 4, 5),
    date(2019, 5, 3), date(2019, 6, 7), date(2019, 7, 5), date(2019, 8, 2),
    date(2019, 9, 6), date(2019, 10, 4), date(2019, 11, 1), date(2019, 12, 6),
    date(2020, 1, 10), date(2020, 2, 7), date(2020, 3, 6), date(2020, 4, 3),
    date(2020, 5, 8), date(2020, 6, 5), date(2020, 7, 2), date(2020, 8, 7),
    date(2020, 9, 4), date(2020, 10, 2), date(2020, 11, 6), date(2020, 12, 4),
    date(2021, 1, 8), date(2021, 2, 5), date(2021, 3, 5), date(2021, 4, 2),
    date(2021, 5, 7), date(2021, 6, 4), date(2021, 7, 2), date(2021, 8, 6),
    date(2021, 9, 3),

    # Extension for the Validation slice, same provenance as the CPI
    # extension above.
    date(2021, 10, 8), date(2021, 11, 5), date(2021, 12, 3),
    date(2022, 1, 7), date(2022, 2, 4), date(2022, 3, 4),
    date(2022, 4, 1), date(2022, 5, 6), date(2022, 6, 3),
    date(2022, 7, 8), date(2022, 8, 5), date(2022, 9, 2),
    date(2022, 10, 7), date(2022, 11, 4), date(2022, 12, 2),
    date(2023, 1, 6), date(2023, 2, 3), date(2023, 3, 10),
    date(2023, 4, 7), date(2023, 5, 5), date(2023, 6, 2),
    date(2023, 7, 7), date(2023, 8, 4), date(2023, 9, 1),
    date(2023, 10, 6), date(2023, 11, 3), date(2023, 12, 8),
]

assert len(CPI_DATES) == 108, f"expected 108 CPI dates, got {len(CPI_DATES)}"
assert len(NFP_DATES) == 108, f"expected 108 NFP dates, got {len(NFP_DATES)}"
assert set(CPI_DATES).isdisjoint(NFP_DATES), "CPI and NFP dates must not overlap (frozen spec item 1)"

CPI_SET = set(CPI_DATES)
NFP_SET = set(NFP_DATES)


def classify_day(day) -> str:
    """day -> 'cpi', 'nfp', or 'normal'. CPI and NFP never overlap
    (asserted above), so this is unambiguous."""
    if day in CPI_SET:
        return "cpi"
    if day in NFP_SET:
        return "nfp"
    return "normal"


def scan_all_days(df: pd.DataFrame) -> pd.DataFrame:
    """One row per Discovery day: its release classification and its
    ABSOLUTE forward return at every horizon, reusing
    study_volatility_regime.compute_forward_return() unmodified."""
    day_groups = {day: sub for day, sub in df.groupby(df.index.date)}
    horizons = [PRIMARY_HORIZON_MINUTES] + SECONDARY_HORIZON_MINUTES
    rows = []
    for day in sorted(day_groups.keys()):
        day_df = day_groups[day]
        row = {"date": day, "release_type": classify_day(day)}
        for h in horizons:
            ret = compute_forward_return(day_df, day, h)
            row[f"abs_return_{h}m"] = abs(ret) if ret is not None else None
        rows.append(row)
    return pd.DataFrame(rows)


def analyze_horizon(df: pd.DataFrame, horizon_minutes: int, release_types) -> dict:
    """Release-day (restricted to `release_types`, e.g. {"cpi","nfp"}
    for the pooled primary test, or {"cpi"} alone for the descriptive
    breakdown) vs normal-day comparison of mean ABSOLUTE return for one
    horizon column."""
    col = f"abs_return_{horizon_minutes}m"
    sub = df.dropna(subset=[col])
    release = sub[sub["release_type"].isin(release_types)][col]
    normal = sub[sub["release_type"] == "normal"][col]

    diff_low, diff_high = bootstrap_mean_diff_ci(release, normal, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED)
    significant = (diff_low > 0) or (diff_high < 0)
    mean_diff = float(release.mean() - normal.mean())

    return {
        "horizon_minutes": horizon_minutes,
        "n_release": int(len(release)),
        "n_normal": int(len(normal)),
        "mean_abs_return_release": float(release.mean()),
        "mean_abs_return_normal": float(normal.mean()),
        "mean_diff_points": mean_diff,
        "mean_diff_dollars": mean_diff * 20.0,  # CONTRACT_MULTIPLIER, matches backtest.py
        "ci_90": (diff_low, diff_high),
        "significant": bool(significant),
        "economically_meaningful": bool(mean_diff >= ECONOMIC_THRESHOLD_POINTS),
    }


def robustness_drop_largest_abs_return_day(df: pd.DataFrame) -> dict:
    """Step-2-gate check 4(a): primary-horizon comparison with the
    single largest-|return| day removed entirely (already absolute
    value, so the max IS the largest magnitude)."""
    col = f"abs_return_{PRIMARY_HORIZON_MINUTES}m"
    sub = df.dropna(subset=[col]).copy()
    if sub.empty:
        return {}
    idx_to_drop = sub[col].idxmax()
    dropped_date = sub.loc[idx_to_drop, "date"]
    reduced = sub.drop(index=idx_to_drop)
    result = analyze_horizon(reduced, PRIMARY_HORIZON_MINUTES, {"cpi", "nfp"})
    result["dropped_date"] = str(dropped_date)
    return result


def robustness_split_half(df: pd.DataFrame) -> dict:
    """Step-2-gate check 4(b): first-half vs second-half chronological
    stability of the primary-horizon comparison."""
    col = f"abs_return_{PRIMARY_HORIZON_MINUTES}m"
    sub = df.dropna(subset=[col]).sort_values("date").reset_index(drop=True)
    midpoint = len(sub) // 2
    first_half = sub.iloc[:midpoint]
    second_half = sub.iloc[midpoint:]
    return {
        "first_half": analyze_horizon(first_half, PRIMARY_HORIZON_MINUTES, {"cpi", "nfp"}),
        "second_half": analyze_horizon(second_half, PRIMARY_HORIZON_MINUTES, {"cpi", "nfp"}),
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_economic_calendar.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    results_df = scan_all_days(discovery_df)
    out_path = DATA_DIR / "study_economic_calendar_discovery.csv"
    results_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("SCHEDULED MACRO-RELEASE VOLATILITY STUDY (CPI/NFP) -- Discovery slice")
    print("=" * 78)
    counts = results_df["release_type"].value_counts()
    print(f"\nDay counts: {counts.to_dict()}")

    print(f"\n--- PRIMARY: {PRIMARY_HORIZON_MINUTES}-minute |post-8:30 return|, release (CPI+NFP) vs normal ---")
    primary = analyze_horizon(results_df, PRIMARY_HORIZON_MINUTES, {"cpi", "nfp"})
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['significant']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= {ECONOMIC_THRESHOLD_POINTS:.3f} pts): "
          f"{primary['economically_meaningful']}")

    print("\n--- Robustness (a): drop single largest-|return| day ---")
    drop_result = robustness_drop_largest_abs_return_day(results_df)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(results_df)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n--- Descriptive breakdown: CPI-only vs NFP-only (never used to judge the study) ---")
    cpi_only = analyze_horizon(results_df, PRIMARY_HORIZON_MINUTES, {"cpi"})
    nfp_only = analyze_horizon(results_df, PRIMARY_HORIZON_MINUTES, {"nfp"})
    print("  CPI-only:", cpi_only)
    print("  NFP-only:", nfp_only)

    print("\n--- SECONDARY horizons (descriptive only) ---")
    secondary = {}
    for h in SECONDARY_HORIZON_MINUTES:
        r = analyze_horizon(results_df, h, {"cpi", "nfp"})
        secondary[h] = r
        print(f"  {h}min: mean_diff={r['mean_diff_points']:+.3f}pts  "
              f"90% CI=[{r['ci_90'][0]:+.3f}, {r['ci_90'][1]:+.3f}]  "
              f"{'SIGNIFICANT' if r['significant'] else 'not significant'}")

    print("\n" + "=" * 78)

    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "descriptive_cpi_only": cpi_only,
        "descriptive_nfp_only": nfp_only,
        "secondary": secondary,
    }
    json_path = DATA_DIR / "study_economic_calendar_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
