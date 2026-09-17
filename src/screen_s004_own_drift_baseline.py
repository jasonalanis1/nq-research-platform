"""
screen_s004_own_drift_baseline.py -- THE BASELINE GATE for S004 (spec s.5).

THE CORRECTION THAT KILLED H118, TURNED INTO A DECISION RULE
  H118 passed Discovery, Validation and Holdout and was rejected on 2026-09-12
  because its LOW-tercile 10-day drift was not distinguishable from NQ's OWN
  unconditional 10-day drift. It made money because the index went up. The
  two-nulls rule (research/KNOWLEDGE.md): the correct null for a DIRECTIONAL
  claim is the instrument's own unconditional drift over the same holding
  period, never zero.

WHAT THIS SCRIPT DOES
  Runs src/screen_strategy.screen() TWICE over the SAME Discovery slice with the
  SAME module, the SAME entry clock, the SAME ten-session hold, the SAME
  4.0 x atr14 stop, the SAME sentinel target, the SAME _resolve_fill_outcome
  bookkeeping and the SAME four-way cost overlay:

    arm A  the strategy            -- LOW-tercile filter ON
    arm B  the own-drift baseline  -- the identical trade on EVERY session,
                                      tercile filter OFF, nothing else changed
                                      (module.UNCONDITIONAL_BASELINE = True)

  Arm B is NOT a strategy and is never registered, never papered, never judged.
  It is the null.

THE GATE
  S004 passes SCREEN only if BOTH hold on the MNQ-market decision basis:
    1. arm A net_usd_1_micro > 0                       (the directive's SCREEN question)
    2. arm A net points/trade - arm B net points/trade > 0    (the baseline margin)
  A positive net with a non-positive margin is a FAIL and goes to Salvage, with
  H118's epitaph repeated in the ledger row.

USAGE
    python3 src/screen_s004_own_drift_baseline.py [--out data/screen_S004.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import cost_model  # noqa: E402
import screen_strategy  # noqa: E402
import bot_stack_paper_run as bpr_module  # noqa: E402
import strategy_s004_vwap_dist_low_drift as s004  # noqa: E402

PROJECT_ROOT = ROOT.parent


def _per_trade_points(res: dict) -> float:
    n = res["trades"]
    return (res["gross_usd_1_micro"] / 2.0 / n) if n else 0.0     # MNQ $2.00/pt


# --- a PURE SPEED FIX, VERIFIED, not a change of bookkeeping -----------------
# screen_strategy.screen() hands _resolve_fill_outcome the WHOLE Discovery frame
# (2.2M bars) as `scan_df` for every cross-session trade, and that function walks
# it bar by bar with .iterrows(). A ten-session hold is ~14,000 bars, and the two
# arms together take ~2,200 trades: ~30 million Python-level row objects, hours of
# work for a screen whose arithmetic is trivial.
#
# `_resolve_vectorized` below is the SAME DECISION RULE expressed in numpy, on the
# same trimmed window: bars strictly after the entry, in order; within a bar the
# STOP is tested first, then the TARGET, then the exit timestamp -- so a stop wins
# a same-bar tie exactly as in the original, and a bar that is both the exit bar
# and a stop bar is a stop. A time exit is booked at that bar's OPEN. If no bar
# resolves the trade the result is None -- OPEN, excluded, never force-closed.
#
# It is not trusted on that argument alone. `--verify N` re-resolves N randomly
# chosen trades of each arm with the ORIGINAL bot_stack_paper_run function on the
# untrimmed frame and asserts the two agree field for field; the screen refuses to
# report numbers if they ever disagree.
_ORIG_RESOLVE = bpr_module._resolve_fill_outcome


def _resolve_vectorized(day_df, direction, from_ts, entry_price, stop, target, time_exit,
                        scan_df=None, exit_ts=None):
    if scan_df is None or exit_ts is None:
        return _ORIG_RESOLVE(day_df, direction, from_ts, entry_price, stop, target,
                             time_exit, scan_df=scan_df, exit_ts=exit_ts)
    import numpy as _np
    import pandas as _pd
    idx = scan_df.index
    lo_i = int(_np.searchsorted(idx.values, _pd.Timestamp(from_ts).to_datetime64(), side="right"))
    frame = scan_df.iloc[lo_i:]
    if frame.empty:
        return None
    low = frame["Low"].to_numpy(dtype=float)
    high = frame["High"].to_numpy(dtype=float)
    opn = frame["Open"].to_numpy(dtype=float)
    fidx = frame.index

    def _first(mask):
        w = _np.flatnonzero(mask)
        return int(w[0]) if w.size else None

    if direction == "long":
        i_stop, i_target = _first(low <= stop), _first(high >= target)
    else:
        i_stop, i_target = _first(high >= stop), _first(low <= target)
    i_exit = int(_np.searchsorted(fidx.values, _pd.Timestamp(exit_ts).to_datetime64(), side="left"))
    i_exit = i_exit if i_exit < len(fidx) else None

    # order of the candidates IS the original loop's within-bar test order
    cands = [(i_stop, "stop"), (i_target, "target"), (i_exit, "time_exit")]
    cands = [(i, w) for i, w in cands if i is not None]
    if not cands:
        return None
    best = min(i for i, _ in cands)
    reason = next(w for i, w in cands if i == best)
    exit_price = {"stop": stop, "target": target}.get(reason, float(opn[best]))
    hit_ts = fidx[best]

    risk = abs(entry_price - stop)
    move = (exit_price - entry_price) if direction == "long" else (entry_price - exit_price)
    r_multiple = round(move / risk, 4) if risk else None
    return {"exit_price": round(exit_price, 4), "exit_reason": reason, "exit_time": str(hit_ts),
            "risk_points": round(risk, 4), "r_multiple": r_multiple}


def _verify_against_original(res: dict, df, n: int, label: str) -> dict:
    """Re-resolve `n` randomly chosen trades of `res` with the ORIGINAL
    bot_stack_paper_run walk on the UNTRIMMED frame and assert agreement."""
    import random
    import pandas as _pd
    trades = res["trades_detail"]
    if not trades:
        return {"arm": label, "checked": 0, "disagreements": 0}
    rng = random.Random(4)
    sample = rng.sample(trades, min(n, len(trades)))
    bad = []
    for t in sample:
        day = _pd.Timestamp(t["date"]).date()
        day_df = df[df.index.date == day]
        ctx = t["context"]
        entry_ts = day_df.between_time("09:30", "09:30").index[0]
        orig = _ORIG_RESOLVE(day_df, t["direction"], entry_ts, t["entry"], t["stop"],
                             t["target"], "15:55", scan_df=df, exit_ts=ctx["exit_ts"])
        if orig is None:
            bad.append((t["date"], "original returned None"))
            continue
        if (orig["exit_reason"] != t["exit_reason"] or orig["exit_time"] != t["exit_time"]
                or abs(orig["r_multiple"] - t["r_gross"]) > 1e-9
                or abs(orig["risk_points"] - t["risk_points"]) > 1e-9):
            bad.append((t["date"], orig, t))
    return {"arm": label, "checked": len(sample), "disagreements": len(bad), "detail": bad[:5]}


def _run_arm(df, baseline: bool) -> dict:
    s004.UNCONDITIONAL_BASELINE = baseline
    s004._PRE.clear()                     # force a rebuild so no state leaks between arms
    bpr_module._resolve_fill_outcome = _resolve_vectorized
    try:
        return screen_strategy.screen(s004, df, "discovery")
    finally:
        bpr_module._resolve_fill_outcome = _ORIG_RESOLVE
        s004.UNCONDITIONAL_BASELINE = False
        s004._PRE.clear()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--verify", type=int, default=40,
                    help="re-resolve this many trades per arm with the ORIGINAL walk and assert agreement")
    a = ap.parse_args(argv)

    from data_loader import load_price_data
    from data_split import get_discovery_data
    df, synthetic = load_price_data(context="screen_s004_own_drift_baseline", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data -- refusing to screen")
    disc = get_discovery_data(df)

    strat = _run_arm(disc, baseline=False)
    base = _run_arm(disc, baseline=True)

    checks = [_verify_against_original(strat, disc, a.verify, "A strategy"),
              _verify_against_original(base, disc, a.verify, "B own-drift baseline")]
    for c in checks:
        print(f"  VERIFY  arm {c['arm']}: {c['checked']} trades re-resolved with the ORIGINAL "
              f"bot_stack_paper_run walk on the untrimmed frame -- {c['disagreements']} disagreement(s)")
        if c["disagreements"]:
            print("    " + str(c["detail"]))
            raise SystemExit("VECTORIZED RESOLVER DISAGREES WITH THE ORIGINAL -- refusing to report numbers")

    a_pt = _per_trade_points(strat)
    b_pt = _per_trade_points(base)
    margin_pt = a_pt - b_pt
    a_r = strat["avg_r_net"] or 0.0
    b_r = base["avg_r_net"] or 0.0

    made_money = bool(strat["made_money_after_assumed_costs"])
    beats_baseline = bool(margin_pt > 0)
    verdict = "PAPER" if (made_money and beats_baseline) else "SALVAGE"

    print("=" * 78)
    print(f"SCREEN  {strat['strategy_name']}  ({strat['strategy_version']})  slice=discovery")
    print("        WITH THE OWN-DRIFT BASELINE GATE (spec s.5) -- the H118 correction")
    print("=" * 78)
    for label, res in (("ARM A  strategy (LOW tercile)", strat),
                       ("ARM B  own-drift baseline (every session, filter OFF)", base)):
        print(f"\n  {label}")
        print(f"    sessions {res['sessions']}   trades {res['trades']}   "
              f"open/unresolved excluded {res['open_unresolved_trades_excluded']}")
        print(f"    NET after ASSUMED costs, 1 micro: ${res['net_usd_1_micro']:,.2f}   "
              f"gross ${res['gross_usd_1_micro']:,.2f}   costs ${res['assumed_costs_usd_1']:,.2f}")
        print(f"    win rate {res['win_rate']}   avg R (net) {res['avg_r_net']}   "
              f"gross pt/trade {_per_trade_points(res):+.4f}")
        print(f"    {'combination':<30}{'net $':>12}{'net R':>10}{'avg R':>9}"
              f"{'gross pt/tr':>13}{'cost pt/tr':>12}{'net pt/tr':>11}")
        for row in res["cost_combinations"]["combinations"]:
            print(f"    {row['label']:<30}{row['net_usd_total']:>12,.2f}{row['total_r_net']:>10.1f}"
                  f"{row['avg_r_net']:>9.4f}{row['gross_points_per_trade']:>13.4f}"
                  f"{row['cost_points_per_trade']:>12.3f}{row['net_points_per_trade']:>11.4f}"
                  f"   {'MAKES MONEY' if row['made_money'] else 'loses'}")
    print(f"\n    LIMIT ROWS ARE OPTIMISTIC: {cost_model.OPTIMISTIC_NOTE}")

    print("\n  " + "-" * 74)
    print("  THE BASELINE GATE (spec s.5) -- the correction that killed H118")
    print(f"    (1) made money after ASSUMED costs, MNQ market : {made_money}  "
          f"(net ${strat['net_usd_1_micro']:,.2f})")
    print(f"    (2) beats NQ's OWN drift over the same 10-session hold:")
    print(f"        strategy {a_pt:+.4f} gross pt/trade  -  baseline {b_pt:+.4f} gross pt/trade"
          f"  =  MARGIN {margin_pt:+.4f} pt/trade  -> {beats_baseline}")
    print(f"        avg R net: strategy {a_r:+.4f}  -  baseline {b_r:+.4f}  =  {a_r - b_r:+.4f} R/trade")
    print(f"    VERDICT: {verdict}")
    if made_money and not beats_baseline:
        print("    -> Positive against ZERO, not against the index. This is exactly what H118 was:")
        print("       the stock market going up. It is a FAIL, not a pass.")
    sp = strat["slow_projection"]
    print(f"    rate {sp['trades_per_session']:.4f} trades/session -> {sp['projected_trades_6_months']:.1f} "
          f"trades in 6 months (~{sp['horizon_sessions']} sessions): "
          f"{'SLOW -- background paper, no queue slot, judged at 40 trades' if sp['slow'] else 'not SLOW, ordinary six-week clock'} (Amendment 1)")

    out = {"strategy": strat, "own_drift_baseline": base, "resolver_verification": checks,
           "gate": {"made_money_after_assumed_costs": made_money,
                    "strategy_gross_points_per_trade": a_pt,
                    "baseline_gross_points_per_trade": b_pt,
                    "margin_points_per_trade": margin_pt,
                    "strategy_avg_r_net": a_r, "baseline_avg_r_net": b_r,
                    "margin_avg_r": a_r - b_r,
                    "beats_own_drift_baseline": beats_baseline,
                    "verdict": verdict,
                    "rule": ("S004 spec s.5 / research/KNOWLEDGE.md two-nulls rule: a directional claim is "
                             "measured against the instrument's own unconditional drift over the same holding "
                             "period, never against zero. Both conditions must hold.")}}
    path = Path(a.out) if a.out else (PROJECT_ROOT / "data" / "screen_S004_with_baseline.json")
    path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\n  written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
