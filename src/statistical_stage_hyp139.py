"""
statistical_stage_hyp139.py
=============================

Statistical stage for hyp-000139 (overnight-vs-RTH return divergence,
HIGH tercile, mean-reversion). Per NEXT_UP.md queue item 0 and the
AGENT PROTOCOL: the 4 Statistical questions (stability, regime
dependence, magnitude, selection sensitivity) plus mandatory same-data
selection disclosure, plus the mechanism doc's own P1-P3 predictions
(research/mechanisms/overnight-rth-divergence-reversion-high-tercile.md).

Scope: Discovery-stage data only (2015-01-01 -> 2021-10-03). hyp-000139
has never been run on Validation -- this is still pre-Validation
robustness work on the SAME Discovery sample Scan 008 used, consistent
with how this project's Statistical stage has been run before
(research/studies/statistical-stage-pass-2026-09-10.md ran on
Discovery+Validation because those 3 candidates already had Validation
results; hyp-000139 does not, so Discovery only, to avoid touching
Validation before this candidate has cleared Triage/Statistical/
Director Re-Eval/Monetization/Integrity in order).

Frozen from Scan 008 / idea_inventory.md Entry 3 (no retuning):
  - state variable: trailing 20-day cumulative overnight-minus-RTH
    signed return divergence, ATR-normalized, terciled.
  - outcome: today's own overnight-minus-RTH divergence, ATR-normalized.
  - candidate cell: HIGH tercile only (the one credible cell).

HOW TO RUN:
    PYTHONPATH=src python3 statistical_stage_hyp139.py
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
import project_wide_multiplicity as pwm

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = Path("/home/claude").parent  # placeholder, overwritten below
N_BOOTSTRAP = 3000
RANDOM_SEED = 8
LOOKBACK_DAYS = 20


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


def summarize(values):
    n = len(values)
    if n < 2:
        return {"n": n, "mean": float("nan"), "ci_90": [float("nan"), float("nan")], "credible": False}
    ci = bootstrap_mean_ci(values)
    credible = ci[0] > 0 or ci[1] < 0
    return {"n": n, "mean": float(np.mean(values)), "ci_90": list(ci), "credible": bool(credible)}


def build_frame(discovery, states, lookback=LOOKBACK_DAYS):
    rth = _rth_daily_ohlc(discovery)
    rth = rth.reindex(states.index)
    atr14 = states["atr14"]
    prior_close = rth["rth_close"].shift(1)
    overnight_return_atr = (rth["rth_open"] - prior_close) / atr14
    rth_return_atr = (rth["rth_close"] - rth["rth_open"]) / atr14
    daily_divergence = overnight_return_atr - rth_return_atr
    trailing_divergence = daily_divergence.rolling(
        lookback, min_periods=lookback).sum().shift(1)
    out = pd.DataFrame({
        "daily_divergence": daily_divergence,
        "trailing_divergence": trailing_divergence,
        "overnight_return_atr": overnight_return_atr,
        "rth_return_atr": rth_return_atr,
        "volume_vs_expected": states["volume_vs_expected"],
        "atr14": atr14,
    })
    return out


def main():
    print("=" * 78)
    print("STATISTICAL STAGE -- hyp-000139 (overnight-vs-RTH divergence, HIGH tercile)")
    print("=" * 78)

    df, is_synthetic = load_price_data(context="statistical_stage_hyp139.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(discovery), discovery)
    frame = build_frame(discovery, states)
    frame = frame.dropna(subset=["trailing_divergence", "daily_divergence"]).copy()
    print(f"Discovery RTH-days with valid trailing-divergence state: {len(frame)}")

    frame["tercile"] = pd.qcut(frame["trailing_divergence"], 3, labels=["low", "mid", "high"])
    high = frame[frame["tercile"] == "high"].copy()
    baseline = summarize(high["daily_divergence"].tolist())
    print(f"\nBaseline (frozen, full Discovery sample) HIGH tercile: n={baseline['n']} "
          f"mean={baseline['mean']:.4f} ci_90={baseline['ci_90']} credible={baseline['credible']}")

    results = {"baseline": baseline}

    # -------------------- Q1: STABILITY (chronological split) --------------------
    print("\n--- Q1: Stability (chronological split-sample) ---")
    mid_idx = len(frame) // 2
    split_date = frame.index[mid_idx]
    first_half = frame.iloc[:mid_idx]
    second_half = frame.iloc[mid_idx:]
    q1 = {}
    for label, half in [("first_half", first_half), ("second_half", second_half)]:
        sub = half[half["tercile"] == "high"]
        s = summarize(sub["daily_divergence"].tolist())
        q1[label] = s
        print(f"  {label}: n={s['n']} mean={s['mean']:.4f} ci_90={s['ci_90']} credible={s['credible']}")
    same_sign = (q1["first_half"]["mean"] < 0) == (q1["second_half"]["mean"] < 0)
    both_credible = q1["first_half"]["credible"] and q1["second_half"]["credible"]
    q1["split_date"] = str(split_date)
    q1["same_sign"] = bool(same_sign)
    q1["both_halves_credible"] = bool(both_credible)
    print(f"  same sign: {same_sign}  both halves credible: {both_credible}  split at {split_date}")
    results["q1_stability"] = q1

    # -------------------- Q2: REGIME DEPENDENCE (ATR median split) --------------------
    print("\n--- Q2: Regime dependence (trailing ATR14 median split) ---")
    atr_median = frame["atr14"].median()
    q2 = {}
    for label, cond in [("low_vol", frame["atr14"] <= atr_median), ("high_vol", frame["atr14"] > atr_median)]:
        sub = frame[cond & (frame["tercile"] == "high")]
        s = summarize(sub["daily_divergence"].tolist())
        q2[label] = s
        print(f"  {label}: n={s['n']} mean={s['mean']:.4f} ci_90={s['ci_90']} credible={s['credible']}")
    q2["atr_median"] = float(atr_median)
    concentrated = q2["low_vol"]["credible"] != q2["high_vol"]["credible"]
    q2["concentrated_in_one_regime"] = bool(concentrated)
    print(f"  concentrated in one regime only: {concentrated}")
    results["q2_regime"] = q2

    # -------------------- Q3: MAGNITUDE (multiplicity-corrected) --------------------
    print("\n--- Q3: Magnitude (project-wide multiplicity correction) ---")
    trial_counts = pwm.compute_stage_trial_counts()
    verdict = pwm.evaluate(
        label="hyp-000139_high_tercile", stage="discovery",
        n_obs=baseline["n"], mean=baseline["mean"], ci_90=tuple(baseline["ci_90"]),
        null_value=0.0, stage_trial_counts=trial_counts,
    )
    atr_norm_dev = abs(baseline["mean"])
    q3 = {
        "n_discovery_trials": trial_counts["discovery"],
        "raw_ci_90": baseline["ci_90"],
        "adjusted_ci": list(verdict.adjusted_ci),
        "survives_adjustment": bool(verdict.survives_adjustment),
        "abs_mean_atr_units": float(atr_norm_dev),
        "clears_005_floor": bool(atr_norm_dev >= 0.05),
    }
    print(f"  discovery-stage trial count: {trial_counts['discovery']}")
    print(f"  raw CI: {baseline['ci_90']}  adjusted CI: {verdict.adjusted_ci}  survives: {verdict.survives_adjustment}")
    print(f"  |mean| = {atr_norm_dev:.4f} ATR units, clears 0.05 floor: {atr_norm_dev >= 0.05}")
    results["q3_magnitude"] = q3

    # -------------------- Q4: SELECTION SENSITIVITY (tercile boundary) --------------------
    print("\n--- Q4: Selection sensitivity (bucket width around frozen terciles) ---")
    q4 = {}
    for pct, label in [(20, "quintile_80_20"), (33.33, "tercile_frozen"), (25, "quartile_75_25")]:
        thresh = frame["trailing_divergence"].quantile(1 - pct / 100)
        sub = frame[frame["trailing_divergence"] >= thresh]
        s = summarize(sub["daily_divergence"].tolist())
        q4[label] = s
        print(f"  top {pct}%: n={s['n']} mean={s['mean']:.4f} ci_90={s['ci_90']} credible={s['credible']}")
    results["q4_selection_sensitivity"] = q4

    # -------------------- Same-data selection disclosure --------------------
    disclosure = (
        "The 20-day lookback window, the tercile cut, and the HIGH-tercile-only "
        "focus were all fixed by Scan 008 / idea_inventory.md Entry 3 BEFORE this "
        "candidate's Discovery result was seen (single pre-registered shot: 3 "
        "cells, 2 mutually exclusive predictions). This Statistical-stage script "
        "reuses that same frozen state variable, outcome variable, and tercile "
        "cut unmodified for Q1/Q2/Q3. Q4 deliberately varies the selection "
        "threshold (20% vs 33.33% vs 25%) but that is diagnostic, not a retune -- "
        "the frozen 33.33% (tercile) result is what is being scored, never the "
        "best-looking alternative."
    )
    results["same_data_selection_disclosure"] = disclosure
    print(f"\nDisclosure: {disclosure}")

    # -------------------- Mechanism doc P1/P2/P3 --------------------
    print("\n--- Mechanism-doc predictions (P1-P3) ---")
    p_results = {}

    # P1: overnight-driven vs RTH-driven subgroup split within HIGH tercile.
    # "overnight-driven": overnight leg's |z| contribution dominates; "RTH-driven": RTH leg dominates.
    high2 = high.copy()
    high2["overnight_abs"] = high2["overnight_return_atr"].abs()
    high2["rth_abs"] = high2["rth_return_atr"].abs()
    overnight_driven = high2[high2["overnight_abs"] > high2["rth_abs"]]
    rth_driven = high2[high2["overnight_abs"] <= high2["rth_abs"]]
    s_on = summarize(overnight_driven["daily_divergence"].tolist())
    s_rth = summarize(rth_driven["daily_divergence"].tolist())
    print(f"  P1 overnight-driven subgroup: n={s_on['n']} mean={s_on['mean']:.4f} ci_90={s_on['ci_90']} credible={s_on['credible']}")
    print(f"  P1 RTH-driven subgroup:       n={s_rth['n']} mean={s_rth['mean']:.4f} ci_90={s_rth['ci_90']} credible={s_rth['credible']}")
    p1_same_sign = (s_on["mean"] < 0) == (s_rth["mean"] < 0)
    p1_both_credible = s_on["credible"] and s_rth["credible"]
    p_results["p1_overnight_vs_rth_driven"] = {
        "overnight_driven": s_on, "rth_driven": s_rth,
        "same_sign": bool(p1_same_sign), "both_credible": bool(p1_both_credible),
        "supports_mechanical_reversion": bool(p1_same_sign and p1_both_credible),
    }

    # P2: window-length generalization (10d, 30d)
    p2 = {}
    for w in [10, 30]:
        fr_w = build_frame(discovery, states, lookback=w)
        fr_w = fr_w.dropna(subset=["trailing_divergence", "daily_divergence"]).copy()
        fr_w["tercile"] = pd.qcut(fr_w["trailing_divergence"], 3, labels=["low", "mid", "high"])
        sub = fr_w[fr_w["tercile"] == "high"]
        s = summarize(sub["daily_divergence"].tolist())
        p2[f"window_{w}d"] = s
        print(f"  P2 window={w}d HIGH tercile: n={s['n']} mean={s['mean']:.4f} ci_90={s['ci_90']} credible={s['credible']}")
    p2_generalizes = all(p2[k]["credible"] and p2[k]["mean"] < 0 for k in p2)
    p_results["p2_window_generalization"] = {**p2, "generalizes_same_sign_and_credible": bool(p2_generalizes)}
    print(f"  P2 generalizes (both 10d/30d credible, same sign as 20d): {p2_generalizes}")

    # P3: volume-conditioned reversion strength within HIGH tercile
    low_vol = high[high["volume_vs_expected"] < high["volume_vs_expected"].median()]
    high_vol = high[high["volume_vs_expected"] >= high["volume_vs_expected"].median()]
    s_lowvol = summarize(low_vol["daily_divergence"].tolist())
    s_highvol = summarize(high_vol["daily_divergence"].tolist())
    print(f"  P3 low-volume subset:  n={s_lowvol['n']} mean={s_lowvol['mean']:.4f} ci_90={s_lowvol['ci_90']} credible={s_lowvol['credible']}")
    print(f"  P3 high-volume subset: n={s_highvol['n']} mean={s_highvol['mean']:.4f} ci_90={s_highvol['ci_90']} credible={s_highvol['credible']}")
    p3_volume_independent = s_lowvol["credible"] and s_highvol["credible"] and \
        (abs(s_lowvol["mean"]) >= 0.5 * abs(s_highvol["mean"]))
    p_results["p3_volume_conditioning"] = {
        "low_volume": s_lowvol, "high_volume": s_highvol,
        "volume_independent": bool(p3_volume_independent),
    }
    print(f"  P3 volume-independence (mechanical story predicts yes): {p3_volume_independent}")

    results["mechanism_predictions"] = p_results

    out_path = Path("research") / "studies"
    out_json = Path("data") / "statistical_stage_hyp139_results.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nWritten: {out_json}")
    return results


if __name__ == "__main__":
    main()
