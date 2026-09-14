"""
validate_hyp162.py -- the ONE-SHOT Validation test for hyp-000162
(M30: opening-range width -> midday range, NQ), written and FROZEN before it is run.

Its sha256 is recorded in research/studies/hyp162-validation-spec-frozen.md and that
spec is committed BEFORE this script is executed. If this file changes, the recorded
hash stops matching and the run is no longer the pre-registered test.

WHY THIS FILE IS NOT "SCAN 036 WITH THE LOADER SWAPPED":
the blind Integrity Gate (September 14th, research/studies/hyp162-blind-gate-2026-09-14.md)
ruled CONDITIONAL and two of its findings change the test itself:
  * Scan 036's tercile edges were FULL-DISCOVERY percentiles -- not knowable at 10:00 ET
    on the day, so not a real-time sizing rule. This test uses TRAILING edges.
  * Scan 036's CI resampled blocks of consecutive WITHIN-ARM observations, independently
    per arm, which cannot contain calendar clustering. This test uses a CALENDAR-TIME
    block bootstrap.
Running the old construction here would test a rule the bot could never follow.

-------------------------------------------------------------------------------
THE SLICE
-------------------------------------------------------------------------------
VALIDATION only: 2021-10-04 -> 2024-01-03 (src/data_split.get_validation_data).
Holdout is untouched. Discovery is used ONLY as warm-up history for the trailing
statistics below -- never scored, never in either arm.

-------------------------------------------------------------------------------
THE CONSTRUCTION (frozen)
-------------------------------------------------------------------------------
state      opening_range_vs_atr -- the 09:30-10:00 ET range over trailing ATR14
           (market_state_primitives; atr14 is rolling(14).mean().shift(1), the
           current session excluded -- verified, Gate condition 4).
edges      TRAILING 250-session percentiles (1/3, 2/3) of opening_range_vs_atr,
           SHIFTED one session. Membership is therefore knowable at 10:00 ET on
           the day. Built on the concatenated Discovery+Validation frame and only
           then restricted to Validation dates, so the first 250 Validation
           sessions warm up from the Discovery tail; no session is scored on a
           partial window and none is dropped for it.
outcome    midday range (11:30-13:30 ET, inclusive="left") divided by the
           trailing-20-session mean midday range, SHIFTED one session. Same
           construction as Discovery. Same warm-up rule as the edges.
statistic  mean(ratio | HIGH) - mean(ratio | LOW). Direction pre-registered
           POSITIVE (wide opening -> larger midday range), tested with a
           two-sided interval, which is the conservative choice.
CI         CALENDAR-TIME block bootstrap: blocks of 10 CONSECUTIVE SESSIONS are
           resampled and the arms are split AFTER resampling, preserving both
           multi-day clustering and the two arms' contemporaneous correlation.
           N_BOOT = 20000, SEED = 20260914.
Sidak      SIDAK_N = 20, this project's stage-specific Validation-stage constant
           (Discovery 467 / Validation 20 / Holdout 3). Frozen as the constant,
           not recomputed at run time.

-------------------------------------------------------------------------------
TWO GATING PREDICTIONS -- BOTH MUST PASS
-------------------------------------------------------------------------------
V1  The Sidak-adjusted interval on the HIGH-LOW spread lies entirely above zero.
V2  Holding the PREVIOUS session's opening range fixed (the discriminating cell
    the Gate demanded), the retained share's LOWER 90% bound is >= 0.50 --
    the bar is cleared by the INTERVAL, never by a point estimate. Raw and
    stratified spreads come from the SAME resample.

FAILURE SEMANTICS, pre-declared (the Gate's own closure rule, moved out of sample):
  V1 fails            -> the family closes NULL.
  V1 passes, V2 fails -> the family closes as a DUPLICATE of the multi-day
                         volatility-regime family. NOT null, and NOT a second
                         attempt with a redrawn stratifier.
  both pass           -> the candidate is Validation-passed as a SIZING fact and
                         is owed Portfolio's incremental-information question
                         before any Holdout slot is requested. It may still NOT
                         attach to B2's live sizing until a MEASURED cost figure
                         exists (Gate condition 7, open, needs the execution record).

-------------------------------------------------------------------------------
NON-GATING DIAGNOSTICS (reported always, cannot flip the verdict)
-------------------------------------------------------------------------------
D1  the same spread computed on Scan 036's ORIGINAL full-sample edges, so the
    cost of moving to trailing edges is visible rather than assumed;
D2  the spread inside each prior-day-range tercile (the regime question), and
    the same in POINTS -- Monetization found the ratio effect regime-stable
    while the points effect flips sign in the MID stratum, and that pattern
    either reappears out of sample or it does not;
D3  n per arm, per year, and the count of sessions dropped for a short midday
    window -- a PASS driven by a coverage artifact should be visible.

-------------------------------------------------------------------------------
PERMANENT DISCLOSURES (Gate-mandated; they travel with every result from here)
-------------------------------------------------------------------------------
1. P1 at Discovery was SELECTION-CONFIRMATORY: the state, outcome, window,
   tercile cut and direction were all chosen because a 1,045-cell descriptive
   sweep showed this family strongest on the same Discovery slice. Promotion
   rests on this out-of-sample test and on V2, never on the Discovery P1.
2. The discriminating separability test was POST-HOC at Discovery -- run after
   the mechanical placebo check flagged the candidate, not before. V2 is the
   pre-registered, out-of-sample version of it.

HOW TO RUN:  python3 src/validate_hyp162.py
"""
from __future__ import annotations

import hashlib
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

BLOCK_SESSIONS = 10
N_BOOT = 20000
SEED = 20260914
SIDAK_N = 20
ALPHA = 0.10
EDGE_WINDOW = 250
RANGE_LOOKBACK = 20
RETAIN_BAR = 0.50
OUT = ROOT.parent / "research" / "studies" / "hyp162-validation-result-2026-09-14.json"

LOW, MID, HIGH = 0, 1, 2


def spec_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def daily_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Midday outcome + state, one row per session, over whatever frame is given."""
    st = build_state_frame(df)
    idx = pd.to_datetime(pd.Index(st.index))
    opening = pd.Series(st["opening_range_vs_atr"].to_numpy(float), index=idx)
    rng_vs_atr = pd.Series(st["range_vs_atr"].to_numpy(float), index=idx)
    rows, short = [], 0
    for day, g in df.groupby(df.index.date):
        mid = g.between_time("11:30", "13:30", inclusive="left")
        if len(mid) < 60:
            short += 1
            continue
        rows.append({"date": pd.Timestamp(day),
                     "midday_range": float(mid["High"].max() - mid["Low"].min())})
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["trailing"] = d["midday_range"].rolling(RANGE_LOOKBACK, min_periods=RANGE_LOOKBACK).mean().shift(1)
    d["ratio"] = d["midday_range"] / d["trailing"]
    d["opening"] = opening.reindex(d.index)
    d["opening_prev"] = d["opening"].shift(1)
    d["prior_rng"] = rng_vs_atr.reindex(d.index)
    d.attrs["short_midday_sessions"] = short
    return d


def trailing_groups(d: pd.DataFrame) -> pd.Series:
    lo = d["opening"].rolling(EDGE_WINDOW, min_periods=EDGE_WINDOW).quantile(1 / 3).shift(1)
    hi = d["opening"].rolling(EDGE_WINDOW, min_periods=EDGE_WINDOW).quantile(2 / 3).shift(1)
    return pd.Series(np.where(d["opening"] <= lo, LOW, np.where(d["opening"] >= hi, HIGH, MID)),
                     index=d.index).where(lo.notna() & hi.notna())


def static_terciles(s: pd.Series) -> pd.Series:
    lo, hi = np.nanpercentile(s.dropna(), [100 / 3, 200 / 3])
    return pd.Series(np.where(s <= lo, LOW, np.where(s >= hi, HIGH, MID)), index=s.index)


def _boot(d: pd.DataFrame, rng, with_strata: bool) -> dict:
    ratio = d["ratio"].to_numpy(float)
    grp = d["grp"].to_numpy(int)
    strat = d["stratum"].to_numpy(int) if with_strata else np.zeros(len(d), dtype=int)
    key = strat * 3 + grp
    n_cells = 9 if with_strata else 3
    n = len(ratio)
    n_blocks = int(np.ceil(n / BLOCK_SESSIONS))
    raws, strats, retains = [], [], []
    for _ in range(N_BOOT):
        starts = rng.integers(0, n - BLOCK_SESSIONS + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(BLOCK_SESSIONS)[None, :]).reshape(-1)[:n]
        k, r = key[idx], ratio[idx]
        cnt = np.bincount(k, minlength=n_cells).astype(float)
        tot = np.bincount(k, weights=r, minlength=n_cells)
        with np.errstate(invalid="ignore", divide="ignore"):
            means = tot / cnt
        n_str = n_cells // 3
        hi_i = [s * 3 + HIGH for s in range(n_str)]
        lo_i = [s * 3 + LOW for s in range(n_str)]
        hn, ln = cnt[hi_i], cnt[lo_i]
        if hn.sum() < 30 or ln.sum() < 30:
            continue
        raw = (np.nansum(means[hi_i] * hn) / hn.sum()) - (np.nansum(means[lo_i] * ln) / ln.sum())
        raws.append(raw)
        if with_strata:
            parts, w = [], []
            for s in range(3):
                a, b = means[s * 3 + HIGH], means[s * 3 + LOW]
                na, nb = cnt[s * 3 + HIGH], cnt[s * 3 + LOW]
                if na < 10 or nb < 10 or not np.isfinite(a) or not np.isfinite(b):
                    continue
                parts.append(a - b); w.append(na + nb)
            if parts:
                st = float(np.average(parts, weights=w))
                strats.append(st)
                if abs(raw) > 1e-9:
                    retains.append(st / raw)
    q = lambda a, p: float(np.percentile(a, p)) if len(a) else float("nan")
    a_sid = 1 - (1 - ALPHA) ** (1 / SIDAK_N)
    out = {"n_replicates": len(raws), "point": float(np.mean(raws)) if raws else float("nan"),
           "ci_90": [q(raws, 100 * ALPHA / 2), q(raws, 100 * (1 - ALPHA / 2))],
           "ci_sidak_N20": [q(raws, 100 * a_sid / 2), q(raws, 100 * (1 - a_sid / 2))]}
    if with_strata:
        out["stratified_point"] = float(np.mean(strats)) if strats else float("nan")
        out["retained_share"] = {"point": float(np.mean(retains)) if retains else float("nan"),
                                 "ci_90": [q(retains, 100 * ALPHA / 2), q(retains, 100 * (1 - ALPHA / 2))],
                                 "lower_90_bound": q(retains, 100 * ALPHA / 2), "bar": RETAIN_BAR}
    return out


def main() -> int:
    print("=" * 78)
    print("ONE-SHOT VALIDATION -- hyp-000162 (M30: opening-range width -> midday range)")
    print(f"frozen spec sha256: {spec_hash()}")
    print("=" * 78)
    df, synthetic = load_price_data(context="validate_hyp162.py", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    disc, val = get_discovery_data(df), get_validation_data(df)
    if val.empty:
        raise SystemExit("no Validation data on disk -- refusing")
    warm = pd.concat([disc, val]).sort_index()
    d_all = daily_frame(warm)
    d_all["grp"] = trailing_groups(d_all)

    val_dates = sorted(set(val.index.date))
    d = d_all[[x.date() in set(val_dates) for x in d_all.index]].copy()
    d = d.dropna(subset=["ratio", "grp", "opening_prev"])
    d["grp"] = d["grp"].astype(int)
    d["stratum"] = static_terciles(d["opening_prev"]).astype(int)

    rng = np.random.default_rng(SEED)
    main_res = _boot(d, rng, with_strata=True)
    v1 = bool(main_res["ci_sidak_N20"][0] > 0)
    v2 = bool(main_res["retained_share"]["lower_90_bound"] >= RETAIN_BAR)

    # ---- non-gating diagnostics ------------------------------------------
    d_static = d.copy()
    d_static["grp"] = static_terciles(d_static["opening"]).astype(int)
    d1 = _boot(d_static, np.random.default_rng(SEED), with_strata=False)

    pr = static_terciles(d["prior_rng"])
    d2 = {}
    for name, code in (("prior_LOW", LOW), ("prior_MID", MID), ("prior_HIGH", HIGH)):
        sub = d[pr == code]
        h, l = sub[sub["grp"] == HIGH], sub[sub["grp"] == LOW]
        if len(h) < 20 or len(l) < 20:
            d2[name] = {"n_high": len(h), "n_low": len(l), "note": "below the reporting floor"}
            continue
        d2[name] = {"n_high": int(len(h)), "n_low": int(len(l)),
                    "ratio_spread": round(float(h["ratio"].mean() - l["ratio"].mean()), 4),
                    "points_spread": round(float(h["midday_range"].mean() - l["midday_range"].mean()), 3)}
    d3 = {"n_scored": int(len(d)),
          "n_high": int((d["grp"] == HIGH).sum()), "n_low": int((d["grp"] == LOW).sum()),
          "by_year": {str(y): int(c) for y, c in d.groupby(d.index.year).size().items()},
          "short_midday_sessions_dropped": int(d_all.attrs.get("short_midday_sessions", 0))}

    verdict = ("PASS" if (v1 and v2) else
               ("CLOSE_NULL" if not v1 else "CLOSE_DUPLICATE"))
    res = {"spec_sha256": spec_hash(), "slice": "validation 2021-10-04 -> 2024-01-03",
           "block_sessions": BLOCK_SESSIONS, "n_boot": N_BOOT, "seed": SEED,
           "sidak_N": SIDAK_N, "edge_window_sessions": EDGE_WINDOW,
           "V1_spread_sidak_above_zero": v1, "V2_retained_lower_bound_ge_bar": v2,
           "verdict": verdict, "main": main_res,
           "D1_original_full_sample_edges": d1, "D2_by_prior_day_range": d2, "D3_coverage": d3,
           "permanent_disclosures": [
               "P1 at Discovery was selection-confirmatory (1,045-cell sweep); promotion rests on this test.",
               "The discriminating separability test was post-hoc at Discovery; V2 is its pre-registered out-of-sample form."]}
    OUT.write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != "main"}, indent=2))
    print(json.dumps(main_res, indent=2))
    print(f"\nVERDICT: {verdict}   -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
