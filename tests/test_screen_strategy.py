"""SCREEN (standing directive s.2): one number, net of ASSUMED costs, using the
paper loop's own bookkeeping so screen and paper cannot drift."""
from __future__ import annotations
import sys, types
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import screen_strategy as ss  # noqa: E402
import bot_stack_paper_run as bpr  # noqa: E402
from strategy_contract import Signal, risk_multiple  # noqa: E402


def _bars(date, prices):
    idx = pd.date_range(f"{date} 09:30", periods=len(prices), freq="min", tz="America/New_York")
    o = [p for p in prices]
    return pd.DataFrame({"Open": o, "High": [p + 0.5 for p in o], "Low": [p - 0.5 for p in o], "Close": o}, index=idx)


def _module(direction_by_day):
    calls = {"precompute": 0}

    def generate_signals(df, history=None):
        out = []
        for day, g in df.groupby(df.index.date):
            d = direction_by_day.get(str(day))
            if not d:
                continue
            e = float(g["Open"].iloc[1])
            stop = e - 10 if d == "long" else e + 10
            target = e + 10 if d == "long" else e - 10
            out.append(Signal(strategy_name="t", strategy_version="v", timestamp=g.index[1], instrument="MNQ", timeframe="1m",
                              direction=d, entry=e, stop=stop, target=target, risk_multiple=risk_multiple(e, stop, target),
                              validation_status="paper-candidate", market_context={"time_exit": "15:55", "date": str(day)}))
        return out

    def precompute(history):
        calls["precompute"] += 1
    return types.SimpleNamespace(STRATEGY_NAME="t", STRATEGY_VERSION="v", generate_signals=generate_signals, precompute=precompute), calls


def test_screen_uses_paper_bookkeeping_and_assumed_costs():
    # Corrected cost (Jason, September 16th 2026): MNQ market round trip $2.60 = 1.30 pt.
    # day 1: long, target (+10 pts = +$20 gross, +$17.40 net); day 2: short, stopped (-$20 gross, -$22.60 net); day 3: no signal
    d1 = _bars("2021-01-04", [100, 100, 100, 111, 111, 111])
    d2 = _bars("2021-01-05", [100, 100, 100, 111, 111, 111])
    d3 = _bars("2021-01-06", [100, 100, 100, 100, 100, 100])
    df = pd.concat([d1, d2, d3])
    mod, calls = _module({"2021-01-04": "long", "2021-01-05": "short"})
    res = ss.screen(mod, df, "test")
    assert calls["precompute"] == 1
    assert res["sessions"] == 3 and res["trades"] == 2
    assert res["gross_usd_1_micro"] == 0.0 and res["assumed_costs_usd_1"] == 5.20
    assert res["net_usd_1_micro"] == -5.20 and res["net_usd_10_micro"] == -52.0
    assert res["made_money_after_assumed_costs"] is False and res["win_rate"] == 0.5
    t = res["trades_detail"]
    assert t[0]["exit_reason"] == "target" and t[1]["exit_reason"] == "stop"
    assert t[0]["r_net"] == 0.87 and t[1]["r_net"] == -1.13       # ($20-$2.60)/$20 ; (-$20-$2.60)/$20
    assert t[0]["pts_gross"] == 10.0 and t[1]["pts_gross"] == -10.0
    assert "ASSUMED" in res["cost_basis"] and "_resolve_fill_outcome" in res["bookkeeping"]


def test_screen_passes_when_net_positive_and_matches_paper_loop_exit():
    d1 = _bars("2021-01-04", [100, 100, 100, 111, 111, 111])
    mod, _ = _module({"2021-01-04": "long"})
    res = ss.screen(mod, d1, "test")
    assert res["made_money_after_assumed_costs"] is True and res["net_usd_1_micro"] == 17.40
    # the same signal through the paper loop's own exit gives the same R
    sig = mod.generate_signals(d1)[0]
    out = bpr._resolve_fill_outcome(d1, "long", sig.timestamp, sig.entry, sig.stop, sig.target, "15:55")
    assert out["r_multiple"] == res["trades_detail"][0]["r_gross"]


def test_exposure_count_is_information_only():
    assert isinstance(ss.exposure_count(), int)


def test_screen_reports_all_four_cost_combinations_on_the_same_trades():
    """Jason, September 16th 2026: every screen shows MNQ/NQ x market/limit side
    by side -- net $, net R and the per-trade edge in points against the per-trade
    cost in points -- so it is visible whether the cost wall is the pattern or the
    contract. Same trades in every row; only the cost overlay differs."""
    d1 = _bars("2021-01-04", [100, 100, 100, 111, 111, 111])
    d2 = _bars("2021-01-05", [100, 100, 100, 111, 111, 111])
    mod, _ = _module({"2021-01-04": "long", "2021-01-05": "short"})
    res = ss.screen(mod, pd.concat([d1, d2]), "test")
    cc = res["cost_combinations"]
    by = {r["key"]: r for r in cc["combinations"]}
    assert [r["key"] for r in cc["combinations"]] == ["MNQ_market", "MNQ_limit", "NQ_market", "NQ_limit"]
    assert {r["gross_points_total"] for r in cc["combinations"]} == {0.0}      # ONE record
    assert by["MNQ_market"]["net_usd_total"] == -5.20 and by["MNQ_market"]["cost_points_per_trade"] == 1.30
    assert by["NQ_market"]["net_usd_total"] == -29.80 and by["NQ_market"]["cost_points_per_trade"] == 0.745
    assert by["NQ_limit"]["net_usd_total"] == -19.80
    # net R per combination: cost in points / risk points (10) subtracted from gross R
    assert abs(by["MNQ_market"]["avg_r_net"] - (-0.13)) < 1e-9
    assert abs(by["NQ_market"]["avg_r_net"] - (-0.0745)) < 1e-9
    assert by["MNQ_limit"]["optimistic"] and by["NQ_limit"]["optimistic"]
    assert not by["MNQ_market"]["optimistic"]
    assert "NOT re-scored" in cc["note"] and "adversely selected" in cc["optimistic_note"]


def test_screen_printout_labels_limit_rows_optimistic(capsys):
    import cost_model as cm
    d1 = _bars("2021-01-04", [100, 100, 100, 111, 111, 111])
    mod, _ = _module({"2021-01-04": "long"})
    res = ss.screen(mod, d1, "test")
    assert "OPTIMISTIC" in cm.label("MNQ", "limit") and "OPTIMISTIC" in cm.label("NQ", "limit")
    assert "1.300 pt" in res["cost_basis"] or "1.30" in res["cost_basis"]
    assert "$2.60" in res["cost_basis"] and "cost_model" in res["cost_basis"]
