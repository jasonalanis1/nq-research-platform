"""
production_paths.py -- the PRODUCTION WRITE GUARD (Jason, refocus memo 7.3,
September 15th: research/infrastructure/refocus-2026-09-15.md).

WHY
  On September 14th a test wrote four synthetic fills into the live execution
  journal. tests/conftest.py then redirected bot_stack_paper_run's paths for
  every test, which fixed that one leak and left the general problem: any
  writer whose author forgot to monkeypatch could still reach a production
  record. Jason: "production paths refuse writes unless an explicit production
  flag is set, so a test cannot reach them by default."

MECHANISM (one, explicit, default-deny)
  A write to a PROTECTED path is refused unless the environment variable
  TONY_PRODUCTION == "1" at the moment of the write. There is no other way in:
  no pytest detection, no argv sniffing, no "looks like a real run" heuristic.
  Two ways the flag gets set:
    1. Ad hoc / one-off scripts:  TONY_PRODUCTION=1 python3 src/<script>.py
       (every scan script that appends to the ledger, every Statistical /
       Validation script, run this way by the cycle).
    2. The standing entry points call enable_production() at the top of their
       main() -- bot_stack_paper_run, b7_replay, bot_forward_log,
       risk_state_engine, forward_validate_h118_daily, batch_screen (frozen,
       but still an entry point), cycle_budget, cycle_close, the Databento
       fetch/top-up scripts. So `python3 src/bot_stack_paper_run.py` keeps
       working unchanged from the command line.
  Tests never set the flag (tests/test_production_paths.py proves a refused
  write; tests/conftest.py asserts the flag is absent for the whole session),
  and enable_production() is never called at import time, only inside main(),
  so importing a module in a test does not open the door. A test that wants
  a writer's behaviour redirects the writer's path to tmp_path, exactly as the
  existing tests do; the guard only looks at PROTECTED paths.

WHAT IS PROTECTED
  PROTECTED_FILES / PROTECTED_TREES / PROTECTED_GLOBS below -- the execution
  record, the ledgers and forward logs, the frozen spec files, the batch-screen
  state, the idea inventory, the strategy registry / revamp list / frozen strategy specs
  (standing directive, September 15th), the per-cycle compliance/history records, and the
  1-minute price series. The full audit of every writer, protected or not, is
  research/integrity/write-path-audit-2026-09-15.md; keep the two in step.

USAGE (in a writer, immediately before the write)
    from production_paths import assert_writable
    assert_writable(path)            # raises ProductionWriteRefused if protected and flag unset
"""
from __future__ import annotations

import os
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAG = "TONY_PRODUCTION"

PROTECTED_FILES = (
    "research/ledger/hypotheses.jsonl",
    "research/ledger/directional_lane.json",
    "research/ledger/prospective_exp047_log.jsonl",
    "research/ledger/strategies.jsonl",          # the strategy registry (standing directive, 2026-09-15)
    "research/ledger/revamp_list.json",          # directive s.9 revamp list
    "research/forward_validation/bot_stack_paper_log.jsonl",
    "research/forward_validation/bot_stack_forward_log.jsonl",
    "research/forward_validation/risk_state_engine_log.jsonl",
    "research/forward_validation/h118_forward_log.jsonl",
    "research/infrastructure/b7-execution-anchor.json",
    "research/infrastructure/risk-state-engine-frozen-params.json",
    "research/_batch_screen_state.json",
    "research/idea_inventory.md",
    "research/_cycle_compliance.jsonl",
    "research/_cycle_history.jsonl",
    "research/ledger/data_coverage.json",          # reference-data coverage state (2026-09-16)
    "data/VXNCLS_MAX.csv",                         # the VXN daily reference series
    "data/macro_event_calendar.csv",               # FOMC/CPI/NFP schedule extension
    "data/macro_event_calendar_coverage.json",     # how far each published schedule was verified
    "data/_reference_data_topup_log.jsonl",        # what each reference top-up added
)
PROTECTED_TREES = (
    "research/forward_validation/order_path_journal",
    "research/forward_validation/b7_replay",
    "research/infrastructure/strategy-specs",    # frozen strategy specs (directive s.13: never edited after FREEZE)
)
PROTECTED_GLOBS = (
    "data/*_1min_*.csv",          # the price series every stage reads
)


class ProductionWriteRefused(PermissionError):
    """Raised when a writer targets a protected production path without the flag."""


def production_enabled() -> bool:
    return os.environ.get(FLAG) == "1"


def enable_production(reason: str = "") -> None:
    """Called ONLY from the main() of a standing entry point (never at import).
    Sets the flag for this process so the writers it drives may write."""
    os.environ[FLAG] = "1"


def _rel(path) -> str | None:
    try:
        return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return None


def _matches(rel: str) -> bool:
    if rel in PROTECTED_FILES:
        return True
    if any(rel == t or rel.startswith(t + "/") for t in PROTECTED_TREES):
        return True
    return any(fnmatch(rel, g) for g in PROTECTED_GLOBS)


def is_protected(path) -> bool:
    p = Path(path)
    # a RELATIVE path (research_ledger's default is one) is judged on its own
    # spelling as well as on its resolution, so running a script from another
    # cwd cannot slip a protected name past the guard
    if not p.is_absolute() and _matches(p.as_posix().lstrip("./")):
        return True
    rel = _rel(p)
    if rel is None:
        return False
    return _matches(rel)


def assert_writable(path, what: str = "") -> Path:
    """The guard. Returns the path so it can be used inline."""
    p = Path(path)
    if is_protected(p) and not production_enabled():
        raise ProductionWriteRefused(
            f"REFUSED write to production path {_rel(p)}{' (' + what + ')' if what else ''}: "
            f"{FLAG}=1 is not set. Tests must redirect this writer to tmp_path; a real run sets "
            f"{FLAG}=1 in the environment or goes through an entry point whose main() calls "
            f"production_paths.enable_production(). See src/production_paths.py.")
    return p


def protected_listing() -> list[str]:
    return list(PROTECTED_FILES) + [t + "/" for t in PROTECTED_TREES] + list(PROTECTED_GLOBS)


if __name__ == "__main__":
    print(f"{FLAG}={'1 (production writes allowed)' if production_enabled() else 'unset (production writes REFUSED)'}")
    for p in protected_listing():
        print("  protected:", p)
