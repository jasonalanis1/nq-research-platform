"""
data_fetch_databento_cross_asset.py
======================================

WHAT THIS FILE DOES (plain English):
Downloads REAL 1-minute futures bars for the three new instruments
exp-051's cross-asset basket needs (ZN, 6E, CL), covering EXACTLY the
same Discovery-slice date range as NQ and ES (2015-01-01 through
2021-10-03 inclusive) -- see
research/studies/cross-asset-weekly-trend-scoping.md, Section 4.

WHY ONE SCRIPT FOR THREE INSTRUMENTS, NOT THREE COPIES OF
data_fetch_databento_es.py: this project has already hit (and fixed)
the "same fetch logic copy-pasted across files" problem once before
(see data_loader.py's own docstring, recommendation #2 of the
2026-08-16 architecture review). Three new near-identical files would
repeat that mistake. Instead, this script takes the instrument as a
plain function argument and loops over the three -- same yearly-
chunked-fetch-with-caching mechanics as data_fetch_databento_es.py,
parametrized instead of duplicated.

UNLIKE data_fetch_databento_es.py, NO price was pre-quoted-and-approved
for these three instruments before this script was written. Jason
explicitly authorized proceeding "at any price" (2026-09-07) rather
than reviewing each quote first -- so this script prints the real
metadata.get_cost() number for each instrument to the console (and to
a small JSON log) BEFORE fetching it, for the record, but does not
pause for confirmation before proceeding, per that explicit
authorization. This is a deliberate, disclosed departure from this
project's usual "get the quote, then get sign-off, then fetch" three
step sequence -- collapsed here into "get the quote, log it, fetch"
because Jason already gave the sign-off in advance.

WHERE THE DATA COMES FROM: same dataset/mechanics as the NQ and ES
pulls -- "GLBX.MDP3" (CME Globex's own feed), continuous front-month
symbols, "ohlcv-1m" schema:
  - ZN.c.0  (10-Year Treasury Note futures) -- rates
  - 6E.c.0  (Euro FX futures) -- currency
  - CL.c.0  (WTI Crude Oil futures) -- commodity

OUTPUT FILE NAMING: saved as <SYMBOL_PREFIX>_1min_databento_<date>.csv
(e.g. ZN_1min_databento_2026-09-07.csv), same convention as ES's file
-- not matching data_loader.py's "NQ_1min_*.csv" glob, so these are
loaded explicitly by exp-051's implementation script, not silently
picked up anywhere else.

ABOUT YOUR API KEY: identical handling to data_fetch_databento.py --
reuses get_api_key() from it unmodified. This script CANNOT run to
completion without your Databento API key being either (a) already
saved in the DATABENTO_API_KEY environment variable, (b) already saved
in a `.databento_key` file in the project root, or (c) typed in when
prompted -- this last option requires an interactive terminal (it will
NOT work run non-interactively/unattended, since the hidden-input
prompt has nothing to read from). Run this yourself, directly in your
own Terminal, not through any automated/unattended process.

HOW TO RUN (from your own machine, with a real interactive terminal):
    python3 src/data_fetch_databento_cross_asset.py

This calls Databento's paid historical API three times (once per
instrument) and will incur real, small charges on your account --
expected similarly cheap to ES's $8.35 for the identical date range
based on ES's own quote, but each instrument's real number is printed
before it's fetched, and also written to
data/_databento_cross_asset_cost_log.json for the record.
"""

import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import databento as db

from data_fetch_databento import get_api_key, NY_TIMEZONE

DATASET = "GLBX.MDP3"
SCHEMA = "ohlcv-1m"
HISTORY_START_DATE = datetime(2015, 1, 1)
HISTORY_END_DATE = datetime(2021, 10, 4)  # FIXED, exclusive -- matches NQ/ES Discovery exactly.
                                            # Do not extend without a fresh cost quote and
                                            # explicit approval -- see file header.

# (symbol, output file prefix, plain-English label)
INSTRUMENTS = [
    ("ZN.c.0", "ZN", "10-Year Treasury Note futures (rates)"),
    ("6E.c.0", "6E", "Euro FX futures (currency)"),
    ("CL.c.0", "CL", "WTI Crude Oil futures (commodity)"),
]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
COST_LOG_PATH = DATA_DIR / "_databento_cross_asset_cost_log.json"


def quote_cost(client: "db.Historical", symbol: str) -> float:
    """Real, live metadata.get_cost() quote for this exact instrument/
    date range/schema -- printed and logged before fetching, per the
    module docstring's disclosed departure from the usual
    quote-then-approve-then-fetch sequence."""
    cost = client.metadata.get_cost(
        dataset=DATASET,
        symbols=[symbol],
        schema=SCHEMA,
        stype_in="continuous",
        start=HISTORY_START_DATE.strftime("%Y-%m-%d"),
        end=HISTORY_END_DATE.strftime("%Y-%m-%d"),
    )
    return float(cost)


def fetch_one_instrument(client: "db.Historical", symbol: str, prefix: str, label: str) -> Path:
    """Same yearly-chunked-fetch-with-caching pattern as
    data_fetch_databento_es.py's fetch function, parametrized by
    instrument instead of hardcoded to ES."""
    chunk_cache_dir = DATA_DIR / f"_databento_yearly_chunks_{prefix.lower()}"
    chunk_cache_dir.mkdir(exist_ok=True)

    start, end = HISTORY_START_DATE, HISTORY_END_DATE
    print(f"\n{'=' * 70}")
    print(f"{prefix} -- {label}")
    print(f"{'=' * 70}")

    real_cost = quote_cost(client, symbol)
    print(f"Real Databento cost quote for {symbol} ({start.date()} -> {end.date()}, "
          f"{SCHEMA}): ${real_cost}")

    raw_chunks = []
    year = start.year
    while datetime(year, 1, 1) < end:
        chunk_start = max(start, datetime(year, 1, 1))
        chunk_end = min(end, datetime(year + 1, 1, 1))
        cache_path = chunk_cache_dir / f"{year}.csv"

        if cache_path.exists():
            print(f"  {year}: using cached chunk ({cache_path.name}), not re-fetching.")
            chunk_df = pd.read_csv(cache_path, index_col=0, parse_dates=[0])
        else:
            print(f"  {year}: fetching {chunk_start.date()} to {chunk_end.date()}...")
            try:
                data = client.timeseries.get_range(
                    dataset=DATASET,
                    symbols=[symbol],
                    schema=SCHEMA,
                    stype_in="continuous",
                    start=chunk_start.strftime("%Y-%m-%d"),
                    end=chunk_end.strftime("%Y-%m-%d"),
                )
            except Exception as e:
                raise RuntimeError(
                    f"Fetch FAILED on {symbol}'s {year} chunk ({chunk_start.date()} to "
                    f"{chunk_end.date()}): {e}. Years fetched before this one are already "
                    f"cached in {chunk_cache_dir} -- fix the issue and re-run; this script "
                    f"will skip them and only retry {year} onward."
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
            f"No data came back from Databento for {symbol} across any yearly chunk. "
            f"Possible causes: your API key doesn't have access to the GLBX.MDP3 "
            f"dataset, your plan/trial doesn't cover this date range, or there's a "
            f"symbol/schema mismatch."
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

    today_str = datetime.now().strftime("%Y-%m-%d")
    out_path = DATA_DIR / f"{prefix}_1min_databento_{today_str}.csv"
    out.to_csv(out_path)
    print(f"Got {len(out)} rows. Date range: {out.index.min()} to {out.index.max()}.")
    print(f"Saved to: {out_path}")

    for f in chunk_cache_dir.glob("*.csv"):
        f.unlink()
    chunk_cache_dir.rmdir()

    return out_path, real_cost


def main():
    api_key = get_api_key()
    client = db.Historical(key=api_key)

    cost_log = {}
    if COST_LOG_PATH.exists():
        cost_log = json.loads(COST_LOG_PATH.read_text())

    for symbol, prefix, label in INSTRUMENTS:
        out_path, real_cost = fetch_one_instrument(client, symbol, prefix, label)
        cost_log[prefix] = {
            "symbol": symbol,
            "label": label,
            "quoted_cost_usd": real_cost,
            "fetched_at": datetime.now().isoformat(),
            "output_file": str(out_path),
            "date_range": f"{HISTORY_START_DATE.date()} -> {HISTORY_END_DATE.date()} (exclusive)",
        }

    COST_LOG_PATH.write_text(json.dumps(cost_log, indent=2))
    total = sum(v["quoted_cost_usd"] for v in cost_log.values())
    print(f"\n{'=' * 70}")
    print(f"All 3 instruments fetched. Total quoted cost across all: ${total:.4f}")
    print(f"Per-instrument cost log saved to: {COST_LOG_PATH}")
    print("Next step: exp-051's implementation script can now be built against "
          "these files -- see research/studies/cross-asset-weekly-trend-scoping.md.")


if __name__ == "__main__":
    main()
