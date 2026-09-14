"""Tests for src/stack_spec.py and the stack registry (U25 / S1)."""
import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import stack_spec as ss  # noqa: E402
import project_wide_multiplicity as pwm  # noqa: E402


def base_spec():
    return {
        "stack_id": "test_stack", "family": "test_family",
        "layers": [
            {"role": "context", "variable": "expected_range_mult", "edges": "top tercile",
             "known_at": -480, "mechanism": "volatility persists day to day"},
            {"role": "trigger", "variable": "orb_break", "edges": "close beyond 09:30-10:00 range",
             "known_at": 600, "mechanism": "momentum participants key on the opening range"},
        ],
        "trigger_window_start": 600,
        "interaction_claim": "a breakout of a wide-expected day has room to run; the same breakout on a "
                             "compressed-expected day is the fade this project's own facts predict",
        "outcome": "R to first of target/stop/time exit", "horizon": "same session",
        "exit": "stop opposite side, target 1x range width, time exit 15:55",
        "cost_model": "1 tick slippage + commission per side", "floor_occurrences": 100,
        "mde": "0.06R difference at n=100 per cell, 80% power", "paired": True,
        "data_slice": "discovery", "mechanism_doc": "research/mechanisms/test.md",
        "look_cells_k": 12, "pre_registered_cells": 4,
    }


def test_valid_spec_passes_and_hashes():
    s = base_spec()
    assert ss.validate(s) is s
    assert len(ss.spec_hash(s)) == 64


def test_any_change_is_a_different_hash():
    a = base_spec()
    for change in ({"floor_occurrences": 150}, {"horizon": "next session"},
                   {"cost_model": "2 ticks slippage + commission per side"}):
        b = copy.deepcopy(a); b.update(change)
        assert ss.spec_hash(b) != ss.spec_hash(a)
    c = copy.deepcopy(a); c["layers"][0]["edges"] = "top quartile"
    assert ss.spec_hash(c) != ss.spec_hash(a)


def test_out_of_time_order_layers_rejected():
    s = base_spec()
    s["layers"][0]["known_at"] = 700  # context known after the trigger
    with pytest.raises(ss.StackSpecError) as e:
        ss.validate(s)
    assert "timing rule" in str(e.value)


def test_layer_ceiling_follows_whether_the_format_has_a_result():
    """Rule 1: 2 layers until the format has produced one result, 3 after.
    Stack A closed as a powered null on 2026-09-13, so the flag is now True."""
    s = base_spec()
    s["layers"].insert(1, {"role": "location", "variable": "pullback_atr", "edges": ">=0.5 ATR",
                           "known_at": 540, "mechanism": "inventory imbalance"})
    with pytest.raises(ss.StackSpecError) as e:
        ss.validate(s, format_has_result=False)
    assert "ceiling is 2" in str(e.value)
    ss.validate(s, format_has_result=True)
    ss.validate(s)  # module default, now that the format has a result
    four = base_spec()
    for extra in ("location", "location"):
        four["layers"].insert(1, {"role": extra, "variable": "x", "edges": "y",
                                  "known_at": 500, "mechanism": "z"})
    with pytest.raises(ss.StackSpecError):
        ss.validate(four, format_has_result=True)


def test_missing_interaction_claim_or_per_layer_mechanism_rejected():
    s = base_spec(); s["interaction_claim"] = ""
    with pytest.raises(ss.StackSpecError) as e:
        ss.validate(s)
    assert "interaction_claim" in str(e.value)
    s = base_spec(); s["layers"][0]["mechanism"] = "  "
    with pytest.raises(ss.StackSpecError) as e:
        ss.validate(s)
    assert "own mechanism" in str(e.value)


def test_floor_and_mde_and_paired_are_enforced():
    for change in ({"floor_occurrences": 40}, {"mde": ""}, {"paired": False}):
        s = base_spec(); s.update(change)
        with pytest.raises(ss.StackSpecError):
            ss.validate(s)


def test_paired_stack_costs_two_trials():
    assert ss.trials_cost(base_spec()) == 2


def test_register_stack_refuses_a_changed_spec_under_the_same_id():
    reg = {}
    h = pwm.register_stack("s1", base_spec(), scan_key="scan_999", registry=reg)
    assert reg["s1"]["spec_hash"] == h and reg["s1"]["trials"] == 2
    assert pwm.stacks_attempted(reg) == 1
    changed = base_spec(); changed["floor_occurrences"] = 200
    with pytest.raises(ValueError) as e:
        pwm.register_stack("s1", changed, scan_key="scan_999", registry=reg)
    assert "DIFFERENT trial" in str(e.value)
