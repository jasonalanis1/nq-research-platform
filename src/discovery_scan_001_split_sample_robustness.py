"""
discovery_scan_001_split_sample_robustness.py
================================================

EXPLORATORY ROBUSTNESS ANALYSIS -- not confirmation, not validation.
Second pass on Scan 001 (market_behavior_discovery_scan.py), per Jason's
explicit instruction (2026-09-09): the top candidates were SELECTED using
the full Discovery sample, so splitting that same sample in half does NOT
produce independent confirmation data -- it can only show whether an
effect looks internally consistent (same sign, similar magnitude) across
two non-overlapping sub-periods of the same selection sample. A candidate
that passes this screen still requires a full frozen spec and a genuine
out-of-sample Validation-slice prospective test before it is anything
more than "worth writing up" -- this script freezes nothing and trades
nothing.

METHOD: for each of the top 6 unique (state_var, bucket) candidates from
Scan 001 (deduped across horizon -- reporting all 16 state x bucket x
horizon rows would just restate the same handful of underlying series
multiple times, since horizons on the same days are highly
autocorrelated; kept to the single best-atr_norm horizon per pair), the
bucket EDGES are the exact ones fit on the FULL Discovery sample in Scan
001 (frozen, not refit per half -- refitting edges separately in each
half would let the split itself curve-fit the bucket boundaries, which
defeats the point of a robustness check). Discovery is then split at its
chronological midpoint (first half vs. second half, no shuffling -- this
is a time series). Each half is scored against ITS OWN baseline (all
days within that half with a valid forward return at that horizon), not
the full-sample baseline, so "vs. baseline" in each half is a fair
same-period comparison, and each half's cost floor uses that half's own
average ATR(14).

Also quantifies multiple-testing exposure from Scan 001's full 48-cell
grid, and checks whether each candidate is measuring something distinct
from the project's 3 already-validated volatility/range findings, or
just re-deriving the same range-persistence structure through a return
lens.

HOW TO RUN:
    python3 src/discovery_scan_001_split_sample_robustness.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_NORMALIZED_FLOOR = 0.05
N_BUCKETS = 3
BUCKET_LABELS = ["low", "mid", "high"]

# Top 6 unique (state_var, bucket) pairs from Scan 001, deduped across
# horizon to their single best-atr_norm horizon (see module docstring).
CANDIDATES = [
    {"state_var": "location_in_range", "bucket": "high", "horizon_days": 10},
    {"state_var": "overnight_range_vs_atr", "bucket": "high", "horizon_days": 10},
    {"state_var": "overnight_range_vs_atr", "bucket": "mid", "horizon_days": 10},
    {"state_var": "location_in_range", "bucket": "mid", "horizon_days": 5},
    {"state_var": "location_in_range", "bucket": "low", "horizon_days": 10},
    {"state_var": "gap_vs_atr", "bucket": "low", "horizon_days": 10},
]

# The 3 already-validated findings' predictor family, for the
# rediscovery-check section below.
VALIDATED_FINDINGS_STATE_FAMILY = {
    "range_vs_atr": "Same predictor as hyp-000046/048 (prior-day range regime -> next-day RANGE). "
                     "That finding predicts MAGNITUDE (range), never direction/return.",
    "overnight_range_vs_atr": "Same predictor as hyp-000056/057 (overnight coil -> same-day RTH RANGE). "
                               "That finding predicts MAGNITUDE (range), never direction/return.",
    "gap_vs_atr": "Not used by any of the 3 validated findings.",
    "location_in_range": "Not used by any of the 3 validated findings.",
    "directional_persistence": "Not used by any of the 3 validated findings.",
}


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        s = rng.choice(v, size=len(v), replace=True)
        means[i] = s.mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def forward_return(close_series, i, horizon):
    if i + horizon >= len(close_series):
        return None
    c0, c1 = close_series.iloc[i], close_series.iloc[i + horizon]
    if c0 <= 0:
        return None
    return float(c1 - c0)


def forward_range(states_reset, i, horizon):
    """Same-window forward RANGE (max High - min Low over the next
    `horizon` days), used only for the rediscovery-check diagnostic
    below -- not part of the candidate's own effect measurement."""
    j = i + horizon
    if j >= len(states_reset):
        return None
    window = states_reset.iloc[i + 1: j + 1]
    if window.empty:
        return None
    return float(window["High"].max() - window["Low"].min())


def score_half(half_states, half_close, var, bucket, horizon, bin_edges, labels):
    bucket_labels = pd.cut(half_states[var], bins=bin_edges, labels=labels, duplicates="drop")
    half_atr = float(half_states["atr14"].dropna().mean())

    fwd_rets_bucket, fwd_rets_baseline = [], []
    for i in range(len(half_states)):
        r = forward_return(half_close, i, horizon)
        if r is None:
            continue
        fwd_rets_baseline.append(r)
        b = bucket_labels.iloc[i]
        if pd.notna(b) and str(b) == bucket:
            fwd_rets_bucket.append(r)

    n = len(fwd_rets_bucket)
    baseline_mean = float(np.mean(fwd_rets_baseline)) if fwd_rets_baseline else float("nan")
    if n < 2:
        return {
            "n": n, "mean_fwd_return_pts": float("nan"), "ci_90": [float("nan"), float("nan")],
            "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": float("nan"),
            "atr_normalized_effect": float("nan"), "credible_vs_zero": False,
            "clears_cost_floor": False, "avg_atr14": half_atr,
        }
    mean_r = float(np.mean(fwd_rets_bucket))
    ci = bootstrap_mean_ci(fwd_rets_bucket)
    effect = mean_r - baseline_mean
    atr_norm = abs(effect) / half_atr if half_atr > 0 else float("nan")
    return {
        "n": n, "mean_fwd_return_pts": mean_r, "ci_90": list(ci),
        "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": effect,
        "atr_normalized_effect": atr_norm,
        "credible_vs_zero": bool(ci[0] > 0 or ci[1] < 0),
        "clears_cost_floor": bool(atr_norm >= ATR_NORMALIZED_FLOOR),
        "avg_atr14": half_atr,
    }


def main():
    print("=" * 78)
    print("SCAN 001 -- EXPLORATORY SPLIT-SAMPLE ROBUSTNESS SCREEN (not confirmation)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="discovery_scan_001_split_sample_robustness.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = build_state_frame(discovery)
    states_reset = states.reset_index()
    close = states_reset["Close"]
    mid = len(states_reset) // 2
    first_half = states_reset.iloc[:mid].reset_index(drop=True)
    second_half = states_reset.iloc[mid:].reset_index(drop=True)
    first_close = first_half["Close"]
    second_close = second_half["Close"]
    print(f"\nDiscovery total days: {len(states_reset)}  ->  first half: {len(first_half)}"
          f"  ({first_half['date'].iloc[0]} to {first_half['date'].iloc[-1]}),"
          f"  second half: {len(second_half)}"
          f"  ({second_half['date'].iloc[0]} to {second_half['date'].iloc[-1]})\n")

    results = []
    for cand in CANDIDATES:
        var, bucket, horizon = cand["state_var"], cand["bucket"], cand["horizon_days"]
        full_series = states_reset[var]
        valid = full_series.notna()
        edges = np.unique(np.nanpercentile(full_series[valid], [100 / 3, 200 / 3]))
        bin_edges = [-np.inf] + list(edges) + [np.inf]
        labels = BUCKET_LABELS[: len(bin_edges) - 1]
        if bucket not in labels:
            print(f"  {var}/{bucket}: bucket collapsed on full sample (degenerate edges), skipped.")
            continue

        first = score_half(first_half, first_close, var, bucket, horizon, bin_edges, labels)
        second = score_half(second_half, second_close, var, bucket, horizon, bin_edges, labels)

        direction_first = np.sign(first["effect_vs_baseline_pts"]) if not np.isnan(first["effect_vs_baseline_pts"]) else 0
        direction_second = np.sign(second["effect_vs_baseline_pts"]) if not np.isnan(second["effect_vs_baseline_pts"]) else 0
        direction_consistent = bool(direction_first != 0 and direction_first == direction_second)

        mag_ratio = None
        if not np.isnan(first["atr_normalized_effect"]) and first["atr_normalized_effect"] > 0:
            mag_ratio = second["atr_normalized_effect"] / first["atr_normalized_effect"] if not np.isnan(second["atr_normalized_effect"]) else None
        magnitude_consistent = bool(mag_ratio is not None and 0.4 <= mag_ratio <= 2.5)

        mechanism_note = VALIDATED_FINDINGS_STATE_FAMILY.get(var, "Not previously used in this project.")

        row = {
            "state_var": var, "bucket": bucket, "horizon_days": horizon,
            "first_half": first, "second_half": second,
            "direction_consistent": direction_consistent,
            "magnitude_ratio_2nd_over_1st": mag_ratio,
            "magnitude_consistent": magnitude_consistent,
            "survives_both_halves": bool(
                first["credible_vs_zero"] and first["clears_cost_floor"]
                and second["credible_vs_zero"] and second["clears_cost_floor"]
                and direction_consistent
            ),
            "mechanism_note": mechanism_note,
            "same_family_as_validated_finding": var in ("range_vs_atr", "overnight_range_vs_atr"),
        }
        results.append(row)

        print(f"{var} / {bucket} / h={horizon}d")
        print(f"  1st half: n={first['n']:4d}  mean={first['mean_fwd_return_pts']:+7.2f}pts  "
              f"vs_baseline={first['effect_vs_baseline_pts']:+7.2f}pts  atr_norm={first['atr_normalized_effect']:.4f}  "
              f"credible={first['credible_vs_zero']}  cost_floor={first['clears_cost_floor']}")
        print(f"  2nd half: n={second['n']:4d}  mean={second['mean_fwd_return_pts']:+7.2f}pts  "
              f"vs_baseline={second['effect_vs_baseline_pts']:+7.2f}pts  atr_norm={second['atr_normalized_effect']:.4f}  "
              f"credible={second['credible_vs_zero']}  cost_floor={second['clears_cost_floor']}")
        print(f"  direction_consistent={direction_consistent}  magnitude_ratio(2nd/1st)={mag_ratio}  "
              f"survives_both_halves={row['survives_both_halves']}")
        print(f"  mechanism_note: {mechanism_note}\n")

    survivors = [r for r in results if r["survives_both_halves"]]

    # --- Multiple-testing exposure quantification (Scan 001's full 48-cell grid) ---
    scan001 = json.load(open(DATA_DIR / "market_behavior_discovery_scan_001_results.json"))
    total_cells = scan001["total_cells"]
    passing_cells = scan001["cells_passing_unusual_and_cost_gate"]
    alpha = 0.10  # two-sided, matches this project's 90% CI convention
    expected_false_positives_naive = alpha * total_cells
    n_state_vars_scanned = 4  # directional_persistence was degenerate/skipped in Scan 001
    n_independent_series_approx = n_state_vars_scanned * N_BUCKETS  # horizons within a series are highly autocorrelated, not independent
    expected_false_positives_effective = alpha * n_independent_series_approx

    print("=" * 78)
    print("MULTIPLE-TESTING EXPOSURE")
    print("=" * 78)
    print(f"Scan 001 total cells tested: {total_cells}")
    print(f"Cells passing (credible + cost floor): {passing_cells}")
    print(f"Naive expectation under pure null at alpha={alpha}: {expected_false_positives_naive:.1f} false positives by chance")
    print(f"Approx. INDEPENDENT series (state_var x bucket, collapsing the 4 overlapping horizons "
          f"per series -- 1/3/5/10-day forward windows on the same days are highly autocorrelated, "
          f"not independent tests): ~{n_independent_series_approx}")
    print(f"Expected false positives at alpha={alpha} among ~{n_independent_series_approx} effectively-independent "
          f"series: {expected_false_positives_effective:.1f}")
    print(f"Observed: {len(set((r['state_var'], r['bucket']) for r in results))} of the top {len(CANDIDATES)} "
          f"deduped series carried into this robustness pass; {len(survivors)} survive both-halves + direction + cost floor.")
    print("Reading: 16/48 raw cells is NOT surprising on its own -- most of that is the same handful of "
          "underlying (state_var, bucket) series repeated across 4 correlated horizons. Collapsed to "
          "~12 effectively-independent series, order-of-magnitude 1-2 would be expected as pure false "
          "positives at this alpha. Whether the observed hit rate is above that baseline is exactly "
          "what the split-sample survival count above should be read against -- it is evidence, not proof.\n")

    out = {
        "analysis": "Scan 001 split-sample robustness screen (EXPLORATORY, not confirmation)",
        "spec": "research/infrastructure/market-behavior-discovery-engine-design.md",
        "candidates_screened": results,
        "survivors_both_halves_direction_and_cost_floor": survivors,
        "multiple_testing": {
            "total_cells_scan001": total_cells,
            "passing_cells_scan001": passing_cells,
            "alpha": alpha,
            "expected_false_positives_naive": expected_false_positives_naive,
            "approx_independent_series": n_independent_series_approx,
            "expected_false_positives_effective": expected_false_positives_effective,
        },
        "note": (
            "Per Jason's explicit instruction: candidates were selected on the full Discovery "
            "sample, so first-half/second-half agreement is NOT independent confirmation -- it "
            "only screens for gross internal inconsistency (sign flips, order-of-magnitude "
            "instability) before any candidate is worth writing a frozen spec for. Nothing here "
            "is promoted, frozen, or traded. A candidate that survives this screen still needs "
            "its own frozen monetization spec and a genuine Validation-slice prospective test."
        ),
    }
    out_path = DATA_DIR / "discovery_scan_001_split_sample_robustness_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Saved full results to {out_path}.")


if __name__ == "__main__":
    main()
