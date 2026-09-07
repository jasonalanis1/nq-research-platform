"""
study_vxn_roc_signal.py
=============================

exp-060 -- second alt-data test, per the 2026-09-07 gameplan
(top-priority branch): VXN's RATE OF CHANGE, not its raw level.
exp-059 tested whether VXN's LEVEL (calm vs fearful) predicts next-day
NQ direction -- it did not (Step 1 FAIL). This is a genuinely different
question: does the DIRECTION AND SPEED of VXN's recent move (rising
fast = fear building, falling fast = fear draining) carry information,
independent of whether the level itself is high or low.

FROZEN HYPOTHESIS (written before this script is run, before any
Discovery-slice number is looked at):

    NQ's next-trading-day close-to-close log return differs between
    days that followed VXN RISING FAST over the prior 5 trading days
    (top tercile of 5-day rate of change, via causal expanding
    percentile rank -- "fear building quickly") versus days that
    followed VXN FALLING FAST (bottom tercile -- "fear draining
    quickly"), tested on the Discovery slice only.

    5-day rate of change = VXN_close[T-1] - VXN_close[T-6] (in VXN
    points), using only VXN closes known before NQ trades on day T --
    no lookahead.

STEP 1 ONLY (statistical, no costs) -- same gate as exp-059/046: this
characterizes whether VXN's rate of change carries predictive
information at all. A costed, tradeable rule is a separate follow-up,
only if Step 1 clears the bar.

Statistically credible = 90% bootstrap CI on (mean return after FAST
RISE) - (mean return after FAST FALL) entirely on one side of zero.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes, compute_daily_log_returns
    (study_volatility_regime.py)
  - causal_expanding_tercile (study_collective_evidence_pilot.py, exp-055)
  - bootstrap_mean_diff_ci (study_futures_expiration.py)

NEW CODE: only the 5-day-rate-of-change computation on the VXN series
(everything else reuses exp-059's plumbing unmodified).

HOW TO RUN:
    python3 src/study_vxn_roc_signal.py
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

ROC_LOOKBACK_DAYS = 5


def main():
    print("=" * 78)
    print("EXP-060: VXN 5-DAY RATE OF CHANGE AS A PREDICTIVE SIGNAL (Step 1, no costs)")
    print("=" * 78)
    print("\nFrozen hypothesis (see this file's docstring): does NQ's next-day return")
    print("differ after VXN rising fast vs falling fast over 5 days? Discovery slice only.\n")

    full_df, is_synthetic = load_price_data(context="study_vxn_roc_signal.py")
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
    vxn_days_sorted = sorted(vxn_by_day.keys())
    vxn_idx = {d: i for i, d in enumerate(vxn_days_sorted)}

    all_days = sorted(day_groups.keys())

    # 5-day rate of change of VXN's OWN series (in VXN's own trading-day
    # index, not NQ's -- VXN trades every weekday same as equities/vol
    # indices; using VXN's own calendar avoids NQ-holiday gaps distorting
    # the "5 trading days" window).
    roc_by_vxn_day = {}
    for d in vxn_days_sorted:
        i = vxn_idx[d]
        if i < ROC_LOOKBACK_DAYS:
            continue
        prior_d = vxn_days_sorted[i - ROC_LOOKBACK_DAYS]
        roc_by_vxn_day[d] = vxn_by_day[d] - vxn_by_day[prior_d]

    # Causal expanding tercile of the RoC series itself (reused unmodified).
    roc_tercile = causal_expanding_tercile(roc_by_vxn_day)  # reused unmodified, exp-055

    fast_rise_returns = []
    fast_fall_returns = []
    for i in range(1, len(all_days)):
        prior_day, day = all_days[i - 1], all_days[i]
        if day not in daily_returns:
            continue
        tercile = roc_tercile.get(prior_day)
        if tercile == "high":
            fast_rise_returns.append(daily_returns[day])
        elif tercile == "low":
            fast_fall_returns.append(daily_returns[day])

    print(f"Days following VXN RISING fast (top tercile of 5-day RoC): n={len(fast_rise_returns)}")
    print(f"Days following VXN FALLING fast (bottom tercile):          n={len(fast_fall_returns)}")

    mean_rise = sum(fast_rise_returns) / len(fast_rise_returns) if fast_rise_returns else float("nan")
    mean_fall = sum(fast_fall_returns) / len(fast_fall_returns) if fast_fall_returns else float("nan")
    print(f"\nMean next-day log return after FAST RISE: {mean_rise:.6f}")
    print(f"Mean next-day log return after FAST FALL: {mean_fall:.6f}")

    ci_low, ci_high = bootstrap_mean_diff_ci(fast_rise_returns, fast_fall_returns)  # reused unmodified
    diff = mean_rise - mean_fall
    statistically_credible = (ci_low > 0) or (ci_high < 0)
    print(f"\nDifference (RISE - FALL): {diff:.6f}")
    print(f"90% bootstrap CI on the difference: ({ci_low:.6f}, {ci_high:.6f})")
    print(f"Statistically credible (CI entirely off zero): {statistically_credible}")

    print(f"\n{'=' * 78}")
    if statistically_credible:
        verdict = ("STEP 1 PASS. VXN's rate of change carries some distinguishable "
                   "predictive signal for next-day NQ direction on the Discovery slice. "
                   "Logged as PROMISING (Step 1 only -- no costed rule built yet, no "
                   "trades). Next step: design one concrete, pre-registered, costed "
                   "trading rule and test it prospectively on the Validation slice, same "
                   "discipline as every other lead in this project.")
    else:
        verdict = ("STEP 1 FAIL. VXN's rate of change alone does not show a statistically "
                   "credible difference in next-day NQ returns between fast-rising and "
                   "fast-falling fear on the Discovery slice. Logged as REJECTED. No "
                   "costed rule is built -- this framing of VXN is closed.")
    print(f"Verdict: {verdict}")

    out = {
        "roc_lookback_days": ROC_LOOKBACK_DAYS,
        "n_fast_rise": len(fast_rise_returns),
        "n_fast_fall": len(fast_fall_returns),
        "mean_fast_rise": mean_rise,
        "mean_fast_fall": mean_fall,
        "diff": diff,
        "ci_90": [ci_low, ci_high],
        "statistically_credible": statistically_credible,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_vxn_roc_signal_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
