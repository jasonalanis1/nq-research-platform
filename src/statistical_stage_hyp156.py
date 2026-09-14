"""
STATISTICAL STAGE -- hyp-000156 (M23 / Entry 27: London FX session-open volatility
burst, 6E). UPGRADE QUEUE v3 item U2; run in the 2026-09-13 7:00 pm test cycle.

Reconstructs Scan 030's frozen construction exactly (research/mechanisms/
london-fx-open-6e-m23.md Section 9; src/market_behavior_discovery_scan_030.py):
per Discovery day, |return over 03:00-04:00 ET| / ATR14 (ATR14 = trailing-14 mean
of the 09:30-16:00 range), compared with the day's own unconditional hourly
|return| / ATR14 over 09:30-16:00. The per-day DIFF (London hour minus that day's
mean unconditional hour) is the series every question below is asked of, so the
null is the instrument's own behaviour, not zero.

Q1 stability      chronological halves of the diff series (block CI each)
Q2 regime         split by trailing-20d 6E range median (block CI each)
Q3 multiplicity   project_wide_multiplicity.evaluate at stage "discovery" --
                  the BINDING constraint (N_discovery = 451 today)
Q4 selection      alternative window definitions, reported only (03:00-03:30,
                  03:00-05:00, 02:30-03:30) -- the frozen cell stays 03:00-04:00
POWER             at the proposed review point = the one-shot Validation attempt:
                  n of Validation days with London bars (COUNT ONLY, no outcome
                  examined), power if the true effect equals / halves Discovery's

Block bootstrap block=10 (daily series), N_BOOT=3000, SEED=20260913, 90% CI.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data, get_validation_data  # noqa: E402
from baseline_relative import _block_means  # noqa: E402
import project_wide_multiplicity as pwm  # noqa: E402

ATR_WINDOW, BLOCK, N_BOOT, SEED = 14, 10, 3000, 20260913
Z90 = 1.2815515655446004
OUT_JSON = ROOT.parent / "data" / "statistical_stage_hyp156_results.json"
OUT_MD = ROOT.parent / "research" / "studies" / "hyp156-statistical-stage-2026-09-13.md"


def block_ci(v):
    v = np.asarray(v, dtype=float); v = v[np.isfinite(v)]
    if len(v) < BLOCK * 3:
        return float("nan"), float("nan")
    m = _block_means(v, BLOCK, N_BOOT, np.random.default_rng(SEED))
    return float(np.percentile(m, 5)), float(np.percentile(m, 95))


def summ(v):
    v = np.asarray(v, dtype=float); v = v[np.isfinite(v)]
    lo, hi = block_ci(v)
    return {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": [lo, hi],
            "credible_positive": bool(np.isfinite(lo) and lo > 0)}


def per_day_series(df, windows):
    """Returns DataFrame indexed by date with diff_<name> for each window and
    'trail_range' for the regime split."""
    rows = []
    for day, g in df.groupby(df.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if len(rth) < 200:
            continue
        rows.append({"date": pd.Timestamp(day), "rth_range": float(rth["High"].max() - rth["Low"].min())})
    if not rows:
        return pd.DataFrame(columns=["uncond", "trail_range"])
    daily = pd.DataFrame(rows).set_index("date").sort_index()
    daily["atr14"] = daily["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    daily["trail_range"] = daily["rth_range"].rolling(20, min_periods=20).mean().shift(1)
    atr_by = daily["atr14"].to_dict()
    out = []
    for day, g in df.groupby(df.index.date):
        ts = pd.Timestamp(day); atr = atr_by.get(ts)
        if atr is None or not np.isfinite(atr) or atr <= 0:
            continue
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if len(rth) < 200:
            continue
        # unconditional: mean |hourly return| over the RTH-equivalent session
        uncond = []
        for h in range(9, 16):
            hs, he = f"{h:02d}:30", f"{h + 1:02d}:30"
            sub = rth.between_time(hs, he, inclusive="left")
            if len(sub) >= 30:
                uncond.append(abs(float(sub["Close"].iloc[-1]) - float(sub["Open"].iloc[0])) / atr)
        if not uncond:
            continue
        rec = {"date": ts, "uncond": float(np.mean(uncond)), "trail_range": daily.loc[ts, "trail_range"]}
        ok = True
        for name, (a, b) in windows.items():
            w = g.between_time(a, b, inclusive="left")
            if w.empty:
                ok = False; break
            rec[f"diff_{name}"] = abs(float(w["Close"].iloc[-1]) - float(w["Open"].iloc[0])) / atr - rec["uncond"]
        if ok:
            out.append(rec)
    return pd.DataFrame(out).set_index("date").sort_index()


def main():
    print("=" * 78); print("STATISTICAL STAGE -- hyp-000156 (M23: London-open volatility burst, 6E)"); print("=" * 78)
    fx, syn = load_price_data(context="statistical_stage_hyp156.py", symbol="6E")
    if syn:
        print("ABORT: synthetic"); return
    disc = get_discovery_data(fx)
    windows = {"frozen_0300_0400": ("03:00", "04:00"), "alt_0300_0330": ("03:00", "03:30"),
               "alt_0300_0500": ("03:00", "05:00"), "alt_0230_0330": ("02:30", "03:30")}
    f = per_day_series(disc, windows)
    d = f["diff_frozen_0300_0400"].to_numpy()
    R = {"hypothesis_id": "hyp-000156", "map_anchor": "M23", "n_days": int(len(f)), "block": BLOCK, "seed": SEED}

    full = summ(d); R["full_sample"] = full
    print(f"Full sample: n={full['n']} mean diff={full['mean']:+.4f} ci_90=({full['ci_90'][0]:+.4f},{full['ci_90'][1]:+.4f}) credible={full['credible_positive']}")

    # Q1
    half = len(f) // 2
    R["Q1_stability"] = {"first_half": summ(d[:half]), "second_half": summ(d[half:])}
    q1 = R["Q1_stability"]["first_half"]["credible_positive"] and R["Q1_stability"]["second_half"]["credible_positive"]
    R["Q1_pass"] = bool(q1)
    print(f"Q1 halves: 1st {R['Q1_stability']['first_half']['mean']:+.4f} {R['Q1_stability']['first_half']['ci_90']} | 2nd {R['Q1_stability']['second_half']['mean']:+.4f} {R['Q1_stability']['second_half']['ci_90']} -> {'PASS' if q1 else 'FAIL'}")

    # Q2
    med = float(np.nanmedian(f["trail_range"]))
    lo_reg = f.loc[f["trail_range"] <= med, "diff_frozen_0300_0400"].to_numpy()
    hi_reg = f.loc[f["trail_range"] > med, "diff_frozen_0300_0400"].to_numpy()
    R["Q2_regime"] = {"low_vol_regime": summ(lo_reg), "high_vol_regime": summ(hi_reg), "median_trailing_range": med}
    q2 = R["Q2_regime"]["low_vol_regime"]["credible_positive"] and R["Q2_regime"]["high_vol_regime"]["credible_positive"]
    R["Q2_pass"] = bool(q2)
    print(f"Q2 regime: low {R['Q2_regime']['low_vol_regime']['mean']:+.4f} {R['Q2_regime']['low_vol_regime']['ci_90']} | high {R['Q2_regime']['high_vol_regime']['mean']:+.4f} {R['Q2_regime']['high_vol_regime']['ci_90']} -> {'PASS' if q2 else 'FAIL'}")

    # Q3 -- binding
    counts = pwm.compute_stage_trial_counts()
    v = pwm.evaluate("hyp-000156 London-open |ret| minus unconditional hourly |ret|, 6E", "discovery",
                     full["n"], full["mean"], tuple(full["ci_90"]), 0.0, counts)
    R["Q3_multiplicity"] = {"n_trials_discovery": v.n_trials, "raw_ci_90": list(v.single_test_ci_90),
                            "sidak_adjusted_ci": list(v.adjusted_ci), "survives": bool(v.survives_adjustment)}
    R["Q3_pass"] = bool(v.survives_adjustment)
    print(f"Q3 Sidak at N={v.n_trials}: raw {list(v.single_test_ci_90)} -> adjusted {list(v.adjusted_ci)} -> {'PASS' if v.survives_adjustment else 'FAIL'}")

    # Q4 -- selection sensitivity (reported, not gated)
    R["Q4_selection"] = {k: summ(f[f"diff_{k}"].to_numpy()) for k in windows}
    for k, s in R["Q4_selection"].items():
        print(f"Q4 {k:16s} mean={s['mean']:+.4f} ci={s['ci_90']} credible={s['credible_positive']}")
    R["Q4_note"] = "frozen window stays 03:00-04:00; alternates reported for sensitivity only, never selected"

    # POWER at the proposed review point (one-shot Validation) -- COUNT ONLY on Validation
    val = get_validation_data(fx)
    fv = per_day_series(val, {"frozen_0300_0400": ("03:00", "04:00")}) if len(val) else pd.DataFrame()
    n_val = int(len(fv))
    val_note = "" if n_val else f"6E data on disk spans {fx.index[0].date()}..{fx.index[-1].date()}; Validation slice has no usable days -- one-shot Validation is BLOCKED on data, not on the result"
    sd = float(np.nanstd(d, ddof=1)); dev = full["mean"]
    def power(true_dev, n):
        if n < 2: return float("nan")
        se = sd / math.sqrt(n); z = (Z90 * se - true_dev) / se
        return 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))
    R["power"] = {"validation_n_days_count_only": n_val, "sd_discovery_diff": sd,
                  "power_if_true_equals_discovery": power(dev, n_val), "power_if_half": power(dev / 2, n_val),
                  "validation_data_touched": "COUNT ONLY -- number of Validation days with London bars; no outcome examined", "note": val_note}
    print(f"POWER: Validation n={n_val} (count only); sd={sd:.4f}; power at Discovery dev {dev:+.4f}: {R['power']['power_if_true_equals_discovery']:.2f}; at half: {R['power']['power_if_half']:.2f}")

    R["verdict"] = "PASS" if (q1 and q2 and v.survives_adjustment) else ("FAIL_Q3_ONLY" if (q1 and q2) else "FAIL")
    OUT_JSON.write_text(json.dumps(R, indent=2, default=str))

    md = [f"# Statistical stage — hyp-000156 (M23 London-open volatility burst, 6E)", "",
          "Run September 13th, 7:00 pm CT test cycle (U2). Construction reproduced from Scan 030 exactly; the per-day",
          "series is London-hour |return|/ATR14 minus that day's mean unconditional hourly |return|/ATR14 — the null",
          "is the instrument's own behaviour, not zero. Block bootstrap block=10, N=3000, seed 20260913, 90% CI.", "",
          f"**Full sample:** n={full['n']}, mean diff {full['mean']:+.4f} ATR, ci_90 ({full['ci_90'][0]:+.4f}, {full['ci_90'][1]:+.4f}).", "",
          "| Question | Result | Pass |", "|---|---|---|",
          f"| Q1 stability (chronological halves) | 1st {R['Q1_stability']['first_half']['mean']:+.4f} {R['Q1_stability']['first_half']['ci_90']} · 2nd {R['Q1_stability']['second_half']['mean']:+.4f} {R['Q1_stability']['second_half']['ci_90']} | {'PASS' if q1 else 'FAIL'} |",
          f"| Q2 regime (trailing-20d range median) | low-vol {R['Q2_regime']['low_vol_regime']['mean']:+.4f} {R['Q2_regime']['low_vol_regime']['ci_90']} · high-vol {R['Q2_regime']['high_vol_regime']['mean']:+.4f} {R['Q2_regime']['high_vol_regime']['ci_90']} | {'PASS' if q2 else 'FAIL'} |",
          f"| Q3 multiplicity (Šidák, N_discovery={v.n_trials}, BINDING) | raw {[round(x,4) for x in v.single_test_ci_90]} → adjusted {[round(x,4) for x in v.adjusted_ci]} | {'PASS' if v.survives_adjustment else 'FAIL'} |",
          f"| Q4 selection sensitivity (reported) | " + "; ".join(f"{k} {s['mean']:+.4f} {'cred' if s['credible_positive'] else 'n/c'}" for k, s in R['Q4_selection'].items()) + " | reported |",
          f"| Power at one-shot Validation | n={n_val} days (count only), power {R['power']['power_if_true_equals_discovery']:.2f} at Discovery effect, {R['power']['power_if_half']:.2f} at half | — |",
          "", f"**Verdict: {R['verdict']}**", ""]
    if R["verdict"] == "FAIL_Q3_ONLY":
        md += ["**This is the Šidák policy case named in research/studies/sidak-stacking-diagnosis-2026-09-13.md:** the raw",
               "Discovery CI is clean and both stability questions pass, but the project-wide Discovery correction at",
               f"N={v.n_trials} closes it before Validation — the stage designed to judge exactly this — can. Not silently",
               "closed: the bar-change decision is Jason's, and this candidate is the concrete example.", ""]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md))
    print("VERDICT:", R["verdict"])


if __name__ == "__main__":
    main()
