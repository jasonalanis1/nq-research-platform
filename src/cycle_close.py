#!/usr/bin/env python3
"""
cycle_close.py -- the standing CLOSING sequence of every cycle, in one command,
and the thing that writes the per-cycle compliance record.

WHY (2026-09-14, Jason: he is letting the day run unattended and will review
every cycle in the evening)
  src/cycle_preflight.py made the OPENING sequence mechanical after an audit
  found the H118 daily checker had not run in four consecutive cycles. The
  closing sequence had the identical weakness: it was a prose protocol a cycle
  had to remember, and nothing checked it. A cycle could skip the tests, fail
  to push, or leave the lock held, and the only way to find out was to read the
  session report it wrote about itself.

  So this runs the mechanical half of close-out and appends ONE ROW PER CYCLE
  to research/_cycle_compliance.jsonl, joining the preflight receipt to the
  close result. That file is the answer to "did every cycle today actually run
  everything" -- readable in one place instead of reconstructed from six
  session reports and a handful of file timestamps.

WHAT IT CHECKS
  tests        the full pytest suite passes
  ops          ops_checks overall status (WARN is acceptable and reported;
               FAIL is not)
  git_pushed   the working tree is committed AND pushed -- not just committed
  lock         the worksession lock was released
  preflight    this cycle's preflight receipt exists, is clean, and is NEWER
               than this cycle's start (i.e. it is THIS cycle's, not the
               previous one's)
  moved        whether a candidate CHANGED STAGE (ledger), a scan was
               registered, or a bot milestone flipped -- from the budget
               clock's own delta. Shelf/inventory additions, studies and
               mechanism docs are listed but count zero (refocus 7.1).

WHAT IT DOES NOT DO
  It does not write the session report, NEXT_UP, or KNOWLEDGE. Those carry
  judgment -- what broke, what was learned, what it means -- and a script that
  generated them would produce exactly the reassuring filler the Operations
  role is explicitly warned against. It records the MECHANICAL facts and leaves
  the judgment where it belongs.

  It also does not run `cycle_budget.py done`, commit, or release the lock --
  it VERIFIES those happened. A checker that performs the work it is checking
  cannot fail.

USAGE
    python3 src/cycle_close.py                      # after committing+pushing
    python3 src/cycle_close.py --label "9:00 am cycle" --skip-tests
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
RESEARCH = ROOT / "research"
COMPLIANCE = RESEARCH / "_cycle_compliance.jsonl"
PREFLIGHT = RESEARCH / "_cycle_preflight.json"
CHECKPOINT = RESEARCH / "_cycle_checkpoint.json"
HISTORY = RESEARCH / "_cycle_history.jsonl"

TESTS_TIMEOUT = 170


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _run(argv, timeout=60) -> tuple:
    try:
        p = subprocess.run(argv, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or ""), (p.stderr or "")
    except subprocess.TimeoutExpired:
        return None, "", f"timed out after {timeout}s"
    except Exception as exc:  # noqa: BLE001
        return None, "", repr(exc)


def check_tests(skip: bool) -> dict:
    if skip:
        return {"ok": None, "skipped": True, "detail": "--skip-tests"}
    rc, out, _ = _run([sys.executable, "-m", "pytest", "-q"], timeout=TESTS_TIMEOUT)
    m = re.search(r"(\d+) passed", out)
    f = re.search(r"(\d+) failed", out)
    return {"ok": rc == 0, "passed": int(m.group(1)) if m else None,
            "failed": int(f.group(1)) if f else 0,
            "detail": (f"{m.group(1)} passed" if m else "no test count parsed")
                      + (f", {f.group(1)} FAILED" if f else "")}


def check_ops() -> dict:
    rc, out, _ = _run([sys.executable, str(SRC / "ops_checks.py"), "--json"], timeout=120)
    try:
        d = json.loads(out)
    except Exception:  # noqa: BLE001
        return {"ok": False, "detail": "ops_checks produced no parsable JSON"}
    overall = d.get("overall")
    bad = [c["name"] for c in d.get("checks", []) if c.get("status") == "FAIL"]
    warn = [c["name"] for c in d.get("checks", []) if c.get("status") == "WARN"]
    return {"ok": overall != "FAIL", "overall": overall, "failing": bad, "warning": warn,
            "detail": f"{overall}" + (f" -- FAIL: {', '.join(bad)}" if bad else "")
                      + (f" -- WARN: {', '.join(warn)}" if warn else "")}


def check_git() -> dict:
    rc, out, _ = _run(["git", "status", "-sb"], timeout=30)
    first = out.splitlines()[0] if out else ""
    dirty = [l for l in out.splitlines()[1:] if l.strip() and not l.startswith("??")]
    ahead = re.search(r"\[ahead (\d+)", first)
    rc2, head, _ = _run(["git", "log", "-1", "--format=%h %s"], timeout=30)
    ok = not ahead and not dirty
    detail = "committed and pushed"
    if ahead:
        detail = f"{ahead.group(1)} commit(s) NOT PUSHED"
    elif dirty:
        detail = f"{len(dirty)} tracked file(s) uncommitted"
    return {"ok": ok, "detail": detail, "head": head.strip(), "uncommitted": len(dirty),
            "unpushed": int(ahead.group(1)) if ahead else 0}


def check_lock() -> dict:
    rc, out, _ = _run([sys.executable, str(SRC / "worksession_lock.py"), "status"], timeout=30)
    free = "FREE" in out
    return {"ok": free, "detail": out.strip().splitlines()[0] if out.strip() else "no status"}


def check_preflight_receipt() -> dict:
    if not PREFLIGHT.exists():
        return {"ok": False, "detail": "no preflight receipt -- the opening sequence never ran"}
    try:
        d = json.loads(PREFLIGHT.read_text())
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": f"unreadable: {exc}"}
    failed = d.get("failed") or []
    ran_at = d.get("ran_at")
    belongs_to_this_cycle = None
    if CHECKPOINT.exists() and ran_at:
        try:
            c = json.loads(CHECKPOINT.read_text())
            if c.get("started"):
                belongs_to_this_cycle = (
                    datetime.fromisoformat(ran_at) >= datetime.fromisoformat(c["started"]))
        except Exception:  # noqa: BLE001
            pass
    steps = {k: bool(v.get("ok")) for k, v in (d.get("steps") or {}).items() if isinstance(v, dict)}
    ok = not failed and belongs_to_this_cycle is not False
    detail = "clean" if not failed else f"FAILED steps: {', '.join(failed)}"
    if belongs_to_this_cycle is False:
        detail += "; receipt predates this cycle's start (belongs to a PREVIOUS cycle)"
    return {"ok": ok, "detail": detail, "ran_at": ran_at, "steps": steps,
            "sourcing_owed": ((d.get("steps") or {}).get("shelf") or {}).get("sourcing_owed")}


def last_history_row() -> dict:
    if not HISTORY.exists():
        return {}
    rows = [l for l in HISTORY.read_text().splitlines() if l.strip()]
    if not rows:
        return {}
    try:
        return json.loads(rows[-1])
    except Exception:  # noqa: BLE001
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description="the standing closing sequence of a cycle")
    ap.add_argument("--label", default="", help="which cycle this is, e.g. '9:00 am cycle'")
    ap.add_argument("--skip-tests", action="store_true")
    a = ap.parse_args()

    print("=" * 78)
    print("CYCLE CLOSE -- mechanical close-out checks")
    print("=" * 78)

    checks = {
        "preflight": check_preflight_receipt(),
        "tests": check_tests(a.skip_tests),
        "ops": check_ops(),
        "git": check_git(),
        "lock": check_lock(),
    }
    hist = last_history_row()
    delta = hist.get("delta") or {}
    moved = bool(hist.get("moved"))

    for name, r in checks.items():
        mark = "ok  " if r.get("ok") else ("skip" if r.get("skipped") else "FAIL")
        print(f"  [{mark}] {name:<10} {r.get('detail','')}")
    print(f"  [info] moved      {moved} {json.dumps({k: v for k, v in delta.items() if v})}")
    if checks["preflight"].get("sourcing_owed"):
        print("  [note] sourcing was OWED this cycle (shelf at/below floor) -- "
              "confirm the session report says whether it ran")

    failing = [k for k, r in checks.items() if r.get("ok") is False]
    row = {
        "closed_at": _now().isoformat(),
        "label": a.label or None,
        "cycle_started": (json.loads(CHECKPOINT.read_text()).get("started")
                          if CHECKPOINT.exists() else None),
        "complete": not failing,
        "failing": failing,
        "checks": checks,
        "moved": moved,
        "delta": {k: v for k, v in delta.items() if v},
    }
    COMPLIANCE.parent.mkdir(parents=True, exist_ok=True)
    with COMPLIANCE.open("a") as f:
        f.write(json.dumps(row, default=str) + "\n")

    print()
    if failing:
        print(f"CLOSE INCOMPLETE -- {', '.join(failing)}")
        print("Say so in the session report. Do not describe the cycle as closed cleanly.")
    else:
        print("CLOSE COMPLETE -- every mechanical check passed.")
    print(f"compliance row appended -> {COMPLIANCE}")
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
