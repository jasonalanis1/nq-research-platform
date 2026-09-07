"""
study_oil_lead_signal.py
=============================

exp-064 -- third cross-market candidate under the 2026-09-07 gameplan
(branch 3), run one market at a time (exp-061 ZN, exp-063 6E, this is
the third and, per the Advisor's original 4-instrument scope, the last
of the already-on-hand cross-asset instruments -- no new markets are
added without a fresh review, to avoid open-ended shotgunning).

FROZEN HYPOTHESIS (written before this script is run, before any
Discovery-slice number is looked at):

    NQ's next-trading-day close-to-close log return differs between
    days that followed CL (WTI Crude Oil futures) closing UP versus
    days that followed CL closing DOWN, tested on the Discovery slice
    only. Same simple single-market shape as exp-061/exp-063, no
    portfolio construction.

    CL's own same-day return (T, the last value known before NQ trades
    on day T+1) is the condition -- no lookahead. Note: exp-051 already
    found and fixed a real bug where WTI traded negative on 2020-04-20/
    21 (the May-2020 contract expiry event) -- reused compute_daily_ref_
    closes() already guards this (non-positive close treated as no
    usable close), so this script inherits that fix automatically.

STEP 1 ONLY (statistical, no costs) -- same gate as exp-059/060/061/063.

Statistically credible = 90% bootstrap CI on (mean NQ return after CL
up) - (mean NQ return after CL down) entirely on one side of zero.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes, compute_daily_log_returns
    (study_volatility_regime.py)
  - bootstrap_mean_diff_ci (study_futures_expiration.py)
  - load_price_data(symbol="CL") (data_loader.py)

HOW TO RUN:
    python3 src/study_oil_lead_signal.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes, compute_daily_log_returns  # reused unmodified
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main():
    print("=" * 78)
    print("EXP-064: CL (WTI CRUDE) SAME-DAY MOVE AS A NEXT-DAY NQ SIGNAL (Step 1)")
    print("=" * 78)
    print("\nFrozen hypothesis (see this file's docstring): does NQ's next-day return")
    print("differ after CL closes up vs down? Discovery slice only, single market.\n")

    nq_full_df, nq_synthetic = load_price_data(context="study_oil_lead_signal.py (NQ)")
    if nq_synthetic:
        print("ABORT: only synthetic NQ data is available -- this study requires real data.")
        return
    try:
        cl_full_df, cl_synthetic = load_price_data(context="study_oil_lead_signal.py (CL)", symbol="CL")
    except FileNotFoundError:
        print("ABORT: CL data file not found.")
        return
    if cl_synthetic:
        print("ABORT: only synthetic CL data is available -- this study requires real data.")
        return

    nq_discovery = get_discovery_data(nq_full_df)
    cl_discovery = get_discovery_data(cl_full_df)

    nq_day_groups = {day: sub for day, sub in nq_discovery.groupby(nq_discovery.index.date)}
    cl_day_groups = {day: sub for day, sub in cl_discovery.groupby(cl_discovery.index.date)}

    nq_ref_closes = compute_daily_ref_closes(nq_day_groups)  # reused unmodified
    cl_ref_closes = compute_daily_ref_closes(cl_day_groups)  # reused unmodified, guards non-positive closes
    nq_returns = compute_daily_log_returns(nq_ref_closes)  # reused unmodified
    cl_returns = compute_daily_log_returns(cl_ref_closes)  # reused unmodified

    nq_days_sorted = sorted(nq_returns.keys())

    cl_up_returns = []
    cl_down_returns = []
    for i in range(1, len(nq_days_sorted)):
        prior_day, day = nq_days_sorted[i - 1], nq_days_sorted[i]
        cl_ret = cl_returns.get(prior_day)
        if cl_ret is None:
            continue
        nq_ret = nq_returns.get(day)
        if nq_ret is None:
            continue
        if cl_ret > 0:
            cl_up_returns.append(nq_ret)
        elif cl_ret < 0:
            cl_down_returns.append(nq_ret)

    print(f"Days following CL closing UP:   n={len(cl_up_returns)}")
    print(f"Days following CL closing DOWN: n={len(cl_down_returns)}")

    mean_up = sum(cl_up_returns) / len(cl_up_returns) if cl_up_returns else float("nan")
    mean_down = sum(cl_down_returns) / len(cl_down_returns) if cl_down_returns else float("nan")
    print(f"\nMean next-day NQ log return after CL UP:   {mean_up:.6f}")
    print(f"Mean next-day NQ log return after CL DOWN: {mean_down:.6f}")

    ci_low, ci_high = bootstrap_mean_diff_ci(cl_up_returns, cl_down_returns)  # reused unmodified
    diff = mean_up - mean_down
    statistically_credible = (ci_low > 0) or (ci_high < 0)
    print(f"\nDifference (UP - DOWN): {diff:.6f}")
    print(f"90% bootstrap CI on the difference: ({ci_low:.6f}, {ci_high:.6f})")
    print(f"Statistically credible (CI entirely off zero): {statistically_credible}")

    print(f"\n{'=' * 78}")
    if statistically_credible:
        verdict = ("STEP 1 PASS. CL's same-day direction carries some distinguishable "
                   "predictive signal for next-day NQ direction on the Discovery slice. "
                   "Logged as PROMISING (Step 1 only -- no costed rule built yet, no "
                   "trades). Next step: design one concrete, pre-registered, costed "
                   "trading rule and test it prospectively on the Validation slice.")
    else:
        verdict = ("STEP 1 FAIL. CL's same-day direction alone does not show a "
                   "statistically credible difference in next-day NQ returns on the "
                   "Discovery slice. Logged as REJECTED. No costed rule is built -- this "
                   "single-market oil-lead framing is closed.")
    print(f"Verdict: {verdict}")

    out = {
        "n_cl_up": len(cl_up_returns),
        "n_cl_down": len(cl_down_returns),
        "mean_nq_after_cl_up": mean_up,
        "mean_nq_after_cl_down": mean_down,
        "diff": diff,
        "ci_90": [ci_low, ci_high],
        "statistically_credible": statistically_credible,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_oil_lead_signal_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
