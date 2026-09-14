"""
portfolio_hyp162.py -- PORTFOLIO stage, hyp-000162 (M30: opening-range width ->
midday range, NQ). The incremental-information question.

Owed after the one-shot Validation PASS (3:00 pm CT cycle). Portfolio's question
is not "is it real" (Statistical), "is it new" (Director), "is there a path to
money" (Monetization) or "could the procedure fool us" (the Gate). It is:
**does this add to the conditioning stack the project already runs, or restate
it -- and does adding it make the stack's forecasts better?**

Precedent: the same question was asked of hyp-000105 (afternoon-range ratio) and
flagged for hyp-000142 (VXN level), where separability against the coil alone was
66% and against coil + prior-day realized range only 53%. The rule that came out
of those is the one applied here: **combine by RESIDUAL, never by product.**

WHAT IS DIFFERENT FROM THE DIRECTOR RE-EVALUATION
The Director held each validated fact fixed ONE AT A TIME (75-88% retained). That
answers "is it a restatement of any single fact". Portfolio asks the harder
joint version: hold the WHOLE existing stack fixed at once. A candidate can
survive every fact individually and still be their linear combination.

METHOD (two tests, both out of sample)
  T1  JOINT RESIDUAL SEPARABILITY. Fit the existing stack's predictors
      (vxn_level_vs_trailing, overnight_range_vs_atr, prior-day range_vs_atr)
      against the midday ratio ON DISCOVERY ONLY -- coefficients never see
      Validation. Score on Validation, take the residual, and measure the
      candidate's HIGH-LOW spread of that residual with the same calendar-time
      block bootstrap and the same paired-resample retention interval the
      Validation stage used. Retained share's LOWER 90% bound vs the 50% bar.

  T3  CONTROLS -- method and single-vs-joint. The Director's stratified method is
      re-run on the VALIDATION slice against each stack member individually, and
      a joint stratified version (terciles of the stack's own forecast) is run
      alongside the linear one. Without these, a joint result could be an
      artifact of switching from stratification to regression rather than of
      holding more facts fixed. Reported whatever they say.

  T2  FORECAST IMPROVEMENT. Does the stack actually forecast midday range better
      with the 10:00 update than without it? Both models fit on Discovery, scored
      on Validation: MAE and correlation of the baseline (existing stack) vs the
      baseline plus the candidate's HIGH/LOW indicators. Reported as the
      improvement in MAE, with a block-bootstrap interval on the DIFFERENCE, so
      "it helps" is a measured claim and not an assumption.

Holdout is untouched. Every edge is the TRAILING real-time definition the blind
Gate required, not the full-sample one.

HOW TO RUN:  python3 src/portfolio_hyp162.py
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
from data_split import get_discovery_data, get_validation_data  # noqa: E402
from market_state_primitives import build_state_frame  # noqa: E402
from market_state_primitives_v2 import extend_state_frame  # noqa: E402
import validate_hyp162 as V  # the FROZEN construction is reused, not re-invented  # noqa: E402

STACK = ["vxn_level_vs_trailing", "overnight_range_vs_atr", "range_vs_atr"]
BLOCK_SESSIONS = 10
N_BOOT = 20000
SEED = 20260914
ALPHA = 0.10
RETAIN_BAR = 0.50
OUT = ROOT.parent / "research" / "studies" / "hyp162-portfolio-2026-09-14.json"


def frame_with_stack(df: pd.DataFrame) -> pd.DataFrame:
    """The frozen Validation construction, plus the existing stack's predictors."""
    d = V.daily_frame(df)
    st = extend_state_frame(build_state_frame(df), df)
    idx = pd.to_datetime(pd.Index(st.index))
    for c in STACK:
        d[c] = pd.Series(st[c].to_numpy(float), index=idx).reindex(d.index)
    d["grp"] = V.trailing_groups(d)
    return d


def ols_fit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.linalg.lstsq(np.column_stack([np.ones(len(X)), X]), y, rcond=None)[0]


def ols_pred(beta: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.column_stack([np.ones(len(X)), X]) @ beta


def _blocks(n: int, rng):
    n_blocks = int(np.ceil(n / BLOCK_SESSIONS))
    starts = rng.integers(0, n - BLOCK_SESSIONS + 1, size=n_blocks)
    return (starts[:, None] + np.arange(BLOCK_SESSIONS)[None, :]).reshape(-1)[:n]


def t1_joint_residual(val: pd.DataFrame, rng) -> dict:
    """HIGH-LOW spread of the residual after the whole existing stack, and the
    share of the raw spread it retains -- both from the SAME resample."""
    raw_y = val["ratio"].to_numpy(float)
    res_y = val["residual"].to_numpy(float)
    grp = val["grp"].to_numpy(int)
    n = len(val)
    raws, resids, retains = [], [], []
    for _ in range(N_BOOT):
        idx = _blocks(n, rng)
        g = grp[idx]
        hi, lo = g == V.HIGH, g == V.LOW
        if hi.sum() < 30 or lo.sum() < 30:
            continue
        raw = raw_y[idx][hi].mean() - raw_y[idx][lo].mean()
        res = res_y[idx][hi].mean() - res_y[idx][lo].mean()
        raws.append(raw); resids.append(res)
        if abs(raw) > 1e-9:
            retains.append(res / raw)
    q = lambda a, p: float(np.percentile(a, p)) if len(a) else float("nan")
    return {"raw_spread": {"point": float(np.mean(raws)), "ci_90": [q(raws, 5), q(raws, 95)]},
            "residual_spread": {"point": float(np.mean(resids)), "ci_90": [q(resids, 5), q(resids, 95)],
                                "credible_above_zero": bool(q(resids, 5) > 0)},
            "retained_share": {"point": float(np.mean(retains)), "ci_90": [q(retains, 5), q(retains, 95)],
                               "lower_90_bound": q(retains, 5), "bar": RETAIN_BAR,
                               "passes_with_interval": bool(q(retains, 5) >= RETAIN_BAR)}}


def t2_forecast(val: pd.DataFrame, rng) -> dict:
    """MAE of baseline vs baseline+candidate on Validation, and a block-bootstrap
    interval on the DIFFERENCE (paired, same resample)."""
    y = val["ratio"].to_numpy(float)
    e0 = np.abs(y - val["pred_base"].to_numpy(float))
    e1 = np.abs(y - val["pred_full"].to_numpy(float))
    d = e0 - e1                      # positive = the candidate helps
    n = len(y)
    diffs = []
    for _ in range(N_BOOT):
        idx = _blocks(n, rng)
        diffs.append(d[idx].mean())
    q = lambda a, p: float(np.percentile(a, p))
    return {"mae_baseline": float(e0.mean()), "mae_with_candidate": float(e1.mean()),
            "mae_improvement": float(d.mean()),
            "mae_improvement_ci_90": [q(np.array(diffs), 5), q(np.array(diffs), 95)],
            "improvement_credible": bool(q(np.array(diffs), 5) > 0),
            "pct_improvement": float(d.mean() / e0.mean() * 100),
            "corr_baseline": float(np.corrcoef(y, val["pred_base"])[0, 1]),
            "corr_with_candidate": float(np.corrcoef(y, val["pred_full"])[0, 1])}


def t3_controls(disc_d: pd.DataFrame, val_d: pd.DataFrame, beta_base: np.ndarray) -> dict:
    """Stratified (Director-method) retention on the Validation slice, per stack
    member and jointly, so the joint finding can be read against its own method."""
    import validate_hyp162 as _V
    saved = _V.N_BOOT
    _V.N_BOOT = 4000
    out = {}
    try:
        for c in STACK + ["opening_prev"]:
            w = val_d.dropna(subset=[c]).copy()
            w["stratum"] = _V.static_terciles(w[c]).astype(int)
            r = _V._boot(w, np.random.default_rng(SEED), with_strata=True)["retained_share"]
            out[f"stratified_vs_{c}"] = {"retained": round(r["point"], 4),
                                          "lower_90": round(r["lower_90_bound"], 4)}
        w = val_d.copy()
        w["stratum"] = _V.static_terciles(pd.Series(ols_pred(beta_base, w[STACK].to_numpy(float)),
                                                     index=w.index)).astype(int)
        r = _V._boot(w, np.random.default_rng(SEED), with_strata=True)["retained_share"]
        out["stratified_vs_JOINT_stack_forecast"] = {"retained": round(r["point"], 4),
                                                      "lower_90": round(r["lower_90_bound"], 4)}
    finally:
        _V.N_BOOT = saved
    return out


def main() -> int:
    df, synthetic = load_price_data(context="portfolio_hyp162.py", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic -- refusing")
    disc, val_raw = get_discovery_data(df), get_validation_data(df)
    d_all = frame_with_stack(pd.concat([disc, val_raw]).sort_index())
    d_all = d_all.dropna(subset=["ratio", "grp"] + STACK).copy()
    d_all["grp"] = d_all["grp"].astype(int)

    val_dates = set(x for x in val_raw.index.date)
    is_val = np.array([x.date() in val_dates for x in d_all.index])
    disc_d, val_d = d_all[~is_val].copy(), d_all[is_val].copy()

    # coefficients fit on DISCOVERY ONLY -- Validation never informs them
    Xd = disc_d[STACK].to_numpy(float)
    beta_base = ols_fit(Xd, disc_d["ratio"].to_numpy(float))
    Dd = np.column_stack([Xd, (disc_d["grp"] == V.HIGH).astype(float),
                          (disc_d["grp"] == V.LOW).astype(float)])
    beta_full = ols_fit(Dd, disc_d["ratio"].to_numpy(float))

    Xv = val_d[STACK].to_numpy(float)
    val_d["pred_base"] = ols_pred(beta_base, Xv)
    Dv = np.column_stack([Xv, (val_d["grp"] == V.HIGH).astype(float),
                          (val_d["grp"] == V.LOW).astype(float)])
    val_d["pred_full"] = ols_pred(beta_full, Dv)
    val_d["residual"] = val_d["ratio"] - val_d["pred_base"]

    res = {"slice": "validation 2021-10-04 -> 2024-01-03, coefficients fit on Discovery only",
           "n_discovery_fit": int(len(disc_d)), "n_validation_scored": int(len(val_d)),
           "stack_held_fixed": STACK,
           "T1_joint_residual_separability": t1_joint_residual(val_d, np.random.default_rng(SEED)),
           "T2_forecast_improvement": t2_forecast(val_d, np.random.default_rng(SEED)),
           "T3_controls_stratified_method": t3_controls(disc_d, val_d, beta_base),
           "coefficients_discovery": {"baseline": [round(float(b), 5) for b in beta_base],
                                      "with_candidate": [round(float(b), 5) for b in beta_full]}}
    OUT.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
