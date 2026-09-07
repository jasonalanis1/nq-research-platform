"""
study_bond_lead_signal.py
=============================

exp-061 -- first "cross-market" candidate under the 2026-09-07 gameplan
(branch 3: cross-market signal expansion, taken ONE market at a time,
per the Advisor's explicit warning against shotgunning many markets at
once). NOT a re-run of exp-051/052 (hyp-000021/000022) -- those tested
a 4-instrument PORTFOLIO construction (inverse-vol-weighted weekly
trend/reversal across NQ+ZN+6E+CL combined). This is a different
question entirely: does ONE market (10-Year Treasury Note futures, ZN
-- a proxy for interest-rate direction) LEAD Nasdaq futures the very
next day, tested as a simple standalone condition, same shape as the
VXN tests (exp-059/060), not a portfolio.

FROZEN HYPOTHESIS (written before this script is run, before any
Discovery-slice number is looked at):

    NQ's next-trading-day close-to-close log return differs between
    days that followed ZN (10Y Treasury futures) closing UP (positive
    log return) that day versus days that followed ZN closing DOWN
    (negative log return), tested on the Discovery slice only. Rising
    bond prices (ZN up) = falling rates = often read as risk-on for
    equities; the reverse for ZN down -- this tests whether that
    relationship actually shows up, next-day, in NQ specifically.

    ZN's own same-day return (T, the last value known before NQ trades
    on day T+1) is the condition -- no lookahead, exactly what a live
    system would have known at NQ's next open.

STEP 1 ONLY (statistical, no costs) -- same gate as exp-059/060/046.

Statistically credible = 90% bootstrap CI on (mean NQ return after ZN
up) - (mean NQ return after ZN down) entirely on one side of zero.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes, compute_daily_log_returns
    (study_volatility_regime.py)
  - bootstrap_mean_diff_ci (study_futures_expiration.py)
  - load_price_data(symbol="ZN") (data_loader.py, already used by
    study_cross_asset_weekly_trend.py)

NEW CODE: only aligning ZN's own daily sign to the following NQ day
(no portfolio construction, no volatility weighting -- this is
deliberately the simplest possible framing to avoid scope creep).

HOW TO RUN:
    python3 src/study_bond_lead_signal.py
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
    print("EXP-061: ZN (10Y TREASURY) SAME-DAY MOVE AS A NEXT-DAY NQ SIGNAL (Step 1)")
    print("=" * 78)
    print("\nFrozen hypothesis (see this file's docstring): does NQ's next-day return")
    print("differ after ZN closes up vs down? Discovery slice only, single market.\n")

    nq_full_df, nq_synthetic = load_price_data(context="study_bond_lead_signal.py (NQ)")
    if nq_synthetic:
        print("ABORT: only synthetic NQ data is available -- this study requires real data.")
        return
    try:
        zn_full_df, zn_synthetic = load_price_data(context="study_bond_lead_signal.py (ZN)", symbol="ZN")
    except FileNotFoundError:
        print("ABORT: ZN data file not found.")
        return
    if zn_synthetic:
        print("ABORT: only synthetic ZN data is available -- this study requires real data.")
        return

    nq_discovery = get_discovery_data(nq_full_df)
    zn_discovery = get_discovery_data(zn_full_df)

    nq_day_groups = {day: sub for day, sub in nq_discovery.groupby(nq_discovery.index.date)}
    zn_day_groups = {day: sub for day, sub in zn_discovery.groupby(zn_discovery.index.date)}

    nq_ref_closes = compute_daily_ref_closes(nq_day_groups)  # reused unmodified
    zn_ref_closes = compute_daily_ref_closes(zn_day_groups)  # reused unmodified
    nq_returns = compute_daily_log_returns(nq_ref_closes)  # reused unmodified
    zn_returns = compute_daily_log_returns(zn_ref_closes)  # reused unmodified

    zn_days_sorted = sorted(zn_returns.keys())
    nq_days_sorted = sorted(nq_returns.keys())

    zn_up_returns = []
    zn_down_returns = []
    for i in range(1, len(nq_days_sorted)):
        prior_day, day = nq_days_sorted[i - 1], nq_days_sorted[i]
        zn_ret = zn_returns.get(prior_day)
        if zn_ret is None:
            continue
        nq_ret = nq_returns.get(day)
        if nq_ret is None:
            continue
        if zn_ret > 0:
            zn_up_returns.append(nq_ret)
        elif zn_ret < 0:
            zn_down_returns.append(nq_ret)

    print(f"Days following ZN closing UP:   n={len(zn_up_returns)}")
    print(f"Days following ZN closing DOWN: n={len(zn_down_returns)}")

    mean_up = sum(zn_up_returns) / len(zn_up_returns) if zn_up_returns else float("nan")
    mean_down = sum(zn_down_returns) / len(zn_down_returns) if zn_down_returns else float("nan")
    print(f"\nMean next-day NQ log return after ZN UP:   {mean_up:.6f}")
    print(f"Mean next-day NQ log return after ZN DOWN: {mean_down:.6f}")

    ci_low, ci_high = bootstrap_mean_diff_ci(zn_up_returns, zn_down_returns)  # reused unmodified
    diff = mean_up - mean_down
    statistically_credible = (ci_low > 0) or (ci_high < 0)
    print(f"\nDifference (UP - DOWN): {diff:.6f}")
    print(f"90% bootstrap CI on the difference: ({ci_low:.6f}, {ci_high:.6f})")
    print(f"Statistically credible (CI entirely off zero): {statistically_credible}")

    print(f"\n{'=' * 78}")
    if statistically_credible:
        verdict = ("STEP 1 PASS. ZN's same-day direction carries some distinguishable "
                   "predictive signal for next-day NQ direction on the Discovery slice. "
                   "Logged as PROMISING (Step 1 only -- no costed rule built yet, no "
                   "trades). Next step: design one concrete, pre-registered, costed "
                   "trading rule and test it prospectively on the Validation slice.")
    else:
        verdict = ("STEP 1 FAIL. ZN's same-day direction alone does not show a "
                   "statistically credible difference in next-day NQ returns on the "
                   "Discovery slice. Logged as REJECTED. No costed rule is built -- this "
                   "single-market bond-lead framing is closed.")
    print(f"Verdict: {verdict}")

    out = {
        "n_zn_up": len(zn_up_returns),
        "n_zn_down": len(zn_down_returns),
        "mean_nq_after_zn_up": mean_up,
        "mean_nq_after_zn_down": mean_down,
        "diff": diff,
        "ci_90": [ci_low, ci_high],
        "statistically_credible": statistically_credible,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_bond_lead_signal_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
