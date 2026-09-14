"""
statistical_hyp162.py -- Statistical stage for hyp-000162 (M30: opening-range
width -> midday range and excursion, NQ). Scan 036, drawn 2026-09-14.

Construction is reproduced from src/market_behavior_discovery_scan_036.py
EXACTLY -- same state variable from the frozen state frame, same tercile cuts,
same midday window, same trailing-20d ratio, same block bootstrap (block=10,
N_BOOT=3000, seed=20260913). Nothing is redefined at this stage; the Statistical
stage asks whether the ALREADY-REGISTERED result holds up, not whether some
better version of it would.

The four questions, in the form the prior stage docs use:
  Q1 stability     chronological halves
  Q2 regime        split at the trailing-20d range median
  Q3 multiplicity  Sidak at the live project-wide Discovery trial count (BINDING)
  Q4 selection     alternative midday windows / tercile edges (REPORTED, not gating)
  + power at the proposed one-shot Validation review point

NOT ANSWERED HERE, deliberately: the U6 placebo red (prior-day OPENING range
reproduces 74% of the effect). Separating "wide opening range" from "wide
multi-day volatility regime" needs a NEW conditioning variable and therefore a
NEW registered trial -- that is the Director's call at the Validation gate and
the blind Gate's to weigh, not this stage's to quietly absorb. Q2 is the closest
this stage legitimately gets, and it is reported as such.
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
import project_wide_multiplicity as pwm  # noqa: E402

BLOCK, N_BOOT, SEED, RANGE_LOOKBACK = 10, 3000, 20260913, 20
Z_90 = 1.6448536269514722


def _block_means(x: np.ndarray, rng) -> np.ndarray:
    n = len(x)
    if n <= BLOCK:
        return rng.choice(x, size=(N_BOOT, n), replace=True).mean(axis=1)
    nb = int(np.ceil(n / BLOCK))
    starts = rng.integers(0, n - BLOCK + 1, size=(N_BOOT, nb))
    idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]).reshape(N_BOOT, -1)[:, :n]
    return x[idx].mean(axis=1)


def diff_ci(high, low):
    high = np.asarray(high, float); low = np.asarray(low, float)
    high, low = high[~np.isnan(high)], low[~np.isnan(low)]
    if len(high) < BLOCK * 3 or len(low) < BLOCK * 3:
        return float("nan"), (float("nan"), float("nan")), len(high), len(low)
    rng = np.random.default_rng(SEED)
    boots = _block_means(high, rng) - _block_means(low, rng)
    return (float(high.mean() - low.mean()),
            (float(np.percentile(boots, 5)), float(np.percentile(boots, 95))),
            len(high), len(low))


def build(midday=("11:30", "13:30"), lookback=RANGE_LOOKBACK):
    df, synthetic = load_price_data(context="statistical_hyp162")
    if synthetic:
        raise SystemExit("synthetic -- refusing")
    disc = get_discovery_data(df)
    st = extend_state_frame(build_state_frame(disc), disc)
    idx = pd.to_datetime(pd.Index(st.index))
    opening = pd.Series(st["opening_range_vs_atr"].to_numpy(float), index=idx)
    rows = []
    for day, g in disc.groupby(disc.index.date):
        mid = g.between_time(midday[0], midday[1], inclusive="left")
        if len(mid) < 60:
            continue
        rows.append({"date": pd.Timestamp(day),
                     "midday_range": float(mid["High"].max() - mid["Low"].min())})
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["trailing"] = d["midday_range"].rolling(lookback, min_periods=lookback).mean().shift(1)
    d["ratio"] = d["midday_range"] / d["trailing"]
    d["opening"] = opening.reindex(d.index)
    # regime variable: the trailing-20d RTH range, known at the prior close
    rth = pd.Series((st["High"] - st["Low"]).to_numpy(float), index=idx)
    d["trailing_rth"] = rth.rolling(lookback, min_periods=lookback).mean().shift(1).reindex(d.index)
    return d.dropna(subset=["ratio", "opening", "trailing_rth"])


def split(u):
    lo, hi = np.nanpercentile(u["opening"], [100 / 3, 200 / 3])
    return (u[u["opening"] >= hi]["ratio"].to_numpy(),
            u[u["opening"] <= lo]["ratio"].to_numpy(), lo, hi)


def main():
    u = build()
    H, L, lo_e, hi_e = split(u)
    full_d, full_ci, nH, nL = diff_ci(H, L)
    print(f"FULL SAMPLE: n={nH}/{nL}  diff {full_d:+.4f}  ci_90 ({full_ci[0]:+.4f},{full_ci[1]:+.4f})")

    out = {"hypothesis": "hyp-000162", "scan": "scan_036_2026-09-14",
           "construction": "reproduced from market_behavior_discovery_scan_036.py",
           "full_sample": {"n_high": nH, "n_low": nL, "diff": full_d, "ci_90": list(full_ci)},
           "questions": {}}

    # Q1 -- chronological halves
    mid = len(u) // 2
    q1 = {}
    for name, sub in (("first_half", u.iloc[:mid]), ("second_half", u.iloc[mid:])):
        h, l, _, _ = split(sub)
        dd, cc, a, b = diff_ci(h, l)
        q1[name] = {"n_high": a, "n_low": b, "diff": dd, "ci_90": list(cc),
                    "credible": bool(cc[0] > 0 or cc[1] < 0)}
        print(f"Q1 {name:12s} diff {dd:+.4f} ci_90 ({cc[0]:+.4f},{cc[1]:+.4f}) n={a}/{b}")
    q1["pass"] = bool(q1["first_half"]["credible"] and q1["second_half"]["credible"]
                      and (q1["first_half"]["diff"] > 0) == (q1["second_half"]["diff"] > 0))
    out["questions"]["Q1_stability"] = q1

    # Q2 -- regime (trailing-20d RTH range median), known at the prior close
    med = float(u["trailing_rth"].median())
    q2 = {"median_trailing_rth_points": med}
    for name, sub in (("low_vol", u[u["trailing_rth"] <= med]), ("high_vol", u[u["trailing_rth"] > med])):
        h, l, _, _ = split(sub)
        dd, cc, a, b = diff_ci(h, l)
        q2[name] = {"n_high": a, "n_low": b, "diff": dd, "ci_90": list(cc),
                    "credible": bool(cc[0] > 0 or cc[1] < 0)}
        print(f"Q2 {name:12s} diff {dd:+.4f} ci_90 ({cc[0]:+.4f},{cc[1]:+.4f}) n={a}/{b}")
    q2["pass"] = bool(q2["low_vol"]["credible"] and q2["high_vol"]["credible"]
                      and (q2["low_vol"]["diff"] > 0) == (q2["high_vol"]["diff"] > 0))
    q2["note"] = ("Closest this stage legitimately gets to the U6 placebo red. It shows the effect "
                  "is not confined to one volatility regime; it does NOT separate 'wide opening "
                  "range' from 'wide multi-day regime', which needs a new conditioning variable "
                  "and therefore a new registered trial.")
    out["questions"]["Q2_regime"] = q2

    # Q3 -- multiplicity, BINDING
    counts = pwm.compute_stage_trial_counts()
    v = pwm.evaluate("hyp-000162 midday range ratio HIGH-LOW", "discovery", nH + nL,
                     full_d, full_ci, 0.0, counts)
    q3 = {"n_trials_discovery": counts["discovery"], "adjusted_ci": list(v.adjusted_ci),
          "survives": bool(v.survives_adjustment), "pass": bool(v.survives_adjustment)}
    print(f"Q3 sidak N={counts['discovery']} adjusted ({v.adjusted_ci[0]:+.4f},{v.adjusted_ci[1]:+.4f}) "
          f"survives={v.survives_adjustment}")
    out["questions"]["Q3_multiplicity"] = q3

    # Q4 -- selection sensitivity, REPORTED
    q4 = {}
    for label, kw in (("frozen_1130_1330", {}),
                      ("alt_1100_1300", {"midday": ("11:00", "13:00")}),
                      ("alt_1200_1400", {"midday": ("12:00", "14:00")}),
                      ("alt_1130_1400", {"midday": ("11:30", "14:00")})):
        try:
            uu = u if not kw else build(**kw)
            h, l, _, _ = split(uu)
            dd, cc, a, b = diff_ci(h, l)
            q4[label] = {"diff": dd, "ci_90": list(cc), "n_high": a, "n_low": b,
                         "credible": bool(cc[0] > 0 or cc[1] < 0)}
            print(f"Q4 {label:18s} diff {dd:+.4f} ci_90 ({cc[0]:+.4f},{cc[1]:+.4f})")
        except Exception as exc:  # noqa: BLE001
            q4[label] = {"error": repr(exc)}
    out["questions"]["Q4_selection_sensitivity"] = q4

    # Power at the proposed one-shot Validation review point
    from data_split import get_validation_data
    df, _ = load_price_data(context="statistical_hyp162 power")
    try:
        val = get_validation_data(df)
        n_val_sessions = len(set(val.index.date))
    except Exception:  # noqa: BLE001
        n_val_sessions = None
    se_disc = (full_ci[1] - full_ci[0]) / (2 * Z_90)
    power = {}
    if n_val_sessions:
        # two terciles of the validation slice, same construction
        n_val_arm = int(n_val_sessions / 3)
        se_val = se_disc * np.sqrt((nH + nL) / max(1, 2 * n_val_arm))
        z_adj = pwm.sidak_z(counts["validation"])
        from math import erf, sqrt
        def _p(effect):
            # two-sided, at the Sidak-adjusted validation threshold
            lam = effect / se_val
            return float(1 - 0.5 * (1 + erf((z_adj - lam) / sqrt(2)))
                         + 0.5 * (1 + erf((-z_adj - lam) / sqrt(2))))
        power = {"n_validation_sessions": n_val_sessions, "n_per_arm_est": n_val_arm,
                 "se_validation_est": se_val, "sidak_z_validation": z_adj,
                 "power_at_discovery_effect": round(_p(full_d), 4),
                 "power_at_half_effect": round(_p(full_d / 2), 4)}
        print(f"POWER n_val={n_val_sessions} per-arm~{n_val_arm} "
              f"power@discovery={power['power_at_discovery_effect']:.3f} "
              f"power@half={power['power_at_half_effect']:.3f}")
    out["power_at_validation"] = power

    gating = [out["questions"]["Q1_stability"]["pass"], out["questions"]["Q2_regime"]["pass"],
              out["questions"]["Q3_multiplicity"]["pass"]]
    out["verdict"] = "PASS" if all(gating) else "FAIL"
    out["note"] = ("Q4 is reported, never gating. The U6 placebo red is NOT resolved here and is "
                   "carried to the blind Integrity Gate unchanged.")
    print(f"\nVERDICT: {out['verdict']}")
    p = ROOT.parent / "research" / "studies" / "hyp162-statistical-stage-2026-09-14.json"
    p.write_text(json.dumps(out, indent=2, default=str))
    print(f"written -> {p}")


if __name__ == "__main__":
    main()
