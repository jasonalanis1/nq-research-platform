"""
screen_s011_own_drift_baseline.py -- THE BASELINE GATE for S011 (spec s.6).

THE TWO-NULLS RULE, AS A DECISION RULE
  research/KNOWLEDGE.md: the correct null for a DIRECTIONAL claim is the
  instrument's own unconditional drift over the same holding period, never zero.
  It killed H118 (2026-09-12) and it is why S004 was rebuilt. S011 is a fade, so
  its null is the identical trade taken LONG on the identical sessions.

WHAT THIS SCRIPT DOES
  Runs src/screen_strategy.screen() TWICE over the SAME Discovery slice with the
  SAME module, the SAME 09:30 entry, the SAME 2.0 x atr14 stop, the SAME sentinel
  target, the SAME 15:55 exit, the SAME _resolve_fill_outcome bookkeeping and the
  SAME four-way cost overlay:

    arm A  the strategy            -- direction = FADE sign(M(prior session))
    arm B  the own-drift baseline  -- direction forced LONG, nothing else changed
                                      (module.BASELINE_ALWAYS_LONG = True)

  Arm B is NOT a strategy and is never registered, never papered, never judged.

THE GATE (spec s.6, pre-registered BEFORE the screen ran)
  S011 passes SCREEN only if BOTH hold on the MNQ-market decision basis:
    1. arm A net_usd_1_micro > 0
    2. arm A net points/trade - arm B net points/trade > 0
  Stated as the pre-freeze falsifier, in screen units: S011 FAILS if arm A's
  MNQ-market net is <= $0.00, or if the margin over arm B is <= 0.0000 net
  points per trade.

EFFECTIVE SAMPLE (spec s.8, the S004 lesson): the holding windows are checked
mechanically for overlap instead of the trade count being assumed to be the
sample size.

USAGE
    python3 src/screen_s011_own_drift_baseline.py [--out data/screen_S011_with_baseline.json]
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
import strategy_s011_daily_reversal_vs_own_drift as s011  # noqa: E402

PROJECT_ROOT = ROOT.parent


def _net_points_per_trade(res: dict) -> float:
    """MNQ-market net points per trade, straight off the four-way overlay."""
    for row in res["cost_combinations"]["combinations"]:
        if row["label"].startswith("MNQ market"):
            return float(row["net_points_per_trade"])
    raise SystemExit("MNQ market row missing from the cost overlay")


def _gross_points_per_trade(res: dict) -> float:
    n = res["trades"]
    return (res["gross_usd_1_micro"] / 2.0 / n) if n else 0.0     # MNQ $2.00/pt


def _overlap_check(res: dict) -> dict:
    """S011 holds 09:30 -> 15:55 of ONE session: distinct dates and zero shared
    bars between holds. Verified, not assumed (spec s.8)."""
    dates = [t["date"] for t in res["trades_detail"]]
    dup = len(dates) - len(set(dates))
    cross = sum(1 for t in res["trades_detail"]
                if str(t["exit_time"])[:10] != str(t["date"])[:10])
    n = len(dates)
    return {"trades": n, "distinct_sessions": len(set(dates)), "duplicate_sessions": dup,
            "holds_crossing_their_own_session": cross,
            "overlapping_holding_windows": 0 if (dup == 0 and cross == 0) else None,
            "effective_sample": n if (dup == 0 and cross == 0) else None,
            "note": ("one trade per session, entry 09:30 and exit by 15:55 of the SAME session, so no two "
                     "holding windows share a bar and the effective sample equals the trade count. The one "
                     "real dependence left is that trade t's SIGNAL is the session trade t-1 was entered in "
                     "-- a one-lag chain in the signal, not in the outcome. Reported, not hidden.")}


def _run_arm(df, baseline: bool) -> dict:
    s011.BASELINE_ALWAYS_LONG = baseline
    s011._PRE.clear()                     # force a rebuild so no state leaks between arms
    try:
        return screen_strategy.screen(s011, df, "discovery")
    finally:
        s011.BASELINE_ALWAYS_LONG = False
        s011._PRE.clear()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    from data_loader import load_price_data
    from data_split import get_discovery_data
    df, synthetic = load_price_data(context="screen_s011_own_drift_baseline", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data -- refusing to screen")
    disc = get_discovery_data(df)

    strat = _run_arm(disc, baseline=False)
    base = _run_arm(disc, baseline=True)

    a_pt, b_pt = _net_points_per_trade(strat), _net_points_per_trade(base)
    margin_pt = a_pt - b_pt
    a_r = strat["avg_r_net"] or 0.0
    b_r = base["avg_r_net"] or 0.0
    made_money = bool(strat["made_money_after_assumed_costs"])
    beats_baseline = bool(margin_pt > 0)
    verdict = "PAPER" if (made_money and beats_baseline) else "SALVAGE"
    overlap = _overlap_check(strat)

    print("=" * 78)
    print(f"SCREEN  {strat['strategy_name']}  ({strat['strategy_version']})  slice=discovery")
    print("        WITH THE OWN-DRIFT BASELINE GATE (spec s.6) -- the two-nulls rule")
    print("=" * 78)
    for label, res in (("ARM A  strategy (FADE the prior session)", strat),
                       ("ARM B  own-drift baseline (same sessions, forced LONG)", base)):
        print(f"\n  {label}")
        print(f"    sessions {res['sessions']}   trades {res['trades']}   "
              f"open/unresolved excluded {res['open_unresolved_trades_excluded']}")
        print(f"    NET after ASSUMED costs, 1 micro: ${res['net_usd_1_micro']:,.2f}   "
              f"gross ${res['gross_usd_1_micro']:,.2f}   costs ${res['assumed_costs_usd_1']:,.2f}")
        print(f"    win rate {res['win_rate']}   avg R (net) {res['avg_r_net']}   "
              f"gross pt/trade {_gross_points_per_trade(res):+.4f}")
        print(f"    {'combination':<30}{'net $':>12}{'net R':>10}{'avg R':>9}"
              f"{'gross pt/tr':>13}{'cost pt/tr':>12}{'net pt/tr':>11}")
        for row in res["cost_combinations"]["combinations"]:
            print(f"    {row['label']:<30}{row['net_usd_total']:>12,.2f}{row['total_r_net']:>10.1f}"
                  f"{row['avg_r_net']:>9.4f}{row['gross_points_per_trade']:>13.4f}"
                  f"{row['cost_points_per_trade']:>12.3f}{row['net_points_per_trade']:>11.4f}"
                  f"   {'MAKES MONEY' if row['made_money'] else 'loses'}")
    print(f"\n    LIMIT ROWS ARE OPTIMISTIC: {cost_model.OPTIMISTIC_NOTE}")

    print("\n  " + "-" * 74)
    print("  THE BASELINE GATE (spec s.6) -- pre-registered before this screen ran")
    print(f"    (1) made money after ASSUMED costs, MNQ market : {made_money}  "
          f"(net ${strat['net_usd_1_micro']:,.2f})")
    print("    (2) beats NQ's OWN next-session drift over the identical window:")
    print(f"        strategy {a_pt:+.4f} net pt/trade  -  baseline {b_pt:+.4f} net pt/trade"
          f"  =  MARGIN {margin_pt:+.4f} pt/trade  -> {beats_baseline}")
    print(f"        avg R net: strategy {a_r:+.4f}  -  baseline {b_r:+.4f}  =  {a_r - b_r:+.4f} R/trade")
    print(f"    VERDICT: {verdict}")
    if made_money and not beats_baseline:
        print("    -> Positive against ZERO, not against the index. That is what H118 was.")
    print(f"\n  EFFECTIVE SAMPLE (spec s.8): trades {overlap['trades']}, distinct sessions "
          f"{overlap['distinct_sessions']}, duplicate sessions {overlap['duplicate_sessions']}, "
          f"holds crossing their own session {overlap['holds_crossing_their_own_session']} "
          f"-> effective sample {overlap['effective_sample']}")
    sp = strat["slow_projection"]
    print(f"\n  rate {sp['trades_per_session']:.4f} trades/session -> {sp['projected_trades_6_months']:.1f} "
          f"trades in 6 months (~{sp['horizon_sessions']} sessions): "
          f"{'SLOW -- background paper, no queue slot, judged at 40 trades' if sp['slow'] else 'NOT SLOW, ordinary six-week clock'} (Amendment 1)")

    out = {"strategy": strat, "own_drift_baseline": base, "effective_sample": overlap,
           "gate": {"made_money_after_assumed_costs": made_money,
                    "strategy_net_points_per_trade": a_pt,
                    "baseline_net_points_per_trade": b_pt,
                    "margin_points_per_trade": margin_pt,
                    "strategy_avg_r_net": a_r, "baseline_avg_r_net": b_r,
                    "margin_avg_r": a_r - b_r,
                    "beats_own_drift_baseline": beats_baseline,
                    "verdict": verdict,
                    "rule": ("S011 spec s.6 / research/KNOWLEDGE.md two-nulls rule: a directional claim is "
                             "measured against the instrument's own unconditional drift over the same holding "
                             "period, never against zero. Both conditions must hold.")}}
    path = Path(a.out) if a.out else (PROJECT_ROOT / "data" / "screen_S011_with_baseline.json")
    path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\n  written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
