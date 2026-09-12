"""Pipeline sweep table -- what every live candidate is OWED next.

Built from the ledger (latest row per hypothesis_id wins), the mechanism
docs on disk, and the Idea Inventory. This is the systemic part of the
PIPELINE SWEEP RULE (Jason, 2026-09-11): a cycle does not pick "queue item
0", it runs this, then works the table front to back, cheapest first.

Tiers:
  FROZEN  -- HOLDOUT PASSED / FORWARD VALIDATION: untouched until the
             candidate's own pre-registered evidence window closes.
  GATED   -- ready for a Holdout slot: cycle prepares, Jason spends.
  OPEN    -- everything else: fully automated, including a one-shot
             Validation attempt once the review chain is cleared.

Bookkeeping rows (PROGRESSION_POINTER / MULTIPLICITY_REEXPRESSION) and
child rows of a family are collapsed into the family's head so one idea
appears once. Legacy PROMISING rows from before the Idea Inventory (no
scan/shelf lineage) are flagged LEGACY: they are owed an explicit
disposition, advance or close to LEARN.

Usage: python3 src/pipeline_sweep.py            (print table)
       python3 src/pipeline_sweep.py --write    (also rewrite the
              "## Pipeline sweep" section of research/NEXT_UP.md and
              data/pipeline_sweep.json)
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "research" / "ledger" / "hypotheses.jsonl"
MECH = ROOT / "research" / "mechanisms"
STUDIES = ROOT / "research" / "studies"
INVENTORY = ROOT / "research" / "idea_inventory.md"
NEXT_UP = ROOT / "research" / "NEXT_UP.md"
OUT_JSON = ROOT / "data" / "pipeline_sweep.json"

CLOSED = {"REJECTED", "CLOSED", "ABANDONED"}
FROZEN_STATUSES = {"HOLDOUT PASSED", "FORWARD VALIDATION", "PAPER VERIFIED", "LIVE"}
BOOKKEEPING = re.compile(r"PROGRESSION_POINTER|MULTIPLICITY_REEXPRESSION", re.I)
# Named families whose head is a promoted/frozen candidate -- children collapse into it.
FAMILY_HEADS = {"H118": {"hyp-000121", "hyp-000122", "hyp-000123", "hyp-000126", "hyp-000130", "hyp-000134"},
                "EXP047": {"hyp-000020"}}


def latest_rows() -> dict:
    latest = {}
    for line in LEDGER.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            latest[r["hypothesis_id"]] = r
    return latest


def _docs_mentioning(hid: str, name: str) -> dict:
    hits = {"mechanism": False, "statistical": False, "director": False, "monetization": False, "integrity_gate": False, "validation_spec": False, "portfolio": False}
    for p in list(MECH.glob("*.md")):
        t = p.read_text(errors="ignore")
        if hid in t or (name and name in t):
            hits["mechanism"] = True
    for p in STUDIES.glob("*.md"):
        t = p.read_text(errors="ignore")
        if hid not in t and not (name and name in t):
            continue
        n = p.name.lower()
        if "statistical" in n: hits["statistical"] = True
        if "director" in n or "reeval" in n: hits["director"] = True
        if "monetiz" in n: hits["monetization"] = True
        if "integrity" in n: hits["integrity_gate"] = True
        # AMENDMENT v2.5: a blind Gate ruling is appended to the frozen spec
        # it ruled on (so ruling and resolution sit together), not to a
        # separately named file. Detect it by its heading.
        if "BLIND INTEGRITY GATE CHECKPOINT" in t and "Ruling" in t: hits["integrity_gate"] = True
        if "validation" in n and "spec" in n: hits["validation_spec"] = True
        if "portfolio" in n: hits["portfolio"] = True
    return hits


def next_owed(row: dict, hits: dict) -> tuple[str, str, str]:
    """-> (tier, stage_reached, next_owed)."""
    status = row["strategy_status"]
    if status == "HOLDOUT PASSED" and row.get("data_slice_used") == "holdout_gen2":
        # A Holdout pass is the end of the front half. A directional edge
        # goes to a Prospective Statistical Forward Test (Jason's call, own
        # spec); a conditioning / range fact has no forward test as a
        # strategy -- Portfolio's incremental-information question is owed,
        # UNLESS a portfolio review doc already exists on disk for it (bug
        # fixed 2026-09-12: this branch used to hardcode "owed" forever,
        # never checking hits[...] the way other branches do, so a
        # completed Portfolio review kept resurfacing as owed every cycle).
        if hits.get("portfolio"):
            return "FROZEN", "HOLDOUT PASSED", "nothing -- Portfolio review complete (see research/studies/, KNOWN TRUE); daily checker only"
        return "FROZEN", "HOLDOUT PASSED", ("Portfolio: incremental information beyond the validated findings, or the same "
                                             "latent state restated? (conditioning fact -> KNOWN TRUE; directional edge -> "
                                             "forward-test spec, Jason's call)")
    if status in FROZEN_STATUSES:
        return "FROZEN", status, "nothing -- evidence window open; daily checker only"
    if status == "VALIDATION CANDIDATE":
        # Bug found 2026-09-11 22:00 UTC cycle: this branch used to hardcode
        # "Director Re-Evaluation" as owed for every VALIDATION CANDIDATE,
        # never checking hits[...] the way the PROMISING branch below does --
        # so a candidate that had already cleared Director Re-Eval and
        # Monetization (e.g. hyp-000105/106, see research/sessions/2026-09-10-0815.md
        # and research/studies/midday-lull-director-reevaluation-and-monetization-2026-09-10.md)
        # kept getting re-flagged as owing a stage it had already run, every
        # cycle. Mirror the PROMISING chain instead.
        # AMENDMENT v2.5 (2026-09-11): Monetization now sits AFTER Validation;
        # the Director's one "worth more capital?" call was made at the
        # Validation gate. GATED chain: Monetization -> blind Integrity Gate
        # -> Waiting on Jason. Work already done under the old order is kept.
        reached = "Validation passed (uncorrected; see multiplicity study)"
        if not hits["monetization"]:
            return "GATED", reached, "Monetization (realization path, execution spec, measured costs) -> frozen Holdout spec + BLIND Integrity Gate checkpoint -> Waiting on Jason"
        reached = "Monetization"
        if not hits["integrity_gate"]:
            return "GATED", reached, "Prepare frozen Holdout spec + BLIND Integrity Gate checkpoint (src/integrity_blind_packet.py, fresh context) -> Waiting on Jason"
        return "GATED", "Integrity Gate checkpoint cleared", "nothing further automated -- frozen Holdout spec ready; Waiting on Jason to spend a Holdout slot"
    # PROMISING (Discovery-stage). AMENDMENT v2.5 order: Mechanism (before the
    # scan) -> Statistical (with power at the review point) -> Director's one
    # capital call -> BLIND Integrity Gate -> frozen Validation spec -> one shot.
    if not hits["mechanism"]:
        return "OPEN", "Discovery credible", "Mechanism doc (claim + 2 predictions + falsifier; Director grade A-F at scan close)"
    if not hits["statistical"]:
        return "OPEN", "Mechanism doc", "Statistical stage (4 questions + multiplicity + POWER at the proposed review point)"
    if not hits["director"]:
        return "OPEN", "Statistical", "Director capital call at the Validation gate (separability first): worth a one-shot Validation attempt?"
    if not hits["integrity_gate"]:
        return "OPEN", "Director CONTINUE", "BLIND Integrity Gate checkpoint (src/integrity_blind_packet.py, fresh context, VETO)"
    if not hits["validation_spec"]:
        return "OPEN", "Integrity Gate cleared", "Freeze Validation spec, then ONE-SHOT Validation attempt (automated)"
    return "OPEN", "Validation spec frozen", "Run the one-shot Validation attempt"


def shelf_line() -> str:
    txt = INVENTORY.read_text(errors="ignore")
    # SHELVED entries are not live (UPGRADE 1); an entry IN TRIAGE has been
    # drawn and is now a ledger candidate (owed its next stage via the sweep
    # table), so it no longer counts toward the shelf floor either (Entry 5
    # precedent, 2026-09-11; made explicit 2026-09-12 when Entry 8 went to
    # Triage and the shelf line kept naming it as the next draw). Same for any
    # title carrying a ledger id (hyp-NNNNNN): once drawn it lives in the
    # sweep table, not on the shelf (Entry 8 again, after it became a
    # VALIDATION CANDIDATE the same night).
    live = re.findall(r"^## ENTRY (\d+) — (?!SHELVED)(?!.*CLOSED)(?!.*IN TRIAGE)(?!.*hyp-\d{6})", txt, flags=re.M)
    closed = re.findall(r"^## ENTRY (\d+) — .*CLOSED", txt, flags=re.M)
    live_ids = sorted(int(x) for x in live)
    floor = 3
    if len(live_ids) < floor:
        return f"Shelf {len(live_ids)}/{floor} live (Entry {', '.join(map(str, live_ids))}) -> TOP-UP OWED before any draw"
    # UPGRADE 1 (2026-09-11): the Director ranks map-anchored scopes; a
    # "map-ranked #N" tag in a live title sets draw order. Untagged -> oldest.
    ranked = sorted(
        (int(n), int(e)) for e, title in re.findall(r"^## ENTRY (\d+) — (?!SHELVED)(?!.*CLOSED)(?!.*IN TRIAGE)(?!.*hyp-\d{6})(.*)$", txt, flags=re.M)
        for n in re.findall(r"map-ranked #(\d+)", title)
    )
    if ranked:
        return f"Shelf {len(live_ids)}/{floor} live (Entry {', '.join(map(str, live_ids))}) -> next DRAW: Entry {ranked[0][1]} (map-ranked #{ranked[0][0]})"
    return f"Shelf {len(live_ids)}/{floor} live (Entry {', '.join(map(str, live_ids))}) -> next DRAW: Entry {live_ids[0]} (oldest live)"


def build() -> dict:
    latest = latest_rows()
    live = {h: r for h, r in latest.items() if r["strategy_status"] not in CLOSED}
    rows = []
    seen_heads = set()
    for hid, r in sorted(live.items()):
        fam = next((k for k, ids in FAMILY_HEADS.items() if hid in ids), None)
        if fam:
            if fam in seen_heads:
                continue
            seen_heads.add(fam)
            head = max((latest[i] for i in FAMILY_HEADS[fam] if i in latest), key=lambda x: x["logged_at"])
            rows.append({"id": fam, "ids": sorted(FAMILY_HEADS[fam] & set(live)), "name": head["strategy_name"],
                         "status": head["strategy_status"], "tier": "FROZEN",
                         "stage_reached": head["strategy_status"], "next_owed": "nothing -- evidence window open (H118: 40 trades AND 12 months); daily checker only",
                         "legacy": False})
            continue
        if BOOKKEEPING.search(r["strategy_name"]):
            continue  # collapsed into its parent idea below via the parent's own row
        hits = _docs_mentioning(hid, r["strategy_name"])
        tier, reached, owed = next_owed(r, hits)
        legacy = r["strategy_status"] == "PROMISING" and r.get("strategy_origin") != "rd_generated" and not hits["mechanism"]
        rows.append({"id": hid, "ids": [hid], "name": r["strategy_name"], "status": r["strategy_status"], "tier": tier,
                     "stage_reached": reached, "next_owed": owed, "legacy": legacy,
                     "parent": r.get("parent_hypothesis_id")})
    # re-expression rows point at a parent idea; note them on the parent if present, else list under the parent id
    for hid, r in sorted(live.items()):
        if BOOKKEEPING.search(r["strategy_name"]):
            parent = r.get("parent_hypothesis_id")
            target = next((x for x in rows if parent in x["ids"]), None)
            if target:
                target.setdefault("reexpressions", []).append(hid)
            else:
                # No live row for the parent idea. Before assuming it is a
                # genuinely orphaned re-expression, check whether the parent's
                # OWN real ledger status (via update_status on its own
                # hypothesis_id, not this bookkeeping row's copy of the status
                # at logging time) is already closed -- a diagnostic overlay
                # row (MULTIPLICITY_REEXPRESSION/PROGRESSION_POINTER) commonly
                # outlives the parent's later closure and must not fabricate a
                # phantom OPEN/GATED candidate for an idea that is done (bug
                # found 2026-09-11 22:00 UTC cycle: hyp-000048/hyp-000056 both
                # already REJECTED via update_status, but their bookkeeping
                # children re-appeared as fake owed work every cycle since).
                parent_status = latest.get(parent, {}).get("strategy_status") if parent else None
                if parent_status in CLOSED:
                    rows.append({"id": parent or hid, "ids": [hid], "name": r["strategy_name"], "status": r["strategy_status"],
                                 "tier": "FROZEN", "stage_reached": f"{parent} already closed ({parent_status})",
                                 "next_owed": "nothing -- underlying candidate already closed; stale bookkeeping row",
                                 "legacy": False, "parent": parent, "hidden": True})
                else:
                    rows.append({"id": parent or hid, "ids": [hid], "name": r["strategy_name"], "status": r["strategy_status"],
                                 "tier": "GATED" if r["strategy_status"] == "VALIDATION CANDIDATE" else "OPEN",
                                 "stage_reached": "Validation (re-expressed under correction)",
                                 "next_owed": "Director Re-Evaluation: advance to a proper one-shot Validation spec, or close to LEARN",
                                 "legacy": True, "parent": parent})
    # Collapse rows that are the same idea under different bookkeeping names
    # (e.g. *_discovery / *_prospective / *_PROGRESSION_POINTER / *_MULTIPLICITY_REEXPRESSION).
    order = {"OPEN": 0, "GATED": 1, "FROZEN": 2}
    def base(name: str) -> str:
        return re.sub(r"_(discovery|prospective|exploratory|holdout|PROGRESSION_POINTER|MULTIPLICITY_REEXPRESSION|INTEGRITY_REVIEW_MULTIPLICITY)$", "", name, flags=re.I)
    merged: dict[str, dict] = {}
    for x in rows:
        k = x["id"] if x["id"] in FAMILY_HEADS else base(x["name"])
        if k in merged:
            m = merged[k]
            m["ids"] = sorted(set(m["ids"]) | set(x["ids"]))
            m["reexpressions"] = sorted(set(m.get("reexpressions", [])) | set(x.get("reexpressions", [])) | (set(x["ids"]) - {m["id"]}))
            if order[x["tier"]] > order[m["tier"]]:  # keep the most advanced stage's owed step
                m.update({"tier": x["tier"], "status": x["status"], "stage_reached": x["stage_reached"], "next_owed": x["next_owed"]})
            m["legacy"] = m["legacy"] or x["legacy"]
        else:
            x = dict(x); x["name"] = base(x["name"]) if k not in FAMILY_HEADS else x["name"]
            merged[k] = x
    rows = sorted(merged.values(), key=lambda x: (order[x["tier"]], x["id"]))
    return {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:00Z"), "shelf": shelf_line(),
            "rows": rows, "counts": {t: sum(1 for x in rows if x["tier"] == t and not x.get("hidden")) for t in order}}


def render(sweep: dict) -> str:
    lines = ["## Pipeline sweep", "",
             f"(auto-built by src/pipeline_sweep.py -- do not hand-edit; rebuilt every cycle. "
             f"Counts: OPEN {sweep['counts']['OPEN']}, GATED {sweep['counts']['GATED']}, FROZEN {sweep['counts']['FROZEN']}.)", "",
             f"- SHELF: {sweep['shelf']}"]
    for x in sweep["rows"]:
        if x.get("hidden"):
            continue
        flag = " [LEGACY -- owed an explicit disposition: advance or close to LEARN]" if x.get("legacy") else ""
        re_ = f" (re-expressions: {', '.join(x['reexpressions'])})" if x.get("reexpressions") else ""
        lines.append(f"- {x['tier']} {x['id']} {x['name']}{re_}: reached {x['stage_reached']} -> OWED: {x['next_owed']}{flag}")
    lines.append("")
    return "\n".join(lines)


def write_next_up(md: str) -> None:
    s = NEXT_UP.read_text()
    m = re.search(r"## Pipeline sweep\n.*?(?=\n## )", s, flags=re.S)
    if m:
        s = s[:m.start()] + md.rstrip("\n") + "\n" + s[m.end():]
    else:
        s = s.replace("## SESSION HANDOFF RULES", md + "\n## SESSION HANDOFF RULES", 1)
    NEXT_UP.write_text(s)


def main(argv: list[str]) -> int:
    sweep = build()
    md = render(sweep)
    print(md)
    if "--write" in argv:
        OUT_JSON.write_text(json.dumps(sweep, indent=1))
        write_next_up(md)
        print(f"[written: {OUT_JSON.relative_to(ROOT)}, NEXT_UP.md section]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
