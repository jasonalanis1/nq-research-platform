"""
volatility_conditioning.py
=============================

A reusable, documented CONTEXT MODULE -- not a hypothesis test, not a
strategy, not subject to this project's 90%-CI promotion bar. Built per
Jason's direction (2026-09-08) to turn the project's two
Validation-confirmed volatility-persistence facts into something
usable, rather than continuing to generate new directional hypotheses.
Full design rationale: research/studies/volatility-conditioning-module-spec.md.

The two facts it's built from (the only two findings in this project's
history to survive a real Validation-slice prospective test):

  1. Prior-day range regime (hyp-000046 Discovery / hyp-000048
     Validation-confirmed): a narrow prior day tends to be followed by
     another narrower-than-average day; a wide prior day by a
     wider-than-average day. Classification and thresholds reused
     UNMODIFIED from study_intraday_behavior_batch1.build_daily_frame /
     RANGE_NARROW_PCTL / RANGE_WIDE_PCTL / LOOKBACK_DAYS.

  2. Overnight coil (hyp-000056 Discovery / hyp-000057 Validation-
     confirmed): an unusually tight overnight (Globex) session tends to
     be followed by a quieter-than-average regular-hours session on
     the SAME day. Classification reused UNMODIFIED from
     study_intraday_behavior_batch3.build_overnight_and_rth_frame /
     COIL_PCTL / LOOKBACK_DAYS.

HONESTY DISCLOSURES (read before using this for anything):
  1. Both facts predict RANGE (how big a move to expect), never
     DIRECTION. This module cannot tell you which way to trade.
  2. Neither fact's economic value has been shown as an actual
     sizing/stop-width rule on any live/future signal -- the 3 overlay
     screens run against already-dead signals earlier in this project
     (exp-077, exp-086, exp-087) found no conditioning effect on THOSE
     specific signals. That does not prove this could never help a
     live signal, only that it hasn't been demonstrated to yet. Any
     strategy that wants to use this module's output as an actual
     sizing input needs its own frozen spec and its own
     Discovery/Validation test of whether doing so helps.
  3. All multipliers below are VALIDATION-slice numbers (the honest,
     out-of-sample-confirmed ones), not Discovery-slice (which this
     project's own effect-size-inflation diagnostic showed runs
     larger than what survives). Deliberately conservative.
  4. The "combined" multiplier when both signals fire the same day is
     an unverified approximation (the product of the two individual
     ratios) -- the interaction of the two conditions together has
     never itself been tested, only each alone. Disclosed in `basis`.

HOW TO USE:
    from volatility_conditioning import get_volatility_conditioning
    result = get_volatility_conditioning(some_date, daily_ohlcv_df)
    # result["expected_range_multiplier"] -- e.g. 0.84 means "today is
    # expected to have roughly 84% of a normal day's range, based on
    # confirmed volatility-persistence facts" -- informational only.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from study_intraday_behavior_batch1 import (
    build_daily_frame,
    RANGE_NARROW_PCTL,
    RANGE_WIDE_PCTL,
    LOOKBACK_DAYS as RANGE_LOOKBACK_DAYS,
)
from study_intraday_behavior_batch3 import (
    build_overnight_and_rth_frame,
    COIL_PCTL,
    LOOKBACK_DAYS as COIL_LOOKBACK_DAYS,
)

# Validation-slice confirmed ratios (hyp-000048, hyp-000057) -- see this
# module's docstring and volatility-conditioning-module-spec.md for the
# exact CI's each of these point estimates came from.
NARROW_PRIOR_DAY_RATIO = 0.9438   # hyp-000048, Validation n=141, ci_90=(0.8884, 0.9982)
WIDE_PRIOR_DAY_RATIO = 1.0809     # hyp-000048, Validation n=130, ci_90=(1.0204, 1.1430)
COILED_OVERNIGHT_RATIO = 0.8944   # hyp-000057, Validation n=103, ci_90=(0.8300, 0.9595)


def build_conditioning_frame(df: pd.DataFrame) -> pd.DataFrame:
    """One row per day: narrow/wide classification (from the prior
    day's own trailing-range percentile) and coiled-overnight
    classification, both reusing the exact frozen definitions
    unmodified. `df` should be minute-bar OHLCV with a tz-aware
    DatetimeIndex, same shape this project's other studies use."""
    daily = build_daily_frame(df)
    narrow_thresh = daily["range"].rolling(RANGE_LOOKBACK_DAYS, min_periods=RANGE_LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, RANGE_NARROW_PCTL), raw=True).shift(1)
    wide_thresh = daily["range"].rolling(RANGE_LOOKBACK_DAYS, min_periods=RANGE_LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, RANGE_WIDE_PCTL), raw=True).shift(1)
    daily["prior_day_narrow"] = (daily["range"] <= narrow_thresh).shift(1).fillna(False).astype(bool)
    daily["prior_day_wide"] = (daily["range"] >= wide_thresh).shift(1).fillna(False).astype(bool)

    overnight = build_overnight_and_rth_frame(df)
    coil_thresh = overnight["overnight_range"].rolling(COIL_LOOKBACK_DAYS, min_periods=COIL_LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, COIL_PCTL), raw=True).shift(1)
    overnight["coiled_overnight"] = overnight["overnight_range"] <= coil_thresh

    out = daily[["prior_day_narrow", "prior_day_wide"]].join(
        overnight[["coiled_overnight"]], how="left")
    out["coiled_overnight"] = out["coiled_overnight"].fillna(False).astype(bool)
    return out


def get_volatility_conditioning(date, conditioning_frame: pd.DataFrame) -> dict:
    """Look up one day's conditioning flags and combined expected-range
    multiplier from a frame already built by build_conditioning_frame.
    Returns a dict, never raises on a missing/unclassifiable date (flags
    default False, multiplier defaults 1.0 -- 'no information')."""
    narrow = bool(conditioning_frame.loc[date, "prior_day_narrow"]) if date in conditioning_frame.index else False
    wide = bool(conditioning_frame.loc[date, "prior_day_wide"]) if date in conditioning_frame.index else False
    coiled = bool(conditioning_frame.loc[date, "coiled_overnight"]) if date in conditioning_frame.index else False

    multiplier = 1.0
    basis = []
    if narrow:
        multiplier *= NARROW_PRIOR_DAY_RATIO
        basis.append(f"prior_day_narrow (hyp-000048, x{NARROW_PRIOR_DAY_RATIO})")
    if wide:
        multiplier *= WIDE_PRIOR_DAY_RATIO
        basis.append(f"prior_day_wide (hyp-000048, x{WIDE_PRIOR_DAY_RATIO})")
    if coiled:
        multiplier *= COILED_OVERNIGHT_RATIO
        basis.append(f"coiled_overnight (hyp-000057, x{COILED_OVERNIGHT_RATIO})")
    if not basis:
        basis.append("no confirmed condition fired -- no adjustment (1.0)")

    return {
        "date": str(date),
        "narrow_prior_day": narrow,
        "wide_prior_day": wide,
        "coiled_overnight": coiled,
        "expected_range_multiplier": round(float(multiplier), 4),
        "basis": basis,
    }


if __name__ == "__main__":
    # Small self-check on real Discovery data: prints the conditioning
    # frame's flag rates and a few example days, so a human can sanity-
    # check the module before anything else depends on it.
    from data_loader import load_price_data
    from data_split import get_discovery_data

    df, is_synthetic = load_price_data(context="volatility_conditioning.py self-check")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
    else:
        discovery = get_discovery_data(df)
        frame = build_conditioning_frame(discovery)
        print(f"Days classified: {len(frame)}")
        print(f"  narrow prior day: {frame['prior_day_narrow'].sum()} "
              f"({frame['prior_day_narrow'].mean():.1%})")
        print(f"  wide prior day:   {frame['prior_day_wide'].sum()} "
              f"({frame['prior_day_wide'].mean():.1%})")
        print(f"  coiled overnight: {frame['coiled_overnight'].sum()} "
              f"({frame['coiled_overnight'].mean():.1%})")
        both = frame[frame["prior_day_narrow"] & frame["coiled_overnight"]]
        print(f"  both narrow-prior-day AND coiled-overnight: {len(both)} days")
        if len(both):
            example_date = both.index[0]
            print(f"\nExample day where both fired ({example_date}):")
            print(f"  {get_volatility_conditioning(example_date, frame)}")
        example_normal = frame[~frame['prior_day_narrow'] & ~frame['prior_day_wide'] & ~frame['coiled_overnight']]
        if len(example_normal):
            print(f"\nExample normal day (nothing fired, {example_normal.index[0]}):")
            print(f"  {get_volatility_conditioning(example_normal.index[0], frame)}")
