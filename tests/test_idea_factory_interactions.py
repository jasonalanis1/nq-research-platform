"""Tests for src/idea_factory.py's pairwise interaction mode (U28).

These cover the parts that decide whether the look table is LEGITIMATE --
the timing rule on both layers, the context/trigger ordering, and the
additive contrast that keeps a main effect from masquerading as an
interaction. The data-dependent parts (tercile cuts, window outcomes) are
shared with the single-state mode via build_frame() and are exercised by
running the engine itself.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

import idea_factory as f  # noqa: E402


# --------------------------------------------------------------------------
# the timing rule, applied to BOTH layers
# --------------------------------------------------------------------------

def test_pair_is_circular_when_either_layer_is_late():
    """vwap_dist_vs_atr is known at the close; pairing it with anything
    against the same session's RTH window is the circularity the single-state
    rule already drops, and a pair is only as legitimate as its worst layer."""
    assert f.classify_pair("vwap_dist_vs_atr", "range_vs_atr", "rth", "move") == "CIRCULAR"
    assert f.classify_pair("range_vs_atr", "vwap_dist_vs_atr", "rth", "move") == "CIRCULAR"


def test_pair_is_circular_when_the_late_layer_is_only_marginally_late():
    """opening_range_vs_atr is known at 10:00, so it cannot be crossed with
    the 09:30-10:00 window it is part of, nor with the full RTH range that
    contains it."""
    assert f.classify_pair("range_vs_atr", "opening_range_vs_atr", "first30", "range") == "CIRCULAR"
    assert f.classify_pair("range_vs_atr", "opening_range_vs_atr", "rth", "range") == "CIRCULAR"
    # but it IS legitimate against a window that starts after 10:00
    assert f.classify_pair("range_vs_atr", "opening_range_vs_atr", "midday", "range") != "CIRCULAR"


def test_pair_survives_when_both_layers_are_known_before_the_window():
    assert f.classify_pair("range_vs_atr", "day_of_week", "rth", "move") == "CANDIDATE"


def test_both_validated_volatility_states_on_a_size_outcome_is_a_restatement():
    assert f.classify_pair("range_vs_atr", "vxn_level_vs_trailing", "rth", "range") == "KNOWN"
    # ...but the same pair against a DIRECTIONAL outcome is not a restatement
    assert f.classify_pair("range_vs_atr", "vxn_level_vs_trailing", "rth", "move") == "CANDIDATE"


def test_one_validated_state_plus_a_novel_one_is_not_auto_known():
    """The interaction with a non-range state is the part that could be new;
    the additive contrast (tested below) is what stops its main effect from
    carrying the cell."""
    assert f.classify_pair("range_vs_atr", "day_of_week", "rth", "range") == "CANDIDATE"


# --------------------------------------------------------------------------
# context must be known no later than the trigger
# --------------------------------------------------------------------------

def test_earlier_known_state_becomes_the_context():
    # range_vs_atr is known at the prior close; gap_vs_atr needs the 09:30 open
    assert f.context_orderings("range_vs_atr", "gap_vs_atr") == [("range_vs_atr", "gap_vs_atr")]
    # argument order must not change the answer
    assert f.context_orderings("gap_vs_atr", "range_vs_atr") == [("range_vs_atr", "gap_vs_atr")]


def test_a_timing_tie_emits_both_orderings():
    """When both are known at the same moment either could serve as the
    context, so the table must not silently pick one."""
    out = f.context_orderings("range_vs_atr", "day_of_week")
    assert set(out) == {("range_vs_atr", "day_of_week"), ("day_of_week", "range_vs_atr")}
    assert len(out) == 2


def test_every_known_at_state_has_a_defined_ordering():
    states = list(f.KNOWN_AT)
    for i, a in enumerate(states):
        for b in states[i + 1:]:
            orderings = f.context_orderings(a, b)
            assert orderings, f"no ordering for {a} x {b}"
            for ctx, trg in orderings:
                assert f.KNOWN_AT[ctx] <= f.KNOWN_AT[trg]


# --------------------------------------------------------------------------
# the additive contrast -- a main effect must not look like an interaction
# --------------------------------------------------------------------------

def test_additive_prediction_is_the_sum_of_the_two_departures():
    # all days 1.0; context runs +0.3 above it; trigger runs -0.1 below it
    assert f.additive_prediction(1.3, 0.9, 1.0) == pytest.approx(1.2)


def test_pure_main_effect_has_zero_interaction():
    """A cell that lands exactly where the two separate effects predict has
    NO interaction, even though it sits far from the all-days mean -- this is
    the case that dominated run 1 when the table was ranked by distance from
    the trigger-alone mean instead."""
    all_mean, ctx_alone, trg_alone = 0.60, 0.73, 0.60
    cell = f.additive_prediction(ctx_alone, trg_alone, all_mean)
    assert cell == pytest.approx(0.73)
    assert cell - f.additive_prediction(ctx_alone, trg_alone, all_mean) == pytest.approx(0.0)
    # the same cell IS far from the all-days mean -- which is exactly why
    # ranking on that distance re-surfaces known volatility facts
    assert abs(cell - all_mean) > 0.1


def test_additive_prediction_is_none_when_a_leg_is_below_the_floor():
    assert f.additive_prediction(None, 0.5, 0.4) is None
    assert f.additive_prediction(0.5, None, 0.4) is None


# --------------------------------------------------------------------------
# floors and thresholds
# --------------------------------------------------------------------------

def test_pair_floor_matches_the_conditional_stack_occurrence_floor():
    """A cell below the stack's own occurrence floor cannot source a testable
    stack, so ranking it would only invite a spec that dies UNDERPOWERED."""
    assert f.MIN_N_PAIR == 100


def test_interaction_threshold_is_descriptive_not_a_test_bar():
    assert f.INTERACTION_Z < 3.0   # deliberately looser than a test would be
