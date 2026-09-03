"""
Tests for larry_validate.py -- the DSR/PBO wiring between purgedcv and
research_ledger.py.

Focus: the 2026-09-03 trial-counting fix (_family_via_lineage() and the
n_trials_override parameter), since that's the part that changed. The
DSR/PBO math itself is purgedcv's responsibility, not re-tested here.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import larry_validate as lv  # noqa: E402


# ---------------------------------------------------------------------------
# _family_via_lineage -- synthetic ledger-shaped records, no file I/O
# ---------------------------------------------------------------------------

def _rec(hid, parent=None):
    return {"hypothesis_id": hid, "parent_hypothesis_id": parent}


def test_family_via_lineage_root_with_no_children_returns_1():
    current = [_rec("hyp-000001")]
    assert lv._family_via_lineage("hyp-000001", current) == 1


def test_family_via_lineage_groups_parent_and_child():
    current = [_rec("hyp-000001"), _rec("hyp-000007", parent="hyp-000001")]
    assert lv._family_via_lineage("hyp-000001", current) == 2
    assert lv._family_via_lineage("hyp-000007", current) == 2


def test_family_via_lineage_groups_multiple_children_of_same_root():
    current = [
        _rec("hyp-000001"),
        _rec("hyp-000007", parent="hyp-000001"),
        _rec("hyp-000009", parent="hyp-000001"),
    ]
    assert lv._family_via_lineage("hyp-000009", current) == 3


def test_family_via_lineage_does_not_group_across_different_roots():
    # This is the documented, disclosed limitation: hyp-000007 (parent
    # hyp-000001) and hyp-000008 (parent hyp-000003) were actually born
    # from ONE joint search, but lineage-walking alone can't see that --
    # it only sees two separate 2-hypothesis families. Callers who know
    # the real batch boundary must use n_trials_override instead.
    current = [
        _rec("hyp-000001"),
        _rec("hyp-000007", parent="hyp-000001"),
        _rec("hyp-000003"),
        _rec("hyp-000008", parent="hyp-000003"),
    ]
    assert lv._family_via_lineage("hyp-000007", current) == 2
    assert lv._family_via_lineage("hyp-000008", current) == 2


def test_family_via_lineage_unknown_hypothesis_returns_1():
    current = [_rec("hyp-000001")]
    assert lv._family_via_lineage("hyp-999999", current) == 1


def test_family_via_lineage_handles_cyclic_parent_chain_without_hanging():
    # A corrupted ledger shouldn't be able to cause infinite recursion.
    current = [
        _rec("hyp-A", parent="hyp-B"),
        _rec("hyp-B", parent="hyp-A"),
    ]
    # Should return *some* finite int, not hang or raise.
    result = lv._family_via_lineage("hyp-A", current)
    assert isinstance(result, int)
    assert result >= 1


def test_family_via_lineage_three_generation_chain():
    current = [
        _rec("hyp-000001"),
        _rec("hyp-000007", parent="hyp-000001"),
        _rec("hyp-000020", parent="hyp-000007"),  # grandchild
    ]
    assert lv._family_via_lineage("hyp-000020", current) == 3
    assert lv._family_via_lineage("hyp-000001", current) == 3


# ---------------------------------------------------------------------------
# evaluate_candidate -- n_trials_override vs. lineage fallback
# ---------------------------------------------------------------------------

class _FakeRecord:
    """Minimal stand-in so evaluate_candidate()'s `record is None` guard
    passes without touching the real ledger file."""
    pass


@pytest.fixture
def patched_ledger(monkeypatch):
    """Patch research_ledger's lookup functions so evaluate_candidate()
    runs against an in-memory fake ledger instead of the real file."""
    current_state = [
        _rec("hyp-000001"),
        _rec("hyp-000007", parent="hyp-000001"),
        _rec("hyp-000003"),
        _rec("hyp-000008", parent="hyp-000003"),
    ]

    def fake_get_current_state(ledger_path=None):
        return current_state

    def fake_get_latest(hid, ledger_path=None):
        return _FakeRecord() if hid in {r["hypothesis_id"] for r in current_state} else None

    monkeypatch.setattr(lv.rl, "get_current_state", fake_get_current_state)
    monkeypatch.setattr(lv.rl, "get_latest", fake_get_latest)
    return current_state


def _fake_returns(seed, n_configs=4, n_obs=200, edge_on=None):
    rng = np.random.RandomState(seed)
    returns = rng.normal(0, 1.0, size=(n_configs, n_obs))
    if edge_on is not None:
        returns[edge_on] += 0.5
    return returns


def test_evaluate_candidate_uses_override_when_given(patched_ledger):
    returns = _fake_returns(seed=1, n_configs=4, edge_on=0)
    verdict = lv.evaluate_candidate(
        "hyp-000007", returns[0], sibling_returns=returns, n_trials_override=4,
    )
    assert verdict.n_trials_considered == 4


def test_evaluate_candidate_falls_back_to_lineage_without_override(patched_ledger):
    returns = _fake_returns(seed=2, n_configs=4, edge_on=0)
    verdict = lv.evaluate_candidate("hyp-000007", returns[0], sibling_returns=returns)
    # No override given -> lineage-only counts hyp-000001+hyp-000007 = 2,
    # NOT the true joint-search size of 4 (the documented gap).
    assert verdict.n_trials_considered == 2


def test_evaluate_candidate_raises_on_unknown_hypothesis(patched_ledger):
    returns = _fake_returns(seed=3, n_configs=4)
    with pytest.raises(ValueError):
        lv.evaluate_candidate("hyp-999999", returns[0], sibling_returns=returns)


def test_evaluate_candidate_rejects_when_dsr_below_threshold(patched_ledger):
    # Pure noise, no planted edge, n_trials_override large -> DSR should
    # come in well below the 0.90 pass threshold.
    returns = _fake_returns(seed=4, n_configs=4, edge_on=None)
    verdict = lv.evaluate_candidate(
        "hyp-000007", returns[0], sibling_returns=returns, n_trials_override=50,
    )
    assert verdict.recommended_status == "REJECTED"
    assert "DSR" in verdict.reasoning


def test_evaluate_candidate_without_sibling_returns_skips_pbo(patched_ledger):
    returns = _fake_returns(seed=5, n_configs=4, edge_on=0)
    verdict = lv.evaluate_candidate(
        "hyp-000007", returns[0], sibling_returns=None, n_trials_override=1,
    )
    assert verdict.pbo is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
