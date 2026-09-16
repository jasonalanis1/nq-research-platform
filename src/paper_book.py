"""
paper_book.py -- measures the PAPER BOOK: every strategy's forward paper record,
per strategy, from research/forward_validation/bot_stack_paper_log.jsonl.

Standing directive (research/infrastructure/standing-directive-2026-09-15.md)
s.5 lists what the owner sees per strategy; s.6 gives the verdict arithmetic;
s.11 says costs are ASSUMED until the broker connection measures them. This
module computes those numbers and nothing else. It never writes the log.

WHAT COUNTS
  * A trade = a paper-log row with `pnl_usd` (a fill that was bookkept to an
    exit). Blocked / no_signal / reset rows are not trades.
  * Rows are grouped by their `strategy` field (rows without it are B3's).
  * PLUMBING rows -- the execution dummy and the B3 ORB placeholder -- are
    reported in a separate list, labelled plumbing, and NEVER judged: they have
    no claimed edge and their record is a test of the order path (Jason,
    September 15th: keep it separate, never judge it).
  * The log's pnl_usd is GROSS (bot_stack_paper_run.py choice 6). The book
    deducts the ASSUMED round-trip cost per micro contract below, so every
    figure here is net of assumed costs and says so.

ASSUMED COSTS (src/integrity_checks.py's constants, applied to the MNQ micro the
paper book trades): commission $2.50/side and 1 tick (0.25 pt) slippage/side.
Round trip per micro = $5.00 + 2 * 0.25 pt * $2/pt = $6.00 = 3.0 index points.
Labelled ASSUMED everywhere until B4b exists; then the report says MEASURED.

JUDGMENT POINT (s.2/s.6 as AMENDED by Amendment 1, Jason, September 16th 2026):
**40 trades. Nothing is ever judged on fewer than 40 trades, SLOW or not.** The
six-week mark is still measured and reported for a non-SLOW strategy -- it is the
directive's clock and it says the strategy is late -- but reaching it with fewer
than 40 trades is NOT a judgment point: the strategy simply keeps trading, no
KILL, no verdict. The "< 15 trades in 6 weeks = KILL" rule is DROPPED.
SLOW (Amendment 1): a strategy whose own screen result projects fewer than 40
trades in six months (trades/sessions * 126 < 40) is labelled SLOW on its PAPER
row by src/strategy_registry.py. It paper trades in the BACKGROUND indefinitely,
takes no queue slot, runs no clock, and is judged whenever it reaches 40 trades.
SURVIVABLE DAILY LIMIT (s.5/s.6): a daily loss limit equal to THREE AVERAGE
WINNERS; the worst losing streak is compared against it.
COST-FRAGILE (s.11): average R under 0.10 on assumed costs.

USAGE
    python3 src/paper_book.py            # human-readable
    python3 src/paper_book.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from integrity_checks import COMMISSION_PER_SIDE_USD, SLIPPAGE_TICKS_PER_SIDE, TICK_SIZE  # noqa: E402
from strategy_registry import (  # noqa: E402
    PLUMBING_LOG_NAMES, read_rows as read_registry, in_paper as registry_in_paper,
    slow_ids as registry_slow_ids, SLOW_HORIZON_SESSIONS, SLOW_MIN_TRADES,
)

LOG = ROOT / "research" / "forward_validation" / "bot_stack_paper_log.jsonl"
B3_LOG_NAME = "base_entry_b3_orb_placeholder"

MNQ_USD_PER_PT = 2.0
JUDGE_TRADES = 40
JUDGE_WEEKS = 6
# Amendment 1 (Jason, September 16th 2026) dropped the 15-trade-at-6-weeks KILL.
# Nothing is judged on fewer than JUDGE_TRADES trades, so that is the floor too.
JUDGE_MIN_TRADES = JUDGE_TRADES
COST_FRAGILE_AVG_R = 0.10
SIZES = (1, 5, 10)
SLIPPAGE_BASIS = "ASSUMED"     # flips to MEASURED only when a real broker feed exists (B4b)

ASSUMED_COST_USD_PER_MICRO_RT = COMMISSION_PER_SIDE_USD * 2 + SLIPPAGE_TICKS_PER_SIDE * 2 * TICK_SIZE * MNQ_USD_PER_PT
ASSUMED_COST_PTS_RT = ASSUMED_COST_USD_PER_MICRO_RT / MNQ_USD_PER_PT


def load_log(path: Path | None = None) -> list[dict]:
    p = path or LOG
    if not p.exists():
        return []
    out = []
    for line in p.read_text(errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def log_name(row: dict) -> str:
    return row.get("strategy") or B3_LOG_NAME


def trades_for(rows: list[dict], name: str) -> list[dict]:
    """One dict per scored trade, chronological, NET of assumed costs per micro.
    r_net is per contract and size-independent; usd_1 is one micro."""
    out = []
    for r in rows:
        if log_name(r) != name or "pnl_usd" not in r:
            continue
        bk = r.get("bookkeeping") or {}
        risk_pts = float(bk.get("risk_points") or 0.0)
        qty = int((r.get("order_path") or {}).get("filled_qty") or 1) or 1
        gross_usd_1 = float(r["pnl_usd"]) / qty
        net_usd_1 = gross_usd_1 - ASSUMED_COST_USD_PER_MICRO_RT
        r_gross = bk.get("r_multiple")
        r_net = (net_usd_1 / (risk_pts * MNQ_USD_PER_PT)) if risk_pts > 0 else None
        out.append({"date": r.get("date"), "leg": r.get("leg"), "direction": (r.get("signal") or {}).get("direction"),
                    "risk_points": risk_pts, "exit_reason": bk.get("exit_reason"),
                    "r_gross": r_gross, "r_net": r_net, "usd_gross_1": round(gross_usd_1, 2), "usd_net_1": round(net_usd_1, 2)})
    return out


def worst_losing_streak(trades: list[dict]) -> dict:
    best_n, best_r, best_usd = 0, 0.0, 0.0
    n, r, usd = 0, 0.0, 0.0
    for t in trades:
        if t["usd_net_1"] < 0:
            n += 1; r += (t["r_net"] or 0.0); usd += t["usd_net_1"]
            if n > best_n or (n == best_n and usd < best_usd):
                best_n, best_r, best_usd = n, r, usd
        else:
            n, r, usd = 0, 0.0, 0.0
    return {"trades": best_n, "r": round(best_r, 3), "usd_1": round(best_usd, 2)}


def measure(trades: list[dict], first_session: str | None, today: date | None = None,
            slow: bool = False) -> dict:
    """Every s.5 number for one strategy, net of ASSUMED costs.

    `slow` is Amendment 1's label: a SLOW strategy runs no six-week clock, so
    `weeks_to_judgment` is None and only the 40th trade is a judgment point.
    A non-SLOW strategy still reports its six-week mark, but reaching it with
    fewer than 40 trades is not a verdict -- it keeps trading."""
    today = today or date.today()
    n = len(trades)
    rs = [t["r_net"] for t in trades if t["r_net"] is not None]
    wins = [t for t in trades if t["usd_net_1"] > 0]
    win_rate = (len(wins) / n) if n else None
    avg_r = (sum(rs) / len(rs)) if rs else None
    total_r = sum(rs) if rs else 0.0
    usd_1 = sum(t["usd_net_1"] for t in trades)
    avg_winner_usd = (sum(t["usd_net_1"] for t in wins) / len(wins)) if wins else None
    avg_winner_r = (sum(t["r_net"] for t in wins if t["r_net"] is not None) / len(wins)) if wins else None
    streak = worst_losing_streak(trades)
    survivable = None
    if avg_winner_usd is not None:
        limit = 3 * avg_winner_usd
        survivable = {"daily_limit_usd_1": round(limit, 2), "daily_limit_r": round(3 * avg_winner_r, 3) if avg_winner_r is not None else None,
                      "worst_streak_inside_limit": bool(-streak["usd_1"] <= limit)}
    days = None
    if first_session:
        try:
            days = (today - datetime.strptime(first_session, "%Y-%m-%d").date()).days
        except ValueError:
            days = None
    weeks_left = None if (days is None or slow) else max(0.0, JUDGE_WEEKS - days / 7.0)
    six_week_mark = None if days is None else bool(days >= JUDGE_WEEKS * 7)
    # Amendment 1: the ONLY judgment point is 40 trades, SLOW or not.
    at_point = n >= JUDGE_TRADES
    reason = None
    if at_point:
        reason = f"{JUDGE_TRADES} trades reached" + (" (SLOW strategy, judged on trades only)" if slow else "")
    elif slow:
        reason = None
    elif six_week_mark:
        reason = (f"{JUDGE_WEEKS} weeks elapsed with {n} trade(s) -- NOT a judgment point: nothing is judged "
                  f"on fewer than {JUDGE_TRADES} trades (Amendment 1). It keeps trading.")
    return {
        "trades": n, "first_session": first_session, "days_elapsed": days, "slow": bool(slow),
        "trades_to_judgment": max(0, JUDGE_TRADES - n), "weeks_to_judgment": weeks_left if weeks_left is None else round(weeks_left, 1),
        "six_week_mark_passed": six_week_mark,
        "at_judgment_point": at_point, "judgment_reason": reason,
        "win_rate": None if win_rate is None else round(win_rate, 3),
        "avg_r": None if avg_r is None else round(avg_r, 4), "total_r": round(total_r, 3),
        "usd_net": {str(k): round(usd_1 * k, 2) for k in SIZES},
        "usd_gross_1": round(sum(t["usd_gross_1"] for t in trades), 2),
        "assumed_costs_usd_1": round(ASSUMED_COST_USD_PER_MICRO_RT * n, 2),
        "worst_losing_streak": streak, "survivable_daily_limit": survivable,
        "slippage": SLIPPAGE_BASIS, "cost_fragile": (avg_r is not None and avg_r < COST_FRAGILE_AVG_R),
        "avg_winner_usd_1": None if avg_winner_usd is None else round(avg_winner_usd, 2),
    }


def _first_session(rows: list[dict], name: str) -> str | None:
    ds = sorted(r.get("date") for r in rows if log_name(r) == name and r.get("date"))
    return ds[0] if ds else None


def book(log_rows: list[dict] | None = None, registry_rows: list[dict] | None = None,
         today: date | None = None) -> dict:
    """The whole paper book: candidates (from the registry, stage PAPER and
    beyond) with their measured record, and plumbing records listed separately."""
    log_rows = load_log() if log_rows is None else log_rows
    registry_rows = read_registry() if registry_rows is None else registry_rows
    names_in_log = {log_name(r) for r in log_rows}
    slow = registry_slow_ids(registry_rows)
    strategies = []
    for reg in registry_in_paper(registry_rows):
        name = reg.get("paper_log_name") or ""
        is_slow = reg.get("strategy_id") in slow
        tr = trades_for(log_rows, name) if name else []
        sessions = sorted({r.get("date") for r in log_rows if log_name(r) == name and r.get("date")})
        m = measure(tr, _first_session(log_rows, name) if name else None, today, slow=is_slow)
        entered = reg.get("ts", "")[:10]
        if m["days_elapsed"] is None and entered:
            try:
                m["days_elapsed"] = ((today or date.today()) - datetime.strptime(entered, "%Y-%m-%d").date()).days
                m["six_week_mark_passed"] = bool(m["days_elapsed"] >= JUDGE_WEEKS * 7)
                if not is_slow:
                    m["weeks_to_judgment"] = round(max(0.0, JUDGE_WEEKS - m["days_elapsed"] / 7.0), 1)
                # Amendment 1: elapsed time never makes a strategy judgeable.
            except ValueError:
                pass
        strategies.append({"strategy_id": reg.get("strategy_id"), "name": reg.get("name"), "stage": reg.get("stage"),
                           "slow_projection": reg.get("slow_projection"),
                           "paper_log_name": name, "sessions_scored": len(sessions), "entered_paper": entered,
                           "salvage": reg.get("verdict") if reg.get("stage") == "SALVAGE" else None, **m})
    plumbing = []
    for name in sorted(names_in_log):
        if name in PLUMBING_LOG_NAMES:
            tr = trades_for(log_rows, name)
            m = measure(tr, _first_session(log_rows, name), today)
            plumbing.append({"paper_log_name": name, "trades": m["trades"], "usd_gross_1": m["usd_gross_1"],
                             "sessions_logged": len({r.get("date") for r in log_rows if log_name(r) == name}),
                             "label": "PLUMBING TEST -- no claimed edge, never judged"})
    return {"strategies": strategies, "plumbing": plumbing,
            "slow_rule": {"horizon_sessions": SLOW_HORIZON_SESSIONS, "min_trades": SLOW_MIN_TRADES,
                          "note": ("Amendment 1 (Jason, September 16th 2026): trades/sessions * 126 < 40 at the SCREEN "
                                   "-> SLOW: background paper, no queue slot, judged whenever it reaches 40 trades. "
                                   "Nothing is ever judged on fewer than 40 trades.")},
            "cost_basis": {"slippage": SLIPPAGE_BASIS, "usd_per_micro_round_trip": ASSUMED_COST_USD_PER_MICRO_RT,
                           "points_per_round_trip": ASSUMED_COST_PTS_RT,
                           "note": f"commission ${COMMISSION_PER_SIDE_USD:.2f}/side + {SLIPPAGE_TICKS_PER_SIDE:g} tick/side, ASSUMED until B4b measures it"}}


def _fmt_usd(x: float) -> str:
    return f"{'-' if x < 0 else '+'}${abs(x):,.0f}"


def plain_lines(bk: dict) -> list[str]:
    """Plain-language lines for the session report / preflight."""
    lines = []
    if not bk["strategies"]:
        lines.append("- No strategy is in paper yet. The paper book is empty -- the first candidate through SCREEN enters it.")
    for s in bk["strategies"]:
        head = f"- **{s['strategy_id']} {s['name']}** -- stage {s['stage']}" + (" **[SLOW]**" if s.get("slow") else "")
        if s["trades"] == 0:
            days = s.get("days_elapsed")
            if s.get("slow"):
                lines.append(head + f": in paper {days if days is not None else '?'} day(s), **0 trades scored yet** "
                                    f"({s['sessions_scored']} session(s) checked). SLOW -- background paper, no queue slot, "
                                    f"no clock; judged whenever it reaches {JUDGE_TRADES} trades.")
            else:
                lines.append(head + f": in paper {days if days is not None else '?'} day(s), **0 trades scored yet** "
                                    f"({s['sessions_scored']} session(s) checked). Judgment at {JUDGE_TRADES} trades"
                                    + (f" (six-week mark in {s['weeks_to_judgment']} week(s); reaching it under {JUDGE_TRADES} trades is not a verdict)."
                                       if s.get('weeks_to_judgment') is not None else "."))
            continue
        wr = f"{s['win_rate']*100:.0f}%" if s["win_rate"] is not None else "n/a"
        avg = f"{s['avg_r']:+.2f}R" if s["avg_r"] is not None else "n/a"
        if s.get("slow"):
            to_judgment = (f"SLOW -- background paper, no queue slot, no clock; {s['trades_to_judgment']} more trade(s) "
                           f"to its {JUDGE_TRADES}-trade judgment point")
        else:
            to_judgment = f"{s['trades_to_judgment']} trades to judgment (six-week mark in {s['weeks_to_judgment']} week(s))"
        lines.append(head + f": **{s['trades']} trades** over {s['days_elapsed']} days; " + to_judgment
                            + (" -- **AT JUDGMENT POINT: " + s["judgment_reason"] + "**" if s["at_judgment_point"] else "")
                            + (" -- six-week mark passed under 40 trades: NOT a verdict, it keeps trading"
                               if (not s.get("slow") and s.get("six_week_mark_passed") and not s["at_judgment_point"]) else "") + ".")
        lines.append(f"  - Win rate {wr}; average result {avg} per trade after ASSUMED costs (R = the amount risked on one trade); total {s['total_r']:+.1f}R.")
        u = s["usd_net"]
        lines.append(f"  - Result at 1 / 5 / 10 micros: **{_fmt_usd(u['1'])} / {_fmt_usd(u['5'])} / {_fmt_usd(u['10'])}** "
                     f"(gross {_fmt_usd(s['usd_gross_1'])} at 1 micro, minus ${s['assumed_costs_usd_1']:,.0f} assumed costs).")
        st = s["worst_losing_streak"]; sv = s["survivable_daily_limit"]
        if sv:
            lines.append(f"  - Worst losing streak: {st['trades']} trade(s), {_fmt_usd(st['usd_1'])} at 1 micro. "
                         f"A daily loss limit of three average winners = ${sv['daily_limit_usd_1']:,.0f}: the streak "
                         f"{'stayed inside it' if sv['worst_streak_inside_limit'] else 'would have BLOWN THROUGH it'}.")
        else:
            lines.append(f"  - Worst losing streak: {st['trades']} trade(s), {_fmt_usd(st['usd_1'])} at 1 micro. No winner yet, so no survivable daily limit can be stated.")
        lines.append(f"  - Slippage: **{s['slippage']}** (simulated fills, 1 tick/side + $2.50/side commission)"
                     + ("; **COST-FRAGILE** (average R under 0.10 on assumed costs)." if s["cost_fragile"] else "."))
        if s.get("salvage"):
            lines.append(f"  - Salvage check: {s['salvage']}")
    for p in bk["plumbing"]:
        lines.append(f"- Plumbing (not a candidate, never judged): {p['paper_log_name']} -- {p['trades']} fill(s) bookkept "
                     f"across {p['sessions_logged']} session(s), gross {_fmt_usd(p['usd_gross_1'])} at 1 micro. Order-path test only.")
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    bk = book()
    if a.json:
        print(json.dumps(bk, indent=1, default=str))
    else:
        print("PAPER BOOK (net of ASSUMED costs: $%.2f per micro round trip)" % ASSUMED_COST_USD_PER_MICRO_RT)
        for ln in plain_lines(bk):
            print(ln)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
