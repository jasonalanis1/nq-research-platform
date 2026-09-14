"""U24 -- status-transition guard. In THIS ledger 'VALIDATION CANDIDATE' means
PASSED Validation, Holdout next; pre-Validation candidates are PROMISING.
hyp-000156 was mislabelled on 2026-09-13 and ops_checks flagged a Holdout slot
that was not owed; this is the guard that makes that impossible."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import research_ledger as rl  # noqa: E402


@pytest.fixture()
def ledger(tmp_path):
    return tmp_path / "ledger.jsonl"


def _log(ledger, slice_used="discovery", status="PROMISING", name="t"):
    return rl.log_hypothesis(strategy_name=name, strategy_origin="data_discovered",
                             parameters={}, data_slice_used=slice_used, trade_count=100,
                             expectancy_r=0.1, strategy_status=status, ledger_path=ledger)


def test_promotion_to_validation_candidate_is_refused_without_a_validation_row(ledger):
    h = _log(ledger).hypothesis_id
    with pytest.raises(ValueError) as e:
        rl.update_status(h, "VALIDATION CANDIDATE", ledger_path=ledger)
    assert "no ledger row with data_slice_used='validation'" in str(e.value)
    assert "PROMISING" in str(e.value)


def test_every_post_validation_status_is_guarded(ledger):
    h = _log(ledger).hypothesis_id
    for st in ("HOLDOUT PASSED", "FORWARD VALIDATION", "PAPER VERIFIED"):
        with pytest.raises(ValueError):
            rl.update_status(h, st, ledger_path=ledger)


def test_promising_and_rejected_are_always_allowed(ledger):
    h = _log(ledger).hypothesis_id
    assert rl.update_status(h, "PROMISING", ledger_path=ledger).strategy_status == "PROMISING"
    assert rl.update_status(h, "REJECTED", ledger_path=ledger).strategy_status == "REJECTED"


def test_promotion_allowed_once_a_validation_slice_row_exists(ledger):
    h = _log(ledger).hypothesis_id
    rl.log_hypothesis(strategy_name="t", strategy_origin="data_discovered", parameters={},
                      data_slice_used="validation", trade_count=120, expectancy_r=0.12,
                      strategy_status="PROMISING", ledger_path=ledger)
    # the validation row is a separate id; the guard is per-hypothesis, so this must still fail
    with pytest.raises(ValueError):
        rl.update_status(h, "VALIDATION CANDIDATE", ledger_path=ledger)
    assert rl.has_validation_row(h, ledger) is False


def test_has_validation_row_reads_the_same_hypothesis_only(ledger):
    h = _log(ledger).hypothesis_id
    assert rl.has_validation_row(h, ledger) is False
