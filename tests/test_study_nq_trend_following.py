"""
test_study_nq_trend_following.py
====================================
Automated tests for the NQ Daily Time-Series Momentum study
(research/studies/nq-daily-trend-following.md).

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

import study_nq_trend_following as tf


def test_compute_momentum_signal_requires_full_lookback():
    """Fewer than MOMENTUM_LOOKBACK_DAYS (252) prior returns -> day is
    excluded entirely (mirrors compute_trailing_volatility's own test)."""
    base = date(2024, 1, 1)
    all_days = [base + timedelta(days=i) for i in range(260)]
    returns = {all_days[i]: 0.001 for i in range(200)}  # only 200 prior returns ever exist
    mom = tf.compute_momentum_signal(returns, all_days)
    assert mom == {}


def test_compute_momentum_signal_uses_exactly_the_last_252():
    """Once 252+ prior returns exist, mom[day_t] must be the SUM of
    exactly the 252 MOST RECENT ones, not all available history."""
    base = date(2024, 1, 1)
    all_days = [base + timedelta(days=i) for i in range(260)]
    returns = {}
    for i in range(255):
        returns[all_days[i]] = 1.0 if i < 3 else 0.01  # first 3 are huge, rest small
    day_t = all_days[256]  # has 255 prior returns available -- only the last 252 should be used
    mom = tf.compute_momentum_signal(returns, all_days)
    expected = sum([0.01] * 252)  # the 3 huge ones fall outside the trailing-252 window
    assert mom[day_t] == pytest.approx(expected)


def test_compute_positions_sign_basic():
    mom_by_day = {date(2024, 1, 1): 0.5, date(2024, 1, 2): -0.3}
    positions = tf.compute_positions(mom_by_day)
    assert positions[date(2024, 1, 1)] == 1
    assert positions[date(2024, 1, 2)] == -1


def test_compute_positions_zero_holds_previous():
    """An exact-zero mom holds the prior day's position rather than
    flipping or going flat."""
    mom_by_day = {
        date(2024, 1, 1): -0.4,   # -> -1
        date(2024, 1, 2): 0.0,    # ties -> holds -1
    }
    positions = tf.compute_positions(mom_by_day)
    assert positions[date(2024, 1, 1)] == -1
    assert positions[date(2024, 1, 2)] == -1


def test_compute_positions_zero_on_first_day_defaults_long():
    mom_by_day = {date(2024, 1, 1): 0.0}
    positions = tf.compute_positions(mom_by_day)
    assert positions[date(2024, 1, 1)] == 1


def test_compute_daily_pnl_hand_checked():
    """Three days: d1 (no output row, no prior close), d2 (same
    position as d1 -- no flip, pnl = 1*(105-100)=5, cost=0), d3
    (position flips to -1 -- pnl = -1*(103-105)=+2, cost=FLIP_COST_POINTS)."""
    d1, d2, d3 = date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)
    positions = {d1: 1, d2: 1, d3: -1}
    ref_closes = {d1: 100.0, d2: 105.0, d3: 103.0}
    df = tf.compute_daily_pnl(positions, ref_closes)
    assert len(df) == 2

    row_d2 = df[df["date"] == d2].iloc[0]
    assert row_d2["pnl"] == pytest.approx(5.0)
    assert row_d2["flipped"] == False
    assert row_d2["cost"] == pytest.approx(0.0)
    assert row_d2["net_pnl"] == pytest.approx(5.0)

    row_d3 = df[df["date"] == d3].iloc[0]
    assert row_d3["pnl"] == pytest.approx(2.0)
    assert row_d3["flipped"] == True
    assert row_d3["cost"] == pytest.approx(tf.FLIP_COST_POINTS)
    assert row_d3["net_pnl"] == pytest.approx(2.0 - tf.FLIP_COST_POINTS)


def test_compute_daily_pnl_skips_over_missing_day_not_both_neighbors():
    """A day with a missing ref_close must be filtered out entirely
    BEFORE pairing, not walked and then dropped as a pair -- its
    neighbors should pair directly with each other, so one missing day
    costs exactly one day of P&L, not two. Hand-checked: d2 is missing,
    so d3 must pair with d1 (the nearest valid predecessor), giving
    price_change = 103 - 100 = 3, not a dropped/absent row."""
    d1, d2, d3, d4 = date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)
    positions = {d1: 1, d2: 1, d3: 1, d4: -1}
    ref_closes = {d1: 100.0, d2: None, d3: 103.0, d4: 110.0}
    df = tf.compute_daily_pnl(positions, ref_closes)
    assert len(df) == 2  # (d1->d3) and (d3->d4); d2 never appears as an endpoint

    row_d3 = df[df["date"] == d3].iloc[0]
    assert row_d3["price_change"] == pytest.approx(3.0)  # 103 - 100, skipping over d2
    assert row_d3["pnl"] == pytest.approx(3.0)  # position[d3]=1
    assert row_d3["flipped"] == False  # position[d3]=1 == position[d1]=1

    row_d4 = df[df["date"] == d4].iloc[0]
    assert row_d4["price_change"] == pytest.approx(7.0)  # 110 - 103
    assert row_d4["pnl"] == pytest.approx(-7.0)  # position[d4]=-1
    assert row_d4["flipped"] == True  # position[d4]=-1 != position[d3]=1


def test_bootstrap_mean_ci_excludes_zero_for_strong_effect():
    rng = np.random.default_rng(1)
    values = rng.normal(5.0, 0.5, size=300)  # clearly positive, tight
    ci_low, ci_high = tf.bootstrap_mean_ci(values, n_bootstrap=200, seed=5)
    assert ci_low > 0


def test_bootstrap_mean_ci_spans_zero_for_no_effect():
    rng = np.random.default_rng(2)
    values = rng.normal(0.0, 10.0, size=300)  # pure noise, centered at zero
    ci_low, ci_high = tf.bootstrap_mean_ci(values, n_bootstrap=200, seed=7)
    assert ci_low < 0 < ci_high


def test_analyze_primary_reports_expected_keys():
    rng = np.random.default_rng(3)
    n = 100
    df = pd.DataFrame({
        "date": [date(2024, 1, 1) + timedelta(days=i) for i in range(n)],
        "position": rng.choice([1, -1], size=n),
        "flipped": [False] * n,
        "price_change": rng.normal(0, 5, size=n),
        "pnl": rng.normal(0.2, 5, size=n),
        "cost": [0.0] * n,
    })
    df["net_pnl"] = df["pnl"] - df["cost"]
    result = tf.analyze_primary(df)
    for key in ("n", "mean_net_pnl", "ci_90", "statistically_credible",
                "n_flips", "total_cost_points", "avg_daily_cost_drag",
                "economic_threshold_points", "economically_meaningful"):
        assert key in result
    assert result["n"] == n
    assert result["n_flips"] == 0


def test_robustness_drop_largest_pnl_day_drops_correct_row():
    df = pd.DataFrame({
        "date": [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)],
        "position": [1, 1, -1, -1],
        "flipped": [False, False, True, False],
        "price_change": [1.0, -1.0, 2.0, -2.0],
        "pnl": [1.0, -1.0, -2.0, 2.0],
        "cost": [0.0, 0.0, tf.FLIP_COST_POINTS, 0.0],
    })
    df["net_pnl"] = df["pnl"] - df["cost"]
    # Jan 3's net_pnl = -2 - FLIP_COST_POINTS, the largest magnitude of the four
    result = tf.robustness_drop_largest_pnl_day(df)
    assert result["dropped_date"] == str(date(2024, 1, 3))
    assert result["n"] == 3
