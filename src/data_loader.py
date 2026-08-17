"""
data_loader.py
================

WHAT THIS FILE DOES (plain English):
One shared place to "find and load the current real price data file."
Before 2026-08-16 this exact logic -- find the data/NQ_1min_*.csv files,
prefer the latest real one over synthetic, parse timestamps safely
across a Daylight Saving Time change, and apply the research/holdout
boundary -- was copy-pasted nearly identically across five different
scripts (detect_setups.py, detect_level_sweep.py, backtest.py,
plot_open.py, plot_setup_example.py). That meant fixing a bug in it (as
happened twice already -- the DST timestamp bug, then adding the holdout
boundary) meant editing five files and hoping none got missed.
Consolidated here per docs/RESEARCH_ARCHITECTURE.md's architecture
review, recommendation #2.

HOW TO USE:
    from data_loader import load_price_data
    df, is_synthetic = load_price_data(context="my_script.py")

`context` is just a short label (usually the calling script's name) used
in the console messages printed by the holdout boundary check, so it's
obvious which script excluded how much data.
"""

import pandas as pd
from pathlib import Path
from data_holdout import apply_holdout_boundary

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def list_data_files() -> list[Path]:
    """All NQ_1min_*.csv files currently on disk, sorted by filename."""
    return sorted(DATA_DIR.glob("NQ_1min_*.csv"))


def find_active_data_file() -> Path:
    """The file the pipeline actually uses: the most recent REAL
    (non-synthetic) file if one exists, otherwise the most recent
    synthetic one. Every script in this project that uses "the current
    data" means whatever this function picks."""
    candidates = list_data_files()
    if not candidates:
        raise FileNotFoundError(
            "No data file found in data/. Run data_fetch.py, "
            "data_fetch_databento.py, or generate_sample_data.py first."
        )
    real_files = [c for c in candidates if "SYNTHETIC" not in c.name]
    return real_files[-1] if real_files else candidates[-1]


def read_price_csv(path: Path) -> pd.DataFrame:
    """Reads one price CSV with DST-safe timestamp parsing. A plain
    pd.read_csv(..., parse_dates=True) silently fails to parse timestamps
    correctly when a file's date range spans a Daylight Saving Time
    change (mixed UTC offsets, e.g. -05:00 in February vs -04:00 in
    August) -- this handles that by parsing as UTC first, then
    converting to New York time."""
    df = pd.read_csv(path, index_col="timestamp_ny")
    df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York")
    return df


def load_price_data(context: str = "", apply_holdout: bool = True) -> tuple[pd.DataFrame, bool]:
    """Finds the active data file, loads it, and -- for real data, unless
    apply_holdout=False is explicitly passed -- restricts it to the
    research portion via data_holdout.py's fixed boundary. This is what
    every script that needs price data should call.

    Returns (df, is_synthetic).
    """
    chosen = find_active_data_file()
    print(f"Loading: {chosen.name}")
    df = read_price_csv(chosen)
    is_synthetic = "SYNTHETIC" in chosen.name
    if not is_synthetic and apply_holdout:
        df = apply_holdout_boundary(df, context=context)
    return df, is_synthetic
