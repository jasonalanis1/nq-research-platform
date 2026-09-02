"""
data_fetch_databento_es.py
=============================

WHAT THIS FILE DOES (plain English):
Downloads REAL 1-minute ES (E-mini S&P 500) futures bars from
Databento, covering EXACTLY the same date range as NQ's Discovery
slice (2015-01-01 through 2021-10-03 inclusive) -- not the full
2015-through-today history data_fetch_databento.py pulls for NQ.

WHY THE DATE RANGE IS DELIBERATELY LIMITED AND FIXED (2026-09-02): this
script exists to acquire exactly what was quoted and approved, nothing
more. Per research/studies/es-cross-market-feasibility.md, the live
Databento cost quote for ES at this exact range (GLBX.MDP3, ES.c.0,
ohlcv-1m, 2015-01-01 -> 2021-10-04 exclusive) was $8.351282700896,
confirmed by Jason running metadata.get_cost() from his own machine
after this project's sandboxed environments were both blocked from
reaching Databento's API. Jason then explicitly authorized "the
purchase" in response to that specific number. Pulling more than this
range -- e.g. extending to match NQ's full 2015-2026 history -- would
cost more than what was quoted and approved, so HISTORY_END_DATE here
is a FIXED, explicit boundary, not an open "through today" pull like
NQ's script. If ES history ever needs extending beyond Discovery, that
requires its own fresh cost quote and its own explicit approval, the
same discipline data_split.py's own DISCOVERY_END_DATE and
data_holdout.py's HOLDOUT_START_DATE already require for boundary
changes -- never an automatic side effect of re-running this script.

WHERE THE DATA COMES FROM: same dataset and mechanics as
data_fetch_databento.py's NQ pull -- "GLBX.MDP3" (CME Globex's own
feed), continuous front-month symbol ("ES.c.0", same ".c.0"
calendar-roll convention already used for "NQ.c.0"), "ohlcv-1m" schema.
Fetched in yearly chunks with per-year on-disk caching, identical
pattern to the NQ script (added there on 2026-08-20 after a single
whole-range request stalled against Databento's API for hours).

OUTPUT FILE NAMING: saved as ES_1min_databento_<date>.csv, deliberately
NOT matching data_loader.py's "NQ_1min_*.csv" glob pattern -- this file
will not be picked up automatically by any existing single-instrument
script. It's meant to be loaded explicitly by name once a specific
cross-market hypothesis is frozen, not silently merged into the
existing NQ-only pipeline.

ABOUT YOUR API KEY: identical handling to data_fetch_databento.py --
see that file's docstring. This script reuses get_api_key() from it
unmodified rather than duplicating the key-handling logic.

HOW TO RUN (from a machine with working network access to Databento --
confirmed blocked from this session's own sandboxed environments):
    python3 src/data_fetch_databento_es.py

This calls Databento's paid historical API and will use the ~$8.35
already quoted and approved for this exact range. It does not
re-confirm the price before pulling -- that confirmation already
happened. If you want a fresh price check first, use the
metadata.get_cost() snippet from the feasibility report instead.
"""

import pandas as pd
import databento as db
from pathlib import Path
from datetime import datetime

from data_fetch_databento import get_api_key, NY_TIMEZONE

DATASET = "GLBX.MDP3"
SYMBOL = "ES.c.0"              # continuous front-month ES, same .c.0 convention as NQ.c.0
SCHEMA = "ohlcv-1m"
HISTORY_START_DATE = datetime(2015, 1, 1)
HISTORY_END_DATE = datetime(2021, 10, 4)   # FIXED, exclusive -- matches exactly what was quoted
                                             # and approved. Do not change without a fresh cost
                                             # quote and explicit approval -- see file header.

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
CHUNK_CACHE_DIR = DATA_DIR / "_databento_yearly_chunks_es"  # separate cache dir from NQ's


def fetch_databento_es_minute_data(api_key: str) -> pd.DataFrame:
    """
    Same yearly-chunked-fetch-with-caching pattern as
    data_fetch_databento.py's fetch_databento_minute_data(), applied to
    ES and bounded by the fixed HISTORY_END_DATE above instead of
    "today". See that function's docstring for why chunking exists.
    """
    end = HISTORY_END_DATE
    start = HISTORY_START_DATE
    CHUNK_CACHE_DIR.mkdir(exist_ok=True)

    print(f"Requesting {SCHEMA} bars for {SYMBOL} ({DATASET}) from "
          f"{start.date()} to {end.date()} (fixed, matching the quoted/approved range), "
          f"in yearly chunks...")
    print("(This calls Databento's paid historical API and will use credits/"
          "billing on your account -- ~$8.35 was quoted and approved for this exact range.)")

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
    df = df[~df.index.duplicated(keep="first")]

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
    if CHUNK_CACHE_DIR.exists():
        for f in CHUNK_CACHE_DIR.glob("*.csv"):
            f.unlink()
        CHUNK_CACHE_DIR.rmdir()


def save_to_csv(df: pd.DataFrame) -> Path:
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_path = DATA_DIR / f"ES_1min_databento_{today_str}.csv"
    df.to_csv(out_path)
    return out_path


def main():
    api_key = get_api_key()
    df = fetch_databento_es_minute_data(api_key)

    print(f"\nGot {len(df)} rows.")
    print(f"Date range: {df.index.min()}  to  {df.index.max()}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nLast 5 rows:")
    print(df.tail())

    out_path = save_to_csv(df)
    print(f"\nSaved to: {out_path}")
    print("This is REAL Databento data (CME Globex GLBX.MDP3 feed) for ES, "
          "covering exactly the quoted/approved Discovery-period range.")

    clear_chunk_cache()
    print("Cleared the per-year chunk cache (everything combined successfully).")


if __name__ == "__main__":
    main()
