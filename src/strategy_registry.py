"""
strategy_registry.py -- the single record of every candidate in the standing
directive's loop (research/infrastructure/standing-directive-2026-09-15.md s.2).

    SOURCE -> SPECIFY -> FREEZE -> SCREEN -> PAPER -> JUDGE -> KEEP / FIX_ONCE / KILL
                                                           KILL -> SALVAGE -> (new candidate) | LEARN
                                                           KEEP -> P1 -> P2 -> P3 -> P4 -> P5

FILE: research/ledger/strategies.jsonl -- append-only, one row per stage EVENT,
production-guarded (src/production_paths.py: a writer needs TONY_PRODUCTION=1 or
an entry point that called enable_production()). The stage of record for a
strategy is its LATEST row, exactly the convention the hypothesis ledger uses.
Nothing here is ever edited or deleted: a correction is a new row that says so.

ROW SHAPE
  ts              ISO timestamp (UTC), filled in by append() if absent
  strategy_id     "S001", "S001a" (a Salvage spawn), ...
  name            plain-language name
  stage           one of STAGES
  spec_hash       {"spec": sha256, "module": sha256} at FREEZE (and echoed later)
  screen_result   {"trades", "net_usd_1_micro", "net_r", "avg_r", "win_rate", ...} at SCREEN
  verdict         at JUDGE stages (KEEP/FIX_ONCE/KILL) the verdict + numbers; at
                  SALVAGE the salvage result ("condition found: ..." | "nothing")
  notes           free text (why it moved, what was learned)
  source_channel  where the candidate came from (s.2 SOURCE priority list)
  lineage         hypothesis ids / map anchor / parent strategy_id
  priority        Director's queue order (lower first); optional
  paper_log_name  the STRATEGY_NAME the paper loop writes into
                  research/forward_validation/bot_stack_paper_log.jsonl rows, once known
  paper_key       the --strategy key in bot_stack_paper_run.STRATEGIES, once registered

The Salvage queue and the revamp list are NOT separate stores: the Salvage queue
is every strategy whose latest stage is KILL without a later SALVAGE row; the
revamp list (directive s.9) is research/ledger/revamp_list.json, built by
src/revamp_list.py from the hypothesis ledger, and a revamp candidate enters
this registry at SOURCE like any other.

USAGE
    python3 src/strategy_registry.py                # print the queue + paper book stages
    TONY_PRODUCTION=1 python3 src/strategy_registry.py append --id S001 --name "..." \
        --stage SOURCE --notes "..." --source-channel salvage --lineage "hyp-000159 / M26"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from production_paths import assert_writable, enable_production  # noqa: E402

REGISTRY = ROOT / "research" / "ledger" / "strategies.jsonl"

STAGES = ("SOURCE", "SPECIFY", "FREEZE", "SCREEN", "PAPER", "JUDGE",
          "KEEP", "FIX_ONCE", "KILL", "SALVAGE",
          "P1", "P2", "P3", "P4", "P5", "LEARN")
QUEUE_STAGES = ("SOURCE", "SPECIFY", "FREEZE", "SCREEN")     # not yet in paper, still moving
PAPER_STAGES = ("PAPER", "FIX_ONCE", "KEEP", "P1", "P2")     # a paper record is accumulating
VERDICT_STAGES = ("KEEP", "FIX_ONCE", "KILL")
CLOSED_STAGES = ("LEARN",)

# The paper log also carries PLUMBING rows: the execution dummy (a fill-collection
# placeholder, Jason's decision September 15th: labelled a plumbing test, its
# record kept separate, never judged) and the B3 ORB placeholder. They are not
# candidates and never appear in this registry as one.
PLUMBING_LOG_NAMES = ("execution_dummy_4x_placeholder", "base_entry_b3_orb_placeholder")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_rows(path: Path | None = None) -> list[dict]:
    p = path or REGISTRY
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def append(row: dict, path: Path | None = None) -> dict:
    """Validate and append one stage event. Returns the row as written."""
    p = path or REGISTRY
    stage = row.get("stage")
    if stage not in STAGES:
        raise ValueError(f"stage {stage!r} is not one of {STAGES}")
    if not row.get("strategy_id"):
        raise ValueError("strategy_id is required")
    if not row.get("name"):
        raise ValueError("name is required")
    if stage == "FREEZE" and not (isinstance(row.get("spec_hash"), dict) and row["spec_hash"].get("spec")):
        raise ValueError("a FREEZE row must carry spec_hash={'spec': sha256, 'module': sha256}")
    if stage == "SCREEN" and not isinstance(row.get("screen_result"), dict):
        raise ValueError("a SCREEN row must carry screen_result")
    if stage in VERDICT_STAGES and not row.get("verdict"):
        raise ValueError(f"a {stage} row must carry the verdict and the numbers that produced it")
    out = dict(row)
    out.setdefault("ts", _now())
    out.setdefault("notes", "")
    p.parent.mkdir(parents=True, exist_ok=True)
    assert_writable(p, "strategy registry")
    with p.open("a") as f:
        f.write(json.dumps(out, default=str) + "\n")
    return out


def latest(rows: list[dict]) -> dict[str, dict]:
    """strategy_id -> its latest row (stage of record), in first-seen order."""
    out: dict[str, dict] = {}
    for r in rows:
        sid = r.get("strategy_id")
        if sid:
            out[sid] = r
    return out


def history(rows: list[dict], strategy_id: str) -> list[dict]:
    return [r for r in rows if r.get("strategy_id") == strategy_id]


def in_paper(rows: list[dict]) -> list[dict]:
    """Strategies whose record is accumulating in the paper engine right now."""
    return [r for r in latest(rows).values() if r.get("stage") in PAPER_STAGES]


def queue(rows: list[dict]) -> list[dict]:
    """Candidates not yet in paper, Director priority order (priority asc, then
    first-seen order). A strategy at SALVAGE is not in the queue -- its spawn is."""
    lat = latest(rows)
    order = {sid: i for i, sid in enumerate(lat)}
    q = [r for r in lat.values() if r.get("stage") in QUEUE_STAGES]
    return sorted(q, key=lambda r: (r.get("priority") if r.get("priority") is not None else 1e9,
                                    order[r["strategy_id"]]))


def salvage_queue(rows: list[dict]) -> list[dict]:
    """KILLED strategies still owed their Salvage check (directive s.7)."""
    out = []
    for sid, r in latest(rows).items():
        if r.get("stage") == "KILL":
            out.append(r)
    return out


def stage_map(rows: list[dict]) -> dict[str, str]:
    """strategy_id -> stage, for the movement rule (cycle_budget.py)."""
    return {sid: r.get("stage") for sid, r in latest(rows).items()}


def count_events(rows: list[dict]) -> dict:
    """Verdicts issued and Salvage checks completed, for the movement rule."""
    verdicts = sum(1 for r in rows if r.get("stage") in VERDICT_STAGES)
    salvages = sum(1 for r in rows if r.get("stage") == "SALVAGE" and r.get("verdict"))
    return {"verdicts": verdicts, "salvage_checks": salvages, "rows": len(rows)}


def summary_lines(rows: list[dict]) -> list[str]:
    lat = latest(rows)
    lines = [f"strategy registry: {len(lat)} strategies, {len(rows)} events"]
    q = queue(rows)
    lines.append(f"  queue (not yet in paper, Director order): " +
                 (", ".join(f"{r['strategy_id']} {r['stage']}" for r in q) if q else "empty"))
    p = in_paper(rows)
    lines.append(f"  in paper: " + (", ".join(f"{r['strategy_id']} {r['stage']}" for r in p) if p else "none"))
    s = salvage_queue(rows)
    lines.append(f"  salvage owed: " + (", ".join(r["strategy_id"] for r in s) if s else "none"))
    closed = [r for r in lat.values() if r.get("stage") in CLOSED_STAGES]
    lines.append(f"  closed to LEARN: " + (", ".join(r["strategy_id"] for r in closed) if closed else "none"))
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("append")
    a.add_argument("--id", required=True); a.add_argument("--name", required=True)
    a.add_argument("--stage", required=True, choices=STAGES)
    a.add_argument("--notes", default=""); a.add_argument("--source-channel", default="")
    a.add_argument("--lineage", default=""); a.add_argument("--priority", type=int, default=None)
    a.add_argument("--verdict", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "append":
        row = {"strategy_id": args.id, "name": args.name, "stage": args.stage, "notes": args.notes,
               "source_channel": args.source_channel, "lineage": args.lineage}
        if args.priority is not None:
            row["priority"] = args.priority
        if args.verdict:
            row["verdict"] = args.verdict
        print(json.dumps(append(row), default=str))
        return 0
    for ln in summary_lines(read_rows()):
        print(ln)
    return 0


if __name__ == "__main__":
    enable_production()
    raise SystemExit(main())
