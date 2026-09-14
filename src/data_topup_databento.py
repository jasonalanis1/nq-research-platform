"""
data_topup_databento.py -- INCREMENTAL top-up of the NQ 1-minute series.

Approved by Jason 2026-09-14 (queue item "Data refresh approved; execution
record begins"): NQ 1-minute bars, GLBX.MDP3, NQ.c.0, from where the file on
disk ends through today, then kept current going forward. Estimated $5-15
against the untouched $20/month cap. This is the OPERATING-COST purchase --
NOT the NO PURCHASE decision on new instruments / order-flow data, which
stands.

RUN FROM JASON'S OWN TERMINAL (the sandboxed shells cannot reach
hist.databento.com):

    cd ~/Documents/nq-research-platform-live && python3 src/data_topup_databento.py

What it does, in order:
  1. finds the active NQ file (data_loader.find_active_data_file) and its
     last bar; start = last bar + 1 minute (UTC), end = now (UTC)
  2. QUOTES the exact cost with metadata.get_cost (buys nothing yet)
  3. REFUSES if the quote exceeds --cap (default $15.00, the top of the
     approved estimate) -- exits 3 with the quote printed
  4. fetches, converts to the pipeline's schema (timestamp_ny,Open,High,
     Low,Close,Volume), MERGES onto the old series (old bars win on any
     overlap), writes data/NQ_1min_databento_<end date>.csv -- a NEW file;
     the old file is never modified, and data_loader picks the newest
  5. logs the REAL quoted cost to data/_databento_cost_log.json
  6. runs data_continuity_check on old vs new and exits 1 if it fails

--quote-only prints step 2 and stops. --cap raises/lowers the refusal line.
Never prints the API key.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from data_loader import DATA_DIR, find_active_data_file, read_price_csv  # noqa: E402
from data_fetch_databento import DATASET, SCHEMA, SYMBOL, NY_TIMEZONE, get_api_key, log_cost_entry  # noqa: E402
from data_continuity_check import check_continuity  # noqa: E402

DEFAULT_CAP_USD = 15.00
COLS = ["Open", "High", "Low", "Close", "Volume"]


def topup_window(old: pd.DataFrame, now_utc: dt.datetime | None = None) -> tuple[dt.datetime, dt.datetime]:
    """start = one minute after the old file's last bar (UTC, tz-naive);
    end = now, floored to the minute. Both tz-naive UTC for the API."""
    last_utc = old.index[-1].tz_convert("UTC").to_pydatetime().replace(tzinfo=None)
    start = last_utc + dt.timedelta(minutes=1)
    end = (now_utc or dt.datetime.utcnow()).replace(second=0, microsecond=0)
    if end <= start:
        raise SystemExit(f"nothing to top up: file already ends {old.index[-1]}")
    return start, end


def to_pipeline_frame(raw: pd.DataFrame) -> pd.DataFrame:
    """Databento to_df() (UTC index, lowercase columns) -> the pipeline's shape."""
    out = pd.DataFrame({c: raw[c.lower()] for c in COLS})
    if out.index.tz is None:
        out.index = out.index.tz_localize("UTC")
    out.index = out.index.tz_convert(NY_TIMEZONE)
    out.index.name = "timestamp_ny"
    return out.sort_index()


def merge(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Old bars are authoritative on any overlap; only bars strictly after
    the old end are appended."""
    added = new[new.index > old.index[-1]]
    merged = pd.concat([old, added]).sort_index()
    return merged[~merged.index.duplicated(keep="first")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=DEFAULT_CAP_USD, help="refuse above this quoted cost (USD)")
    ap.add_argument("--quote-only", action="store_true")
    args = ap.parse_args(argv)

    import databento as db  # imported here so the pure helpers stay testable without it

    old_path = find_active_data_file("NQ")
    old = read_price_csv(old_path)
    start, end = topup_window(old)
    print(f"Active file: {old_path.name} (ends {old.index[-1]})")
    print(f"Top-up window (UTC): {start} -> {end}")

    client = db.Historical(key=get_api_key())
    quote = float(client.metadata.get_cost(dataset=DATASET, symbols=[SYMBOL], schema=SCHEMA,
                                           stype_in="continuous", start=start, end=end))
    print(f"Quoted cost: ${quote:.4f} (cap ${args.cap:.2f})")
    if args.quote_only:
        return 0
    if quote > args.cap:
        print(f"REFUSED: quote ${quote:.2f} exceeds cap ${args.cap:.2f}. Nothing purchased. "
              f"Re-run with --cap if Jason raises it.")
        return 3

    raw = client.timeseries.get_range(dataset=DATASET, symbols=[SYMBOL], schema=SCHEMA,
                                      stype_in="continuous", start=start, end=end).to_df()
    log_cost_entry(quote, start, end)
    if raw.empty:
        print("Databento returned 0 rows for the window (cost logged as quoted). Nothing written.")
        return 1
    new = merge(old, to_pipeline_frame(raw))
    out_path = DATA_DIR / f"NQ_1min_databento_{end.date().isoformat()}.csv"
    if out_path == old_path:
        out_path = DATA_DIR / f"NQ_1min_databento_{end.date().isoformat()}b.csv"
    new.to_csv(out_path)
    print(f"Wrote {out_path.name}: {len(new)} rows ({len(new) - len(old)} added), ends {new.index[-1]}")

    res = check_continuity(old, read_price_csv(out_path))
    for c in res["checks"]:
        print(f"  {c['status']:<4} {c['check']}: {c['note']}")
    print(f"Continuity: {res['status']}")
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
