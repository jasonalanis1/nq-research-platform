"""
study_post_release_continuation.py
=====================================

Implements "Post-Release Directional Continuation" frozen in
`research/studies/post-release-directional-continuation.md`.
Hypothesis #17, third test in the scheduled-information family (after
exp-039 CPI/NFP and exp-040 FOMC, both magnitude-only positives). This
is the family's first test of DIRECTION rather than magnitude.

CHARACTERIZATION STUDY: does NQ's initial 30-minute post-release move
tend to CONTINUE (same sign) or REVERSE over the following 150 minutes
(the 30-to-180-minute mark), on CPI/NFP/FOMC release days? Unlike
exp-039/040, a positive result here IS a specifiable mechanical rule
by construction (Step-2-gate condition 5) -- not a disclosed
limitation. Still a characterization study, not a cost-inclusive,
promotion-bar-tested strategy: see the frozen spec's "What this is
NOT".

NO NEW CALENDAR DATA, NO NEW DETECTION MACHINERY: reuses
CPI_DATES/NFP_DATES/classify_day() from study_economic_calendar.py,
FOMC_PRIMARY_DATES/FOMC_CPI_OVERLAP_DATES/classify_day()/
compute_forward_return_at() from study_fomc_volatility.py, and
bootstrap_mean_ci()/bootstrap_mean_diff_ci() from
study_nq_trend_following.py / study_futures_expiration.py -- all
imported and reused unmodified.

HOW TO RUN:
    python3 src/study_post_release_continuation.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from study_economic_calendar import CPI_SET, NFP_SET
from study_economic_calendar import classify_day as classify_cpi_nfp_day
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified
from study_fomc_volatility import (
    FOMC_ANCHOR_HOUR,
    FOMC_ANCHOR_MINUTE,
    FOMC_PRIMARY_DATES,
    compute_forward_return_at,
)
from study_fomc_volatility import classify_day as classify_fomc_day
from study_nq_trend_following import bootstrap_mean_ci  # reused unmodified
from study_volatility_regime import OPEN_HOUR, OPEN_MINUTE  # 8:30 AM ET, reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

INITIAL_HORIZON_MINUTES = 30    # frozen -- same primary horizon as exp-039/040
TOTAL_HORIZON_MINUTES = 180     # frozen -- same outer secondary horizon as exp-039/040
N_BOOTSTRAP = 2000
RANDOM_SEED = 11
ECONOMIC_THRESHOLD_POINTS = 2 * ROUND_TRIP_COST_POINTS  # frozen Step-2-gate #2, same bar as every prior study

# Runtime-asserted rather than assumed from construction alone, per the
# Advisor's review of the frozen spec draft. FOMC_PRIMARY_DATES is
# disjoint from CPI_SET/NFP_SET by construction (FOMC_CPI_OVERLAP_DATES
# is defined as exactly FOMC_SET & CPI_SET, so subtracting it removes
# 100% of that intersection; FOMC_NFP_OVERLAP_DATES == 0 is already
# asserted in study_fomc_volatility.py) -- these assertions verify that
# construction argument actually holds at import time.
assert CPI_SET.isdisjoint(FOMC_PRIMARY_DATES), "CPI_SET must not overlap FOMC_PRIMARY_DATES"
assert NFP_SET.isdisjoint(FOMC_PRIMARY_DATES), "NFP_SET must not overlap FOMC_PRIMARY_DATES"
assert CPI_SET.isdisjoint(NFP_SET), "CPI_SET must not overlap NFP_SET (re-checked here too)"


def scan_all_days(df: pd.DataFrame) -> pd.DataFrame:
    """One row per Discovery day. Two independent passes, each reusing
    its own source module's classify_day() unmodified:

    - CPI/NFP pass (8:30 AM anchor): every day classify_cpi_nfp_day()
      returns 'cpi' or 'nfp' for. Includes the 6 FOMC/CPI overlap days
      as ordinary 'cpi' days -- their 8:30-11:30 AM window closes well
      before that same day's 2:00 PM FOMC announcement, so it is not
      contaminated by it.
    - FOMC pass (2:00 PM anchor): every day classify_fomc_day() returns
      'fomc' for -- i.e. FOMC_PRIMARY_DATES, which already excludes
      those same 6 overlap days from this pass (attribution to FOMC
      alone would be ambiguous there, exactly exp-040's reasoning).

    Each release day therefore contributes exactly one row: never zero,
    never two. A "true normal" day (ordinary in BOTH passes -- not CPI,
    not NFP, not FOMC-primary, and not a CPI/FOMC overlap day either)
    gets a row at BOTH anchor times, so the normal-day baseline
    comparison (item 6 of the frozen spec) can use whichever anchor
    matches the release type it's being compared against. A release day
    does NOT also contribute a "normal" row at its other anchor --
    e.g. a CPI day's afternoon is not treated as an ordinary FOMC-anchor
    baseline observation, since the morning's CPI release could still be
    working through the market. This keeps the baseline pool free of
    any day carrying a scheduled release of its own, at either anchor.
    """
    day_groups = {day: sub for day, sub in df.groupby(df.index.date)}
    rows = []
    for day in sorted(day_groups.keys()):
        day_df = day_groups[day]

        cpi_nfp_type = classify_cpi_nfp_day(day)  # 'cpi' / 'nfp' / 'normal'
        fomc_type = classify_fomc_day(day)        # 'fomc' / 'fomc_cpi_overlap_excluded' / 'normal'
        is_true_normal_day = (cpi_nfp_type == "normal") and (fomc_type == "normal")

        # 8:30 AM anchor row -- included for 'cpi', 'nfp', and true
        # normal days only (never for an FOMC day's own ordinary
        # morning, which is excluded from the baseline pool by design).
        if cpi_nfp_type in ("cpi", "nfp") or is_true_normal_day:
            initial_830 = compute_forward_return_at(day_df, day, OPEN_HOUR, OPEN_MINUTE, INITIAL_HORIZON_MINUTES)
            total_830 = compute_forward_return_at(day_df, day, OPEN_HOUR, OPEN_MINUTE, TOTAL_HORIZON_MINUTES)
            rows.append({
                "date": day,
                "anchor": "0830",
                "release_type": cpi_nfp_type,
                "initial_return": initial_830,
                "total_return": total_830,
            })

        # 2:00 PM anchor row -- included for 'fomc' and true normal days
        # only. The 6 overlap days are 'fomc_cpi_overlap_excluded' here
        # (not a true normal day, since cpi_nfp_type=='cpi' for them),
        # so they produce no 2:00 PM row, same as before.
        if fomc_type == "fomc" or is_true_normal_day:
            initial_1400 = compute_forward_return_at(day_df, day, FOMC_ANCHOR_HOUR, FOMC_ANCHOR_MINUTE, INITIAL_HORIZON_MINUTES)
            total_1400 = compute_forward_return_at(day_df, day, FOMC_ANCHOR_HOUR, FOMC_ANCHOR_MINUTE, TOTAL_HORIZON_MINUTES)
            rows.append({
                "date": day,
                "anchor": "1400",
                "release_type": fomc_type,
                "initial_return": initial_1400,
                "total_return": total_1400,
            })

    return pd.DataFrame(rows)


def compute_directional_continuation(df: pd.DataFrame) -> pd.DataFrame:
    """Adds continuation_return and directional_continuation columns.
    Drops rows with missing initial/total return (insufficient data)
    or an exactly-zero initial_return (no direction to test
    continuation of) -- both counts reported by the caller, never
    silently absorbed."""
    sub = df.dropna(subset=["initial_return", "total_return"]).copy()
    n_missing_data = len(df) - len(sub)

    n_before_zero_filter = len(sub)
    sub = sub[sub["initial_return"] != 0.0].copy()
    n_zero_initial = n_before_zero_filter - len(sub)

    sub["continuation_return"] = sub["total_return"] - sub["initial_return"]
    sub["directional_continuation"] = sub["continuation_return"] * np.sign(sub["initial_return"])

    return sub, {"n_missing_data": n_missing_data, "n_zero_initial_excluded": n_zero_initial}


def one_sample_test(values) -> dict:
    """Step-2-gate condition 1 check for a pooled or per-type sample:
    90% one-sample bootstrap CI on the mean of `values`, via
    study_nq_trend_following.bootstrap_mean_ci(), reused unmodified."""
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": (float("nan"), float("nan")), "significant": False,
                "economically_meaningful": False}
    mean_val = float(arr.mean())
    ci_low, ci_high = bootstrap_mean_ci(arr, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED)
    significant = ci_low > 0
    return {
        "n": n,
        "mean": mean_val,
        "mean_dollars": mean_val * 20.0,  # CONTRACT_MULTIPLIER, matches backtest.py
        "ci_90": (ci_low, ci_high),
        "significant": bool(significant),
        "economically_meaningful": bool(mean_val >= ECONOMIC_THRESHOLD_POINTS),
    }


def robustness_drop_largest(sub: pd.DataFrame, release_mask) -> dict:
    """Step-2-gate check 4(a): pooled primary test with the single
    largest-|directional_continuation| release-day row removed."""
    release_rows = sub[release_mask]
    if release_rows.empty:
        return {}
    idx_to_drop = release_rows["directional_continuation"].abs().idxmax()
    dropped_date = sub.loc[idx_to_drop, "date"]
    dropped_anchor = sub.loc[idx_to_drop, "anchor"]
    reduced = release_rows.drop(index=idx_to_drop)
    result = one_sample_test(reduced["directional_continuation"])
    result["dropped_date"] = str(dropped_date)
    result["dropped_anchor"] = str(dropped_anchor)
    return result


def robustness_split_half(sub: pd.DataFrame, release_mask) -> dict:
    """Step-2-gate check 4(b): first-half vs second-half chronological
    split of the pooled release-day sample."""
    release_rows = sub[release_mask].sort_values("date").reset_index(drop=True)
    midpoint = len(release_rows) // 2
    first_half = release_rows.iloc[:midpoint]
    second_half = release_rows.iloc[midpoint:]
    return {
        "first_half": one_sample_test(first_half["directional_continuation"]),
        "second_half": one_sample_test(second_half["directional_continuation"]),
    }


def normal_day_baseline(sub: pd.DataFrame) -> dict:
    """Secondary/descriptive (item 6 of the frozen spec): the same
    directional_continuation statistic on normal days, at each matching
    anchor, plus the release-vs-normal diff via bootstrap_mean_diff_ci
    (reused unmodified). Never overrides the primary verdict."""
    out = {}
    for anchor, label in [("0830", "cpi_nfp_vs_normal_0830"), ("1400", "fomc_vs_normal_1400")]:
        anchor_rows = sub[sub["anchor"] == anchor]
        normal_vals = anchor_rows[anchor_rows["release_type"] == "normal"]["directional_continuation"]
        if anchor == "0830":
            release_vals = anchor_rows[anchor_rows["release_type"].isin(["cpi", "nfp"])]["directional_continuation"]
        else:
            release_vals = anchor_rows[anchor_rows["release_type"] == "fomc"]["directional_continuation"]
        normal_stat = one_sample_test(normal_vals)
        diff_low, diff_high = bootstrap_mean_diff_ci(release_vals, normal_vals, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED)
        out[label] = {
            "normal": normal_stat,
            "release_vs_normal_diff_ci_90": (diff_low, diff_high),
            "release_vs_normal_diff_significant": bool((diff_low > 0) or (diff_high < 0)),
        }
    return out


def main():
    full_df, is_synthetic = load_price_data(context="study_post_release_continuation.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    scanned = scan_all_days(discovery_df)
    sub, exclusion_counts = compute_directional_continuation(scanned)

    out_path = DATA_DIR / "study_post_release_continuation_discovery.csv"
    sub.to_csv(out_path, index=False)

    print("=" * 78)
    print("POST-RELEASE DIRECTIONAL CONTINUATION STUDY -- Discovery slice")
    print("=" * 78)
    print(f"\nExclusions: {exclusion_counts}")

    release_mask = sub["release_type"].isin(["cpi", "nfp", "fomc"])
    print(f"\nRelease-day row counts: {sub[release_mask]['release_type'].value_counts().to_dict()}")

    print(f"\n--- PRIMARY: pooled CPI+NFP+FOMC directional continuation "
          f"({INITIAL_HORIZON_MINUTES}min initial -> {TOTAL_HORIZON_MINUTES}min total) ---")
    primary = one_sample_test(sub[release_mask]["directional_continuation"])
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['significant']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= {ECONOMIC_THRESHOLD_POINTS:.3f} pts): "
          f"{primary['economically_meaningful']}")

    print("\n--- Robustness (a): drop single largest-|directional_continuation| release day ---")
    drop_result = robustness_drop_largest(sub, release_mask)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(sub, release_mask)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n--- Descriptive breakdown: cpi-only / nfp-only / fomc-only (never gates the study) ---")
    descriptive = {}
    for rtype in ("cpi", "nfp", "fomc"):
        r = one_sample_test(sub[sub["release_type"] == rtype]["directional_continuation"])
        descriptive[rtype] = r
        sign = "+" if r["mean"] >= 0 else "-"
        print(f"  {rtype}: n={r['n']} mean={r['mean']:+.3f}pts ({sign}) "
              f"90% CI=[{r['ci_90'][0]:+.3f}, {r['ci_90'][1]:+.3f}] "
              f"{'SIGNIFICANT' if r['significant'] else 'not significant'}")

    pooled_sign = 1 if primary["mean"] >= 0 else -1
    sign_disagreements = [rtype for rtype, r in descriptive.items()
                           if r["n"] > 0 and np.sign(r["mean"]) != 0 and np.sign(r["mean"]) != pooled_sign]
    if sign_disagreements:
        print(f"\n  ** SIGN DISAGREEMENT vs pooled result in subtype(s): {sign_disagreements} -- "
              f"per the frozen spec's condition-5 scoping caveat, the mechanical rule must be "
              f"narrowed to exclude these subtype(s), not stated as a blanket rule. **")
    else:
        print("\n  All three subtypes agree in sign with the pooled result -- condition 5's "
              "blanket 'on a confirmed CPI/NFP/FOMC release day' framing is supported.")

    print("\n--- Secondary/descriptive: normal-day baseline comparison ---")
    baseline = normal_day_baseline(sub)
    for label, r in baseline.items():
        print(f"  {label}: normal_mean={r['normal']['mean']:+.3f}pts  "
              f"release_vs_normal_diff_90%CI=[{r['release_vs_normal_diff_ci_90'][0]:+.3f}, "
              f"{r['release_vs_normal_diff_ci_90'][1]:+.3f}]  "
              f"{'SIGNIFICANT' if r['release_vs_normal_diff_significant'] else 'not significant'}")

    print("\n" + "=" * 78)

    out = {
        "exclusion_counts": exclusion_counts,
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "descriptive_by_type": descriptive,
        "sign_disagreements": sign_disagreements,
        "normal_day_baseline": baseline,
    }
    json_path = DATA_DIR / "study_post_release_continuation_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
