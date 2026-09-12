"""UPGRADE 6: every capital-protection rule pinned. These are account
controls; a change here is a change to what Jason authorized."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import capital_protection as cp  # noqa: E402


def _ok_state(**over):
    s = dict(strategy="M2_open_break", paper_trades=0, paper_slippage_measured=False,
             paper_net_usd=0.0, per_trade_swing_usd=90.0, equity_usd=0.0, peak_profit_usd=0.0,
             remaining_budget_usd=300.0, day_pnl_usd=0.0, fill_deviations_pts=[],
             working_edge_pts=10.0, live_signals_today=["L"], reference_signals_today=["L"],
             open_positions=0, orders_today=0, contracts=1, catastrophe_flags=[])
    s.update(over)
    return s


def test_frozen_config_matches_jasons_numbers():
    c = cp.CONFIG
    assert c.starting_budget_usd == 300 and c.raised_budget_usd == 500
    assert c.paper_record_min_trades == 20 and "H118" in c.excluded_strategies
    assert abs(c.trailing_giveback_fraction - 1 / 3) < 1e-9
    assert c.slippage_window_fills == 20 and c.slippage_kill_fraction_of_edge == 0.25
    assert c.catastrophe_stop_r == 2.0 and c.daily_loss_cap_fraction_of_remaining == 0.5


def test_budget_ladder_and_h118_exclusion():
    assert cp.budget_allowed("H118", 100, True, 500.0) == 0.0
    assert cp.budget_allowed("X", 0, False, 0.0) == 300.0
    assert cp.budget_allowed("X", 20, True, 1.0) == 500.0
    assert cp.budget_allowed("X", 20, False, 1.0) == 300.0     # slippage not measured
    assert cp.budget_allowed("X", 20, True, -1.0) == 300.0     # not positive
    assert cp.budget_allowed("X", 19, True, 1.0) == 300.0      # backtest never counts


def test_swing_window_excludes_h118_sized_trades():
    assert cp.swing_fits_budget(90)
    assert not cp.swing_fits_budget(1200)


def test_trailing_kill_levels():
    assert cp.trailing_kill_level(0) == -300
    assert cp.trailing_kill_level(600) == 300          # give back 300 (larger than 200)
    assert abs(cp.trailing_kill_level(1200) - 800) < 1e-9   # give back 400 = 1/3
    assert cp.trailing_kill(-300, 0) and not cp.trailing_kill(-299, 0)
    assert cp.trailing_kill(799, 1200) and not cp.trailing_kill(801, 1200)


def test_slippage_kill():
    assert cp.slippage_kill([1.0] * 19, 10.0) is None
    assert cp.slippage_kill([2.0] * 20, 10.0) is False
    assert cp.slippage_kill([3.0] * 20, 10.0) is True
    assert cp.slippage_kill([0.0] * 5 + [3.0] * 20, 10.0) is True   # only the last 20 count
    assert cp.slippage_kill([0.1] * 20, 0.0) is True


def test_signal_divergence_zero_tolerance():
    assert not cp.signal_divergence(["L", None], ["L", None])
    assert cp.signal_divergence(["L"], ["S"])
    assert cp.signal_divergence([], ["L"])


def test_catastrophe_and_daily_cap():
    assert cp.catastrophe_stop_hit("long", 100, 80, 10)
    assert not cp.catastrophe_stop_hit("long", 100, 81, 10)
    assert cp.catastrophe_stop_hit("short", 100, 120, 10)
    assert cp.catastrophe_stop_hit("long", 100, 100, 0)          # fail closed
    assert cp.daily_loss_cap_hit(-150, 300) and not cp.daily_loss_cap_hit(-149, 300)
    assert cp.catastrophe_tail_finding([True, True, True] + [False] * 37)
    assert not cp.catastrophe_tail_finding([True, True] + [False] * 38)
    assert not cp.catastrophe_tail_finding([True] * 3 + [False] * 40)  # window is last 40


def test_pre_order_allows_clean_state_and_fails_closed():
    assert cp.pre_order_check(_ok_state()).allow
    d = cp.pre_order_check({})
    assert not d.allow and d.reasons[0].startswith("fail-closed")


def test_pre_order_blocks_each_rule():
    assert not cp.pre_order_check(_ok_state(strategy="H118")).allow
    assert not cp.pre_order_check(_ok_state(equity_usd=-300)).allow
    assert not cp.pre_order_check(_ok_state(fill_deviations_pts=[5.0] * 20)).allow
    assert not cp.pre_order_check(_ok_state(reference_signals_today=["S"])).allow
    assert not cp.pre_order_check(_ok_state(day_pnl_usd=-150)).allow
    assert not cp.pre_order_check(_ok_state(open_positions=1)).allow
    assert not cp.pre_order_check(_ok_state(contracts=2)).allow
    assert not cp.pre_order_check(_ok_state(remaining_budget_usd=500)).allow  # no paper record yet
    assert cp.pre_order_check(_ok_state(remaining_budget_usd=500, paper_trades=25,
                                        paper_slippage_measured=True, paper_net_usd=40)).allow


def test_tail_finding_is_logged_not_blocking():
    d = cp.pre_order_check(_ok_state(catastrophe_flags=[True] * 3))
    assert d.allow and any("TAIL FINDING" in x for x in d.divergences)
