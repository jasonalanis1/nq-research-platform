"""
market_behavior_discovery_scan_029.py
========================================

Scan 029. Draws Entry 18 (map anchor M14): option-dealer gamma regime,
tested within NQ and within ES (Baltussen, Da, Lammers, Martens 2021 JFE).
Mechanism doc written before this scan:
research/mechanisms/hedging-demand-gamma-regime-m14.md.

M14's claim is NOT "late-day continuation exists" (that is M13 / 2e). It
is that continuation is STRONGER in negative-gamma regimes than positive-
gamma regimes -- the regime is the conditioning variable, not the level.
M13's own draw (Scan 028, same cycle) tested the level and instrument
ordering; per Section 7's explicit instruction, a shared late-day-
continuation LEVEL must never be counted as evidence for both -- this scan
only ever tests the regime DIFFERENCE, never the bare level.

Proxy (Section 3, price-only, "the weak part", stated plainly): trailing
20-trading-day lag-1 autocorrelation of ES 30-minute RTH intraday returns
(13 bins, 09:30-16:00), pooled across the trailing window and flattened in
chronological order, lagged one day (day d's regime uses only days up to
d-1, no lookahead). Terciles frozen on Discovery. Regime is computed once
on ES (the SPX-options gamma pool) and applied to BOTH NQ and ES per
Section 8's instrument-choice gate ("ES carries the SIGNAL... NQ and ES
both express it").

Full Discovery range used for both instruments (2015-01-01 -> 2021-10-03)
-- M14 needs no RTY, so none of Scan 028's common-window restriction
applies here.

Frozen scope (doc Section 9), Discovery only:
  outcome (per instrument) = sign(r_day) * (close_16:00 - close_15:30) /
  ATR14, same construction as M13/Scan 028's outcome, r_day = 09:30-15:30
  return, computed independently per instrument on its own ATR14.
  regime = ES-derived proxy terciles (TOP = most positive ES intraday
  autocorrelation = most negative gamma; BOTTOM = most negative
  autocorrelation = most positive gamma), same calendar days applied to
  both instruments.
  P1 GATING: TOP-regime outcome credibly LARGER than BOTTOM-regime outcome,
  tested as the DIFFERENCE with its own block-bootstrap CI, per instrument.
  P2 (reported): effect exists with same sign in both NQ and ES; does NOT
  order by instrument (unlike M13); next-session reversal larger after
  negative-gamma-regime (TOP) closes.

EIGHT pre-registered cells (scan_029_2026-09-13):
  Per instrument (NQ, ES), 3 regime cells (TOP/MID/BOTTOM) = 6.
  Per instrument, 1 gating difference (TOP-BOTTOM diff, block bootstrap) = 2.
  6 + 2 = 8 registered cells, matching the doc's own Section 9 count
  exactly. Next-session reversal and the realized-volatility falsifier (b)
  control are diagnostics reported alongside, not separately registered --
  falsifier (b) in particular is a Statistical/Director-stage follow-up
  (a realized-vol-tercile control regression), not a Discovery-stage cell;
  this scan reports the raw regime difference only, as scoped.

Per doc's own explicit instruction: "Do not scan NQ-with-NQ-proxy first"
-- the regime is computed from ES for both instruments in a single pass;
NQ's own result is never inspected using a regime built from NQ itself.

Overlap discipline (Section 7): if this scan's TOP-BOTTOM diff passes for
an instrument, that is NOT double-counted with Scan 028/M13's own TOP-vs-
NULL1 level test (which already failed for all three instruments) -- they
are structurally different tests (regime difference vs. level) and this
scan's own verdict stands on its own regime-difference evidence only.

One shot. No new cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_029.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
from baseline_relative import _block_means  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ATR_WINDOW = 14
BLOCK = 10
N_BOOT = 3000
SEED = 20260913
REGIME_LOOKBACK_DAYS = 20
INSTRUMENTS = ["NQ", "ES"]


def block_ci(v, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < BLOCK * 3:
        return [float("nan"), float("nan")]
    means = _block_means(v, BLOCK, N_BOOT, np.random.default_rng(SEED))
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


def cell(v):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    ci = block_ci(v)
    cred = (ci[0] > 0) or (ci[1] < 0)
    direction = "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")
    return {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": ci,
            "credible_vs_zero": bool(cred), "direction": direction}


def diff_ci(a, b, alpha=0.10, seed_offset=1):
    a = np.asarray([x for x in a if not np.isnan(x)], float)
    b = np.asarray([x for x in b if not np.isnan(x)], float)
    if len(a) < BLOCK * 3 or len(b) < BLOCK * 3:
        return {"mean_diff": float("nan"), "ci_90": [float("nan"), float("nan")],
                "credible_positive": False, "credible_negative": False}
    rng_a = np.random.default_rng(SEED)
    rng_b = np.random.default_rng(SEED + seed_offset)
    ma = _block_means(a, BLOCK, N_BOOT, rng_a)
    mb = _block_means(b, BLOCK, N_BOOT, rng_b)
    d = ma - mb
    ci = [float(np.percentile(d, 100 * alpha / 2)), float(np.percentile(d, 100 * (1 - alpha / 2)))]
    return {"mean_diff": float(a.mean() - b.mean()), "ci_90": ci,
            "credible_positive": bool(ci[0] > 0), "credible_negative": bool(ci[1] < 0)}


def build_daily(symbol: str) -> pd.DataFrame:
    """Full-Discovery daily RTH rows for one instrument: open (09:30),
    close_1530 (last bar at/before 15:30), close (16:00 close), high/low
    for ATR, r_day, sign-adjusted close-window outcome, next-session
    reversal. Mirrors Scan 028's build_daily exactly (same construction),
    just without the common-window restriction (not needed -- M14 uses
    no RTY)."""
    raw, synth = load_price_data(context="market_behavior_discovery_scan_029.py", symbol=symbol)
    if synth:
        raise RuntimeError(f"ABORT: synthetic data for {symbol}.")
    disc = get_discovery_data(raw)

    rows = []
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue
        b0930 = rth.between_time("09:30", "09:30")
        pre1530 = rth.between_time("09:30", "15:30", inclusive="both")
        if b0930.empty or pre1530.empty or len(rth) < 200:
            continue
        close_1530 = float(pre1530["Close"].iloc[-1])
        rows.append({
            "date": pd.Timestamp(day),
            "rth_open": float(rth["Open"].iloc[0]),
            "close_1530": close_1530,
            "rth_close": float(rth["Close"].iloc[-1]),
            "rth_high": float(rth["High"].max()),
            "rth_low": float(rth["Low"].min()),
        })
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["rth_range"] = d["rth_high"] - d["rth_low"]
    d["r_day"] = d["close_1530"] - d["rth_open"]
    d["atr14"] = d["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    d["close_window_ret"] = d["rth_close"] - d["close_1530"]
    d["sign_adj_close"] = np.sign(d["r_day"]) * (d["close_window_ret"] / d["atr14"])
    d["next_session_ret_atr"] = np.sign(d["r_day"]) * ((d["rth_close"] - d["rth_open"]) / d["atr14"]).shift(-1)
    return d, disc


def build_es_regime(es_disc: pd.DataFrame) -> pd.Series:
    """Trailing 20-day lag-1 autocorrelation of ES 30-min RTH intraday
    returns, pooled and flattened in chronological order across the
    trailing window, lagged one day (uses only data through d-1 for day
    d's regime value)."""
    bin_rows = []
    for day, g in es_disc.groupby(es_disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty or len(rth) < 200:
            continue
        bins = rth.resample("30min", origin="start_day", offset="9h30min").agg(
            {"Open": "first", "Close": "last"})
        bins = bins.dropna()
        if len(bins) < 10:
            continue
        rets = (bins["Close"] - bins["Open"]).to_numpy()
        bin_rows.append((pd.Timestamp(day), rets))

    bin_rows.sort(key=lambda t: t[0])
    dates = [t[0] for t in bin_rows]
    regime_vals = {}
    for i in range(REGIME_LOOKBACK_DAYS, len(bin_rows)):
        window = bin_rows[i - REGIME_LOOKBACK_DAYS:i]  # trailing 20 days, up to but NOT including day i (lag 1)
        pooled = np.concatenate([w[1] for w in window])
        if len(pooled) < 30:
            continue
        x0 = pooled[:-1]
        x1 = pooled[1:]
        if x0.std() == 0 or x1.std() == 0:
            continue
        ac = float(np.corrcoef(x0, x1)[0, 1])
        regime_vals[dates[i]] = ac
    return pd.Series(regime_vals, name="es_autocorr_proxy").sort_index()


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 029 (Entry 18 / M14: option-dealer gamma regime, NQ & ES)")
    print("=" * 78)
    print("Regime built from ES 30-min intraday autocorrelation, applied to both NQ and ES.")
    print("Per doc instruction: do not scan NQ-with-NQ-proxy first.\n")

    daily = {}
    disc_raw = {}
    for sym in INSTRUMENTS:
        d, disc = build_daily(sym)
        daily[sym] = d
        disc_raw[sym] = disc
        print(f"{sym}: usable sessions={len(d)}")

    regime = build_es_regime(disc_raw["ES"])
    print(f"ES-derived regime proxy computed for {len(regime)} days (trailing {REGIME_LOOKBACK_DAYS}-day lag-1 autocorr, lagged 1 day, no lookahead)")

    lo_r, hi_r = regime.quantile([1 / 3, 2 / 3])
    tercile = pd.Series(np.where(regime >= hi_r, "TOP", np.where(regime < lo_r, "BOTTOM", "MID")), index=regime.index)
    print(f"Regime terciles (Discovery-frozen): lo={lo_r:.5f} hi={hi_r:.5f}")

    per_instrument = {}
    for sym in INSTRUMENTS:
        base = daily[sym].dropna(subset=["r_day", "sign_adj_close", "atr14"]).copy()
        base = base.join(tercile.rename("regime"), how="inner")

        top = base[base["regime"] == "TOP"]
        mid = base[base["regime"] == "MID"]
        bot = base[base["regime"] == "BOTTOM"]

        r = {}
        r["top"] = cell(top["sign_adj_close"])
        r["mid"] = cell(mid["sign_adj_close"])
        r["bottom"] = cell(bot["sign_adj_close"])
        r["p1_gate_top_minus_bottom"] = diff_ci(top["sign_adj_close"], bot["sign_adj_close"], seed_offset=1)
        r["top_next_session_reversal"] = cell(top["next_session_ret_atr"])
        r["bottom_next_session_reversal"] = cell(bot["next_session_ret_atr"])

        per_instrument[sym] = {"n_used": int(len(base)), "results": r}
        print(f"{sym}: n_used={len(base)} TOP={len(top)} MID={len(mid)} BOTTOM={len(bot)}")

    # kill check per instrument: share of TOP-BOTTOM diff response in the final 15:59-16:00 bar
    for sym in INSTRUMENTS:
        base = daily[sym].dropna(subset=["r_day", "sign_adj_close", "atr14"]).copy()
        base = base.join(tercile.rename("regime"), how="inner")
        top_dates = set(base[base["regime"] == "TOP"].index)
        bot_dates = set(base[base["regime"] == "BOTTOM"].index)
        atr_by_date = base["atr14"].to_dict()
        sign_by_date = np.sign(base["r_day"]).to_dict()

        def last_min_vals(dates):
            rows = []
            for day, g in disc_raw[sym].groupby(disc_raw[sym].index.date):
                ts = pd.Timestamp(day)
                if ts not in dates:
                    continue
                b = g.between_time("15:59", "15:59")
                if b.empty:
                    continue
                atr = atr_by_date.get(ts); sgn = sign_by_date.get(ts)
                if atr is None or sgn is None or not np.isfinite(atr) or atr == 0:
                    continue
                rows.append(sgn * float(b["Close"].iloc[-1] - b["Open"].iloc[0]) / atr)
            return rows

        top_last = last_min_vals(top_dates)
        bot_last = last_min_vals(bot_dates)
        last_min_diff = (float(np.mean(top_last)) if top_last else float("nan")) - (float(np.mean(bot_last)) if bot_last else float("nan"))
        full_diff = per_instrument[sym]["results"]["p1_gate_top_minus_bottom"]["mean_diff"]
        share = float(last_min_diff / full_diff) if full_diff else float("nan")
        kill = bool(abs(share) > 0.5) if not np.isnan(share) else False
        per_instrument[sym]["results"]["kill_share_final_bar"] = {
            "n_top": len(top_last), "n_bottom": len(bot_last),
            "last_min_diff": last_min_diff, "share_of_full": share, "kill": kill}

    print("\nTOP-minus-BOTTOM regime difference, sign-adjusted close-window return (ATR units), block bootstrap 90% CI:")
    for sym in INSTRUMENTS:
        res = per_instrument[sym]["results"]
        g = res["p1_gate_top_minus_bottom"]; k = res["kill_share_final_bar"]
        print(f"  {sym:<4} diff={g['mean_diff']:+.4f} ci_90=({g['ci_90'][0]:+.4f},{g['ci_90'][1]:+.4f}) "
              f"credible_positive={g['credible_positive']} | kill_share={k['share_of_full']:+.3f} KILL={k['kill']}")

    p1_pass = {sym: per_instrument[sym]["results"]["p1_gate_top_minus_bottom"]["credible_positive"] for sym in INSTRUMENTS}
    killed = {sym: per_instrument[sym]["results"]["kill_share_final_bar"]["kill"] for sym in INSTRUMENTS}
    any_p1 = any(p1_pass.values())
    any_killed_where_passing = any(p1_pass[s] and killed[s] for s in INSTRUMENTS)

    print(f"\nP1 gate pass by instrument: {p1_pass}")

    if not any_p1:
        verdict = "P1_FAIL"
        note = ("Neither NQ nor ES shows a credibly larger sign-adjusted close-window response in the TOP "
                "(most-negative-gamma-proxy) regime than the BOTTOM regime. Falsifier (a) applies. Entry closes.")
    elif any_killed_where_passing:
        verdict = "KILLED"
        note = ("At least one instrument's TOP-BOTTOM regime difference is concentrated in the final "
                "15:59-16:00 bar (>50% of the full effect) -- an end-of-day print artifact, not a hedging-"
                "flow difference building in over the last 30 minutes. Family terminates per kill rule (c).")
    else:
        same_sign = np.sign(per_instrument["NQ"]["results"]["p1_gate_top_minus_bottom"]["mean_diff"]) == \
                    np.sign(per_instrument["ES"]["results"]["p1_gate_top_minus_bottom"]["mean_diff"])
        if all(p1_pass.values()) and same_sign:
            verdict = "P1_PASS_P2_PASS"
            note = ("TOP-BOTTOM regime difference credible in both NQ and ES with the same sign, as the "
                    "dealer-hedging mechanism predicts (does not order by instrument, unlike M13). Advance "
                    "to Statistical per pipeline order. Falsifier (b) (realized-volatility-tercile control) "
                    "is a Statistical/Director-stage follow-up, not yet run.")
        else:
            verdict = "P1_PASS_P2_FAIL"
            note = ("At least one instrument's regime difference is credible, but not both with the same "
                    f"sign (p1_pass={p1_pass}). Falsifier (b)-style ambiguity: recorded as-is; closes without "
                    "advancing given the mechanism's own P2 requirement (same-sign effect in both instruments) "
                    "is not met.")

    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {
        "regime_terciles": {"lo": float(lo_r), "hi": float(hi_r)},
        "regime_n_days": int(len(regime)),
        "per_instrument": per_instrument,
        "verdict": verdict,
        "note": note,
        "falsifier_b_note": "Realized-volatility-tercile control (falsifier b) not run in this Discovery-stage scan; deferred to Statistical/Director stage if P1 advances.",
    }
    (DATA_DIR / "market_behavior_discovery_scan_029_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_029_results.json'}")


if __name__ == "__main__":
    main()
