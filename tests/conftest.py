"""
conftest.py
============
pytest automatically loads this file before running any tests. Its only
job here is to make sure Python can find the code in src/ when the tests
try to import it -- since src/ isn't normally on Python's search path.

You don't need to understand pytest internals to use this project -- just
know that running `pytest` from the project folder will find and run
every test in tests/ automatically.
"""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))


# ---------------------------------------------------------------------------
# GUARD (added 2026-09-14 ~9:10 pm CT after a real contamination): a test that
# forgot to isolate bot_stack_paper_run's paths wrote FOUR synthetic fills
# (price 135.05, date 2026-01-06) into the LIVE execution journal. That journal
# is the permanent record the whole back half of the roadmap measures against.
# From now on EVERY test runs with the paper loop's log, journal and anchor
# redirected to a temp dir -- no test can reach the live record, whether or not
# its author remembered to monkeypatch.
# ---------------------------------------------------------------------------
import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _never_touch_the_live_execution_record(tmp_path, monkeypatch):
    try:
        import bot_stack_paper_run as _bpr
    except Exception:
        yield
        return
    monkeypatch.setattr(_bpr, "LOG_DIR", tmp_path)
    monkeypatch.setattr(_bpr, "LOG_PATH", tmp_path / "bot_stack_paper_log.jsonl")
    monkeypatch.setattr(_bpr, "JOURNAL_DIR", tmp_path / "order_path_journal")
    monkeypatch.setattr(_bpr, "B7_ANCHOR_PATH", tmp_path / "anchor.json")
    yield
