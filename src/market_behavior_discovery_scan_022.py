"""
market_behavior_discovery_scan_022.py
========================================

Scan 022. Draws Entry 21 (map anchor M17): intraday periodicity, same
half-hour slot next day (Heston, Korajczyk & Sadka 2010 JF), NQ.
Mechanism doc written BEFORE this scan:
research/mechanisms/intraday-periodicity-same-slot-next-day-m17.md.

Frozen scope (doc Section 7), Discovery only:
  slots: OPEN 09:30-10:00, MIDDAY 12:00-12:30, CLOSE 15:30-16:00.
  slot_ret = close(last bar of slot) - open(first bar of slot), / ATR14.
  predictor = slot_ret on day t; outcome = slot_ret on day t+1,
  sign-adjusted by the predictor's sign.
SEVENTEEN pre-registered cells (scan_022_2026-09-12), 2 gating:
  1. OPEN slot sign-adjusted next-day mean, block CI      <== GATING (P1)
  2. CLOSE slot sign-adjusted next-day mean, block CI     <== GATING (P1)
  3. MIDDAY slot, same statistic                          (P2 control)
  4-5. OPEN / CLOSE unconditional slot means               (NULL 1)
  6-9. cells 1-2 on Discovery halves                       (P3, 4 cells)
  10-15. cells 1-2 split by day-t |slot ret|/ATR tercile   (P4, 6 cells)
  16-17. share of day-(t+1) response in its first 1-min bar (KILL, 2 cells)
Block bootstrap (block=10) is the CI of record. Calendar days with only
Globex bars are not sessions and do not break the day-to-day chain (Scan
020 lesson) -- explicitly checked here since this scan chains consecutive
trading days.

One shot. No new cells, no retuning.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_022.py
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
ATR_WINDOW = 14; BLOCK = 10; N_BOOT = 3000; SEED = 20260912
SLOTS = {"OPEN": ("09:30", "09:59"), "MIDDAY": ("12:00", "12:29"), "CLOSE": ("15:30", "15:59")}


def block_ci(v, alpha=0.10):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    if len(v) < BLOCK * 3:
        return [float("nan"), float("nan")]
    means = _block_means(v, BLOCK, N_BOOT, np.random.default_rng(SEED))
    return [float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))]


def cell(v):
    v = np.asarray([x for x in v if not np.isnan(x)], float)
    ci = block_ci(v); cred = (ci[0] > 0) or (ci[1] < 0)
    return {"n": int(len(v)), "mean": float(v.mean()) if len(v) else float("nan"), "ci_90": ci,
            "credible_vs_zero": bool(cred), "direction": "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")}


def slot_bounds(g, start, end):
    """First bar's Open and last bar's Close within [start,end] inclusive."""
    sub = g.between_time(start, end)
    if sub.empty:
        return None
    return float(sub["Open"].iloc[0]), float(sub["Close"].iloc[-1])


def main():
    print("=" * 78); print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 022 (Entry 21 / M17: intraday periodicity, same slot next day)"); print("=" * 78)
    nq_all, synth = load_price_data(context="market_behavior_discovery_scan_022.py", symbol="NQ")
    if synth:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(nq_all)

    rows = []; dropped = 0
    for day, g in disc.groupby(disc.index.date):
        rth = g.between_time("09:30", "16:00", inclusive="left")
        if rth.empty:
            continue  # Globex-only calendar day (weekend/holiday evening) -- not a session
        b0930 = g.between_time("09:30", "09:30"); b1559 = g.between_time("15:59", "15:59")
        if b0930.empty or b1559.empty or len(rth) < 200:
            dropped += 1
            continue  # a real but partial/roll-day session: unusable for either day t or t+1
        row = {"date": pd.Timestamp(day), "rth_range": float(rth["High"].max() - rth["Low"].min())}
        for name, (s, e) in SLOTS.items():
            b = slot_bounds(g, s, e)
            row[f"{name}_ok"] = b is not None
            if b is not None:
                row[f"{name}_open"], row[f"{name}_close"] = b
        rows.append(row)
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["atr14"] = d["rth_range"].rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean().shift(1)
    print(f"Sessions usable: {len(d)}; dropped (missing 09:30/15:59 bar or partial RTH, not counting Globex-only non-sessions): {dropped}")

    for name in SLOTS:
        d[f"{name}_ret"] = np.where(d[f"{name}_ok"], (d[f"{name}_close"] - d[f"{name}_open"]) / d["atr14"], np.nan)

    # day t -> day t+1 is POSITIONAL on this already-consecutive-trading-day
    # index (Globex-only non-sessions were skipped above, not inserted as
    # NaN rows, so shift(1) here walks trading days, not calendar days).
    for name in SLOTS:
        d[f"{name}_ret_next"] = d[f"{name}_ret"].shift(-1)

    results = {}
    for name in ["OPEN", "CLOSE", "MIDDAY"]:
        pred = d[f"{name}_ret"]; nxt = d[f"{name}_ret_next"]
        sub = pd.concat([pred.rename("p"), nxt.rename("n"), d["atr14"].rename("atr")], axis=1).dropna()
        sa = np.sign(sub["p"]) * sub["n"]
        results[name] = {"sign_adj_next": cell(sa), "unconditional_next": cell(sub["n"]), "n_used": int(len(sub))}
        # dose split by |predictor| tercile
        abspred = sub["p"].abs()
        lo, hi = abspred.quantile([1 / 3, 2 / 3])
        top = sub[abspred >= hi]; bot = sub[abspred < lo]
        results[name]["dose_top_tercile"] = cell(np.sign(top["p"]) * top["n"])
        results[name]["dose_bottom_tercile"] = cell(np.sign(bot["p"]) * bot["n"])
        half = len(sub) // 2
        results[name]["first_half"] = cell(sa.iloc[:half])
        results[name]["second_half"] = cell(sa.iloc[half:])

    # kill rule: share of the next-day slot response in ITS first 1-min bar
    kill = {}
    for name, (s, e) in SLOTS.items():
        first_min = disc.between_time(s, s)  # the slot's opening minute bar
        # rebuild per-day first-minute sign-adjusted return, aligned the same way
        fm_rows = []
        for day, g in disc.groupby(disc.index.date):
            b = g.between_time(s, s)
            if not b.empty:
                fm_rows.append({"date": pd.Timestamp(day), "fm_ret": float(b["Close"].iloc[-1] - b["Open"].iloc[0])})
        fm = pd.DataFrame(fm_rows).set_index("date").sort_index()
        fm = fm.reindex(d.index)
        fm["fm_ret_next"] = fm["fm_ret"].shift(-1)
        pred = d[f"{name}_ret"]
        j = pd.concat([pred.rename("p"), fm["fm_ret_next"].rename("fm"), d["atr14"].rename("atr")], axis=1).dropna()
        sa_fm = (np.sign(j["p"]) * j["fm"] / j["atr"])
        full_mean = results[name]["sign_adj_next"]["mean"]
        share = float(sa_fm.mean() / full_mean) if full_mean else float("nan")
        kill[name] = {"n": int(len(j)), "first_min_mean": float(sa_fm.mean()), "share_of_full": share,
                      "kill": bool(abs(share) > 0.5) if not np.isnan(share) else False}

    print("\nOPEN / CLOSE / MIDDAY sign-adjusted next-day slot return (ATR units, block bootstrap 90% CI):")
    for name in ["OPEN", "CLOSE", "MIDDAY"]:
        s = results[name]["sign_adj_next"]
        tag = " <== GATING" if name in ("OPEN", "CLOSE") else " (control)"
        print(f"  {name:<6} n={s['n']:>4} mean={s['mean']:+.4f} ci_90=({s['ci_90'][0]:+.4f},{s['ci_90'][1]:+.4f}) {s['direction']}{tag}")
        u = results[name]["unconditional_next"]
        print(f"         unconditional next-slot mean={u['mean']:+.4f} ci_90=({u['ci_90'][0]:+.4f},{u['ci_90'][1]:+.4f})")
        print(f"         dose: top_tercile={results[name]['dose_top_tercile']['mean']:+.4f} bottom_tercile={results[name]['dose_bottom_tercile']['mean']:+.4f}")
        print(f"         halves: 1st={results[name]['first_half']['mean']:+.4f} 2nd={results[name]['second_half']['mean']:+.4f}")
        k = kill[name]
        print(f"         kill: first_min_share={k['share_of_full']:+.3f} KILL={k['kill']}")

    open_p1 = results["OPEN"]["sign_adj_next"]["direction"] == "positive"
    close_p1 = results["CLOSE"]["sign_adj_next"]["direction"] == "positive"
    open_killed = kill["OPEN"]["kill"] and open_p1
    close_killed = kill["CLOSE"]["kill"] and close_p1
    if (open_p1 and not open_killed) or (close_p1 and not close_killed):
        midday_p2 = results["MIDDAY"]["sign_adj_next"]["direction"] == "positive"
        if midday_p2:
            verdict, note = "P1_PASS_BUT_CONFOUNDED", "A gating slot passed but MIDDAY shows the same persistence -- this is generic daily autocorrelation, not scheduled-flow periodicity. Recorded confounded per falsifier (b). Closes."
        else:
            verdict, note = "P1_PASS", "A scheduled-slot (OPEN or CLOSE) shows credible same-slot persistence and MIDDAY does not. Advance to Statistical per pipeline order."
    elif open_killed or close_killed:
        verdict, note = "KILLED", "The passing slot's response is concentrated in its own first minute -- an auction-print artifact, not periodicity. Family terminates per kill rule (c)."
    else:
        verdict, note = "P1_FAIL", "Neither OPEN nor CLOSE slot shows credible same-slot next-day persistence. Entry closes on falsifier (a)."
    print(f"\nVERDICT: {verdict}\n  {note}")

    out = {"n_sessions": int(len(d)), "dropped": int(dropped), "results": results, "kill": kill, "verdict": verdict, "note": note}
    (DATA_DIR / "market_behavior_discovery_scan_022_results.json").write_text(json.dumps(out, indent=2, default=float))
    print(f"\nWritten: {DATA_DIR / 'market_behavior_discovery_scan_022_results.json'}")


if __name__ == "__main__":
    main()
