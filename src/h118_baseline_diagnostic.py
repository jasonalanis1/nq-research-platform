"""
h118_baseline_diagnostic.py
===========================

READ-ONLY diagnostic (queue v2 item 1b, September 12th, 2026). Does H118's
LOW-tercile 10-day drift beat NQ's OWN 10-day drift over the same slice, or
did it clear "above zero" by riding the index?

Reuses study_vwap_dist_low_10d_drift_h118 unmodified: same state frame,
same frozen Discovery bucket edges, same run_backtest() -- called once per
bucket and once with an all-days bucket so every number is in H118's own
units (net R-multiple = (close[t+10] - close[t] - round-trip cost) / atr14).

Touches nothing frozen: no spec, no ledger, no forward log. Writes one JSON
and one markdown report under research/studies/.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data, get_validation_data
from market_state_primitives import build_state_frame
from market_state_primitives_v2 import extend_state_frame
import study_vwap_dist_low_10d_drift_h118 as h118
from baseline_relative import baseline_relative, bootstrap_diff_ci, block_bootstrap_diff_ci

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = PROJECT_ROOT / "data" / "h118_baseline_diagnostic.json"
OUT_MD = PROJECT_ROOT / "research" / "studies" / "h118-baseline-diagnostic-2026-09-12.md"


def r_multiples_for_bucket(states_reset, bin_edges, labels, bucket):
    """Run H118's own backtest loop for an arbitrary bucket label by
    temporarily pointing its module-level BUCKET at it. 'ALL' = every day."""
    original = h118.BUCKET
    try:
        if bucket == "ALL":
            frame = states_reset.copy()
            frame[h118.VAR] = 0.0                       # everything lands in one bin
            h118.BUCKET = "all"
            _, _, r = h118.run_backtest(frame, [-np.inf, np.inf], ["all"])
        else:
            h118.BUCKET = bucket
            _, _, r = h118.run_backtest(states_reset, bin_edges, labels)
    finally:
        h118.BUCKET = original
    return r


def slice_report(name, states_reset, bin_edges, labels):
    out = {"slice": name, "n_days": int(len(states_reset)), "buckets": {}}
    all_r = r_multiples_for_bucket(states_reset, bin_edges, labels, "ALL")
    out["all_days"] = {"n": len(all_r), "mean_r": float(np.mean(all_r)),
                       "ci_90_iid": list(h118.bootstrap_mean_ci(all_r))}
    for b in labels:
        r = r_multiples_for_bucket(states_reset, bin_edges, labels, b)
        rel = baseline_relative(r, all_r)
        out["buckets"][b] = {
            "n": len(r), "mean_r": float(np.mean(r)), "ci_90_vs_zero_iid": list(h118.bootstrap_mean_ci(r)),
            "diff_vs_all_days": rel["diff"],
            "diff_ci_90_iid": list(bootstrap_diff_ci(r, all_r)),
            "diff_ci_90_block10": list(block_bootstrap_diff_ci(r, all_r, block=h118.HORIZON_DAYS)),
        }
    return out


def main():
    print("=" * 78); print("H118 BASELINE DIAGNOSTIC -- LOW tercile vs ALL days, same slice, same units"); print("=" * 78)
    df, syn = load_price_data(context="h118_baseline_diagnostic.py")
    if syn:
        print("ABORT: synthetic data."); return
    discovery = get_discovery_data(df)
    disc_states = extend_state_frame(build_state_frame(discovery), discovery).reset_index()
    bin_edges, labels = h118.compute_bin_edges(disc_states)     # frozen on Discovery, as always
    validation = get_validation_data(df)
    val_states = extend_state_frame(build_state_frame(validation), validation).reset_index()

    reports = [slice_report("Discovery", disc_states, bin_edges, labels),
               slice_report("Validation", val_states, bin_edges, labels)]

    lines = ["# H118 baseline diagnostic -- September 12th, 2026", "",
             "READ-ONLY. Question: does the LOW-tercile 10-day drift beat NQ's own 10-day drift over the same slice?",
             "Units: H118's own net R-multiple ((close[t+10]-close[t]-cost)/atr14). Bucket edges frozen on Discovery.",
             "Two CIs on the difference: iid bootstrap (H118's convention) and a 10-day moving-block bootstrap,",
             "which is the honest one because 10-day windows overlap and are autocorrelated.", ""]
    for rep in reports:
        a = rep["all_days"]
        lines += [f"## {rep['slice']} slice ({rep['n_days']} days)", "",
                  f"ALL days: n={a['n']} mean_r={a['mean_r']:+.4f} ci_90=({a['ci_90_iid'][0]:+.4f},{a['ci_90_iid'][1]:+.4f})", ""]
        print(f"\n{rep['slice']}: ALL days n={a['n']} mean_r={a['mean_r']:+.4f}")
        for b, v in rep["buckets"].items():
            tag = "  <== H118" if b == h118.BUCKET else ""
            line = (f"{b:<4} n={v['n']:>4} mean_r={v['mean_r']:+.4f} vs_zero=({v['ci_90_vs_zero_iid'][0]:+.4f},{v['ci_90_vs_zero_iid'][1]:+.4f}) | "
                    f"minus ALL = {v['diff_vs_all_days']:+.4f}  iid=({v['diff_ci_90_iid'][0]:+.4f},{v['diff_ci_90_iid'][1]:+.4f})  "
                    f"block10=({v['diff_ci_90_block10'][0]:+.4f},{v['diff_ci_90_block10'][1]:+.4f}){tag}")
            print("  " + line); lines.append("- " + line)
        lines.append("")

    low_d = reports[0]["buckets"][h118.BUCKET]; low_v = reports[1]["buckets"][h118.BUCKET]
    def verdict(v):
        return "clears" if v["diff_ci_90_block10"][0] > 0 else "does NOT clear"
    summary = (f"Verdict (block bootstrap, the honest CI): LOW minus ALL-days {verdict(low_d)} zero on Discovery "
               f"({low_d['diff_vs_all_days']:+.4f}, block10 CI {low_d['diff_ci_90_block10'][0]:+.4f}..{low_d['diff_ci_90_block10'][1]:+.4f}) "
               f"and {verdict(low_v)} zero on Validation "
               f"({low_v['diff_vs_all_days']:+.4f}, block10 CI {low_v['diff_ci_90_block10'][0]:+.4f}..{low_v['diff_ci_90_block10'][1]:+.4f}).")
    print("\n" + summary)
    lines += ["## Verdict", "", summary, "",
              "This changes nothing frozen. It is the comparison that should have been run when H118 was promoted; ",
              "the ledger status is Jason's call after reading it."]
    OUT_JSON.write_text(json.dumps({"reports": reports, "summary": summary}, indent=2, default=float))
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"\nWritten: {OUT_MD}")


if __name__ == "__main__":
    main()
