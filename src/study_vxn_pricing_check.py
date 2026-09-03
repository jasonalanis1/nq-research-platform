"""
study_vxn_pricing_check.py
==============================

The project's OWN real-data version of the question raised in
`docs/OPTIONS_STRUCTURE_COST_ESTIMATE.md` and first answered only via
outside literature in `docs/OPTIONS_VOLATILITY_RISK_PREMIUM_CHECK.md`
(that pass used academic papers on S&P 500 / Treasury futures options
as a proxy, since this project's own data wasn't reachable that
session). This script replaces the proxy with this project's own real
VXN (CBOE Nasdaq-100 Volatility Index) history, downloaded by Jason
directly from FRED (`data/VXNCLS_MAX.csv`, 2001-02-02 through
2026-09-02), compared against this project's own exact CPI/NFP/FOMC
Discovery-period event days -- the SAME day lists already frozen and
used by exp-039 (`study_economic_calendar.py`) and exp-040
(`study_fomc_volatility.py`). No new price data, no new event-date
research: every date list and every realized-move number here is
reused unmodified from those two studies.

CHARACTERIZATION CHECK, not a trading hypothesis: no trades, no
ledger entry. The question is narrow: does the market's own
forward-looking volatility gauge (VXN) already run higher ahead of
these specific event days than ahead of normal days -- and if so, by
how much relative to what actually happens? That is the direct,
project-data-driven analog of "is the CPI/NFP/FOMC magnitude finding
already priced into options, or is there room for an edge."

TWO tests, in order of how much can be trusted:

Test 1 (PRIMARY, no modeling assumptions): is VXN on the day BEFORE
each event (T-1, the last available close strictly before the event
day -- i.e. what the market already knew going in) higher than VXN
ahead of normal days? This alone tells us whether the market visibly
anticipates these days at all. Uses `bootstrap_mean_diff_ci()` from
`study_futures_expiration.py`, reused unmodified, exactly like every
other study in this project.

Test 2 (SECONDARY, approximate, flagged as such): converts that same
T-1 VXN level into a rough implied 30-minute expected move in NQ
points, and compares it to the ACTUAL realized 30-minute move already
computed by exp-039/exp-040 for the same days (`abs_return_30m`,
reused unmodified via each study's own `scan_all_days()`). This is
the closest this project can get, without buying real options data,
to the literature check's "did implied volatility over- or
under-predict what actually happened" question. It requires a
modeling assumption to translate VXN's annualized, 30-day, blended
index level into a point estimate for one specific 30-minute window --
disclosed explicitly below, not hidden. VXN is also not the same
instrument as an actual event-day option (it's a blended 30-day
measure, not a 1-day-to-expiry price), so Test 2 is a supporting
cross-check, not the primary evidence. Test 1 is the primary evidence.

HOW TO RUN:
    python3 src/study_vxn_pricing_check.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

import study_economic_calendar as ec
import study_fomc_volatility as fv
from data_loader import load_price_data
from data_split import get_discovery_data
from detect_ib_breakout import OPEN_HOUR, OPEN_MINUTE
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VXN_PATH = DATA_DIR / "VXNCLS_MAX.csv"

N_BOOTSTRAP = 2000       # matches study_economic_calendar.py / study_fomc_volatility.py
RANDOM_SEED = 11         # matches study_economic_calendar.py / study_fomc_volatility.py
MAX_LOOKBACK_DAYS = 7    # sanity bound on how far back T-1 is allowed to search for a VXN print

# Test-2 modeling assumption, stated plainly: VXN is an annualized,
# 30-day, percent-of-index-level volatility figure (same construction
# as VIX). To turn that into a rough expected ABSOLUTE move over one
# specific 30-minute window, standard variance-scaling is used:
#   implied_30min_pct = (VXN / 100) * sqrt(30 / (TRADING_DAYS_PER_YEAR * MINUTES_PER_TRADING_DAY))
#   implied_30min_points = implied_30min_pct * that_day's_830am_NQ_price
# This assumes volatility is spread evenly across a 390-minute trading
# day and 252 trading days/year -- both standard conventions, but real
# volatility is NOT evenly spread (it clusters around the open and
# around scheduled releases), so this will tend to UNDER-state the
# implied move on a day the market already expects to be active, and
# OVER-state it on a quiet day. This cuts against finding a positive
# gap on event days, if anything -- disclosed here rather than buried.
TRADING_DAYS_PER_YEAR = 252
MINUTES_PER_TRADING_DAY = 390


def load_vxn_series() -> pd.Series:
    """Date -> VXN close, holidays/gaps (blank in the source file)
    dropped rather than filled -- T-1 lookup below searches backward
    past any gap on its own."""
    df = pd.read_csv(VXN_PATH)
    df["observation_date"] = pd.to_datetime(df["observation_date"]).dt.date
    df["VXNCLS"] = pd.to_numeric(df["VXNCLS"], errors="coerce")
    df = df.dropna(subset=["VXNCLS"]).sort_values("observation_date")
    return pd.Series(df["VXNCLS"].values, index=df["observation_date"].values)


def vxn_prior_close(vxn: pd.Series, day) -> float:
    """Last available VXN close strictly before `day`. Raises if none
    found within MAX_LOOKBACK_DAYS -- every Discovery event day is
    from 2015 onward, deep inside VXN's 2001-onward coverage, so this
    should never trigger; it's a sanity guard, not expected behavior."""
    for lag in range(1, MAX_LOOKBACK_DAYS + 1):
        candidate = pd.Timestamp(day) - pd.Timedelta(days=lag)
        candidate = candidate.date()
        if candidate in vxn.index:
            return float(vxn[candidate])
    raise ValueError(f"No VXN print found within {MAX_LOOKBACK_DAYS} days before {day}")


def implied_30min_points(vxn_level: float, price_level: float) -> float:
    implied_pct = (vxn_level / 100.0) * np.sqrt(30.0 / (TRADING_DAYS_PER_YEAR * MINUTES_PER_TRADING_DAY))
    return implied_pct * price_level


def run_test1(vxn: pd.Series, event_days: list, normal_days: list, label: str) -> dict:
    event_vxn = [vxn_prior_close(vxn, d) for d in event_days]
    normal_vxn = [vxn_prior_close(vxn, d) for d in normal_days]
    diff_low, diff_high = bootstrap_mean_diff_ci(event_vxn, normal_vxn, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED)
    mean_diff = float(np.mean(event_vxn) - np.mean(normal_vxn))
    return {
        "label": label,
        "n_event": len(event_vxn),
        "n_normal": len(normal_vxn),
        "mean_vxn_event_t_minus_1": float(np.mean(event_vxn)),
        "mean_vxn_normal_t_minus_1": float(np.mean(normal_vxn)),
        "mean_diff": mean_diff,
        "ci_90": (diff_low, diff_high),
        "significant": bool(diff_low > 0 or diff_high < 0),
    }


def run_test2(vxn: pd.Series, discovery_df: pd.DataFrame, scan_df: pd.DataFrame,
              event_days: list, label: str) -> dict:
    """Paired implied-vs-realized comparison for event days only,
    reusing bootstrap_mean_diff_ci() unmodified by passing the paired
    differences as group_a and a same-length zero array as group_b --
    this makes bootstrap_mean_diff_ci(paired_diff, zeros) compute
    exactly a one-sample 90% bootstrap CI on mean(paired_diff), since
    resampling an all-zero array with replacement is deterministically
    zero every draw."""
    day_groups = {d: sub for d, sub in discovery_df.groupby(discovery_df.index.date)}
    scan_by_date = scan_df.set_index("date")

    paired_diffs = []
    used_days = []
    for d in event_days:
        if d not in day_groups:
            continue
        day_df = day_groups[d]
        tz = day_df.index.tz
        open_ts = pd.Timestamp(d, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
        open_bars = day_df[day_df.index >= open_ts]
        if open_bars.empty:
            continue
        price_level = float(open_bars.iloc[0]["Open"])
        vxn_level = vxn_prior_close(vxn, d)
        implied = implied_30min_points(vxn_level, price_level)

        if d not in scan_by_date.index:
            continue
        realized = scan_by_date.loc[d, "abs_return_30m"]
        if pd.isna(realized):
            continue

        paired_diffs.append(implied - float(realized))
        used_days.append(d)

    paired_diffs = np.array(paired_diffs)
    zeros = np.zeros_like(paired_diffs)
    diff_low, diff_high = bootstrap_mean_diff_ci(paired_diffs, zeros, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED)

    return {
        "label": label,
        "n": len(paired_diffs),
        "mean_implied_minus_realized": float(paired_diffs.mean()),
        "ci_90": (diff_low, diff_high),
        "implied_over_predicts": bool(diff_low > 0),
        "implied_under_predicts": bool(diff_high < 0),
    }


def print_test1(result: dict):
    print(f"\n--- Test 1 (primary): VXN T-1 level, {result['label']} vs normal ---")
    print(f"n_event={result['n_event']}  n_normal={result['n_normal']}")
    print(f"mean VXN T-1, event days:  {result['mean_vxn_event_t_minus_1']:.3f}")
    print(f"mean VXN T-1, normal days: {result['mean_vxn_normal_t_minus_1']:.3f}")
    print(f"mean diff: {result['mean_diff']:+.3f}  90% CI: ({result['ci_90'][0]:+.3f}, {result['ci_90'][1]:+.3f})")
    print(f"significant (CI excludes 0): {result['significant']}")


def print_test2(result: dict):
    print(f"\n--- Test 2 (secondary, approximate): implied (VXN-based) vs realized 30-min move, {result['label']} ---")
    print(f"n={result['n']}")
    print(f"mean (implied - realized): {result['mean_implied_minus_realized']:+.3f} pts  "
          f"90% CI: ({result['ci_90'][0]:+.3f}, {result['ci_90'][1]:+.3f})")
    print(f"implied over-predicts realized (CI entirely > 0): {result['implied_over_predicts']}")
    print(f"implied under-predicts realized (CI entirely < 0): {result['implied_under_predicts']}")


def main():
    vxn = load_vxn_series()
    print(f"Loaded VXN: {len(vxn)} observations, {vxn.index.min()} to {vxn.index.max()}")

    full_df, is_synthetic = load_price_data(context="study_vxn_pricing_check.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this check requires real data.")
        return
    discovery_df = get_discovery_data(full_df)
    discovery_days = sorted(set(discovery_df.index.date))
    print(f"Discovery days: {len(discovery_days)}")

    # --- CPI+NFP (exp-039's exact universe) ---
    cpi_nfp_days = [d for d in discovery_days if ec.classify_day(d) in ("cpi", "nfp")]
    cpi_days = [d for d in discovery_days if ec.classify_day(d) == "cpi"]
    nfp_days = [d for d in discovery_days if ec.classify_day(d) == "nfp"]
    econ_normal_days = [d for d in discovery_days if ec.classify_day(d) == "normal"]
    print(f"CPI days: {len(cpi_days)}  NFP days: {len(nfp_days)}  "
          f"CPI+NFP pooled: {len(cpi_nfp_days)}  normal (econ calendar): {len(econ_normal_days)}")

    # --- FOMC (exp-040's exact primary universe, overlap-excluded days dropped) ---
    fomc_days = [d for d in discovery_days if fv.classify_day(d) == "fomc"]
    fomc_normal_days = [d for d in discovery_days if fv.classify_day(d) == "normal"]
    print(f"FOMC primary days: {len(fomc_days)}  normal (FOMC calendar): {len(fomc_normal_days)}")

    results = {}
    results["cpi_nfp_t1"] = run_test1(vxn, cpi_nfp_days, econ_normal_days, "CPI+NFP pooled")
    results["cpi_t1"] = run_test1(vxn, cpi_days, econ_normal_days, "CPI only")
    results["nfp_t1"] = run_test1(vxn, nfp_days, econ_normal_days, "NFP only")
    results["fomc_t1"] = run_test1(vxn, fomc_days, fomc_normal_days, "FOMC")

    for key in ["cpi_nfp_t1", "cpi_t1", "nfp_t1", "fomc_t1"]:
        print_test1(results[key])

    econ_scan_df = ec.scan_all_days(discovery_df)
    fomc_scan_df = fv.scan_all_days(discovery_df)

    results["cpi_nfp_t2"] = run_test2(vxn, discovery_df, econ_scan_df, cpi_nfp_days, "CPI+NFP pooled")
    results["fomc_t2"] = run_test2(vxn, discovery_df, fomc_scan_df, fomc_days, "FOMC")
    # Baseline control: does the SAME implied-vs-realized comparison
    # also run positive on ordinary days with no known catalyst? If
    # so, the event-day gap above may just be VXN's generic tendency
    # to run rich (the well-documented broad volatility risk premium
    # that shows up on every day, not something specific to these
    # events) rather than evidence about event-day pricing behavior
    # specifically. Without this control, Test 2 on its own cannot
    # distinguish the two explanations.
    results["normal_t2_econ"] = run_test2(vxn, discovery_df, econ_scan_df, econ_normal_days, "normal days (econ calendar)")
    results["normal_t2_fomc"] = run_test2(vxn, discovery_df, fomc_scan_df, fomc_normal_days, "normal days (FOMC calendar)")

    for key in ["cpi_nfp_t2", "fomc_t2", "normal_t2_econ", "normal_t2_fomc"]:
        print_test2(results[key])

    print("\n=== Bottom line ===")
    print("Test 1 asks: does the market's own volatility gauge already run higher")
    print("ahead of these event days than ahead of normal days? Test 2 asks: does")
    print("that elevation over- or under-predict what actually ends up happening,")
    print("and the normal-day rows are the control needed to tell an event-specific")
    print("effect apart from VXN's generic tendency to run rich on any day.")


if __name__ == "__main__":
    main()
