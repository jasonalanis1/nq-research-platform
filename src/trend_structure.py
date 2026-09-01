"""
trend_structure.py
=====================

WHAT THIS FILE DOES (plain English):
Classifies each Level Sweep Reversal signal as either sweeping a
"protected" level (the specific swing point that, if broken, would flip
the prevailing trend classification) or an "interior" level (everything
else) -- per the frozen definition in
research/setups/trend-structure-liquidity-filter.md. This is a POST-HOC
FILTER on detect_level_sweep.py's existing signals; it does not change
how a signal is detected, entered, stopped, or targeted.

WHY THIS EXISTS: docs/BACKLOG.md flagged a real gap in the Level Sweep
Reversal setup -- it treats every level sweep the same regardless of the
broader trend context, even though a stop-hunt-then-continuation through
an interior level and a genuine structural reversal at a trend-defining
point are, in principle, different things. This module makes that
distinction mechanically checkable instead of a vague chart-reading
judgment call.

NO-LOOKAHEAD IS THE MOST IMPORTANT PROPERTY OF THIS CODE. A swing point
needs SWING_FRACTAL_K trading days of price action AFTER it before it can
be confirmed as a real swing. trend_context_as_of() only ever uses swing
points that were already confirmable strictly before the day being
classified -- never a swing that needed price data from that day or
later to exist. Getting this wrong would let future information leak
into a backtest, which is exactly the kind of bug the project's
Research Integrity Protocol exists to catch. See
test_trend_structure.py's no-lookahead test for a concrete example of
what this would look like if it were broken.

See research/setups/trend-structure-liquidity-filter.md for the full
definition, including every "honesty flag" default choice made below
(daily bars, SWING_FRACTAL_K = 2, mixed-structure = NO_TREND, no
tolerance band) documented as our own choices, not derived from any
source.

STATUS AS OF 2026-09-01: newly written, not yet wired into
detect_level_sweep.py's normal CLI -- used via a temporary driver script
for the first backtest of this filter (see
research/experiments/_index.md for whether that's happened yet).
"""

from dataclasses import dataclass
from typing import Optional

import pandas as pd

SWING_FRACTAL_K = 2  # see the frozen definition doc, section 2 -- a standard, un-tuned choice


def to_daily_bars(df: pd.DataFrame) -> pd.DataFrame:
    """Resamples 1-minute OHLC data (indexed by NY-time timestamp) down to
    one row per trading day: High = that day's highest 1-minute High, Low
    = that day's lowest 1-minute Low. Indexed by day (midnight timestamp,
    tz-naive) in chronological order."""
    daily = df.groupby(df.index.date).agg(High=("High", "max"), Low=("Low", "min"))
    daily.index = pd.to_datetime(daily.index)
    daily = daily.sort_index()
    return daily


def find_swing_points(daily: pd.DataFrame, k: int = SWING_FRACTAL_K) -> pd.DataFrame:
    """Adds boolean swing_high / swing_low columns to a daily-bars
    DataFrame (as produced by to_daily_bars()). A day at position i is a
    swing_high if its High exceeds the High of every one of the k days
    immediately before AND every one of the k days immediately after it
    (symmetric logic for swing_low on Low). The first and last k days can
    never be flagged (not enough neighbors on one side) -- this is
    correct and expected, not a bug."""
    highs = daily["High"].to_numpy()
    lows = daily["Low"].to_numpy()
    n = len(daily)
    swing_high = [False] * n
    swing_low = [False] * n

    for i in range(k, n - k):
        before_highs = highs[i - k:i]
        after_highs = highs[i + 1:i + 1 + k]
        if highs[i] > before_highs.max() and highs[i] > after_highs.max():
            swing_high[i] = True

        before_lows = lows[i - k:i]
        after_lows = lows[i + 1:i + 1 + k]
        if lows[i] < before_lows.min() and lows[i] < after_lows.min():
            swing_low[i] = True

    out = daily.copy()
    out["swing_high"] = swing_high
    out["swing_low"] = swing_low
    return out


@dataclass
class TrendContext:
    trend: str  # "UPTREND", "DOWNTREND", or "NO_TREND"
    protected_low: Optional[float] = None
    protected_high: Optional[float] = None


def trend_context_as_of(swings: pd.DataFrame, as_of_day, k: int = SWING_FRACTAL_K) -> TrendContext:
    """Determines the trend state and protected level as of `as_of_day`,
    using ONLY swing points that were confirmable strictly before that
    day -- see the module docstring's no-lookahead note. `swings` must be
    the output of find_swing_points(), indexed by day in chronological
    order.

    A swing candidate at position i requires positions i-k..i+k to all
    exist, so as of day X (at position x_pos), the latest position whose
    swing flag could possibly be confirmed is x_pos - 1 - k."""
    as_of_ts = pd.Timestamp(as_of_day)
    index_list = list(swings.index)

    if as_of_ts in swings.index:
        x_pos = index_list.index(as_of_ts)
    else:
        later_positions = [i for i, d in enumerate(index_list) if d >= as_of_ts]
        x_pos = later_positions[0] if later_positions else len(index_list)

    max_confirmable_pos = x_pos - 1 - k
    if max_confirmable_pos < 0:
        return TrendContext(trend="NO_TREND")

    confirmed = swings.iloc[: max_confirmable_pos + 1]
    swing_highs = confirmed[confirmed["swing_high"]]
    swing_lows = confirmed[confirmed["swing_low"]]

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return TrendContext(trend="NO_TREND")

    last_high, prior_high = swing_highs["High"].iloc[-1], swing_highs["High"].iloc[-2]
    last_low, prior_low = swing_lows["Low"].iloc[-1], swing_lows["Low"].iloc[-2]

    if last_high > prior_high and last_low > prior_low:
        return TrendContext(trend="UPTREND", protected_low=last_low)
    if last_high < prior_high and last_low < prior_low:
        return TrendContext(trend="DOWNTREND", protected_high=last_high)
    return TrendContext(trend="NO_TREND")


def classify_signal(swings: pd.DataFrame, signal_day, direction: str, level_swept: float,
                     k: int = SWING_FRACTAL_K) -> dict:
    """Classifies one Level Sweep Reversal signal as 'protected' or
    'not_protected' per the frozen definition doc's section 6. `direction`
    is 'long' or 'short' (matching detect_level_sweep.py's signal dicts),
    `level_swept` is that signal's level_swept value (the actual price
    level that got swept)."""
    ctx = trend_context_as_of(swings, signal_day, k)

    if direction == "long":
        is_protected = (
            ctx.trend == "UPTREND"
            and ctx.protected_low is not None
            and level_swept <= ctx.protected_low
        )
    elif direction == "short":
        is_protected = (
            ctx.trend == "DOWNTREND"
            and ctx.protected_high is not None
            and level_swept >= ctx.protected_high
        )
    else:
        raise ValueError(f"Unknown direction: {direction!r}")

    return {
        "trend": ctx.trend,
        "protected_low": ctx.protected_low,
        "protected_high": ctx.protected_high,
        "classification": "protected" if is_protected else "not_protected",
    }
