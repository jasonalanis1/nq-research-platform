"""
study_bond_multiday_lead_signal.py
=============================

exp-065 -- a genuinely different framing of the ZN/bonds lead idea,
NOT a re-run of exp-061 (same-day ZN direction, PROMISING/parked
pending a small data purchase) or exp-051/052 (4-instrument portfolio
constructions, both REJECTED). This tests whether a SUSTAINED bond
move over several days (not just yesterday's single-day direction)
carries information -- a distinct, new hypothesis using data already
on hand, no new purchase needed.

FROZEN HYPOTHESIS (written before this script is run, before any
Discovery-slice number is looked at):

    NQ's next-trading-day close-to-close log return differs between
    days that followed a 3-day CUMULATIVE ZN move in the top tercile
    (bonds rallying hard over 3 days -- rates falling fast) versus the
    bottom tercile (bonds selling off hard -- rates rising fast), via a
    causal expanding percentile rank, tested on the Discovery slice
    only.

    The 3-day cumulative ZN return ending on day T (the last value
    known before NQ trades on day T+1) is the condition -- no
    lookahead.

STEP 1 ONLY (statistical, no costs) -- same gate as every other
alt-data candidate this round.

Statistically credible = 90% bootstrap CI on (mean NQ return after
ZN 3-day RALLY) - (mean NQ return after ZN 3-day SELLOFF) entirely on
one side of zero.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes, compute_daily_log_returns
    (study_volatility_regime.py)
  - causal_expanding_tercile (study_collective_evidence_pilot.py, exp-055)
  - bootstrap_mean_diff_ci (study_futures_expiration.py)
  - load_price_data(symbol="ZN") (data_loader.py)

NEW CODE: only the 3-day cumulative-return computation on ZN's own
daily return series (same general shape as exp-060's VXN rate-of-
change script, applied here to ZN's own returns instead of VXN's
level).

HOW TO RUN:
    python3 src/study_bond_multiday_lead_signal.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes, compute_daily_log_returns  # reused unmodified
from study_collective_evidence_pilot import causal_expanding_tercile  # reused unmodified, exp-055
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

CUMULATIVE_WINDOW_DAYS = 3


def main():
    print("=" * 78)
    print("EXP-065: ZN 3-DAY CUMULATIVE MOVE AS A NEXT-DAY NQ SIGNAL (Step 1)")
    print("=" * 78)
    print("\nFrozen hypothesis (see this file's docstring): does NQ's next-day return")
    print("differ after a 3-day ZN rally vs selloff? Discovery slice only.\n")

    nq_full_df, nq_synthetic = load_price_data(context="study_bond_multiday_lead_signal.py (NQ)")
    if nq_synthetic:
        print("ABORT: only synthetic NQ data is available -- this study requires real data.")
        return
    try:
        zn_full_df, zn_synthetic = load_price_data(
            context="study_bond_multiday_lead_signal.py (ZN)", symbol="ZN"
        )
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
    zn_idx = {d: i for i, d in enumerate(zn_days_sorted)}

    # 3-day cumulative ZN return ending on each ZN trading day.
    cum_by_zn_day = {}
    for d in zn_days_sorted:
        i = zn_idx[d]
        if i < CUMULATIVE_WINDOW_DAYS - 1:
            continue
        window_days = zn_days_sorted[i - CUMULATIVE_WINDOW_DAYS + 1: i + 1]
        cum_by_zn_day[d] = sum(zn_returns[wd] for wd in window_days)

    cum_tercile = causal_expanding_tercile(cum_by_zn_day)  # reused unmodified, exp-055

    nq_days_sorted = sorted(nq_returns.keys())
    rally_returns = []
    selloff_returns = []
    for i in range(1, len(nq_days_sorted)):
        prior_day, day = nq_days_sorted[i - 1], nq_days_sorted[i]
        if day not in nq_returns:
            continue
        tercile = cum_tercile.get(prior_day)
        if tercile == "high":
            rally_returns.append(nq_returns[day])
        elif tercile == "low":
            selloff_returns.append(nq_returns[day])

    print(f"Days following a ZN 3-day RALLY (top tercile):   n={len(rally_returns)}")
    print(f"Days following a ZN 3-day SELLOFF (bottom tercile): n={len(selloff_returns)}")

    mean_rally = sum(rally_returns) / len(rally_returns) if rally_returns else float("nan")
    mean_selloff = sum(selloff_returns) / len(selloff_returns) if selloff_returns else float("nan")
    print(f"\nMean next-day NQ log return after RALLY:   {mean_rally:.6f}")
    print(f"Mean next-day NQ log return after SELLOFF: {mean_selloff:.6f}")

    ci_low, ci_high = bootstrap_mean_diff_ci(rally_returns, selloff_returns)  # reused unmodified
    diff = mean_rally - mean_selloff
    statistically_credible = (ci_low > 0) or (ci_high < 0)
    print(f"\nDifference (RALLY - SELLOFF): {diff:.6f}")
    print(f"90% bootstrap CI on the difference: ({ci_low:.6f}, {ci_high:.6f})")
    print(f"Statistically credible (CI entirely off zero): {statistically_credible}")

    print(f"\n{'=' * 78}")
    if statistically_credible:
        verdict = ("STEP 1 PASS. ZN's 3-day cumulative move carries some distinguishable "
                   "predictive signal for next-day NQ direction on the Discovery slice. "
                   "Logged as PROMISING (Step 1 only -- no costed rule built yet). Next "
                   "step: design one concrete, pre-registered, costed trading rule and "
                   "test it prospectively on the Validation slice (same data-availability "
                   "caveat as exp-061 applies -- ZN data doesn't yet cover Validation).")
    else:
        verdict = ("STEP 1 FAIL. ZN's 3-day cumulative move does not show a statistically "
                   "credible difference in next-day NQ returns on the Discovery slice. "
                   "Logged as REJECTED. This multi-day framing of ZN is closed.")
    print(f"Verdict: {verdict}")

    out = {
        "cumulative_window_days": CUMULATIVE_WINDOW_DAYS,
        "n_rally": len(rally_returns),
        "n_selloff": len(selloff_returns),
        "mean_rally": mean_rally,
        "mean_selloff": mean_selloff,
        "diff": diff,
        "ci_90": [ci_low, ci_high],
        "statistically_credible": statistically_credible,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_bond_multiday_lead_signal_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
