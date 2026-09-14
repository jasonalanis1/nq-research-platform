"""
gate_conditions_hyp162.py -- discharges the BLIND Integrity Gate's conditions 2
and 3 on hyp-000162 (M30: opening-range width -> midday range, NQ).

The Gate ruled CONDITIONAL (September 14th, 1:00 pm CT cycle, ruling recorded
verbatim in research/studies/hyp162-blind-gate-2026-09-14.md). Two of its
conditions attack the CI machinery itself and are answered here, together,
because they need the same resample:

  Condition 3 -- "re-run the CI of record with a CALENDAR-TIME block bootstrap:
  resample blocks of consecutive SESSIONS and split into HIGH/LOW after
  resampling, preserving both multi-day clustering and the arms' contemporaneous
  correlation." The scan's own bootstrap resampled blocks of 10 consecutive
  WITHIN-ARM observations, independently per arm -- ten consecutive HIGH
  sessions can span months, so that block does not contain the calendar
  clustering the placebo red is about.

  Condition 5 -- disclose the sourcing sweep's look-cell count and apply a
  max-selection correction with it. The sweep (research/observatory/
  idea-factory-2026-09-13.md) ranked 1,045 descriptive cells (315 more dropped
  as circular by the timing rule before ranking). Sidak-adjusted intervals at
  K=1045 are reported alongside the project's standing Discovery N=467.

  Condition 6 -- size the retention bar: the MDE at 80% power for the retained
  share against the 50% bar, from the same bootstrap.

  Condition 7 (first half) -- the frozen tercile edges are full-Discovery
  percentiles and are not knowable at 10:00 ET. Re-cut as TRAILING percentiles
  over the prior 250 sessions (strictly shifted) and re-run the raw spread.

  Condition 2 -- "attach an interval to every retention ratio: compute raw and
  stratified differences on the SAME resample and report the distribution of
  their ratio. The bar is met only if the retained share's LOWER 90% bound
  exceeds it." The Director's 75-88% retention figures are point estimates of a
  ratio of two noisy means, compared against a 50% line.

The stratifier used here is the DISCRIMINATING one the Gate named in condition
1: the PREVIOUS session's opening_range_vs_atr -- the placebo's own suspect, not
the prior-day RANGE that P3 used.

Frozen-definition discipline: the candidate's HIGH/LOW membership comes from its
own frozen full-Discovery tercile edges, computed once on the real sample and
held fixed inside every replicate. Re-cutting edges per replicate would change
the candidate's definition, which the freeze forbids; that choice is stated here
rather than buried.

HOW TO RUN:  python3 src/gate_conditions_hyp162.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from director_reeval_hyp162 import build, terciles  # noqa: E402

BLOCK_SESSIONS = 10        # consecutive CALENDAR sessions, not within-arm rows
N_BOOT = 3000
SEED = 20260914
RETAIN_BAR = 0.50
ALPHA = 0.10
OUT = ROOT.parent / "research" / "studies" / "hyp162-gate-conditions-2026-09-14.json"

LOW, MID, HIGH = 0, 1, 2
_CODE = {"LOW": LOW, "MID": MID, "HIGH": HIGH}


def _codes(labels: np.ndarray) -> np.ndarray:
    return np.array([_CODE[x] for x in labels], dtype=np.int64)


def _cell_means(ratio: np.ndarray, key: np.ndarray, n_cells: int, idx: np.ndarray):
    """Mean of `ratio` per cell over one resample (idx), plus per-cell counts."""
    k = key[idx]
    r = ratio[idx]
    cnt = np.bincount(k, minlength=n_cells).astype(float)
    tot = np.bincount(k, weights=r, minlength=n_cells)
    with np.errstate(invalid="ignore", divide="ignore"):
        return tot / cnt, cnt


def calendar_block_bootstrap(d: pd.DataFrame, rng) -> dict:
    """One pass producing, per replicate, BOTH the raw HIGH-LOW spread and the
    spread stratified on the previous session's opening range."""
    ratio = d["ratio"].to_numpy(float)
    grp = _codes(d["grp"].to_numpy())
    strat = _codes(d["stratum"].to_numpy())
    n = len(ratio)
    key = strat * 3 + grp          # 9 cells: stratum x candidate group
    n_cells = 9
    n_blocks = int(np.ceil(n / BLOCK_SESSIONS))

    raws, strats, retains = [], [], []
    for _ in range(N_BOOT):
        starts = rng.integers(0, n - BLOCK_SESSIONS + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(BLOCK_SESSIONS)[None, :]).reshape(-1)[:n]
        means, cnt = _cell_means(ratio, key, n_cells, idx)
        # raw: pooled HIGH vs pooled LOW on the same resample
        hi_n = cnt[[HIGH, 3 + HIGH, 6 + HIGH]]
        lo_n = cnt[[LOW, 3 + LOW, 6 + LOW]]
        hi_m = means[[HIGH, 3 + HIGH, 6 + HIGH]]
        lo_m = means[[LOW, 3 + LOW, 6 + LOW]]
        if hi_n.sum() < 30 or lo_n.sum() < 30:
            continue
        raw = (np.nansum(hi_m * hi_n) / hi_n.sum()) - (np.nansum(lo_m * lo_n) / lo_n.sum())
        # stratified: within-stratum HIGH-LOW, weighted by stratum size, both
        # arms from the SAME resample
        parts, weights = [], []
        for s in range(3):
            a, b = means[s * 3 + HIGH], means[s * 3 + LOW]
            na, nb = cnt[s * 3 + HIGH], cnt[s * 3 + LOW]
            if na < 10 or nb < 10 or not np.isfinite(a) or not np.isfinite(b):
                continue
            parts.append(a - b)
            weights.append(na + nb)
        if not parts:
            continue
        st = float(np.average(parts, weights=weights))
        raws.append(raw)
        strats.append(st)
        if abs(raw) > 1e-9:
            retains.append(st / raw)

    raws, strats, retains = np.array(raws), np.array(strats), np.array(retains)
    def sidak(a, k):
        """Two-sided Sidak-adjusted interval for one of k simultaneous looks."""
        alpha_adj = 1 - (1 - ALPHA) ** (1 / k)
        return [float(np.percentile(a, 100 * alpha_adj / 2)),
                float(np.percentile(a, 100 * (1 - alpha_adj / 2)))]
    se_ret = float(np.std(retains, ddof=1)) if len(retains) > 1 else float("nan")
    q = lambda a, p: float(np.percentile(a, p)) if len(a) else float("nan")
    return {
        "n_replicates_used": int(len(raws)),
        "raw_spread": {"point": float(np.mean(raws)),
                       "ci_90": [q(raws, 100 * ALPHA / 2), q(raws, 100 * (1 - ALPHA / 2))],
                       "credible_above_zero": bool(q(raws, 100 * ALPHA / 2) > 0)},
        "stratified_spread": {"point": float(np.mean(strats)),
                              "ci_90": [q(strats, 100 * ALPHA / 2), q(strats, 100 * (1 - ALPHA / 2))],
                              "credible_above_zero": bool(q(strats, 100 * ALPHA / 2) > 0)},
        "retained_share": {"point": float(np.mean(retains)),
                           "ci_90": [q(retains, 100 * ALPHA / 2), q(retains, 100 * (1 - ALPHA / 2))],
                           "lower_90_bound": q(retains, 100 * ALPHA / 2),
                           "bar": RETAIN_BAR,
                           "passes_with_interval": bool(q(retains, 100 * ALPHA / 2) >= RETAIN_BAR)},
        "sidak_adjusted_raw_spread": {
            "K_1045_sourcing_sweep": sidak(raws, 1045),
            "K_467_project_discovery_N": sidak(raws, 467),
            "note": "bootstrap quantiles widened to the Sidak per-look level; "
                    "credible if the lower bound stays above zero"},
        "condition_6_power": {
            "se_of_retained_share": round(se_ret, 5),
            "mde_at_80pct_power_vs_bar": round(RETAIN_BAR + 2.486 * se_ret, 4),
            "note": "one-sided 5% test, 80% power: the design can distinguish a true "
                    "retained share above this number from the 50% bar"},
    }


def main() -> int:
    d = build()
    d["grp"] = terciles(d["opening_range_vs_atr"])          # frozen candidate edges
    d = d.dropna(subset=["opening_prev"]).copy()
    d["stratum"] = terciles(d["opening_prev"])              # the discriminating stratifier
    rng = np.random.default_rng(SEED)
    res = calendar_block_bootstrap(d, rng)

    # ---- condition 7 (first half): trailing, real-time-estimable edges ----
    op = d["opening_range_vs_atr"]
    lo_t = op.rolling(250, min_periods=250).quantile(1 / 3).shift(1)
    hi_t = op.rolling(250, min_periods=250).quantile(2 / 3).shift(1)
    rt = d.assign(lo_t=lo_t, hi_t=hi_t).dropna(subset=["lo_t", "hi_t"]).copy()
    rt["grp"] = np.where(rt["opening_range_vs_atr"] <= rt["lo_t"], "LOW",
                         np.where(rt["opening_range_vs_atr"] >= rt["hi_t"], "HIGH", "MID"))
    rt2 = rt.copy(); rt2["stratum"] = terciles(rt2["opening_prev"])
    rt_res = calendar_block_bootstrap(rt2, np.random.default_rng(SEED))
    res["condition_7_trailing_edges"] = {
        "n_sessions": int(len(rt)), "window_sessions": 250,
        "n_high": int((rt["grp"] == "HIGH").sum()), "n_low": int((rt["grp"] == "LOW").sum()),
        "raw_spread": rt_res["raw_spread"], "retained_share": rt_res["retained_share"],
        "note": "tercile edges re-cut as trailing-250-session percentiles, shifted one "
                "session, so membership is knowable at 10:00 ET on the day"}
    res |= {"n_sessions": int(len(d)), "block_sessions": BLOCK_SESSIONS, "n_boot": N_BOOT,
            "seed": SEED, "stratifier": "opening_range_vs_atr at t-1 (the placebo's suspect)",
            "answers": ["Gate condition 2 (interval on the retention ratio)",
                        "Gate condition 3 (calendar-time block bootstrap)"]}
    OUT.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
