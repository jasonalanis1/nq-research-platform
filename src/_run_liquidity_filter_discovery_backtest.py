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

PERFORMANCE NOTE (2026-09-01): detect_level_sweep.scan_all_days() and
compute_levels() re-filter the FULL price DataFrame by date on every
call (`df[df.index.date == day]`), which is fine for a normal Terminal
session but too slow to fit in this bridged environment's per-command
time limit against ~2.2M Discovery-slice rows. fast_scan_all_days()
below is a PERFORMANCE-ONLY reimplementation of scan_all_days()'s outer
loop -- it pre-groups the DataFrame by day ONCE, then calls
detect_level_sweep.compute_levels() and .scan_for_signal() COMPLETELY
UNMODIFIED, just fed smaller pre-sliced inputs instead of the full
DataFrame each time. No detection logic is duplicated or changed. This
is verified in verify_fast_scan_matches_original() below -- run before
trusting the full result -- to confirm it produces byte-identical
signals to calling scan_all_days() directly on the same data, the same
way generate_signals() was verified against the CSV output on
2026-08-20 per detect_level_sweep.py's own docstring.

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


def group_by_day(df: pd.DataFrame) -> dict:
    """One dict lookup, built once: day -> that day's price rows."""
    return {day: sub for day, sub in df.groupby(df.index.date)}


def fast_scan_all_days(day_groups: dict, confirmation_mode: str = "close_any") -> tuple:
    """Performance-only reimplementation of detect_level_sweep.scan_all_days()'s
    outer loop -- see module docstring. compute_levels() and
    scan_for_signal() themselves are called completely unmodified."""
    all_days = sorted(day_groups.keys())
    signals = []
    skipped_no_levels = 0
    no_signal_days = 0

    for i, day in enumerate(all_days):
        if i == 0:
            continue
        prior_day = all_days[i - 1]

        # compute_levels() only ever filters by df.index.date == day/prior_day,
        # so handing it just these two days' rows (instead of the full
        # multi-year frame) produces an identical result, much faster.
        two_day_slice = pd.concat([day_groups[prior_day], day_groups[day]])
        levels = dls.compute_levels(two_day_slice, day, prior_day)
        if levels is None:
            skipped_no_levels += 1
            continue

        day_df = day_groups[day]
        signal = dls.scan_for_signal(day_df, levels, confirmation_mode)
        if signal is not None:
            signal["date"] = day
            signals.append(signal)
        else:
            no_signal_days += 1

    stats = {
        "total_days": len(all_days) - 1,
        "skipped_no_levels": skipped_no_levels,
        "no_signal_days": no_signal_days,
    }
    return signals, stats


def verify_fast_scan_matches_original(discovery_df: pd.DataFrame, day_groups: dict,
                                       n_check_days: int = 200) -> None:
    """Runs BOTH the original (slow) scan_all_days() and fast_scan_all_days()
    on the same small leading slice of Discovery data and asserts identical
    output, before trusting the fast version on the full dataset."""
    check_days = sorted(day_groups.keys())[:n_check_days]
    small_df = pd.concat([day_groups[d] for d in check_days])
    small_groups = {d: day_groups[d] for d in check_days}

    for variant in VARIANTS:
        slow_signals, slow_stats = dls.scan_all_days(small_df, variant)
        fast_signals, fast_stats = fast_scan_all_days(small_groups, variant)

        assert slow_stats == fast_stats, f"{variant}: stats differ -- slow={slow_stats} fast={fast_stats}"
        assert len(slow_signals) == len(fast_signals), (
            f"{variant}: signal count differs -- slow={len(slow_signals)} fast={len(fast_signals)}"
        )
        for s, f in zip(slow_signals, fast_signals):
            assert s == f, f"{variant}: a signal differs -- slow={s} fast={f}"

        print(f"  verify OK ({variant}): {len(slow_signals)} signals on {n_check_days}-day check slice, byte-identical.")


def backtest_signal_subset(signals, day_groups, variant, bucket):
    """Runs backtest.simulate_trade() on a list of raw signal dicts
    (detect_level_sweep.py's shape), reusing backtest.py's exact cost
    model, and writes a results CSV in the same shape backtest.py itself
    produces. Returns the output path."""
    rows = []
    for s in signals:
        day = s["date"]
        day_df = day_groups[day]
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
    day_groups = group_by_day(discovery_df)
    print(f"\nVerifying the fast day-scan reimplementation against the original, unmodified scan_all_days()...")
    verify_fast_scan_matches_original(discovery_df, day_groups)
    print("Verification passed -- proceeding with the full Discovery-slice run.\n")

    daily = ts.to_daily_bars(discovery_df)
    swings = ts.find_swing_points(daily)
    n_swing_highs = int(swings["swing_high"].sum())
    n_swing_lows = int(swings["swing_low"].sum())
    print(f"Discovery daily bars: {len(daily)} days. Swing highs found: {n_swing_highs}, swing lows: {n_swing_lows}.\n")

    for variant in VARIANTS:
        raw_signals, stats = fast_scan_all_days(day_groups, variant)
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
            out_path, results_df = backtest_signal_subset(subset, day_groups, variant, bucket)
            resolved = results_df[~results_df["exit_reason"].str.startswith("unresolved")]
            print(f"  {bucket}: {len(subset)} signals -> {len(resolved)} resolved -> {out_path.name}")
        print()


if __name__ == "__main__":
    main()
