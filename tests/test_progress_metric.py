"""Tests for the progress metric: trials spent since the last survivor.

Driven off constructed ledgers and scan registries so each rule is
provably able to fail. The point of this metric is that it is
uncomfortable and hard to flatter -- these tests exist to keep it that
way.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import progress_metric  # noqa: E402


def row(hid, name, slice_used, status="PROMISING", logged="2026-09-09T00:00:00"):
    return {
        "hypothesis_id": hid,
        "strategy_name": name,
        "data_slice_used": slice_used,
        "strategy_status": status,
        "logged_at": logged,
    }


@pytest.fixture
def fake(monkeypatch):
    """Swap in a constructed ledger and scan registry."""
    state = {"rows": [], "registry": {}}

    def install():
        import research_ledger
        import project_wide_multiplicity
        monkeypatch.setattr(research_ledger, "get_current_state", lambda: state["rows"])
        monkeypatch.setattr(project_wide_multiplicity, "SCAN_REGISTRY", state["registry"])

    state["install"] = install
    return state


def test_counts_cells_from_scans_after_the_producing_scan(fake):
    fake["rows"] = [
        row("hyp-000010", "winner", "discovery"),
        row("hyp-000011", "winner_validation", "validation", "VALIDATION CANDIDATE"),
    ]
    fake["registry"] = {
        "scan_001_2026-09-09": {"cells_scanned": 40, "promoted_hypothesis_ids": []},
        "scan_002_2026-09-09": {"cells_scanned": 20, "promoted_hypothesis_ids": ["hyp-000010"]},
        "scan_003_2026-09-09": {"cells_scanned": 30, "promoted_hypothesis_ids": []},
        "scan_004_2026-09-10": {"cells_scanned": 15, "promoted_hypothesis_ids": []},
    }
    fake["install"]()
    out = progress_metric.compute()
    # scans 3 and 4 came after the scan that produced the survivor
    assert out["trials_since_last_survivor"] == 45
    # hyp-000010 came from scan_002, so it is already inside those 20 cells
    assert out["trials_total"] == 105
    assert out["scans_with_no_survivor"] == 3


def test_same_idea_at_two_stages_is_one_survivor(fake):
    """H118 sits at Validation and at Holdout. That is one survivor."""
    fake["rows"] = [
        row("hyp-000121", "vwap_dist_low_10d_drift_h118", "discovery"),
        row("hyp-000122", "vwap_dist_low_10d_drift_h118_prospective", "validation", "VALIDATION CANDIDATE"),
        row("hyp-000123", "vwap_dist_low_10d_drift_h118_holdout", "holdout_gen2", "HOLDOUT PASSED"),
    ]
    fake["registry"] = {"scan_002_2026-09-09": {"cells_scanned": 44, "promoted_hypothesis_ids": ["hyp-000121"]}}
    fake["install"]()
    assert progress_metric.compute()["survivors_alive"] == 1


def test_prospective_never_counts_as_a_survivor(fake):
    """EXP-047 is tracked prospectively and never earned a Validation
    slot. Letting it reset the counter would flatter the number."""
    fake["rows"] = [row("hyp-000020", "weekly_trend_exp047", "prospective", "FORWARD VALIDATION")]
    fake["registry"] = {"scan_001_2026-09-09": {"cells_scanned": 48, "promoted_hypothesis_ids": []}}
    fake["install"]()
    out = progress_metric.compute()
    assert out["survivors_alive"] == 0
    assert out["trials_since_last_survivor"] == 48


def test_a_rejected_candidate_does_not_reset_the_counter(fake):
    """A reset it did not earn is the obvious way to game this."""
    fake["rows"] = [
        row("hyp-000030", "dead_idea", "discovery", "REJECTED"),
        row("hyp-000031", "dead_idea_validation", "validation", "REJECTED"),
    ]
    fake["registry"] = {
        "scan_001_2026-09-09": {"cells_scanned": 10, "promoted_hypothesis_ids": ["hyp-000030"]},
        "scan_002_2026-09-09": {"cells_scanned": 25, "promoted_hypothesis_ids": []},
    }
    fake["install"]()
    out = progress_metric.compute()
    assert out["survivors_alive"] == 0
    assert out["trials_since_last_survivor"] == 35  # every cell still counts


def test_bookkeeping_rows_are_ignored(fake):
    fake["rows"] = [
        row("hyp-000200", "thing_MULTIPLICITY_REEXPRESSION", "validation", "HOLDOUT PASSED"),
    ]
    fake["registry"] = {"scan_001_2026-09-09": {"cells_scanned": 12, "promoted_hypothesis_ids": []}}
    fake["install"]()
    assert progress_metric.compute()["survivors_alive"] == 0


def test_counter_climbs_when_nothing_survives(fake):
    """The core behaviour: scan more, find nothing, number goes up."""
    fake["rows"] = []
    fake["registry"] = {"scan_001_2026-09-09": {"cells_scanned": 48, "promoted_hypothesis_ids": []}}
    fake["install"]()
    first = progress_metric.compute()["trials_since_last_survivor"]
    fake["registry"]["scan_002_2026-09-10"] = {"cells_scanned": 36, "promoted_hypothesis_ids": []}
    fake["install"]()
    second = progress_metric.compute()["trials_since_last_survivor"]
    assert second > first
    assert second - first == 36


def test_idea_key_strips_stage_suffixes():
    assert progress_metric.idea_key("foo_prospective_validation") == "foo"
    assert progress_metric.idea_key("foo_holdout") == "foo"
    assert progress_metric.idea_key("foo") == "foo"
