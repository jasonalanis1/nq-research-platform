"""
observatory_free_look.py -- UPGRADE QUEUE v3 item U11 (adopted 2026-09-13, decision D8).

THE RULE THIS IMPLEMENTS (from outside review D, adopted by Jason):
  Let the Observatory LOOK at Discovery data before anyone writes a mechanism.
  Descriptive only. Spends NO hypothesis ID. Registers NO scan. Nothing here is a
  result. Anything that shows a footprint goes through the normal path afterward:
  mechanism doc -> registered family (cells counted in SCAN_REGISTRY) -> one scan
  -> Statistical -> ... The confirmation slices (Validation/Holdout) are what
  protect the project, not a pre-written story.

WHAT IT DOES: cuts NQ by WHEN (session windows) x STATE (the project's own
validated volatility facts plus the two VXN-derived states), on the DISCOVERY slice
only, and prints one table: for each state tercile x window, the mean net move and
mean range (both in ATR14 units), n, and a z-score against all days in that window.
A |z| >= FOOTPRINT_Z is flagged as a FOOTPRINT -- a candidate for a mechanism doc,
NOT a finding. No bootstrap, no CI, no gating: that is deliberately reserved for the
registered scan that may follow.

Also produces M29's Stage-0 output (implied-minus-realized vol gap) and its overlap
with the VXN-level tercile (the duplicate check the M29 doc requires).

Windows (America/New_York): overnight 18:00(prev)-09:30 | first30 09:30-10:00 |
morning 10:00-11:30 | midday 11:30-13:30 | afternoon 13:30-15:00 | last_hour 15:00-16:00.
States (terciles fixed on the Discovery slice, computed once):
  range_vs_atr (prior-day range; LOW = compressed, the hyp-048 fact),
  overnight_range_vs_atr (LOW = coil, the hyp-057 fact),
  vxn_level_vs_trailing (HIGH = the hyp-142 fact),
  vxn_minus_realized (M29 Stage 0: VXN(t-1) - trailing-20d realized vol, annualized %).
Outputs: data/observatory_free_look_<date>.json and research/observatory/free-look-<date>.md
"""
from __future__ import annotations

import json
import sys
from datetime import date as _date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
from market_state_primitives import build_state_frame  # noqa: E402
from market_state_primitives_v2 import extend_state_frame, _load_vxn_daily  # noqa: E402

FOOTPRINT_Z = 2.5
REALIZED_WINDOW = 20
WINDOWS = {
    "overnight": None,  # special: prev 18:00 -> 09:30
    "first30": ("09:30", "10:00"),
    "morning": ("10:00", "11:30"),
    "midday": ("11:30", "13:30"),
    "afternoon": ("13:30", "15:00"),
    "last_hour": ("15:00", "16:00"),
}
STATES = ["range_vs_atr", "overnight_range_vs_atr", "vxn_level_vs_trailing", "vxn_minus_realized"]
RUN_DATE = _date.today().isoformat()
OUT_JSON = ROOT.parent / "data" / f"observatory_free_look_{RUN_DATE}.json"
OUT_MD = ROOT.parent / "research" / "observatory" / f"free-look-{RUN_DATE}.md"


def window_outcomes(disc: pd.DataFrame, days: list) -> pd.DataFrame:
    """One row per trading day: move_<w>, range_<w> in raw points."""
    tz = disc.index.tz
    day_groups = {k.date(): g for k, g in disc.groupby(disc.index.normalize())}
    rows = []
    prev = None
    for d in days:
        g = day_groups.get(d)
        if g is None:
            prev = d
            continue
        rec = {"date": d}
        for w, span in WINDOWS.items():
            if span is None:
                if prev is None:
                    continue
                start = pd.Timestamp(prev, tz=tz).replace(hour=18, minute=0)
                end = pd.Timestamp(d, tz=tz).replace(hour=9, minute=30)
                seg = disc.loc[start:end]
                seg = seg[seg.index < end]
            else:
                seg = g.between_time(span[0], span[1], inclusive="left")
            if len(seg) < 5:
                continue
            rec[f"move_{w}"] = float(seg["Close"].iloc[-1] - seg["Open"].iloc[0])
            rec[f"range_{w}"] = float(seg["High"].max() - seg["Low"].min())
        rows.append(rec)
        prev = d
    return pd.DataFrame(rows).set_index("date")


def main() -> None:
    df, synthetic = load_price_data(context="observatory_free_look")
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    disc = get_discovery_data(df)

    states = extend_state_frame(build_state_frame(disc), disc)
    # M29 Stage 0: implied minus realized (annualized %, both on the prior day)
    vxn = _load_vxn_daily()
    vxn.index = pd.to_datetime(vxn.index)
    idx = pd.to_datetime(pd.Index(states.index))
    daily_close = pd.Series(states["Close"].to_numpy(dtype=float), index=idx)
    logret = np.log(daily_close).diff()
    realized = logret.rolling(REALIZED_WINDOW, min_periods=REALIZED_WINDOW).std() * np.sqrt(252) * 100
    vxn_prior = vxn.reindex(idx, method="ffill").shift(1)
    states["vxn_minus_realized"] = (vxn_prior.values - realized.reindex(idx).shift(1).values)

    days = [pd.Timestamp(d).date() for d in states.index]
    out = window_outcomes(disc, days)
    out.index = pd.to_datetime(out.index)
    atr = states["atr14"].copy(); atr.index = idx
    both = out.join(atr, how="inner").join(states[STATES].set_axis(idx), how="inner")
    both = both[both["atr14"] > 0]
    for w in WINDOWS:
        for k in ("move", "range"):
            c = f"{k}_{w}"
            if c in both:
                both[c] = both[c] / both["atr14"]

    # terciles fixed on the Discovery slice, once
    terc = {}
    for s in STATES:
        v = both[s].dropna()
        lo, hi = np.nanpercentile(v, [100 / 3, 200 / 3])
        terc[s] = (float(lo), float(hi))
        both[f"{s}_terc"] = np.where(both[s] <= lo, "LOW", np.where(both[s] >= hi, "HIGH", "MID"))
        both.loc[both[s].isna(), f"{s}_terc"] = np.nan

    table, footprints = [], []
    for w in WINDOWS:
        for k in ("move", "range"):
            c = f"{k}_{w}"
            if c not in both:
                continue
            allv = both[c].dropna()
            mu_all, sd_all = float(allv.mean()), float(allv.std(ddof=1))
            for s in STATES:
                for t in ("LOW", "MID", "HIGH"):
                    sub = both.loc[both[f"{s}_terc"] == t, c].dropna()
                    if len(sub) < 30:
                        continue
                    z = (float(sub.mean()) - mu_all) / (sd_all / np.sqrt(len(sub)))
                    row = {"window": w, "outcome": k, "state": s, "tercile": t, "n": int(len(sub)),
                           "mean": round(float(sub.mean()), 4), "all_days_mean": round(mu_all, 4),
                           "z_vs_all": round(float(z), 2), "footprint": bool(abs(z) >= FOOTPRINT_Z)}
                    table.append(row)
                    if row["footprint"]:
                        footprints.append(row)

    # M29 duplicate check: overlap of gap tercile with VXN-level tercile
    a, b = both["vxn_minus_realized_terc"], both["vxn_level_vs_trailing_terc"]
    m = a.notna() & b.notna()
    overlap = float((a[m] == b[m]).mean())
    corr = float(both[["vxn_minus_realized", "vxn_level_vs_trailing"]].dropna().corr().iloc[0, 1])

    result = {"run_date": RUN_DATE, "slice": "discovery", "n_days": int(len(both)),
              "footprint_z": FOOTPRINT_Z, "tercile_edges": terc, "rows": table,
              "footprints": footprints,
              "m29_stage0": {"gap_vs_vxnlevel_tercile_overlap": overlap, "corr": corr,
                              "duplicate_if_overlap_gt": 0.80, "duplicate": overlap > 0.80},
              "rule": "descriptive only; no hypothesis id spent; no scan registered; footprints are candidates for a mechanism doc, not findings"}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, default=str))

    # markdown
    L = [f"# Observatory free-look — {RUN_DATE} (Discovery slice, descriptive only)", "",
         "Rule (D8, adopted 2026-09-13): this table spends no hypothesis ID and registers no scan.",
         "A FOOTPRINT (|z| >= 2.5 vs all days in the same window) is a candidate for a mechanism",
         "doc and a registered family — it is NOT a finding. Units: ATR14 multiples.", "",
         f"Days: {len(both)}. Tercile edges (Discovery, fixed once): " +
         "; ".join(f"{s} LOW<={terc[s][0]:.3f} HIGH>={terc[s][1]:.3f}" for s in STATES), "",
         "## Footprints", ""]
    if footprints:
        L += ["| window | outcome | state | tercile | n | mean | all-days mean | z |", "|---|---|---|---|---:|---:|---:|---:|"]
        L += [f"| {r['window']} | {r['outcome']} | {r['state']} | {r['tercile']} | {r['n']} | {r['mean']:+.3f} | {r['all_days_mean']:+.3f} | {r['z_vs_all']:+.1f} |" for r in
              sorted(footprints, key=lambda r: -abs(r["z_vs_all"]))]
    else:
        L.append("(none)")
    L += ["", "## M29 Stage 0 — implied-minus-realized gap vs VXN-level",
          f"Tercile overlap with vxn_level_vs_trailing: {overlap:.1%} (duplicate if > 80%) → "
          f"{'DUPLICATE — close M29' if overlap > 0.8 else 'DISTINCT — M29 may proceed to a registered family'}; corr {corr:+.2f}.", "",
          "## Full table (every state × tercile × window)", "",
          "| window | outcome | state | tercile | n | mean | z |", "|---|---|---|---|---:|---:|---:|"]
    L += [f"| {r['window']} | {r['outcome']} | {r['state']} | {r['tercile']} | {r['n']} | {r['mean']:+.3f} | {r['z_vs_all']:+.1f} |" for r in table]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"days={len(both)} rows={len(table)} footprints={len(footprints)} m29_overlap={overlap:.3f} corr={corr:+.2f}")
    for r in sorted(footprints, key=lambda r: -abs(r["z_vs_all"]))[:25]:
        print(f"  {r['window']:10s} {r['outcome']:6s} {r['state']:24s} {r['tercile']:4s} n={r['n']:4d} mean={r['mean']:+.3f} all={r['all_days_mean']:+.3f} z={r['z_vs_all']:+.1f}")


if __name__ == "__main__":
    main()
