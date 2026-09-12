#!/usr/bin/env python3
"""Operations checks -- the hard, mechanical half of the Operations Manager.

Every check here answers a PROCEDURAL question with a deterministic
pass/fail. None of them judges a research result, and none of them ever
should: that is the Integrity Gate's job and this module is explicitly
not qualified for it. See AMENDMENT v2.4 for the scope boundary.

The Operations Manager agent runs these and decides what is worth
escalating. Putting the checks in code rather than in an agent's
reasoning is deliberate -- it keeps the role cheap, keeps it honest, and
stops it from becoming an agent that files a reassuring report every
four hours.

    python3 src/ops_checks.py            # human-readable
    python3 src/ops_checks.py --json     # for the console / a session
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

RESEARCH = ROOT / "research"
LEDGER = RESEARCH / "ledger" / "hypotheses.jsonl"
SESSION_LOG = RESEARCH / "_session_log.txt"
SESSIONS_DIR = RESEARCH / "sessions"
MECHANISMS_DIR = RESEARCH / "mechanisms"
LOCK = RESEARCH / "_worksession.lock"
CONSOLE_STATE = RESEARCH / "_console_state.json"
NEXT_UP = RESEARCH / "NEXT_UP.md"

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"

# A session that has taken the lock but logged nothing for this long has
# almost certainly died -- the desktop bridge dropping mid-run is the
# observed failure (2026-09-10).
HEARTBEAT_MINUTES = 30
# The console is refreshed at every research cycle, which now runs every
# 2h on the even UTC hour (changed 2026-09-11, per Jason) -- so an idle
# gap of up to ~2h between cycles is NORMAL, not a refresh failure. Set
# comfortably past that (3h) so this only fires on an actual broken
# refresh step, not routine between-cycle staleness. (Previously 45min,
# which fired as noise on almost every cycle.)
CONSOLE_STALE_MINUTES = 180
# Runs in a row that produced no new information before this is a signal
# about the methodology, not about any one run.
BARREN_RUN_LIMIT = 3


@dataclass
class Result:
    name: str
    status: str
    detail: str

    def as_dict(self) -> dict:
        return asdict(self)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_log_stamp(line: str):
    m = re.match(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})", line.strip())
    if not m:
        return None
    try:
        return datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None


def _log_stamps() -> list:
    if not SESSION_LOG.exists():
        return []
    out = [_parse_log_stamp(l) for l in SESSION_LOG.read_text(errors="replace").splitlines()]
    return [t for t in out if t]


def _session_reports() -> list:
    if not SESSIONS_DIR.exists():
        return []
    return sorted(SESSIONS_DIR.glob("*.md"), reverse=True)


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_lock_health() -> Result:
    """A lock left RUNNING by a session that died makes the whole system
    look busy and blocks nothing usefully."""
    if not LOCK.exists():
        return Result("lock", WARN, "no lock file — sessions cannot coordinate")
    parts = LOCK.read_text().strip().split(None, 1)
    if len(parts) != 2:
        return Result("lock", WARN, f"unreadable lock: {LOCK.read_text().strip()!r}")
    state, stamp = parts[0].upper(), parts[1].strip()
    if state == "FREE":
        return Result("lock", PASS, f"free since {stamp}")
    try:
        started = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return Result("lock", WARN, f"RUNNING with unparseable timestamp {stamp!r}")

    last_beat = max([t for t in (_log_stamps() or []) ] + [started, _work_beat()])
    quiet = (_now() - last_beat).total_seconds() / 60
    if quiet > HEARTBEAT_MINUTES:
        return Result(
            "lock", FAIL,
            f"session holding the lock since {stamp} has logged nothing for "
            f"{quiet:.0f} min — probably died; release the lock",
        )
    running = (_now() - started).total_seconds() / 60
    return Result("lock", PASS, f"session running {running:.0f} min, last activity {quiet:.0f} min ago")


def _work_beat() -> datetime:
    """Newest change across the files a working session actually touches.

    Liveness cannot come from the session log alone: a session doing real
    work writes ledger rows, specs and studies between log lines, and on
    2026-09-10 a perfectly healthy session was reported dead because it
    had spent 30 minutes running a Validation test instead of writing
    prose about it."""
    newest = datetime.fromtimestamp(0, tz=timezone.utc)
    # SESSION_LOG is deliberately absent: its mtime moves whenever it is
    # appended to, even with an old timestamp, so it would mask exactly the
    # staleness _log_stamps() exists to detect.
    watched = [LEDGER, CONSOLE_STATE, SESSIONS_DIR, MECHANISMS_DIR,
               RESEARCH / "studies", RESEARCH / "NEXT_UP.md",
               # worksession_lock.py heartbeats land here; a session
               # running a long scan beats this file even when it writes
               # nothing else (2026-09-11 handoff infrastructure).
               RESEARCH / "_worksession.lock.meta"]
    for path in watched:
        try:
            if path.is_dir():
                stamps = [p.stat().st_mtime for p in path.glob("*") if p.is_file()]
                if not stamps:
                    continue
                mtime = max(stamps)
            elif path.exists():
                mtime = path.stat().st_mtime
            else:
                continue
            newest = max(newest, datetime.fromtimestamp(mtime, tz=timezone.utc))
        except OSError:
            continue
    return newest


def check_console_fresh() -> Result:
    """Jason reads the console on his phone. If the refresh step stops
    happening, nothing else tells him."""
    if not CONSOLE_STATE.exists():
        return Result("console", FAIL, "no console state file has ever been written")
    try:
        state = json.loads(CONSOLE_STATE.read_text())
        gen = datetime.strptime(state["generated_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except Exception as exc:  # noqa: BLE001
        return Result("console", FAIL, f"console state unreadable: {exc}")
    age = (_now() - gen).total_seconds() / 60
    if age > CONSOLE_STALE_MINUTES:
        return Result("console", WARN, f"console state is {age:.0f} min old — refresh step may be failing")
    return Result("console", PASS, f"refreshed {age:.0f} min ago")


def check_session_reports() -> Result:
    """Every run owes a report, and the report owes a fixed shape."""
    reports = _session_reports()
    if not reports:
        return Result("reports", FAIL, "no session reports on disk")
    latest = reports[0]
    text = latest.read_text(errors="replace")
    required = ["Agents"]   # heading level varies (## or ###); the section must exist
    missing = [r for r in required if not re.search(r"^#{2,3}\s+" + r, text, re.MULTILINE)]
    if missing:
        return Result("reports", WARN, f"{latest.name} missing section(s): {', '.join(missing)}")
    if not re.search(r"(?:--|—)\s*(?:RAN|NOT RUN)", text):
        return Result("reports", WARN, f"{latest.name} lists no agents as RAN / NOT RUN")
    return Result("reports", PASS, f"{len(reports)} reports, latest {latest.name} well-formed")


def check_new_information() -> Result:
    """The anti-busy-work scoreboard. A run of runs that produced nothing
    is a methodology signal, and it is the Operations Manager's job to
    say so out loud rather than let it pass unremarked."""
    reports = _session_reports()
    if not reports:
        return Result("new-information", WARN, "no reports to score")
    missing_line, barren = 0, 0
    for path in reports[:BARREN_RUN_LIMIT + 2]:
        text = path.read_text(errors="replace")
        m = re.search(
            r"WHAT NEW INFORMATION THIS RUN PRODUCED[^\n]*\n+(.{0,400}?)(?:\n\n|\n#|$)",
            text, re.IGNORECASE | re.DOTALL,
        )
        if not m:
            missing_line += 1
            continue
        body = " ".join(m.group(1).split()).lower()
        if body.startswith("none") or "nothing new" in body:
            barren += 1
        else:
            break
    if barren >= BARREN_RUN_LIMIT:
        return Result(
            "new-information", FAIL,
            f"{barren} consecutive runs produced no new information — "
            "raise a staff meeting on the methodology",
        )
    if missing_line:
        return Result(
            "new-information", WARN,
            f"{missing_line} recent report(s) omit the new-information line",
        )
    return Result("new-information", PASS, "latest run recorded new information")


def _idea_key(name: str | None) -> str:
    name = name or ""
    for _ in range(6):
        for suffix in (
            "_prospective_validation", "_prospective", "_validation",
            "_holdout", "_discovery", "_excursion",
        ):
            if name.endswith(suffix):
                name = name[: -len(suffix)]
    return name


def check_ledger_consistency() -> Result:
    """The recurring defect: an idea closed by its own later test, whose
    earlier row still reads PROMISING. Ten of these accumulated before
    anyone looked. This makes the pipeline look fuller than it is."""
    try:
        from research_ledger import get_current_state
        rows = get_current_state()
    except Exception as exc:  # noqa: BLE001
        return Result("ledger", WARN, f"could not read ledger: {exc}")

    bookkeeping = (
        "_STATUS_CORRECTION", "_MULTIPLICITY_REEXPRESSION",
        "_PROGRESSION_POINTER", "_INTEGRITY_REVIEW_MULTIPLICITY",
    )
    order = {"discovery": 1, "validation": 2, "holdout_gen1": 2, "holdout_gen2": 3, "prospective": 4}
    families = collections.defaultdict(list)
    for row in rows:
        if (row.get("strategy_name") or "").endswith(bookkeeping):
            continue
        families[_idea_key(row.get("strategy_name"))].append(row)

    stale = []
    for key, family in families.items():
        rejected = [r for r in family if (r.get("strategy_status") or "").startswith("REJECT")]
        if not rejected:
            continue
        deepest = max(order.get(r.get("data_slice_used"), 0) for r in rejected)
        for row in family:
            status = row.get("strategy_status") or ""
            if not status.startswith("REJECT") and order.get(row.get("data_slice_used"), 0) <= deepest:
                stale.append(f"{row.get('hypothesis_id')} ({key}) reads {status}")
    if stale:
        head = "; ".join(stale[:4]) + (f"; +{len(stale) - 4} more" if len(stale) > 4 else "")
        return Result("ledger", FAIL, f"{len(stale)} stale status row(s): {head}")
    return Result("ledger", PASS, f"{len(families)} idea families, no stale statuses")


def check_mechanism_gate() -> Result:
    """Binding since 2026-09-10: nothing advances past Mechanism without a
    document. This checks the rule is actually holding."""
    if not MECHANISMS_DIR.exists():
        return Result("mechanism-gate", FAIL, "research/mechanisms/ does not exist")
    docs = [p.stem for p in MECHANISMS_DIR.glob("*.md") if p.stem not in ("README", "TEMPLATE")]
    try:
        from research_ledger import get_current_state
        rows = get_current_state()
    except Exception as exc:  # noqa: BLE001
        return Result("mechanism-gate", WARN, f"could not read ledger: {exc}")

    advanced = {
        _idea_key(r.get("strategy_name"))
        for r in rows
        if r.get("data_slice_used") in ("validation", "holdout_gen1", "holdout_gen2", "prospective")
        and not (r.get("strategy_status") or "").startswith("REJECT")
        # EXP-047 is a legacy forward tracker (rejected at Discovery, tracked
        # anyway, frozen); the Mechanism Gate binds from 2026-09-10, not
        # retroactively to it.
        and "exp047" not in (r.get("strategy_name") or "").lower()
    }
    def covered(idea: str) -> bool:
        words = [w for w in re.split(r"[_\-]", idea) if len(w) > 3]
        return any(any(w in d for w in words) for d in docs)

    uncovered = sorted(i for i in advanced if i and not covered(i))
    # UPGRADE 3 (2026-09-11): Mechanism writes BEFORE the scan. So the gate
    # now also fires on any inventory entry that has been DRAWN (scan
    # scoped/run) without a mechanism doc -- earlier, stricter, cheaper.
    inv = RESEARCH / "idea_inventory.md"
    if inv.exists():
        txt = inv.read_text(errors="replace")
        heads = list(re.finditer(r"^## ENTRY (\d+) — (.*)$", txt, re.MULTILINE))
        for i, m in enumerate(heads):
            title = m.group(2)
            if title.startswith("SHELVED") or " CLOSED" in title:
                continue
            end = heads[i + 1].start() if i + 1 < len(heads) else len(txt)
            body = txt[m.end():end]
            if not re.search(r"\bDRAWN\b", body):
                continue
            sv = re.search(r"STATE VARIABLE\*\*:?\s*`?([A-Za-z0-9_]+)", body)
            key = sv.group(1) if sv else f"entry{m.group(1)}"
            if not covered(key):
                uncovered.append(f"Entry {m.group(1)} ({key}) drawn without mechanism doc")
    if uncovered:
        return Result(
            "mechanism-gate", WARN,
            f"{len(uncovered)} scope(s)/candidate(s) without a mechanism doc: "
            + ", ".join(uncovered[:3]),
        )
    return Result("mechanism-gate", PASS, f"{len(docs)} mechanism doc(s) cover every advanced candidate")


DATA_STALE_SESSIONS = 5


def _latest_price_date():
    """Last timestamp in the newest NQ 1-minute file, read from the tail so
    a 1 GB CSV is not loaded. Returns a date or None."""
    files = sorted((ROOT / "data").glob("NQ_1min_databento_*.csv"))
    if not files:
        return None
    path = files[-1]
    try:
        with path.open("rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - 4096))
            tail = fh.read().decode(errors="replace").strip().splitlines()
        for line in reversed(tail):
            m = re.match(r"^(\d{4}-\d{2}-\d{2})[ T]", line)
            if m:
                return datetime.strptime(m.group(1), "%Y-%m-%d").date()
    except OSError:
        return None
    return None


def _weekdays_between(a, b) -> int:
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def check_data_currency() -> Result:
    """UPGRADE 2: Jason pulls Databento manually; Ops flags when the
    live-forward window is more than 5 sessions stale."""
    last = _latest_price_date()
    if last is None:
        return Result("data-currency", WARN, "no NQ 1-minute file found")
    stale = _weekdays_between(last, _now().date())
    if stale > DATA_STALE_SESSIONS:
        return Result("data-currency", WARN,
                      f"price data ends {last} — {stale} weekday sessions stale; Jason to run the Databento pull")
    return Result("data-currency", PASS, f"price data through {last} ({stale} sessions behind)")


def check_awaiting_jason() -> Result:
    """Anything parked on Jason has a clock, and somebody has to watch it."""
    if not NEXT_UP.exists():
        return Result("awaiting-jason", WARN, "NEXT_UP.md missing")
    text = NEXT_UP.read_text(errors="replace")
    blocked = re.findall(r"^\s*(\d+[a-z]?)\.\s+(.{0,90})", text, re.MULTILINE)
    # "UNBLOCKED" contains "BLOCKED" -- an item Jason has already answered
    # must not keep reporting as waiting on him.
    waiting = [
        f"{num}. {desc.strip()}" for num, desc in blocked
        if re.search(r"(?<!UN)BLOCKED", desc.upper())
    ]
    # 2026-09-12: a Holdout-slot request written as a "WAITING ON JASON" block
    # (not a numbered BLOCKED item) slipped past this check. Catch both, plus
    # any GATED row in the sweep table that says it is waiting on him.
    for m in re.finditer(r"^WAITING ON JASON[^\n]*\n([^\n]{0,90})", text, re.MULTILINE):
        waiting.append("WAITING ON JASON: " + m.group(1).strip())
    sweep = RESEARCH.parent / "data" / "pipeline_sweep.json"
    if sweep.exists():
        try:
            for row in json.loads(sweep.read_text()).get("rows", []):
                if row.get("tier") == "GATED" and "Waiting on Jason" in (row.get("next_owed") or ""):
                    waiting.append(f"GATED {row.get('id')}: Holdout slot")
        except Exception:
            pass
    if waiting:
        return Result("awaiting-jason", WARN, f"{len(waiting)} item(s) blocked on Jason: " + "; ".join(waiting[:2]))
    return Result("awaiting-jason", PASS, "nothing parked on Jason in the queue")


def check_unfinished_checkpoint() -> Result:
    """Resume safety (Jason, 2026-09-11): a cycle that hit its budget mid-task
    leaves research/_cycle_checkpoint.json in status=running. With the lock
    FREE that is unfinished work the NEXT cycle must resume FIRST -- never
    re-register, never re-run a stage that already produced its artifact,
    never treat half-written files as done."""
    ck = RESEARCH / "_cycle_checkpoint.json"
    if not ck.exists():
        return Result("checkpoint", PASS, "no checkpoint file (no cycle has used the budget clock yet)")
    try:
        c = json.loads(ck.read_text())
    except Exception as e:  # noqa: BLE001
        return Result("checkpoint", WARN, f"checkpoint unreadable: {e}")
    lock_running = LOCK.exists() and LOCK.read_text().startswith("RUNNING")
    if c.get("status") == "running" and not lock_running:
        return Result("checkpoint", WARN, f"UNFINISHED work to resume: item={c.get('item')} step={c.get('step')} files={c.get('files')} (started {c.get('started','?')[:16]})")
    if c.get("status") == "running":
        return Result("checkpoint", PASS, f"cycle in progress: {c.get('item') or 'opening'} / {c.get('step') or '-'}")
    return Result("checkpoint", PASS, f"last cycle closed cleanly at {c.get('finished','?')[:16]}")


BUSY_WORK_LIMIT = 3


def _value_ack(entries: list) -> dict | None:
    """The acknowledgment in research/_value_ack.json, or None if absent,
    malformed, or expired. Expired = some cycle that FINISHED after ack.at
    has moved=True: the empty-queue state Jason acknowledged is over, so a
    later stall must alert fresh."""
    f = RESEARCH / "_value_ack.json"
    if not f.exists():
        return None
    try:
        ack = json.loads(f.read_text())
        at = ack["at"]
        for e in entries:
            if e.get("moved") and (e.get("finished") or "") > at:
                return None
        return {"by": ack.get("by", "Jason"), "at": at, "reason": ack.get("reason", "")}
    except Exception:
        return None


def check_value_per_cycle() -> Result:
    """Quality-control indicator (Jason, 2026-09-11): are cycles MOVING
    anything, or spinning? Reads research/_cycle_history.jsonl (written by
    cycle_budget.py done: objective artifact deltas per cycle). Three closed
    cycles in a row with zero deltas = BUSY WORK -> FAIL (IMMEDIATE item).
    Separately: queue exhausted (sweep owes nothing automated AND the shelf
    is empty) -> FAIL, because only Jason can add map entries or data."""
    hist = RESEARCH / "_cycle_history.jsonl"
    entries = []
    if hist.exists():
        for line in hist.read_text().splitlines():
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except Exception:
                    continue
    # queue exhaustion, from the sweep + shelf
    sweep = RESEARCH.parent / "data" / "pipeline_sweep.json"
    exhausted = False
    if sweep.exists():
        try:
            s = json.loads(sweep.read_text())
            owed = [r for r in s.get("rows", []) if r.get("tier") in ("OPEN", "GATED") and not (r.get("next_owed") or "").startswith("nothing")]
            shelf = s.get("shelf", "") or ""
            live = re.search(r"Shelf (\d+)/", shelf)
            exhausted = (not owed) and live is not None and int(live.group(1)) == 0
        except Exception:
            pass
    # ACKNOWLEDGED STATE (Jason, September 12th, ~1:55 am CT, "make sure the
    # sessions run smoothly moving forward as normal"): once Jason has been
    # told the queue is empty and has chosen to leave it that way for now,
    # every further cycle re-raising it as FAIL is noise, not a signal. A
    # research/_value_ack.json {"by","at","reason"} downgrades BOTH the
    # QUEUE EXHAUSTED and BUSY WORK conditions to WARN. The ack expires on
    # its own the moment any cycle finished after ack.at actually MOVES
    # something -- a later stall is then a NEW event and FAILs again.
    ack = _value_ack(entries)
    if exhausted:
        if ack:
            return Result("value", WARN, f"QUEUE EXHAUSTED, acknowledged by {ack['by']} {ack['at'][:10]}: {ack['reason']} -- routine cycles only, do not manufacture work, do not re-alert")
        return Result("value", FAIL, "QUEUE EXHAUSTED: nothing owed and the shelf is empty -- needs Jason (new map entries or data), do not manufacture work")
    if not entries:
        return Result("value", PASS, "no cycle history yet (first budget-clock cycle pending)")
    recent = entries[-BUSY_WORK_LIMIT:]
    stalled = len(recent) >= BUSY_WORK_LIMIT and not any(e.get("moved") for e in recent)
    if stalled:
        if ack:
            return Result("value", WARN, f"no movement for {BUSY_WORK_LIMIT}+ cycles, acknowledged by {ack['by']} {ack['at'][:10]}: {ack['reason']} -- expected while the map is empty, do not re-alert")
        return Result("value", FAIL, f"BUSY WORK: last {BUSY_WORK_LIMIT} cycles moved nothing (no ledger/scan/doc/inventory change) -- tell Jason, do not keep cycling")
    last = entries[-1]
    return Result("value", PASS, f"last cycle moved={last.get('moved')} delta={ {k: v for k, v in last.get('delta', {}).items() if v} }")


def check_shelf_starving() -> Result:
    """SHELF RULE v2 (Jason, 2026-09-12): the shelf counts drawable entries
    only. If it is below the floor AND the last 3 closed cycles added no
    inventory entries, sourcing is failing to restock -> tell Jason. This
    is a sourcing problem, never a reason to draw thin or invent a scope."""
    sweep = RESEARCH.parent / "data" / "pipeline_sweep.json"
    hist = RESEARCH / "_cycle_history.jsonl"
    try:
        shelf = json.loads(sweep.read_text()).get("shelf", "") if sweep.exists() else ""
    except Exception:
        shelf = ""
    if "SOURCING OWED" not in shelf:
        return Result("shelf", PASS, shelf[:90] if shelf else "no sweep yet")
    entries = []
    if hist.exists():
        for line in hist.read_text().splitlines():
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
    recent = entries[-3:]
    restocked = any((e.get("delta") or {}).get("inventory_entries", 0) for e in recent)
    if len(recent) >= 3 and not restocked:
        return Result("shelf", FAIL, "SHELF STARVING: below the floor and 3 closed cycles added no entries -- tell Jason; sourcing problem, do not draw thin")
    return Result("shelf", WARN, f"below floor, sourcing owed ({shelf[:70]})")


CHECKS = (
    check_lock_health,
    check_shelf_starving,
    check_unfinished_checkpoint,
    check_value_per_cycle,
    check_console_fresh,
    check_session_reports,
    check_new_information,
    check_ledger_consistency,
    check_mechanism_gate,
    check_data_currency,
    check_awaiting_jason,
)


def run_all() -> list:
    results = []
    for check in CHECKS:
        try:
            results.append(check())
        except Exception as exc:  # noqa: BLE001
            results.append(Result(check.__name__, WARN, f"check itself failed: {exc}"))
    return results


def overall(results: list) -> str:
    if any(r.status == FAIL for r in results):
        return FAIL
    if any(r.status == WARN for r in results):
        return WARN
    return PASS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = run_all()
    if args.json:
        print(json.dumps(
            {
                "generated_at": _now().strftime("%Y-%m-%dT%H:%M:00Z"),
                "overall": overall(results),
                "checks": [r.as_dict() for r in results],
            },
            indent=1,
        ))
        return

    print(f"OPERATIONS STATUS: {overall(results)}\n")
    for r in results:
        print(f"  [{r.status:<4}] {r.name:<18} {r.detail}")


if __name__ == "__main__":
    main()
