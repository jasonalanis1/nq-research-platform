"""Revamp list (standing directive s.9): closeness is mechanical, mechanism is a
stated judgment, calendar anomalies stay dead, directive-named items are top."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import revamp_list as rl  # noqa: E402


def test_closeness_from_intervals_and_fallbacks():
    c, b = rl.closeness({"notes": "P1 FAIL: mean +0.03, ci_90=(-0.10,+0.30) n=131", "parameters": {}})
    assert c == 0.5 and "75%" in b                      # 0.30/0.40 = 75% above zero -> 2*(0.75-0.5)
    c, _ = rl.closeness({"notes": "CI (-0.2, +0.2)", "parameters": {}})
    assert c == 0.0
    c, b = rl.closeness({"notes": "", "parameters": {"ci_90_compressed": [0.01, 0.2]}})
    assert c == 1.0 and "credible cell" in b
    assert rl.closeness({"notes": "", "parameters": {}, "expectancy_r": 0.02})[0] == 0.3
    assert rl.closeness({"notes": "", "parameters": {}, "expectancy_r": None})[0] == 0.0


def test_mechanism_reads_the_doc_and_calls_calendar_anomalies_low():
    hi, b = rl.mechanism({"strategy_name": "level-sweep-reversal-prior-day-narrow-m26", "notes": "", "parameters": {}})
    assert hi == "HIGH" and "m26" in b
    lo, b = rl.mechanism({"strategy_name": "pre_holiday_effect_nq_m28", "notes": "", "parameters": {}})
    assert lo == "LOW" and "calendar" in b
    lo, _ = rl.mechanism({"strategy_name": "us_dst_transition_anomaly_nq_m32", "notes": "", "parameters": {}})
    assert lo == "LOW"          # the shared M32 anchor resolves to the DST doc by name overlap
    med, _ = rl.mechanism({"strategy_name": "some_chart_pattern", "strategy_origin": "external_claim", "notes": "", "parameters": {}})
    assert med == "MED"
    lo, _ = rl.mechanism({"strategy_name": "opening_volume_imbalance", "strategy_origin": "rd_generated", "notes": "", "parameters": {}})
    assert lo == "LOW"          # a loose word match must NOT hand a raw effect a mechanism doc


def test_build_tiers_and_directive_named_items():
    latest = {
        "hyp-000157": {"hypothesis_id": "hyp-000157", "strategy_name": "month-end-payment-cycle-reversal-nq-m24", "strategy_status": "REJECTED",
                       "notes": "ci_90=(-0.01,+0.5)", "parameters": {}, "strategy_origin": "jason_hypothesis"},
        "hyp-000164": {"hypothesis_id": "hyp-000164", "strategy_name": "us_dst_transition_anomaly_nq_m32", "strategy_status": "REJECTED",
                       "notes": "CI (+5.57,+25.22) credible but positive", "parameters": {}, "strategy_origin": "jason_hypothesis"},
        "hyp-000148": {"hypothesis_id": "hyp-000148", "strategy_name": "eia_report_volatility_jump_cl_m20", "strategy_status": "REJECTED",
                       "notes": "NO CREDIBLE PATH", "parameters": {}, "strategy_origin": "jason_hypothesis"},
        "hyp-000001": {"hypothesis_id": "hyp-000001", "strategy_name": "raw_thing", "strategy_status": "REJECTED",
                       "notes": "ci_90=(-0.3,+0.3)", "parameters": {}, "strategy_origin": "rd_generated"},
        "hyp-000002": {"hypothesis_id": "hyp-000002", "strategy_name": "still_open", "strategy_status": "PROMISING",
                       "notes": "", "parameters": {}, "strategy_origin": "rd_generated"},
    }
    d = rl.build(latest)
    ids = {e["hypothesis_id"]: e for e in d["entries"]}
    assert "hyp-000002" not in ids                       # not closed
    assert ids["hyp-000157"]["tier"] == "top" and "directive" in ids["hyp-000157"]["disposition"]
    assert ids["hyp-000164"]["tier"] == "bottom" and ids["hyp-000164"]["closeness"] == 1.0   # credible but calendar: stays dead
    assert ids["hyp-000148"]["tier"] == "middle"
    assert ids["hyp-000001"]["tier"] == "bottom"
    assert d["tiers"]["top"][0] == "hyp-000157" and "JUDGMENT" in d["judgment_note"]


def test_written_list_exists_and_names_the_first_candidates():
    d = json.loads((Path(__file__).resolve().parent.parent / "research" / "ledger" / "revamp_list.json").read_text())
    top = set(d["tiers"]["top"])
    assert {"hyp-000159", "hyp-000145", "hyp-000157", "hyp-000121", "hyp-000162", "hyp-000161"} <= top
    assert {"hyp-000163", "hyp-000164", "hyp-000165", "hyp-000166", "hyp-000167"} <= set(d["tiers"]["bottom"])
    assert set(d["tiers"]["middle"]) >= {"hyp-000148", "hyp-000150"}
