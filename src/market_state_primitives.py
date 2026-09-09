"""
market_state_primitives.py
=============================

Layer 0 of the Market Behavior Discovery Engine (frozen spec:
research/infrastructure/market-behavior-discovery-engine-design.md).

WHAT THIS FILE DOES: builds a single daily "market state" frame --
one row per RTH day, one column per state descriptor -- reusing
conventions already validated elsewhere in this project (ATR(14)
normalization, RANGE_LOOKBACK_DAYS trailing-average convention,
build_daily_bars from study_bar_behavior_batch1.py) rather than
re-deriving them. This module computes STATE ONLY -- it does not look
forward, does not compute any return, and is not itself a hypothesis
or a finding. It is the shared input every future Discovery-engine
scan (market_behavior_discovery_scan.py and successors) builds on, the
same role data_loader.py plays for raw price data.

Every descriptor here is derivable from data already on disk (OHLCV +
existing daily-bar/ATR/overnight conventions) -- no new data source.

HOW TO USE:
    from market_state_primitives import build_state_frame
    states = build_state_frame(discovery_df)
    # states.index = calendar date, one column per descriptor below.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from study_bar_behavior_batch1 import build_daily_bars, RANGE_LOOKBACK_DAYS
from study_intraday_behavior_batch3 import build_overnight_and_rth_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ATR_WINDOW = 14
LOCATION_LOOKBACK_DAYS = 20
PERSISTENCE_LOOKBACK_DAYS = 3


def _overnight_range_by_day(df: pd.DataFrame) -> dict:
    """Overnight (prior-day 16:00 ET -> today 09:30 ET) range per RTH
    day. Delegates to build_overnight_and_rth_frame -- the exact,
    already-validated overnight-session definition behind the
    overnight-coil finding (hyp-000056/057) -- rather than
    re-implementing session-boundary logic here."""
    frame = build_overnight_and_rth_frame(df)
    return frame["overnight_range"].to_dict()


def _opening_range_by_day(df: pd.DataFrame, minutes: int = 30) -> dict:
    """First `minutes` of RTH (09:30 start) range per day."""
    out = {}
    idx = df.index
    for day, day_df in df.groupby(idx.date):
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty:
            continue
        opening = rth.iloc[: max(1, minutes)]  # 1-min bars -> `minutes` rows
        if opening.empty:
            continue
        out[day] = float(opening["High"].max() - opening["Low"].min())
    return out


def build_state_frame(df: pd.DataFrame) -> pd.DataFrame:
    """One row per RTH day, columns = state descriptors, all computed
    using ONLY information available as of that day's open (no
    lookahead -- every rolling/trailing stat is shifted to exclude the
    current day before being used as a state descriptor).

    Descriptors (v1 -- a starting menu, not exhaustive; see design spec
    for the full candidate list; unimplemented ones noted below are
    deferred, not abandoned):
      - range_vs_atr: prior day's range / trailing ATR(14) (excludes
        today -- this IS knowable at today's open). Same convention as
        the validated range-contraction finding.
      - overnight_range_vs_atr: last night's overnight range / trailing
        ATR(14). Same convention as the validated overnight-coil
        finding.
      - gap_vs_atr: today's open vs. yesterday's reference close,
        signed, divided by trailing ATR(14).
      - opening_range_vs_atr: first-30-min RTH range / trailing ATR(14)
        (same-day, known by 10:00 -- usable only for same-day/afternoon
        conditional analysis, not pre-open).
      - directional_persistence: sign-consistency of the last
        PERSISTENCE_LOOKBACK_DAYS daily closes (-1..+1, fraction of
        those days that closed in the same direction as the most
        recent one).
      - location_in_range: today's open's percentile position within
        the trailing LOCATION_LOOKBACK_DAYS day's high-low range
        (0=at the low, 1=at the high).
      - day_of_week: Mon=0..Fri=4 (not yet reduced to a numeric state,
        kept as a categorical splitter).

    Deferred (need infrastructure not yet reused here, tracked in the
    design spec, not implemented in v1): distance from session VWAP,
    volume vs. expected volume, cross-market relationships (ES/VXN).
    """
    daily = build_daily_bars(df).copy()
    daily["range"] = daily["High"] - daily["Low"]
    daily["atr14"] = daily["range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)

    overnight = _overnight_range_by_day(df)
    opening = _opening_range_by_day(df)

    daily["overnight_range"] = pd.Series(overnight)
    daily["opening_range_30m"] = pd.Series(opening)

    daily["range_vs_atr"] = daily["range"].shift(1) / daily["atr14"]
    daily["overnight_range_vs_atr"] = daily["overnight_range"] / daily["atr14"]
    daily["opening_range_vs_atr"] = daily["opening_range_30m"] / daily["atr14"]

    prior_close = daily["Close"].shift(1)
    daily["gap_vs_atr"] = (daily["Open"] - prior_close) / daily["atr14"]

    sign = np.sign(daily["Close"].diff())
    latest_sign = sign.shift(1)
    persistence = []
    for i in range(len(daily)):
        if i < PERSISTENCE_LOOKBACK_DAYS + 1:
            persistence.append(np.nan)
            continue
        window = sign.iloc[i - PERSISTENCE_LOOKBACK_DAYS:i]
        ref = latest_sign.iloc[i]
        if pd.isna(ref) or window.isna().any():
            persistence.append(np.nan)
            continue
        persistence.append(float((window == ref).mean()))
    daily["directional_persistence"] = persistence

    trailing_high = daily["High"].rolling(LOCATION_LOOKBACK_DAYS, min_periods=LOCATION_LOOKBACK_DAYS).max().shift(1)
    trailing_low = daily["Low"].rolling(LOCATION_LOOKBACK_DAYS, min_periods=LOCATION_LOOKBACK_DAYS).min().shift(1)
    span = trailing_high - trailing_low
    daily["location_in_range"] = np.where(span > 0, (daily["Open"] - trailing_low) / span, np.nan)

    daily["day_of_week"] = [pd.Timestamp(d).dayofweek for d in daily.index]

    # forward-looking columns for the scan to use (computed here once,
    # shared convention, no lookahead in the STATE columns above)
    daily["fwd_close"] = daily["Close"]  # alias for readability downstream

    return daily
