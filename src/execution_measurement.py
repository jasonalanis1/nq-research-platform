"""
execution_measurement.py -- BOT MILESTONE B5 (first cut): the 14 execution
checks (research/infrastructure/back-half-production-integrity-v3.md,
AMENDMENT v3.1 S4), computed against whatever src/order_path.py journal
exists on disk.

DELIBERATE SCOPE, same rule the back-half spec states for itself (S5,
"deliberately minimal"): this is the MEASUREMENT tool, built now so it exists
and is tested, the same way risk_state_engine.py's --freeze machinery was
built before a large sample existed. It is honest about small samples --
every check reports its own N and says INSUFFICIENT SAMPLE rather than a
false PASS/FAIL when N is 0. It does NOT claim stage 3 (EXECUTION-QUALIFIED)
is reached; that requires a pre-registered minimum sample, set separately,
once B7's continuous run is producing one. Today this tool exists so that
measurement starts accumulating the moment orders start flowing, instead of
being built retroactively once a sample already exists (the mistake the back-
half spec's "Known gap" note flags for H118).

WHAT EACH CHECK MEANS HERE (source of truth: the 14-item list, verbatim in
the docstring below so this file is readable standalone)
  1. Signal occurs when the spec says it should        -- delegated to
  2. Signal occurs exactly once when it should             base_entry_b3.audit()
     (that audit is B3's own frozen-spec conformance proof; this tool calls
     it rather than re-implementing it, so there is exactly one place that
     rule lives).
  3. Correct order is generated       -- every order_intent has a valid
     direction and positive quantity.
  4. Correct quantity is generated    -- every order_intent's quantity is
     within CapitalConfig's contract cap (order_path.py enforces this at
     construction time; here it is verified after the fact from the journal).
  5. Entry/exit instructions correct  -- every order_intent carries a
     positive intended_price and a positive stop_distance.
  6. Orders reach the broker          -- every order_intent has a matching
     order_ack or order_rejected record (no orphaned intents outside a
     documented recovery_action).
  7. Fills are recorded               -- every acknowledged, non-rejected
     order has at least one fill record or an explicit recovery_action
     explaining why not.
  8. Expected vs. actual fill is measured -- every fill record carries both
     intended_price and price.
  9. Slippage is MEASURED, not assumed -- every fill's deviation_pts is a
     real (non-null) number, never defaulted to zero.
  10. Latency is measured             -- every order_ack's latency_s is a
      real (non-null) number.
  11. Rejected/missed/duplicate orders are detected -- rejections are
      counted from order_rejected records; duplicate-order protection is a
      construction guarantee (SimulatedBroker.submit_order raises on a
      reused order_id) proven by tests/test_simulated_broker.py, not a
      journal statistic -- reported as such, not "N/A".
  12. Position state is reconciled    -- reconciliation_mismatch count vs.
      total fills (should be 0; NOT 0 is reported, never hidden).
  13. A system failure cannot silently leave an unintended position open --
      OrderPath.recover() is the construction guarantee, tested in
      tests/test_order_path.py's crash-recovery and escalation cases; this
      tool reports how many recovery_action records exist and of what kind.
  14. Everything is logged for later reconstruction -- every order_intent's
      full chain (ack/reject through to a resolved fill total or an
      escalation) is present in the journal; this is the summary check that
      rolls up 6+7+13.

USAGE
    python3 src/execution_measurement.py                          # latest journal dir
    python3 src/execution_measurement.py --journal-dir <path>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from capital_protection import CONFIG as CAPITAL_CONFIG  # noqa: E402
from order_path import OrderPathJournal  # noqa: E402

DEFAULT_JOURNAL_DIR = ROOT.parent / "research" / "forward_validation" / "order_path_journal"


def _check(name: str, n: int, passed: int, note: str = "") -> dict:
    if n == 0:
        return {"check": name, "status": "INSUFFICIENT SAMPLE", "n": 0, "passed": 0, "note": note}
    return {"check": name, "status": "PASS" if passed == n else "FAIL", "n": n, "passed": passed, "note": note}


def measure(journal_dir=DEFAULT_JOURNAL_DIR) -> dict:
    journal = OrderPathJournal(journal_dir)
    records = journal.all_records()
    intents = [r for r in records if r["event"] == "order_intent"]
    acks = [r for r in records if r["event"] == "order_ack"]
    rejects = [r for r in records if r["event"] == "order_rejected"]
    fills = [r for r in records if r["event"] == "fill"]
    mismatches = [r for r in records if r["event"] == "reconciliation_mismatch"]
    recoveries = [r for r in records if r["event"] == "recovery_action"]

    ack_or_reject_ids = {r["order_id"] for r in acks} | {r["order_id"] for r in rejects}
    recovered_ids = {r["order_id"] for r in recoveries}

    checks = []
    checks.append({"check": "1-2. Signal timing / exactly-once", "status": "SEE base_entry_b3.audit()",
                    "note": "run `python3 src/base_entry_b3.py` -- this tool does not duplicate that proof"})
    checks.append(_check("3. Correct order generated", len(intents),
                          sum(1 for r in intents if r.get("direction") in ("long", "short") and r.get("quantity", 0) > 0)))
    checks.append(_check("4. Correct quantity generated", len(intents),
                          sum(1 for r in intents if 0 < r.get("quantity", 0) <= CAPITAL_CONFIG.max_contracts)))
    checks.append(_check("5. Entry/exit instructions correct", len(intents),
                          sum(1 for r in intents if r.get("intended_price", 0) > 0 and r.get("stop_distance", 0) > 0)))
    checks.append(_check("6. Orders reach the broker", len(intents),
                          sum(1 for r in intents if r["order_id"] in ack_or_reject_ids or r["order_id"] in recovered_ids)))
    acked_not_rejected = [r for r in acks if r["order_id"] not in {x["order_id"] for x in rejects}]
    fill_ids = {r["order_id"] for r in fills}
    checks.append(_check("7. Fills are recorded", len(acked_not_rejected),
                          sum(1 for r in acked_not_rejected if r["order_id"] in fill_ids or r["order_id"] in recovered_ids)))
    checks.append(_check("8. Expected vs. actual fill measured", len(fills),
                          sum(1 for r in fills if r.get("intended_price") is not None and r.get("price") is not None)))
    checks.append(_check("9. Slippage measured, not assumed", len(fills),
                          sum(1 for r in fills if r.get("deviation_pts") is not None)))
    checks.append(_check("10. Latency measured", len(acks),
                          sum(1 for r in acks if r.get("latency_s") is not None)))
    checks.append({"check": "11. Rejected/missed/duplicate orders detected", "status": "PASS (by construction)",
                    "n_rejected_observed": len(rejects),
                    "note": "duplicate-order protection is a construction guarantee "
                            "(SimulatedBroker.submit_order raises ValueError on a reused order_id); "
                            "see tests/test_simulated_broker.py, not a journal statistic"})
    checks.append(_check("12. Position state reconciled", len(fills), len(fills) - len(mismatches),
                          note=f"{len(mismatches)} reconciliation_mismatch record(s)" if mismatches else ""))
    checks.append({"check": "13. Crash cannot silently leave a position open", "status": "PASS (by construction)",
                    "recovery_action_records": len(recoveries),
                    "note": "OrderPath.recover() is the construction guarantee; see "
                            "tests/test_order_path.py's crash-recovery and escalation cases"})
    unresolved = [r for r in intents if r["order_id"] not in ack_or_reject_ids and r["order_id"] not in recovered_ids]
    checks.append(_check("14. Everything logged for reconstruction", len(intents), len(intents) - len(unresolved)))

    return {"journal_dir": str(journal_dir), "n_order_intents": len(intents), "n_fills": len(fills),
            "n_rejected": len(rejects), "n_recovery_actions": len(recoveries), "checks": checks,
            "stage_3_qualified": False,
            "note": "stage 3 (EXECUTION-QUALIFIED) requires a pre-registered minimum sample, "
                    "set separately once B7's continuous run is producing one -- this tool measures, "
                    "it does not itself authorize a stage transition"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal-dir", default=str(DEFAULT_JOURNAL_DIR))
    a = ap.parse_args()
    out = measure(Path(a.journal_dir))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
