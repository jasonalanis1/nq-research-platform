"""
discovery_scan_003_split_sample_robustness.py
================================================

EXPLORATORY ROBUSTNESS ANALYSIS -- not confirmation, not validation.
Second pass on Scan 003 (market_behavior_discovery_scan_003.py), same
method and same caveat as discovery_scan_001_split_sample_robustness.py:
the top candidates were SELECTED using the full Discovery sample, so
splitting that same sample in half does NOT produce independent
confirmation data -- it can only show whether an effect looks
internally consistent (same sign, similar magnitude) across two
non-overlapping sub-periods of the same selection sample. A candidate
that passes this screen still requires a full frozen spec, a Mechanism
pass, and a genuine out-of-sample Validation-slice prospective test
before it is anything more than "worth writing up." This script
freezes nothing and trades nothing.

METHOD: identical to the Scan 001 version -- bucket EDGES are the exact
ones fit on the FULL Discovery sample in Scan 003 (frozen, not refit
per half), Discovery is split at its chronological midpoint, each half
scored against its OWN baseline and its OWN average ATR(14).

CANDIDATES (top 3 unique (state_var, bucket) pairs from Scan 003,
deduped across horizon to each pair's single best-atr_norm horizon --
zn_level_vs_trailing/mid appeared at both h=3d [atr_norm 0.0525] and
h=10d [atr_norm 0.1097]; h=10d kept, h=3d dropped as the same
underlying effect at a shorter, highly autocorrelated horizon):
  - zn_level_vs_trailing / mid / h=10d   (atr_norm 0.1097, strongest)
  - zn_level_vs_trailing / low / h=10d   (atr_norm 0.0598)
  - opening_range_vs_atr / mid / h=1d    (atr_norm 0.0542, weakest --
    1-day horizon, the same timeframe this project's own diagnostic
    work (research/studies/effect-size-inflation-diagnostic-2026-09-08.md)
    has repeatedly found to be cost-dominated even when gross-positive)

HOW TO RUN:
    PYTHONPATH=src python3 src/discovery_scan_003_split_sample_robustness.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_state_primitives_v3 import extend_state_frame_v3

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
ATR_NORMALIZED_FLOOR = 0.05
BUCKET_LABELS = ["low", "mid", "high"]

CANDIDATES = [
    {"state_var": "zn_level_vs_trailing", "bucket": "mid", "horizon_days": 10},
    {"state_var": "zn_level_vs_trailing", "bucket": "low", "horizon_days": 10},
    {"state_var": "opening_range_vs_atr", "bucket": "mid", "horizon_days": 1},
]

MECHANISM_NOTE = {
    "zn_level_vs_trailing": (
        "New descriptor (market_state_primitives_v3.py). Mechanistically ambiguous on its face: "
        "the 'mid' bucket (ZN close near its own trailing average -- a range-bound/calm bond "
        "market) underperforms the Discovery-period's already-strong positive drift baseline, "
        "while BOTH extreme buckets (ZN meaningfully above or below its own trailing average -- "
        "a bond market moving sharply either direction) show stronger-than-baseline NQ drift. "
        "No single directional rates-vs-equities story explains a U-shape in the MIDDLE bucket "
        "specifically -- 'sharp bond moves either direction coincide with stronger equity drift, "
        "calm/range-bound bond markets coincide with weaker equity drift' is a volatility-regime "
        "story, not a rates-direction story, and was not the mechanism this descriptor was built "
        "to test (it mirrors vxn_level_vs_trailing's rates/vol-regime framing, not a directional "
        "rates bet -- see market_state_primitives_v3.py's docstring). Needs a real Mechanism-agent "
        "pass, not assumed here."
    ),
    "opening_range_vs_atr": (
        "Implemented since Scan 001, first scanned here. 1-day horizon -- this project's own "
        "cost-dominance diagnostic (research/studies/effect-size-inflation-diagnostic-2026-09-08.md) "
        "found many 1-day gross-positive effects do not survive round-trip costs at typical NQ risk "
        "distances; this candidate's atr_norm (0.0542) barely clears the 0.05 floor, which itself "
        "does not model actual trading costs, only a coarse ATR-relative-effect-size screen."
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


def forward_return(close_series, i, horizon):
    if i + horizon >= len(close_series):
        return None
    c0, c1 = close_series.iloc[i], close_series.iloc[i + horizon]
    if c0 <= 0:
        return None
    return float(c1 - c0)


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
    print("SCAN 003 -- EXPLORATORY SPLIT-SAMPLE ROBUSTNESS SCREEN (not confirmation)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="discovery_scan_003_split_sample_robustness.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame_v3(extend_state_frame(build_state_frame(discovery), discovery))
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

        row = {
            "state_var": var, "bucket": bucket, "horizon_days": horizon,
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
        print(f"  {var}/{bucket}/h={horizon}d:")
        print(f"    first  half: n={first['n']:4d} effect_vs_baseline={first['effect_vs_baseline_pts']:+7.2f}pts "
              f"atr_norm={first['atr_normalized_effect']:.4f} credible={first['credible_vs_zero']} cost_ok={first['clears_cost_floor']}")
        print(f"    second half: n={second['n']:4d} effect_vs_baseline={second['effect_vs_baseline_pts']:+7.2f}pts "
              f"atr_norm={second['atr_normalized_effect']:.4f} credible={second['credible_vs_zero']} cost_ok={second['clears_cost_floor']}")
        print(f"    direction_consistent={direction_consistent}  magnitude_ratio(2nd/1st)={mag_ratio}  "
              f"magnitude_consistent={magnitude_consistent}  SURVIVES_BOTH_HALVES={row['survives_both_halves']}\n")

    out = {
        "screen": "discovery_scan_003_split_sample_robustness.py",
        "status": "EXPLORATORY -- internal-consistency check on the SAME selection sample, "
                  "NOT independent confirmation. Not logged to the ledger.",
        "candidates": results,
    }
    out_path = DATA_DIR / "discovery_scan_003_split_sample_robustness_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Full results written to {out_path}")


if __name__ == "__main__":
    main()
