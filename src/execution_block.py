"""
execution_block.py -- the short **Execution** block for cycle reports.

Set by the data-refresh queue item (Jason, 2026-09-14, S3): reporting stays
inside the existing 2-hour cycle reports -- no separate stream. Each cycle
report that touches execution adds this block:
  - fills this cycle (replay or live, labelled which)
  - cumulative fill count toward the 40-trade sample (slippage becomes
    measurable at 20 fills -- capital_protection.CONFIG.slippage_window_fills)
  - measured cost so far: average slippage per fill, fees, spec-vs-actual
    deviation -- real numbers, or "no live fills yet"
  - any mechanical defect found and whether it is fixed

Live numbers come from B7's execution record (bot_stack_paper_log.jsonl +
its order_path journal). Replay numbers come from b7_replay's report and are
always labelled REPLAY. Fees: the simulated broker charges none, so the fee
line says so rather than printing a fabricated 0.

Usage: python3 src/execution_block.py [--since ISO] [--replay-report PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import bot_stack_paper_run as bpr  # noqa: E402
from capital_protection import CONFIG as CAPITAL_CONFIG  # noqa: E402
from order_path import OrderPathJournal  # noqa: E402

TARGET_SAMPLE = 40
CHECKPOINT = bpr.PROJECT_ROOT / "research" / "_cycle_checkpoint.json"
REPLAY_REPORT = bpr.LOG_DIR / "b7_replay" / "replay_report.json"


def _cycle_start() -> str | None:
    try:
        return json.loads(CHECKPOINT.read_text()).get("started")
    except Exception:
        return None


def live_stats(journal_dir: Path = None, since: str | None = None) -> dict:
    journal_dir = journal_dir or bpr.JOURNAL_DIR
    fills = [r for r in OrderPathJournal(journal_dir).all_records() if r.get("event") == "fill"] \
        if Path(journal_dir).exists() else []
    this_cycle = [f for f in fills if since and str(f.get("ts", "")) >= since]
    devs = [f["deviation_pts"] for f in fills if f.get("deviation_pts") is not None]
    return {"fills_total": len(fills), "fills_this_cycle": len(this_cycle) if since else None,
            "avg_slippage_pts": round(sum(devs) / len(devs), 4) if devs else None,
            "max_abs_deviation_pts": round(max(abs(d) for d in devs), 4) if devs else None}


def render(replay_report: dict | None = None, live: dict | None = None, since: str | None = None) -> str:
    since = since or _cycle_start()
    live = live if live is not None else live_stats(since=since)
    lines = ["### Execution"]
    if replay_report:
        lines.append(f"- Fills this cycle: {replay_report.get('n_fills', 0)} (REPLAY, "
                     f"{len(replay_report.get('sessions', []))} sessions, "
                     f"{replay_report.get('n_order_intents', 0)} orders; not the live record)")
    n_live_cycle = live["fills_this_cycle"] if live["fills_this_cycle"] is not None else "n/a (no cycle start)"
    lines.append(f"- Fills this cycle: {n_live_cycle} (LIVE paper)")
    lines.append(f"- Cumulative live fills: {live['fills_total']} / {TARGET_SAMPLE} "
                 f"(slippage measurable at {CAPITAL_CONFIG.slippage_window_fills})")
    if live["fills_total"]:
        lines.append(f"- Measured cost so far: avg slippage {live['avg_slippage_pts']:+.4f} pts/fill, "
                     f"max |spec-vs-actual| {live['max_abs_deviation_pts']:.4f} pts, "
                     f"fees: none charged by the simulated broker (not modelled)")
    else:
        lines.append("- Measured cost so far: no live fills yet")
    if replay_report:
        defects = replay_report.get("defects", [])
        if defects:
            lines.append("- Mechanical defects (replay): " + "; ".join(
                f"{d['check']} {d['passed']}/{d['n']} {d.get('note', '')}".strip() for d in defects)
                + " -- NOT yet fixed; live paper does not start until Step A is clean")
        else:
            lines.append("- Mechanical defects: none found in replay "
                         f"({len(replay_report.get('mechanical_checks', []))} checks PASS)")
    else:
        lines.append("- Mechanical defects: no replay this cycle")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    ap.add_argument("--replay-report", default=None)
    args = ap.parse_args(argv)
    rep = None
    p = Path(args.replay_report) if args.replay_report else REPLAY_REPORT
    if p.exists():
        rep = json.loads(p.read_text())
    print(render(replay_report=rep, since=args.since))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
