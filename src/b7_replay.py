"""
b7_replay.py -- STEP A of the data-refresh queue item (Jason, 2026-09-14):
"Replay first, before any live paper session."

Feeds every session on disk from B7's execution anchor forward through the
REAL B7 loop (bot_stack_paper_run.run_session: B3 signal -> B2 decision ->
B6 gate -> B4a order path against the simulated broker) as if each were
arriving live, and captures every order the bot would have placed. This is
a MECHANICAL check, not a performance measurement -- P&L is recorded because
run_session records it, but nothing here scores the strategy.

TWO CLOCKS, KEPT APART: replay writes to its OWN log and journal under
research/forward_validation/b7_replay/ and never touches
bot_stack_paper_log.jsonl (the execution record) or the statistical log.
The replay is rebuilt from scratch every run (log truncated, journal files
truncated -- never deleted, the device shell cannot delete) so it is always
a full re-derivation, never an accumulation.

MECHANICAL CHECKS (any FAIL = a defect to fix BEFORE live paper begins):
  R1 one row per session            -- every session produced exactly one log row
  R2 at most one order per session  -- B3 is one trade/day; >1 order_intent in a
                                       session is a double order
  R3 unique order ids               -- no order_id reused across the replay
  R4 every order terminal           -- each order_intent has an ack, a reject, or
                                       a recovery_action (no hanging orders)
  R5 no hanging positions           -- every session with filled_qty > 0 has a
                                       bookkeeping exit (exit_reason set)
  R6 requested price == spec price  -- the order's intended_price equals the
                                       signal's entry that session (spec-intended
                                       vs what the bot actually requested)
  R7 quantity within cap            -- every intent quantity in (0, max_contracts]
  R8 signal timing / exactly-once   -- base_entry_b3.audit() over the sessions
Then execution_measurement.measure() runs over the replay journal (the 14
checks, labelled REPLAY so they are never mistaken for the live record).

Output: research/forward_validation/b7_replay/replay_report.json and the
Execution block (execution_block.render) printed for the cycle report.

Usage: python3 src/b7_replay.py [--from YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import bot_stack_paper_run as bpr  # noqa: E402
from base_entry_b3 import audit, generate_signals  # noqa: E402
from capital_protection import CONFIG as CAPITAL_CONFIG  # noqa: E402
from order_path import OrderPathJournal  # noqa: E402
import execution_measurement  # noqa: E402

REPLAY_DIR = bpr.LOG_DIR / "b7_replay"
REPLAY_LOG = REPLAY_DIR / "replay_log.jsonl"
REPLAY_JOURNAL = REPLAY_DIR / "journal"
REPLAY_REPORT = REPLAY_DIR / "replay_report.json"


def _reset(replay_dir: Path) -> None:
    """Truncate, never delete (device shell cannot rm)."""
    (replay_dir / "journal").mkdir(parents=True, exist_ok=True)
    (replay_dir / "replay_log.jsonl").write_text("")
    for p in (replay_dir / "journal").glob("*.jsonl"):
        p.write_text("")


def replay(df: pd.DataFrame, sessions: list, replay_dir: Path) -> dict:
    """Run the real B7 loop over `sessions`, journaling under replay_dir.
    Returns {"rows": [...], "intents_per_session": {date: n}}."""
    _reset(replay_dir)
    log_path, journal_dir = replay_dir / "replay_log.jsonl", replay_dir / "journal"
    saved = (bpr.LOG_PATH, bpr.JOURNAL_DIR)
    bpr.LOG_PATH, bpr.JOURNAL_DIR = log_path, journal_dir
    try:
        journal = OrderPathJournal(journal_dir)
        rows, per_session = [], {}
        for d in sessions:
            ok, why = bpr.session_is_complete(df[df.index.date == d])
            if not ok:
                per_session[str(d)] = 0
                rows.append({"date": str(d), "outcome": "skipped_incomplete", "note": why,
                             "replay": True})
                continue
            before = sum(1 for r in journal.all_records() if r.get("event") == "order_intent")
            row = bpr.run_session(d, df[df.index.date == d], rows)
            row["replay"] = True
            bpr.append_row(row)
            rows.append(row)
            after = sum(1 for r in journal.all_records() if r.get("event") == "order_intent")
            per_session[str(d)] = after - before
    finally:
        bpr.LOG_PATH, bpr.JOURNAL_DIR = saved
    return {"rows": rows, "intents_per_session": per_session}


def mechanical_checks(rows: list[dict], per_session: dict, journal_dir: Path, df: pd.DataFrame,
                      sessions: list) -> list[dict]:
    records = OrderPathJournal(journal_dir).all_records()
    intents = [r for r in records if r.get("event") == "order_intent"]
    terminal = {r["order_id"] for r in records
                if r.get("event") in ("order_ack", "order_rejected", "recovery_action")}
    out = []

    def add(name, n, passed, note=""):
        out.append({"check": name, "n": n, "passed": passed,
                    "status": "PASS" if passed == n else "FAIL", "note": note})

    add("R1 one row per session", len(sessions), len(rows) if len(rows) == len(sessions) else 0,
        f"{len(rows)} rows for {len(sessions)} sessions")
    doubles = {d: n for d, n in per_session.items() if n > 1}
    add("R2 at most one order per session", len(per_session), len(per_session) - len(doubles),
        f"double orders: {doubles}" if doubles else "")
    ids = [r["order_id"] for r in intents]
    add("R3 unique order ids", len(ids), len(set(ids)))
    hanging = [i["order_id"] for i in intents if i["order_id"] not in terminal]
    add("R4 every order terminal", len(intents), len(intents) - len(hanging),
        f"hanging: {hanging}" if hanging else "")
    filled = [r for r in rows if (r.get("order_path", {}).get("filled_qty") or 0) > 0]
    add("R5 no hanging positions", len(filled),
        sum(1 for r in filled if r.get("bookkeeping", {}).get("exit_reason")),
        "" if filled else "no fills in replay")
    entry_by_tag = {}
    for r in rows:
        if "signal" in r:
            entry_by_tag[r["date"]] = float(r["signal"]["entry"])
    mism = []
    for i in intents:
        tag_ts = str(i.get("client_tag", "")).split(":", 1)[-1][:10]
        spec = entry_by_tag.get(tag_ts)
        if spec is None or abs(float(i.get("intended_price", 0)) - spec) > 1e-9:
            mism.append((i["order_id"], i.get("intended_price"), spec))
    add("R6 requested price == spec price", len(intents), len(intents) - len(mism),
        f"mismatches: {mism}" if mism else "")
    add("R7 quantity within cap", len(intents),
        sum(1 for i in intents if 0 < i.get("quantity", 0) <= CAPITAL_CONFIG.max_contracts))
    sigs = generate_signals(df[[dd in set(sessions) for dd in df.index.date]])
    a = audit(sigs)
    a_ok = int(bool(a.get("pass")))
    out.append({"check": "R8 signal timing / exactly-once (base_entry_b3.audit)", "n": len(sigs),
                "passed": len(sigs) if a_ok else 0, "status": "PASS" if a_ok else "FAIL", "note": json.dumps(a)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="from_date", default=None, help="first session (default: B7 anchor)")
    args = ap.parse_args(argv)

    from data_loader import load_price_data
    df, synthetic = load_price_data(context="b7_replay.py", apply_holdout=False)
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    all_dates = sorted(set(df.index.date))
    start = pd.Timestamp(args.from_date).date() if args.from_date else bpr._b7_execution_anchor(all_dates)
    sessions = [d for d in all_dates if d >= start]
    print(f"B7 REPLAY (Step A) -- {len(sessions)} session(s) from {start} to {sessions[-1] if sessions else '-'}")

    res = replay(df, sessions, REPLAY_DIR)
    checks = mechanical_checks(res["rows"], res["intents_per_session"], REPLAY_JOURNAL, df, sessions)
    meas = execution_measurement.measure(journal_dir=REPLAY_JOURNAL)
    outcomes = {}
    for r in res["rows"]:
        outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
    report = {
        "ran_at_utc": datetime.now(timezone.utc).isoformat(), "label": "REPLAY -- not the live execution record",
        "sessions": [str(d) for d in sessions], "outcomes": outcomes,
        "n_order_intents": meas["n_order_intents"], "n_fills": meas["n_fills"],
        "mechanical_checks": checks, "execution_measurement_replay": meas,
        "defects": [c for c in checks if c["status"] == "FAIL"],
        "step_a_clean": all(c["status"] == "PASS" for c in checks),
    }
    REPLAY_REPORT.write_text(json.dumps(report, indent=2, default=str))
    for c in checks:
        print(f"  {c['status']:<4} {c['check']} ({c['passed']}/{c['n']}) {c['note']}")
    print(f"Outcomes: {outcomes}")
    print(f"Step A clean: {report['step_a_clean']}  -> {REPLAY_REPORT}")
    from execution_block import render
    print("\n" + render(replay_report=report))
    return 0 if report["step_a_clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
