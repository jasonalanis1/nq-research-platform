"""
market_state_primitives_v2.py
================================

Layer 0 extension for Scan 002. Adds the three state descriptors
market_state_primitives.py's docstring listed as "deferred": distance
from session VWAP, volume vs. expected volume, and a VXN-based
cross-market descriptor (VXN daily close level vs its own trailing
average -- the only cross-market series this project has on disk;
ES per-contract data is not available, so a true ES/NQ relationship
stays deferred). Also adds a non-tercile (quintile) discretization of
directional_persistence, per the KNOWN UNEXPLORED LEARN bucket.

All descriptors use only information known as of the state day's open
(prior-day facts, or trailing/shifted windows) -- no lookahead.

HOW TO USE:
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame
    states = extend_state_frame(build_state_frame(df), df)
"""

from pathlib import Path

import numpy as np
import pandas as pd

from detect_vwap_reversion import compute_session_vwap_bands

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VOLUME_LOOKBACK_DAYS = 20
VXN_LOOKBACK_DAYS = 20
VXN_PATH = DATA_DIR / "VXNCLS_MAX.csv"


def _rth_volume_and_close_vwap_dist_by_day(df: pd.DataFrame, atr_by_day: pd.Series) -> tuple[dict, dict]:
    """Per RTH day: total RTH volume, and the RTH reference close's
    distance from that day's own session VWAP (ATR-normalized)."""
    volume_out = {}
    vwap_dist_out = {}
    idx = df.index
    for day, day_df in df.groupby(idx.date):
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty or "Volume" not in rth.columns:
            continue
        volume_out[day] = float(rth["Volume"].sum())
        bands = compute_session_vwap_bands(rth)
        if bands.empty:
            continue
        last_vwap = float(bands["vwap"].iloc[-1])
        last_close = float(rth["Close"].iloc[-1])
        atr = atr_by_day.get(day, np.nan)
        if pd.isna(atr) or atr <= 0:
            continue
        vwap_dist_out[day] = (last_close - last_vwap) / atr
    return volume_out, vwap_dist_out


def _load_vxn_daily() -> pd.Series:
    vxn = pd.read_csv(VXN_PATH, parse_dates=["observation_date"])
    vxn = vxn.dropna(subset=["VXNCLS"])
    vxn = vxn.set_index(vxn["observation_date"].dt.date)["VXNCLS"].astype(float)
    return vxn.sort_index()


def extend_state_frame(states: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """Adds volume_vs_expected, vwap_dist_vs_atr, vxn_level_vs_trailing,
    and directional_persistence_quintile to an existing v1 state frame
    (from market_state_primitives.build_state_frame). Every new column
    is a PRIOR-day fact shifted into today's state (known at today's
    open) except vwap_dist_vs_atr, which -- like opening_range_vs_atr
    in v1 -- is a same-day-known-by-close descriptor, usable only for
    same-day/afternoon conditional analysis, not pre-open."""
    out = states.copy()

    volume_by_day, vwap_dist_by_day = _rth_volume_and_close_vwap_dist_by_day(df, out["atr14"])
    volume_series = pd.Series(volume_by_day).reindex(out.index)
    trailing_avg_volume = volume_series.rolling(VOLUME_LOOKBACK_DAYS, min_periods=VOLUME_LOOKBACK_DAYS).mean().shift(1)
    out["volume_vs_expected"] = (volume_series.shift(1) / trailing_avg_volume) - 1.0  # prior day's volume vs its own trailing expectation
    out["vwap_dist_vs_atr"] = pd.Series(vwap_dist_by_day).reindex(out.index)  # same-day, known by close

    vxn = _load_vxn_daily()
    vxn_reindexed = vxn.reindex(out.index, method="ffill")  # FRED VXN has occasional gaps -- carry forward last known level
    vxn_trailing_avg = vxn_reindexed.rolling(VXN_LOOKBACK_DAYS, min_periods=VXN_LOOKBACK_DAYS).mean().shift(1)
    vxn_prior = vxn_reindexed.shift(1)
    out["vxn_level_vs_trailing"] = (vxn_prior / vxn_trailing_avg) - 1.0

    # Non-tercile (quintile) cut of the existing directional_persistence
    # descriptor -- same underlying variable, finer discretization, per
    # the KNOWN UNEXPLORED LEARN bucket.
    valid = out["directional_persistence"].notna()
    if valid.sum() >= 25:
        out["directional_persistence_quintile"] = pd.qcut(
            out.loc[valid, "directional_persistence"], q=5, labels=False, duplicates="drop"
        )
    else:
        out["directional_persistence_quintile"] = np.nan

    return out
