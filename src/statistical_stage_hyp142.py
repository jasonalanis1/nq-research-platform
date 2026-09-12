"""Statistical stage -- hyp-000142 (vxn_level_vs_trailing HIGH -> next-session
RTH range, Scan 014 / Entry 8 / map M7). Same four questions as
statistical_stage_hyp140.py plus AMENDMENT v2.5's POWER check at the
proposed Validation review point, plus the disentangling the mechanism doc's
P4 result demands (VXN partly mirrors yesterday's realized range).

Q1 stability (chronological halves) · Q2 regime (trailing-range median) ·
Q3 magnitude under project-wide Sidak (project_wide_multiplicity.evaluate,
the binding constraint) · Q4 selection sensitivity (quintile/tercile/
quartile) · POWER at the Validation slice's expected n · P4-disentangle:
residualise the outcome on BOTH overnight_range_vs_atr and range_vs_atr
terciles and re-measure the HIGH-LOW spread.

Frozen construction from Scan 014, nothing retuned. Discovery data only.
HOW TO RUN: PYTHONPATH=src python3 src/statistical_stage_hyp142.py
"""
import json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import load_price_data
from data_split import get_discovery_data, get_validation_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
from market_behavior_discovery_scan_007 import build_rth_range_frame
import project_wide_multiplicity as pwm

OUT = Path(__file__).resolve().parent.parent / "data" / "statistical_stage_hyp142_results.json"
N_BOOT, SEED = 3000, 7
Z90 = 1.2815515655446004


def ci(vals):
    v = np.asarray([x for x in vals if not (isinstance(x, float) and np.isnan(x))], dtype=float)
    if len(v) < 2: return float("nan"), float("nan")
    rng = np.random.default_rng(SEED)
    m = rng.choice(v, size=(N_BOOT, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(m, 5)), float(np.percentile(m, 95))


def summ(vals, null=1.0):
    vals = list(vals); n = len(vals)
    if n < 2: return {"n": n, "mean": float("nan"), "ci_90": [float("nan")] * 2, "credible": False}
    lo, hi = ci(vals); m = float(np.mean(vals))
    return {"n": n, "mean": m, "ci_90": [lo, hi], "credible": bool(lo > null or hi < null)}


def frame(df):
    rth = build_rth_range_frame(df).dropna(subset=["trailing_avg_rth_range"]).copy()
    rth["ratio"] = rth["rth_range"] / rth["trailing_avg_rth_range"]
    st = extend_state_frame(build_state_frame(df), df)[["vxn_level_vs_trailing", "overnight_range_vs_atr", "range_vs_atr"]]
    return rth.join(st, how="inner").dropna(subset=["vxn_level_vs_trailing", "ratio"]).copy()


def main():
    print("=" * 78); print("STATISTICAL STAGE -- hyp-000142 (vxn_level_vs_trailing HIGH -> next-session RTH range)"); print("=" * 78)
    df, syn = load_price_data(context="statistical_stage_hyp142.py")
    if syn: print("ABORT"); return
    disc = get_discovery_data(df); f = frame(disc)
    edges = np.nanpercentile(f["vxn_level_vs_trailing"], [100 / 3, 200 / 3])
    f["bucket"] = pd.cut(f["vxn_level_vs_trailing"], bins=[-np.inf, edges[0], edges[1], np.inf], labels=["low", "mid", "high"])
    base = {c: summ(f.loc[f.bucket == c, "ratio"]) for c in ["low", "high"]}
    print(f"Baseline: LOW {base['low']}  HIGH {base['high']}")
    R = {"frozen_edges": [float(edges[0]), float(edges[1])], "baseline": base}

    print("\n--- Q1 stability (chronological halves) ---")
    mid = len(f) // 2; q1 = {}
    for c in ["low", "high"]:
        a = summ(f.iloc[:mid].loc[lambda x: x.bucket == c, "ratio"]); b = summ(f.iloc[mid:].loc[lambda x: x.bucket == c, "ratio"])
        q1[c] = {"first_half": a, "second_half": b, "same_sign": (a["mean"] < 1) == (b["mean"] < 1), "both_credible": a["credible"] and b["credible"]}
        print(f"  {c}: 1st n={a['n']} {a['mean']:.3f} cred={a['credible']} | 2nd n={b['n']} {b['mean']:.3f} cred={b['credible']} | both={q1[c]['both_credible']}")
    q1["split_date"] = str(f.index[mid]); R["q1_stability"] = q1

    print("\n--- Q2 regime (trailing-range median) ---")
    med = f["trailing_avg_rth_range"].median(); q2 = {}
    for c in ["low", "high"]:
        lo = summ(f[(f.trailing_avg_rth_range <= med) & (f.bucket == c)]["ratio"]); hi = summ(f[(f.trailing_avg_rth_range > med) & (f.bucket == c)]["ratio"])
        q2[c] = {"low_vol_regime": lo, "high_vol_regime": hi, "concentrated_in_one_regime": lo["credible"] != hi["credible"]}
        print(f"  {c}: lowvol n={lo['n']} {lo['mean']:.3f} cred={lo['credible']} | highvol n={hi['n']} {hi['mean']:.3f} cred={hi['credible']}")
    R["q2_regime"] = q2

    print("\n--- Q3 magnitude (project-wide Sidak) ---")
    tc = pwm.compute_stage_trial_counts(); q3 = {"n_discovery_trials": tc["discovery"]}
    for c in ["low", "high"]:
        v = pwm.evaluate(label=f"hyp-000142_{c}", stage="discovery", n_obs=base[c]["n"], mean=base[c]["mean"], ci_90=tuple(base[c]["ci_90"]), null_value=1.0, stage_trial_counts=tc)
        q3[c] = {"raw_ci_90": base[c]["ci_90"], "adjusted_ci": list(v.adjusted_ci), "survives_adjustment": bool(v.survives_adjustment), "abs_dev": abs(base[c]["mean"] - 1), "clears_005_floor": abs(base[c]["mean"] - 1) >= 0.05}
        print(f"  {c}: adj CI={v.adjusted_ci} survives={v.survives_adjustment} (N_disc={tc['discovery']})")
    R["q3_magnitude"] = q3

    print("\n--- Q4 selection sensitivity ---")
    q4 = {}
    for pct, lab in [(20, "quintile"), (33.33, "tercile_frozen"), (25, "quartile")]:
        h = summ(f[f.vxn_level_vs_trailing >= f.vxn_level_vs_trailing.quantile(1 - pct / 100)]["ratio"])
        l = summ(f[f.vxn_level_vs_trailing <= f.vxn_level_vs_trailing.quantile(pct / 100)]["ratio"])
        q4[lab] = {"high": h, "low": l}; print(f"  {lab}: HIGH {h['mean']:.3f} cred={h['credible']} | LOW {l['mean']:.3f} cred={l['credible']}")
    R["q4_selection"] = q4

    print("\n--- P4 disentangle: residualise on overnight_range AND prior-day range terciles ---")
    g = f.dropna(subset=["overnight_range_vs_atr", "range_vs_atr"]).copy()
    g["on_t"] = pd.qcut(g.overnight_range_vs_atr, 3, labels=["l", "m", "h"]); g["rv_t"] = pd.qcut(g.range_vs_atr, 3, labels=["l", "m", "h"])
    raw = g.loc[g.bucket == "high", "ratio"].mean() - g.loc[g.bucket == "low", "ratio"].mean()
    g["resid"] = g["ratio"] - g.groupby(["on_t", "rv_t"], observed=True)["ratio"].transform("mean") + g["ratio"].mean()
    rh = summ(g.loc[g.bucket == "high", "resid"]); rl = summ(g.loc[g.bucket == "low", "resid"]); res = rh["mean"] - rl["mean"]
    R["p4_disentangle"] = {"raw_spread": float(raw), "resid_spread_both_controls": float(res), "fraction_retained": float(res / raw) if raw else float("nan"), "resid_high": rh, "resid_low": rl,
                           "corr_vxn_vs_range_vs_atr": float(g.vxn_level_vs_trailing.corr(g.range_vs_atr))}
    print(f"  raw {raw:+.3f} -> residualised on both {res:+.3f}, retained {res / raw:.2f}; resid HIGH cred={rh['credible']}; corr(vxn, prior-day range)={R['p4_disentangle']['corr_vxn_vs_range_vs_atr']:+.3f}")

    print("\n--- POWER at the Validation review point ---")
    val = get_validation_data(df); fv = frame(val)
    n_val_high = int((fv.vxn_level_vs_trailing > edges[1]).sum())
    sd = float(f.loc[f.bucket == "high", "ratio"].std())
    def power(true_dev, n): se = sd / math.sqrt(n); z = (Z90 * se - true_dev) / se; return 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))
    dev = base["high"]["mean"] - 1
    R["power"] = {"validation_high_n_at_frozen_edges": n_val_high, "sd_high_cell": sd, "power_if_true_effect_equals_discovery": power(dev, n_val_high),
                  "power_if_true_effect_half_of_discovery": power(dev / 2, n_val_high), "power_if_true_effect_0.10": power(0.10, n_val_high)}
    print(f"  Validation HIGH n={n_val_high} (frozen edges), sd={sd:.3f}; power if true dev={dev:.3f}: {R['power']['power_if_true_effect_equals_discovery']:.2f}; if half: {R['power']['power_if_true_effect_half_of_discovery']:.2f}; if 0.10: {R['power']['power_if_true_effect_0.10']:.2f}")
    R["validation_data_touched"] = "COUNT ONLY -- n of HIGH-tercile days at frozen edges for the power calculation; no outcome examined"
    OUT.write_text(json.dumps(R, indent=1, default=float)); print(f"\nWritten {OUT}")


if __name__ == "__main__":
    main()
