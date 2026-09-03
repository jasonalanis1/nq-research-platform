"""
study_cpi_nfp_reversal_followup.py
====================================

Implements the frozen spec in
`research/studies/cpi-nfp-pooled-reversal-followup.md` (exp-045).
Pooled CPI+NFP version of exp-042's CPI-only reversal follow-up --
identical methodology, one change: the release-type mask is widened
from CPI-only to CPI+NFP, exactly as exp-041's own original design
already anticipated. Reuses `study_post_release_continuation.py`'s
scan/compute functions and `directional_continuation` statistic
UNMODIFIED, same as exp-042.

Read `research/studies/cpi-nfp-pooled-reversal-followup.md` first --
it discloses, before this was run, that exp-041's own descriptive
breakdown shows CPI-only and NFP-only do NOT agree in sign, so pooling
them could dilute the near-miss result exp-042 found, not just enlarge
its sample.

HOW TO RUN:
    python3 src/study_cpi_nfp_reversal_followup.py
"""

import json
from pathlib import Path

import numpy as np

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from study_nq_trend_following import bootstrap_mean_ci  # reused unmodified
from study_post_release_continuation import (
    compute_directional_continuation,
    robustness_drop_largest,
    robustness_split_half,
    scan_all_days,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 2000       # matches study_post_release_continuation.py
RANDOM_SEED = 11         # matches study_post_release_continuation.py
ECONOMIC_THRESHOLD_POINTS = 2 * ROUND_TRIP_COST_POINTS  # frozen Step-2-gate #2, same bar as every prior study
PROMOTION_BAR_MIN_TRADES = 150  # docs/RESEARCH_INTEGRITY_PROTOCOL.md


def one_sample_test(values) -> dict:
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


def main():
    full_df, is_synthetic = load_price_data(context="study_cpi_nfp_reversal_followup.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    scanned = scan_all_days(discovery_df)                       # reused unmodified
    sub, exclusion_counts = compute_directional_continuation(scanned)  # reused unmodified

    pooled_mask = sub["release_type"].isin(["cpi", "nfp"])
    pooled_rows = sub[pooled_mask].copy()

    pooled_rows["reversal_pnl_gross"] = -1.0 * pooled_rows["directional_continuation"]
    pooled_rows["reversal_pnl_net"] = pooled_rows["reversal_pnl_gross"] - ROUND_TRIP_COST_POINTS

    print("=" * 78)
    print("POOLED CPI+NFP REVERSAL FOLLOW-UP (exp-045) -- Discovery slice")
    print("=" * 78)
    print(f"\nExclusions (from the shared scan/compute step): {exclusion_counts}")
    print(f"Pooled CPI+NFP rows available: {len(pooled_rows)}")
    by_type = pooled_rows["release_type"].value_counts().to_dict()
    print(f"  Breakdown: {by_type}")
    meets_min_trades = len(pooled_rows) >= PROMOTION_BAR_MIN_TRADES
    print(f"\n** Promotion-bar reminder: this project's minimum is "
          f"{PROMOTION_BAR_MIN_TRADES} trades. n={len(pooled_rows)} here "
          f"{'MEETS' if meets_min_trades else 'does NOT meet'} that minimum. **")

    print(f"\n--- PRIMARY: pooled CPI+NFP reversal trade, net of round-trip cost "
          f"({ROUND_TRIP_COST_POINTS:.3f} pts) ---")
    primary = one_sample_test(pooled_rows["reversal_pnl_net"])
    for k, v in primary.items():
        print(f"  {k}: {v}")
    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['significant']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= {ECONOMIC_THRESHOLD_POINTS:.3f} pts): "
          f"{primary['economically_meaningful']}")
    print(f"  Trade-count gate (>= {PROMOTION_BAR_MIN_TRADES}): {meets_min_trades}")

    print("\n--- Descriptive: gross (pre-cost) reversal ---")
    gross = one_sample_test(pooled_rows["reversal_pnl_gross"])
    print(f"  n={gross['n']} mean={gross['mean']:+.3f}pts  90% CI=[{gross['ci_90'][0]:+.3f}, {gross['ci_90'][1]:+.3f}]")

    print("\n--- Descriptive: cpi-only vs nfp-only within this pooled sample (disclosed, not gating) ---")
    for rtype in ("cpi", "nfp"):
        r = one_sample_test(pooled_rows.loc[pooled_rows["release_type"] == rtype, "reversal_pnl_net"])
        print(f"  {rtype}: n={r['n']} mean={r['mean']:+.3f}pts  90% CI=[{r['ci_90'][0]:+.3f}, {r['ci_90'][1]:+.3f}]")

    drop_input = sub.copy()
    drop_input.loc[pooled_mask, "directional_continuation"] = -1.0 * (
        sub.loc[pooled_mask, "directional_continuation"]
    ) - ROUND_TRIP_COST_POINTS
    print("\n--- Robustness (a): drop single largest-|reversal_pnl_net| day ---")
    drop_result = robustness_drop_largest(drop_input, pooled_mask)
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(drop_input, pooled_mask)
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n" + "=" * 78)
    if primary["significant"] and primary["economically_meaningful"] and meets_min_trades:
        verdict = "PROMOTE-ELIGIBLE -- clears full promotion bar (statistical, economic, and trade-count gates)"
    elif primary["significant"] and primary["economically_meaningful"]:
        verdict = "retest -- promising, underpowered (n < 150-trade promotion bar)"
    else:
        verdict = "kill -- not statistically credible and/or not economically meaningful after cost"
    print(f"Verdict: {verdict}")

    out = {
        "exclusion_counts": exclusion_counts,
        "n_pooled_rows": len(pooled_rows),
        "release_type_breakdown": by_type,
        "meets_min_trades": meets_min_trades,
        "primary_net": primary,
        "descriptive_gross": gross,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "verdict": verdict,
    }
    json_path = DATA_DIR / "study_cpi_nfp_reversal_followup_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()
