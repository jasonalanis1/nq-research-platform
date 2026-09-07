"""
study_bond_lead_signal_validation.py
=============================

exp-062 -- the pre-registered prospective test that exp-061 (hyp-000031,
ZN bond-lead standalone signal) said was required before its Step 1
Discovery-slice finding could be trusted. Same discipline as every
other candidate in this project: one concrete costed rule, one single
test on fresh out-of-sample data, no retuning if it fails.

FROZEN HYPOTHESIS (written before this script is run, before any
Validation-slice number is looked at):

    A simple costed rule -- go LONG NQ (close-to-close) on days that
    follow ZN closing UP, go SHORT NQ (close-to-close) on days that
    follow ZN closing DOWN, one round-trip cost charged per day held,
    UNCHANGED from exp-061's condition and direction -- clears this
    project's promotion bar when evaluated ONLY on the Validation slice
    (2021-10-04 -> 2024-01-03), data this specific rule has never been
    tested on.

TRADE CONSTRUCTION (same point-based framing as study_turn_of_month.py,
since this is a simple directional day-signal with no natural
stop/target to define an R-multiple against -- reusing that project's
existing precedent rather than inventing a new risk unit):
  - Each day's point_return = ref_close[day] - ref_close[prior_day]
    (close-to-close, same measurement exp-061 already used in log form).
  - Position each day = +1 (long) if ZN closed up the PRIOR day,
    -1 (short) if ZN closed down the prior day, else flat/no trade.
  - net_pnl_points = position * point_return - ROUND_TRIP_COST_POINTS
    (one round-trip cost per day held, position flips daily so every
    held day is its own round trip).

STATISTICAL BAR (stated before any result is looked at, same standard
as study_turn_of_month.py's Step 2): statistically credible = 90%
bootstrap CI on mean net points entirely above zero. Economically
meaningful = mean net points >= 2x ROUND_TRIP_COST_POINTS (a real
economic buffer over costs, not just barely positive).

CONTINUITY: no trailing classifier needed here (ZN's own same-day
sign, no expanding percentile), so no warm-up period concern --
Validation-slice days are evaluated using only ZN/NQ closes within
Discovery+Validation combined, same as exp-061's plumbing.

REUSED, UNMODIFIED:
  - compute_daily_ref_closes, compute_daily_log_returns
    (study_volatility_regime.py)
  - bootstrap_mean_ci (study_turn_of_month.py)
  - ROUND_TRIP_COST_POINTS (backtest.py)
  - load_price_data(symbol="ZN") (data_loader.py)

PROMOTION CONSEQUENCE, decided in advance: same as exp-054/056/058 --
a clean pass here is logged as VALIDATION CANDIDATE (still not
live-authorized, would need a HOLDOUT GEN2 pass next, budgeted
separately). A fail closes this specific rule; no retuning.

HOW TO RUN:
    python3 src/study_bond_lead_signal_validation.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import DISCOVERY_END_DATE, VALIDATION_END_DATE
from study_volatility_regime import compute_daily_ref_closes, compute_daily_log_returns  # reused unmodified
from study_nq_trend_following import bootstrap_mean_ci  # reused unmodified
from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main():
    print("=" * 78)
    print("EXP-062: ZN BOND-LEAD SIGNAL, COSTED RULE -- PROSPECTIVE VALIDATION")
    print("=" * 78)
    print("\nPre-registered single hypothesis (see this file's docstring), tested on the")
    print("Validation slice only -- data this exact rule has never seen.\n")

    nq_full_df, nq_synthetic = load_price_data(context="study_bond_lead_signal_validation.py (NQ)")
    if nq_synthetic:
        print("ABORT: only synthetic NQ data is available -- this study requires real data.")
        return
    try:
        zn_full_df, zn_synthetic = load_price_data(
            context="study_bond_lead_signal_validation.py (ZN)", symbol="ZN"
        )
    except FileNotFoundError:
        print("ABORT: ZN data file not found.")
        return
    if zn_synthetic:
        print("ABORT: only synthetic ZN data is available -- this study requires real data.")
        return

    nq_research_df = nq_full_df[nq_full_df.index <= VALIDATION_END_DATE]
    zn_research_df = zn_full_df[zn_full_df.index <= VALIDATION_END_DATE]
    print(f"Discovery+Validation combined (NQ): "
          f"{len(nq_research_df.index.normalize().unique())} trading day(s) through {VALIDATION_END_DATE.date()}.")

    nq_day_groups = {day: sub for day, sub in nq_research_df.groupby(nq_research_df.index.date)}
    zn_day_groups = {day: sub for day, sub in zn_research_df.groupby(zn_research_df.index.date)}

    nq_ref_closes = compute_daily_ref_closes(nq_day_groups)  # reused unmodified
    zn_ref_closes = compute_daily_ref_closes(zn_day_groups)  # reused unmodified

    nq_days_sorted = sorted(nq_ref_closes.keys())
    zn_returns = compute_daily_log_returns(zn_ref_closes)  # reused unmodified, just for sign

    discovery_end_date = DISCOVERY_END_DATE.date()

    def build_net_pnl(days_subset):
        net_pnls = []
        for i in range(1, len(days_subset)):
            prior_day, day = days_subset[i - 1], days_subset[i]
            zn_ret = zn_returns.get(prior_day)
            if zn_ret is None or zn_ret == 0:
                continue
            day_close = nq_ref_closes.get(day)
            prior_close = nq_ref_closes.get(prior_day)
            if day_close is None or prior_close is None:
                continue
            point_return = day_close - prior_close
            position = 1 if zn_ret > 0 else -1
            net_pnl = position * point_return - ROUND_TRIP_COST_POINTS
            net_pnls.append(net_pnl)
        return net_pnls

    # BACKGROUND: unfiltered Discovery+Validation combined, for context only
    all_net_pnls = build_net_pnl(nq_days_sorted)

    # PRIMARY (pre-registered): Validation-slice only
    validation_days = [d for d in nq_days_sorted if d > discovery_end_date]
    validation_net_pnls = build_net_pnl(validation_days)

    def analyze(net_pnls, label):
        print(f"\n{'-' * 78}")
        print(label)
        print(f"{'-' * 78}")
        n = len(net_pnls)
        if n < 10:
            print(f"  n={n} -- too few days to analyze meaningfully.")
            return {"n": n, "skipped": True}
        mean_net = float(sum(net_pnls) / n)
        ci_low, ci_high = bootstrap_mean_ci(net_pnls)
        economic_threshold = 2 * ROUND_TRIP_COST_POINTS
        statistically_credible = bool(ci_low > 0)
        economically_meaningful = bool(mean_net >= economic_threshold)
        print(f"  n: {n}")
        print(f"  mean_net_pnl_points: {mean_net:.4f}")
        print(f"  ci_90: ({ci_low:.4f}, {ci_high:.4f})")
        print(f"  economic_threshold (2x round-trip cost): {economic_threshold:.4f}")
        print(f"  Statistically credible: {statistically_credible}   "
              f"Economically meaningful: {economically_meaningful}")
        return {
            "n": n,
            "mean_net_pnl_points": mean_net,
            "ci_90": (ci_low, ci_high),
            "economic_threshold": economic_threshold,
            "statistically_credible": statistically_credible,
            "economically_meaningful": economically_meaningful,
        }

    print(f"\n{'=' * 78}")
    print("BACKGROUND (not the test): Discovery+Validation combined")
    print(f"{'=' * 78}")
    background = analyze(all_net_pnls, "All days, Discovery+Validation combined (context only)")

    print(f"\n{'=' * 78}")
    print("PRIMARY TEST (pre-registered): Validation slice only")
    print(f"{'=' * 78}")
    primary = analyze(validation_net_pnls, f"Validation slice only (n={len(validation_net_pnls)})")

    passed = (
        isinstance(primary, dict)
        and not primary.get("skipped")
        and primary.get("statistically_credible")
        and primary.get("economically_meaningful")
    )

    print(f"\n{'=' * 78}")
    if passed:
        verdict = ("PASS. The ZN bond-lead costed rule clears the promotion bar on the "
                   "Validation slice -- fresh data, pre-registered rule, one single test. "
                   "Logged as VALIDATION CANDIDATE. Still NOT authorized for live trading "
                   "-- next step per the project's ladder would be a HOLDOUT GEN2 test, "
                   "budgeted and requested separately, not run casually.")
    else:
        verdict = ("FAIL. The ZN bond-lead costed rule does not clear the bar on fresh "
                   "Validation-slice data. exp-061's Discovery-slice finding does not "
                   "replicate out of sample -- treated as noise, not a real effect. This "
                   "specific rule is closed; no retuning.")
    print(f"Verdict: {verdict}")

    out = {
        "background_all_days": background,
        "primary_validation_only": primary,
        "passed": passed,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_bond_lead_signal_validation_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()
