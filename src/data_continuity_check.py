"""
data_continuity_check.py -- verifies that a refreshed NQ 1-minute file is the
OLD file plus new bars, and nothing else.

Why this exists (2026-09-14, data-refresh queue item): Jason approved keeping
the NQ series current (Sept 8th -> current, then ongoing). Every promoted
result in this project was computed on the sealed slices of the old file, so
a refresh must never alter a single historical bar. This check is Tony's
owed action after each pull: "confirm the file landed, verify continuity
with the existing series".

Checks (FAIL stops the pipeline; WARN is reported, not fatal):
  1. schema      -- same columns, same index name (timestamp_ny)
  2. monotone    -- new index strictly increasing, no duplicate timestamps
  3. superset    -- every old timestamp is present in the new file
  4. identical   -- every old bar's OHLCV is bit-for-bit unchanged
  5. extends     -- the new file ends strictly after the old one
  6. junction    -- gap between old last bar and first new bar <= 72h
                    (a weekend) and the price step across it < 5%
  7. thin (WARN) -- any new weekday session with < 50% of the old file's
                    median weekday bar count (a partial current day is
                    expected and is why this is a warning)

Usage:
    python3 src/data_continuity_check.py OLD.csv NEW.csv
Exit code 0 on PASS, 1 on any FAIL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from data_loader import read_price_csv  # noqa: E402

COLS = ["Open", "High", "Low", "Close", "Volume"]
MAX_JUNCTION_HOURS = 72
MAX_JUNCTION_PRICE_STEP = 0.05
THIN_SESSION_FRACTION = 0.50


def check_continuity(old: pd.DataFrame, new: pd.DataFrame) -> dict:
    """Pure function over two already-loaded frames (see read_price_csv).
    Returns {"status": PASS|FAIL, "checks": [...], "n_old", "n_new", "n_added"}."""
    checks = []

    def add(name, ok, note="", warn=False):
        checks.append({"check": name, "status": ("WARN" if warn else "FAIL") if not ok else "PASS", "note": note})

    add("1. schema", list(old.columns) == list(new.columns) and new.index.name == old.index.name,
        f"old={list(old.columns)} new={list(new.columns)}")
    add("2. monotone, unique", bool(new.index.is_monotonic_increasing and new.index.is_unique),
        f"{int(new.index.duplicated().sum())} duplicate timestamps")
    missing = old.index.difference(new.index)
    add("3. old timestamps all present", len(missing) == 0, f"{len(missing)} old bars missing from new file")
    if len(missing) == 0:
        common = new.loc[old.index, COLS].to_numpy(dtype=float)
        same = np.array_equal(common, old[COLS].to_numpy(dtype=float), equal_nan=True)
        n_diff = 0 if same else int((~np.isclose(common, old[COLS].to_numpy(dtype=float), equal_nan=True)).any(axis=1).sum())
        add("4. old bars unchanged", same, f"{n_diff} old bars differ")
    else:
        add("4. old bars unchanged", False, "not evaluable -- old bars missing")
    old_last = old.index[-1]
    added = new[new.index > old_last]
    add("5. extends past old end", len(added) > 0,
        f"old ends {old_last}, new ends {new.index[-1]}, {len(added)} bars added")
    if len(added) > 0:
        gap_h = (added.index[0] - old_last).total_seconds() / 3600
        step = abs(float(added["Open"].iloc[0]) - float(old["Close"].iloc[-1])) / float(old["Close"].iloc[-1])
        add("6. junction", gap_h <= MAX_JUNCTION_HOURS and step < MAX_JUNCTION_PRICE_STEP,
            f"gap {gap_h:.1f}h, price step {step:.3%}")
        old_days = old.groupby(old.index.date).size()
        old_wd = old_days[[pd.Timestamp(d).weekday() < 5 for d in old_days.index]]
        median = float(old_wd.tail(250).median()) if len(old_wd) else 0.0
        new_days = added.groupby(added.index.date).size()
        thin = [(str(d), int(n)) for d, n in new_days.items()
                if pd.Timestamp(d).weekday() < 5 and median and n < THIN_SESSION_FRACTION * median]
        add("7. thin new sessions", len(thin) == 0,
            f"{thin} vs median weekday {median:.0f} bars" if thin else f"{len(new_days)} new session(s), median weekday {median:.0f} bars",
            warn=True)
    status = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    return {"status": status, "checks": checks, "n_old": int(len(old)), "n_new": int(len(new)),
            "n_added": int(len(added)), "old_end": str(old_last), "new_end": str(new.index[-1])}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    old, new = read_price_csv(Path(argv[0])), read_price_csv(Path(argv[1]))
    res = check_continuity(old, new)
    print(json.dumps(res, indent=2))
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
