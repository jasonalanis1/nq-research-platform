"""Tests for src/risk_state_engine.py (bot milestone B2). Pure-logic tests -- no
price data needed, so they run in the normal suite."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import risk_state_engine as rse  # noqa: E402
from volatility_conditioning import MIN_SIZE_MULT, MAX_SIZE_MULT, position_size_multiplier  # noqa: E402


def test_residual_combination_uses_only_retained_share():
    # VXN HIGH must add (ratio-1)*retention, never the raw 1.2389
    assert rse._combine(1.0, True) == round(1.0 + (rse.VXN_HIGH_RATIO - 1) * rse.VXN_RESIDUAL_RETENTION, 4)
    assert rse._combine(1.0, True) < rse.VXN_HIGH_RATIO
    assert rse._combine(1.0, False) == 1.0


def test_residual_combination_is_multiplicative_on_base():
    base = 0.9438  # prior_day_narrow ratio
    assert rse._combine(base, True) == round(base * (1 + (rse.VXN_HIGH_RATIO - 1) * rse.VXN_RESIDUAL_RETENTION), 4)


def test_stop_and_target_are_frozen_fractions_of_expected_range():
    d = rse.decide(1.0, False, range_avg_points=200.0, atr14_points=100.0, permission_edge=0.5,
                   is_event_day=False, stale=False)
    assert d["expected_range_atr"] == 2.0
    assert d["stop_distance_atr"] == rse.STOP_FRACTION * 2.0
    assert d["target_distance_atr"] == rse.TARGET_FRACTION * 2.0
    assert rse.STOP_FRACTION == 0.5 and rse.TARGET_FRACTION == 1.0


def test_size_multiplier_matches_conditioning_module_and_is_clipped():
    d = rse.decide(0.5, False, 200.0, 100.0, 0.1, False, False)
    assert d["size_multiplier"] == position_size_multiplier(0.5)
    assert MIN_SIZE_MULT <= d["size_multiplier"] <= MAX_SIZE_MULT
    d2 = rse.decide(5.0, False, 200.0, 100.0, 0.1, False, False)
    assert d2["size_multiplier"] == MIN_SIZE_MULT


def test_permission_false_on_bottom_decile():
    d = rse.decide(0.80, False, 200.0, 100.0, permission_edge=0.85, is_event_day=False, stale=False)
    assert d["trade_permission"] is False
    assert any("bottom decile" in r for r in d["permission_reasons"])


def test_permission_false_on_event_day_and_stale_data():
    d = rse.decide(1.0, False, 200.0, 100.0, 0.5, is_event_day=True, stale=False)
    assert d["trade_permission"] is False and "scheduled-event day" in d["permission_reasons"]
    d = rse.decide(1.0, False, 200.0, 100.0, 0.5, is_event_day=False, stale=True)
    assert d["trade_permission"] is False and any("stale" in r for r in d["permission_reasons"])


def test_permission_true_when_nothing_blocks():
    d = rse.decide(1.0, True, 200.0, 100.0, 0.5, False, False)
    assert d["trade_permission"] is True and d["permission_reasons"] == []


def test_engine_never_emits_direction_or_pnl():
    d = rse.decide(1.0, True, 200.0, 100.0, 0.5, False, False)
    assert d["direction"] is None
    assert d["pnl_claim"] is None
    assert "expected_return" not in d and "edge" not in d


def test_missing_atr_gives_nan_and_no_permission():
    d = rse.decide(1.0, False, 200.0, 0.0, 0.5, False, False)
    assert math.isnan(d["expected_range_atr"])
    assert d["trade_permission"] is False


# ---------------------------------------------------------------------------
# FAIL CLOSED on stale reference data (2026-09-17, Jason's follow-up 2)
#
# B2 reads two reference series: the VXN level (vxn_level_vs_trailing, the
# hyp-000151 HIGH-tercile input) and the scheduled-macro-event calendar (the
# trade_permission veto). Both used to fail OPEN -- a forward-filled VXN close
# and a scheduled-event file that does not exist. Every live paper row in
# research/forward_validation/bot_stack_paper_log.jsonl (2026-09-08 onward) was
# decided that way; see research/integrity/vxn-stale-paper-rows-2026-09-17.json.
# These tests prove REFUSAL, not a nicer default.
# ---------------------------------------------------------------------------
def test_b2_refuses_a_session_past_the_vxn_series_instead_of_carrying_it_forward():
    from datetime import timedelta
    from reference_data import ReferenceDataUnavailable, vxn_coverage_end
    end = vxn_coverage_end()
    with pytest.raises(ReferenceDataUnavailable) as e:
        rse.require_reference_data(end + timedelta(days=1))
    assert "VXN" in str(e.value)
    assert "size_multiplier" in str(e.value)


def test_b2_refuses_a_session_past_the_macro_calendar_instead_of_assuming_no_event():
    from datetime import timedelta
    from reference_data import ReferenceDataUnavailable, macro_coverage_end
    end = macro_coverage_end()
    with pytest.raises(ReferenceDataUnavailable) as e:
        rse.require_reference_data(end + timedelta(days=1))
    assert "macro calendar" in str(e.value)


def test_b2_accepts_a_session_inside_both_series_and_names_the_coverage():
    from reference_data import macro_coverage_end, vxn_coverage_end
    inside = macro_coverage_end()          # <= the VXN end by construction here
    cov = rse.require_reference_data(inside)
    assert cov["macro_covered_through"] == macro_coverage_end()
    assert cov["vxn_covered_through"] == vxn_coverage_end()


def test_scheduled_event_day_refuses_rather_than_returning_false_past_coverage():
    """The bug this replaces: `_event_days()` read a CSV that has never existed,
    so is_event_day was False for EVERY session B2 ever scored and the
    directive's scheduled-event veto silently never fired."""
    from datetime import timedelta
    from reference_data import ReferenceDataUnavailable, macro_coverage_end
    with pytest.raises(ReferenceDataUnavailable):
        rse._is_scheduled_event_day(macro_coverage_end() + timedelta(days=1))
    assert rse._event_days() == set() or isinstance(rse._event_days(), set)
