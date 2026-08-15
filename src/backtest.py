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

HOW TO RUN:
    python3 src/backtest.py
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_price_data():
    candidates = sorted(DATA_DIR.glob("NQ_1min_*.csv"))
    real_files = [c for c in candidates if "SYNTHETIC" not in c.name]
    chosen = real_files[-1] if real_files else candidates[-1]
    df = pd.read_csv(chosen, index_col="timestamp_ny", parse_dates=True)
    return df, ("SYNTHETIC" in chosen.name)


def simulate_trade(day_df: pd.DataFrame, signal: pd.Series) -> dict:
    """Walks forward bar-by-bar after the breakout to see which level got
    touched first: stop or target."""
    after = day_df[day_df.index > signal["breakout_time"]]

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
    price_df, is_synthetic = load_price_data()
    signals_df = pd.read_csv(DATA_DIR / "setups_orb.csv", parse_dates=["date", "breakout_time"])

    if signals_df.empty:
        print("No signals to backtest -- run detect_setups.py first.")
        return

    results = []
    for _, sig in signals_df.iterrows():
        day = sig["date"].date()
        day_df = price_df[price_df.index.date == day]
        outcome = simulate_trade(day_df, sig)

        risk_points = abs(sig["entry"] - sig["stop"])
        if sig["direction"] == "long":
            pnl_points = outcome["exit_price"] - sig["entry"]
        else:
            pnl_points = sig["entry"] - outcome["exit_price"]
        r_multiple = pnl_points / risk_points if risk_points else float("nan")

        results.append({
            "date": day,
            "direction": sig["direction"],
            "entry": sig["entry"],
            "stop": sig["stop"],
            "target": sig["target"],
            "exit_time": outcome["exit_time"],
            "exit_price": round(outcome["exit_price"], 2),
            "exit_reason": outcome["exit_reason"],
            "pnl_points": round(pnl_points, 2),
            "r_multiple": round(r_multiple, 3),
        })

    results_df = pd.DataFrame(results)
    out_path = DATA_DIR / "backtest_results.csv"
    results_df.to_csv(out_path, index=False)

    resolved = results_df[~results_df["exit_reason"].str.startswith("unresolved")]
    unresolved_count = len(results_df) - len(resolved)
    wins = resolved[resolved["exit_reason"].str.startswith("target")]
    losses = resolved[resolved["exit_reason"].str.startswith("stop")]

    print(f"Backtested {len(results_df)} signals.")
    if is_synthetic:
        print("NOTE: SYNTHETIC data -- these results are for testing the pipeline only, not a real edge.")
    print(f"  Resolved (hit stop or target): {len(resolved)}")
    print(f"  Unresolved (ran out of data before either hit): {unresolved_count}")
    if len(resolved) > 0:
        print(f"  Wins:   {len(wins)}  ({len(wins)/len(resolved):.1%})")
        print(f"  Losses: {len(losses)}  ({len(losses)/len(resolved):.1%})")
    print(f"\nSaved trade-by-trade results to: {out_path}")


if __name__ == "__main__":
    main()
