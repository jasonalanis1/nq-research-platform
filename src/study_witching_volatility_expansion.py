"""
study_witching_volatility_expansion.py
========================================

Quarterly witching volatility expansion -- frozen spec:
research/studies/witching-volatility-expansion-design-spec.md.

Sourced from the market-microstructure research agent (2026-09-09).
Magnitude/volatility-clustering mechanism (same family as this
project's 3 validated findings), NOT directional. Data requirement:
none beyond existing NQ 1-min bars -- witching dates are calendar-
derived. Directional pre-commitment (witching ratio > 1.0 and >
non-witching ratio) stated in the frozen spec BEFORE this scan ran.

Sample size caveat: ~40 witching-day observations expected -- the
thinnest sample of any Observatory scan run in this project. Treat
any "Promising" label with extra skepticism per the frozen spec.

Non-trading, exploratory. Discovery data only.

HOW TO RUN:
    python3 src/study_witching_volatility_expansion.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from research_ledger import log_hypothesis

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

LOOKBACK_DAYS = 20
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_PROMISING = 40


def third_friday(year, month):
    d = pd.Timestamp(year=year, month=month, day=1)
    # first Friday
    offset = (4 - d.weekday()) % 7  # Monday=0 ... Friday=4
    first_friday = d + pd.Timedelta(days=offset)
    return (first_friday + pd.Timedelta(days=14)).date()


def bootstrap_ratio_ci(ratios, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    r = np.asarray(ratios, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        s = rng.choice(r, size=len(r), replace=True)
        means[i] = s.mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def main():
    print("=" * 78)
    print("QUARTERLY WITCHING VOLATILITY EXPANSION -- frozen scan (exploratory)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/witching-volatility-expansion-design-spec.md\n")

    df, is_synthetic = load_price_data(context="study_witching_volatility_expansion.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index

    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days available: {len(days_sorted)}")

    # RTH range per day
    rth_ranges = {}
    for day in days_sorted:
        rth = day_groups[day].between_time("09:30", "16:00")
        if rth.empty or len(rth) < 20:
            continue
        rth_ranges[day] = float(rth["High"].max() - rth["Low"].min())

    days_with_range = sorted(rth_ranges.keys())

    # witching dates present in Discovery
    years = sorted(set(d.year for d in days_with_range))
    witching_dates = set()
    for y in years:
        for m in (3, 6, 9, 12):
            witching_dates.add(third_friday(y, m))

    ratios_witching, ratios_non_witching = [], []

    for i, day in enumerate(days_with_range):
        # trailing 20-day average range, excluding today
        prior_days = days_with_range[max(0, i - LOOKBACK_DAYS):i]
        if len(prior_days) < LOOKBACK_DAYS:
            continue
        trailing_avg = np.mean([rth_ranges[d] for d in prior_days])
        if trailing_avg <= 0:
            continue
        ratio = rth_ranges[day] / trailing_avg

        if day in witching_dates:
            ratios_witching.append(ratio)
        else:
            ratios_non_witching.append(ratio)

    n_w, n_nw = len(ratios_witching), len(ratios_non_witching)
    print(f"\nWitching-day observations: {n_w}   non-witching observations: {n_nw}")

    if n_w == 0:
        print("\nABORT: 0 witching-day observations. This is a DATA LIMITATION, not a "
              "tested null -- our continuous NQ series has no usable RTH bars on "
              "quarterly witching days (checked directly: 2016/2018/2020 witching "
              "dates all show 0-1 RTH bars vs. 250-450 total bars that day), almost "
              "certainly because the continuous-contract construction rolls exactly "
              "at quarterly expiration and drops/mislabels that session's RTH data. "
              "Needs raw per-contract data across the roll to test properly -- same "
              "limitation as the VIX futures term-structure candidate. Logging as "
              "data-limitation, not REJECTED (a REJECTED/null would misrepresent "
              "this as a tested-and-failed hypothesis).")
        out = {
            "spec": "research/studies/witching-volatility-expansion-design-spec.md",
            "status": "ABORTED -- data limitation, not a tested null",
            "n_witching": 0,
            "reason": "Continuous NQ series has 0 usable RTH bars on quarterly witching days "
                      "(roll-day data gap/mislabeling in continuous-contract construction). "
                      "Needs raw per-contract data across the roll -- not yet available.",
        }
        out_path = DATA_DIR / "study_witching_volatility_expansion_results.json"
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2, default=str)
        record = log_hypothesis(
            strategy_name="witching_volatility_expansion",
            strategy_origin="data_discovered",
            parameters={"n_witching": 0, "reason": "roll-day RTH data gap in continuous series"},
            data_slice_used="discovery",
            trade_count=0,
            strategy_status="REJECTED",
            notes=(
                "Observatory v9 / witching-volatility-expansion-design-spec.md. "
                "ABORTED, not a tested null: continuous NQ series has 0 usable RTH "
                "bars on every quarterly witching day checked (2016/2018/2020) -- "
                "the continuous-contract roll coincides with quarterly expiration and "
                "drops that session's RTH data. Cannot test this hypothesis without "
                "raw per-contract data across the roll. Logged REJECTED only because "
                "the ledger has no ABORTED status; the real status is needs different "
                "data, not run. Do not re-attempt with the continuous series -- fix "
                "the data first. Full: data/study_witching_volatility_expansion_results.json."
            ),
        )
        print(f"\nLogged to ledger: {record.hypothesis_id} -- status {record.strategy_status} (data limitation)")
        return

    ci_w = bootstrap_ratio_ci(ratios_witching)
    ci_nw = bootstrap_ratio_ci(ratios_non_witching)
    mean_w = float(np.mean(ratios_witching)) if ratios_witching else float("nan")
    mean_nw = float(np.mean(ratios_non_witching)) if ratios_non_witching else float("nan")

    print(f"\nWitching-day range ratio:     mean={mean_w:.3f}  ci_90={ci_w}")
    print(f"Non-witching range ratio:     mean={mean_nw:.3f}  ci_90={ci_nw}")

    credible_above_1 = ci_w[0] > 1.0
    credible_above_complement = ci_w[0] > ci_nw[1]
    direction_matches_literature = mean_w > mean_nw

    print(f"\nWitching ratio CI entirely above 1.0: {credible_above_1}")
    print(f"Witching ratio CI entirely above non-witching CI: {credible_above_complement}")
    print(f"Direction matches literature (witching > non-witching): {direction_matches_literature}")
    print(f"n={n_w} -- below MIN_N_FOR_PROMISING={MIN_N_FOR_PROMISING}: {n_w < MIN_N_FOR_PROMISING}")

    if n_w < MIN_N_FOR_PROMISING:
        label = "Interesting (n below promising threshold)" if (credible_above_1 and credible_above_complement) else "No meaningful difference"
    elif credible_above_1 and credible_above_complement:
        label = "Promising"
    elif credible_above_1 or credible_above_complement:
        label = "Interesting"
    else:
        label = "No meaningful difference"

    print(f"\nLabel: {label}")

    out = {
        "spec": "research/studies/witching-volatility-expansion-design-spec.md",
        "status": "EXPLORATORY -- not a finding, not a strategy",
        "n_witching": n_w,
        "n_non_witching": n_nw,
        "witching_ratio_mean": mean_w,
        "witching_ratio_ci_90": ci_w,
        "non_witching_ratio_mean": mean_nw,
        "non_witching_ratio_ci_90": ci_nw,
        "credible_above_1": credible_above_1,
        "credible_above_complement": credible_above_complement,
        "direction_matches_literature": direction_matches_literature,
        "below_min_n_for_promising": n_w < MIN_N_FOR_PROMISING,
        "label": label,
    }
    out_path = DATA_DIR / "study_witching_volatility_expansion_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved results to {out_path}.")

    record = log_hypothesis(
        strategy_name="witching_volatility_expansion",
        strategy_origin="data_discovered",
        parameters={
            "n_witching": n_w, "n_non_witching": n_nw,
            "witching_ratio_mean": mean_w, "witching_ratio_ci_90": list(ci_w),
            "non_witching_ratio_mean": mean_nw, "non_witching_ratio_ci_90": list(ci_nw),
        },
        data_slice_used="discovery",
        trade_count=n_w,
        strategy_status="PROMISING" if label == "Promising" else "REJECTED",
        notes=(
            f"Observatory v9 / witching-volatility-expansion-design-spec.md. "
            f"Sourced from market-microstructure research agent (2026-09-09), free/"
            f"zero-cost calendar-derived data. Magnitude/volatility finding (same "
            f"family as the 3 validated range-persistence findings), not directional. "
            f"Thin sample (n={n_w}, below MIN_N_FOR_PROMISING={MIN_N_FOR_PROMISING}) -- "
            f"flagged in frozen spec as the thinnest sample of any Observatory scan to "
            f"date, treat any positive result with extra skepticism. "
            f"Result: {label}. witching_mean={mean_w:.3f} ci_90={ci_w} vs "
            f"non_witching_mean={mean_nw:.3f} ci_90={ci_nw}. "
            f"Full: data/study_witching_volatility_expansion_results.json."
        ),
    )
    print(f"\nLogged to ledger: {record.hypothesis_id} -- status {record.strategy_status}")


if __name__ == "__main__":
    main()
