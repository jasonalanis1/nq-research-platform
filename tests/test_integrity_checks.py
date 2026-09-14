"""Tests for src/integrity_checks.py -- UPGRADE 6's mechanical suite.

Structured around the thing that matters most for a check that gates a Gate:
a check must be RIGHT in both directions. A false green lets a defect through;
a false RED burns the Gate's attention and teaches everyone to ignore the
suite. Three of the tests below exist because the suite produced a false red on
its very first run and the fix had to be locked in.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

import integrity_checks as ic  # noqa: E402


def _obs(values, start="2018-01-01", **extra):
    import pandas as pd
    days = pd.bdate_range(start, periods=len(values))
    return [{"date": str(d.date()), "value": float(v), **extra} for d, v in zip(days, values)]


# ---------------------------------------------------------------------------
# roll dates
# ---------------------------------------------------------------------------

def test_roll_day_is_expiry_friday_and_the_day_before():
    # third Friday of September 2026 is the 18th
    assert ic.quarterly_roll_window("2026-09-18") is True
    assert ic.quarterly_roll_window("2026-09-17") is True
    assert ic.quarterly_roll_window("2026-09-16") is False
    assert ic.quarterly_roll_window("2026-09-19") is False


def test_roll_day_only_in_quarterly_months():
    assert ic.quarterly_roll_window("2026-08-21") is False   # third Friday of a non-quarter month
    assert ic.quarterly_roll_window("2026-06-19") is True    # third Friday of June


def test_roll_day_base_rate_leaves_the_frozen_5pct_threshold_meaningful():
    """THE FALSE-RED REGRESSION. The first implementation flagged the whole
    8-calendar-day window to expiry, a ~12.7% base rate, so every candidate that
    traded most days tripped the spec's 5% threshold. The definition must keep
    the calendar base rate well below the threshold or the check is noise."""
    import pandas as pd
    days = pd.bdate_range("2015-01-01", "2026-09-08")
    base = float(np.mean([ic.quarterly_roll_window(d) for d in days]))
    assert base < ic.ROLL_SHARE_RED, f"base rate {base:.3f} is at/above the red threshold"
    assert base > 0.01, "definition has collapsed to almost nothing"


def test_roll_check_greens_at_ordinary_calendar_exposure():
    vals = np.full(400, 0.5)
    res = ic.check_roll_date_contamination(_obs(vals), list(vals), 0.0)
    assert res["status"] == "GREEN"
    assert res["share"] <= 0.05


def test_roll_check_reds_when_observations_cluster_on_roll_days():
    obs = [{"date": d, "value": 1.0} for d in
           ["2026-03-19", "2026-03-20", "2026-06-18", "2026-06-19",
            "2026-09-17", "2026-09-18", "2026-12-17", "2026-12-18"] * 5]
    obs += [{"date": "2026-02-0%d" % (i % 9 + 1), "value": 1.0} for i in range(10)]
    res = ic.check_roll_date_contamination(obs, [o["value"] for o in obs], 0.0)
    assert res["status"] == "RED"
    assert res["share"] > ic.ROLL_SHARE_RED


# ---------------------------------------------------------------------------
# drift null
# ---------------------------------------------------------------------------

def test_drift_null_greens_when_the_sign_survives_the_null():
    res = ic.check_drift_null([1.0] * 50, null_value=0.2, null_label="drift")
    assert res["status"] == "GREEN"
    assert res["effect_vs_null"] == pytest.approx(0.8)


def test_drift_null_reds_when_the_correct_null_flips_the_sign():
    """An effect of +0.1 against an unconditional drift of +0.3 is a NEGATIVE
    effect that only looked positive because it was measured against zero."""
    res = ic.check_drift_null([0.1] * 50, null_value=0.3, null_label="unconditional drift")
    assert res["status"] == "RED"
    assert res["effect_vs_null"] < 0


def test_drift_null_is_insufficient_below_the_floor():
    assert ic.check_drift_null([1.0] * 5, 0.0, "zero")["status"] == "INSUFFICIENT"


# ---------------------------------------------------------------------------
# concentration
# ---------------------------------------------------------------------------

def test_concentration_greens_on_an_evenly_spread_effect():
    res = ic.check_concentration([0.5] * 200, 0.0)
    assert res["status"] == "GREEN"


def test_concentration_reds_when_a_few_observations_carry_the_result():
    vals = [0.0] * 190 + [50.0] * 10
    res = ic.check_concentration(vals, 0.0)
    assert res["status"] == "RED"
    assert res["share_of_effect"] > 0.5


def test_concentration_share_above_one_is_valid_not_a_bug():
    """A small net effect left over from large offsetting contributions is a
    STRONGER version of the defect, not a broken calculation."""
    vals = [-1.0] * 100 + [1.0] * 98 + [20.0] * 2
    res = ic.check_concentration(vals, 0.0)
    assert res["status"] == "RED"
    assert res["share_of_effect"] > 1.0


# ---------------------------------------------------------------------------
# subperiod stability
# ---------------------------------------------------------------------------

def test_subperiod_greens_when_both_halves_agree():
    rng = np.random.default_rng(0)
    vals = list(rng.normal(1.0, 0.3, 400))
    res = ic.check_subperiod_stability(_obs(vals), vals, 0.0)
    assert res["status"] == "GREEN"


def test_subperiod_reds_when_one_era_carries_a_sign_change():
    """Deterministic on purpose: the second half's mean has to be reliably
    negative but with a CI that still crosses zero, and drawing that from an
    RNG makes the test's own verdict a coin flip."""
    noise = list(np.linspace(-0.35, 0.35, 200))          # symmetric, sums to 0
    first = [1.0 + x for x in noise]                      # mean +1.00, credible
    second = [-0.02 + x for x in noise]                   # mean -0.02, CI crosses 0
    vals = first + second
    res = ic.check_subperiod_stability(_obs(vals), vals, 0.0)
    assert res["first_half"]["credible"] is True
    assert res["second_half"]["credible"] is False
    assert res["signs_differ"] is True
    assert res["status"] == "RED"


# ---------------------------------------------------------------------------
# cost sensitivity
# ---------------------------------------------------------------------------

def test_cost_sensitivity_not_applicable_without_risk_points():
    """A range ratio has no round-trip cost; assuming one would be fabricating."""
    res = ic.check_cost_sensitivity([{"date": "2020-01-01"}] * 50, [1.0] * 50, 0.0)
    assert res["status"] == "NOT APPLICABLE"


def test_cost_sensitivity_reds_when_a_thin_edge_dies_at_2x_costs():
    """A +0.02R edge on a 20-point stop is smaller than the 2x round-trip cost
    (0.075R), so under stress it lands credibly BELOW zero. The first version
    of this check greened that, because its CI no longer crossed the null --
    it had simply moved to the wrong side of it."""
    noise = list(np.linspace(-0.8, 0.8, 300))            # symmetric, sums to 0
    vals = [0.02 + x for x in noise]                      # mean exactly +0.02R
    res = ic.check_cost_sensitivity(_obs(vals, risk_points=20.0), vals, 0.0)
    assert res["mean_1x"] > 0 and res["mean_2x"] < 0
    assert res["sign_flips"] is True
    assert res["status"] == "RED"


def test_cost_sensitivity_greens_when_the_edge_is_far_larger_than_costs():
    rng = np.random.default_rng(3)
    vals = list(rng.normal(1.5, 0.3, 300))
    res = ic.check_cost_sensitivity(_obs(vals, risk_points=50.0), vals, 0.0)
    assert res["status"] == "GREEN"


# ---------------------------------------------------------------------------
# placebo -- including the persistent-state overlap guard
# ---------------------------------------------------------------------------

def test_placebo_not_applicable_without_population_and_mask():
    """The most dangerous possible green: a placebo that 'passes' because it
    never ran."""
    res = ic.check_placebo(None, None, 0.0, real_effect=1.0)
    assert res["status"] == "NOT APPLICABLE"


def test_placebo_reds_when_the_inverted_signal_works_just_as_well():
    rng = np.random.default_rng(4)
    pop = rng.normal(1.0, 0.1, 400)          # every day has the same effect
    mask = np.zeros(400, dtype=bool); mask[::2] = True   # an arbitrary selector
    res = ic.check_placebo(pop, mask, 0.0)
    assert res["status"] == "RED"


def test_placebo_greens_when_only_the_selected_days_carry_the_effect():
    pop = np.zeros(400)
    mask = np.zeros(400, dtype=bool); mask[:120] = True
    pop[:120] = 1.0
    res = ic.check_placebo(pop, mask, 0.0)
    assert res["status"] == "GREEN"


def test_shifted_placebo_cannot_gate_a_persistent_state():
    """THE SECOND FALSE-RED REGRESSION. hyp-000142's signal (a VXN tercile) has
    P(HIGH tomorrow | HIGH today) ~= 0.79, so the t+1 'placebo' re-selects ~79%
    of the real sample and reproduces the effect by construction. It must be
    REPORTED but must not gate; the inverted leg still does."""
    pop = np.zeros(600)
    mask = np.zeros(600, dtype=bool)
    mask[:300] = True                 # one long persistent block -> high t+1 overlap
    pop[:300] = 1.0
    res = ic.check_placebo(pop, mask, 0.0)
    assert res["shifted_overlap_with_real"] > ic.SHIFT_OVERLAP_MAX
    assert "shifted_t+1" not in res["gating_legs"]
    assert res["placebo_effects"]["shifted_t+1"] is not None   # still reported
    assert res["status"] == "GREEN"


def test_shifted_placebo_still_gates_when_the_signal_is_not_persistent():
    """The guard must not become a blanket excuse: an alternating (non-
    persistent) signal has near-zero overlap, so the shifted leg gates."""
    rng = np.random.default_rng(5)
    pop = rng.normal(1.0, 0.1, 400)
    mask = np.zeros(400, dtype=bool); mask[::2] = True
    res = ic.check_placebo(pop, mask, 0.0)
    assert res["shifted_overlap_with_real"] <= ic.SHIFT_OVERLAP_MAX
    assert "shifted_t+1" in res["gating_legs"]


# ---------------------------------------------------------------------------
# the suite as a whole
# ---------------------------------------------------------------------------

def test_suite_reports_checks_that_did_not_run_separately_from_greens():
    """A NOT APPLICABLE is not a pass, and the Gate has to be told which is
    which -- that is the whole contract of this file."""
    vals = [0.5] * 200
    res = ic.run_suite(_obs(vals), null_value=0.0, candidate="t")
    assert len(res["checks"]) == 7
    assert "7. placebo" in res["not_run"]
    assert "2. overnight_intraday_split" in res["not_run"]
    greens = [c for c in res["checks"] if c["status"] == "GREEN"]
    assert len(greens) + len(res["not_run"]) + len(res["reds"]) == 7


def test_suite_flags_any_red_and_says_a_red_does_not_close_a_candidate():
    vals = [0.0] * 190 + [50.0] * 10
    res = ic.run_suite(_obs(vals), null_value=0.0, candidate="t")
    assert res["any_red"] is True
    assert "BLOCKING FINDING" in res["rule"]
    assert "not an automatic close" in res["rule"]


def test_bootstrap_ci_is_seeded_and_reproducible():
    """A verdict must not change between runs of the same input."""
    rng = np.random.default_rng(6)
    v = list(rng.normal(0.5, 1.0, 200))
    assert ic.bootstrap_ci(v, n_boot=2000, seed=0) == ic.bootstrap_ci(v, n_boot=2000, seed=0)
