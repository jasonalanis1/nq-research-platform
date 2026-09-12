#!/usr/bin/env python3
"""UPGRADE 5 (Jason's direction, 2026-09-11): statistical power of H118's
locked review point.

Question, asked once: at 40 resolved forward trades, what is the
probability the 90% CI clears zero IF the true effect is 0.40R (the
Holdout re-baseline the Integrity Gate imposed)?

The review point does NOT move -- that rule holds. This is information
for Jason about whether the 12-month clock is likely to answer the
question, not a proposal to change it.

Method. Per-trade R lists were never persisted by the H118 studies; only
n, mean and the 90% bootstrap CI were. The per-trade standard deviation
is backed out of each stage's CI (half-width = 1.645 * sd / sqrt(n) for
the bootstrap-of-the-mean, which is normal at these n). Power is then
computed two ways: the normal approximation, and a Monte-Carlo that draws
n=40 trades from a skewed distribution (log-normal-shifted) matched to the
pooled mean/sd, because 10-day time-exit R multiples are right-skewed and
the normal approximation is slightly optimistic for the lower tail.

    python3 src/h118_power_check.py            # prints the table
    python3 src/h118_power_check.py --json     # machine-readable
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STAGES = {
    "discovery": DATA / "study_vwap_dist_low_10d_drift_h118_results.json",
    "validation": DATA / "study_vwap_dist_low_10d_drift_h118_prospective_results.json",
    "holdout": DATA / "study_vwap_dist_low_10d_drift_h118_holdout_results.json",
}
Z90 = 1.6448536  # one-sided 5% -> lower bound of a 90% two-sided CI
REVIEW_N = 40
TRUE_EFFECTS = (0.62, 0.40, 0.28, 0.14)   # Discovery, Holdout re-baseline, Validation, Gate floor


def stage_sd(path: Path) -> dict:
    d = json.loads(path.read_text())
    r = d["r_multiple_result"]
    n, mean = int(r["n"]), float(r["mean_r_multiple_net"])
    lo, hi = (float(x) for x in r["ci_90"])
    half = (hi - lo) / 2.0
    sd = half * math.sqrt(n) / Z90
    return {"n": n, "mean_r": mean, "ci_90": [lo, hi], "sd_r": sd}


def pooled_sd(stages: dict) -> float:
    num = sum((s["n"] - 1) * s["sd_r"] ** 2 for s in stages.values())
    den = sum(s["n"] - 1 for s in stages.values())
    return math.sqrt(num / den)


def power_normal(true_r: float, sd: float, n: int = REVIEW_N) -> float:
    """P(lower 90% bound > 0) when the mean estimate ~ N(true_r, sd/sqrt(n))."""
    se = sd / math.sqrt(n)
    z = (Z90 * se - true_r) / se
    return 1.0 - 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def n_for_power(true_r: float, sd: float, target: float = 0.80) -> int:
    n = 2
    while power_normal(true_r, sd, n) < target:
        n += 1
        if n > 5000:
            return -1
    return n


def power_mc(true_r: float, sd: float, n: int = REVIEW_N, sims: int = 20000,
             boots: int = 400, seed: int = 20260911) -> float:
    """Monte-Carlo with a right-skewed per-trade distribution.

    R = a + b * LogNormal(0, s) shifted so mean/sd match, with skew fixed at
    ~1.0 (typical of long, time-exit, ATR-normalised outcomes). Each sim
    draws n trades and bootstraps the mean exactly as the study code does
    (percentile 5 of resampled means)."""
    rng = np.random.default_rng(seed)
    s = 0.31  # lognormal sigma giving skew ~1.0
    ln_mean = math.exp(s * s / 2.0)
    ln_sd = math.sqrt((math.exp(s * s) - 1.0) * math.exp(s * s))
    b = sd / ln_sd
    a = true_r - b * ln_mean
    hits = 0
    for _ in range(sims):
        trades = a + b * rng.lognormal(0.0, s, size=n)
        idx = rng.integers(0, n, size=(boots, n))
        means = trades[idx].mean(axis=1)
        if np.percentile(means, 5) > 0:
            hits += 1
    return hits / sims


def run(mc: bool = True) -> dict:
    stages = {k: stage_sd(p) for k, p in STAGES.items() if p.exists()}
    sd = pooled_sd(stages)
    table = []
    for tr in TRUE_EFFECTS:
        row = {
            "true_effect_r": tr,
            "power_normal_at_40": round(power_normal(tr, sd), 3),
            "n_for_80pct_power": n_for_power(tr, sd),
        }
        if mc:
            row["power_mc_skewed_at_40"] = round(power_mc(tr, sd), 3)
        table.append(row)
    return {
        "review_point": {"resolved_trades": REVIEW_N, "and_calendar_months": 12,
                         "rule": "locked; never moves"},
        "per_trade_sd_by_stage": stages,
        "pooled_per_trade_sd_r": round(sd, 3),
        "power": table,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-mc", action="store_true")
    args = ap.parse_args()
    out = run(mc=not args.no_mc)
    if args.json:
        print(json.dumps(out, indent=1))
        return
    print(f"H118 power at the locked review point (n={REVIEW_N} resolved trades)")
    print(f"pooled per-trade sd = {out['pooled_per_trade_sd_r']:.2f}R  "
          + "  ".join(f"{k}: sd {v['sd_r']:.2f}R (n={v['n']})" for k, v in out["per_trade_sd_by_stage"].items()))
    print()
    print(f"{'true effect':>12} {'P(CI>0) normal':>16} {'P(CI>0) skewed MC':>19} {'n for 80% power':>16}")
    for r in out["power"]:
        mc = r.get("power_mc_skewed_at_40")
        print(f"{r['true_effect_r']:>11.2f}R {r['power_normal_at_40']:>16.0%} "
              f"{(f'{mc:.0%}' if mc is not None else '-'):>19} {r['n_for_80pct_power']:>16}")


if __name__ == "__main__":
    main()
