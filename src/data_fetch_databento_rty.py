"""
data_fetch_databento_rty.py
=============================

WHAT THIS FILE DOES (plain English):
Downloads REAL 1-minute RTY (E-mini Russell 2000) futures bars from
Databento, covering EXACTLY the same Discovery-slice date range as
NQ/ES (2015-01-01 through 2021-10-03 inclusive) -- see
research/mechanisms/letf-close-rebalance-m13.md and
research/mechanisms/hedging-demand-gamma-regime-m14.md, both of which
are DRAWABLE but parked pending this instrument (and ES, already
scripted in data_fetch_databento_es.py).

UNLIKE data_fetch_databento_es.py, NO price has been pre-quoted-and-
approved for RTY yet as of this writing (2026-09-13). This script
prints the real metadata.get_cost() number to the console (and logs it
to data/_databento_cost_log.json, same running log NQ/ZN/6E/CL use)
BEFORE fetching, and PAUSES for a y/N confirmation before spending
anything -- unlike the cross-asset script's collapsed "quote, log,
fetch" sequence (that one had blanket advance authorization; this one
does not, so it defaults back to this project's usual "quote, then
sign-off, then fetch" three-step discipline).

WHERE THE DATA COMES FROM: same dataset/mechanics as every other pull
in this project -- "GLBX.MDP3" (CME Globex's own feed), continuous
front-month symbol ("RTY.c.0", same ".c.0" calendar-roll convention),
"ohlcv-1m" schema.

OUTPUT FILE NAMING: saved as RTY_1min_databento_<date>.csv, matching
the ES/ZN/6E/CL naming convention -- not picked up automatically by
any single-instrument script, loaded explicitly once M13/M14 are drawn.

ABOUT YOUR API KEY: identical handling to data_fetch_databento.py --
reuses get_api_key() from it unmodified.

HOW TO RUN (from a machine with working network access to Databento --
confirmed blocked from both this project's cloud environment and its
device-bridged shell; must be run from a normal Terminal on Jason's Mac):
    python3 src/data_fetch_databento_rty.py
"""

import pandas as pd
import databento as db
from pathlib import Path
from datetime import datetime

from data_fetch_databento import get_api_key, NY_TIMEZONE, log_cost_entry

DATASET = "GLBX.MDP3"
SYMBOL = "RTY.c.0"             # continuous front-month RTY, same .c.0 convention as NQ.c.0/ES.c.0
SCHEMA = "ohlcv-1m"
HISTORY_START_DATE = datetime(2015, 1, 1)
HISTORY_END_DATE = datetime(2021, 10, 4)   # FIXED, exclusive -- matches ES's Discovery-slice
                                             # range exactly, since M13/M14 are Discovery-only
                                             # tests. Extend only with a fresh quote/approval.

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
CHUNK_CACHE_DIR = DATA_DIR / "_databento_yearly_chunks_rty"


def quote_full_range_cost(api_key: str) -> float:
    """Live cost quote for the WHOLE range in one call (not per-year --
    this is just a number, not a fetch, so there's no stall risk the
    yearly chunking was built to avoid). Logged immediately so there is
    a record even if the user declines to proceed."""
    client = db.Historical(key=api_key)
    cost = client.metadata.get_cost(
        dataset=DATASET,
        symbols=[SYMBOL],
        schema=SCHEMA,
        stype_in="continuous",
        start=HISTORY_START_DATE.strftime("%Y-%m-%d"),
        end=HISTORY_END_DATE.strftime("%Y-%m-%d"),
    )
    log_cost_entry(cost, HISTORY_START_DATE, HISTORY_END_DATE, symbol=SYMBOL, dataset=DATASET, schema=SCHEMA)
    return cost


def fetch_databento_rty_minute_data(api_key: str) -> pd.DataFrame:
    """Same yearly-chunked-fetch-with-caching pattern as the ES script."""
    end = HISTORY_END_DATE
    start = HISTORY_START_DATE
    CHUNK_CACHE_DIR.mkdir(exist_ok=True)

    print(f"Requesting {SCHEMA} bars for {SYMBOL} ({DATASET}) from "
          f"{start.date()} to {end.date()} (fixed, Discovery-slice range), "
          f"in yearly chunks...")

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
    out_path = DATA_DIR / f"RTY_1min_databento_{today_str}.csv"
    df.to_csv(out_path)
    return out_path


def main():
    api_key = get_api_key()

    print("Getting a live cost quote before spending anything...")
    cost = quote_full_range_cost(api_key)
    print(f"\nQuoted cost for RTY, {HISTORY_START_DATE.date()} -> {HISTORY_END_DATE.date()}: ${cost:.4f}")
    answer = input("Proceed with this purchase? [y/N]: ").strip().lower()
    if answer != "y":
        print("Not proceeding. No data fetched, no additional charge beyond this quote lookup "
              "(Databento does not charge for cost quotes, only for actual data pulls).")
        return

    df = fetch_databento_rty_minute_data(api_key)

    print(f"\nGot {len(df)} rows.")
    print(f"Date range: {df.index.min()}  to  {df.index.max()}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nLast 5 rows:")
    print(df.tail())

    out_path = save_to_csv(df)
    print(f"\nSaved to: {out_path}")
    print("This is REAL Databento data (CME Globex GLBX.MDP3 feed) for RTY, "
          "covering the Discovery-period range.")

    clear_chunk_cache()
    print("Cleared the per-year chunk cache (everything combined successfully).")


if __name__ == "__main__":
    main()
