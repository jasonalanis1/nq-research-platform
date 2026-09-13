"""
idea_factory.py -- THE GENERATION ENGINE (UPGRADE QUEUE v3, U11 expanded + U12).

WHY THIS EXISTS (Jason, 2026-09-13, ~5:30 pm CT): "I don't think we made enough
change towards developing more opportunities to finding and discovering more
strategies." Correct. The first free-look used 4 of the project's 12 available
state measurements, 2 of 5 possible outcomes, and produced a table rather than a
queue. This is the full version.

WHAT IT DOES
  Crosses every market state already on disk x every session window x a full
  outcome battery, on the Discovery slice only, descriptively. It spends no
  hypothesis ID and registers no scan (D8, adopted 2026-09-13). It then
  CLASSIFIES and RANKS every result and emits a CANDIDATE QUEUE -- the strongest
  patterns that are neither circular nor restatements of what is already known.
  A queue entry is a candidate for a mechanism document. It is not a finding.

THE TIMING RULE -- the part that makes this legitimate rather than fishing
  Run 1 of this engine (2026-09-13, ~5:35 pm CT) produced a spectacular top
  result: vwap_dist_vs_atr LOW -> RTH move -0.477 vs +0.023, z = -20.4. It is
  circular. vwap_dist_vs_atr is the close's distance from the session VWAP,
  known AT THE CLOSE: "sessions that end far below their own average price are
  down sessions" is a definition, not a discovery. The same defect sat under the
  opening-range family (the opening range is part of the RTH range it was being
  compared against).

  So every state now carries KNOWN_AT -- the moment its value is actually
  available -- and a state may only be crossed with an outcome window that
  STARTS AT OR AFTER that moment. Everything else is dropped as CIRCULAR before
  ranking. This is the same discipline the pipeline applies to chronological
  leakage, pushed up into generation, where the cost of getting it wrong is a
  queue full of definitions dressed as findings.

THE OUTCOME BATTERY (review A's "ask several questions of the same cut")
  move  net directional change across the window, in ATR14 units
  range high-minus-low across the window, in ATR14 units
  mfe   maximum favourable excursion: furthest above the window's open
  mae   maximum adverse excursion: furthest below the window's open
  tte   time-to-extreme: minutes from window start to its furthest point
  (mfe/mae/tte are the raw material exit rules are designed from.)

CLASSIFICATION
  CIRCULAR   the state is not known until at or after the window it is being
             measured against. Dropped, never ranked.
  KNOWN      restates a validated volatility fact (a size-of-move outcome
             conditioned on one of the three confirmed volatility states).
             Reported separately -- useful to the Risk/State Engine, not new.
  CANDIDATE  everything else clearing the threshold. This is the queue.
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

CANDIDATE_Z = 3.0          # descriptive threshold for the queue, not a test
MIN_N = 120
REALIZED_WINDOW = 20
RUN_DATE = _date.today().isoformat()

# Minutes from midnight on the outcome day. Negative = before that day began.
PRIOR_CLOSE = -480.0        # known the previous evening
OPEN_0930 = 9 * 60 + 30
TEN_AM = 10 * 60
CLOSE_1600 = 16 * 60

# state -> the moment its value is actually known
KNOWN_AT = {
    "range_vs_atr":             PRIOR_CLOSE,   # prior day's range
    "directional_persistence":  PRIOR_CLOSE,   # run of prior closes
    "volume_vs_expected":       PRIOR_CLOSE,   # prior day's volume
    "vxn_level_vs_trailing":    PRIOR_CLOSE,   # prior close's VXN
    "vxn_minus_realized":       PRIOR_CLOSE,   # both legs prior close
    "day_of_week":              PRIOR_CLOSE,   # known forever in advance
    "overnight_range_vs_atr":   OPEN_0930,     # complete only at the RTH open
    "gap_vs_atr":               OPEN_0930,     # needs the open price
    "location_in_range":        OPEN_0930,     # uses the open
    "opening_range_vs_atr":     TEN_AM,        # the first 30 minutes
    "vwap_dist_vs_atr":         CLOSE_1600,    # close vs session VWAP
}
NUMERIC_STATES = [s for s in KNOWN_AT if s != "day_of_week"]

# window -> (start minutes on the outcome day, spec)
WINDOWS = {
    "overnight":  (-360.0, None),                 # prior 18:00 -> 09:30
    "first30":    (OPEN_0930, ("09:30", "10:00")),
    "morning":    (TEN_AM, ("10:00", "11:30")),
    "midday":     (11 * 60 + 30, ("11:30", "13:30")),
    "afternoon":  (13 * 60 + 30, ("13:30", "15:00")),
    "last_hour":  (15 * 60, ("15:00", "16:00")),
    "rth":        (OPEN_0930, ("09:30", "16:00")),
    "next_rth":   (CLOSE_1600, ("09:30", "16:00")),   # the FOLLOWING session
}
OUTCOMES = ["move", "range", "mfe", "mae", "tte"]

# the three confirmed volatility states: a size-of-move result here is a
# restatement of an existing validated fact, not a new candidate
KNOWN_RANGE_STATES = {"range_vs_atr", "overnight_range_vs_atr", "vxn_level_vs_trailing"}
SIZE_OUTCOMES = {"range", "mfe", "mae"}


def classify(state: str, window: str, outcome: str) -> str:
    if KNOWN_AT[state] >= WINDOWS[window][0]:
        return "CIRCULAR"
    if outcome in SIZE_OUTCOMES and state in KNOWN_RANGE_STATES:
        return "KNOWN"
    return "CANDIDATE"


def window_outcomes(disc: pd.DataFrame, days: list) -> pd.DataFrame:
    """One row per trading day; five outcomes per window, raw points/minutes."""
    tz = disc.index.tz
    groups = {k.date(): g for k, g in disc.groupby(disc.index.normalize())}
    rows, prev = [], None
    for d in days:
        g = groups.get(d)
        if g is None:
            prev = d
            continue
        rec = {"date": d}
        for w, (_start, span) in WINDOWS.items():
            if w == "next_rth":
                continue  # filled by shifting rth, below
            if span is None:
                if prev is None:
                    continue
                lo_t = pd.Timestamp(prev, tz=tz).replace(hour=18, minute=0)
                hi_t = pd.Timestamp(d, tz=tz).replace(hour=9, minute=30)
                seg = disc.loc[lo_t:hi_t]
                seg = seg[seg.index < hi_t]
            else:
                seg = g.between_time(span[0], span[1], inclusive="left")
            if len(seg) < 5:
                continue
            o = float(seg["Open"].iloc[0])
            hi, lo = float(seg["High"].max()), float(seg["Low"].min())
            rec[f"move_{w}"] = float(seg["Close"].iloc[-1]) - o
            rec[f"range_{w}"] = hi - lo
            rec[f"mfe_{w}"] = hi - o
            rec[f"mae_{w}"] = o - lo
            up, dn = hi - o, o - lo
            tgt = seg["High"].idxmax() if up >= dn else seg["Low"].idxmin()
            rec[f"tte_{w}"] = (tgt - seg.index[0]).total_seconds() / 60.0
        rows.append(rec)
        prev = d
    out = pd.DataFrame(rows).set_index("date")
    for k in OUTCOMES:                       # next session = today's rth, shifted back
        if f"{k}_rth" in out:
            out[f"{k}_next_rth"] = out[f"{k}_rth"].shift(-1)
    return out


def main() -> None:
    df, synthetic = load_price_data(context="idea_factory")
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    disc = get_discovery_data(df)

    states = extend_state_frame(build_state_frame(disc), disc)
    idx = pd.to_datetime(pd.Index(states.index))

    vxn = _load_vxn_daily(); vxn.index = pd.to_datetime(vxn.index)
    close = pd.Series(states["Close"].to_numpy(dtype=float), index=idx)
    realized = np.log(close).diff().rolling(REALIZED_WINDOW, min_periods=REALIZED_WINDOW).std() * np.sqrt(252) * 100
    states["vxn_minus_realized"] = vxn.reindex(idx, method="ffill").shift(1).values - realized.shift(1).values

    out = window_outcomes(disc, [pd.Timestamp(d).date() for d in states.index])
    out.index = pd.to_datetime(out.index)
    atr = pd.Series(states["atr14"].to_numpy(dtype=float), index=idx)
    keep = [c for c in KNOWN_AT if c in states.columns]
    both = out.join(atr.rename("atr14"), how="inner").join(states[keep].set_axis(idx), how="inner")
    both = both[both["atr14"] > 0]

    for w in WINDOWS:
        for k in ("move", "range", "mfe", "mae"):
            c = f"{k}_{w}"
            if c in both:
                both[c] = both[c] / both["atr14"]

    edges = {}
    for s in NUMERIC_STATES:
        if s not in both:
            continue
        v = both[s].replace([np.inf, -np.inf], np.nan).dropna()
        if len(v) < 300:
            continue
        lo, hi = np.nanpercentile(v, [100 / 3, 200 / 3])
        edges[s] = (float(lo), float(hi))
        both[f"{s}_g"] = np.where(both[s] <= lo, "LOW", np.where(both[s] >= hi, "HIGH", "MID"))
        both.loc[both[s].isna(), f"{s}_g"] = np.nan
    if "day_of_week" in both:
        both["day_of_week_g"] = both["day_of_week"].map({0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"})

    rows, n_circ = [], 0
    group_states = [s for s in NUMERIC_STATES if s in edges] + (["day_of_week"] if "day_of_week_g" in both else [])
    for w in WINDOWS:
        for k in OUTCOMES:
            c = f"{k}_{w}"
            if c not in both:
                continue
            allv = both[c].replace([np.inf, -np.inf], np.nan).dropna()
            if len(allv) < 300:
                continue
            mu, sd = float(allv.mean()), float(allv.std(ddof=1))
            if not np.isfinite(sd) or sd == 0:
                continue
            for s in group_states:
                cls = classify(s, w, k)
                col = f"{s}_g"
                for lvl in sorted(set(both[col].dropna())):
                    sub = both.loc[both[col] == lvl, c].replace([np.inf, -np.inf], np.nan).dropna()
                    if len(sub) < MIN_N:
                        continue
                    if cls == "CIRCULAR":
                        n_circ += 1
                        continue
                    z = (float(sub.mean()) - mu) / (sd / np.sqrt(len(sub)))
                    rows.append({"state": s, "level": str(lvl), "window": w, "outcome": k,
                                 "n": int(len(sub)), "mean": round(float(sub.mean()), 4),
                                 "all_mean": round(mu, 4), "z": round(float(z), 2), "class": cls})

    cands = sorted([r for r in rows if r["class"] == "CANDIDATE" and abs(r["z"]) >= CANDIDATE_Z], key=lambda r: -abs(r["z"]))
    known = sorted([r for r in rows if r["class"] == "KNOWN" and abs(r["z"]) >= CANDIDATE_Z], key=lambda r: -abs(r["z"]))
    fams = {}
    for r in cands:
        fams.setdefault((r["state"], r["outcome"]), []).append(r)
    families = sorted(fams.items(), key=lambda kv: -max(abs(x["z"]) for x in kv[1]))

    res = {"run_date": RUN_DATE, "slice": "discovery", "n_days": int(len(both)),
           "cells_ranked": len(rows), "cells_dropped_circular": n_circ,
           "states": group_states, "windows": list(WINDOWS), "outcomes": OUTCOMES,
           "candidate_z": CANDIDATE_Z, "min_n": MIN_N, "known_at": KNOWN_AT,
           "tercile_edges": edges, "rows": rows, "candidate_queue": cands,
           "known_restatements": known,
           "rule": "descriptive only; no hypothesis id spent; no scan registered; "
                   "a queue entry is a candidate for a mechanism doc, not a finding"}
    (ROOT.parent / "data" / f"idea_factory_{RUN_DATE}.json").write_text(json.dumps(res, indent=2, default=str))

    L = [f"# Idea Factory — candidate queue, {RUN_DATE}", "",
         f"Discovery slice only. **{len(rows)} descriptive cells ranked**, "
         f"**{n_circ} dropped as circular** by the timing rule, across "
         f"{len(group_states)} market states × {len(WINDOWS)} windows × {len(OUTCOMES)} outcomes.", "",
         "No hypothesis ID spent. No scan registered. **Nothing below is a finding.** Each",
         "queue entry is a candidate for a mechanism document, which is what licenses a test.", "",
         "**The timing rule:** every state carries the moment its value is actually known, and",
         "may only be crossed with a window starting at or after it. Run 1 of this engine",
         "ranked `vwap_dist_vs_atr` (close vs session VWAP, known at the close) against the",
         "same session's move at z = −20.4 — a definition restated. The rule drops it, and",
         f"{n_circ} cells like it, before ranking.", "",
         f"Thresholds: |z| ≥ {CANDIDATE_Z} vs all days in the same window, n ≥ {MIN_N}.", "",
         f"## Candidate queue — {len(cands)} cells in {len(families)} families", ""]
    if families:
        for (s, k), items in families:
            top = items[0]
            L += [f"### {s} → {k} ({len(items)} cells, strongest |z| {abs(top['z']):.1f})", "",
                  "| level | window | n | mean | all-days | z |", "|---|---|---:|---:|---:|---:|"]
            L += [f"| {r['level']} | {r['window']} | {r['n']} | {r['mean']:+.3f} | {r['all_mean']:+.3f} | {r['z']:+.1f} |" for r in items]
            L.append("")
    else:
        L += ["(nothing cleared the threshold)", ""]
    L += ["## Known restatements (not new — these feed the Risk/State Engine)", "",
          "| state | level | window | outcome | n | mean | all-days | z |", "|---|---|---|---|---:|---:|---:|---:|"]
    L += [f"| {r['state']} | {r['level']} | {r['window']} | {r['outcome']} | {r['n']} | {r['mean']:+.3f} | {r['all_mean']:+.3f} | {r['z']:+.1f} |" for r in known[:40]]
    p = ROOT.parent / "research" / "observatory" / f"idea-factory-{RUN_DATE}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(L) + "\n")

    print(f"days={len(both)} ranked={len(rows)} dropped_circular={n_circ} "
          f"candidates={len(cands)} in {len(families)} families | known={len(known)}")
    print("\nCANDIDATE FAMILIES (descriptive, untested):")
    for (s, k), items in families[:15]:
        t = items[0]
        print(f"  {s:26s} -> {k:5s}  best {t['level']:4s}/{t['window']:9s} n={t['n']:4d} "
              f"mean={t['mean']:+.3f} vs {t['all_mean']:+.3f} z={t['z']:+.1f}  ({len(items)} cells)")
    dirf = [(kk, it) for kk, it in families if kk[1] == "move"]
    print(f"\nDIRECTION families in the queue: {len(dirf)}")
    for (s, k), items in dirf:
        t = items[0]
        print(f"  {s:26s} best {t['level']:4s}/{t['window']:9s} n={t['n']:4d} mean={t['mean']:+.3f} vs {t['all_mean']:+.3f} z={t['z']:+.1f}")


if __name__ == "__main__":
    main()
