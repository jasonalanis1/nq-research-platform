"""
director_reeval_hyp156.py -- DIRECTOR RE-EVALUATION, hyp-000156
(M23: the London-open volatility burst in 6E).

Owed since the Statistical stage passed (September 13th). The Director's question
is **"is it NEW, and is it worth spending the rest of the pipeline on?"** -- not
"is it real", which Statistical settled (+0.0537 ATR, ci_90 +0.0426/+0.0670,
stable across halves and regimes, survives Sidak at N=451).

Precedent for the bar: H116 retained 98% and advanced; hyp-000140 retained 32%
and the Director ruled REAL IS NOT NEW.

THE SPECIFIC DOUBT THIS CANDIDATE ARRIVES WITH
The claim is that ONE named hour (03:00-04:00 ET, the London open) is more
volatile than the day's own average hour. In FX that is close to the most
textbook fact there is: London is the largest session. So the claim is only
NEW if the London hour is distinguishable from **the general shape of the
24-hour clock in 6E** -- if every non-US hour looks like this, the finding is
"session boundaries are volatile", which is knowledge the project can get for
free and must not spend a hypothesis attempt or a data purchase on.

THE TEST -- the hour-of-day profile, computed the candidate's own way
The frozen statistic is re-computed for EVERY hour of the 24-hour clock:
    |return over the hour| / ATR14  -  that day's mean US-RTH hourly |return| / ATR14
with the candidate's own ATR convention (trailing 14-session mean of the
09:30-16:00 range, shifted one session) and its own block bootstrap
(block=10, N_BOOT=3000, seed 20260913). Then three readings:

  R1  WHERE DOES THE LONDON HOUR RANK among all 24? Rank 1 is what the claim
      implicitly asserts; anything else weakens it considerably.
  R2  IS IT SEPARABLE FROM ITS NEIGHBOURS? The spread between the London hour
      and the next-highest hour, with a paired block-bootstrap interval on the
      DIFFERENCE. If the interval contains zero, the hour is not distinguishable
      from the rest of the European morning and the honest claim is the broader,
      cheaper one.
  R3  HOW MANY HOURS CLEAR THE SAME BAR? If a dozen hours are individually
      credible, the candidate is one member of a family, not a fact.

Discovery only (the 6E file on disk covers 2015-01-01 -> 2021-10-03; the
Validation slice has never been fetched and is parked on Jason). Nothing here
re-tests the claim; it asks what the claim is worth.

HOW TO RUN:  python3 src/director_reeval_hyp156.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from data_loader import read_price_csv  # noqa: E402

DATA = ROOT.parent / "data" / "6E_1min_databento_2026-09-07.csv"
OUT = ROOT.parent / "research" / "studies" / "hyp156-director-reeval-2026-09-14.json"
ATR_WINDOW, BLOCK, N_BOOT, SEED, ALPHA = 14, 10, 3000, 20260913, 0.10
LONDON_HOUR = 3          # 03:00-04:00 ET, the frozen window


def hour_profile(df: pd.DataFrame) -> pd.DataFrame:
    """One row per session, one column per hour of the ET clock, each holding
    that hour's |return|/ATR14 minus the day's mean US-RTH hourly |return|/ATR14."""
    rows = []
    for day, g in df.groupby(df.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if len(rth) < 200:
            continue
        rows.append({"date": pd.Timestamp(day), "rth_range": float(rth["High"].max() - rth["Low"].min())})
    daily = pd.DataFrame(rows).set_index("date").sort_index()
    daily["atr14"] = daily["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    atr_by = daily["atr14"].to_dict()

    out = []
    for day, g in df.groupby(df.index.date):
        ts = pd.Timestamp(day)
        atr = atr_by.get(ts)
        if atr is None or not np.isfinite(atr) or atr <= 0:
            continue
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if len(rth) < 200:
            continue
        uncond = []
        for h in range(9, 16):                      # the candidate's own baseline
            sub = rth.between_time(f"{h:02d}:30", f"{h + 1:02d}:30", inclusive="left")
            if len(sub) >= 30:
                uncond.append(abs(float(sub["Close"].iloc[-1]) - float(sub["Open"].iloc[0])) / atr)
        if not uncond:
            continue
        rec = {"date": ts, "uncond": float(np.mean(uncond))}
        for h in range(24):
            sub = g.between_time(f"{h:02d}:00", f"{(h + 1) % 24:02d}:00", inclusive="left")
            rec[h] = (abs(float(sub["Close"].iloc[-1]) - float(sub["Open"].iloc[0])) / atr - rec["uncond"]
                      if len(sub) >= 30 else np.nan)
        out.append(rec)
    return pd.DataFrame(out).set_index("date").sort_index()


def _block_idx(n: int, rng) -> np.ndarray:
    nb = int(np.ceil(n / BLOCK))
    starts = rng.integers(0, max(1, n - BLOCK + 1), size=nb)
    return (starts[:, None] + np.arange(BLOCK)[None, :]).reshape(-1)[:n]


def bootstrap(prof: pd.DataFrame, hours: list[int]) -> dict:
    """Per-hour mean and CI, plus the PAIRED difference between the London hour
    and the best other hour -- all on the same resample, so the difference has an
    honest interval."""
    arr = prof[hours].to_numpy(float)
    n = len(arr)
    rng = np.random.default_rng(SEED)
    means = np.full((N_BOOT, len(hours)), np.nan)
    for b in range(N_BOOT):
        idx = _block_idx(n, rng)
        means[b] = np.nanmean(arr[idx], axis=0)
    point = np.nanmean(arr, axis=0)
    lo = np.nanpercentile(means, 100 * ALPHA / 2, axis=0)
    hi = np.nanpercentile(means, 100 * (1 - ALPHA / 2), axis=0)

    li = hours.index(LONDON_HOUR)
    others = [i for i in range(len(hours)) if i != li]
    best_other = others[int(np.nanargmax(point[others]))]
    diff = means[:, li] - means[:, best_other]
    return {
        "per_hour": [{"hour_et": h, "point": round(float(point[i]), 5),
                      "ci_90": [round(float(lo[i]), 5), round(float(hi[i]), 5)],
                      "credible_above_zero": bool(lo[i] > 0)} for i, h in enumerate(hours)],
        "london_rank": int(1 + sum(1 for i in range(len(hours)) if point[i] > point[li])),
        "best_other_hour_et": hours[best_other],
        "london_minus_best_other": {"point": round(float(point[li] - point[best_other]), 5),
                                    "ci_90": [round(float(np.percentile(diff, 5)), 5),
                                              round(float(np.percentile(diff, 95)), 5)],
                                    "separable": bool(np.percentile(diff, 5) > 0)},
        "n_hours_credible_above_zero": int(sum(1 for i in range(len(hours)) if lo[i] > 0)),
        "n_sessions": int(n),
    }


def main() -> int:
    df = read_price_csv(DATA)
    prof = hour_profile(df)
    hours = [h for h in range(24) if prof[h].notna().sum() >= 200]
    res = bootstrap(prof.dropna(subset=hours), hours)
    res["hours_evaluated"] = hours
    res["note"] = ("Discovery only. The frozen statistic re-computed for every hour of the ET "
                   "clock with the candidate's own ATR and bootstrap conventions.")
    OUT.write_text(json.dumps(res, indent=2))
    for r in sorted(res["per_hour"], key=lambda x: -x["point"])[:8]:
        star = "  <== LONDON (frozen window)" if r["hour_et"] == LONDON_HOUR else ""
        print(f"  {r['hour_et']:02d}:00 ET  {r['point']:+.4f}  ci {r['ci_90']}  {star}")
    print(f"\nLondon rank: {res['london_rank']} of {len(hours)}")
    print(f"vs best other hour ({res['best_other_hour_et']:02d}:00): "
          f"{res['london_minus_best_other']['point']:+.4f} "
          f"ci {res['london_minus_best_other']['ci_90']} -> "
          f"{'SEPARABLE' if res['london_minus_best_other']['separable'] else 'NOT separable'}")
    print(f"hours individually credible above zero: {res['n_hours_credible_above_zero']} of {len(hours)}")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
