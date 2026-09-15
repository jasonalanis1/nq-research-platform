"""Cycle budget clock + resume checkpoint + per-cycle value snapshot.

Jason, September 11th ~9:55 pm CT: (1) use as much of the 2-hour cadence as is
safe; (2) if a cycle hits its budget mid-task the NEXT cycle must pick up
where it left off, never error or half-corrupt; (3) alert when cycles are doing
busy work or the queue is exhausted.

Files (research/):
  _cycle_checkpoint.json  -- the running cycle's item/step/files; status
                             running|done. A "running" checkpoint with a FREE
                             lock = unfinished work the next cycle resumes.
  _cycle_history.jsonl    -- one line per closed cycle: objective counts
                             (ledger rows, registered scans, mechanism docs,
                             studies, inventory entries, closed entries) plus
                             `moved`, which ops_checks reads for BUSY WORK.

MOVEMENT (redefined September 15th, Jason's refocus memo 7.1): a cycle MOVED
only if a candidate CHANGED STAGE -- a ledger row whose (status, data slice)
differs from that hypothesis's previous latest row, or a hypothesis appearing
in the ledger for the first time -- or a scan was registered, or a bot
milestone in docs/BOT_ROADMAP.md flipped. Shelf/inventory additions, new
studies and new mechanism docs count ZERO: batch screening added 25 inventory
rows while discovering nothing and the old activity-based rule passed it.
The counts are still recorded for information; only `stage_changes`,
`scans_registered` and `bot_milestones_flipped` decide `moved`.

Usage:
  python3 src/cycle_budget.py start --minutes 105 [--note "..."]
  python3 src/cycle_budget.py checkpoint --item "Entry 12" --step "scan written, not run" [--files a.py,b.md]
  python3 src/cycle_budget.py remaining      -> prints minutes; exit 0 ok, 3 = <=15 min (CLOSE OUT NOW), 4 = over budget
  python3 src/cycle_budget.py done           -> marks done, appends the value snapshot
  python3 src/cycle_budget.py status         -> prints the checkpoint (for the next cycle's step 2)
"""
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "research"
CKPT = R / "_cycle_checkpoint.json"
HIST = R / "_cycle_history.jsonl"
CLOSE_OUT_MINUTES = 15


def _now() -> datetime:
    return datetime.now(timezone.utc)


MOVEMENT_KEYS = ("stage_changes", "scans_registered", "bot_milestones_flipped")
_MILESTONE_DONE_WORDS = ("DONE", "LIVE", "WIRED", "BUILT")


def ledger_stage_map(ledger: Path) -> dict:
    """hypothesis_id -> 'STATUS|slice' of its LATEST row. The stage of record
    is the latest row per id (NEXT_UP: 'the LEDGER's latest row per
    hypothesis_id is the status of record')."""
    out = {}
    if not ledger.exists():
        return out
    for line in ledger.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        hid = r.get("hypothesis_id")
        if hid:
            out[hid] = f"{r.get('strategy_status')}|{r.get('data_slice_used')}"
    return out


def bot_milestone_map(roadmap: Path) -> dict:
    """B-id -> 'done'|'open' from docs/BOT_ROADMAP.md's table (same words
    session_report.product() uses, so the two cannot disagree)."""
    if not roadmap.exists():
        return {}
    txt = roadmap.read_text(errors="ignore")
    out = {}
    for m in re.finditer(r"^\| (B\d[a-z]?) \| ([^|]+?) \|([^|]*)\|", txt, re.M):
        su = m.group(3).upper()
        out[m.group(1)] = "done" if any(w in su for w in _MILESTONE_DONE_WORDS) else "open"
    return out


def stage_changes(before: dict, after: dict) -> int:
    """Candidates whose stage of record differs, or that entered the ledger."""
    return sum(1 for hid, st in (after or {}).items() if (before or {}).get(hid) != st)


def snapshot() -> dict:
    """Objective counts of research artifacts -- the value ruler -- plus the
    two maps movement is judged on (ledger stage per candidate, bot
    milestone status)."""
    ledger = R / "ledger" / "hypotheses.jsonl"
    rows = [l for l in ledger.read_text().splitlines() if l.strip()] if ledger.exists() else []
    inv = (R / "idea_inventory.md").read_text(errors="ignore") if (R / "idea_inventory.md").exists() else ""
    reg = (ROOT / "src" / "project_wide_multiplicity.py").read_text(errors="ignore")
    return {
        "ledger_rows": len(rows),
        "scans_registered": len(re.findall(r'^\s*"scan_\d+_\d{4}-\d{2}-\d{2}":', reg, re.M)),
        "mechanism_docs": len(list((R / "mechanisms").glob("*.md"))) - 2,   # minus README + TEMPLATE
        "studies": len(list((R / "studies").glob("*.md"))),
        "inventory_entries": len(re.findall(r"^## ENTRY \d+", inv, re.M)),
        "inventory_closed": len(re.findall(r"^## ENTRY \d+ — .*CLOSED", inv, re.M)),
        "ledger_stages": ledger_stage_map(ledger),
        "bot_milestones": bot_milestone_map(ROOT / "docs" / "BOT_ROADMAP.md"),
    }


def movement(s0: dict, s1: dict) -> tuple:
    """(moved, delta) under the stage-change rule. `delta` carries every
    count for information; `moved` reads only MOVEMENT_KEYS."""
    counts = {k: s1[k] - s0.get(k, s1[k]) for k in s1 if isinstance(s1[k], int)}
    if "ledger_stages" in s0:
        counts["stage_changes"] = stage_changes(s0.get("ledger_stages"), s1.get("ledger_stages"))
    else:
        # a checkpoint started before the stage-change rule existed (2026-09-15)
        # has no stage map; rows added is the only honest proxy for that one cycle
        counts["stage_changes"] = max(counts.get("ledger_rows", 0), 0)
    b0, b1 = s0.get("bot_milestones") or {}, s1.get("bot_milestones") or {}
    counts["bot_milestones_flipped"] = sum(1 for k, v in b1.items() if b0.get(k, v) != v)
    moved = any(counts.get(k, 0) > 0 for k in MOVEMENT_KEYS)
    return moved, counts


def _read() -> dict:
    return json.loads(CKPT.read_text()) if CKPT.exists() else {}


def cmd_start(a):
    CKPT.write_text(json.dumps({"status": "running", "started": _now().isoformat(), "budget_minutes": a.minutes,
                                "note": a.note or "", "item": None, "step": None, "files": [], "snapshot_at_start": snapshot()}, indent=1))
    print(f"budget started: {a.minutes} min")


def cmd_checkpoint(a):
    c = _read()
    if not c:
        print("no running budget; run start first"); return 2
    c.update({"item": a.item, "step": a.step, "files": [f for f in (a.files or "").split(",") if f], "checkpoint_at": _now().isoformat()})
    CKPT.write_text(json.dumps(c, indent=1)); print(f"checkpoint: {a.item} -- {a.step}")


def cmd_remaining(_a):
    c = _read()
    if not c or c.get("status") != "running":
        print("no running budget"); return 2
    used = (_now() - datetime.fromisoformat(c["started"])).total_seconds() / 60
    left = c["budget_minutes"] - used
    print(f"{left:.0f} min left of {c['budget_minutes']} (used {used:.0f})")
    if left <= 0:
        print("OVER BUDGET -- checkpoint and close out immediately"); return 4
    if left <= CLOSE_OUT_MINUTES:
        print("CLOSE OUT NOW -- do not start a new stage"); return 3
    return 0


def cmd_done(_a):
    c = _read()
    if not c:
        print("no checkpoint"); return 2
    c["status"] = "done"; c["finished"] = _now().isoformat(); c["snapshot_at_end"] = snapshot()
    CKPT.write_text(json.dumps(c, indent=1))
    s0, s1 = c.get("snapshot_at_start", {}), c["snapshot_at_end"]
    moved, delta = movement(s0, s1)
    with HIST.open("a") as f:
        f.write(json.dumps({"started": c["started"], "finished": c["finished"], "delta": delta, "moved": moved,
                            "movement_rule": "stage-change (refocus 7.1, 2026-09-15)"}) + "\n")
    print(f"cycle done; moved={moved} (stage-change rule) delta={delta}")


def cmd_status(_a):
    c = _read()
    if not c:
        print("NO CHECKPOINT"); return 0
    if c.get("status") == "running":
        print(f"UNFINISHED: started {c['started']} item={c.get('item')} step={c.get('step')} files={c.get('files')}"); return 1
    print(f"done at {c.get('finished')}"); return 0


def main(argv=None):
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); s.add_argument("--minutes", type=int, default=105); s.add_argument("--note", default="")
    s = sub.add_parser("checkpoint"); s.add_argument("--item", required=True); s.add_argument("--step", required=True); s.add_argument("--files", default="")
    sub.add_parser("remaining"); sub.add_parser("done"); sub.add_parser("status")
    a = p.parse_args(argv)
    return {"start": cmd_start, "checkpoint": cmd_checkpoint, "remaining": cmd_remaining, "done": cmd_done, "status": cmd_status}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
