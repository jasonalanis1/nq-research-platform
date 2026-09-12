"""Observatory information-transmission characterization, v1 (queue v2 item
4, September 12th 3pm cycle). NOT a hypothesis test -- characterize, do not
claim, per NEXT_UP.md item 4: "an information-transmission map across
ES/NQ/RTY/YM/ZN/6E/CL ... shock -> first responder -> lag -> decay ->
reversal." At the current data ceiling (NQ/ZN/6E/CL only; ES/RTY/YM parked,
see KNOWLEDGE.md section 3), this is the 4-instrument slice of that program.

v1 scope (deliberately narrow, to get one clean characterization on disk
rather than a half-built full program): pairwise return cross-correlation
between NQ and each of ZN, 6E, CL at 15-minute bars, RTH session only,
lags -4..+4 (i.e. +/-60 minutes), Discovery slice. This answers the single
most basic information-transmission question -- does a move in one
instrument tend to precede, coincide with, or follow a move in NQ at this
resolution -- before building the full shock/decay/reversal machinery on
top. Output is map-ready observations (correlation-by-lag tables), not a
trade claim and not a new Idea Inventory entry on its own.

Multi-resolution (5/15/30/60-min) and the fixed state classifier (broad-
equity agreement / NQ-only residual / rate-confirmed / rate-conflicted /
overnight vs cash-session variance) are the next steps under this same
item, not built here -- this is v1, explicitly incomplete, and says so.

HOW TO RUN:
    python3 src/observatory_information_transmission_v1.py
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

OUT = Path(__file__).resolve().parent.parent / "data" / "observatory_info_transmission_v1_results.json"
BAR = "15min"
MAX_LAG = 4  # +/- 4 bars of 15 min = +/- 60 minutes


def load_rth_returns(symbol: str) -> pd.Series:
    df_all, is_synth = load_price_data(context="observatory_information_transmission_v1.py", symbol=symbol)
    if is_synth:
        raise SystemExit(f"ABORT: only synthetic data available for {symbol}.")
    disc = get_discovery_data(df_all)
    rth = disc.between_time("09:30", "16:00")
    bars = rth["Close"].resample(BAR).last().dropna()
    ret = np.log(bars).diff().dropna()
    return ret


def cross_corr_by_lag(a: pd.Series, b: pd.Series, max_lag: int) -> dict:
    """corr(a_t, b_{t+lag}) for lag in [-max_lag, max_lag]. Positive lag
    means b LEADS a (b's move at t+lag lines up with a's move at t, i.e.
    b happened earlier in calendar time relative to a's reaction) --
    equivalently this is corr(a.shift(-lag), b) in pandas terms. We report
    it explicitly both ways in the label to avoid sign confusion."""
    joined = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    out = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag == 0:
            x, y = joined["a"], joined["b"]
        elif lag > 0:
            # b at time t+lag vs a at time t  => b leads a by `lag` bars
            x = joined["a"].iloc[: len(joined) - lag]
            y = joined["b"].iloc[lag:]
        else:
            k = -lag
            x = joined["a"].iloc[k:]
            y = joined["b"].iloc[: len(joined) - k]
        n = min(len(x), len(y))
        if n < 30:
            out[str(lag)] = {"n": int(n), "corr": None}
            continue
        c = float(np.corrcoef(x.values[:n], y.values[:n])[0, 1])
        out[str(lag)] = {"n": int(n), "corr": round(c, 4)}
    return out


def main():
    print(f"Loading RTH {BAR} returns, Discovery slice, NQ + ZN + 6E + CL ...")
    rets = {}
    for sym in ["NQ", "ZN", "6E", "CL"]:
        rets[sym] = load_rth_returns(sym)
        print(f"  {sym}: {len(rets[sym])} {BAR} bars")

    results = {
        "bar": BAR, "max_lag_bars": MAX_LAG,
        "note": "positive lag = the OTHER instrument leads NQ by that many bars; "
                "negative lag = NQ leads the other instrument. corr at lag 0 is "
                "contemporaneous co-movement, not lead-lag.",
        "pairs": {},
    }
    for other in ["ZN", "6E", "CL"]:
        results["pairs"][f"NQ_vs_{other}"] = cross_corr_by_lag(rets["NQ"], rets[other], MAX_LAG)

    Path("data").mkdir(exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n--- Cross-correlation by lag ({BAR} bars, RTH, Discovery) ---")
    for pair, table in results["pairs"].items():
        print(f"\n{pair}:")
        # find the lag with max |corr|
        best_lag, best_abs = None, -1.0
        for lag_str, cell in table.items():
            if cell["corr"] is not None and abs(cell["corr"]) > best_abs:
                best_abs = abs(cell["corr"])
                best_lag = lag_str
        for lag_str in sorted(table.keys(), key=int):
            cell = table[lag_str]
            marker = "  <-- max |corr|" if lag_str == best_lag else ""
            print(f"  lag {lag_str:>3}: n={cell['n']:>4} corr={cell['corr']}{marker}")

    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
