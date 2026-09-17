"""Salvage check (standing directive s.7): menu only, profitable = net > 0 with
>= 15 trades, thin sides reported not spawned, spec-named fields honoured."""
from __future__ import annotations
import sys
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import salvage_check as sc  # noqa: E402


def _t(d, usd, r, trig="09:40", src="prior_day_low", direction="long"):
    return {"date": d, "usd_net_1": usd, "r_net": r, "direction": direction,
            "context": {"trigger_time": f"{d} {trig}:00-04:00", "level_source": src}}


def test_side_stats_profitable_needs_min_n_and_positive_net():
    s = sc._side_stats([_t("2021-01-04", 10.0, 0.5)] * 20)
    assert s["profitable"] and not s["thin"]
    s = sc._side_stats([_t("2021-01-04", 10.0, 0.5)] * 5)
    assert not s["profitable"] and s["thin"] and s["positive_but_thin"]
    s = sc._side_stats([_t("2021-01-04", -10.0, -0.5)] * 20)
    assert not s["profitable"] and not s["positive_but_thin"]


def test_time_of_day_and_news_labels():
    assert sc.tod_label(_t("2021-01-04", 1, 1, trig="08:45")) == "OPEN_PRE0930"
    assert sc.tod_label(_t("2021-01-04", 1, 1, trig="09:45")) == "OPEN_0930_1000"
    assert sc.tod_label(_t("2021-01-04", 1, 1, trig="11:00")) == "MIDDAY_0930_1200"
    assert sc.tod_label(_t("2021-01-04", 1, 1, trig="14:00")) == "AFTERNOON"
    from study_fomc_volatility import FOMC_DATES
    lab = sc.news_labels([FOMC_DATES[0], date(2015, 1, 5)])
    assert lab[FOMC_DATES[0]] == "NEWS" and lab[date(2015, 1, 5)] == "QUIET"


def test_run_reports_menu_and_spec_named_conditions_without_price_data(monkeypatch):
    monkeypatch.setattr(sc, "vxn_labels", lambda dates: {d: "LOW" for d in dates})
    trades = [_t("2021-01-04", 10.0, 0.5, src="prior_day_low")] * 16 + [_t("2021-01-05", -20.0, -1.0, src="premarket_low")] * 16
    out = sc.run(trades, None, ["level_source"])
    names = [c["condition"] for c in out["conditions"]]
    assert len(names) == 5 and names[-1] == "spec-named: level_source"
    found = {(f["condition"].split(":")[0], f["side"]) for f in out["profitable_conditions"]}
    assert ("spec-named", "prior_day_low") in found
    assert out["conditions"][1]["sides"]["UNKNOWN"]["n"] == 32       # no price data -> condition 2 unknown
    assert out["verdict"].startswith("condition found")
    out2 = sc.run([_t("2021-01-04", -1.0, -0.1)] * 20, None, [])
    assert out2["verdict"].startswith("nothing")


# --------------------------------------------------------------------------
# FAIL-CLOSED on stale reference data (2026-09-16)
#
# The Salvage menu's conditions 1 and 4 read the VXN series and the FOMC/CPI/NFP
# calendar. Both used to fail OPEN: a date past the VXN series got the last
# close ffilled onto it, and a date past the calendar came back "QUIET" because
# the sourced lists stop in 2021/2023, not because the day was quiet. Either one
# decides a salvage -- and spawns a candidate -- on a classification nobody
# measured. They must refuse the session instead.
# --------------------------------------------------------------------------
def test_news_labels_refuse_a_session_past_the_calendar_instead_of_calling_it_quiet():
    import pytest
    from reference_data import ReferenceDataUnavailable
    with pytest.raises(ReferenceDataUnavailable):
        sc.news_labels([date(2026, 9, 16)])


def test_vxn_labels_refuse_a_session_past_the_series_instead_of_carrying_it_forward():
    import pytest
    from reference_data import ReferenceDataUnavailable, vxn_coverage_end
    end = vxn_coverage_end()
    with pytest.raises(ReferenceDataUnavailable) as e:
        sc.vxn_labels([end, end + timedelta(days=30)])
    assert "Salvage menu condition 1" in str(e.value)
    # inside coverage it still labels normally
    assert sc.vxn_labels([end])[end] in {"HIGH", "LOW"}


def test_market_state_frame_does_not_carry_vxn_past_the_series_end():
    """extend_state_frame's ffill is right for a holiday inside the series and
    wrong past its end -- past the end it must be NaN, not the last known level."""
    import pandas as pd
    import numpy as np
    from reference_data import vxn_coverage_end
    import market_state_primitives_v2 as msp
    end = vxn_coverage_end()
    idx = [end - timedelta(days=5), end, end + timedelta(days=5), end + timedelta(days=12)]
    states = pd.DataFrame({"atr14": [100.0] * 4,
                           "directional_persistence": [0.1, 0.2, 0.3, 0.4]}, index=idx)
    bars = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"],
                        index=pd.DatetimeIndex([], tz="America/New_York"))
    out = msp.extend_state_frame(states, bars)
    assert np.isnan(out.loc[idx[2], "vxn_level_vs_trailing"])
    assert np.isnan(out.loc[idx[3], "vxn_level_vs_trailing"])
