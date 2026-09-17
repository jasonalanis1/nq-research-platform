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
import strategy_s004_vwap_dist_low_drift as s004  # noqa: E402

PROJECT_ROOT = ROOT.parent


def _per_trade_points(res: dict) -> float:
    n = res["trades"]
    return (res["gross_usd_1_micro"] / 2.0 / n) if n else 0.0     # MNQ $2.00/pt


def _run_arm(df, baseline: bool) -> dict:
    s004.UNCONDITIONAL_BASELINE = baseline
    s004._PRE.clear()                     # force a rebuild so no state leaks between arms
    try:
        return screen_strategy.screen(s004, df, "discovery")
    finally:
        s004.UNCONDITIONAL_BASELINE = False
        s004._PRE.clear()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    from data_loader import load_price_data
    from data_split import get_discovery_data
    df, synthetic = load_price_data(context="screen_s004_own_drift_baseline", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data -- refusing to screen")
    disc = get_discovery_data(df)

    strat = _run_arm(disc, baseline=False)
    base = _run_arm(disc, baseline=True)

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

    out = {"strategy": strat, "own_drift_baseline": base,
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
