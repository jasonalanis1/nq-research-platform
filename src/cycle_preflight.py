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
    """The shelf FLOOR rule and the "draw thin" rule were RETIRED September 15th
    (standing directive s.12). The old shelf line from the sweep is still
    reported for information, but sourcing is never "owed" by a floor any more:
    the candidate queue in research/ledger/strategies.jsonl is what must not sit
    empty (directive s.3 Step 4), and queue_status() below reports that."""
    p = ROOT / "data" / "pipeline_sweep.json"
    if not p.exists():
        return {"known": False, "sourcing_owed": False, "note": "no pipeline_sweep.json -- run the sweep first"}
    try:
        d = json.loads(p.read_text())
    except Exception as exc:  # noqa: BLE001
        return {"known": False, "sourcing_owed": False, "note": f"unreadable: {exc}"}
    shelf = d.get("shelf") or d.get("SHELF") or ""
    if isinstance(shelf, dict):
        count, floor = shelf.get("count"), shelf.get("floor", 3)
    else:
        import re
        m = re.search(r"Shelf\s+(\d+)\s*/\s*(\d+)", str(shelf))
        count, floor = (int(m.group(1)), int(m.group(2))) if m else (None, 3)
    return {"known": count is not None, "count": count, "floor": floor,
            "sourcing_owed": False, "line": str(shelf)[:200],
            "note": "shelf floor rule RETIRED (directive s.12) -- informational; the candidate queue is the thing that must not be empty"}


def queue_status() -> dict:
    """Directive s.3 Step 4: the candidate queue (registry stages SOURCE..SCREEN)
    must never sit empty while sources exist. Reported, not judged."""
    try:
        import strategy_registry as sr
        rows = sr.read_rows()
        q = sr.queue(rows); s = sr.salvage_queue(rows)
        return {"ok": True, "queue": [f"{r['strategy_id']} {r['stage']}" for r in q],
                "salvage_owed": [r["strategy_id"] for r in s], "empty": not q,
                "note": ("candidate queue EMPTY -- Discovery sources the next candidate this cycle (s.3 Step 4)"
                         if not q else f"next candidate: {q[0]['strategy_id']} {q[0].get('name','')} at {q[0]['stage']}")}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "note": f"registry unreadable: {exc}"}


# ---------------------------------------------------------------------------
# THE REFERENCE-DATA GATE (Jason, September 16th 2026 -- standing rule)
#
#   "Add a standing preflight rule: any reference data past its coverage date
#    blocks the steps that use it and gets reported, never defaulted."
#
# It is a GATE, not a printed line. For every series in
# research/ledger/data_coverage.json, coverage end is compared against the
# current session date; a series that does not reach it BLOCKS the cycle steps
# that depend on it, and the session report says which steps were blocked and
# which series blocked them.
#
# BLOCKED IS NOT ABORTED. The cycle still runs every step that does not depend
# on a stale series -- sourcing, specifying, freezing and screening a price-only
# candidate on the Discovery slice, and close-out. Only the dependent steps stop.
#
# FAIL CLOSED ON A MISSING ENTRY. A series named as a dependency with no entry
# in the coverage ledger at all -- or with no last_date -- is treated as STALE,
# never as fine. "We have no coverage record for it" is not evidence of currency.
# ---------------------------------------------------------------------------
STEP_DEPENDENCIES = {
    "step3_paper_scoring": {
        "series": ["VXN", "FOMC", "CPI", "NFP"],
        "why": "every paper row goes through B2 (src/risk_state_engine.py:decision_for), which "
               "reads vxn_level_vs_trailing and vetoes trade_permission on a scheduled-event day",
    },
    "step3_b2_risk_state_decision": {
        "series": ["VXN", "FOMC", "CPI", "NFP"],
        "why": "src/risk_state_engine.py:require_reference_data refuses a session past either series",
    },
    "step4_salvage_check": {
        "series": ["VXN", "FOMC", "CPI", "NFP"],
        "why": "directive s.7 menu conditions 1 (VXN vs trailing) and 4 (scheduled-news day) -- "
               "src/salvage_check.py:vxn_labels / news_labels",
    },
    "salvage_reruns": {
        "series": ["VXN", "FOMC", "CPI", "NFP"],
        "why": "src/rerun_salvages.py re-runs the salvages that were decided on invented labels",
    },
    "step4_specify_S009a": {
        "series": ["FOMC", "CPI", "NFP"],
        "why": "S009a trades ONLY on days with no scheduled macro event",
    },
    "step4_specify_S010a": {
        "series": ["VXN"],
        "why": "S010a selects LOW-VXN sessions only",
    },
}

# Steps that depend on no reference series at all. Named explicitly so a stale
# series is never used as an excuse to idle a cycle (directive s.3 Step 2).
INDEPENDENT_STEPS = [
    "step4_source (Discovery names a candidate)",
    "step4_specify (price-only candidates)",
    "step4_freeze",
    "step4_screen (Discovery slice, price-only)",
    "step5_closeout (tests, ops checks, commit, push, report)",
]


def reference_data_gate(state: dict | None = None, session_date=None,
                        registry_rows: list | None = None) -> dict:
    """Compare every series' coverage end against the session date and BLOCK the
    steps that depend on a stale one. Reported, never defaulted."""
    from datetime import date as _date

    if session_date is None:
        session_date = _date.today()
    elif isinstance(session_date, str):
        session_date = _date.fromisoformat(session_date[:10])

    if state is None:
        try:
            import reference_data as rd
            state = rd.coverage()
        except Exception as exc:  # noqa: BLE001
            # Cannot read coverage at all -> EVERY dependent step is blocked.
            blocked = {k: {"series": v["series"], "why": v["why"],
                           "reason": f"reference-data coverage unreadable: {exc}"}
                       for k, v in STEP_DEPENDENCIES.items()}
            return {"ok": False, "session_date": session_date.isoformat(),
                    "stale_series": sorted({s for v in STEP_DEPENDENCIES.values() for s in v["series"]}),
                    "series": {}, "blocked_steps": blocked, "allowed_steps": list(INDEPENDENT_STEPS),
                    "lines": [f"REFERENCE-DATA GATE: coverage unreadable ({exc}) -- every dependent step BLOCKED"],
                    "note": "fail closed: no coverage record is not evidence of currency"}

    series_state = state.get("series") or {}
    named = sorted({s for v in STEP_DEPENDENCIES.values() for s in v["series"]})
    detail = {}
    for name in sorted(set(named) | set(series_state)):
        rec = series_state.get(name)
        if not rec or not rec.get("last_date"):
            detail[name] = {"last_date": None, "stale": True,
                            "reason": ("no entry in research/ledger/data_coverage.json -- treated as STALE "
                                       "(fail closed), never as current"),
                            "updater": (rec or {}).get("updater")}
            continue
        last = _date.fromisoformat(str(rec["last_date"])[:10])
        stale = last < session_date
        detail[name] = {"last_date": last.isoformat(), "stale": stale,
                        "days_short": (session_date - last).days if stale else 0,
                        "reason": (f"coverage ends {last.isoformat()}, the session is {session_date.isoformat()}"
                                   if stale else "covers the session"),
                        "updater": rec.get("updater")}

    stale = sorted(n for n, r in detail.items() if r["stale"])
    blocked = {}
    allowed = list(INDEPENDENT_STEPS)
    for step, dep in STEP_DEPENDENCIES.items():
        bad = [s for s in dep["series"] if detail.get(s, {"stale": True})["stale"]]
        if bad:
            blocked[step] = {"series": bad, "why": dep["why"],
                             "reason": "; ".join(f"{s}: {detail[s]['reason']}" for s in bad),
                             "updater": sorted({detail[s].get("updater") for s in bad if detail[s].get("updater")})}
        else:
            allowed.append(step)

    # Salvage reruns owed -- surfaced while pending (Jason's follow-up 1).
    reruns = {"owed": False, "strategies": [], "blocked_by": []}
    try:
        import strategy_registry as sr
        rows = registry_rows if registry_rows is not None else sr.read_rows()
        sup = sr.superseded_salvages(rows)
        blk = sr.blocked_pending_reference_data(rows)
        by = sorted({s for r in sup for s in (r.get("blocked_by") or [])})
        reruns = {"owed": bool(sup), "strategies": [r["strategy_id"] for r in sup],
                  "blocked_candidates": [r["strategy_id"] for r in blk],
                  "blocked_by": by,
                  "runnable_now": bool(sup) and not [s for s in by if detail.get(s, {"stale": True})["stale"]]}
    except Exception as exc:  # noqa: BLE001
        reruns["note"] = f"registry unreadable: {exc}"

    lines = [f"REFERENCE-DATA GATE (session {session_date.isoformat()}) -- "
             + ("every series covers the session; nothing blocked"
                if not stale else f"STALE: {', '.join(stale)}")]
    for step, b in sorted(blocked.items()):
        lines.append(f"  BLOCKED  {step}  <- {', '.join(b['series'])}  ({b['why']})")
    if blocked:
        lines.append("  STILL RUNS: " + ", ".join(INDEPENDENT_STEPS))
        lines.append("  Blocked is not aborted: the cycle runs every step above and reports the block.")
    if reruns.get("owed"):
        lines.append("  salvage reruns owed: " + ", ".join(reruns["strategies"])
                     + (f" -- blocked by {', '.join([s for s in reruns['blocked_by'] if detail.get(s, {'stale': True})['stale']]) or 'nothing named'}"
                        if not reruns.get("runnable_now") else " -- COVERAGE IS CURRENT: run src/rerun_salvages.py THIS CYCLE"))
    if reruns.get("blocked_candidates"):
        lines.append("  BLOCKED_PENDING_REFERENCE_DATA: " + ", ".join(reruns["blocked_candidates"])
                     + " -- these take no queue slot and Step 4 must not advance them")

    return {"ok": not stale, "session_date": session_date.isoformat(), "stale_series": stale,
            "series": detail, "blocked_steps": blocked, "allowed_steps": allowed,
            "salvage_reruns": reruns, "lines": lines,
            "rule": "Jason, September 16th 2026: any reference data past its coverage date blocks the "
                    "steps that use it and gets reported, never defaulted. A series with no coverage "
                    "entry is treated as stale (fail closed)."}


def reference_data_status() -> dict:
    """Directive s.3 Step 1, added 2026-09-16. The non-price reference series --
    VXN and the FOMC/CPI/NFP calendar -- have their own coverage ends, and two
    consecutive cycles burned a Step 4 on a candidate that could not be
    specified because nobody saw the series had run out.

    Surfaced here so staleness is visible BEFORE a candidate is spent on it.
    Reported, never judged: a stale series does not fail preflight, because the
    consumers already fail closed on it (src/reference_data.py). What preflight
    owes the cycle is the warning."""
    try:
        import reference_data as rd
        state = rd.coverage()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "note": f"reference-data coverage unreadable: {exc}", "series": {}}
    stale = state["stale_series"]
    return {"ok": True, "stale_series": stale,
            "covers_price_data": not stale,
            "price_data_end": state["price_data_end"],
            "series": {n: {"last_date": r["last_date"], "stale": r["stale"],
                           "days_short": r["days_short_of_price_data"],
                           "updater": r["updater"], "n_consumers": len(r["consumers"])}
                       for n, r in state["series"].items()},
            "lines": rd.plain_lines(state),
            "note": state["note"]}


def paper_book_status(today=None) -> dict:
    """Directive s.3 Step 1: preflight reports the paper book -- how many
    strategies are live in paper, each one's trade count and days elapsed, and
    whether any has hit its judgment point.

    Amendment 1 (Jason, September 16th 2026): the judgment point is 40 TRADES
    and nothing else. SLOW strategies are shown distinctly (background paper, no
    queue slot, no clock) and are never reported as at judgment point before 40
    trades; neither is anything else."""
    try:
        import paper_book as pb
        bk = pb.book(today=today)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "note": f"paper book unreadable: {exc}", "strategies": [], "at_judgment": []}
    strategies = [{"strategy_id": s["strategy_id"], "name": s["name"], "stage": s["stage"], "trades": s["trades"],
                   "days_elapsed": s["days_elapsed"], "trades_to_judgment": s["trades_to_judgment"],
                   "weeks_to_judgment": s["weeks_to_judgment"], "at_judgment_point": s["at_judgment_point"],
                   "slow": bool(s.get("slow")), "six_week_mark_passed": s.get("six_week_mark_passed"),
                   "judgment_reason": s["judgment_reason"]} for s in bk["strategies"]]
    at = [s["strategy_id"] for s in strategies if s["at_judgment_point"]]
    slow = [s["strategy_id"] for s in strategies if s["slow"]]
    if not strategies:
        note = "no strategy in paper yet"
    else:
        parts = []
        for s in strategies:
            head = f"{s['strategy_id']} {s['trades']} trades / {s['days_elapsed']} days"
            if s["at_judgment_point"]:
                parts.append(head + f" -- AT JUDGMENT POINT ({s['judgment_reason']})")
            elif s["slow"]:
                parts.append(head + f" -- SLOW (background, no queue slot; {s['trades_to_judgment']} more trade(s) to 40)")
            else:
                parts.append(head + f" ({s['trades_to_judgment']} trades to judgment, six-week mark in "
                                    f"{s['weeks_to_judgment']} wk)")
        note = "; ".join(parts)
    return {"ok": True, "n_in_paper": len(strategies), "n_slow": len(slow), "slow": slow,
            "strategies": strategies, "at_judgment": at,
            "plumbing": [p["paper_log_name"] for p in bk["plumbing"]], "note": note}


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
    steps["shelf"] = {"ok": True, **shelf}
    print(f"  [info] shelf (retired)  {shelf.get('line','?')[:80]}")
    q = queue_status()
    steps["queue"] = {"ok": q.get("ok", False), **q}
    print(f"  [{'ok' if q.get('ok') else 'warn'}]   candidate queue {', '.join(q.get('queue', [])) or 'EMPTY'}")
    print(f"         -> {q.get('note','')}")
    ref = reference_data_status()
    steps["reference_data"] = {"ok": ref.get("ok", False), **ref}
    _stale = ref.get("stale_series") or []
    print(f"  [{'ok' if ref.get('ok') and not _stale else 'warn'}]   reference data  "
          + ("VXN + FOMC/CPI/NFP calendar all cover the price data"
             if ref.get("ok") and not _stale else
             (f"STALE: " + ", ".join(f"{n} ends {ref['series'][n]['last_date']}" for n in _stale)
              if ref.get("ok") else ref.get("note", "unreadable"))))
    if _stale:
        print("         -> consumers FAIL CLOSED past these dates (they refuse the session, they do not guess). "
              "Top up from Jason's own Terminal:")
        for n in _stale:
            print(f"            {n}: {ref['series'][n]['updater']}  ({ref['series'][n]['n_consumers']} consumer(s), "
                  f"{ref['series'][n]['days_short']}d short)")

    gate = reference_data_gate(ref if ref.get("ok") else None)
    steps["reference_data_gate"] = {"ok": True, **gate}   # a block is never a preflight FAILURE
    for ln in gate["lines"]:
        print("  " + ("[gate] " if ln.startswith("REFERENCE") else "       ") + ln)

    pbk = paper_book_status()
    steps["paper_book"] = {"ok": pbk.get("ok", False), **pbk}
    print(f"  [{'ok' if pbk.get('ok') else 'warn'}]   PAPER BOOK      {pbk.get('n_in_paper', 0)} strateg{'y' if pbk.get('n_in_paper', 0) == 1 else 'ies'} in paper"
          + (f" ({pbk.get('n_slow')} SLOW: background, no queue slot, judged at 40 trades)" if pbk.get("n_slow") else "")
          + (f"; AT JUDGMENT POINT: {', '.join(pbk['at_judgment'])} -- Director verdict THIS cycle (s.6)" if pbk.get("at_judgment") else ""))
    print(f"         -> {pbk.get('note','')}")

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
        print("PREFLIGHT COMPLETE -- Step 2 data check, Step 3 advance the paper book, Step 4 advance one candidate (directive s.3).")
    if gate["blocked_steps"]:
        print(f"REFERENCE-DATA GATE: {len(gate['blocked_steps'])} step(s) BLOCKED by "
              f"{', '.join(gate['stale_series'])} -- the cycle still runs everything else and "
              f"the session report must say which steps were blocked and why.")
    print(f"receipt -> {RECEIPT}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
