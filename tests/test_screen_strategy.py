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
    # day 1: long, rallies to target (+10 pts = +$20 gross, +$14 net); day 2: short, stopped (-$20 gross, -$26 net); day 3: no signal
    d1 = _bars("2021-01-04", [100, 100, 100, 111, 111, 111])
    d2 = _bars("2021-01-05", [100, 100, 100, 111, 111, 111])
    d3 = _bars("2021-01-06", [100, 100, 100, 100, 100, 100])
    df = pd.concat([d1, d2, d3])
    mod, calls = _module({"2021-01-04": "long", "2021-01-05": "short"})
    res = ss.screen(mod, df, "test")
    assert calls["precompute"] == 1
    assert res["sessions"] == 3 and res["trades"] == 2
    assert res["gross_usd_1_micro"] == 0.0 and res["assumed_costs_usd_1"] == 12.0
    assert res["net_usd_1_micro"] == -12.0 and res["net_usd_10_micro"] == -120.0
    assert res["made_money_after_assumed_costs"] is False and res["win_rate"] == 0.5
    t = res["trades_detail"]
    assert t[0]["exit_reason"] == "target" and t[1]["exit_reason"] == "stop"
    assert t[0]["r_net"] == 0.7 and t[1]["r_net"] == -1.3         # ($20-$6)/$20 ; (-$20-$6)/$20
    assert "ASSUMED" in res["cost_basis"] and "_resolve_fill_outcome" in res["bookkeeping"]


def test_screen_passes_when_net_positive_and_matches_paper_loop_exit():
    d1 = _bars("2021-01-04", [100, 100, 100, 111, 111, 111])
    mod, _ = _module({"2021-01-04": "long"})
    res = ss.screen(mod, d1, "test")
    assert res["made_money_after_assumed_costs"] is True and res["net_usd_1_micro"] == 14.0
    # the same signal through the paper loop's own exit gives the same R
    sig = mod.generate_signals(d1)[0]
    out = bpr._resolve_fill_outcome(d1, "long", sig.timestamp, sig.entry, sig.stop, sig.target, "15:55")
    assert out["r_multiple"] == res["trades_detail"][0]["r_gross"]


def test_exposure_count_is_information_only():
    assert isinstance(ss.exposure_count(), int)
