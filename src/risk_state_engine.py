"""
risk_state_engine.py -- BOT MILESTONE B2 (UPGRADE QUEUE v3 item U13).

WHAT THIS IS
  The project's validated volatility facts turned into ONE daily decision the bot
  can act on. It answers "how big, how far, and whether at all" for a session.
  It NEVER answers "which way". It makes NO profit claim. Its spec is
  research/infrastructure/upgrade-specs-2026-09-13.md (U13) and it is the first
  thing that gets paper-traded (decision D3, 2026-09-13), attached to a
  placeholder entry (B3) purely so the machine can be measured.

INPUTS (all known at the prior close / the 09:30 open -- nothing intraday)
  prior_day_narrow / prior_day_wide   hyp-000046/048  (Validation-confirmed)
  coiled_overnight                    hyp-000056/057  (Validation-confirmed)
  vxn_level_vs_trailing HIGH tercile  hyp-000142/144/151 (Holdout-passed)
  The midday->afternoon fact (hyp-000105/141) is INTRADAY-only (usable from
  14:00 ET) and is exposed as a separate afternoon update, never folded into the
  pre-open number -- same separation volatility_conditioning.py already enforces.

COMBINATION -- BY RESIDUAL, NOT PRODUCT
  The prior-day and overnight facts keep the product convention already frozen in
  volatility_conditioning.get_volatility_conditioning (their ratios were
  validated jointly there). The VXN fact is the most overlapping of the four:
  the 2026-09-13 Portfolio review found only 53-66% of its effect survives after
  controlling for the other two. So VXN contributes ONLY its residual share:
      vxn_factor = 1 + (VXN_HIGH_RATIO - 1) * VXN_RESIDUAL_RETENTION
  with retention fixed at the CONSERVATIVE end (0.53). Multiplying the raw 1.239
  on top of the other facts would double-count; that is exactly what the review
  warned against.

OUTPUTS, per session, frozen for the day
  expected_range_mult     multiplier on the trailing-20d average RTH range
  expected_range_atr      the same, expressed in ATR14 units (range_avg/ATR14 * mult)
  within_session_shape    descriptive share of session range by window, from the
                          2026-09-13 free-look (Discovery slice); descriptive only
  stop_distance_atr       STOP_FRACTION  * expected_range_atr   (0.5x, frozen)
  target_distance_atr     TARGET_FRACTION * expected_range_atr  (1.0x, frozen)
  size_multiplier         volatility_conditioning.position_size_multiplier(mult)
  trade_permission        FALSE on: bottom-decile expected range (frozen edge),
                          scheduled-event days (calendar file, if present),
                          stale data (latest bar older than STALE_SESSIONS)
  basis                   which facts fired and the frozen numbers used

FROZEN PARAMETERS
  Anything derived from data (the VXN HIGH tercile edge, the bottom-decile
  permission edge, the session-shape shares) is computed ONCE on the Discovery
  slice by `--freeze`, written to research/infrastructure/
  risk-state-engine-frozen-params.json (versioned in git), and read back on every
  run. The engine refuses to run without that file. Nothing is refit.

USAGE
  python3 src/risk_state_engine.py --freeze      # once; writes the frozen params
  python3 src/risk_state_engine.py               # decision for the latest session
  python3 src/risk_state_engine.py --date 2026-09-08
  python3 src/risk_state_engine.py --log         # append to the daily log (B7 feeder)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from production_paths import assert_writable, enable_production
from volatility_conditioning import (  # noqa: E402
    build_conditioning_frame, get_volatility_conditioning, position_size_multiplier,
    build_midday_afternoon_frame, get_afternoon_conditioning,
)

ENGINE_VERSION = "B2-1.0 (2026-09-13)"
PARAMS_PATH = ROOT.parent / "research" / "infrastructure" / "risk-state-engine-frozen-params.json"
LOG_PATH = ROOT.parent / "research" / "forward_validation" / "risk_state_engine_log.jsonl"
EVENT_CALENDAR = ROOT.parent / "research" / "calendars" / "event_days.csv"   # optional: one ISO date per line

# --- frozen constants (no data needed) ---
VXN_HIGH_RATIO = 1.2389            # hyp-000151 Holdout HIGH ratio (Sidak-adjusted CI [1.154,1.324] > 1)
VXN_RESIDUAL_RETENTION = 0.53      # conservative end of the 53-66% Portfolio-review range
STOP_FRACTION = 0.5                # stop  = 0.5 x expected range (frozen before any paper trade)
TARGET_FRACTION = 1.0              # target = 1.0 x expected range
RANGE_LOOKBACK = 20                # trailing-average RTH range the multipliers apply to
ATR_WINDOW = 14
STALE_SESSIONS = 3                 # permission FALSE if the latest bar is older than this many sessions
PERMISSION_DECILE = 10             # bottom decile of expected_range_mult on Discovery -> no trade
SESSION_WINDOWS = ["first30", "morning", "midday", "afternoon", "last_hour"]


# ----------------------------------------------------------------------------
# frozen-parameter management
# ----------------------------------------------------------------------------
def _discovery_frame():
    from data_loader import load_price_data
    from data_split import get_discovery_data
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame
    df, synthetic = load_price_data(context="risk_state_engine")
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    disc = get_discovery_data(df)
    states = extend_state_frame(build_state_frame(disc), disc)
    return df, disc, states


def freeze_params() -> dict:
    """Compute every data-derived constant ONCE on the Discovery slice."""
    _, disc, states = _discovery_frame()
    cond = build_conditioning_frame(disc)
    vxn = states["vxn_level_vs_trailing"].replace([np.inf, -np.inf], np.nan).dropna()
    vxn_high_edge = float(np.nanpercentile(vxn, 200 / 3))

    # distribution of the combined multiplier over Discovery -> bottom-decile edge
    idx = pd.to_datetime(pd.Index(states.index))
    vxn_by_day = pd.Series(states["vxn_level_vs_trailing"].to_numpy(dtype=float), index=idx)
    mults = []
    for d in cond.index:
        base = get_volatility_conditioning(d, cond)["expected_range_multiplier"]
        v = vxn_by_day.get(pd.Timestamp(d), np.nan)
        mults.append(_combine(base, bool(np.isfinite(v) and v >= vxn_high_edge)))
    permission_edge = float(np.nanpercentile(np.asarray(mults), PERMISSION_DECILE))

    # descriptive within-session shape from the 2026-09-13 idea-factory / free-look run
    shape = {}
    for name in ("idea_factory_2026-09-13.json", "observatory_free_look_2026-09-13.json"):
        p = ROOT.parent / "data" / name
        if p.exists():
            rows = json.loads(p.read_text()).get("rows", [])
            allm = {r["window"]: r.get("all_mean", r.get("all_days_mean")) for r in rows if r.get("outcome") == "range"}
            if "rth" in allm and allm["rth"]:
                shape = {w: round(allm[w] / allm["rth"], 3) for w in SESSION_WINDOWS if w in allm}
            elif allm:
                tot = sum(allm.get(w, 0) for w in SESSION_WINDOWS)
                shape = {w: round(allm[w] / tot, 3) for w in SESSION_WINDOWS if w in allm and tot}
            if shape:
                break

    params = {
        "engine_version": ENGINE_VERSION,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "discovery_slice": f"{cond.index[0]}..{cond.index[-1]}",
        "vxn_high_tercile_edge": vxn_high_edge,
        "permission_bottom_decile_edge": permission_edge,
        "within_session_shape": shape,
        "constants": {"VXN_HIGH_RATIO": VXN_HIGH_RATIO, "VXN_RESIDUAL_RETENTION": VXN_RESIDUAL_RETENTION,
                      "STOP_FRACTION": STOP_FRACTION, "TARGET_FRACTION": TARGET_FRACTION,
                      "RANGE_LOOKBACK": RANGE_LOOKBACK, "ATR_WINDOW": ATR_WINDOW,
                      "STALE_SESSIONS": STALE_SESSIONS, "PERMISSION_DECILE": PERMISSION_DECILE},
        "note": "computed once on the Discovery slice; never refit; no P&L claim anywhere in this engine",
    }
    PARAMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    assert_writable(PARAMS_PATH, "frozen risk/state params")
    PARAMS_PATH.write_text(json.dumps(params, indent=2))
    return params


def load_params() -> dict:
    if not PARAMS_PATH.exists():
        raise SystemExit(f"frozen params missing: run `python3 src/risk_state_engine.py --freeze` first ({PARAMS_PATH})")
    return json.loads(PARAMS_PATH.read_text())


# ----------------------------------------------------------------------------
# pure decision logic (unit-testable without data)
# ----------------------------------------------------------------------------
def _combine(base_multiplier: float, vxn_high: bool) -> float:
    """Residual combination: base (product convention, already validated jointly)
    times VXN's residual share only."""
    vxn_factor = 1.0 + (VXN_HIGH_RATIO - 1.0) * VXN_RESIDUAL_RETENTION if vxn_high else 1.0
    return round(float(base_multiplier) * vxn_factor, 4)


def decide(base_multiplier: float, vxn_high: bool, range_avg_points: float, atr14_points: float,
           permission_edge: float, is_event_day: bool, stale: bool, shape: dict | None = None,
           basis: list | None = None) -> dict:
    """The whole decision, given already-looked-up inputs. No data access here."""
    mult = _combine(base_multiplier, vxn_high)
    if atr14_points and atr14_points > 0 and range_avg_points and range_avg_points > 0:
        exp_atr = round(float(range_avg_points) / float(atr14_points) * mult, 4)
    else:
        exp_atr = float("nan")
    reasons = []
    if not np.isfinite(exp_atr):
        reasons.append("no usable range/ATR")
    if mult <= permission_edge:
        reasons.append(f"expected range in bottom decile (mult {mult} <= {permission_edge:.4f})")
    if is_event_day:
        reasons.append("scheduled-event day")
    if stale:
        reasons.append(f"data stale (> {STALE_SESSIONS} sessions)")
    return {
        "engine_version": ENGINE_VERSION,
        "expected_range_mult": mult,
        "expected_range_atr": exp_atr,
        "stop_distance_atr": round(STOP_FRACTION * exp_atr, 4) if np.isfinite(exp_atr) else float("nan"),
        "target_distance_atr": round(TARGET_FRACTION * exp_atr, 4) if np.isfinite(exp_atr) else float("nan"),
        "size_multiplier": position_size_multiplier(mult),
        "trade_permission": len(reasons) == 0,
        "permission_reasons": reasons,
        "within_session_shape": shape or {},
        "basis": (basis or []) + ([f"vxn HIGH tercile (hyp-000151, x{VXN_HIGH_RATIO} at {VXN_RESIDUAL_RETENTION} residual retention)"] if vxn_high else []),
        "direction": None,
        "pnl_claim": None,
    }


# ----------------------------------------------------------------------------
# data-backed decision for a session date
# ----------------------------------------------------------------------------
def _event_days() -> set:
    if not EVENT_CALENDAR.exists():
        return set()
    return {ln.strip() for ln in EVENT_CALENDAR.read_text().splitlines() if ln.strip() and not ln.startswith("#")}


def decision_for(date=None) -> dict:
    params = load_params()
    from data_loader import load_price_data
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame
    # The bot layer reads ALL data on disk. The Holdout boundary is a RESEARCH
    # rule (it protects unseen years from search); a live decision engine must
    # see the latest sessions or it is stale by construction. Found by the
    # 2026-09-13 7:00 pm test cycle: with the default loader the "latest
    # session" was April 6th. Nothing here searches, so nothing is contaminated.
    df, synthetic = load_price_data(context="risk_state_engine (live layer, holdout boundary not applied)", apply_holdout=False)
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    states = extend_state_frame(build_state_frame(df), df)
    cond = build_conditioning_frame(df)
    idx = pd.to_datetime(pd.Index(states.index))
    daily_range = pd.Series((states["High"] - states["Low"]).to_numpy(dtype=float), index=idx)
    range_avg = daily_range.rolling(RANGE_LOOKBACK, min_periods=RANGE_LOOKBACK).mean().shift(1)
    atr = pd.Series(states["atr14"].to_numpy(dtype=float), index=idx)
    vxn = pd.Series(states["vxn_level_vs_trailing"].to_numpy(dtype=float), index=idx)

    if date is None:
        d = idx[-1]
    else:
        d = pd.Timestamp(date)
        if d not in idx:
            raise SystemExit(f"{date} is not a session in the data on disk")
    d_date = d.date()
    base = get_volatility_conditioning(d_date, cond)
    v = vxn.get(d, np.nan)
    vxn_high = bool(np.isfinite(v) and v >= params["vxn_high_tercile_edge"])
    last_bar = df.index[-1]
    stale = (date is None) and ((pd.Timestamp.now(tz=last_bar.tz) - last_bar).days > STALE_SESSIONS * 1.6)
    out = decide(base["expected_range_multiplier"], vxn_high, float(range_avg.get(d, np.nan)), float(atr.get(d, np.nan)),
                 params["permission_bottom_decile_edge"], d.strftime("%Y-%m-%d") in _event_days(), bool(stale),
                 params.get("within_session_shape", {}), base.get("basis", []))
    out.update({"session": d.strftime("%Y-%m-%d"), "computed_at": datetime.now(timezone.utc).isoformat(),
                "inputs": {"prior_day_narrow": base["narrow_prior_day"], "prior_day_wide": base["wide_prior_day"],
                           "coiled_overnight": base["coiled_overnight"], "vxn_level_vs_trailing": None if not np.isfinite(v) else round(float(v), 4),
                           "vxn_high": vxn_high, "range_avg_points": None if not np.isfinite(range_avg.get(d, np.nan)) else round(float(range_avg.get(d)), 2),
                           "atr14_points": None if not np.isfinite(atr.get(d, np.nan)) else round(float(atr.get(d)), 2),
                           "last_bar": str(last_bar)}})
    # afternoon update, intraday-only, kept separate on purpose
    out["afternoon_update"] = {"usable_from": "14:00 ET", "note": "midday->afternoon fact (hyp-000105/141) applies intraday only; call get_afternoon_conditioning() after 14:00 ET, never folded into the pre-open number"}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--date", default=None)
    ap.add_argument("--log", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        p = freeze_params()
        print(json.dumps({k: p[k] for k in ("engine_version", "discovery_slice", "vxn_high_tercile_edge", "permission_bottom_decile_edge", "within_session_shape")}, indent=2))
        return
    out = decision_for(a.date)
    print(json.dumps(out, indent=2, default=str))
    if a.log:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        assert_writable(LOG_PATH, "risk/state daily log")
        with LOG_PATH.open("a") as f:
            f.write(json.dumps(out, default=str) + "\n")
        print(f"logged -> {LOG_PATH}")


if __name__ == "__main__":
    enable_production()
    main()
