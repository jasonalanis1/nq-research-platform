"""
cost_model.py -- THE one place that owns what a round trip costs.

WHY THIS FILE EXISTS (Jason's correction, September 16th 2026)
  Every cost figure in this repo was built on `src/integrity_checks.py`'s
  COMMISSION_PER_SIDE_USD = 2.50, applied to a MICRO (MNQ) contract. $2.50 a side
  is a FULL-SIZE E-mini (NQ) all-in figure; on a micro it is roughly 3-10x too
  high on the commission leg. The resulting "$6.00 per micro round trip = 3.00
  index points" was wrong by 2-3x, and a strategy (S008) was refused on it.
  Jason caught it. This module replaces that constant everywhere.

SOURCES (cited, not assumed)
  * Interactive Brokers, official micro futures page
    (interactivebrokers.com/en/trading/micro-futures-comparison.php):
    micro futures commission **$0.25 per contract** fixed ($0.10-0.25 tiered),
    "plus exchange and regulatory fees".
  * BrokerChooser, IBKR MNQ page: NFA + exchange + clearing fees come to
    **~$0.55 per contract** for MNQ.
  * BrokerChooser, IBKR NQ page: commission **$0.85 per contract**, NFA +
    exchange + clearing **~$1.60 per contract**.
  * Contract specs (CME): MNQ $2.00 per index point, NQ $20.00 per index point;
    both tick 0.25 points, so a tick is $0.50 on MNQ and $5.00 on NQ.

THE THREE COMPONENTS, NAMED SEPARATELY AND NEVER MERGED
  commission   the broker's own charge, per contract per side
  fees         exchange + regulatory (NFA) + clearing, per contract per side
  slippage     how much worse than the signal price a MARKET order fills, per
               side, ASSUMED at 1 tick until a real broker measures it (s.11).

ENTRY STYLE -- AND THE HONEST LABEL ON THE LIMIT NUMBERS
  market  a market order on entry AND on exit: slippage is paid on both sides.
  limit   a resting limit order on entry, market order on exit: the spread is
          not paid on entry, so slippage is charged on the exit only.

  **Every limit-entry figure this module produces is OPTIMISTIC -- an upper
  bound on what a limit entry can save.** A real resting limit order does not
  always fill, and it fills PREFERENTIALLY when the market is about to trade
  through it, i.e. when the trade is about to go against you (adverse
  selection). A historical screen cannot model a non-fill: it silently assumes
  every limit order filled at its price and that the fills it got are a fair
  sample of the fills it would have got. Both assumptions flatter the limit
  column. So the limit numbers are a CEILING on the limit-entry result, never an
  estimate of it, and every printer and writer of them must say so -- use
  OPTIMISTIC_NOTE / label(). The market column is the honest one; the decision
  basis for a 1-micro paper strategy is DEFAULT = MNQ market.

THE STRUCTURAL POINT WORTH SEEING
  In DOLLARS the full-size NQ round trip is ~5.7x the micro's. In POINTS -- the
  unit a strategy's edge is measured in -- the full-size NQ costs roughly HALF
  what the micro costs (0.745 pt vs 1.30 pt at market), because the fixed
  commission + fee component is spread over 10x the notional while the slippage
  component is the same 1 tick either way. A "the cost wall killed it" finding
  on MNQ is therefore not automatically a finding about the pattern: the same
  trade on NQ pays half the points. That is exactly why every screen from now on
  prints all four combinations side by side.

THE SPECIFY GATE (Jason, September 16th 2026)
  "At SPECIFY, reject only if the expected edge is below the corrected cost
  itself; otherwise screen it." -- `specify_gate()` below. There is no 3x
  multiple, no cost budget, no "well north of" rule. Those were Tony's
  invention; the directive never had them.

USAGE
    python3 src/cost_model.py              # print the table
    from cost_model import DEFAULT, round_trip, COMBINATIONS, specify_gate
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict

# --- sources, machine-readable so a report can cite them --------------------
SOURCES = {
    "ibkr_micro_commission": (
        "Interactive Brokers, micro futures comparison "
        "(interactivebrokers.com/en/trading/micro-futures-comparison.php): micro futures "
        "commission $0.25/contract fixed ($0.10-0.25 tiered), plus exchange and regulatory fees."),
    "mnq_fees": "BrokerChooser, IBKR MNQ page: NFA + exchange + clearing ~= $0.55/contract.",
    "nq_commission_and_fees": "BrokerChooser, IBKR NQ page: commission $0.85/contract; NFA + exchange + clearing ~= $1.60/contract.",
    "contract_specs": "CME: MNQ $2.00/index point, NQ $20.00/index point; tick 0.25 point (= $0.50 MNQ, $5.00 NQ).",
    "slippage": "ASSUMED 1 tick per side on a market order, standing directive s.11, until a real broker measures it (B4b).",
}

SLIPPAGE_TICKS_PER_SIDE = 1.0     # ASSUMED (s.11). Paid per side on a MARKET order only.
SLIPPAGE_BASIS = "ASSUMED"        # flips to MEASURED only when a real broker feed exists (B4b)

ENTRY_STYLES = ("market", "limit")
OPTIMISTIC_NOTE = ("OPTIMISTIC UPPER BOUND -- a limit entry is assumed to always fill at its price. "
                   "Real limit orders miss fills and are adversely selected (they fill when the market "
                   "is about to run the other way); the screen cannot model a non-fill.")


@dataclass(frozen=True)
class ContractSpec:
    """One tradeable contract and what a single side of a trade costs on it."""
    symbol: str
    name: str
    usd_per_point: float
    tick_size_points: float
    commission_per_side_usd: float
    fees_per_side_usd: float          # exchange + regulatory (NFA) + clearing
    commission_source: str
    fees_source: str

    @property
    def usd_per_tick(self) -> float:
        return self.tick_size_points * self.usd_per_point

    @property
    def fixed_per_side_usd(self) -> float:
        """Commission + fees: the part that does NOT scale with notional."""
        return self.commission_per_side_usd + self.fees_per_side_usd


MNQ = ContractSpec(
    symbol="MNQ", name="Micro E-mini Nasdaq-100",
    usd_per_point=2.0, tick_size_points=0.25,
    commission_per_side_usd=0.25, fees_per_side_usd=0.55,
    commission_source=SOURCES["ibkr_micro_commission"], fees_source=SOURCES["mnq_fees"])

NQ = ContractSpec(
    symbol="NQ", name="E-mini Nasdaq-100 (full size)",
    usd_per_point=20.0, tick_size_points=0.25,
    commission_per_side_usd=0.85, fees_per_side_usd=1.60,
    commission_source=SOURCES["nq_commission_and_fees"], fees_source=SOURCES["nq_commission_and_fees"])

CONTRACTS = {"MNQ": MNQ, "NQ": NQ}


def slippage_sides(entry_style: str) -> int:
    """How many sides of the trade pay slippage. market = 2 (entry and exit);
    limit = 1 (exit only -- the resting entry does not pay the spread)."""
    if entry_style not in ENTRY_STYLES:
        raise ValueError(f"entry_style must be one of {ENTRY_STYLES}, got {entry_style!r}")
    return 2 if entry_style == "market" else 1


def is_optimistic(entry_style: str) -> bool:
    """True for every limit-entry figure. See OPTIMISTIC_NOTE."""
    return entry_style == "limit"


def label(contract: ContractSpec | str, entry_style: str) -> str:
    """The short label every printer must use, carrying the optimistic flag."""
    c = contract if isinstance(contract, ContractSpec) else CONTRACTS[contract]
    return f"{c.symbol} {entry_style} entry" + (" (OPTIMISTIC)" if is_optimistic(entry_style) else "")


def round_trip(contract: ContractSpec | str = MNQ, entry_style: str = "market") -> dict:
    """The full per-round-trip cost breakdown for ONE contract of `contract`,
    every component named separately, in dollars AND in index points."""
    c = contract if isinstance(contract, ContractSpec) else CONTRACTS[contract]
    n_slip = slippage_sides(entry_style)
    commission = c.commission_per_side_usd * 2
    fees = c.fees_per_side_usd * 2
    slippage = SLIPPAGE_TICKS_PER_SIDE * c.usd_per_tick * n_slip
    total = commission + fees + slippage
    return {
        "contract": c.symbol, "entry_style": entry_style, "label": label(c, entry_style),
        "usd_per_point": c.usd_per_point, "tick_size_points": c.tick_size_points,
        "usd_per_tick": c.usd_per_tick,
        "commission_per_side_usd": c.commission_per_side_usd,
        "fees_per_side_usd": c.fees_per_side_usd,
        "slippage_per_side_usd": SLIPPAGE_TICKS_PER_SIDE * c.usd_per_tick,
        "slippage_sides": n_slip,
        "commission_usd": round(commission, 4),
        "fees_usd": round(fees, 4),
        "slippage_usd": round(slippage, 4),
        "usd": round(total, 4),
        "points": round(total / c.usd_per_point, 6),
        "slippage_basis": SLIPPAGE_BASIS,
        "optimistic": is_optimistic(entry_style),
        "optimistic_note": OPTIMISTIC_NOTE if is_optimistic(entry_style) else None,
    }


# The four combinations, in the fixed order every report prints them.
COMBINATION_KEYS = (("MNQ", "market"), ("MNQ", "limit"), ("NQ", "market"), ("NQ", "limit"))


def combinations() -> list:
    """All four MNQ/NQ x market/limit round trips, in the fixed report order."""
    return [round_trip(CONTRACTS[sym], style) for sym, style in COMBINATION_KEYS]


COMBINATIONS = combinations()

# The decision basis: what the paper book actually trades -- 1 micro, market
# orders, simulated fills. Honest (not optimistic), and the most expensive in
# points, so a strategy that clears it clears all four.
DEFAULT_CONTRACT = MNQ
DEFAULT_ENTRY_STYLE = "market"
DEFAULT = round_trip(MNQ, "market")
DEFAULT_USD_PER_ROUND_TRIP = DEFAULT["usd"]          # 2.60
DEFAULT_POINTS_PER_ROUND_TRIP = DEFAULT["points"]    # 1.30
DEFAULT_LABEL = DEFAULT["label"]
DEFAULT_NOTE = (f"ASSUMED: {MNQ.symbol} market entry+exit = "
                f"commission ${MNQ.commission_per_side_usd:.2f}/side + fees ${MNQ.fees_per_side_usd:.2f}/side + "
                f"{SLIPPAGE_TICKS_PER_SIDE:g} tick/side slippage "
                f"= ${DEFAULT_USD_PER_ROUND_TRIP:.2f} per round trip = {DEFAULT_POINTS_PER_ROUND_TRIP:.3f} index points "
                f"(src/cost_model.py; sources cited there). Labelled ASSUMED until B4b measures it.")


def cost_usd(contract="MNQ", entry_style="market") -> float:
    return round_trip(contract, entry_style)["usd"]


def cost_points(contract="MNQ", entry_style="market") -> float:
    return round_trip(contract, entry_style)["points"]


def net_points(gross_points: float, contract="MNQ", entry_style="market") -> float:
    """Gross per-trade edge in index points -> net, after this combination's cost."""
    return gross_points - cost_points(contract, entry_style)


def net_usd(gross_points: float, contract="MNQ", entry_style="market", contracts: int = 1) -> float:
    """Gross per-trade edge in index points -> net dollars for `contracts` contracts."""
    rt = round_trip(contract, entry_style)
    return (gross_points * rt["usd_per_point"] - rt["usd"]) * contracts


def specify_gate(expected_edge_points: float, contract="MNQ", entry_style="market") -> dict:
    """JASON'S SPECIFY RULE (September 16th 2026), replacing Tony's invented
    '3x cost' pre-screen, which the standing directive never contained:

        "At SPECIFY, reject only if the expected edge is below the corrected
         cost itself; otherwise screen it."

    So: reject iff expected_edge_points <= cost_points. No multiple, no budget,
    no 'well north of'. Everything else goes to SCREEN and is judged there on
    the one number the directive asks for."""
    cost = cost_points(contract, entry_style)
    edge = float(expected_edge_points)
    passes = edge > cost
    return {
        "expected_edge_points": edge, "cost_points": cost,
        "contract": contract if isinstance(contract, str) else contract.symbol,
        "entry_style": entry_style,
        "passes": passes, "verdict": "SCREEN" if passes else "REJECT",
        "rule": ("Jason, September 16th 2026: at SPECIFY reject ONLY if the expected per-trade edge is below "
                 "the corrected per-trade cost itself; otherwise it goes to SCREEN. No multiple of cost."),
    }


def overlay(gross_points_total: float, trades: int) -> dict:
    """Apply all four cost combinations to an ALREADY-RECORDED gross result.

    `gross_points_total` is the total gross P&L of the record expressed in INDEX
    POINTS (points, not dollars, so it is contract-independent) and `trades` is
    the number of round trips in it. NOTHING about the record is re-scored here:
    the fills, the entries, the exits and the gross points are untouched inputs.
    Only the cost overlay applied on top of them changes."""
    trades = int(trades)
    gp = float(gross_points_total)
    rows = []
    for rt in combinations():
        cost_pts = rt["points"] * trades
        net_pts = gp - cost_pts
        rows.append({
            "key": f"{rt['contract']}_{rt['entry_style']}", "label": rt["label"],
            "contract": rt["contract"], "entry_style": rt["entry_style"],
            "optimistic": rt["optimistic"],
            "cost_usd_per_trade": rt["usd"], "cost_points_per_trade": rt["points"],
            "gross_points_total": round(gp, 4),
            "gross_points_per_trade": round(gp / trades, 6) if trades else None,
            "cost_points_total": round(cost_pts, 4),
            "net_points_total": round(net_pts, 4),
            "net_points_per_trade": round(net_pts / trades, 6) if trades else None,
            "gross_usd_total": round(gp * rt["usd_per_point"], 2),
            "cost_usd_total": round(rt["usd"] * trades, 2),
            "net_usd_total": round(net_pts * rt["usd_per_point"], 2),
            "net_usd_per_trade": round(net_pts * rt["usd_per_point"] / trades, 4) if trades else None,
            "made_money": bool(trades and net_pts > 0),
        })
    return {"trades": trades, "combinations": rows,
            "optimistic_note": OPTIMISTIC_NOTE,
            "note": ("The record itself is NOT re-scored -- same fills, same entries, same exits, same gross "
                     "points. Only the cost overlay applied to them changes (standing directive s.13: the "
                     "paper record is never adjusted, deleted or re-scored)."),
            "decision_basis": DEFAULT_LABEL}


def table_lines() -> list:
    """The breakdown table, as plain lines, for a report or a doc."""
    out = ["| combination | commission/side | fees/side | slippage/side | round trip $ | round trip POINTS |",
           "|---|---|---|---|---|---|"]
    for rt in combinations():
        c = CONTRACTS[rt["contract"]]
        slip = f"${rt['slippage_per_side_usd']:.2f}" + ("" if rt["entry_style"] == "market" else " (exit only)")
        out.append(f"| {rt['label']} | ${c.commission_per_side_usd:.2f} | ${c.fees_per_side_usd:.2f} | "
                   f"{slip} | ${rt['usd']:.2f} | {rt['points']:.3f} pt |")
    out.append("")
    out.append(f"Decision basis: **{DEFAULT_LABEL}** (${DEFAULT_USD_PER_ROUND_TRIP:.2f} = "
               f"{DEFAULT_POINTS_PER_ROUND_TRIP:.3f} pt). Slippage is {SLIPPAGE_BASIS}.")
    out.append(f"Limit-entry rows are {OPTIMISTIC_NOTE}")
    out.append("In POINTS the full-size NQ round trip costs about HALF the micro's, because the fixed "
               "commission+fee component spreads over 10x the notional while the tick of slippage is the same.")
    return out


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.json:
        print(json.dumps({"contracts": {k: asdict(v) for k, v in CONTRACTS.items()},
                          "combinations": combinations(), "default": DEFAULT, "sources": SOURCES}, indent=1))
    else:
        print("ROUND-TRIP COST MODEL (src/cost_model.py)")
        for ln in table_lines():
            print(ln)
        print("\nSources:")
        for k, v in SOURCES.items():
            print(f"  - {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
