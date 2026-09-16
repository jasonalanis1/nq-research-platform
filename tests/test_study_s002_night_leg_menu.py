"""S002 SOURCE->SPECIFY diagnostic: the night leg is 16:00 bar close (D-1) -> 09:30 bar
open (D), Monday legs are tagged weekend, sessions without a 09:30 bar are dropped,
and net = points x $2 - the ASSUMED $6 round trip."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import study_s002_night_leg_menu as m  # noqa: E402


def _session(date, close_px, open_px):
    idx = pd.date_range(f"{date} 09:30", f"{date} 15:59", freq="min", tz="America/New_York")
    o = np.full(len(idx), open_px, float); c = np.full(len(idx), close_px, float)
    return pd.DataFrame({"Open": o, "High": np.maximum(o, c) + 1, "Low": np.minimum(o, c) - 1, "Close": c, "Volume": 1.0}, index=idx)


def test_night_leg_points_and_weekend_tag():
    fri = _session("2021-01-08", 1000.0, 990.0)      # closes 1000
    mon = _session("2021-01-11", 1030.0, 1010.0)     # opens 1010 -> +10 pts = $20 gross, $17.40 net
    # (corrected MNQ round trip $2.60, src/cost_model.py -- was $6.00)
    tue = _session("2021-01-12", 1020.0, 1025.0)     # opens 1025 vs Monday close 1030 -> -5 pts
    legs = m.night_legs(pd.concat([fri, mon, tue]))
    assert [(l["date"], l["points"], l["usd_net_1"], l["weekend"]) for l in legs] == \
           [("2021-01-11", 10.0, 17.4, True), ("2021-01-12", -5.0, -12.6, False)]


def test_session_without_0930_bar_is_dropped_and_breaks_the_chain():
    a = _session("2021-01-11", 1000.0, 990.0)
    b = _session("2021-01-12", 1020.0, 1010.0).iloc[30:]     # starts 10:00 -> no 09:30 bar
    c = _session("2021-01-13", 1020.0, 1015.0)
    legs = m.night_legs(pd.concat([a, b, c]))
    assert [l["date"] for l in legs] == ["2021-01-13"] and legs[0]["points"] == -5.0
