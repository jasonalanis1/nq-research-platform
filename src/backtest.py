"""
backtest.py
=============
Stage 3 of the roadmap: for every signal detect_setups.py found, actually
simulate what would have happened -- did price hit the target first (a
win), the stop first (a loss), or neither before we ran out of data for
that day (unresolved)?

HOW THIS WORKS, IN PLAIN ENGLISH:
For each signal, we start at the minute AFTER the breakout bar and walk
forward one minute at a time. On each bar we check: did the price touch
the stop level? Did it touch the target level? The first one it touches
wins. If a single 1-minute bar's high/low range happens to touch BOTH
the stop and the target (rare, but possible with volatile bars), we
conservatively assume the stop was hit first -- this avoids making the
system look better than it might really be, since we don't know the
exact order price moved within that one minute.

CAVEAT (important, see docs/ROADMAP.md): the synthetic data currently
only covers 6:00-11:00 AM NY each day. Some signals won't resolve (hit
neither stop nor target) before the data simply ends for that day. Those
get marked "unresolved" and excluded from the win-rate math, not counted
as losses. Once real data (which covers a full trading session) is used,
this should mostly go away.

COST MODELING (added 2026-08-16): real trading costs money per trade --
commissions the broker charges, plus "slippage" (the difference between
the price you wanted and the price you actually got, since orders take a
moment to fill and the market doesn't wait). Earlier versions of this
script ignored both, which made results look better than they'd really
be. Every trade below now gets both a GROSS result (pure price action,
ignoring costs -- what earlier runs showed) and a NET result (after
estimated costs -- much closer to what you'd actually keep). The NET
numbers are what scoring should trust.

THE COST ASSUMPTIONS BELOW ARE PLACEHOLDERS, NOT YOUR REAL COSTS. Typical
retail futures costs, so you have a defensible starting point, but every
broker is different -- swap these for your actual commission schedule and
a slippage estimate you trust once you have one:
  - CONTRACT_MULTIPLIER: $20/point is standard full-size NQ. Micro NQ
    (MNQ) is $2/point instead -- change this if that's what you trade.
  - COMMISSION_PER_SIDE: a commonly-cited all-in (commission + exchange +
    NFA fees) retail futures rate. Round-trip (in + out) is double this.
  - SLIPPAGE_TICKS_PER_SIDE: how many ticks worse than the signal price
    we assume you actually get filled at, each side. 1 tick = 0.25
    points for NQ.

STRESS-TESTING COSTS (added 2026-08-16): to check how sensitive a result
is to the cost assumptions above being too optimistic, set the
COST_STRESS_MULTIPLIER environment variable to scale BOTH commission and
slippage by that factor, e.g.:
    COST_STRESS_MULTIPLIER=2 python3 src/backtest.py setups_level_sweep_close_min_distance.csv
Defaults to 1.0 (no change) if not set. When a multiplier other than 1.0
is used, it's appended to the output filename (e.g.
backtest_results_level_sweep_close_min_distance_stress2x.csv) so a
stress-test run can never overwrite the normal-cost result.

HOW TO RUN:
    python3 src/backtest.py
"""

import os
import sys
import pandas as pd
from pathlib import Path
from data_holdout import apply_holdout_boundary

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# This script now works with ANY setup's signal file, not just the ORB
# one -- run it as `python3 src/backtest.py setups_level_sweep.csv` to
# backtest a different setup. Defaults to the original ORB signals so
# existing habits/commands keep working unchanged.
DEFAULT_SIGNALS_FILE = "setups_orb.csv"

# --- Cost assumptions (see COST MODELING note above -- placeholders) ---
COST_STRESS_MULTIPLIER = float(os.environ.get("COST_STRESS_MULTIPLIER", "1.0"))
CONTRACT_MULTIPLIER = 20.0     # dollars per index point, full-size NQ (MNQ = 2.0)
TICK_SIZE = 0.25                # NQ minimum price movement, in points
COMMISSION_PER_SIDE = 2.50 * COST_STRESS_MULTIPLIER      # dollars, all-in estimate, per contract, per side
SLIPPAGE_TICKS_PER_SIDE = 1.0 * COST_STRESS_MULTIPLIER   # assumed ticks of slippage, per side

ROUND_TRIP_COMMISSION_DOLLARS = COMMISSION_PER_SIDE * 2
ROUND_TRIP_SLIPPAGE_POINTS = SLIPPAGE_TICKS_PER_SIDE * TICK_SIZE * 2
ROUND_TRIP_COST_POINTS = (ROUND_TRIP_COMMISSION_DOLLARS / CONTRACT_MULTIPLIER) + ROUND_TRIP_SLIPPAGE_POINTS


def load_price_data():
    candidates = sorted(DATA_DIR.glob("NQ_1min_*.csv"))
    real_files = [c for c in candidates if "SYNTHETIC" not in c.name]
    chosen = real_files[-1] if real_files else candidates[-1]
    df = pd.read_csv(chosen, index_col="timestamp_ny")
    # See detect_setups.py's load_latest_data() for why this can't be a
    # plain parse_dates=True -- files spanning a DST change mix UTC
    # offsets, which that silently fails to parse correctly.
    df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York")
    is_synthetic = "SYNTHETIC" in chosen.name
    if not is_synthetic:
        df = apply_holdout_boundary(df, context="backtest.py")
    return df, is_synthetic


def simulate_trade(day_df: pd.DataFrame, signal: pd.Series, signal_time_col: str) -> dict:
    """Walks forward bar-by-bar after the signal to see which level got
    touched first: stop or target. `signal_time_col` is whichever column
    in this setup's signal file marks the entry moment (different setups
    name it differently -- "breakout_time" for ORB, "signal_time" for
    Level Sweep Reversal)."""
    after = day_df[day_df.index > signal[signal_time_col]]

    for ts, bar in after.iterrows():
        if signal["direction"] == "long":
            hit_stop = bar["Low"] <= signal["stop"]
            hit_target = bar["High"] >= signal["target"]
        else:  # short
            hit_stop = bar["High"] >= signal["stop"]
            hit_target = bar["Low"] <= signal["target"]

        if hit_stop and hit_target:
            # Can't tell which happened first within this one bar --
            # conservatively assume the worse outcome (the stop).
            return {"exit_time": ts, "exit_price": signal["stop"], "exit_reason": "stop (ambiguous bar)"}
        if hit_stop:
            return {"exit_time": ts, "exit_price": signal["stop"], "exit_reason": "stop"}
        if hit_target:
            return {"exit_time": ts, "exit_price": signal["target"], "exit_reason": "target"}

    # Ran out of bars for the day without hitting either level.
    last_bar = day_df.iloc[-1]
    return {"exit_time": day_df.index[-1], "exit_price": last_bar["Close"], "exit_reason": "unresolved_end_of_data"}


def main():
    signals_filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SIGNALS_FILE
    signals_path = DATA_DIR / signals_filename
    if not signals_path.exists():
        print(f"No signals file found at {signals_path}. Run the matching detect_*.py script first.")
        return

    # Different setups name their "when the signal fired" column
    # differently -- figure out which one this file uses.
    header = pd.read_csv(signals_path, nrows=0).columns
    if "breakout_time" in header:
        signal_time_col = "breakout_time"
    elif "signal_time" in header:
        signal_time_col = "signal_time"
    else:
        print(f"Couldn't find a recognized signal-time column in {signals_filename}.")
        return

    price_df, is_synthetic = load_price_data()
    signals_df = pd.read_csv(signals_path, parse_dates=["date", signal_time_col])

    if signals_df.empty:
        print(f"No signals in {signals_filename} to backtest.")
        return

    # Output filename mirrors the input, so different setups' results
    # never overwrite each other: setups_orb.csv -> backtest_results.csv
    # (kept as the original name for backward compatibility), anything
    # else -> backtest_results_<suffix>.csv
    stress_suffix = "" if COST_STRESS_MULTIPLIER == 1.0 else f"_stress{COST_STRESS_MULTIPLIER:g}x"
    if signals_filename == "setups_orb.csv":
        out_path = DATA_DIR / f"backtest_results{stress_suffix}.csv"
    else:
        suffix = signals_filename.replace("setups_", "").replace(".csv", "")
        out_path = DATA_DIR / f"backtest_results_{suffix}{stress_suffix}.csv"

    results = []
    for _, sig in signals_df.iterrows():
        day = sig["date"].date()
        day_df = price_df[price_df.index.date == day]
        outcome = simulate_trade(day_df, sig, signal_time_col)

        risk_points = abs(sig["entry"] - sig["stop"])
        if sig["direction"] == "long":
            pnl_points_gross = outcome["exit_price"] - sig["entry"]
        else:
            pnl_points_gross = sig["entry"] - outcome["exit_price"]

        # Unresolved trades never actually closed, so no cost was paid --
        # only resolved (stop or target hit) trades get costs deducted.
        is_resolved = not outcome["exit_reason"].startswith("unresolved")
        pnl_points_net = pnl_points_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_points_gross

        r_multiple_gross = pnl_points_gross / risk_points if risk_points else float("nan")
        r_multiple_net = pnl_points_net / risk_points if risk_points else float("nan")

        results.append({
            "date": day,
            "direction": sig["direction"],
            "entry": sig["entry"],
            "stop": sig["stop"],
            "target": sig["target"],
            "exit_time": outcome["exit_time"],
            "exit_price": round(outcome["exit_price"], 2),
            "exit_reason": outcome["exit_reason"],
            "pnl_points_gross": round(pnl_points_gross, 2),
            "pnl_points_net": round(pnl_points_net, 2),
            "pnl_dollars_net": round(pnl_points_net * CONTRACT_MULTIPLIER, 2),
            "r_multiple_gross": round(r_multiple_gross, 3),
            "r_multiple_net": round(r_multiple_net, 3),
            "is_synthetic": is_synthetic,
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(out_path, index=False)

    resolved = results_df[~results_df["exit_reason"].str.startswith("unresolved")]
    unresolved_count = len(results_df) - len(resolved)
    wins_net = resolved[resolved["r_multiple_net"] > 0]
    losses_net = resolved[resolved["r_multiple_net"] <= 0]

    print(f"Backtested {len(results_df)} signals.")
    if COST_STRESS_MULTIPLIER != 1.0:
        print(f"  COST STRESS TEST: commission/slippage scaled {COST_STRESS_MULTIPLIER:g}x above the normal placeholder assumptions.")
    if is_synthetic:
        print("NOTE: SYNTHETIC data -- these results are for testing the pipeline only, not a real edge.")
    print(f"  Resolved (hit stop or target): {len(resolved)}")
    print(f"  Unresolved (ran out of data before either hit): {unresolved_count}")
    print(f"  Assumed round-trip cost per trade: {ROUND_TRIP_COST_POINTS:.3f} points "
          f"(${ROUND_TRIP_COMMISSION_DOLLARS:.2f} commission + "
          f"{ROUND_TRIP_SLIPPAGE_POINTS:.2f}pt slippage) -- see script header to adjust")
    if len(resolved) > 0:
        print(f"  Wins (net of costs):   {len(wins_net)}  ({len(wins_net)/len(resolved):.1%})")
        print(f"  Losses (net of costs): {len(losses_net)}  ({len(losses_net)/len(resolved):.1%})")
        # Show how much costs alone changed the picture, since that's easy to
        # miss if you only ever look at the net numbers.
        flipped = resolved[(resolved["r_multiple_gross"] > 0) & (resolved["r_multiple_net"] <= 0)]
        if len(flipped) > 0:
            print(f"  Trades that were winners gross but losers after costs: {len(flipped)}")
    print(f"\nSaved trade-by-trade results to: {out_path}")


if __name__ == "__main__":
    main()
