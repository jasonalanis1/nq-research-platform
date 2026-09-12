"""The pipeline sweep must be complete, non-duplicated, and must never put a
promoted candidate anywhere but FROZEN (PIPELINE SWEEP RULE, 2026-09-11)."""
import pipeline_sweep as ps


def test_every_live_ledger_idea_appears_exactly_once():
    sweep = ps.build()
    latest = ps.latest_rows()
    live = {h for h, r in latest.items() if r["strategy_status"] not in ps.CLOSED}
    covered = set()
    for row in sweep["rows"]:
        ids = set(row["ids"]) | set(row.get("reexpressions", []))
        assert not (ids & covered), f"{row['id']} overlaps an earlier row"
        covered |= ids
    missing = live - covered
    assert not missing, f"live ledger ids missing from the sweep: {sorted(missing)}"


def test_promoted_candidates_are_frozen_and_owed_nothing():
    for row in ps.build()["rows"]:
        if row["status"] in ps.FROZEN_STATUSES:
            assert row["tier"] == "FROZEN"
            # A fresh HOLDOUT PASSED owes exactly one thing -- the Portfolio
            # incremental-information question (2026-09-12) -- until a
            # portfolio review doc exists on disk for it, after which it
            # owes nothing until its evidence window closes (hyp-000105's
            # own review completed 2026-09-12, see next_owed()'s hits check).
            assert row["next_owed"].startswith("Portfolio") or row["next_owed"].startswith("nothing")


def test_only_frozen_or_gated_can_touch_holdout():
    for row in ps.build()["rows"]:
        if row["tier"] == "OPEN":
            assert "Holdout" not in row["next_owed"].split("->")[0]


def test_shelf_line_reports_floor_state():
    line = ps.shelf_line()
    assert line.startswith("Shelf ") and ("TOP-UP OWED" in line or "next DRAW" in line)


def test_closed_parent_bookkeeping_row_is_hidden_not_phantom_owed_work():
    """Bug found 2026-09-11 22:00 UTC cycle: hyp-000048 and hyp-000056 were
    both closed (REJECTED) via a proper update_status() call on their OWN
    hypothesis_id, but their MULTIPLICITY_REEXPRESSION/PROGRESSION_POINTER
    bookkeeping children (separate hypothesis_ids, e.g. hyp-000131/132) kept
    their own logged-at-the-time PROMISING/VALIDATION CANDIDATE status
    forever, so every cycle's sweep fabricated a phantom OPEN/GATED row for
    an idea that was already done -- manufacturing fake owed work. A
    bookkeeping row whose parent's real current ledger status is closed must
    be marked hidden (not printed, no fabricated tier/owed text) while still
    counting as covered for completeness."""
    latest = ps.latest_rows()
    closed_parents_with_live_bookkeeping = [
        (hid, r) for hid, r in latest.items()
        if ps.BOOKKEEPING.search(r["strategy_name"])
        and r["strategy_status"] not in ps.CLOSED
        and latest.get(r.get("parent_hypothesis_id"), {}).get("strategy_status") in ps.CLOSED
    ]
    if not closed_parents_with_live_bookkeeping:
        return  # nothing in the current ledger exercises this path right now
    sweep = ps.build()
    rendered_ids = set()
    for row in sweep["rows"]:
        if row.get("hidden"):
            continue
        rendered_ids |= set(row["ids"]) | set(row.get("reexpressions", []))
    for hid, r in closed_parents_with_live_bookkeeping:
        assert hid not in rendered_ids, (
            f"{hid} (bookkeeping row for already-closed parent "
            f"{r.get('parent_hypothesis_id')}) was rendered as live/owed work"
        )


def test_validation_candidate_owed_stage_reflects_docs_not_hardcoded():
    """Bug found 2026-09-11 22:00 UTC cycle: every VALIDATION CANDIDATE row
    used to be hardcoded as owing "Director Re-Evaluation" regardless of
    whether that stage (and Monetization) had already run and been
    documented -- so a candidate that had genuinely cleared both stages
    (hyp-000105/106, see research/studies/midday-lull-director-reevaluation-
    and-monetization-2026-09-10.md) kept getting flagged as owing a stage it
    had already run, every single cycle. next_owed() for a VALIDATION
    CANDIDATE row must walk hits[...] the same way the PROMISING branch
    does, never assume "Director Re-Evaluation" unconditionally."""
    row = {"strategy_status": "VALIDATION CANDIDATE"}
    tier, reached, owed = ps.next_owed(row, {"mechanism": True, "statistical": True,
                                              "director": True, "monetization": True,
                                              "integrity_gate": False, "validation_spec": False})
    assert tier == "GATED"
    assert "Director Re-Evaluation" not in owed, "already-cleared stage re-flagged as owed"
    assert "Integrity Gate" in owed

    row2 = {"strategy_status": "VALIDATION CANDIDATE"}
    tier2, reached2, owed2 = ps.next_owed(row2, {"mechanism": True, "statistical": True,
                                                  "director": False, "monetization": False,
                                                  "integrity_gate": False, "validation_spec": False})
    assert tier2 == "GATED"
    # AMENDMENT v2.5 (2026-09-11): Director Re-Evaluation no longer exists as
    # a post-Validation stage (the Director's one capital call is made at the
    # Validation gate). A VALIDATION CANDIDATE with no Monetization doc owes
    # Monetization, then the blind Integrity Gate.
    assert owed2.startswith("Monetization")
    assert "Director Re-Evaluation" not in owed2

    for hid, r in ps.latest_rows().items():
        if r["strategy_status"] != "VALIDATION CANDIDATE":
            continue
        hits = ps._docs_mentioning(hid, r["strategy_name"])
        if hits["director"] and hits["monetization"]:
            _, _, owed_live = ps.next_owed(r, hits)
            assert "Director Re-Evaluation under" not in owed_live, (
                f"{hid} already has Director Re-Eval + Monetization docs on disk "
                f"but the sweep still says it owes Director Re-Evaluation"
            )


def test_blind_gate_ruling_inside_a_spec_counts_as_integrity_gate():
    """AMENDMENT v2.5: the blind Gate's ruling is appended to the frozen spec
    (first real run: midday-lull-holdout-spec-frozen-2026-09-12.md). The sweep
    must see it, or it keeps owing a checkpoint that already ran."""
    hits = ps._docs_mentioning("hyp-000105", "midday_lull_afternoon_expansion")
    assert hits["integrity_gate"]


def test_holdout_row_collapses_into_its_family_and_owes_portfolio():
    """2026-09-12: hyp-000141 (midday_lull_afternoon_expansion_holdout) must
    merge into the hyp-000105 family (not sit beside a stale GATED row), and
    never sit under "waiting on Jason to spend a slot". Its Portfolio review
    completed the same day (research/studies/portfolio-hyp105-separability-
    2026-09-12.md), so the live sweep now reports nothing further owed --
    see test_next_owed_holdout_portfolio_branch_both_states below for the
    branch logic itself, independent of today's completed-review state."""
    sweep = ps.build()
    rows = [r for r in sweep["rows"] if "midday_lull" in r["name"] and not r.get("hidden")]
    assert len(rows) == 1, [r["id"] for r in rows]
    assert rows[0]["tier"] == "FROZEN"
    assert "Portfolio" in rows[0]["next_owed"] or "Portfolio review complete" in rows[0]["next_owed"]


def test_next_owed_holdout_portfolio_branch_both_states():
    """Direct unit test of the branch fixed 2026-09-12: a fresh Holdout pass
    with no portfolio review doc owes the Portfolio question; once a
    portfolio review doc exists (hits["portfolio"]), it owes nothing. Before
    the fix this branch hardcoded "owed" forever and never checked hits at
    all, the same bug class as hyp-000048/hyp-000056 (2026-09-11 22:00 UTC)."""
    row = {"strategy_status": "HOLDOUT PASSED", "data_slice_used": "holdout_gen2"}
    hits_incomplete = {"portfolio": False}
    hits_complete = {"portfolio": True}
    tier1, reached1, owed1 = ps.next_owed(row, hits_incomplete)
    tier2, reached2, owed2 = ps.next_owed(row, hits_complete)
    assert tier1 == tier2 == "FROZEN" and reached1 == reached2 == "HOLDOUT PASSED"
    assert owed1.startswith("Portfolio")
    assert owed2.startswith("nothing")


def test_shelf_line_excludes_entries_in_triage(tmp_path, monkeypatch):
    """2026-09-12: an inventory entry marked IN TRIAGE has been drawn and is a
    ledger candidate; it must not count toward the floor or be named as the
    next draw (Entry 8 / hyp-000142 kept showing as 'next DRAW' after it was
    already in the sweep table as an OPEN candidate)."""
    inv = tmp_path / "idea_inventory.md"
    inv.write_text("## ENTRY 1 — live thing (map-ranked #2)\n\n## ENTRY 2 — drawn thing — IN TRIAGE\n\n## ENTRY 5 — validated thing — VALIDATION CANDIDATE, GATED (hyp-000999)\n\n## ENTRY 3 — old thing — CLOSED 2026-09-01\n\n## ENTRY 4 — SHELVED thing\n")
    monkeypatch.setattr(ps, "INVENTORY", inv)
    line = ps.shelf_line()
    assert line.startswith("Shelf 1/3 live (Entry 1)") and "TOP-UP OWED" in line
