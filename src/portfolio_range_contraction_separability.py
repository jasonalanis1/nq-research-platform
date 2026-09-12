"""Portfolio Agent separability check for hyp-000046/048 (prior-day range
regime -> today's range ratio, the FIRST of the project's three validated
volatility-persistence facts) against the other two: overnight coil
(hyp-056/057) and midday-lull afternoon persistence (hyp-105/106/141).

This is the pairing that was never explicitly run: H105's own separability
check (2026-09-12) tested H105 against the overnight coil only; H140's
director-reeval (2026-09-11) tested a different candidate against the
overnight coil. Range-contraction vs. overnight-coil and range-contraction
vs. midday-lull have both been used together in volatility_conditioning.py
since 2026-09-08 without ever being checked pairwise for redundancy. This
closes that gap (queue v2 item 4, September 12th 3pm cycle).

Same discipline as every prior separability check in this project:
  1. correlation between the two binary/near-binary classifications;
  2. within each conditioning tercile/class of the OTHER fact, does the
     narrow/wide-vs-not spread in same-day range ratio survive;
  3. fraction of the raw spread retained after residualizing (subtracting
     the other fact's group mean).

Discovery data only. All three classifications reused UNMODIFIED from
volatility_conditioning.py (prior_day_narrow/wide, coiled_overnight,
narrow_midday) -- nothing retuned, nothing refit.

HOW TO RUN:
    python3 src/portfolio_range_contraction_separability.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
from volatility_conditioning import build_conditioning_frame, build_midday_afternoon_frame  # noqa: E402
from study_intraday_behavior_batch1 import build_daily_frame  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "data" / "portfolio_range_contraction_separability_results.json"
N_BOOTSTRAP = 3000
RNG_SEED = 20260912


def block_bootstrap_ci(values: np.ndarray, n_boot: int = N_BOOTSTRAP, block: int = 10, seed: int = RNG_SEED):
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n == 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block))
    means = []
    for _ in range(n_boot):
        starts = rng.integers(0, max(n - block, 1), size=n_blocks)
        sample = np.concatenate([values[s:s + block] for s in starts])[:n]
        means.append(sample.mean())
    means = np.sort(means)
    lo = means[int(0.05 * n_boot)]
    hi = means[int(0.95 * n_boot)]
    return (float(lo), float(hi))


def main():
    df_all, is_synthetic = load_price_data(context="portfolio_range_contraction_separability.py")
    if is_synthetic:
        raise SystemExit("ABORT: only synthetic data available.")
    disc = get_discovery_data(df_all)

    cond = build_conditioning_frame(disc)          # prior_day_narrow, prior_day_wide, coiled_overnight
    midday = build_midday_afternoon_frame(disc)     # narrow_midday
    daily = build_daily_frame(disc)                 # range, trailing_avg_range -> next_range_ratio needs shift
    daily = daily.copy()
    daily["same_day_range_ratio"] = daily["range"] / daily["trailing_avg_range"]

    frame = cond.join(midday[["narrow_midday"]], how="inner").join(
        daily[["same_day_range_ratio"]], how="inner").dropna(subset=["same_day_range_ratio"])

    results = {"n_total": int(len(frame))}

    for other_name, other_col in [("coiled_overnight", "coiled_overnight"), ("narrow_midday", "narrow_midday")]:
        block = {}
        # correlation between prior_day_narrow (as the range-contraction signal) and the other binary fact
        corr = float(np.corrcoef(frame["prior_day_narrow"].astype(float), frame[other_col].astype(float))[0, 1])
        block["correlation_prior_day_narrow_vs_" + other_name] = round(corr, 4)

        overlap = float((frame["prior_day_narrow"] & frame[other_col]).mean())
        expected_indep = float(frame["prior_day_narrow"].mean() * frame[other_col].mean())
        block["overlap_both_true"] = round(overlap, 4)
        block["overlap_expected_if_independent"] = round(expected_indep, 4)

        # raw spread: prior_day_narrow vs not, on same_day_range_ratio
        narrow_vals = frame.loc[frame["prior_day_narrow"], "same_day_range_ratio"].values
        not_narrow_vals = frame.loc[~frame["prior_day_narrow"], "same_day_range_ratio"].values
        raw_spread = float(not_narrow_vals.mean() - narrow_vals.mean())
        block["raw_spread_not_narrow_minus_narrow"] = round(raw_spread, 4)
        block["n_narrow"] = int(len(narrow_vals))
        block["n_not_narrow"] = int(len(not_narrow_vals))

        # within each level of the OTHER fact, does the spread survive
        within = {}
        for level, sub in frame.groupby(other_col):
            nv = sub.loc[sub["prior_day_narrow"], "same_day_range_ratio"].values
            nnv = sub.loc[~sub["prior_day_narrow"], "same_day_range_ratio"].values
            if len(nv) < 5 or len(nnv) < 5:
                within[str(level)] = {"n_narrow": int(len(nv)), "n_not_narrow": int(len(nnv)), "note": "too few for a stable estimate"}
                continue
            spread = float(nnv.mean() - nv.mean())
            within[str(level)] = {
                "n_narrow": int(len(nv)), "n_not_narrow": int(len(nnv)),
                "spread": round(spread, 4),
            }
        block["within_other_fact_level"] = within

        # residualized: subtract the other-fact group mean from same_day_range_ratio, then recompute spread
        group_mean = frame.groupby(other_col)["same_day_range_ratio"].transform("mean")
        frame["_resid"] = frame["same_day_range_ratio"] - group_mean
        resid_narrow = frame.loc[frame["prior_day_narrow"], "_resid"].values
        resid_not_narrow = frame.loc[~frame["prior_day_narrow"], "_resid"].values
        resid_spread = float(resid_not_narrow.mean() - resid_narrow.mean())
        pct_retained = round(100.0 * resid_spread / raw_spread, 1) if raw_spread else float("nan")
        block["residualized_spread"] = round(resid_spread, 4)
        block["pct_of_raw_spread_retained"] = pct_retained

        # bootstrap CI on the residualized spread (diff of group means, block bootstrap on the residual series per group)
        lo_n, hi_n = block_bootstrap_ci(resid_narrow)
        lo_nn, hi_nn = block_bootstrap_ci(resid_not_narrow)
        block["residualized_narrow_mean_ci_90"] = (round(lo_n, 4), round(hi_n, 4))
        block["residualized_not_narrow_mean_ci_90"] = (round(lo_nn, 4), round(hi_nn, 4))

        results[f"vs_{other_name}"] = block

    Path("data").mkdir(exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)

    print(f"n_total={results['n_total']}")
    for other_name in ("coiled_overnight", "narrow_midday"):
        b = results[f"vs_{other_name}"]
        print(f"\n--- prior_day_narrow vs {other_name} ---")
        print(f"  correlation: {b['correlation_prior_day_narrow_vs_' + other_name]}")
        print(f"  overlap both true: {b['overlap_both_true']} (expected if independent: {b['overlap_expected_if_independent']})")
        print(f"  raw spread (not_narrow - narrow): {b['raw_spread_not_narrow_minus_narrow']}  n_narrow={b['n_narrow']} n_not_narrow={b['n_not_narrow']}")
        print(f"  within-level spreads: {b['within_other_fact_level']}")
        print(f"  residualized spread: {b['residualized_spread']}  ({b['pct_of_raw_spread_retained']}% of raw retained)")
    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
