"""Observatory information-transmission characterization, v2 (queue v2 item
4, continued -- the sub-steps v1 listed as "next"). Characterize, do not
claim. No hypothesis, no promotion bar, no ledger row.

Extends src/observatory_information_transmission_v1.py in three directions
on the same NQ/ZN/6E/CL basket, Discovery slice:
  (a) SESSION: RTH (09:30-16:00 ET) vs OVERNIGHT (18:00 -> 09:30 ET) --
      v1 was RTH only.
  (b) RESOLUTION: 5 / 15 / 30 / 60-minute bars -- v1 was 15-min only.
  (c) SHOCK-CONDITIONED: instead of unconditional cross-correlation, take
      bars where the OTHER instrument's return is in its top/bottom 5% by
      absolute size (a "shock"), and measure NQ's mean sign-adjusted
      response over the next 1..4 bars, block-bootstrap 90% CI. This is
      the "shock -> responder -> lag -> decay" question the program spec
      names; unconditional correlation can hide conditional structure.

Outputs one JSON with the whole grid and prints a compact table. The
reading (what it does / does not settle) goes in the study doc, not here.

HOW TO RUN:
    python3 src/observatory_information_transmission_v2.py
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

OUT = Path(__file__).resolve().parent.parent / "data" / "observatory_info_transmission_v2_results.json"
SYMBOLS = ["NQ", "ZN", "6E", "CL"]
BARS = ["5min", "15min", "30min", "60min"]
MAX_LAG = 4
SHOCK_PCT = 5.0          # top/bottom 5% of |return| = shock
N_BOOT = 1000
SEED = 20260912


def session_slice(df: pd.DataFrame, session: str) -> pd.DataFrame:
    if session == "RTH":
        return df.between_time("09:30", "16:00")
    # overnight: 18:00 -> 09:30 next day. between_time handles wraparound.
    return df.between_time("18:00", "09:29")


def bar_returns(df: pd.DataFrame, bar: str) -> pd.Series:
    bars = df["Close"].resample(bar).last().dropna()
    bars = bars[bars > 0]
    return np.log(bars).diff().dropna()


def xcorr(a: pd.Series, b: pd.Series, max_lag: int) -> dict:
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    out = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag > 0:
            x, y = j["a"].values[:-lag], j["b"].values[lag:]
        elif lag < 0:
            x, y = j["a"].values[-lag:], j["b"].values[:lag]
        else:
            x, y = j["a"].values, j["b"].values
        out[str(lag)] = round(float(np.corrcoef(x, y)[0, 1]), 4) if len(x) > 30 else None
    return out


def block_ci(v: np.ndarray, block: int = 10, n_boot: int = N_BOOT, seed: int = SEED):
    v = np.asarray(v, float)
    n = len(v)
    if n < 30:
        return (None, None)
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    means = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, max(n - block, 1), size=nb)
        s = np.concatenate([v[st:st + block] for st in starts])[:n]
        means[i] = s.mean()
    means.sort()
    return (round(float(means[int(0.05 * n_boot)]), 5), round(float(means[int(0.95 * n_boot)]), 5))


def shock_response(nq: pd.Series, other: pd.Series, max_lag: int) -> dict:
    """Bars where |other| is in its top SHOCK_PCT percent. For each lag k in
    1..max_lag, NQ's return k bars AFTER the shock bar, sign-adjusted by
    the shock's sign, in units of NQ's own bar-return std (so resolutions
    are comparable). Positive = NQ moves WITH the shock later (transmission
    with lag); ~0 = nothing after the fact; negative = reversal."""
    j = pd.concat([nq.rename("nq"), other.rename("o")], axis=1).dropna()
    thr = np.percentile(np.abs(j["o"].values), 100 - SHOCK_PCT)
    shock_idx = np.where(np.abs(j["o"].values) >= thr)[0]
    sd = j["nq"].std()
    out = {"n_shocks": int(len(shock_idx)), "shock_threshold_abs_ret": round(float(thr), 6)}
    # same-bar co-movement for reference
    same = np.sign(j["o"].values[shock_idx]) * j["nq"].values[shock_idx] / sd
    out["lag0_same_bar"] = {"mean_sd_units": round(float(same.mean()), 4), "ci_90": block_ci(same)}
    for k in range(1, max_lag + 1):
        idx = shock_idx[shock_idx + k < len(j)]
        resp = np.sign(j["o"].values[idx]) * j["nq"].values[idx + k] / sd
        out[f"lag{k}"] = {"mean_sd_units": round(float(resp.mean()), 4), "ci_90": block_ci(resp)}
    return out


def main():
    print("Loading Discovery slices ...")
    raw = {}
    for s in SYMBOLS:
        df_all, synth = load_price_data(context="observatory_information_transmission_v2.py", symbol=s)
        if synth:
            raise SystemExit(f"ABORT: synthetic data for {s}")
        raw[s] = get_discovery_data(df_all)

    results = {"shock_pct": SHOCK_PCT, "max_lag": MAX_LAG, "grid": {}}
    for session in ["RTH", "OVN"]:
        for bar in BARS:
            rets = {s: bar_returns(session_slice(raw[s], session), bar) for s in SYMBOLS}
            cell = {"n_bars_NQ": int(len(rets["NQ"])), "pairs": {}}
            for o in ["ZN", "6E", "CL"]:
                cell["pairs"][f"NQ_vs_{o}"] = {
                    "xcorr_by_lag": xcorr(rets["NQ"], rets[o], MAX_LAG),
                    "shock_in_other_then_NQ": shock_response(rets["NQ"], rets[o], MAX_LAG),
                    "shock_in_NQ_then_other": shock_response(rets[o], rets["NQ"], MAX_LAG),
                }
            results["grid"][f"{session}_{bar}"] = cell
            print(f"  done {session} {bar}: NQ bars={cell['n_bars_NQ']}")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1))

    print("\n=== Summary: max |xcorr| at any NONZERO lag vs lag0 (unconditional) ===")
    for key, cell in results["grid"].items():
        for pair, d in cell["pairs"].items():
            xc = d["xcorr_by_lag"]
            l0 = xc["0"]
            nz = max(((abs(v), k) for k, v in xc.items() if k != "0" and v is not None), default=(0, None))
            print(f"  {key:10s} {pair:9s} lag0={l0:+.3f}  max|nonzero|={nz[0]:.3f} @lag {nz[1]}")
    print("\n=== Summary: shock in OTHER -> NQ next-bar response (sd units, 90% CI) ===")
    for key, cell in results["grid"].items():
        for pair, d in cell["pairs"].items():
            r = d["shock_in_other_then_NQ"]
            print(f"  {key:10s} {pair:9s} n={r['n_shocks']:5d} lag0={r['lag0_same_bar']['mean_sd_units']:+.3f} "
                  f"lag1={r['lag1']['mean_sd_units']:+.3f} CI={r['lag1']['ci_90']} lag2={r['lag2']['mean_sd_units']:+.3f}")
    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
