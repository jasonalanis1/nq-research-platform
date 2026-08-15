"""
generate_sample_data.py
========================

WHY THIS FILE EXISTS:
This cloud workspace (where I, your coding assistant, run code) is on a
locked-down network that only allows connections to a small allowlist of
sites (mainly software package registries). It CANNOT reach Yahoo Finance,
or any other market data provider I tested. That's a hard limitation of
this sandbox, not something we can code around.

So, to keep building and testing the rest of the platform (setup
detection, backtesting, scoring) without being blocked, this script
generates FAKE-BUT-REALISTIC-LOOKING NQ minute bars. It uses a random walk
(basically: start at a price, then each minute nudge it up or down by a
random small amount) with volatility roughly in the ballpark of real NQ.

*** THIS IS NOT REAL MARKET DATA. DO NOT DRAW ANY TRADING CONCLUSIONS FROM
IT. ITS ONLY JOB IS TO LOOK ENOUGH LIKE REAL DATA THAT WE CAN BUILD AND
TEST CODE. ***

Once you run the real data_fetch.py on a machine with normal internet
access (your own Mac, for example), you'll swap this synthetic data out
for the real thing and everything downstream (setup detection, backtest
engine, scoring) will work on it exactly the same way, because they only
care about the shape of the data (timestamp, open, high, low, close,
volume) -- not where it came from.

HOW TO RUN:
    python3 src/generate_sample_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------
N_TRADING_DAYS = 90            # how many fake trading days to generate
SESSION_START_HOUR = 6         # 6:00 AM NY -- a bit before the open, for context
SESSION_END_HOUR = 11          # 11:00 AM NY -- a bit after the open
STARTING_PRICE = 20000.0       # arbitrary placeholder price level (NOT a real quote)
MINUTE_VOL_POINTS = 4.0        # rough standard deviation of price change per minute, in NQ points
OPEN_HOUR_NY = 8                # the 8:30 open we care about
OPEN_MINUTE_NY = 30
RANDOM_SEED = 42                # fixes the "randomness" so results are reproducible

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


def generate_trading_days(n_days: int) -> list[pd.Timestamp]:
    """
    Builds a list of weekday dates, walking backwards from today, skipping
    Saturday and Sunday (a simple stand-in for "market holidays" -- real
    holiday calendars are more precise, but this is fine for synthetic
    data whose only job is to exercise our code).
    """
    days = []
    current = pd.Timestamp.now(tz="America/New_York").normalize()
    while len(days) < n_days:
        current -= timedelta(days=1)
        if current.dayofweek < 5:  # Monday=0 ... Friday=4
            days.append(current)
    return sorted(days)


def generate_one_day(day: pd.Timestamp, start_price: float, rng: np.random.Generator) -> pd.DataFrame:
    """
    Generates one fake trading day of 1-minute OHLCV bars using a random
    walk. A "random walk" means: price_next = price_now + random_step,
    where random_step is drawn from a normal (bell-curve) distribution.
    This is a standard, simple way to produce data that LOOKS like a real
    price series (it wiggles up and down unpredictably) without claiming
    to model any real market behavior.

    We also add a small artificial "volatility bump" in the few minutes
    right after 8:30 to loosely mimic the fact that real markets often
    get more active right at the open -- again, purely so the resulting
    chart is a useful visual stand-in, not a claim about how real markets
    behave.
    """
    start_ts = day.replace(hour=SESSION_START_HOUR, minute=0)
    end_ts = day.replace(hour=SESSION_END_HOUR, minute=0)
    timestamps = pd.date_range(start=start_ts, end=end_ts, freq="1min", tz="America/New_York")

    n = len(timestamps)
    steps = rng.normal(loc=0.0, scale=MINUTE_VOL_POINTS, size=n)

    # Bump volatility for the 10 minutes after the 8:30 open
    open_ts = day.replace(hour=OPEN_HOUR_NY, minute=OPEN_MINUTE_NY)
    for i, ts in enumerate(timestamps):
        minutes_after_open = (ts - open_ts).total_seconds() / 60
        if 0 <= minutes_after_open < 10:
            steps[i] *= 2.5  # more chop/movement right after the open

    prices = start_price + np.cumsum(steps)

    # Build simple OHLC bars from the minute-close random walk: treat each
    # step as the close, and derive a small synthetic high/low wiggle
    # around it so the bars look like real candles instead of flat dots.
    closes = prices
    opens = np.concatenate([[start_price], closes[:-1]])
    wiggle = rng.uniform(0.5, 2.5, size=n)
    highs = np.maximum(opens, closes) + wiggle
    lows = np.minimum(opens, closes) - wiggle
    volumes = rng.integers(200, 2000, size=n)

    df = pd.DataFrame(
        {
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": volumes,
        },
        index=timestamps,
    )
    df.index.name = "timestamp_ny"
    return df, closes[-1]


def main():
    rng = np.random.default_rng(RANDOM_SEED)
    days = generate_trading_days(N_TRADING_DAYS)

    print(f"Generating {len(days)} fake trading days of synthetic NQ 1-minute bars...")

    all_days = []
    price = STARTING_PRICE
    for day in days:
        day_df, price = generate_one_day(day, price, rng)
        all_days.append(day_df)

    full_df = pd.concat(all_days)

    print(f"Generated {len(full_df)} rows.")
    print(f"Date range: {full_df.index.min()}  to  {full_df.index.max()}")

    out_path = DATA_DIR / "NQ_1min_SYNTHETIC.csv"
    full_df.to_csv(out_path)
    print(f"\nSaved SYNTHETIC data to: {out_path}")
    print("Remember: this is fake data for building/testing code only.")


if __name__ == "__main__":
    main()
