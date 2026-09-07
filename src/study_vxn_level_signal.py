"""
study_vxn_level_signal.py
=============================

exp-059 -- first test of VXN (CBOE Nasdaq-100 Volatility Index) as a
STANDALONE predictive signal, not just an event-day pricing check
(exp-039/040/vxn_pricing_check used it only to characterize whether
CPI/NFP/FOMC magnitude findings were already priced in). Directly
follows the 2026-09-07 strategic-direction conversation: after 58
experiments, mostly on price/time patterns, Claude and the Advisor
independently recommended pivoting the search to a genuinely different
kind of data. VXN is already on hand (Jason downloaded it from FRED,
data/VXNCLS_MAX.csv, 2001-02-02 through 2026-09-02) -- free, no new
purchase, no new event-date research.

FROZEN HYPOTHESIS (written before this script is run, before any
Discovery-slice number is looked at):

    NQ's next-trading-day close-to-close log return differs between
    days that followed an unusually LOW VXN close (bottom tercile, via
    a causal expanding percentile rank -- "the options market was
    unusually calm") versus days that followed an unusually HIGH VXN
    close (top tercile -- "the options market was unusually fearful"),
    tested on the Discovery slice only.

    VXN's own prior-day close (T-1, the last value known before NQ
    trades on day T) is the condition -- no lookahead, exactly what a
    live system would have known.

STEP 1 ONLY (statistical, no costs) -- same gate style as exp-046's
multi-factor model: this is a characterization test of whether VXN's
level carries any predictive information at all. A costed, tradeable
rule is only built as a SEPARATE follow-up if Step 1 clears the bar.
Statistically credible = 90% bootstrap CI on (mean return after LOW
VXN) - (mean return after HIGH VXN) entirely on one side of zero.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes, compute_daily_log_returns
    (study_volatility_regime.py)
  - causal_expanding_tercile (study_collective_evidence_pilot.py, exp-055)
  - bootstrap_mean_diff_ci (study_futures_expiration.py)

NEW CODE: only reading/aligning the VXN CSV to NQ trading days.

HOW TO RUN:
    python3 src/study_vxn_level_signal.py
"""

import json
from pathlib import Path

import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes, compute_daily_log_returns  # reused unmodified
from study_collective_evidence_pilot import causal_expanding_tercile  # reused unmodified, exp-055
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VXN_PATH = DATA_DIR / "VXNCLS_MAX.csv"


def main():
    print("=" * 78)
    print("EXP-059: VXN LEVEL AS A STANDALONE PREDICTIVE SIGNAL (Step 1, no costs)")
    print("=" * 78)
    print("\nFrozen hypothesis (see this file's docstring): does NQ's next-day return")
    print("differ after an unusually LOW vs unusually HIGH prior VXN close? Discovery slice only.\n")

    full_df, is_synthetic = load_price_data(context="study_vxn_level_signal.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)  # reused unmodified
    daily_returns = compute_daily_log_returns(ref_closes)  # reused unmodified

    vxn_df = pd.read_csv(VXN_PATH, parse_dates=["observation_date"])
    vxn_df["date"] = vxn_df["observation_date"].dt.date
    vxn_df = vxn_df.dropna(subset=["VXNCLS"]).sort_values("date")
    vxn_by_day = dict(zip(vxn_df["date"], vxn_df["VXNCLS"]))

    all_days = sorted(day_groups.keys())
    # Causal expanding tercile of VXN's OWN level, using only VXN values
    # known as of each day (VXN closes same day as NQ, so VXN[day] is
    # available at NQ's close on `day` -- used here as the condition for
    # the FOLLOWING day's NQ return, i.e. no lookahead).
    vxn_values_on_nq_days = {d: vxn_by_day[d] for d in all_days if d in vxn_by_day}
    vxn_tercile = causal_expanding_tercile(vxn_values_on_nq_days)  # reused unmodified, exp-055

    low_returns = []
    high_returns = []
    for i in range(1, len(all_days)):
        prior_day, day = all_days[i - 1], all_days[i]
        if day not in daily_returns:
            continue
        tercile = vxn_tercile.get(prior_day)
        if tercile == "low":
            low_returns.append(daily_returns[day])
        elif tercile == "high":
            high_returns.append(daily_returns[day])

    print(f"Days following a LOW VXN close (bottom tercile): n={len(low_returns)}")
    print(f"Days following a HIGH VXN close (top tercile):   n={len(high_returns)}")

    mean_low = sum(low_returns) / len(low_returns) if low_returns else float("nan")
    mean_high = sum(high_returns) / len(high_returns) if high_returns else float("nan")
    print(f"\nMean next-day log return after LOW VXN:  {mean_low:.6f}")
    print(f"Mean next-day log return after HIGH VXN: {mean_high:.6f}")

    ci_low, ci_high = bootstrap_mean_diff_ci(low_returns, high_returns)  # reused unmodified
    diff = mean_low - mean_high
    statistically_credible = (ci_low > 0) or (ci_high < 0)
    print(f"\nDifference (LOW - HIGH): {diff:.6f}")
    print(f"90% bootstrap CI on the difference: ({ci_low:.6f}, {ci_high:.6f})")
    print(f"Statistically credible (CI entirely off zero): {statistically_credible}")

    print(f"\n{'=' * 78}")
    if statistically_credible:
        verdict = ("STEP 1 PASS. VXN's level carries some distinguishable predictive "
                   "signal for next-day NQ direction on the Discovery slice. Logged as "
                   "PROMISING (Step 1 only -- no costed rule built yet, no trades). Next "
                   "step: design one concrete, pre-registered, costed trading rule around "
                   "this and test it prospectively on the Validation slice, same discipline "
                   "as every other lead in this project.")
    else:
        verdict = ("STEP 1 FAIL. VXN's level alone does not show a statistically credible "
                   "difference in next-day NQ returns between calm and fearful days on the "
                   "Discovery slice. Logged as REJECTED. No costed rule is built -- this "
                   "specific framing of VXN as a standalone signal is closed.")
    print(f"Verdict: {verdict}")

    out = {
        "n_low": len(low_returns),
        "n_high": len(high_returns),
        "mean_low": mean_low,
        "mean_high": mean_high,
        "diff": diff,
        "ci_90": [ci_low, ci_high],
        "statistically_credible": statistically_credible,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_vxn_level_signal_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
