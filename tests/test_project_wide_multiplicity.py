"""
Tests for project_wide_multiplicity.py -- the stage-specific Sidak
family-wise correction that closes the H118 Integrity Gate's open
"project-wide multiple-testing exposure never quantified" item
(docs/BACKLOG.md, 2026-09-09).

Focus: the meta-row exclusion rule (is a ledger row a real trial or a
pure bookkeeping correction?), the Sidak math itself, and the
stage-specific trial-count wiring -- since applying the WRONG trial
count to the WRONG stage is exactly the mistake this module's own
docstring says an earlier draft made and had to catch before logging a
real result. Not re-testing purgedcv/DSR itself -- that's
larry_validate.py's test file's job, and this module deliberately does
not depend on purgedcv.
"""
import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import project_wide_multiplicity as pwm  # noqa: E402


# ---------------------------------------------------------------------------
# _is_meta_row -- synthetic ledger-shaped records, no file I/O
# ---------------------------------------------------------------------------

def _rec(name, trade_count=None, parameters=None, notes=""):
    return {
        "strategy_name": name,
        "trade_count": trade_count,
        "parameters": parameters or {},
        "notes": notes,
    }


def test_ordinary_hypothesis_is_not_meta():
    assert not pwm._is_meta_row(_rec("vwap_dist_low_10d_drift_h118", trade_count=554))


def test_status_correction_suffix_is_meta():
    assert pwm._is_meta_row(_rec("some_finding_STATUS_CORRECTION", parameters={"corrects": "hyp-000023"}))


def test_progression_pointer_suffix_is_meta():
    assert pwm._is_meta_row(_rec("some_finding_PROGRESSION_POINTER", parameters={"corrects": "hyp-000121"}))


def test_corrects_param_is_meta_even_without_suffix_convention():
    # hyp-000093-style rows: predate the _STATUS_CORRECTION naming convention
    # but still carry a "corrects" key.
    assert pwm._is_meta_row(_rec("cot_positioning_leveraged_money_weekly", parameters={"corrects": "hyp-000063"}))


def test_ledger_hygiene_phrase_without_own_data_is_meta():
    assert pwm._is_meta_row(_rec(
        "intraday_volume_profile_skew_front_and_back_loaded",
        trade_count=None,
        notes="Ledger hygiene correction: left PROMISING from its Discovery-slice pass...",
    ))


def test_ledger_hygiene_phrase_WITH_own_data_is_not_meta():
    # hyp-000091: narratively a "correction" but has its own independent
    # n=85 re-test -- a genuine second trial, must still be counted.
    assert not pwm._is_meta_row(_rec(
        "multiday_pullback_continuation_v2_frequency_increased",
        trade_count=85,
        notes="Ledger hygiene correction: hyp-000079 was left logged as PROMISING even after this project's own v2 re-test grew the sample to n=85...",
    ))


# ---------------------------------------------------------------------------
# sidak_z -- monotonicity and the N=1 no-op case
# ---------------------------------------------------------------------------

def test_sidak_z_at_n_equals_1_matches_single_test_z():
    z = pwm.sidak_z(1)
    assert z == pytest.approx(pwm.Z_90_SINGLE, abs=1e-6)


def test_sidak_z_increases_with_more_trials():
    z_small = pwm.sidak_z(10)
    z_large = pwm.sidak_z(200)
    assert z_large > z_small > pwm.Z_90_SINGLE


# ---------------------------------------------------------------------------
# evaluate() -- the actual survives/fails decision
# ---------------------------------------------------------------------------

def _counts(discovery=1, validation=1, holdout=1):
    return {"discovery": discovery, "validation": validation, "holdout": holdout}


def test_evaluate_survives_when_ci_stays_clear_of_null_after_adjustment():
    # Huge n, tight CI, single trial (N=1) -> adjustment barely widens it.
    v = pwm.evaluate("test", "discovery", 1000, 0.60, (0.55, 0.65), 0.0, _counts(discovery=1))
    assert v.survives_adjustment


def test_evaluate_fails_when_marginal_ci_widens_past_null_under_many_trials():
    # H118 Validation's own real numbers: marginal single-test CI (barely
    # excludes 0), N=18 Validation-stage trials -> should fail.
    counts = _counts(validation=18)
    v = pwm.evaluate(
        "H118 Validation", "validation", 213, 0.2839896940801262,
        (0.047924667873678724, 0.5192995801763663), 0.0, counts,
    )
    assert not v.survives_adjustment
    assert v.adjusted_ci[0] < 0.0 < v.adjusted_ci[1]


def test_evaluate_holdout_stage_with_n_equals_1_is_unadjusted():
    # With only one candidate ever at Holdout, the adjustment must be a
    # no-op. Uses a SYMMETRIC synthetic CI (mean exactly at the CI
    # midpoint) rather than H118's real bootstrap numbers -- a real
    # bootstrap CI is not always exactly centered on the point estimate,
    # so the normal-approximation round-trip (back out SE from the
    # half-width, then re-expand around mean) only reproduces the
    # original CI exactly when the input already was symmetric. That is
    # a disclosed limitation of the method (see module docstring), not
    # something this test should paper over by loosening tolerance on
    # asymmetric real data.
    counts = _counts(holdout=1)
    v = pwm.evaluate("H118 Holdout", "holdout", 187, 0.30, (0.05, 0.55), 0.0, counts)
    assert v.adjusted_ci == pytest.approx(v.single_test_ci_90, abs=1e-9)
    assert v.survives_adjustment


def test_evaluate_at_n_equals_1_approximately_reproduces_asymmetric_real_ci():
    # The real, mildly-asymmetric H118 holdout numbers: N=1 shouldn't
    # move the survives/fails verdict or the CI by more than the
    # inherent symmetric-approximation error (a few percent), even
    # though it won't reproduce the original bounds exactly.
    counts = _counts(holdout=1)
    v = pwm.evaluate(
        "H118 Holdout", "holdout", 187, 0.39594291085440664,
        (0.13649436895644734, 0.6503324231137323), 0.0, counts,
    )
    assert v.survives_adjustment
    assert v.adjusted_ci[0] == pytest.approx(v.single_test_ci_90[0], rel=0.05)
    assert v.adjusted_ci[1] == pytest.approx(v.single_test_ci_90[1], rel=0.05)


def test_evaluate_uses_the_stage_specific_count_not_a_single_global_one():
    # Same CI, same n, different stage -> different trial count -> can
    # flip the verdict. This is the core design point of the module.
    ci = (0.05, 0.55)
    counts = _counts(discovery=178, validation=18, holdout=1)
    v_holdout = pwm.evaluate("x", "holdout", 200, 0.30, ci, 0.0, counts)
    v_discovery = pwm.evaluate("x", "discovery", 200, 0.30, ci, 0.0, counts)
    assert v_holdout.n_trials != v_discovery.n_trials
    assert v_holdout.survives_adjustment and not v_discovery.survives_adjustment


# ---------------------------------------------------------------------------
# compute_stage_trial_counts -- against a small synthetic ledger file
# ---------------------------------------------------------------------------

def test_compute_stage_trial_counts_excludes_meta_rows(tmp_path):
    import json
    ledger = tmp_path / "hypotheses.jsonl"
    rows = [
        {"hypothesis_id": "hyp-000001", "strategy_name": "real_one", "parameters": {},
         "notes": "", "trade_count": 100, "data_slice_used": "discovery"},
        {"hypothesis_id": "hyp-000002", "strategy_name": "real_two", "parameters": {},
         "notes": "", "trade_count": 50, "data_slice_used": "validation"},
        {"hypothesis_id": "hyp-000003", "strategy_name": "real_two_STATUS_CORRECTION",
         "parameters": {"corrects": "hyp-000002"}, "notes": "", "trade_count": None,
         "data_slice_used": "validation"},
        {"hypothesis_id": "hyp-000004", "strategy_name": "real_three", "parameters": {},
         "notes": "", "trade_count": 30, "data_slice_used": "holdout_gen2"},
    ]
    with open(ledger, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    counts = pwm.compute_stage_trial_counts(ledger_path=ledger)
    # hyp-000003 (a correction, no own data) must not inflate the validation count
    assert counts["_detail"]["n_validation_logged"] == 1
    assert counts["_detail"]["n_discovery_logged"] == 1
    assert counts["_detail"]["n_holdout_logged"] == 1
    # discovery total also includes the (constant, real-ledger-derived) unpromoted
    # scan-cell addend from SCAN_REGISTRY, so it's >= the logged count
    assert counts["discovery"] >= counts["_detail"]["n_discovery_logged"]
