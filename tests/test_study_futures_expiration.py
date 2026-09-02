"""
test_study_futures_expiration.py
===================================
Automated tests for the Futures Expiration/Rollover Proximity
characterization study (research/studies/futures-expiration-effects.md).

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date

import numpy as np
import pandas as pd

import study_futures_expiration as sfe


def test_third_friday_march_2024_matches_known_cme_expiration():
    """March 2024's real CME quarterly expiration was March 15, 2024 --
    a known, independently checkable date."""
    assert sfe.third_friday(2024, 3) == date(2024, 3, 15)


def test_third_friday_june_2024_matches_known_cme_expiration():
    """June 2024's real CME quarterly expiration was June 21, 2024."""
    assert sfe.third_friday(2024, 6) == date(2024, 6, 21)


def test_third_friday_handles_a_month_starting_on_friday():
    """March 2024 starts on a Friday -- makes sure the first-of-month
    edge case doesn't shift the count off by one week."""
    d = sfe.third_friday(2024, 3)
    assert d.weekday() == 4  # Friday
    assert d.day == 15


def test_expiration_dates_covers_all_four_quarters_per_year():
    dates = sfe.expiration_dates(2020, 2020)
    assert len(dates) == 4
    assert [d.month for d in dates] == [3, 6, 9, 12]
    assert all(d.weekday() == 4 for d in dates)  # all Fridays


def test_is_expiration_week_true_for_the_expiration_friday_itself():
    is_exp = sfe.make_is_expiration_week(2024, 2024)
    assert is_exp(date(2024, 3, 15)) is True


def test_is_expiration_week_true_for_earlier_days_in_the_same_week():
    """Expiration Week is Monday-Friday of the week containing the
    expiration date -- Monday should also count."""
    is_exp = sfe.make_is_expiration_week(2024, 2024)
    assert is_exp(date(2024, 3, 11)) is True  # the Monday of that week


def test_is_expiration_week_false_the_week_before():
    is_exp = sfe.make_is_expiration_week(2024, 2024)
    assert is_exp(date(2024, 3, 8)) is False  # the Friday before expiration week


def test_is_expiration_week_false_the_week_after():
    is_exp = sfe.make_is_expiration_week(2024, 2024)
    assert is_exp(date(2024, 3, 18)) is False  # the Monday after expiration week


def test_bootstrap_total_r_ci_tight_around_the_true_sum_for_identical_values():
    """All-identical trade values should produce a bootstrap CI that's
    exactly that sum on both ends (every resample is the same list)."""
    r_values = [1.0] * 50
    low, high = sfe.bootstrap_total_r_ci(r_values, n_bootstrap=200, seed=1)
    assert low == 50.0
    assert high == 50.0


def test_bootstrap_mean_diff_ci_near_zero_for_identical_groups():
    """Two groups drawn from the exact same values should produce a CI
    straddling (or very near) zero."""
    a = [1.0, 2.0, 3.0, 4.0, 5.0] * 20
    b = [1.0, 2.0, 3.0, 4.0, 5.0] * 20
    low, high = sfe.bootstrap_mean_diff_ci(a, b, n_bootstrap=500, seed=1)
    assert low <= 0.0 <= high


def test_analyze_ib_breakout_by_expiration_splits_trades_correctly(tmp_path, monkeypatch):
    """Builds a tiny fake trades CSV with known dates, one inside
    Expiration Week and one outside, and checks the grouping/expectancy
    math directly rather than trusting scale alone."""
    df = pd.DataFrame([
        {"date": "2024-03-12", "exit_reason": "target", "r_multiple_net": 1.0},   # in expiration week
        {"date": "2024-03-12", "exit_reason": "stop", "r_multiple_net": -1.0},    # in expiration week
        {"date": "2024-04-01", "exit_reason": "target", "r_multiple_net": 2.0},   # normal week
    ])
    data_dir = tmp_path
    csv_path = data_dir / "backtest_results_ib_breakout_discovery.csv"
    df.to_csv(csv_path, index=False)

    monkeypatch.setattr(sfe, "DATA_DIR", data_dir)
    is_exp = sfe.make_is_expiration_week(2024, 2024)

    result = sfe.analyze_ib_breakout_by_expiration(is_exp)

    assert result["expiration_week"]["n"] == 2
    assert result["expiration_week"]["win_rate"] == 0.5
    assert result["expiration_week"]["expectancy_r"] == 0.0
    assert result["normal_week"]["n"] == 1
    assert result["normal_week"]["win_rate"] == 1.0
    assert result["normal_week"]["expectancy_r"] == 2.0
