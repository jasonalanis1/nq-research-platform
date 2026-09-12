"""
study_ib_breakout_afternoon_conditioned_stop.py
===================================================

exp-127 -- frozen spec:
research/studies/ib-breakout-afternoon-conditioned-stop-overlay-spec.md

Tests whether the IB Breakout continuation setup's costed economics
differ when the stop distance is re-anchored (widened or tightened,
never the target) at 14:00 ET using get_afternoon_conditioning()'s
Validation-confirmed multiplier (hyp-000106 / OBS-FINDING-011), for
trades still open at that point. Paired design: same signal set, two
policies (UNCONDITIONED vs CONDITIONED), diff = conditioned - baseline
per trade.

REUSED, UNMODIFIED: detect_ib_breakout.detect_ib_breakout_for_day,
backtest.ROUND_TRIP_COST_POINTS, data_split.get_discovery_data,
volatility_conditioning.build_midday_afternoon_frame,
volatility_conditioning.get_afternoon_conditioning.

HOW TO RUN:
    python3 src/study_ib_breakout_afternoon_conditioned_stop.py
    COST_STRESS_MULTIPLIER=2 python3 src/study_ib_breakout_afternoon_conditioned_stop.py
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from detect_ib_breakout import detect_ib_breakout_for_day
from backtest import ROUND_TRIP_COST_POINTS
from volatility_conditioning import build_midday_afternoon_frame, get_afternoon_conditioning

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_BUCKET_TRADES = 30
COST_STRESS_MULTIPLIER = float(os.environ.get("COST_STRESS_MULTIPLIER", "1.0"))


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    """Bootstrap CI on the MEAN of a single sample (paired-diff use case
    -- distinct from exp-077/093's two-sample bootstrap_diff_ci)."""
    rng = np.random.default_rng(seed)
    arr = np.array(values)
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        means[i] = rng.choice(arr, size=len(arr), replace=True).mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def simulate_trade_baseline(day_df: pd.DataFrame, signal: dict, cost_points: float) -> dict:
    """Exact reproduction of backtest.simulate_trade(), inlined so both
    arms share one bar-walk loop shape for a clean diff -- fixed stop,
    fixed target throughout."""
    after = day_df[day_df.index > signal["breakout_time"]]
    for ts, bar in after.iterrows():
        if signal["direction"] == "long":
            hit_stop = bar["Low"] <= signal["stop"]
            hit_target = bar["High"] >= signal["target"]
        else:
            hit_stop = bar["High"] >= signal["stop"]
            hit_target = bar["Low"] <= signal["target"]
        if hit_stop and hit_target:
            return {"exit_time": ts, "exit_price": signal["stop"], "exit_reason": "stop (ambiguous bar)"}
        if hit_stop:
            return {"exit_time": ts, "exit_price": signal["stop"], "exit_reason": "stop"}
        if hit_target:
            return {"exit_time": ts, "exit_price": signal["target"], "exit_reason": "target"}
    last_bar = day_df.iloc[-1]
    return {"exit_time": day_df.index[-1], "exit_price": last_bar["Close"], "exit_reason": "unresolved_end_of_data"}


def simulate_trade_afternoon_conditioned(day_df: pd.DataFrame, signal: dict, day,
                                          midday_afternoon_frame: pd.DataFrame) -> dict:
    """Frozen spec Section 6. Identical walk to simulate_trade_baseline
    except: at the first bar with timestamp >= 14:00:00 ET (if not
    already exited), the stop is re-anchored from ENTRY using
    get_afternoon_conditioning()'s multiplier. Target is never touched.
    Returns an extra 'afternoon_adjusted' flag: True iff the trade was
    still open at/after 14:00 (the AFFECTED subset, spec Section 7#2)."""
    entry = signal["entry"]
    direction = signal["direction"]
    target = signal["target"]
    original_risk = abs(entry - signal["stop"])
    current_stop = signal["stop"]

    tz = day_df.index.tz
    afternoon_ts = pd.Timestamp(day, tz=tz).replace(hour=14, minute=0, second=0)

    after = day_df[day_df.index > signal["breakout_time"]]
    adjusted_applied = False

    for ts, bar in after.iterrows():
        if not adjusted_applied and ts >= afternoon_ts:
            cond = get_afternoon_conditioning(day, midday_afternoon_frame)
            mult = cond["expected_afternoon_range_multiplier"]
            adjusted_risk = original_risk * mult
            current_stop = (entry - adjusted_risk) if direction == "long" else (entry + adjusted_risk)
            adjusted_applied = True

        if direction == "long":
            hit_stop = bar["Low"] <= current_stop
            hit_target = bar["High"] >= target
        else:
            hit_stop = bar["High"] >= current_stop
            hit_target = bar["Low"] <= target

        if hit_stop and hit_target:
            return {"exit_time": ts, "exit_price": current_stop, "exit_reason": "stop (ambiguous bar)", "afternoon_adjusted": adjusted_applied}
        if hit_stop:
            return {"exit_time": ts, "exit_price": current_stop, "exit_reason": "stop", "afternoon_adjusted": adjusted_applied}
        if hit_target:
            return {"exit_time": ts, "exit_price": target, "exit_reason": "target", "afternoon_adjusted": adjusted_applied}

    last_bar = day_df.iloc[-1]
    return {"exit_time": day_df.index[-1], "exit_price": last_bar["Close"],
            "exit_reason": "unresolved_end_of_data", "afternoon_adjusted": adjusted_applied}


def r_multiple_net(entry, direction, risk_points, outcome, cost_points):
    if direction == "long":
        pnl_gross = outcome["exit_price"] - entry
    else:
        pnl_gross = entry - outcome["exit_price"]
    is_resolved = not outcome["exit_reason"].startswith("unresolved")
    pnl_net = pnl_gross - cost_points if is_resolved else pnl_gross
    return pnl_net / risk_points if risk_points else float("nan")


def main():
    print("=" * 78)
    print("EXP-127: IB BREAKOUT, AFTERNOON-CONDITIONED STOP-WIDTH OVERLAY")
    print(f"(cost stress multiplier: {COST_STRESS_MULTIPLIER}x)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/ib-breakout-afternoon-conditioned-stop-overlay-spec.md\n")

    df, is_synthetic = load_price_data(context="study_ib_breakout_afternoon_conditioned_stop.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    day_groups = {d: g for d, g in discovery.groupby(discovery.index.date)}

    signals = []
    for day, day_df in day_groups.items():
        sig = detect_ib_breakout_for_day(day_df, day)
        if sig is not None:
            signals.append(sig)
    print(f"IB Breakout signals on Discovery: {len(signals)} (of {len(day_groups)} days scanned)")

    midday_afternoon_frame = build_midday_afternoon_frame(discovery)

    cost_points = ROUND_TRIP_COST_POINTS  # already reflects COST_STRESS_MULTIPLIER via backtest.py's own env read

    rows = []
    for sig in signals:
        day = sig["date"]
        day_df = day_groups.get(day)
        if day_df is None:
            continue
        risk_points = abs(sig["entry"] - sig["stop"])
        if not risk_points:
            continue

        baseline = simulate_trade_baseline(day_df, sig, cost_points)
        conditioned = simulate_trade_afternoon_conditioned(day_df, sig, day, midday_afternoon_frame)

        r_base = r_multiple_net(sig["entry"], sig["direction"], risk_points, baseline, cost_points)
        r_cond = r_multiple_net(sig["entry"], sig["direction"], risk_points, conditioned, cost_points)

        narrow = bool(midday_afternoon_frame.loc[day, "narrow_midday"]) if day in midday_afternoon_frame.index and pd.notna(midday_afternoon_frame.loc[day, "narrow_midday"]) else False

        rows.append({
            "date": str(day),
            "direction": sig["direction"],
            "r_multiple_net_baseline": r_base,
            "r_multiple_net_conditioned": r_cond,
            "diff": r_cond - r_base,
            "afternoon_adjusted": conditioned["afternoon_adjusted"],
            "narrow_midday": narrow,
        })

    results = pd.DataFrame(rows)
    print(f"\nTotal trades: {len(results)}")

    affected = results[results["afternoon_adjusted"]]
    unaffected = results[~results["afternoon_adjusted"]]
    print(f"Still open at 14:00 ET (AFFECTED, overlay could act): {len(affected)}")
    print(f"Already exited before 14:00 (UNAFFECTED, diff=0 by construction): {len(unaffected)}")
    print(f"  unaffected max|diff| (sanity check, should be 0): {unaffected['diff'].abs().max() if len(unaffected) else float('nan')}")

    def report(label, sub):
        if len(sub) < MIN_BUCKET_TRADES:
            print(f"\n{label}: n={len(sub)} -- BELOW {MIN_BUCKET_TRADES}-trade eligibility floor, flagged too thin to trust, no verdict drawn.")
            return None
        lo, hi = bootstrap_mean_ci(sub["diff"].values)
        mean_diff = sub["diff"].mean()
        mean_base = sub["r_multiple_net_baseline"].mean()
        mean_cond = sub["r_multiple_net_conditioned"].mean()
        print(f"\n{label}: n={len(sub)}")
        print(f"  mean baseline r_multiple_net:    {mean_base:.4f}")
        print(f"  mean conditioned r_multiple_net: {mean_cond:.4f}")
        print(f"  mean paired diff (cond-base):    {mean_diff:.4f}  90% CI [{lo:.4f}, {hi:.4f}]")
        credible = lo > 0 or hi < 0
        print(f"  credible (CI excludes zero): {credible}")
        return {"n": len(sub), "mean_baseline": mean_base, "mean_conditioned": mean_cond,
                "mean_diff": mean_diff, "ci_90": [lo, hi], "credible": credible}

    print("\n" + "-" * 78)
    print("1. ALL TRADES (intent-to-treat)")
    all_result = report("All trades", results)

    print("\n" + "-" * 78)
    print("2. AFFECTED-ONLY (the real test)")
    affected_result = report("Affected-only (open at 14:00)", affected)

    print("\n" + "-" * 78)
    print("3. AFFECTED, split by narrow vs not-narrow afternoon (diagnostic)")
    narrow_result = report("Affected, narrow_midday=True", affected[affected["narrow_midday"]])
    not_narrow_result = report("Affected, narrow_midday=False", affected[~affected["narrow_midday"]])

    out = {
        "cost_stress_multiplier": COST_STRESS_MULTIPLIER,
        "total_signals": len(results),
        "all_trades": all_result,
        "affected_only": affected_result,
        "affected_narrow_midday": narrow_result,
        "affected_not_narrow_midday": not_narrow_result,
    }

    suffix = "" if COST_STRESS_MULTIPLIER == 1.0 else f"_stress{COST_STRESS_MULTIPLIER:g}x"
    out_path = DATA_DIR / f"exp127_ib_breakout_afternoon_conditioned_results{suffix}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")

    results_path = DATA_DIR / f"exp127_ib_breakout_afternoon_conditioned_trades{suffix}.csv"
    results.to_csv(results_path, index=False)
    print(f"Saved: {results_path}")


if __name__ == "__main__":
    main()
