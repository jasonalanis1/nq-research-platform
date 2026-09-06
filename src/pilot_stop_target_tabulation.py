"""
pilot_stop_target_tabulation.py
================================
PURELY DESCRIPTIVE pilot check, not a promotion-relevant result. Run
before Jason signs off on exp-048's parameters, per the Advisor's
explicit recommendation (item 6): show how the 299 exp-047 weeks
resolve under the proposed 20-day-ATR / -1R / +2R rule -- stop-hit
first, target-hit first, or neither -- so parameters aren't approved
blind on resulting sample size. Reports COUNTS only, no P&L, no
verdict. Not logged to the research ledger (same convention as other
free Step-1 descriptive checks, e.g. exp-043/044's Step 1).
"""

import numpy as np
import pandas as pd
from pathlib import Path

import sys
sys.path.insert(0, "src")

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes
from study_nq_weekly_trend_following import (
    resample_to_weekly_closes,
    compute_weekly_log_returns,
    compute_weekly_momentum_signal,
)
from study_nq_trend_following import compute_positions

ATR_WINDOW_DAYS = 20
STOP_R = 1.0
TARGET_R = 2.0

full_df, is_synthetic = load_price_data(context="pilot_stop_target_tabulation.py")
assert not is_synthetic, "ABORT: only synthetic data available"

discovery_df = get_discovery_data(full_df)
day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
ref_closes = compute_daily_ref_closes(day_groups)

# daily OHLC (for ATR) -- aggregate each day's 1-min bars
daily_ohlc = {}
for day, sub in day_groups.items():
    if len(sub) == 0:
        continue
    daily_ohlc[day] = {
        "high": sub["High"].max(),
        "low": sub["Low"].min(),
        "close": ref_closes.get(day),
    }

days_sorted = sorted(daily_ohlc.keys())

# True Range per day, then trailing 20-day ATR (causal: only days strictly before)
tr_by_day = {}
for i in range(1, len(days_sorted)):
    d, prev_d = days_sorted[i], days_sorted[i - 1]
    if daily_ohlc[d]["close"] is None or daily_ohlc[prev_d]["close"] is None:
        continue
    h, l, prev_c = daily_ohlc[d]["high"], daily_ohlc[d]["low"], daily_ohlc[prev_d]["close"]
    tr_by_day[d] = max(h - l, abs(h - prev_c), abs(l - prev_c))

def atr_as_of(target_day):
    """Trailing ATR_WINDOW_DAYS-day mean True Range using only days strictly before target_day."""
    prior_days = [d for d in days_sorted if d in tr_by_day and d < target_day]
    if len(prior_days) < ATR_WINDOW_DAYS:
        return None
    window = prior_days[-ATR_WINDOW_DAYS:]
    return float(np.mean([tr_by_day[d] for d in window]))

weekly_closes = resample_to_weekly_closes(ref_closes)
weekly_returns = compute_weekly_log_returns(weekly_closes)
all_weeks = sorted(weekly_closes.keys())
mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)
positions = compute_positions(mom_by_week)

weeks_with_position = sorted(w for w in positions.keys() if weekly_closes.get(w) is not None)

# map each ISO (year, week) to its calendar days, so we can pull 1-min bars for that week
day_to_week = {}
for day in days_sorted:
    iso_year, iso_week, _ = day.isocalendar()
    day_to_week.setdefault((iso_year, iso_week), []).append(day)

counts = {"stop_first": 0, "target_first": 0, "neither": 0, "no_atr_available": 0}
r_multiples_used = []

weeks_seq = [w for w in weeks_with_position]
for i in range(1, len(weeks_seq)):
    prev_w, w = weeks_seq[i - 1], weeks_seq[i]
    position = positions[w]
    entry_price = weekly_closes[prev_w]  # entry = last week's closing ref price, matches exp-047 timing
    # find the first trading day of week w to anchor the ATR lookup
    week_days = sorted(day_to_week.get(w, []))
    if not week_days:
        continue
    entry_day = week_days[0]
    r = atr_as_of(entry_day)
    if r is None or r <= 0:
        counts["no_atr_available"] += 1
        continue
    r_multiples_used.append(r)

    if position > 0:
        stop_level = entry_price - STOP_R * r
        target_level = entry_price + TARGET_R * r
    else:
        stop_level = entry_price + STOP_R * r
        target_level = entry_price - TARGET_R * r

    # walk this week's 1-minute bars in chronological order
    outcome = "neither"
    for day in week_days:
        sub = day_groups.get(day)
        if sub is None or len(sub) == 0:
            continue
        for _, bar in sub.sort_index().iterrows():
            hi, lo = bar["High"], bar["Low"]
            if position > 0:
                stop_touched = lo <= stop_level
                target_touched = hi >= target_level
            else:
                stop_touched = hi >= stop_level
                target_touched = lo <= target_level
            if stop_touched and target_touched:
                # same-bar ambiguity -- conservatively assume stop first (standard convention)
                outcome = "stop_first"
                break
            elif stop_touched:
                outcome = "stop_first"
                break
            elif target_touched:
                outcome = "target_first"
                break
        if outcome != "neither":
            break
    counts[outcome] += 1

total = sum(counts.values())
print("=" * 70)
print("PILOT (descriptive only, not a promotion-relevant result)")
print(f"exp-048 candidate: {STOP_R}R stop / {TARGET_R}R target, {ATR_WINDOW_DAYS}-day ATR")
print("=" * 70)
print(f"Total weeks evaluated: {total}")
for k, v in counts.items():
    pct = 100.0 * v / total if total else 0.0
    print(f"  {k}: {v} ({pct:.1f}%)")
if r_multiples_used:
    print(f"\n1R (20-day ATR) at entry -- median: {np.median(r_multiples_used):.2f} pts, "
          f"mean: {np.mean(r_multiples_used):.2f} pts, "
          f"min: {np.min(r_multiples_used):.2f}, max: {np.max(r_multiples_used):.2f}")
