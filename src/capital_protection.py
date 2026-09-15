#!/usr/bin/env python3
"""UPGRADE 6 -- capital-protection rules, in code, frozen before any live
authorization (Jason's direction, September 11th 2026).

These are ACCOUNT controls, not strategy edits. Every trigger is logged as
an execution-spec divergence from the research spec; nothing here ever
feeds back into a frozen strategy's definition. A statistical kill stays
prohibited during any forward-validation window; the kills below are
execution / capital kills and are REQUIRED from the first live order.

Everything is a pure function of the numbers handed to it, so it can be
tested exhaustively and called before every order. Fail-closed: any
missing or malformed input BLOCKS the order.

    python3 src/capital_protection.py     # prints the frozen config
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Iterable, Optional


@dataclass(frozen=True)
class CapitalConfig:
    # 1. Starting risk budget. Reserved for a SHORT-HORIZON candidate whose
    #    per-trade swing is $50-150 per micro. Rises to 500 only after a
    #    positive, MEASURED paper record. H118 is excluded at this budget.
    starting_budget_usd: float = 300.0
    raised_budget_usd: float = 500.0
    paper_record_min_trades: int = 20
    excluded_strategies: tuple = ("H118",)
    per_trade_swing_min_usd: float = 50.0
    per_trade_swing_max_usd: float = 150.0
    # 2. Trailing kill: equity below max(-300, peak - max(300, peak/3)).
    #    Jason marked the one-third provisional.
    trailing_floor_usd: float = 300.0
    trailing_giveback_fraction: float = 1.0 / 3.0
    # 3. Slippage kill: mean fill deviation over the last 20 fills > 25% of
    #    the strategy's working edge (points) -> suspend, report.
    slippage_window_fills: int = 20
    slippage_kill_fraction_of_edge: float = 0.25
    # 4. Signal-divergence halt: zero tolerance.
    # 5. Per-trade catastrophe stop 2R (2 x entry-day ATR14) and a daily
    #    loss cap of half the remaining budget. More than 2 catastrophe
    #    triggers in 40 trades is a finding about the tail -- reported,
    #    never tuned.
    catastrophe_stop_r: float = 2.0
    daily_loss_cap_fraction_of_remaining: float = 0.5
    catastrophe_trigger_limit: int = 2
    catastrophe_trigger_window_trades: int = 40
    # 6. Position / order caps, fail-closed.
    max_contracts: int = 1
    max_open_positions: int = 1
    max_orders_per_day: int = 4
    # 7. PAPER MODE -- R-denominated (staff meeting, September 14th 2026,
    #    research/infrastructure/staff-meeting-swing-band-2026-09-14.md;
    #    Jason: "available to add more money if the ROI on the trade is there").
    #    The dollar figures above (1.) are Jason's LIVE appetite from the
    #    September 11th brief and they belong to B8. In paper, one R is whatever
    #    the strategy's own stop is worth in dollars, and every budget ratio he
    #    set is kept as a multiple of R: $300 at a $50-150 trade is 2-6R
    #    (midpoint 4R); $500 is 3-10R (6R). The dollar swing band is NOT
    #    applied in paper -- 1R only has to be positive and finite -- so the
    #    paper record can exist at the strategy's real stop size. Every
    #    Execution block that cites a paper drawdown states the current dollar
    #    value of 1R. paper -> live comparisons are comparisons of EXECUTION,
    #    never of kill-switch behaviour (Gate condition 3 of that meeting).
    paper_mode: bool = False
    paper_starting_budget_r: float = 4.0
    paper_raised_budget_r: float = 6.0
    paper_trailing_floor_r: float = 4.0


CONFIG = CapitalConfig()
PAPER_CONFIG = CapitalConfig(paper_mode=True)


def effective_config(cfg: CapitalConfig, per_trade_swing_usd: float) -> CapitalConfig:
    """In paper mode, express the dollar rules in R for THIS trade: 1R is the
    trade's own swing. Outside paper mode, returns cfg unchanged, so every live
    rule keeps Jason's dollars exactly as written."""
    if not cfg.paper_mode:
        return cfg
    r = float(per_trade_swing_usd)
    if not (r > 0 and r == r and r != float("inf")):
        return cfg      # a non-positive/non-finite R is blocked by swing_fits_budget below
    from dataclasses import replace
    return replace(cfg,
                   starting_budget_usd=cfg.paper_starting_budget_r * r,
                   raised_budget_usd=cfg.paper_raised_budget_r * r,
                   trailing_floor_usd=cfg.paper_trailing_floor_r * r,
                   per_trade_swing_min_usd=1e-9,
                   per_trade_swing_max_usd=float("inf"))


@dataclass
class Decision:
    allow: bool
    reasons: list = field(default_factory=list)
    divergences: list = field(default_factory=list)   # logged, never tuned

    def block(self, why: str) -> None:
        self.allow = False
        self.reasons.append(why)


# --------------------------------------------------------------------------
# rule 1 -- budget
# --------------------------------------------------------------------------

def budget_allowed(strategy: str, paper_trades: int, paper_slippage_measured: bool,
                   paper_net_usd: float, cfg: CapitalConfig = CONFIG) -> float:
    """Dollars of risk budget this strategy may be funded with. 0 = not fundable."""
    if strategy in cfg.excluded_strategies:
        return 0.0
    if (paper_trades >= cfg.paper_record_min_trades and paper_slippage_measured
            and paper_net_usd > 0):
        return cfg.raised_budget_usd
    return cfg.starting_budget_usd


def swing_fits_budget(per_trade_swing_usd: float, cfg: CapitalConfig = CONFIG) -> bool:
    """LIVE: the starting budget is reserved for candidates whose one-micro swing
    is $50-150. H118 (~$1,000-1,400 per trade) fails this by construction.
    PAPER (cfg.paper_mode): 1R only has to be positive and finite."""
    r = float(per_trade_swing_usd)
    if cfg.paper_mode:
        return r > 0 and r == r and r != float("inf")
    return cfg.per_trade_swing_min_usd <= r <= cfg.per_trade_swing_max_usd


# --------------------------------------------------------------------------
# rule 2 -- trailing kill
# --------------------------------------------------------------------------

def trailing_kill_level(peak_profit_usd: float, cfg: CapitalConfig = CONFIG) -> float:
    """Equity (cumulative P&L) level at or below which trading shuts off."""
    peak = max(0.0, peak_profit_usd)
    giveback = max(cfg.trailing_floor_usd, peak * cfg.trailing_giveback_fraction)
    return max(-cfg.trailing_floor_usd, peak - giveback)


def trailing_kill(equity_usd: float, peak_profit_usd: float, cfg: CapitalConfig = CONFIG) -> bool:
    return equity_usd <= trailing_kill_level(peak_profit_usd, cfg)


# --------------------------------------------------------------------------
# rule 3 -- slippage kill
# --------------------------------------------------------------------------

def slippage_kill(fill_deviations_pts: Iterable[float], working_edge_pts: float,
                  cfg: CapitalConfig = CONFIG) -> Optional[bool]:
    """None = not enough fills to judge yet (report, do not kill).
    True = suspend. Deviations are adverse-positive (points lost to the fill)."""
    devs = [float(d) for d in fill_deviations_pts]
    if len(devs) < cfg.slippage_window_fills:
        return None
    if working_edge_pts <= 0:
        return True   # an edge of zero or less cannot afford any slippage
    recent = devs[-cfg.slippage_window_fills:]
    return (sum(recent) / len(recent)) > cfg.slippage_kill_fraction_of_edge * working_edge_pts


# --------------------------------------------------------------------------
# rule 4 -- signal divergence
# --------------------------------------------------------------------------

def signal_divergence(live_signals: Iterable, reference_signals: Iterable) -> bool:
    """True when the live engine's signals for a day differ from the frozen
    reference implementation in any way. Zero tolerance -> halt all orders."""
    return list(live_signals) != list(reference_signals)


# --------------------------------------------------------------------------
# rule 5 -- catastrophe stop, daily cap, tail finding
# --------------------------------------------------------------------------

def catastrophe_stop_hit(direction: str, entry_price: float, current_price: float,
                         entry_day_atr14: float, cfg: CapitalConfig = CONFIG) -> bool:
    if entry_day_atr14 <= 0:
        return True   # cannot size the stop -> treat as hit (fail closed)
    adverse = (entry_price - current_price) if direction == "long" else (current_price - entry_price)
    return adverse >= cfg.catastrophe_stop_r * entry_day_atr14


def daily_loss_cap_hit(day_pnl_usd: float, remaining_budget_usd: float,
                       cfg: CapitalConfig = CONFIG) -> bool:
    if remaining_budget_usd <= 0:
        return True
    return day_pnl_usd <= -cfg.daily_loss_cap_fraction_of_remaining * remaining_budget_usd


def catastrophe_tail_finding(catastrophe_flags: Iterable[bool], cfg: CapitalConfig = CONFIG) -> bool:
    """More than `limit` catastrophe triggers in the last `window` trades is a
    finding about the strategy's tail. It is REPORTED. It is never tuned."""
    flags = [bool(f) for f in catastrophe_flags][-cfg.catastrophe_trigger_window_trades:]
    return sum(flags) > cfg.catastrophe_trigger_limit


# --------------------------------------------------------------------------
# the pre-order gate -- every rule, fail-closed
# --------------------------------------------------------------------------

def pre_order_check(state: dict, cfg: CapitalConfig = CONFIG) -> Decision:
    """`state` is what the execution engine knows right before sending an
    order. Missing keys block. Keys:
        strategy, paper_trades, paper_slippage_measured, paper_net_usd,
        per_trade_swing_usd, equity_usd, peak_profit_usd, remaining_budget_usd,
        day_pnl_usd, fill_deviations_pts (list), working_edge_pts,
        live_signals_today (list), reference_signals_today (list),
        open_positions (int), orders_today (int), contracts (int),
        catastrophe_flags (list of bool, per resolved trade)
    """
    d = Decision(allow=True)
    required = ("strategy", "paper_trades", "paper_slippage_measured", "paper_net_usd",
                "per_trade_swing_usd", "equity_usd", "peak_profit_usd", "remaining_budget_usd",
                "day_pnl_usd", "fill_deviations_pts", "working_edge_pts",
                "live_signals_today", "reference_signals_today",
                "open_positions", "orders_today", "contracts", "catastrophe_flags")
    missing = [k for k in required if k not in state]
    if missing:
        d.block("fail-closed: missing " + ", ".join(missing))
        return d
    if cfg.paper_mode and not swing_fits_budget(state["per_trade_swing_usd"], cfg):
        d.block(f"paper mode: 1R must be positive and finite, got {state['per_trade_swing_usd']!r}")
        return d
    cfg = effective_config(cfg, state["per_trade_swing_usd"])

    budget = budget_allowed(state["strategy"], state["paper_trades"],
                            state["paper_slippage_measured"], state["paper_net_usd"], cfg)
    if budget <= 0:
        d.block(f"{state['strategy']} is not fundable at this budget")
    if not cfg.paper_mode and not swing_fits_budget(state["per_trade_swing_usd"], cfg):
        d.block(f"per-trade swing ${state['per_trade_swing_usd']:.0f} outside "
                f"${cfg.per_trade_swing_min_usd:.0f}-{cfg.per_trade_swing_max_usd:.0f}")
    if state["remaining_budget_usd"] > budget + 1e-6:   # tolerance: float rounding, not a real breach
        d.block(f"remaining budget ${state['remaining_budget_usd']:.0f} exceeds allowed ${budget:.0f}")
    if trailing_kill(state["equity_usd"], state["peak_profit_usd"], cfg):
        d.block(f"TRAILING KILL: equity ${state['equity_usd']:.0f} <= "
                f"${trailing_kill_level(state['peak_profit_usd'], cfg):.0f}")
    sk = slippage_kill(state["fill_deviations_pts"], state["working_edge_pts"], cfg)
    if sk:
        d.block("SLIPPAGE KILL: mean fill deviation over last "
                f"{cfg.slippage_window_fills} fills > {cfg.slippage_kill_fraction_of_edge:.0%} of edge")
    elif sk is None:
        d.divergences.append("slippage not yet measurable (< 20 fills)")
    if signal_divergence(state["live_signals_today"], state["reference_signals_today"]):
        d.block("SIGNAL DIVERGENCE HALT: live engine != frozen reference -- flag Jason")
    if daily_loss_cap_hit(state["day_pnl_usd"], state["remaining_budget_usd"], cfg):
        d.block("DAILY LOSS CAP: day P&L at/below half of remaining budget")
    if catastrophe_tail_finding(state["catastrophe_flags"], cfg):
        d.divergences.append("TAIL FINDING: >2 catastrophe stops in 40 trades -- report, never tune")
    if state["open_positions"] >= cfg.max_open_positions:
        d.block("position cap reached")
    if state["orders_today"] >= cfg.max_orders_per_day:
        d.block("daily order cap reached")
    if state["contracts"] > cfg.max_contracts:
        d.block(f"contracts {state['contracts']} > cap {cfg.max_contracts}")
    return d


if __name__ == "__main__":
    print(json.dumps(asdict(CONFIG), indent=1))
