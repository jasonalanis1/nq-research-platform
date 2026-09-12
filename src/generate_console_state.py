#!/usr/bin/env python3
"""Emit the live-state JSON the phone console reads from the Artifact database.

Deterministic and cheap on purpose: this does the counting so a session
does not have to reason about it or regenerate any HTML. A work session
runs this, then writes the printed JSON to the console artifact with the
Artifact tool's write_db action (collection "state", doc_id "current").

    python3 src/generate_console_state.py            # print JSON
    python3 src/generate_console_state.py -o s.json  # and write to a file
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from research_ledger import get_current_state  # noqa: E402
from local_time import fmt_central  # noqa: E402

LEDGER = ROOT / "research" / "ledger" / "hypotheses.jsonl"
SESSION_LOG = ROOT / "research" / "_session_log.txt"
SESSIONS_DIR = ROOT / "research" / "sessions"
FORWARD_LOG = ROOT / "research" / "forward_validation" / "h118_forward_log.jsonl"
IDEA_INVENTORY = ROOT / "research" / "idea_inventory.md"
SHELF_FLOOR = 3

# Bookkeeping rows carry a status of their own but are not candidates.
BOOKKEEPING = (
    "_STATUS_CORRECTION",
    "_MULTIPLICITY_REEXPRESSION",
    "_PROGRESSION_POINTER",
    "_INTEGRITY_REVIEW_MULTIPLICITY",
)
# Stage suffixes stripped to group rows belonging to one idea.
STAGE_SUFFIXES = [
    "_prospective_validation",
    "_prospective",
    "_validation",
    "_holdout",
    "_discovery",
    "_excursion",
]
SLICE_ORDER = {
    "discovery": 1,
    "validation": 2,
    "holdout_gen1": 2,
    "holdout_gen2": 3,
    "prospective": 4,
}
# Readable names. Anything unmapped falls back to a de-underscored title.
DISPLAY = {
    "vwap_dist_low_10d_drift_h118": "H118 · VWAP distance LOW tercile, 10-day drift",
    "prospective_validation_weekly_trend_exp047": "EXP-047 · weekly momentum tracker",
    "intraday_overnight_coil_rth_range": "Overnight coil → RTH range",
    "intraday_range_contraction_expansion_cycle": "Range contraction → expansion cycle",
    "midday_lull_afternoon_expansion": "Midday lull → afternoon expansion",
    "nq_weekly_trend_volatility_regime_split_exploratory": "Weekly trend split by volatility regime",
    "collective_evidence_pilot_trend_family": "Trend family collective-evidence pilot",
    "intraday_collective_evidence_pilot": "Intraday collective-evidence pilot",
    "zn_bond_lead_standalone_signal": "ZN bond lead as a standalone signal",
    "intraday_multiday_base_breakout": "Intraday multi-day base breakout",
}


def idea_key(name: str | None) -> str:
    name = name or ""
    changed = True
    while changed:
        changed = False
        for suffix in STAGE_SUFFIXES:
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                changed = True
    return name


def display_name(key: str) -> str:
    return DISPLAY.get(key) or key.replace("_", " ").capitalize()


def build_stages(rows: list[dict]) -> tuple[dict, dict]:
    """Group rows into idea families and place each family at its furthest
    live stage. A family with any REJECTED row is closed -- Validation is
    one shot, so a later rejection closes the idea even though its earlier
    Discovery row may still read PROMISING."""
    families: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        if (row.get("strategy_name") or "").endswith(BOOKKEEPING):
            continue
        families[idea_key(row.get("strategy_name"))].append(row)

    stages: dict[str, list[dict]] = collections.defaultdict(list)
    closed = 0
    for key, family in families.items():
        family.sort(key=lambda r: SLICE_ORDER.get(r.get("data_slice_used"), 0))
        if any((r.get("strategy_status") or "").startswith("REJECT") for r in family):
            closed += 1
            continue
        top = family[-1]
        stages[top.get("data_slice_used") or "discovery"].append(
            {
                "name": display_name(key),
                "id": top.get("hypothesis_id"),
                "status": top.get("strategy_status"),
            }
        )
    for bucket in stages.values():
        bucket.sort(key=lambda c: c["name"])

    funnel = {
        "closed": closed,
        "discovery": len(stages.get("discovery", [])),
        "validation": len(stages.get("validation", [])),
        "holdout": len(stages.get("holdout_gen2", [])) + len(stages.get("holdout_gen1", [])),
        "forward": len(stages.get("prospective", [])) + len(stages.get("holdout_gen2", [])),
        "paper": 0,
        "live": 0,
    }
    return dict(stages), funnel


def read_audit(limit: int = 12) -> list[dict]:
    if not SESSION_LOG.exists():
        return []
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (.*)$")
    entries = []
    for line in SESSION_LOG.read_text(errors="replace").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        date, time, text = match.groups()
        full = text.strip()
        # The phone view is for scanning; the full line is kept so the
        # page can expand it on tap.
        short = full
        if len(full) > 200:
            cut = full.rfind(". ", 0, 200)
            short = (full[: cut + 1] if cut > 120 else full[:197].rstrip() + "…")
        entry = {"ts": f"{date}T{time}Z", "text": short}
        if short != full:
            entry["full"] = full
        entries.append(entry)
    return entries[-limit:][::-1]


AGENT_HEADER = re.compile(
    r"(?m)^(?P<name>[A-Za-z][A-Za-z0-9 /\-\(\),']{1,70}?)\s*(?:--|\u2014)\s*(?P<status>RAN|NOT RUN)\b",
    re.IGNORECASE,
)


def parse_agents(text: str) -> list:
    """Pull the per-agent blocks out of a session report so the console can
    show what each agent actually did, not just how many ran."""
    hits = list(AGENT_HEADER.finditer(text))
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        body = " ".join(text[m.end():end].split())
        status = m.group("status").upper()

        rec_m = re.search(r"Recommendation:\s*([A-Z]{4,8})", body)
        rec = rec_m.group(1) if rec_m else None

        if status == "NOT RUN":
            cond = re.search(
                r"[Ii]nput condition not met\s*(?:--|\u2014|:|,)?\s*(.+?)(?:\.|$)", body
            )
            note = cond.group(1).strip() if cond else "input condition not met"
        else:
            find = re.search(r"Finding:\s*(.+?)(?:\.\s|$)", body)
            note = (find.group(1) if find else body.split(". ")[0]).strip()
        if len(note) > 180:
            note = note[:177].rstrip() + "\u2026"

        out.append({
            "name": m.group("name").strip().rstrip(".:"),
            "status": status,
            "recommendation": rec,
            "note": note,
        })
    return out


def parse_new_information(text: str) -> str:
    """The anti-busy-work line: what this run actually produced."""
    m = re.search(
        r"WHAT NEW INFORMATION THIS RUN PRODUCED[^\n]*\n+(.{10,400}?)(?:\n\n|\n#|$)",
        text, re.IGNORECASE | re.DOTALL,
    )
    return " ".join(m.group(1).split())[:400] if m else ""


def read_sessions(limit: int = 10) -> list[dict]:
    if not SESSIONS_DIR.exists():
        return []
    out = []
    for path in sorted(SESSIONS_DIR.glob("*.md"), reverse=True)[:limit]:
        stem = path.stem  # YYYY-MM-DD-HHMM
        try:
            ts = datetime.strptime(stem, "%Y-%m-%d-%H%M").replace(tzinfo=timezone.utc)
            iso = ts.strftime("%Y-%m-%dT%H:%M:00Z")
        except ValueError:
            iso = None
        text = path.read_text(errors="replace")
        agents = parse_agents(text)
        ran = sum(1 for a in agents if a["status"] == "RAN")
        not_run = sum(1 for a in agents if a["status"] == "NOT RUN")
        meeting = "Convened" in text.split("### Staff meeting")[-1][:200] if "### Staff meeting" in text else False
        returns = "none" not in text.split("### Returns issued")[-1][:120].lower() if "### Returns issued" in text else False
        disposition = None
        found = re.search(r"\*\*Disposition:\s*([A-Z]+)", text)
        if found:
            disposition = found.group(1)
        out.append(
            {
                "file": path.name,
                "ts": iso,
                "agents": agents,
                "new_information": parse_new_information(text),
                "agents_ran": ran,
                "agents_not_run": not_run,
                "staff_meeting": bool(meeting),
                "returns": bool(returns),
                "disposition": disposition,
            }
        )
    return out


def read_forward() -> dict:
    if not FORWARD_LOG.exists():
        return {}
    trades = [json.loads(l) for l in FORWARD_LOG.read_text().splitlines() if l.strip()]
    resolved = [t for t in trades if t.get("status") != "OPEN"]
    open_trades = [t for t in trades if t.get("status") == "OPEN"]
    return {
        "resolved": len(resolved),
        "target_trades": 40,
        "open": len(open_trades),
        "entry": open_trades[0].get("entry_close") if open_trades else None,
        "entry_date": open_trades[0].get("signal_date") if open_trades else None,
        "horizon_days": open_trades[0].get("horizon_days") if open_trades else None,
        "net_points_resolved": sum(t.get("net_points") or 0 for t in resolved),
    }


def running_since() -> str | None:
    """If a work session holds the lock right now, when it took it. Lets
    the console say "a session is working" instead of looking stalled --
    runs take hours and only report at the end."""
    lock = ROOT / "research" / "_worksession.lock"
    if not lock.exists():
        return None
    parts = lock.read_text().strip().split(None, 1)
    if len(parts) != 2 or parts[0].upper() != "RUNNING":
        return None
    try:
        started = datetime.strptime(parts[1].strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return started.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:00Z")


def last_activity() -> str | None:
    """Timestamp of the newest session-log line. The console compares this
    to the lock: a lock still reading RUNNING while nothing has been logged
    for half an hour is a session that died, not a session working."""
    entries = read_audit(limit=1)
    return entries[0]["ts"] if entries else None


def ops_status() -> dict:
    """The Operations Manager's own checks, folded into the console feed.
    Operations is accountable for this console being current (AMENDMENT
    v2.4), so its status belongs where Jason actually looks."""
    try:
        import ops_checks
        results = ops_checks.run_all()
        return {
            "overall": ops_checks.overall(results),
            "checks": [r.as_dict() for r in results],
        }
    except Exception as exc:  # noqa: BLE001
        # Operations must never be able to break the console it owns.
        return {"overall": "WARN", "checks": [
            {"name": "ops-checks", "status": "WARN", "detail": f"could not run: {exc}"}]}


def progress() -> dict:
    """Trials spent since the last survivor -- adopted by staff meeting
    2026-09-10 as the project's progress measure. Guarded: a metric must
    never be able to break the console."""
    try:
        import progress_metric
        return progress_metric.compute()
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def test_status() -> str:
    """Last recorded pytest result, read from the session log rather than
    re-running the suite (a session runs it anyway and logs the outcome)."""
    if not SESSION_LOG.exists():
        return ""
    # Count the tests that actually exist rather than trusting prose in the
    # log -- the console showed 202/202 for hours after the suite reached 227.
    tests_dir = ROOT / "tests"
    if tests_dir.exists():
        n = 0
        for path in tests_dir.glob("test_*.py"):
            n += len(re.findall(r"^def test_", path.read_text(errors="replace"), re.MULTILINE))
        if n:
            return f"{n} tests"
    hits = re.findall(r"(\d+)\s*/\s*(\d+)\s*green", SESSION_LOG.read_text(errors="replace"))
    if not hits:
        return ""
    passed, total = hits[-1]
    return f"{passed} / {total} green"




ENTRY_RE = re.compile(
    r"^## ENTRY (\d+) \u2014 (.*?)$", re.MULTILINE
)


def _clean(text: str) -> str:
    return " ".join(text.split())


def _field(body: str, label: str, max_len: int = 220) -> str:
    """Pull the short numbered-list restatement of a field (e.g. the final
    '1. **STATE VARIABLE**: ...' line), which is always the compact version
    -- the generation-meeting prose above it says the same thing at length.
    Returns "" if the pattern isn't found, so a format drift degrades to a
    missing summary rather than a crash."""
    m = re.search(
        r"\*\*" + re.escape(label) + r"\*\*:\s*(.+?)(?:\n\s*\n|\n\d\.\s*\*\*|$)",
        body, re.DOTALL,
    )
    if not m:
        return ""
    text = _clean(m.group(1))
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "\u2026"
    return text


def parse_shelf() -> dict:
    """Parse research/idea_inventory.md -- the vetted-but-unscanned shelf.
    Entries are large, free-form generation-meeting writeups; this only
    pulls a short display summary per entry, and skips (rather than
    crashes on) any entry it can't parse cleanly, since a work session's
    state-generation must never fail because a human writeup varied in
    format."""
    if not IDEA_INVENTORY.exists():
        return {"floor": SHELF_FLOOR, "count": 0, "live_entries": [], "closed_entries_recent": []}

    text = IDEA_INVENTORY.read_text(errors="replace")
    headers = list(ENTRY_RE.finditer(text))
    live, closed = [], []

    for i, m in enumerate(headers):
        try:
            entry_id = int(m.group(1))
            title_raw = m.group(2).strip()
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            body = text[m.end():end]

            is_closed = (" CLOSED " in (" " + title_raw)) or title_raw.startswith("SHELVED")  # SHELVED = no map anchor, no attempt spent (UPGRADE 1)
            closed_m = re.search(r"\u2014\s*CLOSED\s+(\d{4}-\d{2}-\d{2})\s*(\([^)]*\))?", title_raw)
            if closed_m:
                title = title_raw[: closed_m.start()].strip(" \u2014-")
                closed_date = closed_m.group(1)
                closed_why = closed_m.group(2).strip("()") if closed_m.group(2) else ""
            else:
                title = title_raw
                closed_date, closed_why = None, ""

            state_var = _field(body, "STATE VARIABLE")
            mechanism = _field(body, "MECHANISM CLAIM")

            if is_closed or closed_date:
                # A brief why-it-closed line: prefer the RESULT sentence.
                res_m = re.search(r"RESULT:\s*(.+?)(?:\.\s|\n\n)", body, re.DOTALL)
                why = _clean(res_m.group(1)) if res_m else closed_why
                if len(why) > 220:
                    why = why[:219].rstrip() + "\u2026"
                closed.append({
                    "id": entry_id,
                    "name": title,
                    "closed_date": closed_date,
                    "why": why or closed_why or "closed",
                })
            else:
                if "Not yet drawn or scanned" in body:
                    status = "vetted \u00b7 ready to draw"
                elif re.search(r"DRAWN and run", body):
                    status = "drawn \u00b7 running"
                else:
                    status = "vetted"
                live.append({
                    "id": entry_id,
                    "name": title,
                    "state_variable": state_var,
                    "mechanism": mechanism,
                    "status": status,
                })
        except Exception:  # noqa: BLE001
            # Skip a malformed entry rather than fail the whole script --
            # this feeds an automated session that must never crash here.
            continue

    live.sort(key=lambda e: e["id"])
    closed.sort(key=lambda e: e["id"], reverse=True)

    return {
        "floor": SHELF_FLOOR,
        "count": len(live),
        "floor_met": len(live) >= SHELF_FLOOR,
        "live_entries": live,
        "closed_entries_recent": closed[:4],
    }



SWEEP_JSON = ROOT / "data" / "pipeline_sweep.json"


def read_sweep() -> dict:
    """The pipeline sweep table (src/pipeline_sweep.py --write) is the
    console's tracker now: every live candidate and what it is owed next.
    Hidden rows (stale bookkeeping for an already-closed parent) are
    dropped; everything else is passed through with only display fields."""
    if not SWEEP_JSON.exists():
        return {"shelf": "", "rows": [], "counts": {"OPEN": 0, "GATED": 0, "FROZEN": 0}}
    try:
        raw = json.loads(SWEEP_JSON.read_text())
    except Exception as exc:  # noqa: BLE001
        return {"shelf": "", "rows": [], "counts": {}, "error": str(exc)}
    rows = []
    for r in raw.get("rows", []):
        if r.get("hidden"):
            continue
        rows.append({
            "tier": r.get("tier"),
            "id": r.get("id"),
            "name": {"H118": "H118 \u00b7 VWAP distance LOW tercile, 10-day drift",
                     "EXP047": "EXP-047 \u00b7 weekly momentum tracker"}.get(r.get("id")) or display_name(idea_key(r.get("name"))),
            "stage_reached": r.get("stage_reached"),
            "next_owed": r.get("next_owed"),
            "legacy": bool(r.get("legacy")),
        })
    return {"shelf": raw.get("shelf", ""), "rows": rows, "counts": raw.get("counts", {})}


def waiting_on_jason(sweep: dict) -> list[dict]:
    """Derived, never hand-typed: GATED sweep rows are the only research
    items that can be parked on Jason. 'ready' means the frozen Holdout
    spec and Integrity Gate checkpoint exist; otherwise the cycle is still
    preparing it. The three standing gates (Holdout slot, $5+ spend, live
    capital) are explained on the page as process, not listed here."""
    out = []
    for r in sweep.get("rows", []):
        if r.get("tier") != "GATED":
            continue
        ready = str(r.get("next_owed", "")).startswith("nothing further automated")
        out.append({
            "id": r["id"],
            "name": r["name"],
            "status": "ready for your sign-off" if ready else "being prepared by the cycle",
            "detail": r.get("next_owed", ""),
        })
    return out


def recent_closures(limit: int = 5) -> list[dict]:
    """Last few candidates closed, straight from the ledger -- replaces the
    hand-typed 'Recent kills' list that drifted."""
    if not LEDGER.exists():
        return []
    seen, out = set(), []
    lines = [l for l in LEDGER.read_text().splitlines() if l.strip()]
    for line in reversed(lines):
        try:
            r = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if not (r.get("strategy_status") or "").startswith("REJECT"):
            continue
        name = r.get("strategy_name") or ""
        if name.endswith(BOOKKEEPING):
            continue
        key = idea_key(name)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "id": r.get("hypothesis_id"),
            "name": display_name(key),
            "date": (r.get("logged_at") or "")[:10],
        })
        if len(out) >= limit:
            break
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--out", help="also write JSON to this path")
    args = parser.parse_args()

    rows = get_current_state()
    stages, funnel = build_stages(rows)

    sessions = read_sessions()
    last_run = sessions[0]["ts"] if sessions and sessions[0].get("ts") else None
    # Cadence is now a FIXED recurring cron schedule, not the old
    # self-scheduling send_later chain -- changed 2026-09-11 per Jason:
    # fires on the even UTC hour, every 2 hours (00:00, 02:00, ... 22:00),
    # bound to this persistent session so device access carries over.
    # This makes next_run fully deterministic -- no more reading a
    # session-written timestamp file or estimating from last_run (both of
    # those approaches drifted from the truth; a prior bug from the
    # last_run+2h estimate showed the console 66 minutes off). Simply: the
    # next even UTC top-of-hour strictly after "now".
    now = datetime.now(timezone.utc)
    next_run_dt = now.replace(minute=0, second=0, microsecond=0)
    if next_run_dt <= now:
        next_run_dt += timedelta(hours=1)
    while next_run_dt.hour % 2 != 0:
        next_run_dt += timedelta(hours=1)
    next_run = next_run_dt.strftime("%Y-%m-%dT%H:%M:00Z")

    try:
        shelf = parse_shelf()
    except Exception as exc:  # noqa: BLE001
        shelf = {"error": str(exc), "floor": SHELF_FLOOR, "count": 0,
                 "live_entries": [], "closed_entries_recent": []}

    sweep = read_sweep()
    # Sessions: last 3 only, counts + the new-information line. The per-
    # agent arrays were ~40% of the old document and nobody read them on a
    # phone; the session report on disk keeps the full record.
    slim_sessions = [
        {k: v for k, v in sess.items() if k != "agents"} | {"ts_local": fmt_central(sess["ts"]) if sess.get("ts") else None}
        for sess in sessions[:3]
    ]
    state = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:00Z"),
        "generated_at_local": fmt_central(),
        "last_run": last_run,
        "last_run_local": fmt_central(last_run) if last_run else None,
        "next_run": next_run,
        "next_run_local": fmt_central(next_run),
        "cadence": "Every 2 hours, on the odd Central hour",
        "tests": test_status(),
        "ops": ops_status(),
        "progress": progress(),
        "ledger_rows": sum(1 for l in LEDGER.read_text().splitlines() if l.strip()),
        "distinct_hypotheses": len(rows),
        "funnel": funnel,
        "sweep": sweep,
        "waiting_on_jason": waiting_on_jason(sweep),
        "h118_forward": read_forward(),
        "shelf": {
            "floor": shelf.get("floor", SHELF_FLOOR),
            "count": shelf.get("count", 0),
            "floor_met": shelf.get("floor_met", False),
            "live": [{"id": e["id"], "name": re.sub(r"\s*\(fresh generation meeting.*$", "", e["name"]).strip()}
                     for e in shelf.get("live_entries", [])],
        },
        "recent_closures": recent_closures(),
        "sessions": slim_sessions,
    }

    text = json.dumps(state, indent=1, sort_keys=False)
    print(text)
    if args.out:
        Path(args.out).write_text(text)


if __name__ == "__main__":
    main()
