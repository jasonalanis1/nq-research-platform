"""
market_state_primitives_v3.py
================================

Layer 0 extension for Scan 003 (research/NEXT_UP.md queue item 2, the
"reasonable next Discovery Engine step" flagged 2026-09-09: untested
state variables opening_range_vs_atr -- already implemented in v1,
never scanned -- and a ZN-bond-derived state variable, not yet built).

Adds ONE new descriptor: zn_level_vs_trailing -- ZN (10-Year Treasury
Note futures) prior-day reference close relative to its own
ZN_LOOKBACK_DAYS trailing average, i.e. "is the rate/bond-price
environment persistently elevated or depressed relative to its own
recent history," using exactly the same shape and shift/lookahead
convention as market_state_primitives_v2.py's vxn_level_vs_trailing
(prior-day fact, shifted, no lookahead).

WHY THIS IS A DIFFERENT QUESTION FROM THE ALREADY-REJECTED ZN
STANDALONE SIGNAL (hyp from src/study_bond_lead_signal.py, REJECTED):
that test asked "does ZN's own single-day return SIGN the day before
predict NQ's next-day return sign" -- a momentum/direction bet on ONE
forward horizon. This descriptor asks a structurally different
question ("is the bond/rate regime persistently high or low vs its own
recent trailing average"), scanned across MULTIPLE forward horizons and
outcome buckets via the Discovery Engine, exactly the same relationship
Scan 002 already drew between vxn_level_vs_trailing (this new
descriptor's direct analogue) and the already-independently-rejected
standalone VXN signal tests. Reusing that precedent, not inventing a
new exception to the no-hypothesis-resurrection rule.

Every new column uses only information known as of the state day's
open (ZN's PRIOR day close, shifted) -- no lookahead.

HOW TO USE:
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame
    from market_state_primitives_v3 import extend_state_frame_v3
    states = extend_state_frame_v3(extend_state_frame(build_state_frame(df), df))
"""

from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ZN_LOOKBACK_DAYS = 20  # same convention as VXN_LOOKBACK_DAYS in v2


def _load_zn_daily_ref_closes() -> pd.Series:
    """ZN daily reference close, full disk history (2015-01-01 through
    2024-01-03 -- Discovery-slice-safe: covers all of Discovery
    (ends 2021-10-03) and all of Validation (ends 2024-01-03), never
    reaches into Holdout Gen2 (starts 2024-01-04), so no holdout
    boundary logic is needed here -- there is nothing on disk past it).
    Reuses compute_daily_ref_closes (study_volatility_regime.py)
    unmodified, same function study_bond_lead_signal.py already used
    for ZN, applied here with apply_holdout=False purely because the
    on-disk ZN file already ends before the holdout boundary -- the
    boundary function would be a no-op, not a bypass of it."""
    zn_df, is_synthetic = load_price_data(context="market_state_primitives_v3.py (ZN)",
                                           apply_holdout=False, symbol="ZN")
    if is_synthetic:
        raise RuntimeError("Only synthetic ZN data available -- zn_level_vs_trailing cannot be built.")
    day_groups = {day: sub for day, sub in zn_df.groupby(zn_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)
    s = pd.Series(ref_closes).dropna()
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def extend_state_frame_v3(states: pd.DataFrame) -> pd.DataFrame:
    """Adds zn_level_vs_trailing to an existing (v1+v2-extended) state
    frame. `states.index` must be datetime-like (matches build_state_frame's
    daily index)."""
    out = states.copy()
    zn_ref_closes = _load_zn_daily_ref_closes()

    idx = pd.to_datetime(out.index)
    zn_reindexed = zn_ref_closes.reindex(idx, method="ffill")  # ZN/NQ trading calendars differ slightly (e.g. bond-market holidays); carry forward last known ZN close, same convention as v2's VXN ffill
    zn_trailing_avg = zn_reindexed.rolling(ZN_LOOKBACK_DAYS, min_periods=ZN_LOOKBACK_DAYS).mean().shift(1)
    zn_prior = zn_reindexed.shift(1)
    zn_level_vs_trailing = (zn_prior / zn_trailing_avg) - 1.0
    out["zn_level_vs_trailing"] = pd.Series(zn_level_vs_trailing.values, index=out.index)

    return out


if __name__ == "__main__":
    # Sanity check only, not a hypothesis test.
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame

    df, synthetic = load_price_data(context="market_state_primitives_v3.py sanity check")
    if synthetic:
        print("ABORT: only synthetic data available.")
    else:
        discovery = get_discovery_data(df)
        states = extend_state_frame_v3(extend_state_frame(build_state_frame(discovery), discovery))
        n_valid = int(states["zn_level_vs_trailing"].notna().sum())
        print(f"zn_level_vs_trailing: {n_valid} non-null of {len(states)} Discovery days")
        print(states["zn_level_vs_trailing"].describe())
