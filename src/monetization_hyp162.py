"""
monetization_hyp162.py -- MONETIZATION stage, hyp-000162 (M30: opening-range
width -> midday range, NQ).

Owed after the Director Re-Evaluation ADVANCE (11:00 am CT cycle,
research/studies/hyp162-director-reeval-2026-09-14.md). The Monetization
question is NOT "is it real" (Statistical) and NOT "is it new" (Director) but
"is there a credible path from this fact to money, and what does it cost?" --
and "no credible path" is a valid, successful answer.

Discovery data only. Frozen Scan 036 construction reused exactly (same midday
window, same trailing-20 ratio, same frozen tercile edges) -- this stage
measures the SAME effect in units a trading decision can use, it does not
re-test it.

What it computes:
  A. the effect in POINTS, not ratios -- mean midday range by opening-range
     tercile, so the monetization-screening-rule.md check (cost vs stop
     distance) can actually be applied
  B. the expected-midday-range MULTIPLIER per tercile, the form
     volatility_conditioning.py consumes (x1.00 = "no information")
  C. the CONDITIONAL multiplier: the Director found the effect is largest in
     the HIGH volatility stratum, so the multiplier is computed inside each
     prior-day-range tercile rather than assumed constant
  D. the cost check: what the multiplier changes in B2's stop distance, in
     points, against the 0.75pt fixed cost
  E. the double-counting check, in the form Portfolio will need: the residual
     multiplier after the existing conditioning inputs have had their say

Every number here is a DISCOVERY point estimate. The multipliers that would
ever be used are set after Validation/Holdout, never from Discovery -- same
rule hyp-000142's monetization stated.

HOW TO RUN:  python3 src/monetization_hyp162.py
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
import volatility_conditioning as vc  # noqa: E402
import risk_state_engine as rse  # noqa: E402

RANGE_LOOKBACK = 20
FIXED_COST_PTS = 0.75          # the project's standing per-trade cost assumption
COST_SHARE_BAR = 0.05          # monetization-screening-rule.md: cost <= ~5% of stop
OUT = ROOT.parent / "research" / "studies" / "hyp162-monetization-2026-09-14.json"


def build_daily(disc: pd.DataFrame) -> pd.DataFrame:
    """Scan 036's own daily frame, reproduced: midday 11:30-13:30 ET, range in
    POINTS, the trailing-20 mean shifted one session, and the states."""
    states = extend_state_frame(build_state_frame(disc), disc)
    idx = pd.to_datetime(pd.Index(states.index))
    opening = pd.Series(states["opening_range_vs_atr"].to_numpy(dtype=float), index=idx)
    prior_rng = pd.Series(states["range_vs_atr"].to_numpy(dtype=float), index=idx)
    atr = pd.Series(states["atr14"].to_numpy(dtype=float), index=idx)

    rows = []
    for day, g in disc.groupby(disc.index.date):
        mid = g.between_time("11:30", "13:30", inclusive="left")
        if len(mid) < 60:
            continue
        rows.append({"date": pd.Timestamp(day), "midday_range": float(mid["High"].max() - mid["Low"].min())})
    daily = pd.DataFrame(rows).set_index("date").sort_index()
    daily["trailing_midday"] = daily["midday_range"].rolling(RANGE_LOOKBACK, min_periods=RANGE_LOOKBACK).mean().shift(1)
    daily["ratio"] = daily["midday_range"] / daily["trailing_midday"]
    daily["atr14"] = atr.reindex(daily.index)
    daily["opening"] = opening.reindex(daily.index)
    daily["prior_rng"] = prior_rng.reindex(daily.index)
    return daily.dropna(subset=["ratio", "opening", "atr14"])


def terciles(s: pd.Series) -> tuple[float, float]:
    lo, hi = np.nanpercentile(s, [100 / 3, 200 / 3])
    return float(lo), float(hi)


def label(s: pd.Series, lo: float, hi: float) -> np.ndarray:
    return np.where(s <= lo, "LOW", np.where(s >= hi, "HIGH", "MID"))


def analyse(daily: pd.DataFrame) -> dict:
    lo_e, hi_e = terciles(daily["opening"])
    d = daily.assign(grp=label(daily["opening"], lo_e, hi_e))

    # ---- A/B: points and multipliers by opening-range tercile -------------
    by_group = {}
    for g in ("LOW", "MID", "HIGH"):
        sub = d[d["grp"] == g]
        by_group[g] = {
            "n": int(len(sub)),
            "mean_midday_range_pts": round(float(sub["midday_range"].mean()), 3),
            "median_midday_range_pts": round(float(sub["midday_range"].median()), 3),
            "mean_ratio": round(float(sub["ratio"].mean()), 4),
            "multiplier_vs_all": round(float(sub["ratio"].mean() / d["ratio"].mean()), 4),
        }
    spread_pts = by_group["HIGH"]["mean_midday_range_pts"] - by_group["LOW"]["mean_midday_range_pts"]

    # ---- C: conditional multiplier inside each prior-day-range tercile ----
    p_lo, p_hi = terciles(d["prior_rng"].dropna())
    d = d.assign(vol=label(d["prior_rng"], p_lo, p_hi))
    conditional = {}
    for v in ("LOW", "MID", "HIGH"):
        sub = d[d["vol"] == v]
        if len(sub) < 60:
            continue
        base = float(sub["ratio"].mean())
        cell = {}
        for g in ("LOW", "MID", "HIGH"):
            s2 = sub[sub["grp"] == g]
            if len(s2) < 30:
                continue
            cell[g] = {"n": int(len(s2)),
                       "multiplier": round(float(s2["ratio"].mean() / base), 4),
                       "mean_midday_range_pts": round(float(s2["midday_range"].mean()), 3)}
        if "HIGH" in cell and "LOW" in cell:
            cell["high_minus_low_pts"] = round(cell["HIGH"]["mean_midday_range_pts"]
                                               - cell["LOW"]["mean_midday_range_pts"], 3)
            cell["high_minus_low_mult"] = round(cell["HIGH"]["multiplier"] - cell["LOW"]["multiplier"], 4)
        conditional[f"prior_day_range_{v}"] = cell

    # ---- D: cost check, in points, against the screening rule -------------
    # B2 sizes stops as STOP_FRACTION x expected range (risk_state_engine).
    stop_frac = float(getattr(rse, "STOP_FRACTION", 0.5))
    rows = []
    for g in ("LOW", "HIGH"):
        rng_pts = by_group[g]["mean_midday_range_pts"]
        stop_pts = stop_frac * rng_pts
        rows.append({"tercile": g, "mean_midday_range_pts": rng_pts,
                     "implied_stop_pts": round(stop_pts, 3),
                     "cost_share_of_stop": round(FIXED_COST_PTS / stop_pts, 5),
                     "clears_5pct_bar": bool(FIXED_COST_PTS / stop_pts <= COST_SHARE_BAR)})
    stop_delta_pts = round(stop_frac * spread_pts, 3)

    # ---- E: residual after the existing conditioning inputs ---------------
    # The existing pre-open multiplier (volatility_conditioning) is a function
    # of prior-day range and the overnight coil. Within each level of that
    # multiplier, does the opening-range tercile still move the midday ratio?
    cond_frame_dates = d.index
    base_mult = []
    try:
        cf = vc.build_conditioning_frame(DISC_CACHE["disc"])
        for ts in cond_frame_dates:
            base_mult.append(vc.get_volatility_conditioning(ts.date(), cf)["expected_range_multiplier"])
    except Exception as e:  # pragma: no cover -- reported, never silently zeroed
        base_mult = [float("nan")] * len(cond_frame_dates)
        residual_note = f"pre-open multiplier unavailable ({type(e).__name__}: {e})"
    else:
        residual_note = ""
    d = d.assign(base_mult=base_mult)
    residual = {}
    for lvl, sub in d.dropna(subset=["base_mult"]).groupby("base_mult"):
        if len(sub) < 60:
            continue
        h = sub[sub["grp"] == "HIGH"]["ratio"]
        l = sub[sub["grp"] == "LOW"]["ratio"]
        if len(h) < 30 or len(l) < 30:
            continue
        residual[f"pre_open_mult_{lvl:.4f}"] = {
            "n": int(len(sub)), "n_high": int(len(h)), "n_low": int(len(l)),
            "high_minus_low_ratio": round(float(h.mean() - l.mean()), 4)}

    return {
        "n_sessions": int(len(d)),
        "tercile_edges_opening_range_vs_atr": {"LOW<=": round(lo_e, 4), "HIGH>=": round(hi_e, 4)},
        "A_B_by_opening_range_tercile": by_group,
        "high_minus_low_midday_range_pts": round(spread_pts, 3),
        "C_conditional_on_prior_day_range": conditional,
        "D_cost_check": {"stop_fraction": stop_frac, "fixed_cost_pts": FIXED_COST_PTS,
                         "bar": COST_SHARE_BAR, "rows": rows,
                         "stop_distance_delta_HIGH_minus_LOW_pts": stop_delta_pts,
                         "cost_share_of_that_delta": round(FIXED_COST_PTS / stop_delta_pts, 5)
                         if stop_delta_pts else None},
        "E_residual_within_pre_open_multiplier": {"note": residual_note, "levels": residual},
    }


DISC_CACHE: dict = {}


def main() -> int:
    df, synthetic = load_price_data(context="monetization_hyp162.py")
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    disc = get_discovery_data(df)
    DISC_CACHE["disc"] = disc
    daily = build_daily(disc)
    res = analyse(daily)
    OUT.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
