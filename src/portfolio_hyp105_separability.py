"""Portfolio Agent separability check for hyp-000105/106/141 (midday-lull ->
afternoon range persistence, HOLDOUT PASSED 2026-09-12) -- the one question
that decides whether this is a NEW conditioning fact or the already-validated
overnight-coil finding (overnight_range_vs_atr -> RTH range, hyp-056/057)
restated at a finer grain. Both are volatility-persistence facts on the same
underlying instrument; the mechanism doc for hyp-105/106 itself flags this
exact concern ("same family of claim... shared daily activity state").

Same discipline as H140's director-reeval separability check (2026-09-11,
32% retained -> ABANDON) and H116's (2026-09-09, 98% retained -> separable):
  1. correlation of the midday-lull signal (is_narrow_midday, the frozen
     Discovery-stage construction) with overnight_range_vs_atr;
  2. within EACH overnight_range_vs_atr tercile, does the narrow-vs-not
     spread in afternoon_range_ratio survive;
  3. fraction of the raw narrow-vs-not spread retained after subtracting
     the overnight-range-tercile mean (residualised outcome).

Discovery data only. Frozen exp-125 construction (LOOKBACK_DAYS=20,
NARROW_PCTL=20), nothing retuned. Portfolio's job per AMENDMENT v2 is
"does this add incremental information or is it the same latent state
restated" -- NOT sizing/combination, which is deliberately out of scope here.
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

OUT = Path(__file__).resolve().parent.parent / "data" / "portfolio_hyp105_separability_results.json"
LOOKBACK_DAYS = 20
NARROW_PCTL = 20
N_BOOTSTRAP = 3000
RANDOM_SEED = 7


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    arr = np.asarray(values, dtype=float)
    if len(arr) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = rng.choice(arr, size=(n_bootstrap, len(arr)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def tercile(s: pd.Series) -> pd.Series:
    return pd.qcut(s, 3, labels=["low", "mid", "high"])


def cell(vals: pd.Series) -> dict:
    vals = vals.dropna().to_numpy()
    if len(vals) < 5:
        return {"n": int(len(vals)), "mean": None, "ci_90": [None, None], "credible": False}
    lo, hi = bootstrap_mean_ci(vals)
    return {"n": int(len(vals)), "mean": round(float(vals.mean()), 4),
            "ci_90": [round(lo, 4), round(hi, 4)], "credible": bool(lo > 1.0 or hi < 1.0)}


def main() -> dict:
    df_all, is_synthetic = load_price_data(context="portfolio_hyp105_separability.py")
    if is_synthetic:
        raise SystemExit("ABORT: only synthetic data available.")
    disc = get_discovery_data(df_all)

    # --- frozen exp-125 construction (verbatim from study_midday_lull_afternoon_expansion.py) ---
    idx = disc.index
    day_groups = {d: g for d, g in disc.groupby(idx.date)}
    rows = []
    for day, day_df in sorted(day_groups.items()):
        midday = day_df.between_time("12:00", "14:00")
        afternoon = day_df.between_time("14:00", "16:00")
        if midday.empty or afternoon.empty:
            continue
        rows.append({
            "date": day,
            "midday_range": float(midday["High"].max() - midday["Low"].min()),
            "afternoon_range": float(afternoon["High"].max() - afternoon["Low"].min()),
        })
    daily = pd.DataFrame(rows).set_index("date").sort_index()
    daily["trailing_avg_midday_range"] = daily["midday_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    daily["trailing_avg_afternoon_range"] = daily["afternoon_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    narrow_thresh = daily["midday_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, NARROW_PCTL), raw=True).shift(1)
    valid = daily.dropna(subset=["trailing_avg_midday_range", "trailing_avg_afternoon_range"]).copy()
    valid["afternoon_range_ratio"] = valid["afternoon_range"] / valid["trailing_avg_afternoon_range"]
    valid["is_narrow_midday"] = valid["midday_range"] <= narrow_thresh.reindex(valid.index)

    # --- overnight_range_vs_atr, same frozen state-primitive used by the coil finding ---
    st = build_state_frame(disc)[["overnight_range_vs_atr"]].copy()
    st.index = pd.to_datetime(st.index).date
    valid.index = pd.to_datetime(valid.index).date if not isinstance(valid.index[0], type(st.index[0])) else valid.index

    df = valid.join(st, how="inner").dropna(subset=["overnight_range_vs_atr", "afternoon_range_ratio"])
    df["on_t"] = tercile(df["overnight_range_vs_atr"])

    out = {"n": int(len(df))}

    # 1. correlation of the binary midday-lull signal with overnight_range_vs_atr
    out["corr_narrow_midday_vs_overnight_range"] = round(
        float(df["is_narrow_midday"].astype(float).corr(df["overnight_range_vs_atr"])), 4)
    out["narrow_midday_days_that_are_also_low_overnight_tercile_pct"] = round(
        float((df.loc[df["is_narrow_midday"], "on_t"] == "low").mean() * 100), 1)

    raw_narrow = cell(df.loc[df["is_narrow_midday"], "afternoon_range_ratio"])
    raw_not = cell(df.loc[~df["is_narrow_midday"], "afternoon_range_ratio"])
    out["raw"] = {"narrow_midday": raw_narrow, "not_narrow": raw_not,
                  "spread": round(raw_not["mean"] - raw_narrow["mean"], 4) if raw_narrow["mean"] and raw_not["mean"] else None}

    # 2. within each overnight-range tercile
    within = {}
    for on in ["low", "mid", "high"]:
        sub = df[df.on_t == on]
        n_cell = cell(sub.loc[sub["is_narrow_midday"], "afternoon_range_ratio"])
        nn_cell = cell(sub.loc[~sub["is_narrow_midday"], "afternoon_range_ratio"])
        spread = (nn_cell["mean"] - n_cell["mean"]) if (n_cell["mean"] is not None and nn_cell["mean"] is not None) else None
        within[on] = {"narrow_midday": n_cell, "not_narrow": nn_cell, "spread": round(spread, 4) if spread is not None else None}
    out["within_overnight_tercile"] = within

    # 3. residualised: remove the overnight-tercile mean, then re-measure the narrow-vs-not spread
    df["ratio_resid"] = df["afternoon_range_ratio"] - df.groupby("on_t", observed=True)["afternoon_range_ratio"].transform("mean") + df["afternoon_range_ratio"].mean()
    rn = cell(df.loc[df["is_narrow_midday"], "ratio_resid"])
    rnn = cell(df.loc[~df["is_narrow_midday"], "ratio_resid"])
    spread_resid = (rnn["mean"] - rn["mean"]) if (rn["mean"] is not None and rnn["mean"] is not None) else None
    out["residualised"] = {"narrow_midday": rn, "not_narrow": rnn,
                           "spread": round(spread_resid, 4) if spread_resid is not None else None}
    if out["raw"]["spread"] and spread_resid is not None and out["raw"]["spread"] != 0:
        out["residualised"]["fraction_of_raw_spread_retained"] = round(spread_resid / out["raw"]["spread"], 3)

    OUT.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))
    return out


if __name__ == "__main__":
    main()
