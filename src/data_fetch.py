"""
data_fetch.py
==============

WHAT THIS FILE DOES (plain English):
This script downloads recent price history for NQ futures (the E-mini
Nasdaq-100 futures contract) and saves it to a CSV file on your computer
so we can analyze it later without re-downloading every time.

WHO THIS IS FOR:
You have minimal Python experience, so this file has a LOT of comments.
Comments are the lines starting with "#" -- Python ignores them completely,
they exist only for humans to read. Read them like a narrator explaining
what's happening.

HOW TO RUN THIS FILE:
From a terminal, inside this project folder, type:
    python3 src/data_fetch.py
That's it. It will print progress messages and save a CSV file into the
data/ folder.
"""

# ---------------------------------------------------------------------------
# SECTION 1: IMPORTS
# ---------------------------------------------------------------------------
# "import" brings in code that other people already wrote, so we don't have
# to write everything from scratch. Think of it like plugging in a tool.

import yfinance as yf   # the library that talks to Yahoo Finance for us
import pandas as pd     # the library for working with tables of data ("DataFrames")
from pathlib import Path  # a clean way to handle file paths across Mac/Windows/Linux
from datetime import datetime, timedelta  # for working with dates and times


# ---------------------------------------------------------------------------
# SECTION 2: SETTINGS
# ---------------------------------------------------------------------------
# Putting all the "knobs you might want to turn" in one place near the top
# is a common Python convention. If you want to change something later
# (like which symbol to pull, or how many days of history), you change it
# HERE, not buried deep in the code below.

TICKER = "NQ=F"          # Yahoo Finance's symbol for continuous front-month NQ futures
INTERVAL = "1m"           # "1m" = 1-minute bars. Other options: "5m", "15m", "1h", "1d"
LOOKBACK_DAYS = 59        # Yahoo only allows ~60 days of history at 1-minute resolution
NY_TIMEZONE = "America/New_York"  # we care about NY time because that's when NQ trades on the CME and 8:30 AM ET is the cash market open time we're focused on

# This figures out where to save the file. Path(__file__) means "the file
# you are reading right now." .parent means "the folder that contains it"
# (src/). .parent again means "the folder containing THAT" (the project
# root). Then we go into the data/ folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)  # create the data/ folder if it doesn't already exist


def fetch_nq_minute_data() -> pd.DataFrame:
    """
    Downloads recent 1-minute NQ futures bars from Yahoo Finance.

    A "DataFrame" (the pd.DataFrame in the type hint above) is the core
    data structure in the pandas library -- think of it as a spreadsheet
    inside Python: rows and columns, with labels. Every price bar
    (timestamp, open, high, low, close, volume) will be one row.

    Returns:
        A pandas DataFrame with columns: Open, High, Low, Close, Volume,
        indexed by timestamp (in New York time).
    """
    print(f"Downloading {LOOKBACK_DAYS} days of {INTERVAL} bars for {TICKER}...")

    # yf.download() is the main function of the yfinance library. We give
    # it a symbol, an interval, and a period, and it hands back a DataFrame.
    df = yf.download(
        tickers=TICKER,
        period=f"{LOOKBACK_DAYS}d",
        interval=INTERVAL,
        progress=False,       # don't print yfinance's own progress bar
        auto_adjust=False,    # futures don't need dividend/split adjustment
    )

    if df.empty:
        # This is a "guard clause" -- checking for a problem early and
        # failing loudly with a clear message, instead of silently
        # continuing with broken/empty data.
        raise RuntimeError(
            "No data came back from Yahoo Finance. Possible causes: "
            "no internet connection, Yahoo is rate-limiting us, or the "
            "market has been closed long enough that there's nothing new."
        )

    # yfinance sometimes returns "MultiIndex" columns (a fancier table
    # shape) when you pass certain arguments. This line flattens that back
    # down to simple column names like "Open", "Close", etc. if needed.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # The timestamps yfinance gives us are in UTC (Coordinated Universal
    # Time) or sometimes already tz-aware in the exchange's timezone,
    # depending on version. We explicitly convert to New York time so that
    # "8:30 AM" in our data always means 8:30 AM New York time, regardless
    # of daylight saving changes. This step matters a lot -- getting
    # timezones wrong is one of the most common (and dangerous) bugs in
    # trading research code.
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df.index = df.index.tz_convert(NY_TIMEZONE)
    df.index.name = "timestamp_ny"

    return df


def save_to_csv(df: pd.DataFrame) -> Path:
    """
    Saves the DataFrame to a CSV file with today's date in the filename,
    so each day you run this you get a fresh snapshot instead of silently
    overwriting old data.

    "CSV" = Comma-Separated Values, a plain-text spreadsheet format that
    Excel, Python, and basically every data tool can open.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_path = DATA_DIR / f"NQ_1min_{today_str}.csv"
    df.to_csv(out_path)
    return out_path


def main():
    """
    This is the function that actually runs when you execute this file
    directly (see the "if __name__ ..." block at the very bottom). Keeping
    the "do the work" logic in a main() function is a common Python
    pattern that makes the code easier to test and reuse later.
    """
    df = fetch_nq_minute_data()

    print(f"Got {len(df)} rows.")
    print(f"Date range: {df.index.min()}  to  {df.index.max()}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nLast 5 rows:")
    print(df.tail())

    out_path = save_to_csv(df)
    print(f"\nSaved to: {out_path}")


# This funny-looking line is a Python convention. It means: "only run
# main() if this file is being run directly (like `python3 data_fetch.py`),
# not if some other file imports this one to reuse its functions." It lets
# us safely reuse fetch_nq_minute_data() from other scripts later without
# it printing a bunch of stuff or re-saving files.
if __name__ == "__main__":
    main()
