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

MOVEMENT (redefined AGAIN September 15th by the STANDING OPERATING DIRECTIVE,
research/infrastructure/standing-directive-2026-09-15.md s.3, which replaces
the refocus memo's 7.1 rule): a cycle MOVED only if
  * a candidate CHANGED STAGE in the loop -- its latest row in
    research/ledger/strategies.jsonl (the strategy registry) has a different
    stage than before, or a strategy appears in the registry for the first time;
  * a PAPER TRADE was recorded -- a new bookkept fill (pnl_usd row) for a
    CANDIDATE strategy in research/forward_validation/bot_stack_paper_log.jsonl
    (plumbing rows -- execution dummy, B3 -- count zero);
  * a VERDICT was issued (a KEEP / FIX_ONCE / KILL registry row); or
  * a SALVAGE CHECK was completed (a SALVAGE registry row carrying its result).
Mechanism docs, shelf entries, study files, inventory rows, hypothesis-ledger
rows and scan registrations still count ZERO. Every count is recorded for
information; only MOVEMENT_KEYS decide `moved`.

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from production_paths import assert_writable, enable_production  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "research"
CKPT = R / "_cycle_checkpoint.json"
HIST = R / "_cycle_history.jsonl"
CLOSE_OUT_MINUTES = 15


def _now() -> datetime:
    return datetime.now(timezone.utc)


MOVEMENT_KEYS = ("stage_changes", "paper_trades_recorded", "verdicts_issued", "salvage_checks_completed")
MOVEMENT_RULE = "standing directive s.3 (2026-09-15): stage change / paper trade / verdict / salvage check"
_MILESTONE_DONE_WORDS = ("DONE", "LIVE", "WIRED", "BUILT")


def registry_state() -> dict:
    """The strategy registry's stage map and event counts, plus the candidate
    paper-trade count -- the four things movement is judged on."""
    try:
        import strategy_registry as sr
        rows = sr.read_rows()
        stages = sr.stage_map(rows)
        ev = sr.count_events(rows)
    except Exception:  # noqa: BLE001
        stages, ev = {}, {"verdicts": 0, "salvage_checks": 0, "rows": 0}
    try:
        import paper_book as pb
        log = pb.load_log()
        trades = sum(1 for r in log if "pnl_usd" in r and pb.log_name(r) not in pb.PLUMBING_LOG_NAMES)
    except Exception:  # noqa: BLE001
        trades = 0
    return {"registry_stages": stages, "registry_rows": ev["rows"], "verdicts": ev["verdicts"],
            "salvage_checks": ev["salvage_checks"], "candidate_paper_trades": trades}


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
        **registry_state(),
    }


def movement(s0: dict, s1: dict) -> tuple:
    """(moved, delta) under the standing directive's s.3 rule. `delta` carries
    every count for information; `moved` reads only MOVEMENT_KEYS:
      stage_changes            candidates whose REGISTRY stage differs / new strategies
      paper_trades_recorded    new candidate fills bookkept in the paper log
      verdicts_issued          new KEEP / FIX_ONCE / KILL rows
      salvage_checks_completed new SALVAGE rows with a result
    Hypothesis-ledger stage changes, scan registrations and bot-milestone flips
    are still counted (ledger_stage_changes, scans_registered,
    bot_milestones_flipped) for information only."""
    counts = {k: s1[k] - s0.get(k, s1[k]) for k in s1 if isinstance(s1[k], int) and not isinstance(s1[k], bool)}
    counts["ledger_stage_changes"] = stage_changes(s0.get("ledger_stages"), s1.get("ledger_stages")) if "ledger_stages" in s0 else 0
    b0, b1 = s0.get("bot_milestones") or {}, s1.get("bot_milestones") or {}
    counts["bot_milestones_flipped"] = sum(1 for k, v in b1.items() if b0.get(k, v) != v)
    # the four movement counts (a snapshot taken before the registry existed has
    # no registry_* keys; every s1 count is then measured against zero)
    counts["stage_changes"] = stage_changes(s0.get("registry_stages"), s1.get("registry_stages"))
    counts["paper_trades_recorded"] = max(0, s1.get("candidate_paper_trades", 0) - s0.get("candidate_paper_trades", 0))
    counts["verdicts_issued"] = max(0, s1.get("verdicts", 0) - s0.get("verdicts", 0))
    counts["salvage_checks_completed"] = max(0, s1.get("salvage_checks", 0) - s0.get("salvage_checks", 0))
    for k in ("candidate_paper_trades", "verdicts", "salvage_checks", "registry_rows"):
        counts.pop(k, None)
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
    assert_writable(HIST, "cycle history")
    with HIST.open("a") as f:
        f.write(json.dumps({"started": c["started"], "finished": c["finished"], "delta": delta, "moved": moved,
                            "movement_rule": MOVEMENT_RULE}) + "\n")
    print(f"cycle done; moved={moved} ({MOVEMENT_RULE}) delta={ {k: v for k, v in delta.items() if v} }")


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
    enable_production()
    sys.exit(main())
