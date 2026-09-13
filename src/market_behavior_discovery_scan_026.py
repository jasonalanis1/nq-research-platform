"""
market_behavior_discovery_scan_026.py
========================================

Scan 026. Draws Entry 22 (map anchor M18): volume-conditioned daily
reversal (Campbell, Grossman & Wang 1993 QJE), NQ.
Mechanism doc written BEFORE this scan:
research/mechanisms/volume-conditioned-daily-reversal-m18.md.

Frozen scope (doc Section 7), Discovery only:
  session = RTH 09:30-16:00.
  vol_ratio = RTH volume / trailing-20d mean RTH volume (lagged).
  terciles frozen on Discovery.
  outcome = next-session RTH return / ATR14, sign-adjusted by today's
  RTH return sign.
TEN pre-registered cells (scan_026_2026-09-13), 1 gating:
  1. HIGH-volume sign-adjusted next-day mean, block CI   <== GATING (P1)
  2. LOW-volume, same statistic                           (P2 comparison)
  3. MID-volume                                            (reported)
  4. HIGH minus LOW, bootstrap on the difference           (P2, reported)
  5. unconditional sign-adjusted next-day mean             (NULL 1)
  6-7. HIGH cell split by today's |ret|/ATR top tercile vs rest (P3, 2 cells)
  8-9. HIGH cell on Discovery halves                       (P4, 2 cells)
  10. share of HIGH-cell response in next session's first 1-min bar (KILL)
Block bootstrap (block=10) is the CI of record. Calendar days with only
Globex bars are not sessions and do not break the day-to-day chain (Scan
020 lesson) -- explicitly checked here since this scan chains consecutive
trading days.

One shot. No new cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_026.py
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
ATR_WINDOW = 14; VOL_WINDOW = 20; BLOCK = 10; N_BOOT = 3000; SEED = 20260913


def block_ci(v, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < BLOCK * 3:
        return [float("nan"), float("nan")]
    means = _block_means(v, BLOCK, N_BOOT, np.random.default_rng(SEED))
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


def cell(v, want_negative=False):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    ci = block_ci(v); cred = (ci[0] > 0) or (ci[1] < 0)
    direction = "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")
    out = {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": ci,
           "credible_vs_zero": bool(cred), "direction": direction}
    if want_negative:
        out["credible_negative"] = bool(cred and ci[1] < 0)
    return out


def diff_ci(a, b, alpha=0.10):
    """Block-bootstrap CI on the difference of two independent daily series (a - b),
    resampled separately (both are keyed on distinct calendar days, not paired)."""
    a = np.asarray([x for x in a if not np.isnan(x)], float)
    b = np.asarray([x for x in b if not np.isnan(x)], float)
    if len(a) < BLOCK * 3 or len(b) < BLOCK * 3:
        return {"mean_diff": float("nan"), "ci_90": [float("nan"), float("nan")], "credible_negative": False}
    rng = np.random.default_rng(SEED)
    ma = _block_means(a, BLOCK, N_BOOT, rng)
    mb = _block_means(b, BLOCK, N_BOOT, np.random.default_rng(SEED + 1))
    d = ma - mb
    ci = [float(np.percentile(d, 100 * alpha / 2)), float(np.percentile(d, 100 * (1 - alpha / 2)))]
    return {"mean_diff": float(a.mean() - b.mean()), "ci_90": ci, "credible_negative": bool(ci[1] < 0)}


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 026 (Entry 22 / M18: volume-conditioned daily reversal, NQ)"); print("=" * 78)
    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_026.py", symbol="NQ")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(nq_all)

    rows = []; dropped = 0
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue  # Globex-only calendar day -- not a session, does not break the chain
        b0930 = rth.between_time("09:30", "09:30")
        if b0930.empty or len(rth) < 200:
            dropped += 1
            continue  # a real but partial/roll-day session: unusable for either day t or t+1
        rows.append({
            "date": pd.Timestamp(day),
            "rth_open": float(rth["Open"].iloc[0]),
            "rth_close": float(rth["Close"].iloc[-1]),
            "rth_high": float(rth["High"].max()),
            "rth_low": float(rth["Low"].min()),
            "rth_volume": float(rth["Volume"].sum()),
        })
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["rth_range"] = d["rth_high"] - d["rth_low"]
    d["rth_ret"] = d["rth_close"] - d["rth_open"]
    d["atr14"] = d["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    d["vol_trail20"] = d["rth_volume"].rolling(VOL_WINDOW, min_periods=VOL_WINDOW).mean().shift(1)
    d["vol_ratio"] = d["rth_volume"] / d["vol_trail20"]
    print(f"Sessions usable: {len(d)}; dropped (missing 09:30 bar or partial RTH, not counting Globex-only non-sessions): {dropped}")

    d["ret_atr"] = d["rth_ret"] / d["atr14"]
    d["sign_adj_next"] = np.sign(d["rth_ret"]) * d["ret_atr"].shift(-1)
    d["abs_ret_atr"] = d["ret_atr"].abs()

    base = d.dropna(subset=["vol_ratio", "sign_adj_next", "ret_atr"]).copy()
    lo_v, hi_v = base["vol_ratio"].quantile([1 / 3, 2 / 3])
    base["vol_bucket"] = np.where(base["vol_ratio"] >= hi_v, "HIGH", np.where(base["vol_ratio"] < lo_v, "LOW", "MID"))
    print(f"n_used={len(base)}; vol_ratio terciles (Discovery-frozen): lo={lo_v:.4f} hi={hi_v:.4f}")

    high = base[base["vol_bucket"] == "HIGH"]
    low = base[base["vol_bucket"] == "LOW"]
    mid = base[base["vol_bucket"] == "MID"]

    results = {}
    results["cell1_high"] = cell(high["sign_adj_next"], want_negative=True)          # P1 GATING
    results["cell2_low"] = cell(low["sign_adj_next"])                                # P2 comparison
    results["cell3_mid"] = cell(mid["sign_adj_next"])                                # reported
    results["cell4_high_minus_low"] = diff_ci(high["sign_adj_next"], low["sign_adj_next"])  # P2
    results["cell5_unconditional"] = cell(base["sign_adj_next"])                     # NULL 1

    abs_hi = high["abs_ret_atr"].quantile(2 / 3)
    high_bigmove = high[high["abs_ret_atr"] >= abs_hi]
    high_smallmove = high[high["abs_ret_atr"] < abs_hi]
    results["cell6_high_bigmove"] = cell(high_bigmove["sign_adj_next"])              # P3
    results["cell7_high_smallmove"] = cell(high_smallmove["sign_adj_next"])          # P3

    half = len(high) // 2
    results["cell8_high_first_half"] = cell(high["sign_adj_next"].iloc[:half])       # P4
    results["cell9_high_second_half"] = cell(high["sign_adj_next"].iloc[half:])      # P4

    # kill rule: share of the next-session HIGH-cell response in its first 1-min bar
    fm_rows = []
    for day, g in disc.groupby(disc.index.date):
        b = g.between_time("09:30", "09:30")
        if not b.empty:
            fm_rows.append({"date": pd.Timestamp(day), "fm_ret": float(b["Close"].iloc[-1] - b["Open"].iloc[0])})
    fm = pd.DataFrame(fm_rows).set_index("date").sort_index().reindex(d.index)
    fm["fm_ret_next"] = fm["fm_ret"].shift(-1)
    j = base.join(fm[["fm_ret_next"]], how="left").dropna(subset=["fm_ret_next", "atr14"])
    j_high = j[j["vol_bucket"] == "HIGH"]
    sa_fm_high = np.sign(j_high["rth_ret"]) * (j_high["fm_ret_next"] / j_high["atr14"])
    full_mean = results["cell1_high"]["mean"]
    share = float(sa_fm_high.mean() / full_mean) if full_mean else float("nan")
    kill = {"n": int(len(j_high)), "first_min_mean": float(sa_fm_high.mean()), "share_of_full": share,
            "kill": bool(abs(share) > 0.5) if not np.isnan(share) else False}
    results["cell10_kill"] = kill

    print("\nHIGH / LOW / MID sign-adjusted next-session RTH return (ATR units, block bootstrap 90% CI):")
    for key, label, tag in [("cell1_high", "HIGH", " <== GATING"), ("cell2_low", "LOW", " (control)"), ("cell3_mid", "MID", " (control)")]:
        c = results[key]
        print(f"  {label:<5} n={c['n']:>4} mean={c['mean']:+.4f} ci_90=({c['ci_90'][0]:+.4f},{c['ci_90'][1]:+.4f}) {c['direction']}{tag}")
    print(f"  unconditional (NULL 1): n={results['cell5_unconditional']['n']} mean={results['cell5_unconditional']['mean']:+.4f}")
    dcl = results["cell4_high_minus_low"]
    print(f"  HIGH-LOW diff: mean={dcl['mean_diff']:+.4f} ci_90=({dcl['ci_90'][0]:+.4f},{dcl['ci_90'][1]:+.4f}) credible_negative={dcl['credible_negative']}")
    print(f"  P3 confound: HIGH+bigmove mean={results['cell6_high_bigmove']['mean']:+.4f}  HIGH+smallmove mean={results['cell7_high_smallmove']['mean']:+.4f}")
    print(f"  P4 halves: 1st={results['cell8_high_first_half']['mean']:+.4f} 2nd={results['cell9_high_second_half']['mean']:+.4f}")
    print(f"  kill: first_min_share={kill['share_of_full']:+.3f} KILL={kill['kill']}")

    p1_pass = results["cell1_high"]["credible_negative"]
    p2_pass = results["cell4_high_minus_low"]["credible_negative"]
    killed = kill["kill"] and p1_pass
    if not p1_pass:
        verdict, note = "P1_FAIL", "HIGH-volume sign-adjusted next-day return's 90% CI does not credibly clear zero on the negative side. Entry closes on falsifier (a)."
    elif killed:
        verdict, note = "KILLED", "The HIGH-volume next-session response is concentrated in its own first minute -- an overnight-gap artifact, not a reversal building in over the session. Family terminates per kill rule (c)."
    elif not p2_pass:
        verdict, note = "P1_PASS_P2_FAIL", "HIGH-volume cell reverses, but it is not credibly below the LOW-volume cell -- this is NQ's own daily reversal (or lack of it), volume adds nothing. Recorded per falsifier (b). Closes."
    else:
        bigmove_dir = results["cell6_high_bigmove"]["direction"]
        smallmove_dir = results["cell7_high_smallmove"]["direction"]
        if bigmove_dir == "negative" and smallmove_dir != "negative":
            confound_note = " P3: reversal concentrated in the large-move HIGH-volume cell -- confounded with the closed gap/level-fade family; recorded CONFOUNDED per Llorente et al."
            verdict = "P1_PASS_CONFOUNDED"
        else:
            confound_note = " P3: reversal not confined to the large-move cell -- mechanism confirmed in its own terms, not the informed-volume confound."
            verdict = "P1_PASS"
        note = f"HIGH-volume cell credibly reverses and is credibly below LOW-volume (P1+P2 pass).{confound_note} Advance to Statistical per pipeline order."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_used": int(len(base)), "dropped": int(dropped), "vol_terciles": {"lo": float(lo_v), "hi": float(hi_v)},
           "results": results, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_026_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_026_results.json'}")


if __name__ == "__main__":
    main()
