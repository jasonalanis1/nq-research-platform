#!/usr/bin/env python3
"""Trials spent since the last survivor -- the project's progress measure.

Adopted 2026-09-10 by staff meeting, 4-2-1 (Statistical, Research
Director, LEARN, Discovery for it; Integrity Gate and Monetization for
the H118 countdown; Mechanism for pre-registered-mechanism count).

WHY THIS ONE. The obvious measure -- how many live candidates do we have
-- is actively harmful: it rises when you scan more, and scanning more
tightens the multiple-testing correction on everything still in flight.
Time-to-resolution was rejected because the Integrity Gate showed it is
confounded: the short-horizon retarget of 2026-09-10 will improve that
number over the coming months whether or not the research is going well.

This counter climbs with every trial spent and resets ONLY when a
candidate genuinely clears its pre-registered Validation-slice test and
stays alive. It can be gamed only by not scanning, which is a legitimate
choice anyway. It is meant to be uncomfortable.

    python3 src/progress_metric.py
    python3 src/progress_metric.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# Slices that mean a candidate got out of Discovery on a real test.
# "prospective" is deliberately EXCLUDED: per research_ledger, a
# prospective record never substitutes for a budgeted Validation or
# Holdout slot. EXP-047 is tracked prospectively and has never earned a
# Validation slot, so it must not reset this counter.
ABOVE_DISCOVERY = ("validation", "holdout_gen1", "holdout_gen2")

STAGE_SUFFIXES = (
    "_prospective_validation", "_prospective", "_validation",
    "_holdout", "_discovery", "_excursion",
)


def idea_key(name: str | None) -> str:
    """Collapse a candidate's stage-suffixed names to one idea, so H118 at
    Validation and H118 at Holdout are not two survivors."""
    name = name or ""
    changed = True
    while changed:
        changed = False
        for suffix in STAGE_SUFFIXES:
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                changed = True
    return name
BOOKKEEPING = (
    "_STATUS_CORRECTION", "_MULTIPLICITY_REEXPRESSION",
    "_PROGRESSION_POINTER", "_INTEGRITY_REVIEW_MULTIPLICITY",
)


def _hyp_number(hypothesis_id: str | None) -> int:
    try:
        return int(str(hypothesis_id).split("-")[-1])
    except (ValueError, AttributeError):
        return -1


def _scan_index(scan_key: str) -> int:
    """'scan_002_2026-09-09' -> 2. Scans are ordered by their number, not
    their date -- four scans share 2026-09-09, so dates cannot separate
    the scan that PRODUCED a survivor from the ones that came after it."""
    for part in scan_key.split("_"):
        if part.isdigit():
            return int(part)
    return 0


def compute() -> dict:
    from research_ledger import get_current_state
    from project_wide_multiplicity import SCAN_REGISTRY

    rows = [
        r for r in get_current_state()
        if not (r.get("strategy_name") or "").endswith(BOOKKEEPING)
    ]

    # A survivor is a candidate that cleared a pre-registered out-of-sample
    # test AND is still alive. A candidate later rejected never counts --
    # a reset it did not earn would flatter the number.
    survivor_rows = [
        r for r in rows
        if r.get("data_slice_used") in ABOVE_DISCOVERY
        and not (r.get("strategy_status") or "").startswith("REJECT")
    ]
    # One survivor per IDEA, not per row.
    by_idea = {}
    for r in survivor_rows:
        key = idea_key(r.get("strategy_name"))
        if key not in by_idea or _hyp_number(r.get("hypothesis_id")) > _hyp_number(
            by_idea[key].get("hypothesis_id")
        ):
            by_idea[key] = r
    survivors = sorted(by_idea.values(), key=lambda r: _hyp_number(r.get("hypothesis_id")))
    last = survivors[-1] if survivors else None
    last_id = _hyp_number(last.get("hypothesis_id")) if last else -1
    last_date = (last.get("logged_at") or "")[:10] if last else ""
    last_family = idea_key(last.get("strategy_name")) if last else ""

    # Trials come from two places: cells burned by Discovery Engine scans,
    # and standalone Discovery-stage hypotheses tested outside a scan.
    scan_cells_total = sum(s["cells_scanned"] for s in SCAN_REGISTRY.values())
    # Which scan produced the surviving idea? Everything scanned AFTER it
    # is trials spent without a survivor to show for them.
    producing_scan = 0
    for key, scan in SCAN_REGISTRY.items():
        for promoted in scan["promoted_hypothesis_ids"]:
            if _hyp_number(promoted) <= last_id:
                producing_scan = max(producing_scan, _scan_index(key))
    scan_cells_since = sum(
        s["cells_scanned"] for key, s in SCAN_REGISTRY.items()
        if _scan_index(key) > producing_scan
    )
    # A Discovery hypothesis promoted BY a scan was already counted as one
    # of that scan's cells. Counting it again would inflate the total and
    # make the project look like it had searched harder than it did.
    from_scans = {
        pid for scan in SCAN_REGISTRY.values() for pid in scan["promoted_hypothesis_ids"]
    }
    standalone = [
        r for r in rows
        if r.get("data_slice_used") == "discovery"
        and r.get("hypothesis_id") not in from_scans
    ]
    standalone_total = len(standalone)
    standalone_since = sum(
        1 for r in standalone if _hyp_number(r.get("hypothesis_id")) > last_id
    )

    trials_total = scan_cells_total + standalone_total
    trials_since = scan_cells_since + standalone_since
    survivors_ever = len(survivors)
    del last_family

    return {
        "trials_since_last_survivor": trials_since,
        "trials_total": trials_total,
        "survivors_alive": survivors_ever,
        "trials_per_survivor": round(trials_total / survivors_ever, 1) if survivors_ever else None,
        "last_survivor": {
            "hypothesis_id": last.get("hypothesis_id") if last else None,
            "name": last.get("strategy_name") if last else None,
            "date": last_date or None,
        },
        "scan_cells_total": scan_cells_total,
        "standalone_total": standalone_total,
        "scans_run": len(SCAN_REGISTRY),
        "scans_with_no_survivor": sum(
            1 for s in SCAN_REGISTRY.values() if not s["promoted_hypothesis_ids"]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = compute()
    if args.json:
        print(json.dumps(data, indent=1))
        return
    print("PROGRESS -- trials spent since the last survivor\n")
    print(f"  since last survivor : {data['trials_since_last_survivor']}")
    print(f"  last survivor       : {data['last_survivor']['name']} "
          f"({data['last_survivor']['hypothesis_id']}, {data['last_survivor']['date']})")
    print(f"  trials all time     : {data['trials_total']} "
          f"({data['scan_cells_total']} scan cells + {data['standalone_total']} standalone)")
    print(f"  survivors alive     : {data['survivors_alive']}")
    print(f"  trials per survivor : {data['trials_per_survivor']}")
    print(f"  scans run           : {data['scans_run']} "
          f"({data['scans_with_no_survivor']} produced nothing)")


if __name__ == "__main__":
    main()
