"""
revamp_list.py -- the REVAMP LIST (standing directive s.9): every closed
hypothesis in research/ledger/hypotheses.jsonl, ranked by
  (a) CLOSENESS  -- how near the effect's interval came to clearing, and
  (b) MECHANISM  -- how good its mechanism story was,
then sorted into TOP (near-misses with a real mechanism: get a full strategy
specified and screened), MIDDLE (passed Discovery but "nowhere to go" -- the
EIA and ECB volatility findings; parked, noted, not worked) and BOTTOM (clean
nulls with no mechanism, and anything whose only story was a published
calendar anomaly: stays dead, never resurrected).

Output: research/ledger/revamp_list.json (production-guarded). Discovery
maintains it; a revamp candidate enters research/ledger/strategies.jsonl at
SOURCE like any other and competes on the Director's priority order (s.9:
no separate lane).

HOW THE TWO SCORES ARE COMPUTED -- and which parts are a JUDGMENT
  (a) closeness, 0..1, MECHANICAL: from every 90% interval the ledger row
      carries (parameters.*ci* lists, or "ci_90=(lo,hi)" / "CI (lo,hi)" in the
      notes) take the fraction of the interval lying on ONE side of zero,
      f in [0.5, 1]; closeness = 2*(f - 0.5), so an interval straddling zero
      symmetrically scores 0 and one whose edge touches zero scores 1. Rows
      with no interval fall back on expectancy_r (positive 0.3, else 0.1;
      unknown 0). The best interval on the row wins -- the gating cell is
      not always labelled, so this errs toward generosity.
  (b) mechanism, JUDGMENT (this cycle's, stated so it can be argued with):
      HIGH 1.0  a mechanism doc exists (research/mechanisms/) and names a
                counterparty or a forced flow;
      LOW  0.15 the doc itself says "no single named counterparty" / "weaker
                mechanism story" (the published calendar anomalies: M28 pre-
                holiday, M32 DST, M33 weekend, M34 Santa, M35 semi-monthly --
                and by the same reading turn-of-month, day-of-week, opex-day
                calendar cuts with no flow doc);
      MED  0.5  no doc (pre-Mechanism-Gate) but a practitioner or Jason
                hypothesis with a stated reason (external_claim /
                jason_hypothesis origin);
      LOW  0.15 no doc and a state-library / derivative / R&D-generated scan
                (data_discovered, rd_generated, derivative) -- a raw effect.
  score = closeness * mechanism. Tier: TOP if score >= 0.40 or named by the
  directive (M24 hyp-000157, H118's lineage, hyp-000162 as a sizing INPUT,
  Stack A hyp-000161); MIDDLE if the directive names it (EIA hyp-000148,
  ECB hyp-000150) or it closed as Monetization "no credible path" on a
  non-NQ instrument; BOTTOM otherwise, and ALWAYS bottom when mechanism is
  LOW (a calendar anomaly cannot climb on closeness alone).

USAGE
    TONY_PRODUCTION=1 python3 src/revamp_list.py --write
    python3 src/revamp_list.py            # print, no write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from production_paths import assert_writable  # noqa: E402

LEDGER = ROOT / "research" / "ledger" / "hypotheses.jsonl"
MECHANISMS = ROOT / "research" / "mechanisms"
OUT = ROOT / "research" / "ledger" / "revamp_list.json"

CLOSED = ("REJECTED", "VALIDATED_NOT_PROMOTED")
TOP_SCORE = 0.40
MECH = {"HIGH": 1.0, "MED": 0.5, "LOW": 0.15}

# directive s.9 names these explicitly
FORCED_TOP = {
    "hyp-000157": "month-end payment-cycle reversal (M24) -- directive s.9 names it: full strategy",
    "hyp-000121": "H118 VWAP-drift lineage -- directive s.9: re-measure against the CORRECT baseline (NQ's own drift over the same horizon, not zero)",
    "hyp-000122": "H118 lineage (see hyp-000121)", "hyp-000123": "H118 lineage (see hyp-000121)",
    "hyp-000162": "opening-range width -> midday excursion -- directive s.9: a STOP/SIZING INPUT, not a standalone strategy",
    "hyp-000161": "Stack A (B2 expected-range context x B3 breakout) -- directive s.9 names it",
    "hyp-000159": "Level Sweep Reversal x prior-day compression (M26) -- directive s.7: first through Salvage (S001)",
    "hyp-000145": "overnight-vs-intraday split (M15) -- directive s.7: second through Salvage (S002)",
}
FORCED_MIDDLE = {
    "hyp-000148": "EIA report volatility (CL, M20) -- passed Discovery, no CL book: parked, noted, not worked",
    "hyp-000150": "ECB decision volatility (6E, M21) -- passed Discovery, no 6E book: parked, noted, not worked",
}
CALENDAR_WORDS = ("holiday", "dst", "weekend", "monday", "santa", "semi_monthly", "turn_of_month", "day_of_week",
                  "opex", "expiration", "witching", "month_end", "turn-of")
CI_RE = re.compile(r"[Cc][Ii](?:_?90)?\s*[=:]?\s*[\(\[]\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)\s*[\)\]]")


def _load() -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for line in LEDGER.read_text().splitlines():
        if line.strip():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            latest[r["hypothesis_id"]] = r
    return latest


def _intervals(row: dict) -> list[tuple[float, float]]:
    out = []
    for k, v in (row.get("parameters") or {}).items():
        if "ci" in k.lower() and isinstance(v, list) and len(v) == 2:
            try:
                out.append((float(v[0]), float(v[1])))
            except (TypeError, ValueError):
                pass
    for m in CI_RE.finditer(row.get("notes") or ""):
        out.append((float(m.group(1)), float(m.group(2))))
    return [(lo, hi) for lo, hi in out if hi > lo]


def closeness(row: dict) -> tuple[float, str]:
    best, basis = None, ""
    for lo, hi in _intervals(row):
        w = hi - lo
        f = max(hi, 0.0) / w if lo < 0 < hi else 1.0     # fraction above zero, clipped
        f = max(f, 1.0 - f)                                # the side with more mass
        c = round(2 * (f - 0.5), 3)
        if best is None or c > best:
            best, basis = c, f"best interval ({lo:+.4g}, {hi:+.4g}): {f:.0%} on one side of zero"
    if best is not None:
        if best >= 0.999:
            basis += " -- a credible cell; the hypothesis closed on another cell or rule"
        return best, basis
    e = row.get("expectancy_r")
    if e is None:
        return 0.0, "no interval and no expectancy on the row"
    return (0.3 if e > 0 else 0.1), f"no interval; expectancy_r {e:+.3f}"


GENERIC_WORDS = {"discovery", "validation", "prospective", "excursion", "drift", "range", "volume", "reversal",
                 "effect", "tercile", "daily", "next", "high", "low", "open", "close", "first", "last", "mid",
                 "status", "correction", "pointer", "multiplicity", "reexpression", "integrity", "review",
                 "progression", "day", "same", "with", "return", "returns", "signal", "study", "regime", "week",
                 "session", "intraday", "weekly", "monthly", "conditioned", "continuation", "fade", "check"}
LOW_PHRASES = ("no single named counterparty", "weaker mechanism story", "no single named forced",
               "no-named-counterparty", "weaker\nmechanism story")


def _words(name: str) -> list[str]:
    return [w for w in re.split(r"[_\-]", name.lower()) if len(w) > 3 and w not in GENERIC_WORDS and not w.isdigit()]


def _doc_for(row: dict) -> Path | None:
    """The mechanism doc for a row: by map anchor (-m##) first, breaking a
    shared anchor by name overlap; otherwise by distinctive-word overlap with
    the doc stem (at least 2 words and at least half the row's words) -- strict
    on purpose, a wrong doc would hand a raw effect a mechanism it never had."""
    name = (row.get("strategy_name") or "")
    notes = (row.get("notes") or "")
    anchors = set(re.findall(r"\bm(\d{1,2})\b", name.lower())) | set(re.findall(r"\bM(\d{1,2})\b", notes))
    ma = (row.get("parameters") or {}).get("map_anchor")
    if ma:
        anchors |= set(re.findall(r"(\d+)", str(ma)))
    docs = [p for p in MECHANISMS.glob("*.md") if p.stem not in ("README", "TEMPLATE")]
    words = _words(name)
    cands = []
    for p in docs:
        m = re.search(r"-m(\d{1,2})$", p.stem)
        if m and m.group(1) in anchors:
            cands.append((sum(1 for w in words if w in p.stem), p))
    if cands:
        return max(cands, key=lambda x: x[0])[1]
    best = None
    for p in docs:
        hits = sum(1 for w in words if w in p.stem)
        if words and hits >= 2 and hits * 2 >= len(words) and (best is None or hits > best[0]):
            best = (hits, p)
    return best[1] if best else None


def mechanism(row: dict) -> tuple[str, str]:
    doc = _doc_for(row)
    name = (row.get("strategy_name") or "").lower()
    if doc is not None:
        txt = doc.read_text(errors="replace").lower()
        if any(ph in txt for ph in LOW_PHRASES):
            return "LOW", f"doc {doc.name} says no single named counterparty (published calendar anomaly)"
        return "HIGH", f"doc {doc.name} names a counterparty / flow"
    if any(w in name for w in CALENDAR_WORDS):
        return "LOW", "calendar cut with no mechanism doc"
    if row.get("strategy_origin") in ("external_claim", "jason_hypothesis"):
        return "MED", "no mechanism doc (pre-Gate); practitioner / Jason hypothesis with a stated reason"
    return "LOW", f"no mechanism doc; {row.get('strategy_origin')} scan -- a raw effect"


def build(latest: dict[str, dict] | None = None) -> dict:
    latest = latest or _load()
    entries = []
    for hid, r in latest.items():
        st = r.get("strategy_status") or ""
        if st not in CLOSED and hid not in FORCED_TOP:
            continue
        if (r.get("strategy_name") or "").endswith(("_STATUS_CORRECTION", "_MULTIPLICITY_REEXPRESSION",
                                                    "_PROGRESSION_POINTER", "_INTEGRITY_REVIEW_MULTIPLICITY")):
            continue      # ledger bookkeeping rows, not hypotheses
        c, cb = closeness(r)
        mq, mb = mechanism(r)
        score = round(c * MECH[mq], 3)
        if hid in FORCED_TOP:
            tier, why = "top", FORCED_TOP[hid]
        elif hid in FORCED_MIDDLE:
            tier, why = "middle", FORCED_MIDDLE[hid]
        elif "no credible path" in (r.get("notes") or "").lower() and any(x in (r.get("strategy_name") or "").lower() for x in ("_cl_", "_6e_", "_zn_", "_es_", "_rty_")):
            tier, why = "middle", "passed Discovery on a non-NQ instrument, Monetization: no credible path -- parked"
        elif mq == "LOW":
            tier, why = "bottom", "stays dead: " + mb
        elif score >= TOP_SCORE:
            tier, why = "top", f"near-miss (closeness {c}) with a real mechanism"
        else:
            tier, why = "bottom", f"clean null (closeness {c}), not resurrected"
        entries.append({"hypothesis_id": hid, "name": r.get("strategy_name"), "status": st,
                        "slice": r.get("data_slice_used"), "expectancy_r": r.get("expectancy_r"),
                        "closeness": c, "closeness_basis": cb, "mechanism": mq, "mechanism_basis": mb,
                        "score": score, "tier": tier, "disposition": why})
    entries.sort(key=lambda e: (-{"top": 2, "middle": 1, "bottom": 0}[e["tier"]], -e["score"], e["hypothesis_id"]))
    tiers = {t: [e["hypothesis_id"] for e in entries if e["tier"] == t] for t in ("top", "middle", "bottom")}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rule": "standing directive s.9 (2026-09-15): rank closed hypotheses by closeness x mechanism; "
                "top = full strategy specified and screened; middle = parked, noted, not worked; bottom = stays dead",
        "judgment_note": "mechanism quality is Discovery's JUDGMENT read from each mechanism doc's counterparty "
                         "section (or its absence); closeness is mechanical from the row's intervals. Both bases are printed per row.",
        "counts": {t: len(v) for t, v in tiers.items()}, "tiers": tiers, "entries": entries,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    d = build()
    print(f"revamp list: {len(d['entries'])} closed hypotheses -- top {d['counts']['top']}, middle {d['counts']['middle']}, bottom {d['counts']['bottom']}")
    for e in d["entries"]:
        if e["tier"] != "bottom":
            print(f"  [{e['tier']:<6}] {e['hypothesis_id']} {e['name'][:60]:<60} close={e['closeness']:.2f} mech={e['mechanism']:<4} score={e['score']:.2f} -- {e['disposition'][:80]}")
    if a.write:
        assert_writable(OUT, "revamp list")
        OUT.write_text(json.dumps(d, indent=1, default=str) + "\n")
        print(f"written -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
