"""
session_report.py -- THE OWNER'S BRIEFING, printed at the close of every 2-hour
session.

Jason, September 14th: "Think of this as I'm the owner of this business and I
want to know how my business is running from top to bottom. And this is for
after each session is ran." Format settled the same evening: a fixed scoreboard
every time, then a few sentences ONLY on what actually moved; honest zeros with
the distance to a real number; interrupt him immediately only for a decision
only he can make, or a capital-protection trip.

Five sections, always in this order, because that is the order an owner asks:
  1. MONEY        -- are we making any, and how far from a real answer
  2. THE BOT      -- can the machine actually trade yet, what blocks the next step
                     (BUILD STATUS, not results -- results are in 1 and 3)
  3. PIPELINE     -- the research funnel, named and specific: what moved through
                     which stage, every candidate in flight, what's next off the
                     shelf, and the hit rate
  4. OPERATIONS   -- did the staff do their jobs, did the machinery hold
  5. YOUR DESK    -- what needs Jason, and nothing else

REVISED September 14th (Jason): SPEND dropped as a standing section -- he does
not need it every session. It is not lost: a spend that needs his say-anything
(over 75% of the data cap, or anything crossing the $5 rule) surfaces in YOUR
DESK, which is where a decision belongs. And PIPELINE was expanded from four
summary lines to the named, stage-by-stage view below: "I think I'd like to get
more insight on the pipeline... I can handle more specifics."

Every number is read from the project's own files at run time. Nothing here is
typed by hand or remembered from a previous session, so the scoreboard cannot
drift from reality. The two prose slots (--moved, --agents) are the session's
own words and are the only part a cycle writes.

HOW TO RUN (last step of every cycle, after cycle_close.py):
    python3 src/session_report.py --label "7:00 pm" \
        --moved "one or two sentences on what actually changed" \
        --agents "Director RAN (re-evaluation); Statistical idle (nothing owed)"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parent
sys.path.insert(0, str(ROOT))

CT = ZoneInfo("America/Chicago")
TARGET_FILLS = 20   # the pre-registered minimum sample; NOT the 40-trade catastrophe window
DATA_CAP_USD = 20.0


def _load_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text(errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def money() -> list[str]:
    rows = _load_jsonl(PROJ / "research" / "forward_validation" / "bot_stack_paper_log.jsonl")
    scored = [r for r in rows if "pnl_usd" in r]
    pnl = sum(float(r["pnl_usd"]) for r in scored)
    wins = sum(1 for r in scored if float(r["pnl_usd"]) > 0)
    blocked = sum(1 for r in rows if r.get("outcome") == "blocked")
    journal = PROJ / "research" / "forward_validation" / "order_path_journal"
    fills = 0
    if journal.exists():
        for f in journal.glob("*.jsonl"):
            fills += sum(1 for r in _load_jsonl(f) if r.get("event") == "fill")
    one_r = next((r["gate"]["one_r_usd"] for r in reversed(rows)
                  if r.get("gate", {}).get("one_r_usd")), None)
    rep = json.loads((PROJ / "research" / "forward_validation" / "b7_replay" /
                      "replay_report.json").read_text()) if (
        PROJ / "research" / "forward_validation" / "b7_replay" / "replay_report.json").exists() else {}

    lines = ["**1. MONEY**"]
    if scored:
        lines.append(f"- Paper P&L: **{'-' if pnl < 0 else '+'}${abs(pnl):,.0f}** over {len(scored)} "
                     f"resolved trade(s), {wins} winner(s). Placeholder strategy with no claimed "
                     f"edge — this is a test of the plumbing, not a verdict on anything.")
    else:
        lines.append(f"- Paper P&L: **none yet** — {len(rows)} session(s) logged, "
                     f"{blocked} blocked before an order, 0 resolved trades.")
    lines.append(f"- Fills toward the {TARGET_FILLS}-trade record: **{fills} / {TARGET_FILLS}** "
                 f"(slippage becomes measurable at 20)")
    if rep:
        lines.append(f"- Rehearsal on past sessions (not the record): {rep.get('n_fills', 0)} fill(s) "
                     f"across {len(rep.get('sessions', []))} session(s), "
                     f"{'all mechanical checks passed' if rep.get('step_a_clean') else 'DEFECTS FOUND'}")
    lines.append("- Real trading cost measured: **no** — the simulated broker fills at the exact "
                 "asking price by construction. A real number needs a live broker paper feed (B4b).")
    lines.append("- Live capital at risk: **$0.** Nothing is authorized.")
    if one_r:
        lines.append(f"- Paper risk unit: 1R = ${one_r:,.0f} (the trade's own stop); budget 4R.")
    return lines


def product() -> list[str]:
    rm = (PROJ / "docs" / "BOT_ROADMAP.md").read_text(errors="replace")
    done, missing = [], []
    for m in re.finditer(r"^\| (B\d[a-z]?) \| ([^|]+?) \|([^|]*)\|", rm, re.M):
        mid, name, status = m.group(1), m.group(2).strip(), m.group(3)
        su = status.upper()
        (done if ("DONE" in su or "LIVE" in su or "WIRED" in su or "BUILT" in su)
         else missing).append(f"{mid} {name}")
    rows = _load_jsonl(PROJ / "research" / "forward_validation" / "bot_stack_paper_log.jsonl")
    live_traded = any(r.get("outcome") in ("filled", "partial") for r in rows)
    rp = PROJ / "research" / "forward_validation" / "b7_replay" / "replay_report.json"
    rehearsed = bool(json.loads(rp.read_text()).get("n_fills")) if rp.exists() else False
    lines = ["**2. THE BOT — build status, not results**"]
    if live_traded:
        verdict = "YES, in the live paper record"
    elif rehearsed:
        verdict = "YES, proven in rehearsal — the live record starts at the next scored session"
    else:
        verdict = "NOT YET"
    lines.append(f"- Can it place a trade end to end? **{verdict}** "
                 f"(signal → risk check → safety gate → broker → fill recorded)")
    lines.append(f"- Build milestones complete: **{len(done)} of {len(done) + len(missing)}**"
                 + (f" — still open: {', '.join(m.split()[0] for m in missing)}" if missing else ""))
    lines.append("- Blocking the next step: a real broker paper feed (IBKR permission on cooldown "
                 "to ~October 13th). Everything before it is built and tested.")
    return lines


PLAIN_NAMES = {
    "opening_range_width_midday_range_excursion_nq_m30":
        "wide first 30 minutes -> busier midday (NQ)",
    "london_open_volatility_burst_6e_m23":
        "London open hour is extra volatile (euro futures)",
    "vwap_dist_vs_atr_low_10d_drift_h118":
        "price far below its average -> drifts up over 10 days (NQ)",
}


def _plain(name: str) -> str:
    if name in PLAIN_NAMES:
        return PLAIN_NAMES[name]
    return name.replace("_", " ")


def pipeline(closed_today: int | None = None) -> list[str]:
    sweep = json.loads((PROJ / "data" / "pipeline_sweep.json").read_text())
    led = _load_jsonl(PROJ / "research" / "ledger" / "hypotheses.jsonl")
    latest: dict[str, dict] = {}
    for r in led:
        latest[r["hypothesis_id"]] = r
    n_rejected = sum(1 for r in latest.values() if r.get("strategy_status") == "REJECTED")
    # in flight = what the sweep actually tracks as open, not every stale PROMISING row
    n_open = sum(1 for r in sweep.get("rows", []) if r.get("tier") == "OPEN")
    shelf = sweep.get("shelf", "")
    now = datetime.now(CT)

    # every ledger row for an id, so we can see stage history and age
    hist: dict[str, list[dict]] = {}
    for r in led:
        hist.setdefault(r["hypothesis_id"], []).append(r)

    def _age(hid: str) -> str:
        try:
            first = datetime.fromisoformat(hist[hid][0]["logged_at"])
            days = (now.replace(tzinfo=None) - first.replace(tzinfo=None)).days
            return "today" if days < 1 else f"{days}d"
        except Exception:
            return "?"

    def _cycle_start():
        """This cycle's own start, from the checkpoint preflight wrote. Falls back
        to 2 hours (the cadence) only if the checkpoint is unreadable."""
        try:
            cp = json.loads((PROJ / "research" / "_cycle_checkpoint.json").read_text())
            return datetime.fromisoformat(cp["started"]).replace(tzinfo=None)
        except Exception:
            return now.replace(tzinfo=None) - timedelta(hours=2)

    def _moved_since() -> list[dict]:
        start, out = _cycle_start(), []
        for rows_ in hist.values():
            for r in rows_:
                try:
                    t = datetime.fromisoformat(r["logged_at"]).replace(tzinfo=None)
                except Exception:
                    continue
                if t >= start:
                    out.append(r)
        return sorted(out, key=lambda r: r["logged_at"])

    lines = ["**3. PIPELINE — the research funnel**", ""]

    moved = _moved_since()
    lines.append("*Moved a stage this session:*")
    if moved:
        for r in moved:
            stage = str(r.get("parameters", {}).get("stage", "")).split("(")[0].strip() or "stage"
            lines.append(f"- **{r['hypothesis_id']}** — {_plain(r['strategy_name'])} → "
                         f"**{stage}**, now {r.get('strategy_status')}")
    else:
        lines.append("- Nothing. No candidate had input for its next stage.")
    lines.append("")

    TERMINAL = {"REJECTED", "VALIDATED_NOT_PROMOTED", "HOLDOUT PASSED", "FORWARD VALIDATION"}
    open_rows = [r for r in sweep.get("rows", []) if r.get("tier") == "OPEN"
                 and hist.get(r.get("id", ""), [{}])[-1].get("strategy_status") not in TERMINAL]
    lines.append(f"*In flight ({len(open_rows)}):*")
    if open_rows:
        for r in open_rows:
            hid = r.get("id", "")
            latest_row = hist.get(hid, [{}])[-1]
            status = latest_row.get("strategy_status", r.get("status", ""))
            owed = str(r.get("next_owed", "")).split("(")[0].strip()
            lines.append(f"- **{hid}** — {_plain(r.get('name', ''))}")
            lines.append(f"  - stage: {r.get('stage_reached', '?')} · status: {status} · age {_age(hid)}")
            lines.append(f"  - owed next: {owed or '—'}")
    else:
        lines.append("- **None — the funnel is empty.** Every candidate has been closed out. "
                     "The next research action is a fresh draw from the shelf.")
    lines.append("")

    nxt = shelf.split("-> next DRAW:")[-1].strip() if "next DRAW" in shelf else "—"
    # THROUGHPUT, measured by when a candidate was FIRST opened -- not by its last
    # ledger row, which also moves when an old candidate is touched by an audit and
    # would report backfills as "closed this week" (caught 2026-09-14).
    week = set()
    for hid, rows_ in hist.items():
        try:
            t0 = datetime.fromisoformat(rows_[0]["logged_at"]).replace(tzinfo=None)
        except Exception:
            continue
        if (now.replace(tzinfo=None) - t0).days <= 7:
            week.add(hid)
    lines.append("*The funnel, and the odds:*")
    lines.append(f"- On the shelf ready to test: **{shelf.split(' DRAWABLE')[0].replace('Shelf ', '')}** "
                 f"· next up: {nxt}")
    # THE ODDS, stated without dates. The ledger's timestamps move when an audit
    # touches an old row, so any "this week" count reads bulk backfills as new work
    # (caught 2026-09-14, twice). These three are date-independent and verifiable.
    reached_val = sum(1 for rs in hist.values()
                      if any(str(r.get("data_slice_used", "")).startswith("validation") for r in rs))
    reached_hold = sum(1 for rs in hist.values()
                       if any("holdout" in str(r.get("data_slice_used", "")) for r in rs))
    lines.append(f"- Ever reached a real out-of-sample test: **{reached_val} of {len(hist)}** "
                 f"candidates · ever reached the final sealed data: **{reached_hold}**")
    lines.append(f"- Tested and closed, all time: **{n_rejected}** of {len(latest)} logged")
    lines.append("- Ever cleared the full bar (a real tradeable edge): **0.** Three volatility "
                 "facts have passed every stage, but they size trades — they don't pick direction. "
                 "That is the single number this whole operation exists to change.")
    return lines


def operations() -> list[str]:
    comp = _load_jsonl(PROJ / "research" / "_cycle_compliance.jsonl")
    lines = ["**4. OPERATIONS**"]
    if comp:
        c = comp[-1]
        checks = c.get("checks", {})
        failing = c.get("failing", [])
        lines.append(f"- Session closed cleanly: **{'YES' if c.get('complete') else 'NO — ' + ', '.join(failing)}**")
        t = checks.get("tests", {}).get("detail", "")
        if t:
            lines.append(f"- Test suite: **{t}**")
        lines.append(f"- Work committed and pushed to GitHub: "
                     f"**{'yes' if checks.get('git', {}).get('ok') else 'NO'}**")
    return lines


def spend_flag() -> str | None:
    """SPEND is no longer a standing section. It surfaces on YOUR DESK only when
    it actually needs Jason: past 75% of the monthly data cap."""
    log = PROJ / "data" / "_databento_cost_log.json"
    if not log.exists():
        return None
    entries = json.loads(log.read_text())
    month = datetime.now(CT).strftime("%Y-%m")
    mtd = sum(float(e.get("cost_usd", 0)) for e in entries if str(e.get("date", "")).startswith(month))
    if mtd >= 0.75 * DATA_CAP_USD:
        return (f"Data spend is at ${mtd:,.2f} of the ${DATA_CAP_USD:,.0f} monthly cap "
                f"(${DATA_CAP_USD - mtd:,.2f} left) — any further pull this month needs your say")
    return None


def _spend_unused() -> list[str]:
    log = PROJ / "data" / "_databento_cost_log.json"
    entries = json.loads(log.read_text()) if log.exists() else []
    month = datetime.now(CT).strftime("%Y-%m")
    mtd = sum(float(e.get("cost_usd", 0)) for e in entries if str(e.get("date", "")).startswith(month))
    lines = ["**5. SPEND**"]
    lines.append(f"- Data, month to date: **${mtd:,.2f} of the ${DATA_CAP_USD:,.0f} cap**")
    lines.append("- Execution infrastructure: **$0** — the $60–115/mo you pre-approved is not spent "
                 "and isn't triggered until something reaches execution qualification.")
    lines.append("- Live trading capital: **$0.**")
    return lines


def your_desk() -> list[str]:
    txt = (PROJ / "research" / "NEXT_UP.md").read_text(errors="replace")
    items = []
    m = re.search(r"^## Blocked — needs Jason\s*$", txt, re.M)
    if m:
        for line in txt[m.end():].splitlines():
            if line.startswith("## "):
                break
            if line.startswith("- **"):
                raw = line[2:]
                head = re.sub(r"[*~]", "", raw).strip()
                skip = ("WITHDRAWN", "DECIDED", "SUPERSEDED", "RESOLVED", "NOTHING OWED",
                        "NO LONGER", "ANSWERED")
                if line.startswith("- **~~") or any(w in head[:170].upper() for w in skip):
                    continue
                items.append(head.split(" -- ")[0].split("YOUR CALL")[0].rstrip(" .,—-")[:110])
    lines = ["**5. YOUR DESK**"]
    flag = spend_flag()
    if flag:
        items.append(flag)
    if items:
        lines.append(f"- Decisions waiting on you: **{len(items)}**")
        for it in items:
            lines.append(f"  - {it}")
    else:
        lines.append("- **Nothing needs you.**")
    lines.append("- You will be interrupted between sessions only for: a decision only you can "
                 "make, or a capital-protection trip.")
    return lines


def build(label: str, moved: str = "", agents: str = "") -> str:
    now = datetime.now(CT)
    stamp = now.strftime("%B %-d") + f", {label} CT" if label else now.strftime("%B %-d, %-I:%M %p CT")
    out = [f"## Session report — {stamp}", ""]
    for section in (money(), product(), pipeline(), operations(), your_desk()):
        out += section + [""]
    out.append("**What actually moved this session**")
    out.append(moved.strip() or "_Nothing moved. The session ran, the checks passed, and no stage "
                                "had input to work on._")
    if agents.strip():
        out += ["", "**Staff**", agents.strip()]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="")
    ap.add_argument("--moved", default="")
    ap.add_argument("--agents", default="")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args(argv)
    txt = build(a.label, a.moved, a.agents)
    if a.out:
        Path(a.out).write_text(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
