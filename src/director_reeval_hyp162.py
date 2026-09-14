"""
director_reeval_hyp162.py -- Director Re-Evaluation for hyp-000162
(M30: opening-range width -> midday range, NQ). Scan 036 construction, frozen.

THE QUESTION IS NOT "IS IT REAL" -- Statistical already answered that (PASS on
every gating question, survives Sidak at N=467). The Re-Evaluation question is
"IS IT NEW": does it survive residualizing on the volatility facts the project
ALREADY OWNS? Precedent: H116 retained 98% and advanced; hyp-000140 retained 32%
and the Director ruled "real is not new" (research/studies/
hyp140-director-reeval-2026-09-11.md).

This candidate arrives with a specific reason for doubt already attached: the U6
mechanical suite's placebo check found that YESTERDAY'S opening range reproduces
~74% of the effect. So the separability question here is sharper than usual --
the candidate may be reading a multi-day volatility regime the project has
already validated under other names.

STRATA TESTED (each a fact the project already holds, or the placebo's own
suspect), all known before the midday window opens:
  1. vxn_level_vs_trailing      hyp-000142, HOLDOUT PASSED -- implied vol level
  2. overnight_range_vs_atr     hyp-056/057, the "coil"
  3. range_vs_atr               F-048, prior-day range (scan_036's own P3 already
                                did this and retained 83.6% -- reproduced here as
                                a control on the method)
  4. opening_range_vs_atr, t-1  the placebo's suspect: yesterday's own value

Discovery slice only. No new cells are registered: this is a Director stage on an
existing candidate, not a new scan.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
from market_state_primitives import build_state_frame  # noqa: E402
from market_state_primitives_v2 import extend_state_frame  # noqa: E402
from statistical_hyp162 import diff_ci, BLOCK  # noqa: E402

RETAIN_BAR = 0.50   # the P3 convention already used in scan_036


def build():
    df, synthetic = load_price_data(context="director_reeval_hyp162")
    if synthetic:
        raise SystemExit("synthetic -- refusing")
    disc = get_discovery_data(df)
    st = extend_state_frame(build_state_frame(disc), disc)
    idx = pd.to_datetime(pd.Index(st.index))

    rows = []
    for day, g in disc.groupby(disc.index.date):
        mid = g.between_time("11:30", "13:30", inclusive="left")
        if len(mid) < 60:
            continue
        rows.append({"date": pd.Timestamp(day),
                     "midday_range": float(mid["High"].max() - mid["Low"].min())})
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["trailing"] = d["midday_range"].rolling(20, min_periods=20).mean().shift(1)
    d["ratio"] = d["midday_range"] / d["trailing"]

    for col in ("opening_range_vs_atr", "vxn_level_vs_trailing",
                "overnight_range_vs_atr", "range_vs_atr"):
        d[col] = pd.Series(st[col].to_numpy(float), index=idx).reindex(d.index)
    d["opening_prev"] = d["opening_range_vs_atr"].shift(1)     # the placebo's suspect
    return d.dropna(subset=["ratio", "opening_range_vs_atr"])


def terciles(s: pd.Series):
    lo, hi = np.nanpercentile(s.dropna(), [100 / 3, 200 / 3])
    return np.where(s <= lo, "LOW", np.where(s >= hi, "HIGH", "MID"))


def spread(sub: pd.DataFrame):
    """HIGH-LOW midday-ratio spread within one stratum, on the candidate's own
    Discovery tercile edges (edges are NOT recut per stratum -- recutting would
    change the candidate's definition, which the freeze forbids)."""
    h = sub.loc[sub["grp"] == "HIGH", "ratio"].to_numpy()
    l = sub.loc[sub["grp"] == "LOW", "ratio"].to_numpy()
    h, l = h[~np.isnan(h)], l[~np.isnan(l)]
    if len(h) < BLOCK * 3 or len(l) < BLOCK * 3:
        return None, (float("nan"), float("nan")), len(h), len(l)
    return diff_ci(h, l)[0], diff_ci(h, l)[1], len(h), len(l)


def main():
    d = build()
    d["grp"] = terciles(d["opening_range_vs_atr"])
    raw, raw_ci, nH, nL = spread(d)
    print(f"RAW (reproduces Scan 036): {raw:+.4f} ci_90 ({raw_ci[0]:+.4f},{raw_ci[1]:+.4f}) n={nH}/{nL}\n")

    out = {"hypothesis": "hyp-000162", "stage": "Director Re-Evaluation",
           "question": "is it NEW, not is it real", "raw_spread": raw,
           "raw_ci_90": list(raw_ci), "n_high": nH, "n_low": nL,
           "retain_bar": RETAIN_BAR, "strata": {}}

    for name, col, owner in (
        ("vxn_level_vs_trailing", "vxn_level_vs_trailing", "hyp-000142, HOLDOUT PASSED"),
        ("overnight_range_vs_atr", "overnight_range_vs_atr", "hyp-056/057, the coil"),
        ("prior_day_range", "range_vs_atr", "F-048 (scan_036 P3 control)"),
        ("opening_range_YESTERDAY", "opening_prev", "the U6 placebo's suspect"),
    ):
        sub = d.dropna(subset=[col]).copy()
        sub["stratum"] = terciles(sub[col])
        corr_p = float(sub["opening_range_vs_atr"].corr(sub[col]))
        corr_s = float(sub["opening_range_vs_atr"].corr(sub[col], method="spearman"))
        parts, weights, detail = [], [], []
        for lvl in ("LOW", "MID", "HIGH"):
            s = sub[sub["stratum"] == lvl]
            sp, ci, a, b = spread(s)
            detail.append({"stratum": lvl, "n_high": a, "n_low": b,
                           "spread": None if sp is None else round(sp, 4),
                           "ci_90": [None if np.isnan(x) else round(x, 4) for x in ci]})
            if sp is not None:
                parts.append(sp); weights.append(a + b)
        resid = float(np.average(parts, weights=weights)) if parts else float("nan")
        retained = resid / raw if raw else float("nan")
        # overlap: share of HIGH-candidate days that are also HIGH on the stratum
        hh = float(((sub["grp"] == "HIGH") & (sub["stratum"] == "HIGH")).sum() /
                   max(1, (sub["grp"] == "HIGH").sum()))
        out["strata"][name] = {"owner": owner, "pearson": round(corr_p, 4),
                               "spearman": round(corr_s, 4), "high_high_overlap": round(hh, 4),
                               "residualised_spread": round(resid, 4),
                               "share_retained": round(retained, 4),
                               "passes_bar": bool(np.isfinite(retained) and retained >= RETAIN_BAR),
                               "per_stratum": detail}
        print(f"{name:26s} r={corr_p:+.3f}  HIGH/HIGH overlap {hh:5.1%}  "
              f"resid {resid:+.4f}  RETAINED {retained:6.1%}  "
              f"{'PASS' if retained >= RETAIN_BAR else 'FAIL'}  ({owner})")
        for x in detail:
            print(f"      {x['stratum']:5s} n={x['n_high']:4d}/{x['n_low']:4d} spread={x['spread']}")

    worst = min((v["share_retained"] for v in out["strata"].values()
                 if np.isfinite(v["share_retained"])), default=float("nan"))
    out["worst_retained"] = round(worst, 4)
    out["separable"] = bool(np.isfinite(worst) and worst >= RETAIN_BAR)
    print(f"\nWORST retained across strata: {worst:.1%} -> "
          f"{'SEPARABLE' if out['separable'] else 'NOT SEPARABLE at the 50% bar'}")
    p = ROOT.parent / "research" / "studies" / "hyp162-director-reeval-2026-09-14.json"
    p.write_text(json.dumps(out, indent=2, default=str))
    print(f"written -> {p}")


if __name__ == "__main__":
    main()
