"""
screen_strategy.py -- the SCREEN stage (standing directive s.2): one pass of a
frozen strategy over the Discovery slice, one question -- did it make money
after ASSUMED costs? -- one number. No confidence-interval gate, no multiplicity
correction, no holdout. Net > 0 -> the strategy enters PAPER; net <= 0 -> Salvage.

SAME BOOKKEEPING AS THE PAPER LOOP, ON PURPOSE. Each session's signals come from
the module's own generate_signals(day_df, history=...) exactly as
bot_stack_paper_run.py calls it; the first signal of a session is the trade
(one trade a session); the fill is at the signal's entry price (the paper loop
fills at signal.entry too -- choice 5 in its header); the exit is
bot_stack_paper_run._resolve_fill_outcome -- first touch wins, stop wins a
same-bar tie, time exit from the signal's market_context, session-end fallback.
So a screen number and a paper number for the same strategy cannot drift apart
by construction. What the screen does NOT include: the simulated broker's
hostile rejections/partials (plumbing noise, not the strategy) and the B7 loop's
Risk/State Engine session gate (a paper-engine property, disclosed in every spec).

COSTS: src/paper_book.py's ASSUMED micro round trip ($2.50/side commission +
1 tick/side slippage = $6.00 = 3.0 pts on MNQ), labelled ASSUMED.

EXPOSURE (for information only, never a gate): the number of SCREEN rows in
research/ledger/strategies.jsonl so far is printed with every result.

USAGE
    python3 src/screen_strategy.py strategy_s001_level_sweep_reversal [--out data/screen_S001.json]
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import bot_stack_paper_run as bpr  # noqa: E402
from paper_book import ASSUMED_COST_USD_PER_MICRO_RT, MNQ_USD_PER_PT, SLIPPAGE_BASIS  # noqa: E402

PROJECT_ROOT = ROOT.parent


def screen(module, df: pd.DataFrame, slice_label: str = "discovery") -> dict:
    """Run `module` over every session in `df` with the paper loop's bookkeeping.
    Returns the one number (net_usd_1_micro) plus the per-trade list."""
    if hasattr(module, "precompute"):
        module.precompute(df)
    gen = module.generate_signals
    trades = []
    n_sessions = 0
    n_unresolved = 0        # cross-session trades whose exit falls past the slice
    for day, day_df in df.groupby(df.index.date):
        n_sessions += 1
        sigs = bpr._signals(gen, day_df, df)
        if not sigs:
            continue
        sig = sigs[0]                       # one trade a session, the paper loop's rule
        time_exit = (getattr(sig, "market_context", {}) or {}).get("time_exit") or bpr.SESSION_COMPLETE_BY
        # CROSS-SESSION (choice 7 in the paper loop): a strategy holding past its
        # entry session declares an absolute market_context["exit_ts"] and is
        # walked across the boundary on the WHOLE frame, identically to paper.
        # Same-session strategies pass scan_df=None/exit_ts=None -- unchanged.
        x_exit = bpr.cross_session_exit_ts(sig)
        out = bpr._resolve_fill_outcome(day_df, sig.direction, sig.timestamp, float(sig.entry),
                                        float(sig.stop), float(sig.target), time_exit,
                                        scan_df=(df if x_exit is not None else None),
                                        exit_ts=x_exit)
        if out is None:
            # the exit falls past the end of this slice: the trade is OPEN and is
            # not counted. Never force-closed, never fabricated.
            n_unresolved += 1
            continue
        risk = out["risk_points"]
        r_gross = out["r_multiple"] if out["r_multiple"] is not None else 0.0
        gross_usd = r_gross * risk * MNQ_USD_PER_PT
        net_usd = gross_usd - ASSUMED_COST_USD_PER_MICRO_RT
        r_net = net_usd / (risk * MNQ_USD_PER_PT) if risk > 0 else 0.0
        trades.append({"date": str(day), "direction": sig.direction, "entry": float(sig.entry), "stop": float(sig.stop),
                       "target": float(sig.target), "risk_points": risk, "exit_reason": out["exit_reason"],
                       "exit_time": out["exit_time"], "r_gross": r_gross, "r_net": round(r_net, 4),
                       "usd_gross_1": round(gross_usd, 2), "usd_net_1": round(net_usd, 2),
                       "context": {k: v for k, v in (getattr(sig, "market_context", {}) or {}).items()
                                   if isinstance(v, (str, int, float, bool))}})
    n = len(trades)
    wins = sum(1 for t in trades if t["usd_net_1"] > 0)
    net = round(sum(t["usd_net_1"] for t in trades), 2)
    gross = round(sum(t["usd_gross_1"] for t in trades), 2)
    avg_r = round(sum(t["r_net"] for t in trades) / n, 4) if n else None
    return {
        "strategy_name": module.STRATEGY_NAME, "strategy_version": getattr(module, "STRATEGY_VERSION", ""),
        "slice": slice_label, "sessions": n_sessions, "trades": n,
        "open_unresolved_trades_excluded": n_unresolved,
        "net_usd_1_micro": net, "net_usd_5_micro": round(net * 5, 2), "net_usd_10_micro": round(net * 10, 2),
        "gross_usd_1_micro": gross, "assumed_costs_usd_1": round(ASSUMED_COST_USD_PER_MICRO_RT * n, 2),
        "win_rate": round(wins / n, 4) if n else None, "avg_r_net": avg_r,
        "total_r_net": round(sum(t["r_net"] for t in trades), 3),
        "made_money_after_assumed_costs": bool(n and net > 0),
        "cost_basis": f"{SLIPPAGE_BASIS}: ${ASSUMED_COST_USD_PER_MICRO_RT:.2f} per micro round trip (commission $2.50/side + 1 tick/side)",
        "bookkeeping": "bot_stack_paper_run._resolve_fill_outcome (first touch, stop wins ties, time exit, session-end fallback; cross-session exits walk the whole frame to market_context['exit_ts'] and an unresolvable one is excluded, never force-closed); fill at signal.entry",
        "trades_detail": trades,
    }


def exposure_count() -> int:
    try:
        import strategy_registry as sr
        return sum(1 for r in sr.read_rows() if r.get("stage") == "SCREEN")
    except Exception:  # noqa: BLE001
        return -1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("module", help="strategy module name in src/, e.g. strategy_s001_level_sweep_reversal")
    ap.add_argument("--out", default=None, help="write the full result (with per-trade detail) here")
    a = ap.parse_args(argv)
    module = importlib.import_module(a.module)
    from data_loader import load_price_data
    from data_split import get_discovery_data
    df, synthetic = load_price_data(context="screen_strategy", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data -- refusing to screen")
    disc = get_discovery_data(df)
    res = screen(module, disc, "discovery")
    res["exposure_screens_so_far_for_information"] = exposure_count()
    print("=" * 78)
    print(f"SCREEN  {res['strategy_name']}  ({res['strategy_version']})  slice={res['slice']}")
    print("=" * 78)
    print(f"  sessions scanned : {res['sessions']}")
    print(f"  trades           : {res['trades']}")
    print(f"  NET after ASSUMED costs, 1 micro : ${res['net_usd_1_micro']:,.2f}   (5: ${res['net_usd_5_micro']:,.2f}  10: ${res['net_usd_10_micro']:,.2f})")
    print(f"  gross ${res['gross_usd_1_micro']:,.2f}  minus assumed costs ${res['assumed_costs_usd_1']:,.2f}  [{res['cost_basis']}]")
    print(f"  win rate {res['win_rate']}   avg R (net) {res['avg_r_net']}   total R (net) {res['total_r_net']}")
    print(f"  MADE MONEY AFTER ASSUMED COSTS: {res['made_money_after_assumed_costs']}  -> {'PAPER' if res['made_money_after_assumed_costs'] else 'SALVAGE'}")
    print(f"  exposure (screens run so far, information only): {res['exposure_screens_so_far_for_information']}")
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, default=str))
        print(f"  detail -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
