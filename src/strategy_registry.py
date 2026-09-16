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
  slow            bool, set on the PAPER row (Amendment 1, Jason, September 16th
                  2026): the strategy's own SCREEN result projects fewer than 40
                  paper trades in six months, so it trades in the BACKGROUND,
                  takes NO QUEUE SLOT, and is judged whenever it reaches 40
                  trades. The label is sticky -- the latest row that carries a
                  `slow` key wins, exactly like `stage`.
  slow_projection {"trades", "sessions_screened", "trades_per_session",
                  "projected_trades_6_months"} -- the arithmetic behind `slow`

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

# --- the SLOW label (Amendment 1, Jason, September 16th 2026) ---------------
# At SCREEN time the strategy's own screen result gives its expected paper trade
# rate: trades / sessions_screened. Six months is about 126 trading sessions. If
# rate * 126 < 40 the strategy can never reach a judgeable 40 trades on the
# six-week clock, so it is labelled SLOW when it enters PAPER: it keeps trading
# in the background, does NOT occupy a queue slot, and is judged whenever it
# reaches 40 trades. NOTHING is ever judged on fewer than 40 trades, SLOW or not.
SLOW_HORIZON_SESSIONS = 126     # ~six months of trading sessions
SLOW_MIN_TRADES = 40            # the only number a verdict is ever taken at


def slow_projection(trades: int, sessions_screened: int) -> dict:
    """The Amendment 1 arithmetic, from a strategy's own SCREEN result."""
    trades = int(trades or 0)
    sessions = int(sessions_screened or 0)
    rate = (trades / sessions) if sessions > 0 else 0.0
    projected = rate * SLOW_HORIZON_SESSIONS
    return {"trades": trades, "sessions_screened": sessions,
            "trades_per_session": round(rate, 6),
            "projected_trades_6_months": round(projected, 2),
            "horizon_sessions": SLOW_HORIZON_SESSIONS,
            "min_trades": SLOW_MIN_TRADES,
            "slow": projected < SLOW_MIN_TRADES}


def is_slow_by_screen(trades: int, sessions_screened: int) -> bool:
    """rate * 126 < 40 -> SLOW. A strategy with no screened sessions is SLOW
    (nothing projects it to 40 trades), which is the conservative label."""
    return bool(slow_projection(trades, sessions_screened)["slow"])


def slow_ids(rows: list[dict]) -> set:
    """Strategy ids currently labelled SLOW. Latest row carrying a `slow` key
    wins, so the label can be set and (by Jason's rule change only) unset."""
    state: dict[str, bool] = {}
    for r in rows:
        sid = r.get("strategy_id")
        if sid and "slow" in r:
            state[sid] = bool(r["slow"])
    return {sid for sid, v in state.items() if v}


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
    if "slow" in row and not isinstance(row["slow"], bool):
        raise ValueError("`slow` must be a bool (Amendment 1's SLOW label)")
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
    """Strategies whose record is accumulating in the paper engine right now,
    SLOW ones included -- they are still in paper, just not on a clock."""
    return [r for r in latest(rows).values() if r.get("stage") in PAPER_STAGES]


def in_paper_slow(rows: list[dict]) -> list[dict]:
    """The SLOW background book (Amendment 1): in paper, no clock, no queue slot."""
    slow = slow_ids(rows)
    return [r for r in in_paper(rows) if r.get("strategy_id") in slow]


def in_paper_active(rows: list[dict]) -> list[dict]:
    """In paper and on the ordinary six-week clock (i.e. not SLOW)."""
    slow = slow_ids(rows)
    return [r for r in in_paper(rows) if r.get("strategy_id") not in slow]


def queue(rows: list[dict]) -> list[dict]:
    """Candidates not yet in paper, Director priority order (priority asc, then
    first-seen order). A strategy at SALVAGE is not in the queue -- its spawn is.
    A SLOW strategy (Amendment 1) is in PAPER, never in QUEUE_STAGES, so it
    takes no queue slot and Step 4 works the next non-SLOW candidate."""
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
    p = in_paper_active(rows)
    lines.append(f"  in paper: " + (", ".join(f"{r['strategy_id']} {r['stage']}" for r in p) if p else "none"))
    sl = in_paper_slow(rows)
    lines.append(f"  in paper, SLOW (background, no queue slot, judged at {SLOW_MIN_TRADES} trades): " +
                 (", ".join(f"{r['strategy_id']} {r['stage']}" for r in sl) if sl else "none"))
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
    a.add_argument("--slow", dest="slow", action="store_true", default=None,
                   help="label the strategy SLOW (Amendment 1): background paper, no queue slot, judged at 40 trades")
    a.add_argument("--not-slow", dest="slow", action="store_false",
                   help="clear the SLOW label")
    a.add_argument("--paper-log-name", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "append":
        row = {"strategy_id": args.id, "name": args.name, "stage": args.stage, "notes": args.notes,
               "source_channel": args.source_channel, "lineage": args.lineage}
        if args.priority is not None:
            row["priority"] = args.priority
        if args.verdict:
            row["verdict"] = args.verdict
        if args.slow is not None:
            row["slow"] = bool(args.slow)
        if args.paper_log_name:
            row["paper_log_name"] = args.paper_log_name
        print(json.dumps(append(row), default=str))
        return 0
    for ln in summary_lines(read_rows()):
        print(ln)
    return 0


if __name__ == "__main__":
    enable_production()
    raise SystemExit(main())
