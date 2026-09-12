"""
discovery_scan_004_split_sample_robustness.py
================================================

EXPLORATORY ROBUSTNESS ANALYSIS -- not confirmation, not validation.
Same method and same caveat as discovery_scan_001/003's split-sample
screens: Scan 004's one surviving cell was SELECTED using the full
Discovery sample, so splitting that same sample in half does NOT
produce independent confirmation data -- it can only show whether the
effect looks internally consistent (same sign, similar magnitude)
across two non-overlapping sub-periods of the same selection sample. A
candidate that passes this screen still requires a regime check, a
Mechanism pass, a full frozen spec, and a genuine out-of-sample
Validation-slice prospective test before it is anything more than
"worth writing up." This script freezes nothing and trades nothing.

METHOD: identical to the Scan 001/003 versions -- bucket EDGES are the
exact ones fit on the FULL Discovery sample in Scan 004 (frozen, not
refit per half), Discovery is split at its chronological midpoint, each
half scored against its OWN baseline and its OWN average ATR(14).

CANDIDATE (the sole survivor of Scan 004's Discovery pass,
market_behavior_discovery_scan_004_results.json):
  - prior_close_location_in_range / low / intraday
    (n=552, atr_norm=0.0550 full-sample -- barely above the 0.05 floor,
    flagged going in as a real risk this dies here, not a formality)

HOW TO RUN:
    PYTHONPATH=src python3 src/discovery_scan_004_split_sample_robustness.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS
from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_state_primitives_v3 import extend_state_frame_v3
from market_state_primitives_v4 import extend_state_frame_v4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_NORMALIZED_FLOOR = 0.05
ABSOLUTE_COST_MULTIPLE = 3.0
BUCKET_LABELS = ["low", "mid", "high"]

CANDIDATES = [
    {"state_var": "prior_close_location_in_range", "bucket": "low", "horizon": "intraday"},
]

MECHANISM_NOTE = {
    "prior_close_location_in_range": (
        "New descriptor (market_state_primitives_v4.py). Candidate mechanism: "
        "a session that closes in the bottom tercile of its own RTH range "
        "reflects late selling pressure/weak positioning into the close; the "
        "following session's own RTH move then runs positive on average -- a "
        "same-day mean-reversion/bounce story, consistent with a liquidity- "
        "provision or overextension-unwind explanation, not an arbitrary grid "
        "cell. Distinct from hyp-000110 (closing-pressure-reversal, REJECTED "
        "cost-dominated): that test used last-15-min RETURN magnitude/sign as "
        "state and NEXT-DAY close-to-close as outcome; this uses the close's "
        "LOCATION within its own day's range as state and the SAME-DAY "
        "following session (open-to-close) as outcome -- a different state "
        "variable and a different, more directly-connected outcome window. "
        "Needs a real Mechanism-agent pass before being taken as confirmed, "
        "not assumed here."
    ),
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


def forward_return_intraday(close_series, rth_open_series, i):
    o, c = rth_open_series.iloc[i], close_series.iloc[i]
    if pd.isna(o) or pd.isna(c):
        return None
    return float(c - o)


def score_half(half_states, half_close, half_rth_open, var, bucket, bin_edges, labels, absolute_cost_floor_pts):
    bucket_labels = pd.cut(half_states[var], bins=bin_edges, labels=labels, duplicates="drop")
    half_atr = float(half_states["atr14"].dropna().mean())

    fwd_rets_bucket, fwd_rets_baseline = [], []
    for i in range(len(half_states)):
        r = forward_return_intraday(half_close, half_rth_open, i)
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
    clears_atr_floor = bool(atr_norm >= ATR_NORMALIZED_FLOOR)
    clears_absolute_floor = bool(abs(effect) >= absolute_cost_floor_pts)
    return {
        "n": n, "mean_fwd_return_pts": mean_r, "ci_90": list(ci),
        "baseline_mean_pts": baseline_mean, "effect_vs_baseline_pts": effect,
        "atr_normalized_effect": atr_norm,
        "credible_vs_zero": bool(ci[0] > 0 or ci[1] < 0),
        "clears_cost_floor": clears_atr_floor and clears_absolute_floor,
        "avg_atr14": half_atr,
    }


def main():
    print("=" * 78)
    print("SCAN 004 -- EXPLORATORY SPLIT-SAMPLE ROBUSTNESS SCREEN (not confirmation)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="discovery_scan_004_split_sample_robustness.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame_v4(
        extend_state_frame_v3(extend_state_frame(build_state_frame(discovery), discovery)),
        discovery,
    )
    states_reset = states.reset_index()
    close = states_reset["Close"]
    rth_open = states_reset["rth_open"]
    absolute_cost_floor_pts = ABSOLUTE_COST_MULTIPLE * ROUND_TRIP_COST_POINTS

    mid = len(states_reset) // 2
    first_half = states_reset.iloc[:mid].reset_index(drop=True)
    second_half = states_reset.iloc[mid:].reset_index(drop=True)
    first_close, second_close = first_half["Close"], second_half["Close"]
    first_rth_open, second_rth_open = first_half["rth_open"], second_half["rth_open"]
    print(f"\nDiscovery total days: {len(states_reset)}  ->  first half: {len(first_half)}"
          f"  ({first_half['date'].iloc[0]} to {first_half['date'].iloc[-1]}),"
          f"  second half: {len(second_half)}"
          f"  ({second_half['date'].iloc[0]} to {second_half['date'].iloc[-1]})\n")

    results = []
    for cand in CANDIDATES:
        var, bucket = cand["state_var"], cand["bucket"]
        full_series = states_reset[var]
        valid = full_series.notna()
        edges = np.unique(np.nanpercentile(full_series[valid], [100 / 3, 200 / 3]))
        bin_edges = [-np.inf] + list(edges) + [np.inf]
        labels = BUCKET_LABELS[: len(bin_edges) - 1]
        if bucket not in labels:
            print(f"  {var}/{bucket}: bucket collapsed on full sample (degenerate edges), skipped.")
            continue

        first = score_half(first_half, first_close, first_rth_open, var, bucket, bin_edges, labels, absolute_cost_floor_pts)
        second = score_half(second_half, second_close, second_rth_open, var, bucket, bin_edges, labels, absolute_cost_floor_pts)

        direction_first = np.sign(first["effect_vs_baseline_pts"]) if not np.isnan(first["effect_vs_baseline_pts"]) else 0
        direction_second = np.sign(second["effect_vs_baseline_pts"]) if not np.isnan(second["effect_vs_baseline_pts"]) else 0
        direction_consistent = bool(direction_first != 0 and direction_first == direction_second)

        mag_ratio = None
        if not np.isnan(first["atr_normalized_effect"]) and first["atr_normalized_effect"] > 0:
            mag_ratio = second["atr_normalized_effect"] / first["atr_normalized_effect"] if not np.isnan(second["atr_normalized_effect"]) else None
        magnitude_consistent = bool(mag_ratio is not None and 0.4 <= mag_ratio <= 2.5)

        row = {
            "state_var": var, "bucket": bucket, "horizon": "intraday",
            "first_half": first, "second_half": second,
            "direction_consistent": direction_consistent,
            "magnitude_ratio_2nd_over_1st": mag_ratio,
            "magnitude_consistent": magnitude_consistent,
            "survives_both_halves": bool(first["credible_vs_zero"] and first["clears_cost_floor"]
                                          and second["credible_vs_zero"] and second["clears_cost_floor"]
                                          and direction_consistent),
            "mechanism_note": MECHANISM_NOTE.get(var, "Not previously used in this project."),
        }
        results.append(row)
        print(f"  {var}/{bucket}/h=intraday:")
        print(f"    first  half: n={first['n']:4d} effect_vs_baseline={first['effect_vs_baseline_pts']:+7.2f}pts "
              f"atr_norm={first['atr_normalized_effect']:.4f} credible={first['credible_vs_zero']} cost_ok={first['clears_cost_floor']}")
        print(f"    second half: n={second['n']:4d} effect_vs_baseline={second['effect_vs_baseline_pts']:+7.2f}pts "
              f"atr_norm={second['atr_normalized_effect']:.4f} credible={second['credible_vs_zero']} cost_ok={second['clears_cost_floor']}")
        print(f"    direction_consistent={direction_consistent}  magnitude_ratio(2nd/1st)={mag_ratio}  "
              f"magnitude_consistent={magnitude_consistent}  SURVIVES_BOTH_HALVES={row['survives_both_halves']}\n")

    out = {
        "screen": "discovery_scan_004_split_sample_robustness.py",
        "status": "EXPLORATORY -- internal-consistency check on the SAME selection sample, "
                  "NOT independent confirmation. Not logged to the ledger.",
        "candidates": results,
    }
    out_path = DATA_DIR / "discovery_scan_004_split_sample_robustness_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Full results written to {out_path}")


if __name__ == "__main__":
    main()
