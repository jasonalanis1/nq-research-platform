"""Director Re-Evaluation for hyp-000140 -- the one question that decides
whether Monetization capital is worth spending: is |gap_vs_atr| -> same-day
RTH range a NEW fact, or the validated overnight-coil range finding
(overnight_range_vs_atr -> RTH range, hyp-056/057) restated?

A large opening gap and a large overnight range are plausibly the same
night. If the gap effect vanishes once overnight range is held fixed, the
candidate is redundant (Triage F) and should close to LEARN as known-true,
not-incremental, before anyone designs a monetization around it.

Separability check, same discipline as H116's (2026-09-09, 98% retained):
  1. correlation of abs_gap_vs_atr with overnight_range_vs_atr;
  2. tercile-of-tercile: within EACH overnight_range tercile, does the
     HIGH-vs-LOW gap spread in same-day range ratio survive?
  3. fraction of the raw HIGH-LOW gap effect retained after subtracting
     the overnight-range-tercile mean (residualised outcome).
Discovery data only. Frozen Scan 010 construction, nothing retuned.
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
from market_state_primitives import build_state_frame  # noqa: E402
from market_state_primitives_v2 import extend_state_frame  # noqa: E402
from market_behavior_discovery_scan_007 import build_rth_range_frame  # noqa: E402
from statistical_stage_hyp140 import bootstrap_mean_ci  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "data" / "director_reeval_hyp140_results.json"


def tercile(s: pd.Series) -> pd.Series:
    return pd.qcut(s, 3, labels=["low", "mid", "high"])


def cell(vals: pd.Series) -> dict:
    vals = vals.dropna().to_numpy()
    lo, hi = bootstrap_mean_ci(vals)
    return {"n": int(len(vals)), "mean": round(float(vals.mean()), 4),
            "ci_90": [round(lo, 4), round(hi, 4)], "credible": bool(lo > 1.0 or hi < 1.0)}


def main() -> dict:
    df_all, is_synthetic = load_price_data(context="director_reeval_hyp140.py")
    if is_synthetic:
        raise SystemExit("ABORT: only synthetic data available.")
    disc = get_discovery_data(df_all)
    rth = build_rth_range_frame(disc).dropna(subset=["trailing_avg_rth_range"]).copy()
    rth["ratio"] = rth["rth_range"] / rth["trailing_avg_rth_range"]
    st = extend_state_frame(build_state_frame(disc), disc)[["gap_vs_atr", "overnight_range_vs_atr"]].copy()
    st["abs_gap"] = st["gap_vs_atr"].abs()
    df = rth.join(st, how="inner").dropna(subset=["abs_gap", "overnight_range_vs_atr"])
    df["gap_t"] = tercile(df["abs_gap"])
    df["on_t"] = tercile(df["overnight_range_vs_atr"])

    out = {"n": int(len(df)),
           "corr_abs_gap_vs_overnight_range": round(float(df["abs_gap"].corr(df["overnight_range_vs_atr"])), 4),
           "spearman": round(float(df["abs_gap"].corr(df["overnight_range_vs_atr"], method="spearman")), 4)}

    raw_hi, raw_lo = cell(df.loc[df.gap_t == "high", "ratio"]), cell(df.loc[df.gap_t == "low", "ratio"])
    out["raw"] = {"high_gap": raw_hi, "low_gap": raw_lo, "spread": round(raw_hi["mean"] - raw_lo["mean"], 4)}

    # 2. within each overnight-range tercile
    within = {}
    for on in ["low", "mid", "high"]:
        sub = df[df.on_t == on]
        h, l = cell(sub.loc[sub.gap_t == "high", "ratio"]), cell(sub.loc[sub.gap_t == "low", "ratio"])
        within[on] = {"high_gap": h, "low_gap": l, "spread": round(h["mean"] - l["mean"], 4)}
    out["within_overnight_tercile"] = within

    # 3. residualised: remove the overnight-tercile mean, then re-measure the gap spread
    df["ratio_resid"] = df["ratio"] - df.groupby("on_t", observed=True)["ratio"].transform("mean") + df["ratio"].mean()
    rh, rl = cell(df.loc[df.gap_t == "high", "ratio_resid"]), cell(df.loc[df.gap_t == "low", "ratio_resid"])
    spread_resid = rh["mean"] - rl["mean"]
    out["residualised"] = {"high_gap": rh, "low_gap": rl, "spread": round(spread_resid, 4),
                           "fraction_of_raw_spread_retained": round(spread_resid / out["raw"]["spread"], 3)}

    # overlap of the two HIGH terciles (33% expected under independence)
    hi_gap = df.gap_t == "high"
    out["high_gap_days_that_are_also_high_overnight_range_pct"] = round(float((df.loc[hi_gap, "on_t"] == "high").mean() * 100), 1)

    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()
