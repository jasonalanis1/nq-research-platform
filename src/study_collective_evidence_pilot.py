"""
study_collective_evidence_pilot.py
======================================

exp-055 -- pilot of the "collective evidence" research methodology
Jason proposed 2026-09-07, scoped narrow per his own decision. Full
design: research/studies/collective-evidence-pilot-scoping.md
(Advisor-reviewed, one required addition incorporated: an 11-bucket
multiple-comparisons accounting and a 30-distinct-week eligibility
floor, both pre-registered below, before any result is looked at).

WHAT THIS IS: 4 lenses (exp-047 raw NQ trend, exp-048 stop/target
overlay, exp-049 trailing-stop overlay, exp-051 cross-asset portfolio
blend) all share the SAME underlying 52-week momentum signal. This
pilot reads each one's own already-computed, already-verified weekly
P&L (from data/*_discovery.csv, unmodified) and asks: across 4
pre-registered market conditions, do weeks with a given condition show
these lenses collectively doing better or worse than each lens's own
typical week -- counted by DISTINCT WEEK, never by (week, lens) pair,
so 4 correlated lenses agreeing on one unusual week cannot masquerade
as 4 independent confirmations.

THIS IS A DRY RUN OF THE AGGREGATION MACHINERY, not a test of
independent cross-strategy corroboration (see the scoping doc's
Provenance section) -- these 4 lenses are too correlated with each
other for that. Nothing found here is tradeable; a promising bucket
becomes ONE pre-registered hypothesis for prospective testing on the
Validation slice, exactly the exp-053 -> exp-054 pattern already used
once in this project.

CONDITIONS (frozen, causal, point-in-time; NQ's own weekly series is
the reference "market state" for all 4 lenses, since 3 of the 4 are
NQ-only and the 4th blends NQ with 3 other markets):
  1. Volatility regime -- classify_regimes() (study_volatility_regime.py),
     reused unmodified. 3 values (low/mid/high).
  2. Prior-week direction -- sign of the immediately preceding week's
     own log return. 2 values (up/down).
  3. Trend strength -- |52-week trailing momentum signal|, same causal
     expanding-tercile method as classify_regimes(), reimplemented
     generically below since it needs to rank a different series.
     3 values (weak/moderate/strong).
  4. Distance from the 52-week moving average of weekly closes, as a
     percentage, same causal expanding-tercile method. 3 values
     (near/mid/far).
11 buckets total (3+2+3+3) -- stated here before results are looked
at, per the scoping doc's multiple-comparisons accounting.

OUTCOME DEFINITION: per lens, baseline = that lens's own overall mean
weekly net_pnl across its full sample (already-known headline result,
recomputed here directly from its own CSV for exactness). Per week,
relative_outcome = that week's net_pnl - that lens's baseline.

AGGREGATION: group by ISO week FIRST. Per condition bucket: number of
distinct weeks (the real sample size), then the average fraction of
the (up to 4) available lenses beating their own baseline that week,
with a 90% bootstrap CI computed by resampling WEEKS (never lens-weeks).
A bucket is not reported as a candidate unless it has >= 30 distinct
weeks (pre-registered floor, per the scoping doc).

REUSED, UNMODIFIED: classify_regimes, compute_trailing_volatility,
compute_daily_ref_closes, compute_daily_log_returns
(study_volatility_regime.py); resample_to_weekly_closes,
compute_weekly_log_returns, compute_weekly_momentum_signal
(study_nq_weekly_trend_following.py). NEW: the generic tercile ranker
(trend-strength / distance-from-MA use the same causal method
classify_regimes() already established, just applied to different
series), the week-level aggregation, and the day/week condition
mapping.

HOW TO RUN:
    python3 src/study_collective_evidence_pilot.py
"""

import bisect
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import (  # reused unmodified
    compute_daily_ref_closes,
    compute_daily_log_returns,
    compute_trailing_volatility,
    classify_regimes,
)
from study_nq_weekly_trend_following import (  # reused unmodified
    resample_to_weekly_closes,
    compute_weekly_log_returns,
    compute_weekly_momentum_signal,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

MIN_DISTINCT_WEEKS = 30  # pre-registered eligibility floor (Advisor-required)
N_BOOTSTRAP = 5000

LENSES = {
    "exp-047 (raw NQ trend)": "study_nq_weekly_trend_following_discovery.csv",
    "exp-048 (stop/target overlay)": "study_asymmetric_stop_target_overlay_discovery.csv",
    "exp-049 (trailing-stop overlay)": "study_trailing_stop_overlay_discovery.csv",
    "exp-051 (cross-asset portfolio)": "study_cross_asset_weekly_trend_discovery.csv",
}


def causal_expanding_tercile(values_by_week: dict) -> dict:
    """week -> 'low'/'mid'/'high' (or for a 2-value series, only
    'low'/'high' is ever produced since the >=2/3 vs <=1/3 rank test
    still applies, just never lands 'mid' for a strictly binary input)
    via the SAME method as study_volatility_regime.classify_regimes():
    an expanding, causal percentile rank against every value known at
    or before this week, in chronological order. Generic version of
    that function so it can rank trend-strength and distance-from-MA
    too, not just volatility."""
    weeks_sorted = sorted(values_by_week.keys())
    out = {}
    pool = []
    for w in weeks_sorted:
        v = values_by_week[w]
        bisect.insort(pool, v)
        n = len(pool)
        count_le = bisect.bisect_right(pool, v)
        rank = count_le / n
        if rank >= 2.0 / 3.0:
            out[w] = "high"
        elif rank <= 1.0 / 3.0:
            out[w] = "low"
        else:
            out[w] = "mid"
    return out


def build_conditions():
    """Everything condition-related, computed once on NQ's own
    Discovery-slice daily/weekly series (the reference market state
    for all 4 lenses)."""
    full_df, is_synthetic = load_price_data(context="study_collective_evidence_pilot.py (NQ)")
    if is_synthetic:
        return None
    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)  # reused unmodified

    daily_returns = compute_daily_log_returns(ref_closes)  # reused unmodified
    all_days = sorted(day_groups.keys())
    vol_by_day = compute_trailing_volatility(daily_returns, all_days)  # reused unmodified
    vol_regime_by_day = classify_regimes(vol_by_day)  # reused unmodified

    weekly_closes = resample_to_weekly_closes(ref_closes)  # reused unmodified
    weekly_returns = compute_weekly_log_returns(weekly_closes)  # reused unmodified
    all_weeks = sorted(weekly_closes.keys())
    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)  # reused unmodified

    # Condition 1: volatility regime, mapped to each week via its own first trading day.
    day_to_week = {}
    for day in all_days:
        iso_year, iso_week, _ = day.isocalendar()
        day_to_week.setdefault((iso_year, iso_week), []).append(day)
    vol_regime_by_week = {}
    for wk, days in day_to_week.items():
        first_day = sorted(days)[0]
        if first_day in vol_regime_by_day:
            vol_regime_by_week[wk] = vol_regime_by_day[first_day]

    # Condition 2: prior-week direction (sign of the immediately preceding week's own return).
    weeks_with_returns = sorted(weekly_returns.keys())
    prior_dir_by_week = {}
    for i in range(1, len(weeks_with_returns)):
        prev_w, w = weeks_with_returns[i - 1], weeks_with_returns[i]
        prior_dir_by_week[w] = "up" if weekly_returns[prev_w] > 0 else "down"

    # Condition 3: trend strength = |52-week momentum signal|, same weeks mom_by_week covers.
    strength_values = {w: abs(v) for w, v in mom_by_week.items()}
    strength_by_week = causal_expanding_tercile(strength_values)

    # Condition 4: distance from the 52-week moving average of weekly closes, as a percentage.
    # Causal: only closes strictly before week_t are in that week's own trailing average.
    dist_values = {}
    for i, w in enumerate(all_weeks):
        if i < 52:
            continue
        window = [weekly_closes[all_weeks[j]] for j in range(i - 52, i)]
        ma = sum(window) / len(window)
        dist_values[w] = 100.0 * (weekly_closes[w] - ma) / ma
    dist_by_week = causal_expanding_tercile(dist_values)

    return {
        "volatility_regime": vol_regime_by_week,
        "prior_week_direction": prior_dir_by_week,
        "trend_strength": strength_by_week,
        "distance_from_52wk_ma": dist_by_week,
    }


def load_lens(filename: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / filename)
    baseline = df["net_pnl"].mean()
    df = df.copy()
    df["relative_outcome"] = df["net_pnl"] - baseline
    df["beat_baseline"] = df["relative_outcome"] > 0
    return df.set_index("date")


def bootstrap_ci_on_weeks(week_fractions: list, n_boot=N_BOOTSTRAP, seed=13) -> tuple:
    """90% bootstrap CI on the mean of week_fractions, resampling WEEKS
    (each entry here already IS one week's aggregated fraction across
    lenses) -- never lens-weeks. Same percentile-bootstrap convention
    used throughout this project's other studies."""
    rng = np.random.default_rng(seed)
    arr = np.array(week_fractions)
    n = len(arr)
    if n == 0:
        return (None, None)
    boot_means = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        boot_means[i] = sample.mean()
    lo = float(np.percentile(boot_means, 5))
    hi = float(np.percentile(boot_means, 95))
    return (lo, hi)


def analyze_bucket(label: str, weeks_in_bucket: list, lens_data: dict) -> dict:
    """weeks_in_bucket: list of week-key strings ('YYYY-Www'). For each
    such week, look up how many of the 4 lenses have a row AND what
    fraction of those beat their own baseline. One number PER WEEK
    (never per lens-week) feeds the bootstrap."""
    week_fractions = []
    week_detail = []
    for wk in weeks_in_bucket:
        available = []
        for lens_name, df in lens_data.items():
            if wk in df.index:
                available.append(bool(df.loc[wk, "beat_baseline"]))
        if not available:
            continue
        frac = sum(available) / len(available)
        week_fractions.append(frac)
        week_detail.append({"week": wk, "n_lenses": len(available), "frac_beating_baseline": frac})

    n_weeks = len(week_fractions)
    result = {
        "label": label,
        "n_distinct_weeks": n_weeks,
        "eligible": n_weeks >= MIN_DISTINCT_WEEKS,
    }
    if n_weeks == 0:
        result["mean_frac_beating_baseline"] = None
        result["ci_90"] = (None, None)
        return result

    mean_frac = float(np.mean(week_fractions))
    result["mean_frac_beating_baseline"] = mean_frac
    if result["eligible"]:
        result["ci_90"] = bootstrap_ci_on_weeks(week_fractions)
    else:
        result["ci_90"] = (None, None)  # not computed -- ineligible, per pre-registered floor
    return result


def main():
    print("=" * 78)
    print("EXP-055: COLLECTIVE-EVIDENCE PILOT (trend family, 4 correlated lenses)")
    print("=" * 78)
    print("\nDry run of the aggregation machinery -- NOT a test of independent")
    print("cross-strategy corroboration (see scoping doc's Provenance section).")
    print(f"Pre-registered eligibility floor: {MIN_DISTINCT_WEEKS} distinct weeks per bucket.\n")

    conditions = build_conditions()
    if conditions is None:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    lens_data = {name: load_lens(fname) for name, fname in LENSES.items()}
    for name, df in lens_data.items():
        print(f"  {name}: {len(df)} weeks, own baseline mean_net_pnl = {df['net_pnl'].mean():.4f}")

    all_results = {}
    for cond_name, cond_by_week in conditions.items():
        values = sorted(set(cond_by_week.values()))
        print(f"\n{'=' * 78}")
        print(f"CONDITION: {cond_name}  (values: {values})")
        print(f"{'=' * 78}")
        cond_results = {}
        for val in values:
            weeks_str = [f"{wk[0]}-W{wk[1]:02d}" for wk, v in cond_by_week.items() if v == val]
            r = analyze_bucket(f"{cond_name} = {val}", weeks_str, lens_data)
            cond_results[val] = r
            eligibility = "ELIGIBLE" if r["eligible"] else f"NOT ELIGIBLE (< {MIN_DISTINCT_WEEKS} weeks)"
            print(f"  {val:>8}: n_distinct_weeks={r['n_distinct_weeks']:>4}  "
                  f"mean_frac_beating_baseline={r['mean_frac_beating_baseline']}  "
                  f"ci_90={r['ci_90']}  [{eligibility}]")
        all_results[cond_name] = cond_results

    print(f"\n{'=' * 78}")
    print("SUMMARY -- candidates for a follow-up pre-registered prospective test")
    print(f"{'=' * 78}")
    candidates = []
    for cond_name, cond_results in all_results.items():
        for val, r in cond_results.items():
            if r["eligible"] and r["ci_90"][0] is not None and r["ci_90"][0] > 0.5:
                candidates.append((cond_name, val, r))
    if candidates:
        for cond_name, val, r in candidates:
            print(f"  {cond_name} = {val}: {r['n_distinct_weeks']} weeks, "
                  f"90% CI on fraction-beating-baseline = {r['ci_90']} (entirely above 0.5)")
        print("\n  These are candidates ONLY -- per the pre-registered next-step rule, each")
        print("  would need its own single pre-registered prospective test on the")
        print("  Validation slice before being treated as a real finding.")
    else:
        print("  None of the 11 buckets show a 90% CI entirely above the 0.5 baseline")
        print("  fraction (or didn't have enough distinct weeks to test at all). On this")
        print("  narrow, correlated 4-lens pilot, no condition stands out -- consistent")
        print("  with the honest expectation that 4 near-identical lenses mostly just")
        print("  agree with each other everywhere, not selectively.")

    out_path = DATA_DIR / "study_collective_evidence_pilot_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
