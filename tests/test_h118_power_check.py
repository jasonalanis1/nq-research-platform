"""UPGRADE 5: the power check is deterministic, reads the published CIs,
and reports honestly (power at n=40 for 0.40R is well under 50%)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import h118_power_check as h  # noqa: E402


def test_sd_backed_out_of_ci_is_plausible():
    out = h.run(mc=False)
    for s in out["per_trade_sd_by_stage"].values():
        assert 1.5 < s["sd_r"] < 3.5
    assert 1.8 < out["pooled_per_trade_sd_r"] < 2.8


def test_power_monotone_in_effect_and_n():
    sd = 2.27
    assert h.power_normal(0.62, sd) > h.power_normal(0.40, sd) > h.power_normal(0.14, sd)
    assert h.power_normal(0.40, sd, 80) > h.power_normal(0.40, sd, 40)


def test_review_point_is_underpowered_and_locked():
    out = h.run(mc=False)
    row = next(r for r in out["power"] if r["true_effect_r"] == 0.40)
    assert row["power_normal_at_40"] < 0.5
    assert row["n_for_80pct_power"] > 100
    assert out["review_point"]["resolved_trades"] == 40
    assert "never moves" in out["review_point"]["rule"]
