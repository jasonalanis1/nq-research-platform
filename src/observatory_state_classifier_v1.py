"""Observatory fixed state classifier, v1 (queue v2 item 4, final listed
sub-step). Characterize, do not claim. No ML, no fitting: every state is a
fixed, interpretable rule computed from information available BEFORE the
session it describes.

At the current data ceiling (no ES/RTY/YM), the "broad-equity agreement vs
NQ-only residual" states from the spec are NOT computable and are recorded
as parked. What IS computable from NQ + ZN:

  RATE state (from the PRIOR RTH session):
    rate_confirmed  : sign(NQ prior RTH return) != sign(ZN prior RTH return)
                      -- the normal risk-on/risk-off configuration
    rate_conflicted : same sign (both up or both down)
  OVERNIGHT VARIANCE state (from the overnight session just ended):
    ovn_high / ovn_mid / ovn_low  : tercile of overnight range / ATR14,
                                    terciles frozen on Discovery
  PRIOR CASH-SESSION VARIANCE state (from the prior RTH session):
    cash_high / cash_mid / cash_low : tercile of prior RTH range / ATR14

Outcomes for the RTH session the state describes (all / ATR14, lagged):
  range_ratio   : RTH range / trailing-20d mean RTH range
  abs_ret       : |RTH close-to-close return| (an MAE-style magnitude)
  signed_ret    : RTH return, reported next to the UNCONDITIONAL mean
                  (NULL 1) so no state's drift is read against zero.

Per state: n, mean of each outcome, block-bootstrap 90% CI (block 10),
and the unconditional row. Output = map-ready characterization.

HOW TO RUN:
    python3 src/observatory_state_classifier_v1.py
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

OUT = Path(__file__).resolve().parent.parent / "data" / "observatory_state_classifier_v1_results.json"
N_BOOT = 1000
SEED = 20260912


def daily_frames(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for day, g in df.groupby(df.index.date):
        rth = g.between_time("09:30", "16:00")
        if len(rth) < 200:      # skip roll-day / holiday partial sessions
            continue
        rows.append({"date": pd.Timestamp(day), "rth_open": rth["Open"].iloc[0], "rth_close": rth["Close"].iloc[-1],
                     "rth_range": rth["High"].max() - rth["Low"].min()})
    d = pd.DataFrame(rows).set_index("date").sort_index()
    d["rth_ret"] = d["rth_close"] / d["rth_open"] - 1
    return d


def overnight_ranges(df: pd.DataFrame) -> pd.Series:
    """Overnight range ending at each RTH date: bars from 18:00 the prior
    calendar day through 09:29 on `date`."""
    ovn = df.between_time("18:00", "09:29").copy()
    # assign each overnight bar to the RTH date it precedes
    ts = ovn.index
    sess_date = np.where(ts.hour >= 18, (ts + pd.Timedelta(days=1)).date, ts.date)
    ovn["sess"] = pd.to_datetime(sess_date)
    r = ovn.groupby("sess").agg(hi=("High", "max"), lo=("Low", "min"), n=("Close", "size"))
    r = r[r["n"] >= 300]
    return (r["hi"] - r["lo"]).rename("ovn_range")


def block_ci(v, block=10, n_boot=N_BOOT, seed=SEED):
    v = np.asarray(v, float); n = len(v)
    if n < 30:
        return [None, None]
    rng = np.random.default_rng(seed); nb = int(np.ceil(n / block)); m = np.empty(n_boot)
    for i in range(n_boot):
        st = rng.integers(0, max(n - block, 1), size=nb)
        m[i] = np.concatenate([v[s:s + block] for s in st])[:n].mean()
    m.sort()
    return [round(float(m[int(0.05 * n_boot)]), 4), round(float(m[int(0.95 * n_boot)]), 4)]


def summarize(sub: pd.DataFrame) -> dict:
    out = {"n": int(len(sub))}
    for col in ["range_ratio", "abs_ret_atr", "signed_ret_atr"]:
        v = sub[col].dropna().values
        out[col] = {"mean": round(float(v.mean()), 4) if len(v) else None, "ci_90": block_ci(v)}
    return out


def main():
    nq_all, s1 = load_price_data(context="observatory_state_classifier_v1.py", symbol="NQ")
    zn_all, s2 = load_price_data(context="observatory_state_classifier_v1.py", symbol="ZN")
    if s1 or s2:
        raise SystemExit("ABORT: synthetic data")
    nq = get_discovery_data(nq_all); zn = get_discovery_data(zn_all)

    d = daily_frames(nq)
    z = daily_frames(zn)[["rth_ret"]].rename(columns={"rth_ret": "zn_rth_ret"})
    d = d.join(z, how="inner")
    d = d.join(overnight_ranges(nq), how="left")

    # ATR14 = trailing mean RTH range, lagged one day (no lookahead)
    d["atr14"] = d["rth_range"].rolling(14).mean().shift(1)
    d["trail20_range"] = d["rth_range"].rolling(20).mean().shift(1)
    d["range_ratio"] = d["rth_range"] / d["trail20_range"]
    d["abs_ret_atr"] = (d["rth_close"] - d["rth_open"]).abs() / d["atr14"]
    d["signed_ret_atr"] = (d["rth_close"] - d["rth_open"]) / d["atr14"]

    # --- states, all from PRIOR information ---
    prior_nq = d["rth_ret"].shift(1); prior_zn = d["zn_rth_ret"].shift(1)
    d["rate_state"] = np.where(np.sign(prior_nq) != np.sign(prior_zn), "rate_confirmed", "rate_conflicted")
    d.loc[prior_nq.isna() | prior_zn.isna(), "rate_state"] = None

    ovn_norm = d["ovn_range"] / d["atr14"]
    q = ovn_norm.quantile([1 / 3, 2 / 3])
    d["ovn_state"] = pd.cut(ovn_norm, [-np.inf, q.iloc[0], q.iloc[1], np.inf], labels=["ovn_low", "ovn_mid", "ovn_high"]).astype(object)

    cash_norm = (d["rth_range"] / d["atr14"]).shift(1)
    q2 = cash_norm.quantile([1 / 3, 2 / 3])
    d["cash_state"] = pd.cut(cash_norm, [-np.inf, q2.iloc[0], q2.iloc[1], np.inf], labels=["cash_low", "cash_mid", "cash_high"]).astype(object)

    d = d.dropna(subset=["range_ratio", "abs_ret_atr", "signed_ret_atr"])

    results = {
        "n_days": int(len(d)),
        "tercile_edges": {"ovn_range_over_atr": [round(float(x), 4) for x in q.values],
                          "prior_cash_range_over_atr": [round(float(x), 4) for x in q2.values]},
        "parked_states": "broad-equity agreement / NQ-only residual need ES (data ceiling)",
        "unconditional": summarize(d),
        "by_state": {},
        "joint_rate_x_ovn": {},
    }
    for col in ["rate_state", "ovn_state", "cash_state"]:
        for st, sub in d.groupby(col):
            results["by_state"][str(st)] = summarize(sub)
    for (rs, os_), sub in d.groupby(["rate_state", "ovn_state"]):
        results["joint_rate_x_ovn"][f"{rs}|{os_}"] = summarize(sub)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1))

    u = results["unconditional"]
    print(f"n_days={results['n_days']}  UNCONDITIONAL: range_ratio={u['range_ratio']['mean']} abs_ret={u['abs_ret_atr']['mean']} signed={u['signed_ret_atr']['mean']} CI={u['signed_ret_atr']['ci_90']}")
    print("\nstate              n    range_ratio [CI]           abs_ret/ATR       signed/ATR [CI]")
    for st, r in results["by_state"].items():
        print(f"{st:17s} {r['n']:5d}  {r['range_ratio']['mean']:.3f} {r['range_ratio']['ci_90']}   {r['abs_ret_atr']['mean']:.3f}   {r['signed_ret_atr']['mean']:+.3f} {r['signed_ret_atr']['ci_90']}")
    print("\njoint rate x overnight:")
    for st, r in results["joint_rate_x_ovn"].items():
        print(f"{st:30s} n={r['n']:4d} range_ratio={r['range_ratio']['mean']:.3f} {r['range_ratio']['ci_90']} signed={r['signed_ret_atr']['mean']:+.3f}")
    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
