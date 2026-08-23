"""
data_fetch_databento.py
=========================

WHAT THIS FILE DOES (plain English):
Downloads REAL 1-minute NQ futures bars from Databento (a paid market
data vendor), from a FIXED start date (2015-01-01, extended 2026-08-20
-- see below) through today, and saves them to data/, in the same format
the rest of the pipeline (detect_setups.py, detect_level_sweep.py,
backtest.py, ...) already expects. This is a step up from
data_fetch.py (Yahoo Finance), which only gives ~30 days of 1-minute
history -- Databento gives us a much longer, better-quality window to
backtest against.

FIXED START DATE, NOT A ROLLING WINDOW (fixed 2026-08-20): this used to
request a rolling "LOOKBACK_DAYS back from today" window. That silently
eroded the research portion of the data every time this script was
re-run: as "today" advanced, the window's start date rolled forward
too, dropping the oldest days entirely (they never come back, since the
holdout boundary in data_holdout.py absorbs every new day going forward
instead). A real-world re-run on 2026-08-20 caught this: research days
dropped from 513 to 510 in one pull. Fixed by anchoring HISTORY_START_DATE
at a fixed calendar date instead of computing it from "today" -- every
re-run requests HISTORY_START_DATE through today, growing forward over
time, never dropping days off the front.

HISTORY EXTENDED TO 2015-01-01 (2026-08-20, per
docs/RESEARCH_INTEGRITY_PROTOCOL.md's data acquisition step): before
extending, cost was quoted via metadata.get_cost() ($14.42 for
2015-01-01 through today, confirmed proportionate to earlier 5yr/max-
lookback estimates, not an anomaly -- Jason approved spending it), and
a manual data-quality spot check pulled sample days from 2011, 2015, and
2019 to compare gap rates, price sanity, and rollover-splice cleanliness
across eras. 2015 was the quality floor chosen: full weekday coverage,
~91% minute-level coverage in the 8:30-10:00 NY watch window (vs only
~17.5% in 2011 -- too sparse for this project's minute-by-minute
detection logic), sane era-appropriate price levels, and a clean
(if unadjusted) rollover splice. 2011-2014 was deliberately left out on
quality grounds, not cost grounds.

FETCHED IN YEARLY CHUNKS, NOT ONE REQUEST (2026-08-20): the first
attempt at this 2015-01-01 pull was one single ~11.6-year request, which
stalled against Databento's API for hours (confirmed genuinely stuck via
an active-but-flatlined TCP connection, not just slow). Fixed by
requesting one calendar year at a time instead -- see
fetch_databento_minute_data()'s docstring for how caching/resuming
works. HISTORY_START_DATE itself is unchanged; this only changed how the
request gets batched.

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
HISTORY_START_DATE = datetime(2015, 1, 1)  # FIXED anchor, not a rolling lookback -- see file header.
                                             # Extended from 2024-08-15 to 2015-01-01 on 2026-08-20 after
                                             # a cost quote ($14.42, approved) and a manual data-quality
                                             # spot check confirmed 2015+ is clean (2011-2014 was excluded
                                             # on quality grounds -- see file header). Never derive this
                                             # from "today" -- that's exactly the bug this constant fixes.
NY_TIMEZONE = "America/New_York"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
KEY_FILE = PROJECT_ROOT / ".databento_key"
CHUNK_CACHE_DIR = DATA_DIR / "_databento_yearly_chunks"  # temporary per-year cache, see fetch_databento_minute_data()


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
    Downloads 1-minute NQ futures bars from Databento's historical API,
    from the fixed HISTORY_START_DATE through today -- fetched in YEARLY
    CHUNKS, not one single request.

    WHY CHUNKED (2026-08-20): a single request spanning the full history
    (2015-01-01 through today, ~11.6 years at the time this was added)
    stalled against Databento's API -- confirmed genuinely stuck, not
    just slow, via an active-but-flatlined TCP connection over several
    hours. Splitting into one request per calendar year is dramatically
    more reliable, matches the same per-request-chunking pattern
    data_fetch.py already uses for Yahoo's per-request limits, and (via
    the on-disk cache below) means a failure in one year doesn't cost
    re-fetching every year before it.

    Each year's raw chunk is cached to CHUNK_CACHE_DIR immediately after
    a successful fetch. Re-running this script skips any year that's
    already cached, so a failure partway through can be fixed and
    re-run without re-paying for or re-waiting on already-fetched years.
    The cache is deleted only after everything is successfully combined
    and saved to the final CSV.

    Returns a DataFrame with columns Open, High, Low, Close, Volume,
    indexed by timestamp in New York time -- matching the exact shape
    data_fetch.py (the Yahoo Finance version) already produces, so every
    downstream script (detect_setups.py, backtest.py, etc.) works with
    this data without any changes.
    """
    end = datetime.now()
    start = HISTORY_START_DATE
    CHUNK_CACHE_DIR.mkdir(exist_ok=True)

    print(f"Requesting {SCHEMA} bars for {SYMBOL} ({DATASET}) from "
          f"{start.date()} (fixed) to {end.date()} (today), in yearly chunks...")
    print("(This calls Databento's paid historical API and will use credits/"
          "billing on your account.)")

    client = db.Historical(key=api_key)

    raw_chunks = []
    year = start.year
    while datetime(year, 1, 1) < end:
        chunk_start = max(start, datetime(year, 1, 1))
        chunk_end = min(end, datetime(year + 1, 1, 1))
        cache_path = CHUNK_CACHE_DIR / f"{year}.csv"

        if cache_path.exists():
            print(f"  {year}: using cached chunk ({cache_path.name}), not re-fetching.")
            chunk_df = pd.read_csv(cache_path, index_col=0, parse_dates=[0])
        else:
            print(f"  {year}: fetching {chunk_start.date()} to {chunk_end.date()}...")
            try:
                # stype_in="continuous" tells Databento that SYMBOL is a
                # continuous-contract symbol (NQ.c.0) rather than one
                # specific expiring contract code (like NQZ6) -- this is
                # what gives us one unbroken price series.
                data = client.timeseries.get_range(
                    dataset=DATASET,
                    symbols=[SYMBOL],
                    schema=SCHEMA,
                    stype_in="continuous",
                    start=chunk_start.strftime("%Y-%m-%d"),
                    end=chunk_end.strftime("%Y-%m-%d"),
                )
            except Exception as e:
                raise RuntimeError(
                    f"Fetch FAILED on the {year} chunk ({chunk_start.date()} to "
                    f"{chunk_end.date()}): {e}. Years fetched before this one are "
                    f"already cached in {CHUNK_CACHE_DIR} -- fix the issue and "
                    f"re-run; this script will skip them and only retry {year} "
                    f"onward."
                ) from e
            chunk_df = data.to_df()
            if not chunk_df.empty:
                chunk_df.to_csv(cache_path)
            print(f"    Got {len(chunk_df)} rows for {year}.")

        if not chunk_df.empty:
            raw_chunks.append(chunk_df)
        year += 1

    if not raw_chunks:
        raise RuntimeError(
            "No data came back from Databento across any yearly chunk. "
            "Possible causes: your API key doesn't have access to the "
            "GLBX.MDP3 dataset, your plan/trial doesn't cover this date "
            "range, or there's a symbol/schema mismatch."
        )

    df = pd.concat(raw_chunks).sort_index()
    df = df[~df.index.duplicated(keep="first")]  # in case adjacent year boundaries overlapped

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


def clear_chunk_cache():
    """Deletes the per-year chunk cache -- only called after the final
    combined CSV has been saved successfully, so a mid-run failure never
    loses already-fetched years."""
    if CHUNK_CACHE_DIR.exists():
        for f in CHUNK_CACHE_DIR.glob("*.csv"):
            f.unlink()
        CHUNK_CACHE_DIR.rmdir()


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

    clear_chunk_cache()
    print("Cleared the per-year chunk cache (everything combined successfully).")


if __name__ == "__main__":
    main()
