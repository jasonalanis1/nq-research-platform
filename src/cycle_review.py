#!/usr/bin/env python3
"""
cycle_review.py -- "did every cycle today actually run everything?"

Reads research/_cycle_compliance.jsonl (one row per cycle, written by
src/cycle_close.py) and prints a day's cycles side by side. Built 2026-09-14
because Jason is letting the day run unattended and wants to review the whole
day in one place in the evening, rather than reading six session reports and
inferring the rest from file timestamps -- which is how the previous day's
skipped daily checkers were eventually found.

It reports, per cycle: whether the opening sequence ran and was clean, whether
the tests passed, ops_checks' verdict, whether the work was committed AND
pushed, whether the lock was released, and what the cycle actually moved.

A cycle that never called cycle_close.py has NO ROW AT ALL -- and that absence
is itself the finding, so expected cycle times are listed and missing ones are
called out rather than silently omitted.

    python3 src/cycle_review.py                 # today
    python3 src/cycle_review.py --date 2026-09-14
    python3 src/cycle_review.py --json          # for the console
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPLIANCE = ROOT / "research" / "_cycle_compliance.jsonl"

CT_OFFSET = timedelta(hours=-5)            # America/Chicago, CDT
EXPECTED_CT_HOURS = list(range(1, 24, 2))  # the standing cadence: odd Central hours


def _ct(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc) + CT_OFFSET


def _ct_label(h: int) -> str:
    suffix = "am" if h < 12 else "pm"
    display = h % 12 or 12
    return f"{display}:00 {suffix}"


def load_rows() -> list:
    if not COMPLIANCE.exists():
        return []
    out = []
    for line in COMPLIANCE.read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except Exception:  # noqa: BLE001
                pass
    return out


def build(day_ct: str, now_ct: datetime | None = None) -> dict:
    """`now_ct` is injectable so a test can fix "what time is it" without
    monkeypatching _ct, which is also used to place each row on the clock --
    patching it globally moved the rows too, and the test silently passed for
    the wrong reason."""
    rows = []
    for r in load_rows():
        try:
            closed = datetime.fromisoformat(r["closed_at"])
        except Exception:  # noqa: BLE001
            continue
        ct = _ct(closed)
        if ct.date().isoformat() != day_ct:
            continue
        r["_ct"] = ct
        rows.append(r)
    rows.sort(key=lambda r: r["_ct"])

    now_ct = now_ct or _ct(datetime.now(timezone.utc))
    is_today = now_ct.date().isoformat() == day_ct
    # a cycle is "due" once its hour has passed (plus a little slack to close)
    due = [h for h in EXPECTED_CT_HOURS
           if (not is_today) or (now_ct.hour > h) or (now_ct.hour == h and now_ct.minute > 45)]
    covered = {r["_ct"].hour for r in rows} | {(r["_ct"].hour - 1) for r in rows}
    missing = [h for h in due if h not in covered]

    complete = [r for r in rows if r.get("complete")]
    moved = [r for r in rows if r.get("moved")]
    return {"date_ct": day_ct, "rows": rows, "due": due, "missing_hours": missing,
            "n_cycles": len(rows), "n_complete": len(complete), "n_moved": len(moved)}


def render(d: dict) -> str:
    L = [f"CYCLE REVIEW — {d['date_ct']} (Central)", "=" * 88]
    if not d["rows"]:
        L.append("No cycle has recorded a close today.")
    else:
        L.append(f"{'closed':<9} {'cycle':<12} {'pre':<5} {'test':<6} {'ops':<6} "
                 f"{'git':<6} {'lock':<6} {'moved':<6} notes")
        L.append("-" * 88)
        for r in d["rows"]:
            c = r.get("checks", {})
            def m(k):
                v = c.get(k, {})
                return "ok" if v.get("ok") else ("skip" if v.get("skipped") else "FAIL")
            notes = []
            if c.get("ops", {}).get("warning"):
                notes.append("warn:" + ",".join(c["ops"]["warning"][:2]))
            if c.get("preflight", {}).get("sourcing_owed"):
                notes.append("sourcing owed")
            if r.get("delta"):
                notes.append(json.dumps(r["delta"]))
            L.append(f"{r['_ct'].strftime('%H:%M'):<9} {(r.get('label') or '-')[:12]:<12} "
                     f"{m('preflight'):<5} {m('tests'):<6} {m('ops'):<6} {m('git'):<6} "
                     f"{m('lock'):<6} {str(r.get('moved')):<6} {'; '.join(notes)[:30]}")
    L.append("")
    L.append(f"cycles recorded: {d['n_cycles']}   fully complete: {d['n_complete']}   "
             f"moved the pipeline: {d['n_moved']}")
    if d["missing_hours"]:
        L.append("")
        L.append("*** CYCLES WITH NO RECORDED CLOSE (due but never closed out): "
                 + ", ".join(_ct_label(h) for h in d["missing_hours"]))
        L.append("    A cycle with no row either never fired, or fired and never reached")
        L.append("    cycle_close.py. Both are failures worth knowing about.")
    else:
        L.append("every cycle due so far has a recorded close.")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD in Central time; default today")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    day = a.date or _ct(datetime.now(timezone.utc)).date().isoformat()
    d = build(day)
    if a.json:
        out = {k: v for k, v in d.items() if k != "rows"}
        out["rows"] = [{kk: vv for kk, vv in r.items() if kk != "_ct"} | {"ct": r["_ct"].strftime("%H:%M")}
                       for r in d["rows"]]
        print(json.dumps(out, indent=1, default=str))
        return
    print(render(d))


if __name__ == "__main__":
    main()
