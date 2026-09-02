"""
test_study_es_gap_incremental_info.py
=========================================
Automated tests for the ES Overnight Gap Incremental-Information
characterization study
(research/studies/es-overnight-gap-incremental-information.md).

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date

import numpy as np
import pandas as pd
import pytest

import study_es_gap_incremental_info as eg


def make_bars(day, tz, bars):
    rows = []
    index = []
    for hour, minute, o, h, l, c, v in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": v})
    return pd.DataFrame(rows, index=index)


def test_compute_instrument_day_data_basic():
    """A day with an 8:30 bar followed by a 4pm bar (chronological
    order, as real data always is) should yield both a ref_close and an
    open; day_df should be the original bars."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    bars = [(8, 30, 100.0, 100.0, 100.0, 100.0, 10.0), (16, 0, 99.0, 99.0, 99.0, 99.0, 10.0)]
    df = make_bars(day, tz, bars)
    out = eg.compute_instrument_day_data(df)
    assert out[day]["ref_close"] == 99.0
    assert out[day]["open"] == 100.0
    assert len(out[day]["day_df"]) == 2


def test_compute_instrument_day_data_missing_open_is_none():
    """A day with only a pre-8:30 bar (no bar at/after 8:30 AM) has a
    ref_close (the last bar at/before 4pm, which this early bar
    qualifies as) but no open."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    bars = [(7, 0, 99.0, 99.0, 99.0, 99.0, 10.0)]
    df = make_bars(day, tz, bars)
    out = eg.compute_instrument_day_data(df)
    assert out[day]["ref_close"] == 99.0
    assert out[day]["open"] is None


def test_compute_gap_basic():
    """gap = today_open - prior_day's ref_close, hand-checked."""
    instrument_days = {
        date(2024, 1, 1): {"ref_close": 100.0, "open": 101.0},
        date(2024, 1, 2): {"ref_close": 102.0, "open": 105.0},
    }
    gap = eg.compute_gap(instrument_days, date(2024, 1, 2), date(2024, 1, 1))
    assert gap == pytest.approx(5.0)  # 105.0 - 100.0


def test_compute_gap_none_when_either_side_missing():
    instrument_days = {
        date(2024, 1, 1): {"ref_close": None, "open": 101.0},
        date(2024, 1, 2): {"ref_close": 102.0, "open": 105.0},
    }
    assert eg.compute_gap(instrument_days, date(2024, 1, 2), date(2024, 1, 1)) is None

    instrument_days2 = {
        date(2024, 1, 1): {"ref_close": 100.0, "open": 101.0},
        date(2024, 1, 2): {"ref_close": 102.0, "open": None},
    }
    assert eg.compute_gap(instrument_days2, date(2024, 1, 2), date(2024, 1, 1)) is None


def test_build_joint_dataset_drops_day_missing_from_one_instrument():
    """A day present and valid in NQ but entirely absent from ES must
    not appear in the joint dataset -- the inner join in frozen spec
    item 3."""
    tz = "America/New_York"
    days = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
    nq_frames, es_frames = [], []
    for i, day in enumerate(days):
        bars = [(16, 0, 100.0 + i, 100.0 + i, 100.0 + i, 100.0 + i, 10.0),
                (8, 30, 100.0 + i, 100.0 + i, 100.0 + i, 100.0 + i, 10.0)]
        bars += [(9, m, 100.0 + i, 100.0 + i, 100.0 + i, 100.0 + i, 10.0) for m in range(60)]
        bars += [(h, m, 100.0 + i, 100.0 + i, 100.0 + i, 100.0 + i, 10.0)
                 for h in range(10, 12) for m in range(60)]
        nq_frames.append(make_bars(day, tz, bars))
        if day != date(2024, 1, 2):  # ES has no data at all on Jan 2
            es_frames.append(make_bars(day, tz, bars))
    nq_df = pd.concat(nq_frames)
    es_df = pd.concat(es_frames)

    joint = eg.build_joint_dataset(nq_df, es_df)
    # Jan 2 can't appear as a "day" at all -- ES has no data for it, so
    # it's excluded from the common (valid-on-both) day set entirely.
    assert date(2024, 1, 2) not in set(joint["date"])
    # Jan 3 DOES appear -- per the documented "immediately preceding day
    # in the joined list" semantics (frozen spec item 3), its prior_day
    # becomes Jan 1 (skipping over the excluded Jan 2), not a missing
    # gap. Confirm that skip actually happened: Jan 3's nq_gap must be
    # computed against Jan 1's reference close, not Jan 2's.
    assert date(2024, 1, 3) in set(joint["date"])
    row = joint[joint["date"] == date(2024, 1, 3)].iloc[0]
    jan1_ref_close = 100.0  # bars built with value 100.0 + i, i=0 for Jan 1
    jan3_open = 102.0       # i=2 for Jan 3
    assert row["nq_gap"] == pytest.approx(jan3_open - jan1_ref_close)


def test_fit_regression_recovers_exact_linear_relationship():
    """No-noise synthetic data: y = 2 + 3*nq_gap - 1*es_gap exactly.
    OLS on noiseless data must recover the true coefficients (up to
    floating-point tolerance)."""
    rng = np.random.default_rng(0)
    nq_gap = rng.uniform(-5, 5, size=50)
    es_gap = rng.uniform(-5, 5, size=50)
    y = 2.0 + 3.0 * nq_gap - 1.0 * es_gap
    b0, b1, b2 = eg.fit_regression(nq_gap, es_gap, y)
    assert b0 == pytest.approx(2.0, abs=1e-8)
    assert b1 == pytest.approx(3.0, abs=1e-8)
    assert b2 == pytest.approx(-1.0, abs=1e-8)


def test_bootstrap_regression_coef_ci_excludes_zero_for_strong_real_effect():
    """A clear, noiseless positive relationship between es_gap and y
    (holding nq_gap fixed at zero effect) must produce a 90% CI on b2
    that excludes zero."""
    rng = np.random.default_rng(1)
    n = 200
    nq_gap = rng.uniform(-5, 5, size=n)
    es_gap = rng.uniform(-5, 5, size=n)
    y = 4.0 * es_gap + rng.normal(0, 0.1, size=n)  # b2 should come out near +4, tight CI
    ci_low, ci_high = eg.bootstrap_regression_coef_ci(nq_gap, es_gap, y, n_bootstrap=200, seed=5)
    assert ci_low > 0


def test_bootstrap_regression_coef_ci_spans_zero_for_no_effect():
    """Pure noise for y, unrelated to either gap -- the 90% CI on b2
    should span zero (not be spuriously significant on random data)."""
    rng = np.random.default_rng(2)
    n = 200
    nq_gap = rng.uniform(-5, 5, size=n)
    es_gap = rng.uniform(-5, 5, size=n)
    y = rng.normal(0, 10, size=n)  # no real relationship to either gap
    ci_low, ci_high = eg.bootstrap_regression_coef_ci(nq_gap, es_gap, y, n_bootstrap=200, seed=7)
    assert ci_low < 0 < ci_high


def test_analyze_horizon_reports_expected_keys():
    """Small synthetic dataset -- checks the analyze_horizon pipeline
    wires together and produces the expected shape, not exact values
    (those are covered by the unit tests above)."""
    rng = np.random.default_rng(3)
    n = 60
    df = pd.DataFrame({
        "nq_gap": rng.uniform(-5, 5, size=n),
        "es_gap": rng.uniform(-5, 5, size=n),
        f"nq_fwd_return_{eg.PRIMARY_HORIZON_MINUTES}m": rng.normal(0, 5, size=n),
    })
    result = eg.analyze_horizon(df, eg.PRIMARY_HORIZON_MINUTES)
    for key in ("n", "b0_intercept", "b1_nq_gap_coef", "b2_es_gap_coef",
                "b2_90ci", "significant", "translated_effect_points",
                "economically_meaningful"):
        assert key in result
    assert result["n"] == n


def test_robustness_drop_largest_es_gap_day_drops_correct_row():
    """The row with the single largest |es_gap| must be excluded, and
    the dropped_date reported must match it."""
    col = f"nq_fwd_return_{eg.PRIMARY_HORIZON_MINUTES}m"
    df = pd.DataFrame({
        "date": [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)],
        "nq_gap": [1.0, -2.0, 3.0, -1.0],
        "es_gap": [1.0, -2.0, 50.0, -1.0],  # Jan 3 is the largest-magnitude es_gap
        col: [1.0, -1.0, 2.0, -2.0],
    })
    result = eg.robustness_drop_largest_es_gap_day(df)
    assert result["dropped_date"] == str(date(2024, 1, 3))
    assert result["n"] == 3
