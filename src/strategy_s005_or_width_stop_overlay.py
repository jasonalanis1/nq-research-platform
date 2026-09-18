"""
strategy_s005_or_width_stop_overlay.py -- S005, opening-range width
(hyp-000162) as a STOP-SIZING OVERLAY on the frozen S008.

hyp-000162 is VALIDATED_NOT_PROMOTED (research/studies/hyp162-portfolio-
2026-09-14.md: joint residual retention ~17.7%, 90% CI -14.3%..+15.1% against a
50% bar; adding it to the forecast stack made the forecast very slightly WORSE,
MAE 0.3252 -> 0.3256). It is NEVER a standalone strategy. The one narrow
pre-specified question here is whether using it to set STOP DISTANCE and TARGET
on an ALREADY-FROZEN strategy improves that strategy's screen result.

HOST: S008 (late-day constant-leverage rebalance continuation, frozen
2026-09-16) -- the best-performing frozen strategy, the only one in PAPER that is
NOT SLOW, and the one whose stop is already sized off an intraday RANGE, which is
exactly the quantity this fact would inform.

S008's FROZEN SPEC AND MODULE ARE NOT EDITED (directive s.13). This module
imports S008 READ-ONLY and rescales the risk it hands back.

FROZEN with its spec:
research/infrastructure/strategy-specs/S005-or-width-stop-overlay-on-S008.md.

THE OVERLAY -- THE ONLY THING THAT CHANGES
  known-at   10:00 ET, from that session's own RTH bars:
               ORW     = High(09:30..10:00) - Low(09:30..10:00)
               ORW_med = median(ORW) over the trailing 20 RTH sessions,
                         STRICTLY EARLIER than the one being traded
               k       = clip(ORW / ORW_med, 0.75, 1.35)
  risk'      = k * 0.50 * RNG            (host: risk = 0.50 * RNG)
  target'    = entry +/- 1.50 * risk'    (the 1.5R multiple is unchanged)
  fallback   k = 1.0 exactly (the host's own trade) whenever ORW or its
             trailing median is unavailable.

Direction is the validated fact's own: a WIDE opening half-hour forecasts a wider
midday/afternoon, so the stop is WIDENED to avoid being shaken out by the
expected noise, and tightened on a narrow open. The [0.75, 1.35] clip is a
sanity bound fixed in the spec BEFORE any result, not a tuned parameter.

THE OVERLAY NEVER CREATES, SUPPRESSES OR RE-DIRECTS A TRADE. Condition,
direction, 15:00 ET decision, next-bar-open entry, 15:55 ET time exit, 1 micro
MNQ and the 1.5R multiple all come from the host unchanged, so trade count and
entry price are identical to the host's by construction and only the stop and
target move.

NO LOOK-AHEAD: ORW is measured at 10:00 ET, five hours BEFORE the host's 15:00
decision; the trailing median uses sessions strictly earlier than the traded one;
the only bar read after the decision is the next bar's open, which is the host's
fill price by construction.

CONTRACT: STRATEGY_NAME, STRATEGY_VERSION, precompute(history),
generate_signals(df, history=None) -> list[strategy_contract.Signal].
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from strategy_contract import Signal, risk_multiple  # noqa: E402
import cost_model  # noqa: E402
import strategy_s008_late_day_rebalance_continuation as host  # noqa: E402  READ-ONLY

STRATEGY_ID = "S005"
STRATEGY_NAME = "s005_or_width_stop_overlay_on_s008"
STRATEGY_VERSION = "S005-1.0 (frozen 2026-09-17)"
VALIDATION_STATUS = "paper-candidate"
SPEC_PATH = "research/infrastructure/strategy-specs/S005-or-width-stop-overlay-on-S008.md"

HOST_ID = host.STRATEGY_ID
HOST_VERSION = host.STRATEGY_VERSION
OR_START = "09:30"
OR_END = "10:00"                 # opening range known at 10:00 ET
OR_MIN_BARS = 28                 # completeness guard on the 31-bar 09:30-10:00 window
TRAILING_SESSIONS = 20
K_MIN, K_MAX = 0.75, 1.35        # sanity band, fixed in the spec before any result
INSTRUMENT = host.INSTRUMENT

_OR_WIDTH: dict = {}             # session date -> ORW
_OR_MEDIAN: dict = {}            # session date -> trailing-20 median of ORW, shifted


def opening_range_width(day_df: pd.DataFrame) -> float | None:
    """ORW = the 09:30-10:00 high-low range, or None if that window is a fragment."""
    win = day_df.between_time(OR_START, OR_END, inclusive="both")
    if len(win) < OR_MIN_BARS:
        return None
    if win.index[0].strftime("%H:%M") != OR_START or win.index[-1].strftime("%H:%M") != OR_END:
        return None
    w = float(win["High"].max() - win["Low"].min())
    return w if w > 0 else None


def precompute(history: pd.DataFrame) -> None:
    """Build the per-session ORW and its trailing-20 median (shifted, so a session
    never reads its own value or any later one), then hand `history` to the host's
    own precompute so the host is driven exactly as it is standalone."""
    _OR_WIDTH.clear()
    _OR_MEDIAN.clear()
    dates, widths = [], []
    for day, g in history.groupby(history.index.date):
        w = opening_range_width(g)
        if w is None:
            continue
        _OR_WIDTH[day] = w
        dates.append(day)
        widths.append(w)
    s = pd.Series(widths, index=pd.Index(dates))
    med = s.rolling(TRAILING_SESSIONS, min_periods=TRAILING_SESSIONS).median().shift(1)
    for d, m in med.items():
        if np.isfinite(m) and m > 0:
            _OR_MEDIAN[d] = float(m)
    host.precompute(history)


def scaler_for_day(day) -> tuple[float, dict]:
    """k and its provenance for one session. k = 1.0 exactly when the input is
    unavailable -- the host's own trade, never a guess."""
    w = _OR_WIDTH.get(day)
    m = _OR_MEDIAN.get(day)
    if w is None or m is None or not (m > 0):
        return 1.0, {"or_width": w, "or_width_trailing_median": m,
                     "or_width_ratio": None, "k": 1.0,
                     "k_basis": "input unavailable -- host stop unchanged", "k_clipped": False}
    ratio = w / m
    k = min(max(ratio, K_MIN), K_MAX)
    return k, {"or_width": w, "or_width_trailing_median": m,
               "or_width_ratio": float(ratio), "k": float(k),
               "k_basis": f"clip(ORW / trailing-{TRAILING_SESSIONS} median ORW, {K_MIN}, {K_MAX})",
               "k_clipped": bool(k != ratio)}


def signal_for_day(day_df: pd.DataFrame) -> dict | None:
    """The host's own signal with the risk rescaled by k. None whenever the host
    would not trade -- the overlay never creates a trade."""
    s = host.signal_for_day(day_df)
    if s is None:
        return None
    k, prov = scaler_for_day(s["date"])
    risk = k * s["risk_points"]
    if risk <= 0:
        return None
    entry = s["entry"]
    if s["direction"] == "long":
        stop, target = entry - risk, entry + host.TARGET_R_MULTIPLE * risk
    else:
        stop, target = entry + risk, entry - host.TARGET_R_MULTIPLE * risk
    out = dict(s)
    out.update({"stop": stop, "target": target, "risk_points": risk,
                "host_risk_points": s["risk_points"], "overlay": prov})
    return out


def _to_signal(s: dict) -> Signal:
    p = s["overlay"]
    return Signal(
        strategy_name=STRATEGY_NAME, strategy_version=STRATEGY_VERSION,
        timestamp=s["entry_time"], instrument=INSTRUMENT, timeframe="1m",
        direction=s["direction"], entry=s["entry"], stop=s["stop"], target=s["target"],
        risk_multiple=risk_multiple(s["entry"], s["stop"], s["target"]),
        validation_status=VALIDATION_STATUS,
        market_context={
            "strategy_id": STRATEGY_ID, "spec": SPEC_PATH, "date": str(s["date"]),
            "host_strategy_id": HOST_ID, "host_version": HOST_VERSION,
            "condition": "host S008 condition, unchanged (overlay never creates or suppresses a trade)",
            "move_points": s["move"], "session_range": s["session_range"],
            "trailing_median_range": s["trailing_median_range"],
            "decision_time": str(s["decision_time"]),
            "or_width": p["or_width"], "or_width_trailing_median": p["or_width_trailing_median"],
            "or_width_ratio": p["or_width_ratio"], "stop_scaler_k": p["k"],
            "k_basis": p["k_basis"], "k_clipped": p["k_clipped"],
            "host_risk_points": s["host_risk_points"], "risk_points": s["risk_points"],
            "stop_basis": f"k x {host.STOP_FRACTION} x the {host.SESSION_OPEN}-{host.DECISION_TIME} range",
            "target_basis": f"{host.TARGET_R_MULTIPLE}R on the rescaled risk",
            "cost_basis": cost_model.DEFAULT_NOTE,
            "time_exit": host.TIME_EXIT,
        },
    )


def generate_signals(df: pd.DataFrame, history: pd.DataFrame | None = None) -> list[Signal]:
    if not _OR_MEDIAN or not host._TRAILING_MEDIAN:
        precompute(history if history is not None else df)
    out = []
    for _, g in df.groupby(df.index.date):
        s = signal_for_day(g)
        if s is not None:
            out.append(_to_signal(s))
    return out


def audit(signals: list[Signal]) -> dict:
    dates = [sg.market_context["date"] for sg in signals]
    dup = len(dates) - len(set(dates))
    lookahead = sum(1 for sg in signals
                    if pd.Timestamp(sg.market_context["decision_time"]) >= pd.Timestamp(sg.timestamp))
    bad_rr = sum(1 for sg in signals
                 if round(sg.risk_multiple, 2) != host.TARGET_R_MULTIPLE)
    zero_risk = sum(1 for sg in signals if abs(sg.entry - sg.stop) <= 0)
    wrong_dir = sum(1 for sg in signals
                    if (sg.market_context["move_points"] > 0) != (sg.direction == "long"))
    bad_k = sum(1 for sg in signals
                if not (K_MIN - 1e-9 <= sg.market_context["stop_scaler_k"] <= K_MAX + 1e-9))
    bad_risk = sum(1 for sg in signals
                   if abs(sg.market_context["risk_points"]
                          - sg.market_context["stop_scaler_k"] * sg.market_context["host_risk_points"]) > 1e-6)
    ks = [sg.market_context["stop_scaler_k"] for sg in signals]
    return {"n_signals": len(signals), "duplicate_days": dup, "lookahead_violations": lookahead,
            "wrong_reward_risk": bad_rr, "zero_risk_signals": zero_risk,
            "wrong_direction": wrong_dir, "k_out_of_band": bad_k, "risk_not_k_times_host": bad_risk,
            "k_mean": round(float(np.mean(ks)), 4) if ks else None,
            "k_median": round(float(np.median(ks)), 4) if ks else None,
            "k_at_clip": sum(1 for sg in signals if sg.market_context["k_clipped"]),
            "k_is_one_fallback": sum(1 for sg in signals if sg.market_context["or_width_ratio"] is None),
            "pass": dup == 0 and lookahead == 0 and bad_rr == 0 and zero_risk == 0
                    and wrong_dir == 0 and bad_k == 0 and bad_risk == 0}


def main():
    from data_loader import load_price_data
    df, syn = load_price_data(context="strategy_s005 (audit only)", apply_holdout=False)
    if syn:
        raise SystemExit("synthetic -- refusing")
    precompute(df)
    sigs = generate_signals(df, df)
    a = audit(sigs)
    days = len(set(df.index.date))
    print(json.dumps({"strategy": STRATEGY_NAME, "version": STRATEGY_VERSION,
                      "host": f"{HOST_ID} {HOST_VERSION}",
                      "sessions_on_disk": days, "audit": a,
                      "fire_rate": round(a["n_signals"] / days, 3) if days else None},
                     indent=2, default=str))


if __name__ == "__main__":
    main()
