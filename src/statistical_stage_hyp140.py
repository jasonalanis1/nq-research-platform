"""
statistical_stage_hyp140.py
=============================

Statistical stage for hyp-000140 (|gap_vs_atr| magnitude, same-day RTH
range). Per the standing 4 Statistical questions (stability, regime
dependence, magnitude, selection sensitivity) plus mandatory same-data
selection disclosure, plus the mechanism doc's own P1-P3 predictions
(research/mechanisms/abs-gap-vs-atr-same-day-range-magnitude.md).

Scope: Discovery-stage data only (2015-01-01 -> 2021-10-03), the same
sample Scan 010 used. hyp-000140 has never touched Validation.

Frozen from Scan 010 / idea_inventory.md Entry 5 (no retuning):
  - state variable: abs(gap_vs_atr), terciled.
  - outcome: same-day RTH range vs trailing-20d average RTH range.
  - candidate cells: LOW (compression) and HIGH (elevation) terciles,
    both credible in Scan 010; MID is the non-gating null middle cell.

HOW TO RUN:
    PYTHONPATH=src python3 statistical_stage_hyp140.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")

from data_loader import load_price_data
from data_split import get_discovery_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_state_primitives_v4 import _rth_daily_ohlc
from market_behavior_discovery_scan_007 import build_rth_range_frame
import project_wide_multiplicity as pwm

N_BOOTSTRAP = 3000
RANDOM_SEED = 9


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


def summarize(values, null_value=1.0):
    n = len(values)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": [float("nan"), float("nan")], "credible": False}
    ci = bootstrap_mean_ci(values)
    credible = ci[0] > null_value or ci[1] < null_value
    return {"n": n, "mean": float(np.mean(values)), "ci_90": list(ci), "credible": bool(credible)}


def first_hour_close_by_day(df: pd.DataFrame) -> dict:
    """First 60 minutes of RTH (09:30-10:30) close price per day, for
    the gap validated-vs-faded split (mechanism doc P1)."""
    out = {}
    idx = df.index
    for day, day_df in df.groupby(idx.date):
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty:
            continue
        first_hour = rth.iloc[:60]
        if first_hour.empty:
            continue
        out[day] = float(first_hour["Close"].iloc[-1])
    return out


def build_gap_range_frame(discovery, lookback=20):
    """abs(gap_vs_atr) terciled + same-day RTH range vs trailing avg,
    the exact Scan 010 construction, plus rth_open/rth_close/gap_sign
    for the P1 validated-vs-faded split."""
    rth = build_rth_range_frame(discovery)
    rth = rth.dropna(subset=["trailing_avg_rth_range"]).copy()
    rth["ratio"] = rth["rth_range"] / rth["trailing_avg_rth_range"]

    states = extend_state_frame(build_state_frame(discovery), discovery)
    states = states[["gap_vs_atr", "volume_vs_expected"]].copy()
    states["abs_gap_vs_atr"] = states["gap_vs_atr"].abs()

    labeled = rth.join(states, how="inner")
    labeled = labeled.dropna(subset=["abs_gap_vs_atr"])
    return labeled


def main():
    print("=" * 78)
    print("STATISTICAL STAGE -- hyp-000140 (|gap_vs_atr| magnitude, same-day RTH range)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="statistical_stage_hyp140.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    labeled = build_gap_range_frame(discovery)
    print(f"Discovery RTH-days with valid gap/trailing-range state: {len(labeled)}")

    # Frozen tercile edges, same as Scan 010 -- cut fresh on THIS sample
    # (same sample as Scan 010, so the same edges, re-derived not reused
    # verbatim to keep this script self-contained).
    edges = np.nanpercentile(labeled["abs_gap_vs_atr"], [100 / 3, 200 / 3])
    bin_edges = [-np.inf, edges[0], edges[1], np.inf]
    labeled["bucket"] = pd.cut(labeled["abs_gap_vs_atr"], bins=bin_edges, labels=["low", "mid", "high"])

    low = labeled[labeled["bucket"] == "low"].copy()
    high = labeled[labeled["bucket"] == "high"].copy()
    baseline_low = summarize(low["ratio"].tolist())
    baseline_high = summarize(high["ratio"].tolist())
    print(f"\nBaseline (frozen, full Discovery sample):")
    print(f"  LOW:  n={baseline_low['n']} mean={baseline_low['mean']:.4f} ci_90={baseline_low['ci_90']} credible={baseline_low['credible']}")
    print(f"  HIGH: n={baseline_high['n']} mean={baseline_high['mean']:.4f} ci_90={baseline_high['ci_90']} credible={baseline_high['credible']}")

    results = {"baseline": {"low": baseline_low, "high": baseline_high}}

    # -------------------- Q1: STABILITY (chronological split) --------------------
    print("\n--- Q1: Stability (chronological split-sample) ---")
    mid_idx = len(labeled) // 2
    split_date = labeled.index[mid_idx]
    first_half = labeled.iloc[:mid_idx]
    second_half = labeled.iloc[mid_idx:]
    q1 = {}
    for cell in ["low", "high"]:
        q1[cell] = {}
        for label, half in [("first_half", first_half), ("second_half", second_half)]:
            sub = half[half["bucket"] == cell]
            s = summarize(sub["ratio"].tolist())
            q1[cell][label] = s
            print(f"  {cell}/{label}: n={s['n']} mean={s['mean']:.4f} ci_90={s['ci_90']} credible={s['credible']}")
        same_sign = (q1[cell]["first_half"]["mean"] < 1.0) == (q1[cell]["second_half"]["mean"] < 1.0)
        both_credible = q1[cell]["first_half"]["credible"] and q1[cell]["second_half"]["credible"]
        q1[cell]["same_sign"] = bool(same_sign)
        q1[cell]["both_halves_credible"] = bool(both_credible)
        print(f"  {cell}: same sign={same_sign}  both halves credible={both_credible}")
    q1["split_date"] = str(split_date)
    results["q1_stability"] = q1

    # -------------------- Q2: REGIME DEPENDENCE (trailing ATR median split) --------------------
    print("\n--- Q2: Regime dependence (trailing avg RTH range median split) ---")
    range_median = labeled["trailing_avg_rth_range"].median()
    q2 = {}
    for cell in ["low", "high"]:
        q2[cell] = {}
        for label, cond in [("low_vol_regime", labeled["trailing_avg_rth_range"] <= range_median),
                             ("high_vol_regime", labeled["trailing_avg_rth_range"] > range_median)]:
            sub = labeled[cond & (labeled["bucket"] == cell)]
            s = summarize(sub["ratio"].tolist())
            q2[cell][label] = s
            print(f"  {cell}/{label}: n={s['n']} mean={s['mean']:.4f} ci_90={s['ci_90']} credible={s['credible']}")
        concentrated = q2[cell]["low_vol_regime"]["credible"] != q2[cell]["high_vol_regime"]["credible"]
        q2[cell]["concentrated_in_one_regime"] = bool(concentrated)
        print(f"  {cell}: concentrated in one regime only: {concentrated}")
    q2["range_median"] = float(range_median)
    results["q2_regime"] = q2

    # -------------------- Q3: MAGNITUDE (multiplicity-corrected) --------------------
    print("\n--- Q3: Magnitude (project-wide multiplicity correction) ---")
    trial_counts = pwm.compute_stage_trial_counts()
    q3 = {"n_discovery_trials": trial_counts["discovery"]}
    for cell, baseline in [("low", baseline_low), ("high", baseline_high)]:
        verdict = pwm.evaluate(
            label=f"hyp-000140_{cell}_tercile", stage="discovery",
            n_obs=baseline["n"], mean=baseline["mean"], ci_90=tuple(baseline["ci_90"]),
            null_value=1.0, stage_trial_counts=trial_counts,
        )
        dev = abs(baseline["mean"] - 1.0)
        q3[cell] = {
            "raw_ci_90": baseline["ci_90"],
            "adjusted_ci": list(verdict.adjusted_ci),
            "survives_adjustment": bool(verdict.survives_adjustment),
            "abs_deviation_from_1": float(dev),
            "clears_005_floor": bool(dev >= 0.05),
        }
        print(f"  {cell}: raw CI={baseline['ci_90']}  adjusted CI={verdict.adjusted_ci}  "
              f"survives={verdict.survives_adjustment}  |dev from 1.0|={dev:.4f}  clears 0.05 floor={dev >= 0.05}")
    results["q3_magnitude"] = q3

    # -------------------- Q4: SELECTION SENSITIVITY (bucket width) --------------------
    print("\n--- Q4: Selection sensitivity (bucket width around frozen terciles) ---")
    q4 = {}
    for pct, label in [(20, "quintile_80_20"), (33.33, "tercile_frozen"), (25, "quartile_75_25")]:
        thresh_high = labeled["abs_gap_vs_atr"].quantile(1 - pct / 100)
        thresh_low = labeled["abs_gap_vs_atr"].quantile(pct / 100)
        sub_high = labeled[labeled["abs_gap_vs_atr"] >= thresh_high]
        sub_low = labeled[labeled["abs_gap_vs_atr"] <= thresh_low]
        s_high = summarize(sub_high["ratio"].tolist())
        s_low = summarize(sub_low["ratio"].tolist())
        q4[label] = {"top": s_high, "bottom": s_low}
        print(f"  {label}: top {pct}% n={s_high['n']} mean={s_high['mean']:.4f} credible={s_high['credible']}"
              f"  |  bottom {pct}% n={s_low['n']} mean={s_low['mean']:.4f} credible={s_low['credible']}")
    results["q4_selection_sensitivity"] = q4

    # -------------------- Same-data selection disclosure --------------------
    disclosure = (
        "The abs(gap_vs_atr) state variable, the RTH-range-vs-trailing-20d-avg "
        "outcome, and the tercile cut were all fixed by Scan 010 / idea_inventory.md "
        "Entry 5 BEFORE this candidate's Discovery result was seen (single "
        "pre-registered shot: 3 cells, 2 mutually exclusive predictions). This "
        "Statistical-stage script reuses that same frozen state variable, outcome "
        "variable, and tercile cut unmodified for Q1/Q2/Q3. Q4 deliberately varies "
        "the selection threshold (20% vs 33.33% vs 25%) but that is diagnostic, not "
        "a retune -- the frozen 33.33% (tercile) result is what is being scored, "
        "never the best-looking alternative."
    )
    results["same_data_selection_disclosure"] = disclosure
    print(f"\nDisclosure: {disclosure}")

    # -------------------- Mechanism doc P1/P2/P3 --------------------
    print("\n--- Mechanism-doc predictions (P1-P3) ---")
    p_results = {}

    # P1: gap validated-vs-faded split within HIGH tercile. "Validated":
    # first-RTH-hour close continues in the gap's direction; "faded":
    # first-RTH-hour close moves opposite the gap's direction.
    fh_close = first_hour_close_by_day(discovery)
    rth_daily = _rth_daily_ohlc(discovery)
    high2 = high.copy()
    high2["first_hour_close"] = pd.Series(fh_close).reindex(high2.index)
    high2["rth_open"] = rth_daily["rth_open"].reindex(high2.index)
    high2 = high2.dropna(subset=["first_hour_close", "rth_open"])
    gap_sign = np.sign(high2["gap_vs_atr"])
    first_hour_move_sign = np.sign(high2["first_hour_close"] - high2["rth_open"])
    validated = high2[first_hour_move_sign == gap_sign]
    faded = high2[first_hour_move_sign != gap_sign]
    s_validated = summarize(validated["ratio"].tolist())
    s_faded = summarize(faded["ratio"].tolist())
    print(f"  P1 validated subgroup: n={s_validated['n']} mean={s_validated['mean']:.4f} ci_90={s_validated['ci_90']} credible={s_validated['credible']}")
    print(f"  P1 faded subgroup:     n={s_faded['n']} mean={s_faded['mean']:.4f} ci_90={s_faded['ci_90']} credible={s_faded['credible']}")
    p1_concentrated_in_validated = s_validated["credible"] and (
        not s_faded["credible"] or s_validated["mean"] > s_faded["mean"])
    p_results["p1_validated_vs_faded"] = {
        "validated": s_validated, "faded": s_faded,
        "concentrated_in_validated": bool(p1_concentrated_in_validated),
    }
    print(f"  P1 elevation concentrated in validated subgroup: {p1_concentrated_in_validated}")

    # P2: full volume-tercile x gap-tercile grid (monotonic amplification check)
    print("\n  P2 volume x gap-magnitude grid:")
    vol_edges = np.nanpercentile(labeled["volume_vs_expected"].dropna(), [100 / 3, 200 / 3])
    labeled["vol_bucket"] = pd.cut(labeled["volume_vs_expected"],
                                    bins=[-np.inf, vol_edges[0], vol_edges[1], np.inf],
                                    labels=["low", "mid", "high"])
    p2 = {}
    for gap_cell in ["low", "high"]:
        p2[gap_cell] = {}
        for vol_cell in ["low", "mid", "high"]:
            sub = labeled[(labeled["bucket"] == gap_cell) & (labeled["vol_bucket"] == vol_cell)]
            s = summarize(sub["ratio"].tolist())
            p2[gap_cell][vol_cell] = s
            print(f"    gap={gap_cell} vol={vol_cell}: n={s['n']} mean={s['mean']:.4f} credible={s['credible']}")
    high_means = [p2["high"][v]["mean"] for v in ["low", "mid", "high"]]
    low_means = [p2["low"][v]["mean"] for v in ["low", "mid", "high"]]
    high_monotonic = all(high_means[i] <= high_means[i + 1] for i in range(len(high_means) - 1))
    low_monotonic = all(low_means[i] >= low_means[i + 1] for i in range(len(low_means) - 1))
    p_results["p2_volume_gap_grid"] = {
        **p2,
        "high_gap_monotonic_increasing_with_volume": bool(high_monotonic),
        "low_gap_monotonic_decreasing_with_volume": bool(low_monotonic),
        "symmetric_amplification": bool(high_monotonic and low_monotonic),
    }
    print(f"  P2 HIGH-gap monotonic increasing with volume: {high_monotonic}")
    print(f"  P2 LOW-gap monotonic decreasing with volume: {low_monotonic}")
    print(f"  P2 symmetric amplification (both sides): {high_monotonic and low_monotonic}")

    # P3: volume-tercile re-cut of the existing P3 median split (HIGH gap only)
    print("\n  P3 volume-tercile re-cut (HIGH-gap cell only):")
    p3 = {}
    for vol_cell in ["low", "mid", "high"]:
        sub = high[high["volume_vs_expected"].notna()]
        sub = sub.join(labeled["vol_bucket"])
        sub = sub[sub["vol_bucket"] == vol_cell] if "vol_bucket" in sub.columns else sub
        s = summarize(sub["ratio"].tolist())
        p3[vol_cell] = s
        print(f"    vol={vol_cell}: n={s['n']} mean={s['mean']:.4f} ci_90={s['ci_90']} credible={s['credible']}")
    p3_means = [p3[v]["mean"] for v in ["low", "mid", "high"]]
    p3_monotonic = all(p3_means[i] <= p3_means[i + 1] for i in range(len(p3_means) - 1))
    p_results["p3_volume_tercile_recut"] = {**p3, "monotonic_increasing": bool(p3_monotonic)}
    print(f"  P3 monotonic ordering preserved under finer (tercile) cut: {p3_monotonic}")

    results["mechanism_predictions"] = p_results

    out_json = Path("data") / "statistical_stage_hyp140_results.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nWritten: {out_json}")
    return results


if __name__ == "__main__":
    main()
