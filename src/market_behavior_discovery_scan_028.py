"""
market_behavior_discovery_scan_028.py
========================================

Scan 028. Draws Entry 17 (map anchor M13): LETF close-rebalance flow
(Cheng & Madhavan 2009), tested across RTY, ES, NQ as an instrument
factor. Mechanism doc written before this scan:
research/mechanisms/letf-close-rebalance-m13.md.

DATA-CEILING NOTE (disclosed, not silently absorbed): RTY futures
moved from ICE to CME (GLBX.MDP3) in mid-2017, so no earlier CME
history exists to buy. RTY data on disk starts 2017-07-09. To keep
the 3-instrument comparison apples-to-apples, ALL THREE instruments
are restricted to the common window 2017-07-09 -> DISCOVERY_END_DATE
(2021-10-03) in this scan, rather than NQ/ES's full ~6.75-year
Discovery history. This shortens the usable sample to ~4.25 years for
all three and is reported plainly below, not hidden in the output.

Frozen scope (doc Section 7), Discovery only, common window:
  session = RTH 09:30-16:00.
  r_day (gating variable) = 09:30-15:30 return (close_15:30 - open_09:30).
  outcome = sign(r_day) * (close_16:00 - close_15:30) / ATR14.
  terciles of |r_day| frozen per instrument on the common-window
  Discovery sample (each instrument has its own scale/vol regime).
  P1 GATING: TOP-tercile outcome is credibly positive vs NULL 1 (the
  instrument's own unconditional sign-adjusted close-window return),
  tested as a difference with its own block-bootstrap CI.
  P2 (reported, mechanism fingerprint): effect ORDERED RTY > ES >= NQ;
  larger in 2nd half of the common window than 1st half (LETF AUM grew
  several-fold 2015-2021); next-session sign-adjusted reversal.

FIFTEEN pre-registered cells (scan_028_2026-09-13):
  Per instrument (RTY, ES, NQ), 3 tercile cells (TOP/MID/BOTTOM) = 9.
  Per instrument, 2 reported cells (1st-half vs 2nd-half TOP-tercile
  split; next-session sign-adjusted open-to-close reversal on the
  TOP-tercile subset) = 6.
  9 + 6 = 15 registered cells. The P1 gate is the TOP-tercile cell's
  diff-vs-NULL1 test, run once per instrument (3 gate tests inside the
  9). The kill-rule check (share of TOP-tercile close-window response
  living in the final 15:59-16:00 bar) is computed per instrument as a
  standard diagnostic, same convention as Scan 026's cell10, and is
  NOT counted against the 15 registered cells (Scan 026 counted its
  kill check as a registered cell; this scan's own doc explicitly
  totals 9+6=15 with no separate kill-cell line item, so the kill
  check here is reported but not separately registered, to match the
  doc's own accounting exactly).

Per doc's own explicit instruction: "Do NOT run NQ alone first: that
would spend the family's one shot on the instrument where the
mechanism predicts the WEAKEST effect." All three instruments are
computed together below in a single pass; no instrument's result is
inspected or reported before the others are computed.

LABELING NOTE: the mechanism doc's falsifier (b) cites "queue item 2b"
as the generic intraday-momentum comparator/confound. Other entries'
own self-labeling suggests this citation should likely read "2e" (M16,
already closed: Scan 021 / hyp-000146, clean null, no promotion). This
scan does not alter the frozen doc's wording -- it is flagged here
plainly and M16's already-closed clean null is used as the relevant
corroborating context regardless of which label is correct.

One shot. No new cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_028.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data, DISCOVERY_END_DATE  # noqa: E402
from baseline_relative import _block_means  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ATR_WINDOW = 14
BLOCK = 10
N_BOOT = 3000
SEED = 20260913

COMMON_START = pd.Timestamp("2017-07-09", tz="America/New_York")
COMMON_END = DISCOVERY_END_DATE
INSTRUMENTS = ["RTY", "ES", "NQ"]


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
    """Block-bootstrap CI on the difference of two series (a - b), resampled
    independently (not paired -- a is a subset of the same day-index as b in
    some calls here, but we treat them as independent series per the same
    convention Scan 026 used for HIGH-vs-LOW)."""
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
    """Load one instrument, restrict to the common window, build daily RTH
    rows: open (09:30), close_1530 (last bar at/before 15:30), close (16:00
    close), high/low for ATR, plus the 09:30 first-minute bar for the kill
    check and the next-session RTH return for the reversal cell."""
    raw, synth = load_price_data(context="market_behavior_discovery_scan_028.py", symbol=symbol)
    if synth:
        raise RuntimeError(f"ABORT: synthetic data for {symbol}.")
    disc = get_discovery_data(raw)
    disc = disc[(disc.index.normalize() >= COMMON_START) & (disc.index <= COMMON_END)]

    rows = []
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue  # Globex-only calendar day, not a session
        b0930 = rth.between_time("09:30", "09:30")
        pre1530 = rth.between_time("09:30", "15:30", inclusive="both")
        if b0930.empty or pre1530.empty or len(rth) < 200:
            continue  # partial/roll-day session, unusable
        close_1530 = float(pre1530["Close"].iloc[-1])
        rows.append({
            "date": pd.Timestamp(day),
            "rth_open": float(rth["Open"].iloc[0]),
            "close_1530": close_1530,
            "rth_close": float(rth["Close"].iloc[-1]),
            "rth_high": float(rth["High"].max()),
            "rth_low": float(rth["Low"].min()),
            "fm_ret": float(b0930["Close"].iloc[-1] - b0930["Open"].iloc[0]),
        })
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["rth_range"] = d["rth_high"] - d["rth_low"]
    d["r_day"] = d["close_1530"] - d["rth_open"]  # 09:30-15:30 return, the gating variable
    d["atr14"] = d["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    d["close_window_ret"] = d["rth_close"] - d["close_1530"]  # 15:30-16:00 move
    d["sign_adj_close"] = np.sign(d["r_day"]) * (d["close_window_ret"] / d["atr14"])
    d["abs_r_day"] = d["r_day"].abs()
    # next-session sign-adjusted RTH open-to-close return, for the reversal cell
    d["next_session_ret_atr"] = np.sign(d["r_day"]) * ((d["rth_close"] - d["rth_open"]) / d["atr14"]).shift(-1)
    return d


def instrument_block(symbol: str, d: pd.DataFrame) -> dict:
    base = d.dropna(subset=["r_day", "sign_adj_close", "atr14"]).copy()
    lo_r, hi_r = base["abs_r_day"].quantile([1 / 3, 2 / 3])
    base["tercile"] = np.where(base["abs_r_day"] >= hi_r, "TOP",
                        np.where(base["abs_r_day"] < lo_r, "BOTTOM", "MID"))

    top = base[base["tercile"] == "TOP"]
    mid = base[base["tercile"] == "MID"]
    bot = base[base["tercile"] == "BOTTOM"]

    r = {}
    r["top"] = cell(top["sign_adj_close"])
    r["mid"] = cell(mid["sign_adj_close"])
    r["bottom"] = cell(bot["sign_adj_close"])
    r["unconditional_null1"] = cell(base["sign_adj_close"])
    r["p1_gate_top_vs_null1"] = diff_ci(top["sign_adj_close"], base["sign_adj_close"], seed_offset=1)

    half = len(top) // 2
    r["top_first_half"] = cell(top["sign_adj_close"].iloc[:half])
    r["top_second_half"] = cell(top["sign_adj_close"].iloc[half:])

    r["top_next_session_reversal"] = cell(top["next_session_ret_atr"])

    # kill check: share of TOP-tercile close-window response in the final
    # 1-min bar (15:59-16:00) -- approximated here as the share attributable
    # to the day's own 09:30 first-minute bar is NOT what falsifier (c) asks;
    # falsifier (c) is about the 15:59-16:00 bar specifically. We do not have
    # a per-day 15:59 bar column built above, so compute it directly here.
    kill_n = int(len(top))
    top_full_mean = r["top"]["mean"]
    r["kill_share_final_bar"] = {"note": "computed in main() with direct 15:59-16:00 bar extraction",
                                  "n": kill_n}

    return {"n_used": int(len(base)), "tercile_bounds": {"lo": float(lo_r), "hi": float(hi_r)}, "results": r}


def kill_check(symbol: str, disc_common: pd.DataFrame, base_top_dates, atr_by_date, sign_by_date) -> dict:
    """Share of the TOP-tercile close-window response concentrated in the
    final 15:59-16:00 minute bar, per falsifier (c)."""
    rows = []
    for day, g in disc_common.groupby(disc_common.index.date):
        ts = pd.Timestamp(day)
        if ts not in base_top_dates:
            continue
        b = g.between_time("15:59", "15:59")
        if b.empty:
            continue
        atr = atr_by_date.get(ts)
        sgn = sign_by_date.get(ts)
        if atr is None or sgn is None or not np.isfinite(atr) or atr == 0:
            continue
        last_min_ret = float(b["Close"].iloc[-1] - b["Open"].iloc[0])
        rows.append(sgn * last_min_ret / atr)
    if not rows:
        return {"n": 0, "first_min_mean": float("nan"), "share_of_full": float("nan"), "kill": False}
    arr = np.asarray(rows, float)
    return {"n": int(len(arr)), "last_min_mean": float(arr.mean())}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 028 (Entry 17 / M13: LETF close-rebalance, RTY/ES/NQ)")
    print("=" * 78)
    print(f"Common window (RTY-constrained, disclosed): {COMMON_START.date()} -> {COMMON_END.date()}")
    print("Running all three instruments together per doc instruction (do not run NQ alone first).\n")

    per_instrument = {}
    daily = {}
    for sym in INSTRUMENTS:
        d = build_daily(sym)
        daily[sym] = d
        per_instrument[sym] = instrument_block(sym, d)
        n = per_instrument[sym]["n_used"]
        print(f"{sym}: n_used={n}")

    # kill checks, direct 15:59-16:00 extraction per instrument
    for sym in INSTRUMENTS:
        d = daily[sym]
        base = d.dropna(subset=["r_day", "sign_adj_close", "atr14"]).copy()
        lo_r, hi_r = base["abs_r_day"].quantile([1 / 3, 2 / 3])
        top = base[base["abs_r_day"] >= hi_r]
        raw, _ = load_price_data(context="market_behavior_discovery_scan_028.py:kill", symbol=sym)
        disc_common = get_discovery_data(raw)
        disc_common = disc_common[(disc_common.index.normalize() >= COMMON_START) & (disc_common.index <= COMMON_END)]
        atr_by_date = top["atr14"].to_dict()
        sign_by_date = np.sign(top["r_day"]).to_dict()
        kc = kill_check(sym, disc_common, set(top.index), atr_by_date, sign_by_date)
        full_mean = per_instrument[sym]["results"]["top"]["mean"]
        share = float(kc["last_min_mean"] / full_mean) if kc.get("n", 0) and full_mean else float("nan")
        kc["share_of_full"] = share
        kc["kill"] = bool(abs(share) > 0.5) if not np.isnan(share) else False
        per_instrument[sym]["results"]["kill_share_final_bar"] = kc

    print("\nTOP-tercile sign-adjusted close-window return (ATR units), P1 gate = diff vs NULL1 (unconditional):")
    for sym in INSTRUMENTS:
        res = per_instrument[sym]["results"]
        t = res["top"]; g = res["p1_gate_top_vs_null1"]; k = res["kill_share_final_bar"]
        print(f"  {sym:<4} TOP n={t['n']:>4} mean={t['mean']:+.4f} ci_90=({t['ci_90'][0]:+.4f},{t['ci_90'][1]:+.4f}) "
              f"| vs NULL1 diff={g['mean_diff']:+.4f} ci_90=({g['ci_90'][0]:+.4f},{g['ci_90'][1]:+.4f}) credible_positive={g['credible_positive']} "
              f"| kill_share={k.get('share_of_full', float('nan')):+.3f} KILL={k.get('kill', False)}")

    p1_pass = {sym: per_instrument[sym]["results"]["p1_gate_top_vs_null1"]["credible_positive"] for sym in INSTRUMENTS}
    any_p1 = any(p1_pass.values())
    killed = {sym: per_instrument[sym]["results"]["kill_share_final_bar"].get("kill", False) for sym in INSTRUMENTS}
    any_killed_where_passing = any(p1_pass[s] and killed[s] for s in INSTRUMENTS)

    print(f"\nP1 gate pass by instrument: {p1_pass}")

    if not any_p1:
        verdict = "P1_FAIL"
        note = ("No instrument's TOP-tercile sign-adjusted close-window return is credibly positive vs its own "
                "unconditional (NULL 1). Falsifier (a) applies for all three instruments. Entry closes.")
    elif any_killed_where_passing:
        verdict = "KILLED"
        note = ("At least one instrument that passed P1 has its close-window response concentrated in the final "
                "15:59-16:00 bar (>50% of the full effect) -- an end-of-day print/marking artifact, not a rebalance "
                "flow building in over the last 30 minutes. Family terminates per kill rule (c).")
    else:
        means = {sym: per_instrument[sym]["results"]["top"]["mean"] for sym in INSTRUMENTS}
        ordered = means["RTY"] > means["ES"] >= means["NQ"] if all(p1_pass.values()) else None
        h1 = {sym: per_instrument[sym]["results"]["top_first_half"]["mean"] for sym in INSTRUMENTS}
        h2 = {sym: per_instrument[sym]["results"]["top_second_half"]["mean"] for sym in INSTRUMENTS}
        growth_pattern = all(h2[s] > h1[s] for s in INSTRUMENTS if p1_pass[s])
        if all(p1_pass.values()) and ordered:
            verdict = "P1_PASS_P2_PASS"
            note = ("TOP-tercile effect credible in all three instruments, ordered RTY > ES >= NQ as the LETF-AUM "
                    "mechanism predicts. Advance to Statistical per pipeline order.")
        elif any_p1 and not (all(p1_pass.values()) and ordered):
            verdict = "P1_PASS_P2_FAIL"
            note = ("At least one instrument's TOP-tercile effect is credible, but the cross-instrument ordering "
                    "(RTY > ES >= NQ) required by falsifier (b) does not hold, or not all three instruments are "
                    "credible. This is consistent with generic intraday continuation rather than the AUM-scaled "
                    "LETF-rebalance mechanism specifically -- recorded per falsifier (b). See labeling note above "
                    "re: M16 (Scan 021, hyp-000146, already-closed clean null on generic intraday momentum) as the "
                    "relevant corroborating context. Closes.")
        else:
            verdict = "P1_PASS_AMBIGUOUS"
            note = "Mixed pattern not cleanly covered by the pre-registered falsifiers; recorded as-is for Director review."
        note += f" Growth-pattern (2nd half > 1st half, LETF AUM growth) holds for all P1-passing instruments: {growth_pattern}."

    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {
        "common_window": {"start": str(COMMON_START.date()), "end": str(COMMON_END.date())},
        "per_instrument": per_instrument,
        "verdict": verdict,
        "note": note,
        "labeling_note": "Doc falsifier (b) cites 'queue item 2b'; likely should read '2e' (M16, Scan 021, hyp-000146, already-closed clean null). Not altered in the frozen doc; flagged here.",
    }
    (DATA_DIR / "market_behavior_discovery_scan_028_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_028_results.json'}")


if __name__ == "__main__":
    main()
