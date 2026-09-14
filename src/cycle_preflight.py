#!/usr/bin/env python3
"""
cycle_preflight.py -- the standing opening sequence of every cycle, in ONE
command, so it cannot be skipped by forgetting.

WHY THIS EXISTS (2026-09-14, Jason: "I wanna make sure that we're running
through everything")
  The standing protocol says every cycle takes the lock, starts the budget
  clock, rebuilds the pipeline sweep, runs both daily checkers on the frozen
  forward-validation candidates, and reports the shelf/sourcing position --
  BEFORE any work item is chosen. An audit on 2026-09-14 found that across the
  four cycles of 2026-09-14 (06:04, 12:09, 12:20, 12:32 UTC) the H118 daily
  checker ran ZERO times, the pipeline sweep ran once, and sourcing was never
  reported. The evidence was not ambiguous: h118_forward_log.jsonl's mtime sat
  at 03:39 UTC, the 11:00 pm cycle, for the whole morning.

  The cause was not a broken script. It was that the opening sequence lived in
  a prose protocol that a cycle had to REMEMBER, while the headline build was
  the thing that produced something to show. Nothing detected the omission,
  so nothing corrected it, four times running.

  So the sequence becomes one command that either completes or fails loudly,
  and it leaves a RECEIPT on disk. ops_checks reads that receipt: a cycle that
  did not run its preflight now fails the `preflight` check, and a cycle that
  skipped a step inside it shows which one. The point is not that this script
  does anything the protocol did not already require -- it is that skipping it
  is now visible instead of silent.

WHAT IT DOES NOT DO
  It does not choose the work item and it does not run close-out. The
  ordering principle (docs/BOT_ROADMAP.md outranks research/NEXT_UP.md) is a
  judgment about what can actually be advanced, and this script deliberately
  makes no judgments -- same scope boundary ops_checks.py states for itself.

USAGE
    python3 src/cycle_preflight.py --owner cycle --note "3:00 am cycle"
    python3 src/cycle_preflight.py --owner cycle --skip-lock   # lock already held
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
RECEIPT = ROOT / "research" / "_cycle_preflight.json"

# Each step: (key, human label, argv, required)
# `required` False means a failure is reported but does not fail the preflight
# -- used for steps that legitimately have nothing to do on a given day.
STEPS = [
    ("sweep",  "pipeline sweep",        [sys.executable, str(SRC / "pipeline_sweep.py"), "--write"], True),
    ("h118",   "H118 daily checker",    [sys.executable, str(SRC / "forward_validate_h118_daily.py")], True),
    ("exp047", "EXP047 weekly checker", [sys.executable, str(SRC / "study_prospective_exp047.py")], True),
]

TIMEOUT_S = 150   # device_bash's own ceiling is ~180s; stay under it


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(argv: list, timeout: int = TIMEOUT_S) -> dict:
    try:
        p = subprocess.run(argv, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        tail = [ln for ln in (p.stdout or "").strip().splitlines() if ln.strip()][-3:]
        return {"ok": p.returncode == 0, "returncode": p.returncode, "tail": tail,
                "stderr_tail": [ln for ln in (p.stderr or "").strip().splitlines() if ln.strip()][-3:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None, "tail": [], "stderr_tail": [f"timed out after {timeout}s"]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "returncode": None, "tail": [], "stderr_tail": [repr(exc)]}


def shelf_status() -> dict:
    """Read the shelf position the sweep just wrote. Sourcing is a JUDGMENT
    (read the map, the literature, practitioner practice, the observatory) and
    is not automatable -- so this reports the position and whether sourcing is
    OWED, and the cycle still has to do it. Reporting it is what makes
    forgetting it visible."""
    p = ROOT / "data" / "pipeline_sweep.json"
    if not p.exists():
        return {"known": False, "note": "no pipeline_sweep.json -- run the sweep first"}
    try:
        d = json.loads(p.read_text())
    except Exception as exc:  # noqa: BLE001
        return {"known": False, "note": f"unreadable: {exc}"}
    shelf = d.get("shelf") or d.get("SHELF") or ""
    if isinstance(shelf, dict):
        count, floor = shelf.get("count"), shelf.get("floor", 3)
    else:
        import re
        m = re.search(r"Shelf\s+(\d+)\s*/\s*(\d+)", str(shelf))
        count, floor = (int(m.group(1)), int(m.group(2))) if m else (None, 3)
    owed = None if count is None else count <= floor
    return {"known": count is not None, "count": count, "floor": floor,
            "sourcing_owed": owed, "line": str(shelf)[:200],
            "note": ("shelf is AT OR BELOW the floor -- SOURCING IS OWED this cycle, before the work item"
                     if owed else "shelf above the floor -- sourcing still runs every cycle per SHELF RULE v2")}


def main() -> int:
    ap = argparse.ArgumentParser(description="the standing opening sequence of a cycle")
    ap.add_argument("--owner", default="cycle")
    ap.add_argument("--note", default="")
    ap.add_argument("--minutes", type=int, default=105)
    ap.add_argument("--skip-lock", action="store_true", help="lock already held by this cycle")
    ap.add_argument("--skip-budget", action="store_true")
    a = ap.parse_args()

    print("=" * 78)
    print("CYCLE PREFLIGHT -- the standing opening sequence")
    print("=" * 78)

    steps: dict = {}

    if not a.skip_lock:
        argv = [sys.executable, str(SRC / "worksession_lock.py"), "acquire", "--owner", a.owner]
        if a.note:
            argv += ["--note", a.note]
        steps["lock"] = _run(argv, timeout=60)
        # the lock script exits non-zero on TAKEN even when it succeeded, so
        # confirm by asking for status rather than trusting the return code
        st = _run([sys.executable, str(SRC / "worksession_lock.py"), "status"], timeout=60)
        holding = any("BUSY" in ln and f"owner={a.owner}" in ln for ln in st["tail"])
        steps["lock"]["ok"] = holding
        steps["lock"]["tail"] = st["tail"]
        if not holding:
            print("  [FAIL] lock            could not confirm this cycle holds the lock:")
            for ln in st["tail"]:
                print(f"         {ln}")
            print("\n  A cycle that finds the lock BUSY defers (retry in 15 min) and ALWAYS")
            print("  reschedules its successor -- the chain must not break.")
            RECEIPT.write_text(json.dumps({"ran_at": _now(), "owner": a.owner, "aborted": "lock",
                                            "steps": steps}, indent=1))
            return 2
        print("  [ok]   lock            held by this cycle")
    else:
        steps["lock"] = {"ok": True, "skipped": True, "tail": ["--skip-lock"]}
        print("  [ok]   lock            assumed already held (--skip-lock)")

    if not a.skip_budget:
        steps["budget"] = _run([sys.executable, str(SRC / "cycle_budget.py"), "start",
                                "--minutes", str(a.minutes)], timeout=60)
        print(f"  [{'ok' if steps['budget']['ok'] else 'FAIL'}]   budget          {a.minutes} min")
    else:
        steps["budget"] = {"ok": True, "skipped": True}
        print("  [ok]   budget          assumed already started (--skip-budget)")

    for key, label, argv, required in STEPS:
        r = _run(argv)
        steps[key] = r
        mark = "ok" if r["ok"] else ("FAIL" if required else "warn")
        print(f"  [{mark}]   {label:<15} " + (r["tail"][-1][:90] if r["tail"] else
                                              (r["stderr_tail"][-1][:90] if r["stderr_tail"] else "")))

    shelf = shelf_status()
    steps["shelf"] = {"ok": shelf.get("known", False), **shelf}
    print(f"  [{'ok' if shelf.get('known') else 'warn'}]   shelf/sourcing  {shelf.get('line','?')[:80]}")
    print(f"         -> {shelf.get('note','')}")

    failed = [k for k, (_, _, _, req) in {s[0]: s for s in STEPS}.items()
              if req and not steps.get(k, {}).get("ok")]
    for k in ("lock", "budget"):
        if not steps.get(k, {}).get("ok"):
            failed.append(k)

    receipt = {"ran_at": _now(), "owner": a.owner, "note": a.note,
               "steps": steps, "failed": failed, "ok": not failed,
               "rule": "ops_checks reads this receipt. A cycle with no fresh receipt, or one with "
                       "failed steps, fails the `preflight` check -- skipping the opening sequence is "
                       "visible, not silent. See this file's header for why it exists."}
    RECEIPT.write_text(json.dumps(receipt, indent=1, default=str))

    print()
    if failed:
        print(f"PREFLIGHT INCOMPLETE -- failed: {', '.join(failed)}")
        print("Do NOT proceed to the work item until these are resolved or explicitly waived in the report.")
    else:
        print("PREFLIGHT COMPLETE -- proceed to the ordering principle (BOT_ROADMAP before research).")
    print(f"receipt -> {RECEIPT}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
