"""
market_state_primitives_v4.py
================================

Layer 0 extension for Scan 004 -- frozen spec:
research/studies/scan-004-scoping-2026-09-10.md. Adds THREE new
descriptors, one per new event family queued in research/NEXT_UP.md per
research/studies/project-audit-and-new-starting-point-2026-09-09.md's
"thread 2" (options-expiration effects, session-transition behavior,
multi-day reference-level touches), retargeted to the short-horizon
Standing Research Priority (2026-09-10).

Each descriptor is explicitly checked against, and distinguished from, a
prior related, already-closed test in the frozen scoping doc -- not
repeated here in full: exp-035 (quarterly futures/IMM rollover, REJECTED
clean null), hyp-000110 (closing-pressure-reversal, last-15-min RTH
return, REJECTED cost-dominated), and the opening-hour/mid-morning
single-prior-day reference-level fade studies (hyp-000081 family). None
of the three descriptors below reuse those exact definitions.

IMPORTANT -- WHY THIS MODULE COMPUTES ITS OWN RTH-ONLY OPEN/HIGH/LOW
INSTEAD OF REUSING build_daily_bars (study_bar_behavior_batch1.py):
build_daily_bars groups by calendar DATE across the full near-24h
trading day -- its "Open" is the first bar of the calendar date (well
before 09:30 ET for this instrument), and its "High"/"Low" span into
the evening overnight session past 16:00 ET. That is the right
definition for that module's own callers, but "today's own RTH session
return" and "yesterday's own RTH high-low range" (this scan's frozen
definitions) mean the literal 09:30-16:00 ET regular session, nothing
before or after. _rth_daily_ohlc below reuses the exact same
between_time("09:30", "16:00") RTH window every observatory/study
module in this project already uses (e.g. market_state_primitives.py's
own _opening_range_by_day) -- not a new convention, just the correct
existing one for this specific question.

Every descriptor uses only information knowable as of day i's RTH open
(09:30 ET) -- same no-lookahead convention as v1/v2/v3 (every trailing
stat is shifted to exclude the current day before use).

HOW TO USE:
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame
    from market_state_primitives_v3 import extend_state_frame_v3
    from market_state_primitives_v4 import extend_state_frame_v4
    states = extend_state_frame_v3(extend_state_frame(build_state_frame(discovery_df), discovery_df))
    states = extend_state_frame_v4(states, discovery_df)
    # extend_state_frame_v4 needs the RAW 1-min frame (`discovery_df`) as
    # its second argument, unlike v2/v3 -- see note above on why it can't
    # just reuse states["Open"]/["High"]/["Low"] from build_daily_bars.
"""

import calendar as _calendar_module
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OPEX_LOOKAHEAD_MONTHS = 2  # always enough to find "the next 3rd Friday," including on the 3rd Friday itself
MULTIDAY_LOOKBACKS = [5, 20]  # trading days -- short and long leg, same 20-day long leg convention as v1's LOCATION_LOOKBACK_DAYS (different statistic, see module docstring in market_state_primitives.py's location_in_range vs this module's min-distance-to-nearest-extreme)


def _third_friday(year: int, month: int) -> date:
    """Standard monthly equity-index options expiration convention --
    same third-Friday rule already frozen in study_futures_expiration.py
    (there applied only to the 4 quarterly IMM months; here to all 12,
    see module docstring for why that is a different question, not a
    resurrection)."""
    cal = _calendar_module.Calendar()
    fridays = [d for d in cal.itermonthdates(year, month)
               if d.month == month and d.weekday() == _calendar_module.FRIDAY]
    return fridays[2]


def _next_monthly_opex(day: date) -> date:
    """The next monthly options expiration on or after `day`."""
    y, m = day.year, day.month
    for _ in range(OPEX_LOOKAHEAD_MONTHS + 1):
        candidate = _third_friday(y, m)
        if candidate >= day:
            return candidate
        m += 1
        if m > 12:
            m = 1
            y += 1
    raise RuntimeError(f"No monthly opex found within lookahead window for {day}")


def _rth_daily_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """RTH-only (09:30-16:00 ET) Open/High/Low/Close per calendar day,
    computed directly from the raw 1-min frame. See module docstring for
    why this is NOT build_daily_bars' Open/High/Low."""
    rows = []
    for day, day_df in df.groupby(df.index.date):
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty:
            continue
        rows.append({
            "date": day,
            "rth_open": float(rth.iloc[0]["Open"]),
            "rth_high": float(rth["High"].max()),
            "rth_low": float(rth["Low"].min()),
            "rth_close": float(rth.iloc[-1]["Close"]),
        })
    return pd.DataFrame(rows).set_index("date").sort_index()


def extend_state_frame_v4(states: pd.DataFrame, raw_df: pd.DataFrame) -> pd.DataFrame:
    """Adds the 3 Scan-004 descriptors to an existing (v1+v2+v3-extended)
    state frame. `raw_df` must be the SAME raw 1-min frame `states` was
    ultimately built from (e.g. the Discovery slice) -- needed for
    genuine RTH-only Open/High/Low (see _rth_daily_ohlc)."""
    out = states.copy()
    rth = _rth_daily_ohlc(raw_df)
    rth_aligned = rth.reindex(out.index)  # same date-object index convention as build_daily_bars/build_state_frame

    # Stored for the scan script's forward-return computation (the
    # `intraday` and `overnight` horizons need the TRUE RTH open, not
    # build_daily_bars' calendar-day-first-bar "Open" -- see module
    # docstring). Not itself a conditioning descriptor.
    out["rth_open"] = rth_aligned["rth_open"]

    # --- 1. days_to_monthly_opex (options-expiration family) ---
    all_days = list(out.index)
    day_ordinals = np.array([d.toordinal() for d in all_days])
    days_to_opex = []
    for day in all_days:
        opex_ord = _next_monthly_opex(day).toordinal()
        day_ord = day.toordinal()
        lo = int(np.searchsorted(day_ordinals, day_ord, side="right"))   # count of trading days <= today
        hi = int(np.searchsorted(day_ordinals, opex_ord, side="right"))  # count of trading days <= opex date
        days_to_opex.append(hi - lo)  # trading days strictly after today, through and including opex
    out["days_to_monthly_opex"] = days_to_opex

    # --- 2. prior_close_location_in_range (session-transition family) ---
    span = rth_aligned["rth_high"] - rth_aligned["rth_low"]
    loc = (rth_aligned["rth_close"] - rth_aligned["rth_low"]) / span
    loc = loc.where(span > 0)
    out["prior_close_location_in_range"] = loc.shift(1)  # yesterday's fact, known at today's open, no lookahead

    # --- 3. dist_to_multiday_reference_level_vs_atr (reference-level family) ---
    today_open = rth_aligned["rth_open"]
    dist_components = []
    for lb in MULTIDAY_LOOKBACKS:
        trailing_high = rth_aligned["rth_high"].rolling(lb, min_periods=lb).max().shift(1)
        trailing_low = rth_aligned["rth_low"].rolling(lb, min_periods=lb).min().shift(1)
        dist_components.append((today_open - trailing_high).abs())
        dist_components.append((today_open - trailing_low).abs())
    min_dist = pd.concat(dist_components, axis=1).min(axis=1)
    out["dist_to_multiday_reference_level_vs_atr"] = min_dist / out["atr14"]

    return out


if __name__ == "__main__":
    # Sanity check only, not a hypothesis test.
    from data_loader import load_price_data
    from data_split import get_discovery_data
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame
    from market_state_primitives_v3 import extend_state_frame_v3

    df, synthetic = load_price_data(context="market_state_primitives_v4.py sanity check")
    if synthetic:
        print("ABORT: only synthetic data available.")
    else:
        discovery = get_discovery_data(df)
        states = extend_state_frame_v3(extend_state_frame(build_state_frame(discovery), discovery))
        states = extend_state_frame_v4(states, discovery)
        for col in ["days_to_monthly_opex", "prior_close_location_in_range", "dist_to_multiday_reference_level_vs_atr"]:
            n_valid = int(states[col].notna().sum())
            print(f"{col}: {n_valid} non-null of {len(states)} Discovery days")
            print(states[col].describe())
            print()
