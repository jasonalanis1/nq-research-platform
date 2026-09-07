"""
study_currency_lead_signal.py
=============================

exp-063 -- second cross-market candidate under the 2026-09-07 gameplan
(branch 3), run ONE market at a time per the Advisor's explicit warning
against shotgunning many markets at once (exp-061/ZN was the first;
this is the next, run only after exp-061's result was fully logged and
handled on its own, not in the same batch).

FROZEN HYPOTHESIS (written before this script is run, before any
Discovery-slice number is looked at):

    NQ's next-trading-day close-to-close log return differs between
    days that followed 6E (Euro FX futures) closing UP (positive
    log return) that day versus days that followed 6E closing DOWN,
    tested on the Discovery slice only. A stronger Euro / weaker
    dollar is often read as risk-on for US equities; this tests
    whether that shows up, next-day, in NQ specifically. Same simple
    single-market shape as exp-061 (ZN), no portfolio construction.

    6E's own same-day return (T, the last value known before NQ trades
    on day T+1) is the condition -- no lookahead.

STEP 1 ONLY (statistical, no costs) -- same gate as exp-059/060/061.

Statistically credible = 90% bootstrap CI on (mean NQ return after 6E
up) - (mean NQ return after 6E down) entirely on one side of zero.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes, compute_daily_log_returns
    (study_volatility_regime.py)
  - bootstrap_mean_diff_ci (study_futures_expiration.py)
  - load_price_data(symbol="6E") (data_loader.py)

HOW TO RUN:
    python3 src/study_currency_lead_signal.py
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
    print("EXP-063: 6E (EURO FX) SAME-DAY MOVE AS A NEXT-DAY NQ SIGNAL (Step 1)")
    print("=" * 78)
    print("\nFrozen hypothesis (see this file's docstring): does NQ's next-day return")
    print("differ after 6E closes up vs down? Discovery slice only, single market.\n")

    nq_full_df, nq_synthetic = load_price_data(context="study_currency_lead_signal.py (NQ)")
    if nq_synthetic:
        print("ABORT: only synthetic NQ data is available -- this study requires real data.")
        return
    try:
        fx_full_df, fx_synthetic = load_price_data(context="study_currency_lead_signal.py (6E)", symbol="6E")
    except FileNotFoundError:
        print("ABORT: 6E data file not found.")
        return
    if fx_synthetic:
        print("ABORT: only synthetic 6E data is available -- this study requires real data.")
        return

    nq_discovery = get_discovery_data(nq_full_df)
    fx_discovery = get_discovery_data(fx_full_df)

    nq_day_groups = {day: sub for day, sub in nq_discovery.groupby(nq_discovery.index.date)}
    fx_day_groups = {day: sub for day, sub in fx_discovery.groupby(fx_discovery.index.date)}

    nq_ref_closes = compute_daily_ref_closes(nq_day_groups)  # reused unmodified
    fx_ref_closes = compute_daily_ref_closes(fx_day_groups)  # reused unmodified
    nq_returns = compute_daily_log_returns(nq_ref_closes)  # reused unmodified
    fx_returns = compute_daily_log_returns(fx_ref_closes)  # reused unmodified

    nq_days_sorted = sorted(nq_returns.keys())

    fx_up_returns = []
    fx_down_returns = []
    for i in range(1, len(nq_days_sorted)):
        prior_day, day = nq_days_sorted[i - 1], nq_days_sorted[i]
        fx_ret = fx_returns.get(prior_day)
        if fx_ret is None:
            continue
        nq_ret = nq_returns.get(day)
        if nq_ret is None:
            continue
        if fx_ret > 0:
            fx_up_returns.append(nq_ret)
        elif fx_ret < 0:
            fx_down_returns.append(nq_ret)

    print(f"Days following 6E closing UP:   n={len(fx_up_returns)}")
    print(f"Days following 6E closing DOWN: n={len(fx_down_returns)}")

    mean_up = sum(fx_up_returns) / len(fx_up_returns) if fx_up_returns else float("nan")
    mean_down = sum(fx_down_returns) / len(fx_down_returns) if fx_down_returns else float("nan")
    print(f"\nMean next-day NQ log return after 6E UP:   {mean_up:.6f}")
    print(f"Mean next-day NQ log return after 6E DOWN: {mean_down:.6f}")

    ci_low, ci_high = bootstrap_mean_diff_ci(fx_up_returns, fx_down_returns)  # reused unmodified
    diff = mean_up - mean_down
    statistically_credible = (ci_low > 0) or (ci_high < 0)
    print(f"\nDifference (UP - DOWN): {diff:.6f}")
    print(f"90% bootstrap CI on the difference: ({ci_low:.6f}, {ci_high:.6f})")
    print(f"Statistically credible (CI entirely off zero): {statistically_credible}")

    print(f"\n{'=' * 78}")
    if statistically_credible:
        verdict = ("STEP 1 PASS. 6E's same-day direction carries some distinguishable "
                   "predictive signal for next-day NQ direction on the Discovery slice. "
                   "Logged as PROMISING (Step 1 only -- no costed rule built yet, no "
                   "trades). Next step: design one concrete, pre-registered, costed "
                   "trading rule and test it prospectively on the Validation slice.")
    else:
        verdict = ("STEP 1 FAIL. 6E's same-day direction alone does not show a "
                   "statistically credible difference in next-day NQ returns on the "
                   "Discovery slice. Logged as REJECTED. No costed rule is built -- this "
                   "single-market currency-lead framing is closed.")
    print(f"Verdict: {verdict}")

    out = {
        "n_fx_up": len(fx_up_returns),
        "n_fx_down": len(fx_down_returns),
        "mean_nq_after_fx_up": mean_up,
        "mean_nq_after_fx_down": mean_down,
        "diff": diff,
        "ci_90": [ci_low, ci_high],
        "statistically_credible": statistically_credible,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_currency_lead_signal_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
