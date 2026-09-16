"""cost_model.py -- the corrected round-trip cost (Jason, September 16th 2026).
The old $6.00 micro round trip applied a FULL-SIZE NQ commission ($2.50/side) to
a MICRO contract. These tests pin the corrected components, the four
combinations, the optimistic labelling of every limit-entry figure, and Jason's
SPECIFY rule (reject only below cost itself -- no 3x multiple)."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import cost_model as cm  # noqa: E402


def test_contract_specs_match_the_exchange():
    assert cm.MNQ.usd_per_point == 2.0 and cm.MNQ.tick_size_points == 0.25
    assert cm.NQ.usd_per_point == 20.0 and cm.NQ.tick_size_points == 0.25
    assert cm.MNQ.usd_per_tick == 0.50 and cm.NQ.usd_per_tick == 5.00


def test_components_are_the_researched_figures():
    assert cm.MNQ.commission_per_side_usd == 0.25      # IBKR micro futures, fixed
    assert cm.MNQ.fees_per_side_usd == 0.55            # NFA + exchange + clearing, MNQ
    assert cm.NQ.commission_per_side_usd == 0.85
    assert cm.NQ.fees_per_side_usd == 1.60
    assert cm.SLIPPAGE_TICKS_PER_SIDE == 1.0 and cm.SLIPPAGE_BASIS == "ASSUMED"


def test_the_four_round_trips_in_dollars_and_points():
    exp = {("MNQ", "market"): (2.60, 1.30), ("MNQ", "limit"): (2.10, 1.05),
           ("NQ", "market"): (14.90, 0.745), ("NQ", "limit"): (9.90, 0.495)}
    for (sym, style), (usd, pts) in exp.items():
        rt = cm.round_trip(sym, style)
        assert abs(rt["usd"] - usd) < 1e-9, (sym, style, rt["usd"])
        assert abs(rt["points"] - pts) < 1e-9, (sym, style, rt["points"])
        # components named separately and adding up
        assert abs(rt["commission_usd"] + rt["fees_usd"] + rt["slippage_usd"] - rt["usd"]) < 1e-9


def test_limit_entry_pays_slippage_on_the_exit_only():
    m, l = cm.round_trip("MNQ", "market"), cm.round_trip("MNQ", "limit")
    assert m["slippage_sides"] == 2 and l["slippage_sides"] == 1
    assert abs((m["usd"] - l["usd"]) - cm.MNQ.usd_per_tick) < 1e-9
    assert m["commission_usd"] == l["commission_usd"] and m["fees_usd"] == l["fees_usd"]


def test_every_limit_figure_is_labelled_optimistic():
    for sym in ("MNQ", "NQ"):
        rt = cm.round_trip(sym, "limit")
        assert rt["optimistic"] is True
        assert "OPTIMISTIC" in rt["label"] and rt["optimistic_note"]
        assert "adversely selected" in rt["optimistic_note"]
        assert cm.round_trip(sym, "market")["optimistic"] is False
        assert "OPTIMISTIC" not in cm.round_trip(sym, "market")["label"]
    assert all(("OPTIMISTIC" in ln) for ln in cm.table_lines() if "limit entry |" in ln)


def test_full_size_nq_is_cheaper_in_points_and_dearer_in_dollars():
    """The structural point: fixed costs spread over 10x notional."""
    assert cm.cost_points("NQ", "market") < cm.cost_points("MNQ", "market") / 1.5
    assert cm.cost_usd("NQ", "market") > cm.cost_usd("MNQ", "market") * 5


def test_default_is_mnq_market_the_honest_basis():
    assert cm.DEFAULT_CONTRACT is cm.MNQ and cm.DEFAULT_ENTRY_STYLE == "market"
    assert cm.DEFAULT_USD_PER_ROUND_TRIP == 2.60 and cm.DEFAULT_POINTS_PER_ROUND_TRIP == 1.30
    assert cm.DEFAULT["optimistic"] is False
    # and it is the most expensive in points, so clearing it clears all four
    assert cm.DEFAULT_POINTS_PER_ROUND_TRIP == max(r["points"] for r in cm.combinations())


def test_the_old_six_dollar_constant_is_gone():
    assert cm.DEFAULT_USD_PER_ROUND_TRIP != 6.0 and cm.DEFAULT_POINTS_PER_ROUND_TRIP != 3.0


def test_combinations_are_the_four_in_report_order():
    assert [(r["contract"], r["entry_style"]) for r in cm.combinations()] == list(cm.COMBINATION_KEYS)
    assert len(cm.COMBINATIONS) == 4


def test_specify_gate_is_below_cost_only_no_multiple():
    # edge just above the MNQ market cost -> SCREEN, not rejected
    g = cm.specify_gate(1.31, "MNQ", "market")
    assert g["passes"] and g["verdict"] == "SCREEN" and g["cost_points"] == 1.30
    # the old 3x rule would have demanded 3.9 pts; it does not exist any more
    assert cm.specify_gate(2.55, "MNQ", "market")["passes"]
    assert not cm.specify_gate(1.29, "MNQ", "market")["passes"]
    assert not cm.specify_gate(1.30, "MNQ", "market")["passes"]     # below OR AT cost is not an edge
    assert "No multiple of cost" in g["rule"]


def test_net_helpers():
    assert abs(cm.net_points(2.55, "MNQ", "market") - 1.25) < 1e-9
    assert abs(cm.net_points(2.55, "NQ", "market") - 1.805) < 1e-9
    assert abs(cm.net_usd(2.55, "MNQ", "market") - 2.50) < 1e-9


def test_overlay_does_not_rescore_only_recosts():
    ov = cm.overlay(gross_points_total=100.0, trades=50)      # +2.0 gross pts/trade
    assert ov["trades"] == 50
    by = {r["key"]: r for r in ov["combinations"]}
    assert abs(by["MNQ_market"]["net_points_per_trade"] - 0.70) < 1e-9
    assert abs(by["NQ_market"]["net_points_per_trade"] - 1.255) < 1e-9
    # gross is an untouched input in every row
    assert {r["gross_points_total"] for r in ov["combinations"]} == {100.0}
    assert "NOT re-scored" in ov["note"]
    assert by["MNQ_limit"]["optimistic"] and not by["NQ_market"]["optimistic"]


def test_sources_are_cited_in_the_module():
    txt = (Path(__file__).resolve().parent.parent / "src" / "cost_model.py").read_text()
    assert "interactivebrokers.com" in txt and "BrokerChooser" in txt
    assert all(cm.SOURCES.values())
