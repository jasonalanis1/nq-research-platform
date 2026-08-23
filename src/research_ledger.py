"""
research_ledger.py
====================

WHAT THIS FILE DOES (plain English):
Logs EVERY hypothesis that gets tested -- not just the ones that turn
out interesting enough to get a full write-up in
research/experiments/_index.md. That's the whole point: _index.md has
always been a curated list of noteworthy runs, which is exactly the
"1,847 hypotheses tested, but you only see the promising 37"
undercount problem docs/RESEARCH_INTEGRITY_PROTOCOL.md's "Prominent
counter" section calls out. This file is the exhaustive, un-curated
backing log that _index.md's curated view sits on top of.

WHY THIS EXISTS: once a Strategy R&D Agent exists (per the protocol,
still gated behind data acquisition + this infrastructure), it may test
hundreds or thousands of parameter variations automatically. If only the
interesting-looking ones get written down, nobody -- not Jason, not
Larry, not future-Jason six months from now -- can tell a real 2.0
Sharpe found after 3 honest attempts apart from a 2.0 Sharpe found by
grinding through 50,000 variations until one looked good by chance. Both
would look identical in a curated results table. This ledger is what
makes that distinction checkable instead of just trusted.

THE THREE-FIELD MODEL (per docs/RESEARCH_INTEGRITY_PROTOCOL.md): every
entry carries Strategy Origin, Strategy Status, and Live Authorization
as three SEPARATE fields, matching the protocol exactly. Live
Authorization defaults to "Not authorized" and this file never sets it
to anything else automatically -- that field only ever changes through
a deliberate, separate, human action, never as a side effect of logging
a test result. See strategy_contract.py's validation_status field for
the related-but-distinct per-Signal status; this file's strategy_status
is about the STRATEGY as a research object, not any one live signal.

STORAGE: an append-only JSONL file (research/ledger/hypotheses.jsonl),
one JSON object per line, one line per hypothesis test. Append-only
matters here for the same reason data_holdout.py's boundary is a fixed
date rather than a percentage: a log you can quietly edit or delete rows
from is a log that can quietly stop being honest. Nothing in this module
exposes a delete or overwrite -- log_hypothesis() only ever appends, and
update_status() appends a NEW record referencing the original by
hypothesis_id rather than mutating the old line in place, so the full
history of a hypothesis's status changes over time stays visible.

HYPOTHESIS_ID is the running global counter the protocol asks for --
it's just "how many lines have ever been appended," zero-padded
(hyp-000001, hyp-000002, ...). No separate counter to keep in sync and
no way for it to drift from the actual log.

STATUS AS OF 2026-08-23: drafted as infrastructure, NOT yet wired into
any detector or the dashboard. Per docs/RESEARCH_INTEGRITY_PROTOCOL.md's
build order, this is safe to build now (decisions are locked, data
acquisition is done) but nothing should write real hypothesis rows here
until Jason has reviewed this file and it's been merged into the actual
repo. The synthetic sanity check at the bottom of this file is NOT real
research data -- delete/ignore that output.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

LEDGER_PATH = Path("research/ledger/hypotheses.jsonl")

# Strategy Origin -- per the three-field model, this is METADATA about
# where an idea came from. It never changes once logged.
VALID_ORIGINS = {
    "external_claim",
    "jason_hypothesis",
    "rd_generated",
    "data_discovered",
    "derivative",
}

# Strategy Status -- the six-state Larry classification, now the single
# official status field per docs/RESEARCH_INTEGRITY_PROTOCOL.md decision #2.
VALID_STATUSES = {
    "REJECTED",
    "PROMISING",
    "VALIDATION CANDIDATE",
    "HOLDOUT PASSED",
    "FORWARD VALIDATION",
    "PAPER VERIFIED",
}

# Live Authorization -- earned eligibility ONLY. Never a substitute for
# CLAUDE.md's real-time per-trade approval requirement. This module
# never sets anything but "not_authorized" on its own.
VALID_AUTHORIZATIONS = {"not_authorized", "human_approved", "automated_approved"}

# Which data slice a test ran against. "discovery" should be the vast
# majority of rows -- validation/holdout_gen2/holdout_gen1 rows are the
# rare, budgeted, should-be-logged-with-extra-care ones.
VALID_DATA_SLICES = {"discovery", "validation", "holdout_gen1", "holdout_gen2"}


@dataclass
class HypothesisRecord:
    """One row in the ledger -- one hypothesis test, one point in time.

    parent_hypothesis_id: set when this test is a variant/mutation of an
      earlier logged hypothesis (e.g. an R&D agent trying a nearby
      parameter value). None for a genuinely new idea. This is what
      makes "hypothesis lineage" (the protocol's phrase) actually
      traceable -- you can walk the parent chain back to see how many
      generations of tweaking produced a given result.
    parameters: the exact parameter values tested, as a plain dict.
      Two rows with the same strategy_name but different parameters are
      different hypotheses, both logged -- this is specifically what
      catches "50,000 near-identical variations" data-dredging, which a
      curated results table would never surface.
    experiment_doc_id: set only if/when this hypothesis earns a full
      write-up in research/experiments/_index.md (e.g. "exp-023"). Most
      rows will have this as None -- that's expected and correct, not
      missing data.
    holdout_slot_id: set only if this hypothesis consumed a formal
      holdout evaluation slot (e.g. "H-001" from the Holdout Generation
      1 ledger table in docs/RESEARCH_INTEGRITY_PROTOCOL.md). None for
      the overwhelming majority of rows, by design -- holdout access is
      rare and budgeted.
    """
    hypothesis_id: str
    logged_at: str
    strategy_name: str
    strategy_origin: str
    parameters: dict
    data_slice_used: str
    trade_count: Optional[int] = None
    expectancy_r: Optional[float] = None
    profit_factor: Optional[float] = None
    max_drawdown_r: Optional[float] = None
    strategy_status: str = "PROMISING"
    live_authorization: str = "not_authorized"
    parent_hypothesis_id: Optional[str] = None
    experiment_doc_id: Optional[str] = None
    holdout_slot_id: Optional[str] = None
    notes: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def _next_hypothesis_id(ledger_path: Path = LEDGER_PATH) -> str:
    """Counts existing lines to determine the next ID. Deliberately not a
    stored counter variable -- the ledger file itself is the only source
    of truth, so the count can never drift out of sync with it."""
    if not ledger_path.exists():
        n = 0
    else:
        with open(ledger_path, "r") as f:
            n = sum(1 for line in f if line.strip())
    return f"hyp-{n + 1:06d}"


def log_hypothesis(
    strategy_name: str,
    strategy_origin: str,
    parameters: dict,
    data_slice_used: str,
    trade_count: Optional[int] = None,
    expectancy_r: Optional[float] = None,
    profit_factor: Optional[float] = None,
    max_drawdown_r: Optional[float] = None,
    strategy_status: str = "PROMISING",
    parent_hypothesis_id: Optional[str] = None,
    notes: str = "",
    ledger_path: Path = LEDGER_PATH,
) -> HypothesisRecord:
    """Appends one new hypothesis test to the ledger. This is the ONLY
    way new rows get created -- always a fresh append, never an edit."""
    if strategy_origin not in VALID_ORIGINS:
        raise ValueError(f"strategy_origin must be one of {VALID_ORIGINS}, got {strategy_origin!r}")
    if strategy_status not in VALID_STATUSES:
        raise ValueError(f"strategy_status must be one of {VALID_STATUSES}, got {strategy_status!r}")
    if data_slice_used not in VALID_DATA_SLICES:
        raise ValueError(f"data_slice_used must be one of {VALID_DATA_SLICES}, got {data_slice_used!r}")
    if data_slice_used in ("holdout_gen1", "holdout_gen2"):
        print(f"*** LEDGER: logging a HOLDOUT test ({data_slice_used}) for {strategy_name!r} *** "
              f"confirm this was a deliberate, budgeted, sign-off'd holdout evaluation, "
              f"not routine testing.")

    record = HypothesisRecord(
        hypothesis_id=_next_hypothesis_id(ledger_path),
        logged_at=datetime.now().isoformat(),
        strategy_name=strategy_name,
        strategy_origin=strategy_origin,
        parameters=parameters,
        data_slice_used=data_slice_used,
        trade_count=trade_count,
        expectancy_r=expectancy_r,
        profit_factor=profit_factor,
        max_drawdown_r=max_drawdown_r,
        strategy_status=strategy_status,
        parent_hypothesis_id=parent_hypothesis_id,
        notes=notes,
    )
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger_path, "a") as f:
        f.write(json.dumps(record.as_dict()) + "\n")
    return record


def update_status(
    hypothesis_id: str,
    new_status: str,
    experiment_doc_id: Optional[str] = None,
    holdout_slot_id: Optional[str] = None,
    notes: str = "",
    ledger_path: Path = LEDGER_PATH,
) -> HypothesisRecord:
    """Records a status change for an EXISTING hypothesis by appending a
    new line that references the original, rather than rewriting the
    original line. Read all lines for a given hypothesis_id, in order,
    to see its full history -- the latest one is its current state."""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"new_status must be one of {VALID_STATUSES}, got {new_status!r}")

    original = get_latest(hypothesis_id, ledger_path)
    if original is None:
        raise ValueError(f"No existing hypothesis found with id {hypothesis_id!r}")

    updated = HypothesisRecord(
        hypothesis_id=hypothesis_id,          # SAME id -- this is an update, not a new hypothesis
        logged_at=datetime.now().isoformat(),
        strategy_name=original["strategy_name"],
        strategy_origin=original["strategy_origin"],
        parameters=original["parameters"],
        data_slice_used=original["data_slice_used"],
        trade_count=original.get("trade_count"),
        expectancy_r=original.get("expectancy_r"),
        profit_factor=original.get("profit_factor"),
        max_drawdown_r=original.get("max_drawdown_r"),
        strategy_status=new_status,
        live_authorization=original.get("live_authorization", "not_authorized"),
        parent_hypothesis_id=original.get("parent_hypothesis_id"),
        experiment_doc_id=experiment_doc_id or original.get("experiment_doc_id"),
        holdout_slot_id=holdout_slot_id or original.get("holdout_slot_id"),
        notes=notes,
    )
    with open(ledger_path, "a") as f:
        f.write(json.dumps(updated.as_dict()) + "\n")
    return updated


def _read_all(ledger_path: Path = LEDGER_PATH) -> list:
    if not ledger_path.exists():
        return []
    with open(ledger_path, "r") as f:
        return [json.loads(line) for line in f if line.strip()]


def get_latest(hypothesis_id: str, ledger_path: Path = LEDGER_PATH) -> Optional[dict]:
    """Returns the most recent record for a given hypothesis_id (i.e. its
    current state after any status updates), or None if not found."""
    matches = [r for r in _read_all(ledger_path) if r["hypothesis_id"] == hypothesis_id]
    return matches[-1] if matches else None


def get_current_state(ledger_path: Path = LEDGER_PATH) -> list:
    """Collapses the append-only log down to one row per hypothesis_id
    (its latest state) -- what most reporting/counting should use rather
    than the raw file, so a hypothesis with 3 status updates doesn't get
    triple-counted."""
    latest_by_id = {}
    for r in _read_all(ledger_path):
        latest_by_id[r["hypothesis_id"]] = r
    return list(latest_by_id.values())


def get_funnel_counts(ledger_path: Path = LEDGER_PATH) -> dict:
    """The four numbers docs/RESEARCH_INTEGRITY_PROTOCOL.md's 'Prominent
    counter' section asks for: total tested, reached validation, received
    holdout access, survived. Computed live from current state -- never
    a separately-maintained number that could drift from the actual log."""
    current = get_current_state(ledger_path)
    reached_validation_statuses = {
        "VALIDATION CANDIDATE", "HOLDOUT PASSED", "FORWARD VALIDATION", "PAPER VERIFIED",
    }
    survived_statuses = {"HOLDOUT PASSED", "FORWARD VALIDATION", "PAPER VERIFIED"}
    return {
        "hypotheses_tested": len(current),
        "reached_validation": sum(1 for r in current if r["strategy_status"] in reached_validation_statuses),
        "received_holdout_access": sum(1 for r in current if r.get("holdout_slot_id")),
        "survived": sum(1 for r in current if r["strategy_status"] in survived_statuses),
    }


def format_dashboard_counter(ledger_path: Path = LEDGER_PATH) -> str:
    """The exact style of counter the protocol doc's example shows:
    '1,847 hypotheses tested. 37 candidates reached validation.
    4 received holdout access. 1 survived.'"""
    c = get_funnel_counts(ledger_path)
    return (
        f"{c['hypotheses_tested']:,} hypotheses tested. "
        f"{c['reached_validation']:,} candidates reached validation. "
        f"{c['received_holdout_access']:,} received holdout access. "
        f"{c['survived']:,} survived."
    )
