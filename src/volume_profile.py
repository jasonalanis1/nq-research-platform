"""
volume_profile.py
==================

Infrastructure module -- frozen spec:
research/studies/volume-profile-infra-spec.md. Approximates a session's
Point of Control (POC) and Value Area High/Low (VAH/VAL) from 1-minute
OHLCV bars (no tick/order-book data available), using the standard
70%-of-volume convention. Reused unmodified by observatory_v6.py and
any future value-area-based study.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

BUCKET_SIZE_POINTS = 1.0
VALUE_AREA_FRACTION = 0.70


def build_daily_volume_profile(rth_day_df: pd.DataFrame) -> dict | None:
    """rth_day_df: one day's RTH (09:30-16:00) 1-minute bars, with
    High/Low/Close/Volume columns. Returns None if empty or no volume."""
    if rth_day_df.empty:
        return None
    typical = (rth_day_df["High"] + rth_day_df["Low"] + rth_day_df["Close"]) / 3.0
    volume = rth_day_df["Volume"]
    total_volume = float(volume.sum())
    if total_volume <= 0:
        return None

    bucket = (typical / BUCKET_SIZE_POINTS).round() * BUCKET_SIZE_POINTS
    profile = volume.groupby(bucket).sum().sort_index()
    if profile.empty:
        return None

    poc_price = float(profile.idxmax())
    poc_idx = profile.index.get_loc(poc_price)
    prices = profile.index.to_numpy()
    vols = profile.to_numpy()

    captured = float(vols[poc_idx])
    lo, hi = poc_idx, poc_idx
    target = VALUE_AREA_FRACTION * total_volume
    while captured < target and (lo > 0 or hi < len(vols) - 1):
        add_lo = float(vols[lo - 1]) if lo > 0 else -1.0
        add_hi = float(vols[hi + 1]) if hi < len(vols) - 1 else -1.0
        if add_hi >= add_lo:
            hi += 1
            captured += add_hi
        else:
            lo -= 1
            captured += add_lo

    return {
        "poc": poc_price,
        "vah": float(prices[hi]),
        "val": float(prices[lo]),
        "total_volume": total_volume,
        "value_area_volume_fraction": captured / total_volume,
    }
