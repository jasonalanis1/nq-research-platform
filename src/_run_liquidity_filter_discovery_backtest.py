"""
_run_liquidity_filter_discovery_backtest.py
==============================================
TEMPORARY DRIVER -- not part of the permanent pipeline, deleted after use,
same pattern as exp-025's _run_fvg_discovery_backtest.py.

Runs Level Sweep Reversal's close_min_distance and full_bar_range
variants on the Discovery slice ONLY, classifies every signal as
'protected' or 'not_protected' per trend_structure.py /
research/setups/trend-structure-liquidity-filter.md, and backtests each
of the four resulting buckets (2 variants x 2 buckets) through the
existing, unmodified cost model (reusing backtest.simulate_trade
directly, not reimplementing it), writing results in the exact shape
score_results.py and confidence_analysis.py already expect.

Swing/trend structure is computed from Discovery-slice daily bars ONLY
-- never Validation or Holdout data -- consistent with data_split.py's
entire purpose (an R&D agent, and this driver is playing that role, may
only ever see Discovery).
"""
import sys
import pandas as pd
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
import detect_level_sweep as dls
import trend_structure as ts
import backtest as bt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

VARIANTS = ["close_min_distance", "full_bar_range"]


def backtest_signal_subset(signals, discovery_df, variant, bucket):
    """Runs backtest.simulate_trade() on a list of raw signal dicts
    (detect_level_sweep.py's shape), reusing backtest.py's exact cost
    model, and writes a results CSV in the same shape backtest.py itself
    produces. Returns the output path."""
    rows = []
    for s in signals:
        day = s["date"]
        day_df = discovery_df[discovery_df.index.date == day]
        sig_series = pd.Series({
            "direction": s["direction"],
            "signal_time": s["signal_time"],
            "stop": s["stop"],
            "target": s["target"],
        })
        outcome = bt.simulate_trade(day_df, sig_series, "signal_time")

        risk_points = abs(s["entry"] - s["stop"])
        if s["direction"] == "long":
            pnl_points_gross = outcome["exit_price"] - s["entry"]
        else:
            pnl_points_gross = s["entry"] - outcome["exit_price"]

        is_resolved = not outcome["exit_reason"].startswith("unresolved")
        pnl_points_net = pnl_points_gross - bt.ROUND_TRIP_COST_POINTS if is_resolved else pnl_points_gross
        r_multiple_gross = pnl_points_gross / risk_points if risk_points else float("nan")
        r_multiple_net = pnl_points_net / risk_points if risk_points else float("nan")

        rows.append({
            "date": day,
            "direction": s["direction"],
            "entry": s["entry"],
            "stop": s["stop"],
            "target": s["target"],
            "exit_time": outcome["exit_time"],
            "exit_price": round(outcome["exit_price"], 2),
            "exit_reason": outcome["exit_reason"],
            "pnl_points_gross": round(pnl_points_gross, 2),
            "pnl_points_net": round(pnl_points_net, 2),
            "pnl_dollars_net": round(pnl_points_net * bt.CONTRACT_MULTIPLIER, 2),
            "r_multiple_gross": round(r_multiple_gross, 3),
            "r_multiple_net": round(r_multiple_net, 3),
            "is_synthetic": False,
        })

    results_df = pd.DataFrame(rows)
    out_path = DATA_DIR / f"backtest_results_level_sweep_{variant}_{bucket}_discovery.csv"
    results_df.to_csv(out_path, index=False)
    return out_path, results_df


def main():
    full_df, is_synthetic = load_price_data(context="_run_liquidity_filter_discovery_backtest.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this driver requires real data.")
        return

    discovery_df = get_discovery_data(full_df)

    daily = ts.to_daily_bars(discovery_df)
    swings = ts.find_swing_points(daily)
    n_swing_highs = int(swings["swing_high"].sum())
    n_swing_lows = int(swings["swing_low"].sum())
    print(f"Discovery daily bars: {len(daily)} days. Swing highs found: {n_swing_highs}, swing lows: {n_swing_lows}.\n")

    for variant in VARIANTS:
        raw_signals, stats = dls.scan_all_days(discovery_df, variant)
        print(f"=== {variant}: {len(raw_signals)} raw signals on Discovery ({stats}) ===")

        protected, not_protected = [], []
        trend_counts = {}
        for s in raw_signals:
            classification = ts.classify_signal(swings, s["date"], s["direction"], s["level_swept"])
            trend_counts[classification["trend"]] = trend_counts.get(classification["trend"], 0) + 1
            if classification["classification"] == "protected":
                protected.append(s)
            else:
                not_protected.append(s)

        print(f"  Trend context at signal time: {trend_counts}")
        print(f"  Protected-level sweeps: {len(protected)}   Interior/not_protected sweeps: {len(not_protected)}")

        for bucket, subset in [("protected", protected), ("not_protected", not_protected)]:
            if not subset:
                print(f"  {bucket}: 0 signals, skipping backtest.")
                continue
            out_path, results_df = backtest_signal_subset(subset, discovery_df, variant, bucket)
            resolved = results_df[~results_df["exit_reason"].str.startswith("unresolved")]
            print(f"  {bucket}: {len(subset)} signals -> {len(resolved)} resolved -> {out_path.name}")
        print()


if __name__ == "__main__":
    main()
