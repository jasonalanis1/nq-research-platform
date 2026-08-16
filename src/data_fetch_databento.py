"""
data_fetch_databento.py
=========================

WHAT THIS FILE DOES (plain English):
Downloads 2 years of REAL 1-minute NQ futures bars from Databento (a
paid market data vendor) and saves them to data/, in the same format the
rest of the pipeline (detect_setups.py, detect_level_sweep.py,
backtest.py, ...) already expects. This is a step up from
data_fetch.py (Yahoo Finance), which only gives ~30 days of 1-minute
history -- Databento gives us a much longer, better-quality window to
backtest against. (Cost check, 2026-08-16: a 2-year pull of this data
quotes at ~$2.55 via Databento's own cost-estimation endpoint -- cheap
relative to Jason's remaining account balance.)

WHERE THE DATA COMES FROM: dataset "GLBX.MDP3" is CME Globex's own
market data feed (the exchange NQ futures actually trade on) -- this is
closer to institutional-grade than Yahoo's free feed. We pull the
CONTINUOUS front-month contract (symbol "NQ.c.0"), which is Databento's
equivalent of Yahoo's "NQ=F": one unbroken price series that
automatically splices together whichever contract month is currently
most active, instead of you having to track contract expirations
yourself. Same rollover caveat as Yahoo's NQ=F applies: small price
jumps at contract rollover dates.

ABOUT YOUR API KEY (read this before running):
Databento is a PAID service and your API key is a secret, like a
password -- anyone with it can rack up charges on your account. This
script never asks you to paste it into a chat conversation. Instead, in
order of preference, it looks for the key:
    1. In the DATABENTO_API_KEY environment variable, if you've set one.
    2. In a local file called `.databento_key` in the project root (one
       line, just the key). This file is listed in .gitignore, so it
       can never accidentally get pushed to GitHub.
    3. If neither exists, it asks you to type/paste it directly into
       Terminal (hidden as you type, like a password prompt) and offers
       to save it to that local file so you don't have to re-enter it
       next time.

HOW TO RUN:
    python3 src/data_fetch_databento.py
"""

import os
import sys
import getpass
import pandas as pd
import databento as db
from pathlib import Path
from datetime import datetime, timedelta

DATASET = "GLBX.MDP3"        # CME Globex MDP 3.0 -- the exchange feed NQ futures trade on
SYMBOL = "NQ.c.0"             # continuous front-month NQ futures (Databento's equivalent of Yahoo's NQ=F)
SCHEMA = "ohlcv-1m"           # 1-minute OHLCV bars
LOOKBACK_DAYS = 730           # ~2 years. Databento's trial/plan limits may cap this further --
                               # if so, the error message from the API will say so plainly.
                               # ohlcv-1m for GLBX.MDP3 goes back to 2010, so this is well within range.
NY_TIMEZONE = "America/New_York"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
KEY_FILE = PROJECT_ROOT / ".databento_key"


def get_api_key() -> str:
    """
    Finds the Databento API key without ever needing it typed into a
    chat conversation -- see the file header for the three places this
    checks, in order.
    """
    env_key = os.environ.get("DATABENTO_API_KEY")
    if env_key:
        print("Using API key from the DATABENTO_API_KEY environment variable.")
        return env_key.strip()

    if KEY_FILE.exists():
        print(f"Using API key saved in {KEY_FILE.name}.")
        return KEY_FILE.read_text().strip()

    print(f"\nNo Databento API key found (checked the DATABENTO_API_KEY "
          f"environment variable and {KEY_FILE.name}).")
    key = getpass.getpass("Paste your Databento API key (input will be hidden): ").strip()
    if not key:
        raise RuntimeError("No API key entered -- can't continue without one.")

    save = input(f"Save this key to {KEY_FILE.name} so you don't have to re-enter it next time? [y/N]: ").strip().lower()
    if save == "y":
        KEY_FILE.write_text(key + "\n")
        KEY_FILE.chmod(0o600)  # restrict the file to only your user account, like a password file
        print(f"Saved to {KEY_FILE.name} (already excluded from git via .gitignore).")

    return key


def fetch_databento_minute_data(api_key: str) -> pd.DataFrame:
    """
    Downloads ~LOOKBACK_DAYS days of 1-minute NQ futures bars from
    Databento's historical API.

    Returns a DataFrame with columns Open, High, Low, Close, Volume,
    indexed by timestamp in New York time -- matching the exact shape
    data_fetch.py (the Yahoo Finance version) already produces, so every
    downstream script (detect_setups.py, backtest.py, etc.) works with
    this data without any changes.
    """
    end = datetime.now()
    start = end - timedelta(days=LOOKBACK_DAYS)

    print(f"Requesting {LOOKBACK_DAYS} days of {SCHEMA} bars for {SYMBOL} "
          f"({DATASET}) from {start.date()} to {end.date()}...")
    print("(This calls Databento's paid historical API and will use credits/"
          "billing on your account.)")

    client = db.Historical(key=api_key)

    # stype_in="continuous" tells Databento that SYMBOL is a continuous-
    # contract symbol (NQ.c.0) rather than one specific expiring contract
    # code (like NQZ6) -- this is what gives us one unbroken price series.
    data = client.timeseries.get_range(
        dataset=DATASET,
        symbols=[SYMBOL],
        schema=SCHEMA,
        stype_in="continuous",
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
    )

    df = data.to_df()

    if df.empty:
        raise RuntimeError(
            "No data came back from Databento. Possible causes: your API "
            "key doesn't have access to the GLBX.MDP3 dataset, your "
            "plan/trial doesn't cover this date range, or there's a "
            "symbol/schema mismatch. Check the error details Databento "
            "printed above, if any."
        )

    # Databento's to_df() gives us a UTC-indexed DataFrame with lowercase
    # column names (open/high/low/close/volume) plus some extra metadata
    # columns we don't need. Rename and trim down to match the format
    # data_fetch.py (Yahoo) already produces.
    out = pd.DataFrame({
        "Open": df["open"],
        "High": df["high"],
        "Low": df["low"],
        "Close": df["close"],
        "Volume": df["volume"],
    })

    if out.index.tz is None:
        out.index = out.index.tz_localize("UTC")
    out.index = out.index.tz_convert(NY_TIMEZONE)
    out.index.name = "timestamp_ny"

    return out


def save_to_csv(df: pd.DataFrame) -> Path:
    """
    Saves with "databento" in the filename so it's unmistakably NOT the
    Yahoo Finance file or the synthetic file, and so every script that
    auto-picks "the latest real data file" (they sort filenames and skip
    anything with SYNTHETIC in the name) picks this one over a Yahoo
    pull -- "databento" sorts after any date-only Yahoo filename
    alphabetically, so this richer dataset naturally takes priority.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_path = DATA_DIR / f"NQ_1min_databento_{today_str}.csv"
    df.to_csv(out_path)
    return out_path


def main():
    api_key = get_api_key()
    df = fetch_databento_minute_data(api_key)

    print(f"\nGot {len(df)} rows.")
    print(f"Date range: {df.index.min()}  to  {df.index.max()}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nLast 5 rows:")
    print(df.tail())

    out_path = save_to_csv(df)
    print(f"\nSaved to: {out_path}")
    print("This is REAL Databento data (CME Globex GLBX.MDP3 feed) -- "
          "not Yahoo Finance, not synthetic.")


if __name__ == "__main__":
    main()
