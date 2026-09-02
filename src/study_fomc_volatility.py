"""
study_fomc_volatility.py
=========================

Implements "Scheduled Macro-Release Volatility (FOMC)" frozen in
`research/studies/fomc-release-volatility.md`. Extends exp-039's
CPI/NFP scheduled-information family (the first result in this
project's history to replicate on Validation) to FOMC policy decisions,
the single most information-dense scheduled US macro event.

CHARACTERIZATION STUDY testing MAGNITUDE (announcement-volatility
clustering), not direction -- no trades, no ledger entry unless the
Step 2 gate (all five conditions) is satisfied, same convention as
exp-039.

ONE primary test: does the mean ABSOLUTE 30-minute post-2:00-PM-ET
return differ between FOMC decision days (excluding the 6 days that
also coincide with a CPI release -- see below) and normal days? Four
secondary horizons are reported descriptively only -- never used to
judge the study.

NEW MACHINERY (disclosed in the frozen spec, not hidden): every other
intraday study in this project anchors to the 8:30 AM ET session open
via study_volatility_regime.compute_forward_return(), which hardcodes
OPEN_HOUR/OPEN_MINUTE (8, 30). FOMC statements release at 2:00 PM ET,
so this module adds compute_forward_return_at() -- identical
window/edge-case logic, with the anchor hour/minute parameterized
instead of hardcoded.

HOW TO RUN:
    python3 src/study_fomc_volatility.py
"""

import json
from datetime import date
from pathlib import Path

import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from study_economic_calendar import CPI_DATES, NFP_DATES  # for the overlap check, reused unmodified
from study_futures_expiration import bootstrap_mean_diff_ci, make_is_expiration_week  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

PRIMARY_HORIZON_MINUTES = 30      # frozen -- structural (first 30 min post-release), matches exp-039's convention
SECONDARY_HORIZON_MINUTES = [60, 90, 120, 180]  # descriptive only, never used to judge the study
N_BOOTSTRAP = 2000
RANDOM_SEED = 11
ECONOMIC_THRESHOLD_POINTS = 2 * ROUND_TRIP_COST_POINTS  # frozen Step-2-gate #2, same bar as every prior study

FOMC_ANCHOR_HOUR = 14   # 2:00 PM ET
FOMC_ANCHOR_MINUTE = 0

# Frozen, sourced reference calendar of REGULARLY-SCHEDULED FOMC policy
# decision dates -- compiled from federalreserve.gov's own year-by-year
# historical meeting archive pages
# (federalreserve.gov/monetarypolicy/fomchistoricalYYYY.htm) and
# cross-checked against individual press-release pages
# (federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm).
# Seven emergency/inter-meeting/non-decision items in this window were
# identified and deliberately excluded (not just missed): the 2020-03-03
# and 2020-03-15 emergency inter-meeting rate cuts, three March 2020
# notation votes, the 2019-10-11 repo-operations statement, and the
# 2020-08-27 longer-run-goals strategy statement -- none was a
# regularly-scheduled decision on the pre-published calendar. See
# research/studies/fomc-release-volatility.md item 1 for full provenance.
FOMC_DATES = [
    date(2015, 1, 28), date(2015, 3, 18), date(2015, 4, 29), date(2015, 6, 17),
    date(2015, 7, 29), date(2015, 9, 17), date(2015, 10, 28), date(2015, 12, 16),
    date(2016, 1, 27), date(2016, 3, 16), date(2016, 4, 27), date(2016, 6, 15),
    date(2016, 7, 27), date(2016, 9, 21), date(2016, 11, 2), date(2016, 12, 14),
    date(2017, 2, 1), date(2017, 3, 15), date(2017, 5, 3), date(2017, 6, 14),
    date(2017, 7, 26), date(2017, 9, 20), date(2017, 11, 1), date(2017, 12, 13),
    date(2018, 1, 31), date(2018, 3, 21), date(2018, 5, 2), date(2018, 6, 13),
    date(2018, 8, 1), date(2018, 9, 26), date(2018, 11, 8), date(2018, 12, 19),
    date(2019, 1, 30), date(2019, 3, 20), date(2019, 5, 1), date(2019, 6, 19),
    date(2019, 7, 31), date(2019, 9, 18), date(2019, 10, 30), date(2019, 12, 11),
    date(2020, 1, 29), date(2020, 4, 29), date(2020, 6, 10), date(2020, 7, 29),
    date(2020, 9, 16), date(2020, 11, 5), date(2020, 12, 16),
    date(2021, 1, 27), date(2021, 3, 17), date(2021, 4, 28), date(2021, 6, 16),
    date(2021, 7, 28), date(2021, 9, 22),
]

assert len(FOMC_DATES) == 53, f"expected 53 FOMC dates, got {len(FOMC_DATES)}"
assert FOMC_DATES == sorted(set(FOMC_DATES)), "FOMC_DATES must be sorted and unique"

FOMC_SET = set(FOMC_DATES)

# Overlap check, run rather than assumed away (frozen spec item 1 /
# feasibility report Risk #2). FOMC/CPI same-day overlaps are excluded
# from the primary classification entirely -- two distinct scheduled
# releases on one day make attribution to FOMC alone ambiguous.
# FOMC/expiration-week overlap is disclosed, not excluded (see the
# frozen spec's Honesty flags for why).
FOMC_CPI_OVERLAP_DATES = frozenset(FOMC_SET & set(CPI_DATES))
FOMC_NFP_OVERLAP_DATES = frozenset(FOMC_SET & set(NFP_DATES))
assert len(FOMC_CPI_OVERLAP_DATES) == 6, f"expected 6 FOMC/CPI overlap dates, got {len(FOMC_CPI_OVERLAP_DATES)}"
assert len(FOMC_NFP_OVERLAP_DATES) == 0, f"expected 0 FOMC/NFP overlap dates, got {len(FOMC_NFP_OVERLAP_DATES)}"

FOMC_PRIMARY_DATES = frozenset(FOMC_SET - FOMC_CPI_OVERLAP_DATES)
assert len(FOMC_PRIMARY_DATES) == 47, f"expected 47 primary FOMC dates, got {len(FOMC_PRIMARY_DATES)}"


def classify_day(day) -> str:
    """day -> 'fomc', 'fomc_cpi_overlap_excluded', or 'normal'.
    Overlap-excluded days are neither 'fomc' nor 'normal' -- they are
    dropped from the primary/secondary comparisons entirely (see
    analyze_horizon), not silently folded into either bucket."""
    if day in FOMC_CPI_OVERLAP_DATES:
        return "fomc_cpi_overlap_excluded"
    if day in FOMC_SET:
        return "fomc"
    return "normal"


def compute_forward_return_at(day_df: pd.DataFrame, day, hour: int, minute: int, horizon_minutes: int):
    """Signed NQ-point return from today's own `hour:minute` ET Open to
    the last available Close within [anchor, anchor+horizon) -- a
    direct generalization of
    study_volatility_regime.compute_forward_return(), which hardcodes
    the anchor to 8:30 AM (OPEN_HOUR/OPEN_MINUTE). Identical window and
    edge-case logic; only the anchor time is now a parameter. This is
    the one genuinely new piece of machinery this study introduces --
    disclosed in the frozen spec, not a reuse-unmodified case like
    everything else in this module."""
    if day_df.empty:
        return None
    tz = day_df.index.tz
    anchor_ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
    anchor_bars = day_df[day_df.index >= anchor_ts]
    if anchor_bars.empty:
        return None
    anchor_open = float(anchor_bars.iloc[0]["Open"])

    horizon_end_ts = anchor_ts + pd.Timedelta(minutes=horizon_minutes)
    day_last_ts = day_df.index.max()
    bar_duration = pd.Timedelta(minutes=1)
    if day_last_ts < horizon_end_ts - bar_duration:
        return None
    window = day_df[(day_df.index >= anchor_ts) & (day_df.index < horizon_end_ts)]
    if window.empty:
        return None
    return float(window.iloc[-1]["Close"] - anchor_open)


def scan_all_days(df: pd.DataFrame) -> pd.DataFrame:
    """One row per Discovery day: its FOMC classification and its
    ABSOLUTE forward return at every horizon, anchored to 2:00 PM ET
    via compute_forward_return_at()."""
    day_groups = {day: sub for day, sub in df.groupby(df.index.date)}
    horizons = [PRIMARY_HORIZON_MINUTES] + SECONDARY_HORIZON_MINUTES
    rows = []
    for day in sorted(day_groups.keys()):
        day_df = day_groups[day]
        row = {"date": day, "release_type": classify_day(day)}
        for h in horizons:
            ret = compute_forward_return_at(day_df, day, FOMC_ANCHOR_HOUR, FOMC_ANCHOR_MINUTE, h)
            row[f"abs_return_{h}m"] = abs(ret) if ret is not None else None
        rows.append(row)
    return pd.DataFrame(rows)


def analyze_horizon(df: pd.DataFrame, horizon_minutes: int, release_types) -> dict:
    """FOMC (restricted to `release_types`, normally {"fomc"}) vs
    normal-day comparison of mean ABSOLUTE return for one horizon
    column. Rows classified 'fomc_cpi_overlap_excluded' are excluded
    from both sides automatically, since they match neither
    `release_types` nor "normal"."""
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
    single largest-|return| day removed entirely."""
    col = f"abs_return_{PRIMARY_HORIZON_MINUTES}m"
    sub = df.dropna(subset=[col]).copy()
    if sub.empty:
        return {}
    idx_to_drop = sub[col].idxmax()
    dropped_date = sub.loc[idx_to_drop, "date"]
    reduced = sub.drop(index=idx_to_drop)
    result = analyze_horizon(reduced, PRIMARY_HORIZON_MINUTES, {"fomc"})
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
        "first_half": analyze_horizon(first_half, PRIMARY_HORIZON_MINUTES, {"fomc"}),
        "second_half": analyze_horizon(second_half, PRIMARY_HORIZON_MINUTES, {"fomc"}),
    }


def expiration_week_overlap_report(df: pd.DataFrame) -> dict:
    """Disclosure-only (not a robustness check that changes the primary
    result): how many of the classified FOMC days also fall inside an
    expiration week, per exp-035's own classification. Reported since
    the frozen spec discloses this overlap rather than excluding it."""
    is_exp_week = make_is_expiration_week(2014, 2022)
    fomc_days = df[df["release_type"] == "fomc"]["date"]
    overlap = [d for d in fomc_days if is_exp_week(d)]
    return {
        "n_fomc_days": int(len(fomc_days)),
        "n_also_expiration_week": len(overlap),
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_fomc_volatility.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    results_df = scan_all_days(discovery_df)
    out_path = DATA_DIR / "study_fomc_volatility_discovery.csv"
    results_df.to_csv(out_path, index=False)

    print("=" * 78)
    print("SCHEDULED MACRO-RELEASE VOLATILITY STUDY (FOMC) -- Discovery slice")
    print("=" * 78)
    counts = results_df["release_type"].value_counts()
    print(f"\nDay counts: {counts.to_dict()}")

    print(f"\n--- PRIMARY: {PRIMARY_HORIZON_MINUTES}-minute |post-2:00-PM return|, FOMC vs normal ---")
    primary = analyze_horizon(results_df, PRIMARY_HORIZON_MINUTES, {"fomc"})
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

    print("\n--- Disclosure: expiration-week overlap (not excluded, not a robustness check) ---")
    exp_overlap = expiration_week_overlap_report(results_df)
    print(f"  {exp_overlap}")

    print("\n--- SECONDARY horizons (descriptive only) ---")
    secondary = {}
    for h in SECONDARY_HORIZON_MINUTES:
        r = analyze_horizon(results_df, h, {"fomc"})
        secondary[h] = r
        print(f"  {h}min: mean_diff={r['mean_diff_points']:+.3f}pts  "
              f"90% CI=[{r['ci_90'][0]:+.3f}, {r['ci_90'][1]:+.3f}]  "
              f"{'SIGNIFICANT' if r['significant'] else 'not significant'}")

    print("\n" + "=" * 78)

    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "expiration_week_overlap_disclosure": exp_overlap,
        "secondary": secondary,
    }
    json_path = DATA_DIR / "study_fomc_volatility_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
